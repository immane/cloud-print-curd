# Mini‑Program Frontend → FastAPI Backend: Architecture Research

This document summarizes practical choices and patterns for building a lightweight WeChat Mini‑Program frontend that pairs with a separate FastAPI (OpenAPI/REST) backend. Goals and constraints:
- Strict separation: frontend (mini‑program) and backend (FastAPI).
- File uploads: prefer presigned S3 POST forms (direct from client) or an upload proxy when necessary.
- Payments: WeChat Pay integration (mini‑program).
- Developer productivity: quick dev iterations, component libraries.
- Small ops footprint: CI deployable, runnable on a single server; optional serverless cloud functions.
- Security: short-lived credentials, server verification, minimal secrets on client.

Framework comparison (6 options)
- Native WeChat Mini Program (vanilla)
  - Strengths: smallest runtime, official APIs, simplest dependency surface.
  - Learning curve: low if team knows JS + WeChat API.
  - Ecosystem: many UI libs provide Weapp versions.
  - Tooling: WeChat DevTools, miniprogram-ci.
  - Pros: minimal complexity, smallest bundle; Cons: limited cross-platform reuse.
- uni-app (Vue-based)
  - Strengths: Vue3 syntax (Composition API), cross-platform builds (WeChat, H5, Android/iOS via wrappers).
  - Learning curve: medium for Vue developers.
  - Ecosystem: Vant‑Uni, Pinia supported.
  - Tooling: uni‑app CLI, HBuilderX optional.
  - Pros: fast UI dev, reusable code; Cons: build quirks, occasionally platform-specific adapters.
- Taro (React-based)
  - Strengths: React syntax, multi‑platform (WeChat, H5, React Native).
  - Learning curve: medium for React devs.
  - Ecosystem: NutUI, Taro plugin ecosystem.
  - Tooling: Taro CLI, Babel bundling.
  - Pros: React-friendly, good for teams who prefer React; Cons: extra transpilation layers, platform mismatches.
- MPX / MPVue / WePY (brief)
  - Note: older Vue-to-miniprogram frameworks. Workable but less active; weigh maintenance risk.
- Kbone (Tencent multi-end)
  - Strengths: aims to run web code in WeChat Mini Programs with minimal changes.
  - Use case: porting existing web app; less common for greenfield projects.
- Cross-platform native alternatives (context)
  - Flutter / React Native / Kotlin Multiplatform: give deeper native control and unified codebase but larger binaries, more ops complexity for mini‑program channel. Use only if you need native apps beyond mini‑programs.

UI component libraries and integrations
- Vant Weapp (Weapp) and Vant‑uni (uni-app) — widely used, polished components.
- WeUI — official style components (lightweight).
- NutUI — works well with Taro and uni‑app (mobile-first).
- Lin UI, uView — popular in Chinese ecosystem; integrate with uni‑app/Taro.
Recommendation: for vanilla Weapp use Vant Weapp / WeUI; uni‑app => Vant‑uni + Pinia; Taro => NutUI or uView.

Networking, upload & storage patterns
- Direct client → S3 with presigned POST
  - Flow: client requests a presign endpoint on your FastAPI backend (/presign) with metadata (filename, content-type, size). Backend uses AWS SDK to generate a presigned POST (policy, key, x-amz-*) and returns form fields + URL. Client calls wx.uploadFile with:
    - url: presigned POST URL
    - formData: policy fields (key, policy, x‑amz-algorithm, x‑amz-credential, x‑amz‑signature, etc.) + any metadata
    - filePath & name: file binary
  - Notes: wx.uploadFile does multipart/form-data POST — presigned POSTs work well. Presigned PUTs are harder from mini‑programs.
  - Limitations: cannot set arbitrary headers; size limits in client; CORS is not relevant (WeChat runtime).
- Proxy through backend
  - Flow: client uploads file to your backend (wx.uploadFile → backend endpoint). Backend streams to S3 (multipart upload).
  - Benefits: server can scan for viruses, enforce authorization, compute checksums, centralize logs.
  - Trade-offs: higher bandwidth/cost on your server, increased ops/complexity, but better control and compatibility (supports presigned PUT workflows, large files).
Decision guidance: prefer presigned POST for low ops and cost; use proxy if you need server-side validation, scanning, or must support PUT flows.

Payment integration specifics (WeChat Pay mini‑program)
- Flow summary:
 1. Client asks backend to create an order (/create_order).
 2. Backend calls WeChat unifiedorder API (server side) with appid, mch_id, amount, notify_url, openid, etc., and signs payload with your merchant key.
 3. WeChat returns prepay_id. Backend constructs prepay params (nonceStr, package=prepay_id, timeStamp, signType) and signs them; return to client.
 4. Client calls wx.requestPayment with these params to invoke the payment UI.
 5. WeChat sends asynchronous payment notifications (notify_url) to your backend — verify signature and update order state.
