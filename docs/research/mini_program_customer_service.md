# Live customer service (chat) for a WeChat Mini‑Program
Project context
- Client: WeChat Mini‑Program frontend.
- Backend: FastAPI (file upload + payment app already present).
- Goal: provide live customer support / chat inside the mini‑program (real‑time messaging, attachments, offline notifications, agent dashboard).

This note summarizes integration options, WeChat specifics, third‑party IM flows, server considerations, UX patterns, code snippets and a recommended approach for a small team.

---

## Integration options — overview, traits, pros/cons, when to choose

1. WeChat built‑in customer service conversation (wx.openCustomerServiceConversation)
   - Traits: native Mini‑Program API to open a WeChat-managed customer service chat session. Supports session context (sessionFrom), message card, and attachments when supported.
   - Pros: simplest integration, no extra IM infra, familiar UX, free.
   - Cons: limited customization, agent UX tied to WeChat service account / public account, possible limitations on message types & automation.
   - Costs: free (requires configuration/linking with official account / service account in WeChat Console).
   - When: small/medium apps needing quick support with minimal infra.

2. WeChat official account customer service connection
   - Traits: route Mini‑Program chats to a public/service account customer service backend.
   - Pros: unified customer service across public account + mini‑program.
   - Cons: requires public/service account and setup; agent tools may be constrained.
   - When: you already use a WeChat Official Account and want unified handling.

3. Mini‑Program plugins (customer service plugins)
   - Traits: third‑party plugins embedded in mini‑program, provide full chat UI/features.
   - Pros: fast integration, feature rich (bots, transcripts), lower engineering effort.
   - Cons: sandboxing limits (plugin’s runtime), dependency on vendor, potential data export limits, revenue/fee.
   - When: want fastest integration with richer UX and don't need deep customization.

4. Third‑party cloud IM providers (Tencent Cloud IM / NetEase / RongCloud / Easemob) or SaaS chat widgets
   - Traits: full IM SDKs for Mini‑Program + server APIs for userSig/token generation, message persistence, web admin consoles.
   - Pros: full control, richer features (typing indicators, read receipts, message history, offline push), scalable.
   - Cons: costs (per‑message, per‑MAU), integration overhead, compliance work.
   - Costs: provider dependent — usually a combination of free tier + pay per MAU/messages/storage.
   - When: you need full control, multi‑channel agent console, compliance/auditing, or advanced routing.

---

## WeChat-specific APIs & components

- wx.openCustomerServiceConversation(params)
  - Key params:
    - sessionFrom: string — a context string shown to agents.
    - showMessageCard: boolean — show a message card with a link.
    - sendMessageTitle/path/img: used if showMessageCard true.
  - Example usage:
    - wx.openCustomerServiceConversation({
        sessionFrom: 'order:12345',
        showMessageCard: true,
        sendMessageTitle: 'Order #12345 details',
        sendMessagePath: '/pages/order?id=12345'
      })
  - Limits/requirements:
    - Some advanced features require linking the mini‑program to a WeChat public/service account or to enable customer service in WeChat Console.
    - Message types supported are limited compared to full IM SDKs.
    - For notifications to users you may need subscribeMessage / template messages.

- Notifications:
  - Use wx.requestSubscribeMessage to request permission for subscription messages (offline/critical notifications).
  - Template messages can also be used server‑side to notify users if they opted in.

- Content & security:
  - Use WeChat content security APIs for moderation where required.

Links:
- openCustomerServiceConversation doc: https://developers.weixin.qq.com/miniprogram/dev/api/open-api/customer-service/wx.openCustomerServiceConversation.html
- subscribeMessage doc: https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/subscribe-message.html

---

## Third‑party IM providers — flow & notes

Typical flow (applies to Tencent IM, NetEase, RongCloud, etc.):
1. Client-side (Mini‑Program): import provider’s Mini‑Program SDK and init (requires a user identifier).
2. Server-side: generate authentication token / userSig for the user (provider secret kept on server), return to client.
3. Client connects to provider's IM service via SDK using the token.
4. Messages go through provider; server can use REST APIs for offline messages, message history, or to inject system messages.
5. Persistence, archiving, and web admin UI are provided or built by you.

Provider notes:
- Tencent Cloud IM (TIM):
  - Generate userSig server‑side using SDK or REST API (userSig expires, secret kept on server).
  - Client uses web / mini‑program SDK to login with userID + userSig.
  - Docs: https://cloud.tencent.com/document/product/269
- NetEase (网易云信):
  - Similar model: server generates token, client SDK in mini‑program, server REST for history.
  - Docs: https://dev.yunxin.163.com
- RongCloud / Easemob:
  - Similar flows; check provider docs for token generation and message storage APIs.
  - RongCloud docs: https://www.rongcloud.cn/docs

---

