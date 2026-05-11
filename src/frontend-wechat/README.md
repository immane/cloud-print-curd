# cloud-print-mini

Frontend mini-app style client for Cloud Print, built with Vue 3 + Vite.

## Stack

- Vue 3 (Composition API)
- TypeScript
- Vite
- Vitest + Vue Test Utils
- Playwright (E2E)

## Scripts

```bash
npm install
npm run dev
npm run build
npm run test
npm run e2e
```

## Structure

- `src/App.vue`: app shell and global styling
- `src/pages/`: Home / Library / Me tabs
- `src/components/`: shared UI and modal components
- `src/composables/useMiniApp.ts`: page state + API orchestration
- `tests/e2e/`: Playwright tests

## UI Direction

- Mobile-first layout, max width 460px
- Gradient background and card-based content blocks
- Emphasis on readability and touch-friendly actions

## Testing

- Unit tests: `src/**/*.test.ts`
- E2E tests: `tests/e2e/*.spec.ts`

Before running E2E tests, make sure port `5174` is available.
