---
 title: WeChat Mini‑Program Payment APIs — Research & Integration Notes
 description: High level guide for integrating Mini‑Program (JSAPI) payments with a Python 3.12 FastAPI backend and MySQL
---

# WeChat Mini‑Program Payment APIs (JSAPI) — Research & Integration Notes

Project context
- Client: WeChat Mini‑Program (JSAPI / mini‑program payment flow).
- Server: FastAPI (Python 3.12) backend.
- DB: MySQL (orders, payment status, webhooks audit).
- Requirement: Accept payments via WeChat Pay using the Mini‑Program JSAPI flow (prefer v3, but note v2 differences).

This document describes the payment flow, v2 vs v3 endpoints, required parameters, client APIs, server responsibilities, signature & certificate handling, testing tips, error handling and a minimal endpoint checklist.

---

## High‑level payment flow (Mini‑Program / JSAPI)
1. Client obtains user's openid:
   - wx.login() → get auth code → send code to backend.
   - Backend exchanges code to openid via code2session (wx.login code -> /sns/jscode2session) or OAuth, and ties to a local user/order.
2. Create order on server: create local order row (out_trade_no), compute amount, and call WeChat unifiedorder (v2) or v3 JSAPI transactions to get a prepay_id.
3. Server prepares client payment parameters (timeStamp, nonceStr, package = "prepay_id=...", signType, paySign) and returns them to the Mini‑Program.
4. Client calls wx.requestPayment(...) with those params.
5. Asynchronous server‑to‑server notify: WeChat calls your notify URL when payment completes — verify signature, update order status, ensure idempotency.
6. Optional: server triggers order query / refunds / download bills as needed.

---

## WeChat Pay v2 (legacy) — unifiedorder (JSAPI)
- Endpoint (POST XML):
  - https://api.mch.weixin.qq.com/pay/unifiedorder
- Required fields (XML):
  - appid, mch_id, nonce_str, sign, body, out_trade_no, total_fee (integer, cents), spbill_create_ip, notify_url, trade_type=JSAPI, openid
- Response (XML):
  - return_code, return_msg; if success: result_code, prepay_id, trade_type
- Signature:
  - sign is computed by sorting params lexicographically, concatenating `k=v` pairs with `&`, appending `&key=API_KEY`, then MD5 (uppercase). Optionally sign_type=HMAC-SHA256 supported.
- Preparing client params (for wx.requestPayment):
  - timeStamp (string), nonceStr, package=`prepay_id=XXX`, signType (e.g., MD5), paySign (computed as above over appId, timeStamp, nonceStr, package, key).
- Notify verification:
  - Verify the XML `sign` and `result_code`. Respond with XML success acknowledgment.

---

## WeChat Pay v3 (recommended) — transactions/jsapi
- Endpoint (POST JSON):
  - https://api.mch.weixin.qq.com/v3/pay/transactions/jsapi
- Request body (JSON):
  - {
      "mchid":"<MCHID>",
      "appid":"<APPID>",
      "description":"Order description",
      "out_trade_no":"<OUT_TRADE_NO>",
      "notify_url":"https://your.server/wechat/notify",
      "amount": { "total": 100, "currency":"CNY" },
      "payer": { "openid":"USER_OPENID" }
    }
- Response (JSON):
  - { "prepay_id":"wx281...,", ... }
- Signature & Authorization for requests:
  - Requests to v3 require an Authorization header constructed with your merchant private key (RSA‑SHA256) following the WECHATPAY2‑SHA256‑RSA2048 scheme. You sign a canonical message (timestamp + nonce + body) with your merchant private key and include merchant id, serial_no, signature, nonce, timestamp in the header.
- Preparing client params for wx.requestPayment:
  - server returns: appId, timeStamp, nonceStr, package=`prepay_id=...`, signType=`RSA`, paySign
  - paySign is created by signing the canonical string:
    appId + "\n" + timeStamp + "\n" + nonceStr + "\n" + package + "\n"
    using your merchant private key with SHA256withRSA.
- Notify verification:
  - WeChat sends headers: Wechatpay-Timestamp, Wechatpay-Nonce, Wechatpay-Serial, Wechatpay-Signature.
  - Reconstruct message: timestamp + "\n" + nonce + "\n" + body + "\n"; verify signature using WeChat platform certificate corresponding to Serial.
  - Platform certs fetched via: GET https://api.mch.weixin.qq.com/v3/certificates (signed request).

---

## Client APIs (Mini‑Program)
- wx.login()
  - Usage: get a temporary code, send to backend to obtain openid.
- wx.requestPayment(params)
  - Required fields:
    - timeStamp: string (seconds)
    - nonceStr: string
    - package: "prepay_id=xxx"
    - signType: "RSA" (v3) or "MD5"/"HMAC-SHA256" (v2)
    - paySign: computed signature
  - Example usage:
    - wx.requestPayment({
        timeStamp, nonceStr, package, signType, paySign,
        success(res){ /* handle */ },
        fail(err){ /* handle */ }
      });
- Notes:
  - Never compute paySign on client. Always server‑generate and return parameters over HTTPS.
  - Validate order state from server after successful payment event rather than only trusting client callback.

---

## Server-side responsibilities & endpoints (recommended)
Minimal endpoints:
- POST /api/pay/create-order
  - Create DB order, call WeChat v3 /v2, return client params
- POST /api/wechat/notify
  - Receive async notify (v3/v2), verify signature, update order (idempotent)
- GET /api/pay/query/{out_trade_no}
  - Query order status (call WeChat order query)
- POST /api/pay/refund
  - Initiate refund (v3 preferred)
- GET /api/pay/download-bill?date=YYYY-MM-DD
  - Download billing file