## Plugin approach
- How it works: vendor supplies a mini‑program plugin that you reference; plugin runs in sandboxed environment but can provide full chat UI and server connectivity.
- Trade‑offs: very quick to launch; but sandboxing limits direct code control, updates depend on plugin vendor, and data flows may reside with vendor.
- Use when: fast MVP or when vendor features (bots, analytics) are valuable.

---

## Server‑side considerations

- Auth mapping: map mini‑program openid/unionid to IM user accounts; keep mapping in DB.
- Token generation: provider tokens/userSig must be generated server‑side and short‑lived.
- Message persistence & auditing: persist transcripts for disputes; consider export formats.
- Webhooks & callbacks: handle message events from providers (incoming, offline, delivery receipts).
- Moderation/filters: run content through WeChat content security or provider moderation APIs before storing/delivering.
- Session routing: support round‑robin, skills routing, or priority queues; keep state in DB/Redis.
- Offline messages & notifications: trigger subscription/template messages or provider push to notify agents/offline users.
- Scaling & cost: estimate MAU, message volume, attachments storage; plan CDN/presigned uploads to reduce server load.

---

## UX patterns & constraints

- Context: open chat from order page using sessionFrom to pass order id/ref.
- Prefilled messages: use sessionFrom or send initial system message so agents see context.
- Attachments: prefer presigned upload URLs (storage service) — client uploads directly; send attachment metadata in messages. Proxy uploads if moderation is required.
- Showing order details to agent: share minimal necessary info (order id + read‑only link or tokenized view); avoid sending full PII in chat body.
- Operator UI: web admin with agent presence, conversation list, search, message history, quick replies, attachments.
- Features: typing indicators, read receipts, message history, privacy notices and data retention policy for users.

---

## Sample snippets (conceptual)

Mini‑Program: openCustomerServiceConversation
```js
wx.openCustomerServiceConversation({
  sessionFrom: JSON.stringify({ type: 'order', id: 12345 }),
  showMessageCard: true,
  sendMessageTitle: 'Order #12345 — help with printing',
  sendMessagePath: '/pages/order?id=12345',
  success() { console.log('opened customer service') },
  fail(err) { console.error(err) }
});
```

Server: generate Tencent userSig (conceptual, Python)
```py
# Pseudocode: use Tencent SDK or implement algorithm with sdkAppID and secretKey
def generate_user_sig(user_id):
    # do NOT embed secret in client
    # Use provider SDK to create userSig for user_id
    userSig = TencentIMSDK.generate_user_sig(sdk_app_id, secret_key, user_id, expire=3600)
    return {"userId": user_id, "userSig": userSig}
```

Server webhook verification (conceptual)
```py
from fastapi import Request, HTTPException

@app.post("/webhook/provider")
async def provider_webhook(req: Request):
    # verify signature/header provided by provider
    sig = req.headers.get("X-Provider-Signature")
    body = await req.body()
    if not verify_signature(body, sig, secret):
        raise HTTPException(status_code=401, detail="Invalid signature")
    event = await req.json()
    handle_event(event)
    return {"ok": True}
```

---

## Notifications & fallback
- Use wx.requestSubscribeMessage to request permission at appropriate UX moments; send offline/critical notifications via template messages if user consented.
- Fallback channels: phone, email, or web chat links shown when users decline messages.

---

## Moderation & compliance
- Content audit: WeChat content security APIs or provider moderation endpoints before publishing.
- Data retention & consent: display retention and obtain consent; keep logs for disputes.
- Logging: keep detailed transcripts, delivery receipts, and moderation decisions.

---

## Links & resources
- wx.openCustomerServiceConversation: https://developers.weixin.qq.com/miniprogram/dev/api/open-api/customer-service/wx.openCustomerServiceConversation.html
- subscribeMessage: https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/subscribe-message.html
- WeChat content security: https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/security.html
- Tencent Cloud IM (TIM): https://cloud.tencent.com/document/product/269
- NetEase (网易云信): https://dev.yunxin.163.com
- RongCloud: https://www.rongcloud.cn/doc

---

## Final recommendation (small team, single server)
For a small team deploying on one FastAPI server: start with the WeChat built‑in customer service (wx.openCustomerServiceConversation) to get chat working quickly and leverage WeChat notifications (subscribeMessage). If you need richer features (attachments, multi‑agent routing, web dashboard), adopt Tencent Cloud IM (or another provider) next — generate userSig on the FastAPI server, use the Mini‑Program SDK on the client, and use a minimal web admin for agents. This balances speed of delivery and future scalability.

Bootstrap checklist
1. Enable customer service in WeChat Console and link required accounts.
2. Implement wx.openCustomerServiceConversation with sessionFrom on order pages.
3. Add wx.requestSubscribeMessage flow for offline notifications.
4. Map mini‑program openid → agent user id in DB; create API to fetch/generate provider tokens.
5. If moving to third‑party IM: implement server userSig/token generation, integrate mini‑program SDK, and build a minimal web admin.
6. Add content moderation and webhook verification, and create a retention policy.