- Security:
  - Keep merchant key and app secret server‑side only.
  - Verify signatures on notify messages and use HTTPS.
  - Use sandbox/test mode for development.
- Order idempotency & webhook security:
  - Use unique client_order_id referenced by backend; if unifiedorder retried, handle duplicate prepay_id responses idempotently.
  - Protect notify endpoint: validate appid/mch_id, sign, verify IP ranges, replay prevention (nonce/timestamp), and mark events processed once.

State management & storage
- Keep client state minimal. Prefer server state with lightweight local cache.
- Options:
  - uni‑app/Vue: Pinia (small, familiar).
  - Taro/React: Zustand (very small), MobX, or use React Context.
  - Vanilla: tiny event bus or reactive store file.
- Data fetching: prefer a query pattern (cache + background refresh) — use equivalents of TanStack Query or roll simple caching layers; avoid large local databases.

Build, testing & CI
- Local tools: WeChat DevTools for debugging and simulator.
- CI & packaging: miniprogram-ci (npm package) can upload builds from CI (GitHub Actions).
- Unit testing: Vitest works for uni‑app components; Jest/Vitest for business logic.
- E2E: miniprogram-automator for automated UI tests.
- Local backend mocking: run FastAPI locally, or use a small proxy to mock S3 (or use a dedicated dev S3 bucket).
- For file testing: use a dev S3 bucket or local S3 compatible (e.g., LocalStack) with restricted credentials.

Deployment & ops
- WeChat platform requires uploading packaged code, filling app info, then submitting for review.
- CI flow: build → run tests → miniprogram-ci upload (requires appid & privateKey stored in CI secrets) → optionally trigger WeChat review.
- Cloud functions: Tencent CloudBase (TCB) or short serverless functions can host small backend endpoints; trade-offs include vendor lock‑in vs simpler ops.

Security & best practices
- Never embed long‑lived secrets on the client. Use short‑lived presigned URLs and short TTL tokens.
- Protect presigned URLs: short TTL, scoped key prefixes, and server-side validation after upload (checksum, metadata verification).
- S3 ACLs: enforce bucket policy to only allow presigned POSTs / put from your domain patterns, and block public list/get.
- For payments: keep merchant key secret, validate async notify, rate‑limit endpoints, and log suspicious activity.

Three recommended minimal stacks
- A) Native (recommended for smallest runtime)
  - Vanilla WeChat Mini Program + Vant Weapp
  - Backend: FastAPI presign endpoint + WeChat Pay unifiedorder
  - Pros: smallest deps, simplest ops
- B) Vue-based (recommended for fastest development & cross-platform)
  - uni‑app (Vue3) + Vant‑uni + Pinia + GitHub Actions + presigned POST to S3
  - Pros: fast UI dev, potential cross-platform reuse
- C) React-based (for React teams)
  - Taro + NutUI + React + miniprogram-ci
  - Pros: React ecosystem, multi-platform builds

Links & resources
- WeChat Mini Program API: wx.uploadFile — https://developers.weixin.qq.com/miniprogram/dev/api/network/upload/wx.uploadFile.html
- WeChat Pay mini‑program: wx.requestPayment + server unifiedorder docs — https://developers.weixin.qq.com/miniprogram/dev/framework/open-ability/payment.html
- uni‑app docs — https://uniapp.dcloud.io/
- Vant Weapp / Vant‑uni — https://youzan.github.io/vant-weapp/ and https://vant-contrib.gitee.io/vant-uni/
- Taro — https://taro-docs.jd.com/
- miniprogram-ci — https://github.com/wechat-miniprogram/miniprogram-ci
- S3 presigned POST — https://docs.aws.amazon.com/AmazonS3/latest/API/sigv4-post-example.html

Final recommendation
- For a small team wanting fast iteration and easy cross-platform options: choose B — uni‑app (Vue3) + Vant‑uni + Pinia, with FastAPI backend issuing presigned POSTs for uploads and handling WeChat Pay server flow.

Minimal bootstrap checklist
- Frontend files: app.json, pages/, components/, utils/api.js (wrapper for requests), upload component using wx.uploadFile.
- Backend endpoints: POST /presign (returns S3 presigned POST fields), POST /create_order (calls unifiedorder), POST /notify (WeChat notify handler).
- Scripts: build (uni/taro/wechat), test, ci:upload (miniprogram-ci).
- CI steps (GitHub Actions):
  1. Checkout, install, run tests.
  2. Build mini‑program bundle.
  3. Run miniprogram-ci upload using secrets (APPID, PRIVATE_KEY, MCH_KEY).
  4. Deploy backend (single server or CloudBase) and ensure webhook URL is reachable.
- Dev: run local FastAPI, use dev S3 bucket or LocalStack, test payments with WeChat sandbox.

Keep the client thin: presigned POSTs where possible, proxy for server-side checks when required, and always keep payment credentials on the server.