Example v3 create-order (conceptual Python requests):
```python
import time, uuid, requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

mchid = "1234567890"
appid = "wxapp..."
notify_url = "https://your.server/wechat/notify"
private_key_pem = open("mch_private_key.pem","rb").read()

body = {
  "mchid": mchid, "appid": appid,
  "description":"Test order", "out_trade_no": str(uuid.uuid4()),
  "notify_url": notify_url,
  "amount":{"total":100,"currency":"CNY"},
  "payer":{"openid":"USER_OPENID"}
}
timestamp = str(int(time.time()))
nonce = uuid.uuid4().hex
# Canonical message = timestamp + "\n" + nonce + "\n" + json_body + "\n"
# Sign with RSA SHA256, attach to Authorization header (WECHATPAY2-SHA256-RSA2048)
# (Constructing header omitted here — use official SDK or follow docs)
resp = requests.post("https://api.mch.weixin.qq.com/v3/pay/transactions/jsapi",
                     json=body, headers={"Authorization":"...","Content-Type":"application/json"})
resp.raise_for_status()
prepay_id = resp.json().get("prepay_id")
```

Notify signature verification (conceptual):
```python
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
# headers: Wechatpay-Timestamp, Wechatpay-Nonce, Wechatpay-Serial, Wechatpay-Signature
msg = f"{timestamp}\n{nonce}\n{body}\n".encode()
platform_cert_pem = open("platform_cert.pem","rb").read()
pub = serialization.load_pem_public_key(platform_cert_pem)
pub.verify(signature_bytes, msg, padding.PKCS1v15(), hashes.SHA256())
# On success, process body and update order idempotently.
```

---

## Signature & security details
- v2:
  - Sign = MD5( sort(params) + &key=API_KEY ) uppercase by default. Optionally HMAC-SHA256 if sign_type specified.
  - Verify incoming notify by recomputing sign on payload.
- v3:
  - Client → WeChat: Authorization header signed with merchant private key (RSA-SHA256). Include merchant serial_no.
  - WeChat → Server (notify): Verify Wechatpay-Signature over (timestamp + "\n" + nonce + "\n" + body + "\n") using WeChat platform certificate (Serial in header).
  - Fetch/rotate platform certs from /v3/certificates periodically; store them and use for verification.
- Protections:
  - Verify nonce and timestamp, reject replays (e.g., timestamp tolerance +/- 5 minutes).
  - Save raw notify payload and headers for audit.
  - Keep merchant private key secure (server only), never expose to client.
  - Use HTTPS and strict TLS.

---

## Testing & sandbox
- v2 sandbox: use sandbox endpoints and get a sandbox sign key via /sandboxnew/pay/getsignkey.
- v3 testing: WeChat provides developer sandbox and test accounts in developer console.
- Local testing:
  - Use WeChat DevTools simulator to test client behavior.
  - Expose local notify endpoint using ngrok/localtunnel for WeChat to call.
  - For webhook testing use recorded signed messages or use the real sandbox environment.
- Tools/SDKs:
  - Official: wechatpay-python SDK (official, handles Authorization header and verification).
  - wechatpy (v2 utilities), third‑party SDKs.
  - Java: wechatpay-apache-httpclient (reference implementation).

---

## Error handling & idempotency
- Always treat notifications as possibly duplicated. Implement idempotency by:
  - Using out_trade_no or transaction_id and checking if order already moved to PAID.
  - Responding 200 immediately after successful verification & idempotent update.
- Retry logic:
  - If verification fails, return non‑200 to allow WeChat retries, but avoid looping failures—log and alert.
- Logging:
  - Log raw request, headers, computed verification result, DB updates for audits.
- Rate limiting and backoff:
  - Protect notify endpoint from abusive traffic; verify signature before costly DB ops.

---

## Practical recommendations for this project
- Prefer v3 for new integrations — stronger security and standards.
- Keep merchant private key & API key on server, not in source control (use env vars/secret manager).
- Server must always generate prepay params; never build on client.
- Verify notify signatures using platform certs; store and rotate platform certs.
- Store raw payloads for auditing and troubleshooting.
- Pay attention to short prepay_id lifetime; client should call wx.requestPayment soon after receiving params.
- Implement order lifecycle states: CREATED → PENDING_PAY → PAID → FULFILLED/REFUNDED → CLOSED.
- Minimal server endpoints: create-order, notify, query, refund, download-bill.

Bootstrap checklist
- [ ] Register WeChat Pay merchant, get mchid, api_v3_key, private key, certificate serial.
- [ ] Configure notify URL in merchant console.
- [ ] Implement /create-order (v3), return client params.
- [ ] Implement /wechat/notify with signature verification + idempotency.
- [ ] Setup periodic fetch of platform certificates.
- [ ] Add logging, alerts for failed verifications.

---

## Useful links
- WeChat Pay JSAPI v3 docs: https://pay.weixin.qq.com/wiki/doc/apiv3/apis/chapter3_1_1.shtml
- v2 unifiedorder docs: https://pay.weixin.qq.com/wiki/doc/api/jsapi.php?chapter=9_1
- wx.requestPayment docs: https://developers.weixin.qq.com/miniprogram/dev/api/open-api/payment/wx.requestPayment.html
- v3 notification verification & certificates: https://pay.weixin.qq.com/wiki/doc/apiv3/wechatpay/wechatpay4_1.shtml
- SDKs / examples:
  - wechatpay-python (official SDK)
  - wechatpy (v2 helpers)
  - GitHub search: "wechatpay python example" for sample repos.

---

Notes
- This is a practical integration guide; follow official docs for exact header formats and up‑to‑date endpoints. Use the official SDKs where possible to avoid low‑level mistakes.
