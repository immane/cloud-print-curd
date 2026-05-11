# 9零云印 (9 Ling Yun Yin) — UI Analysis & Implementation Notes

Short context
- 9零云印 is a WeChat Mini‑Program that offers cloud‑print-like upload & pay services: users upload files, configure print options (size, color, copies), view pricing, pay, and manage orders. This analysis emphasizes UI patterns relevant to upload, order creation, payment, file lists, and any visible admin/manage flows.

Key screens & components observed
1. Home screen
   - Main components: top header with logo/title, search / quick actions, primary CTA tiles (Upload, My Orders, Nearby Printers), promotional banner carousel.
   - Notable interactions: banner swipe, CTA chips, permission prompts (file / album access).

2. Upload flow
   - Steps: file pick → preview → metadata → presign step → upload progress → create order.
   - Components: file picker (native + custom Uploader), thumbnail grid/cards, preview modal (image/pdf preview), metadata form (Fields for name, pages, color options), presign call (spinner/loading overlay), progress bar/percent indicator, retry/delete buttons.
   - Interactions: immediate thumbnail generation, inline validation (file size/type), toast on presign failure, modal confirmation before uploading to remote storage.

3. Product / options selection
   - Components: option cards (paper size, color, single/double-sided), number input / stepper for copies, dropdown/picker for paper type, toggles for finishing options.
   - Interactions: real-time pricing recalculation, disabled state when incompatible options selected, inline helper text.

4. Pricing summary
   - Components: price breakdown card (unit price, copies, extras, tax/fees), sticky footer summary with “Pay” button, coupon/discount field.
   - Interactions: expandable detail rows, promo code input with immediate validation, sticky total that updates live.

5. Payment screen
   - Components: order summary, payment methods list (WeChat Pay primary), confirm payment button, security/privacy microcopy.
   - Interactions: modal confirmation, loading indicator during payment, toast/error if payment fails, redirect to order page on success.

6. Order list
   - Components: vertical list (cells) with order status tags, thumbnail, summary, action buttons (reprint, contact, cancel), filter tabs (All / Pending / Completed).
   - Interactions: swipe to reveal actions (sometimes), status chips with color coding, pull‑to‑refresh.

7. User profile
   - Components: profile header, account balance, payment methods, address/bookmarks, settings.
   - Interactions: navigation to admin/merchant area (if role permitted), quick links to support.

8. Admin / Manage panels (if present)
   - Components: order queue list, status update actions, detailed order modal, print job details, bulk operations.
   - Interactions: confirm dialogs for status changes, search and filter, toast confirmations.

Visual style
- Approximate palette:
  - Primary: teal/blue-green ~ #00A0A0 (used for CTAs)
  - Secondary: deep blue #005A8D or navy for headers/links
  - Accent: orange/yellow ~ #FFB000 for highlights/discounts
  - Background: light gray #F6F8FA
  - Surface: white #FFFFFF
  - Success: #2BC46D, Danger: #FF4D4F, Border: #E6EAF0, Text primary: #1F2D3D, Text secondary: #6B7380
  - (If unsure, pick tokens from a neutral material/WeChat palette and tune for contrast.)
- Typography:
  - Compact mobile scale: headings ~16–18px, body ~14px, caption ~12px; button text 14–16px.
- Spacing & layout:
  - 8px-based spacing scale (4 / 8 / 12 / 16 / 24 / 32). Surface padding typically 12–16px; list items height ~56–64px.
- Roundedness:
  - Soft rounded corners ~6–10px for cards and buttons.
- Iconography:
  - Simple outline style, 20–24px for list icons, 28–32px for main CTAs.
- Button treatment:
  - Primary: solid filled (primary color), white text.
  - Secondary: ghost/outline with primary color border.
  - Disabled: muted background + lowered opacity.

Component mapping to libraries
- Vant Weapp / Vant‑uni / uni‑app primitives:
  - Upload list / file row: use Vant Cell / List or van-cell-group for orders.
  - File uploader: Vant Uploader (van-uploader) or native <uploader> wrapper in uni‑app.
  - Modals & confirmations: Vant Dialog or van-popup.
  - Toast / notifications: Vant Toast (van-toast).
  - Pickers: Vant Picker / van-picker or native <picker>.
  - Buttons: van-button (primary/ghost/small).
  - Price summary: van-card / van-cell with sticky footer using position: fixed or uni‑app sticky.
  - Progress: van‑progress or van-loading overlay for presign/upload.
- Recommendations:
  - Use van-uploader for thumbnails + progress; van-list/cell for order list; van-field for metadata forms; van-stepper for copies.

Interaction & UX notes
- Upload feedback:
  - Show quick thumbnail + file meta immediately, then asynchronously request presign.
  - Use subtle skeleton or spinner for presign. On presign success start upload and show progress %.
  - Allow pause/cancel and retry on network failure.
- Error/retry:
  - Use transient toast for minor errors, modal for destructive failures (e.g., payment failure).
  - Provide clear retry CTA and show last attempt timestamp.
- Confirmation before payment:
  - Show a compact order summary modal before triggering WeChat Pay.
- Accessibility:
  - Tap targets >= 44px, high color contrast for primary CTAs, labels for icons, readable font sizes, and use aria-like attributes for screen readers where possible in mini‑programs.
- Microcopy tips:
  - CTAs: “Upload”, “Preview & Options”, “Pay Now”, “Create Order”.
  - Use inline helper copy for file requirements (max size, page limits).

Implementation notes & starter tokens
- Suggested design tokens (SCSS / variables):
  - $color-primary: #00A0A0
  - $color-secondary: #005A8D
  - $color-accent: #FFB000
  - $color-bg: #F6F8FA
  - $color-surface: #FFFFFF
  - $color-text: #1F2D3D
  - $color-muted: #6B7380
  - $color-border: #E6EAF0
  - $success: #2BC46D
  - $danger: #FF4D4F
  - $radius-md: 8px
  - $spacing-base: 8px
- Upload preview + presign (mini‑program pseudocode):
 1. User picks file via wx.chooseMessageFile / chooseImage.
 2. Show preview thumbnail locally.
 3. Call backend: wx.request({ url: '/presign', data: { filename, size, type } })
 4. If backend returns uploadUrl / token:
    - Use wx.uploadFile({ url: uploadUrl, filePath, name: 'file', formData: {...token fields}, success, fail, progress: wx.onProgressUpdate(...) })
    - Update UI with progress() and on success call backend to create order (wx.request createOrder with remote file key).
 5. On errors show van-toast and offer retry.
- Consider using qiniu SDK if the system uses Qiniu for storage; otherwise straight wx.uploadFile to your signed endpoint is fine.

Assets & icons
- Icon sets: recommend using WeUI icons, Vant icon set, or Iconfont (Alibaba) for consistent outline fills.
- SVG strategy: inline critical icons, load others via sprite/svg-sprite for performance.
- Image sizes:
  - File thumbnail grid: 160×160 px (2x for retina -> 320×320).
  - Preview modal: fit to screen width, up to 1080px for full-screen preview.
  - Hero/banner: 720×300 designed responsive.
- Use compressed webp/png for thumbnails and lazy-load full preview.

Final recommendation
- The app uses a pragmatic, compact mobile UI focused on fast upload → configure → pay flows. Replicate core layout, spacing, and interaction patterns closely (thumbnail-first upload, presign + progress, sticky price CTA), but adapt visual tokens to your brand. Start implementation with uni‑app + Vant‑uni (van-uploader, van-cell/list, van-toast, van-dialog). Implement the presign → wx.uploadFile sequence as the canonical flow and prototype the sticky pricing/footer early to validate the order/payment UX.
