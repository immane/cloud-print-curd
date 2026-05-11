# Admin Frontend Architecture (Research)

This document outlines a compact, practical frontend architecture for a PC/web admin/manage UI that pairs with a separate FastAPI backend (OpenAPI/REST). It is intended to be actionable and ready to drop into docs/research/admin_frontend_architecture.md.

Summary / Project constraints and goals
- Separate frontend (single-page or server-rendered hybrid) talking to FastAPI REST (OpenAPI).
- Lightweight admin/manage interface optimized for desktop (PC/web).
- Priorities: developer productivity, accessibility (a11y), maintainability, and easy deployment to a single server or static host.
- Keep the build small enough for static hosting (Netlify/Vercel/S3) but allow Docker/nginx deployment when needed.

Framework comparison (short, actionable)
- React (Vite; CRA deprecated for new projects)
  - Strengths: vast ecosystem, best library support for admin UIs; mature tooling (Vite).
  - Learning curve: low–medium.
  - Use-cases: standard admin dashboards, custom tooling.
  - Maturity: excellent.
  - Perf: good; bundle size controllable with Vite/code-splitting.
  - Pros/Cons: best ecosystem but can require many libraries.
  - Docs: https://reactjs.org/ • Vite + React: https://vitejs.dev/guide/
- Next.js (App Router, minimal SSR/ISR)
  - Strengths: file-based routing, optional SSR for SEO or initial data.
  - Learning curve: medium.
  - Use-cases: admin panels that need server-rendered pages or integrated auth middleware.
  - Maturity: excellent.
  - Perf: good; built-in image optimization and edge options.
  - Pros/Cons: heavier; more features than needed for pure admin SPA.
  - Docs: https://nextjs.org/docs
- Vue 3 (+ Vite)
  - Strengths: approachable, great DX, single-file components.
  - Learning curve: low–medium.
  - Use-cases: admin UIs, rapid prototyping.
  - Maturity: excellent.
  - Perf: very good.
  - Pros/Cons: fewer React-specific libs, but solid component libraries.
  - Docs: https://v3.vuejs.org/
- SvelteKit
  - Strengths: small bundles, very fast runtime.
  - Learning curve: medium (new mental model).
  - Use-cases: ultra-lightweight admin, high perf.
  - Maturity: improving quickly.
  - Perf: excellent (small output).
  - Pros/Cons: fewer off-the-shelf admin templates.
  - Docs: https://kit.svelte.dev/
- SolidStart (optional)
  - Strengths: high perf, reactive primitives.
  - Learning curve: medium–high.
  - Use-cases: highly interactive dashboards with minimal runtime.
  - Docs: https://www.solidjs.com/docs
- Angular
  - Strengths: batteries-included, strong typing and structure.
  - Learning curve: steep.
  - Use-cases: large enterprise admin apps with long-term maintenance.
  - Maturity: mature.
  - Pros/Cons: heavier and more opinionated.
  - Docs: https://angular.io/docs

UI & component libraries for admin UIs
- Ant Design (React)
  - Language: enterprise, data-dense.
  - Components: complete (tables, forms, modals, data-grid-like components).
  - Theming: built-in token/theme support.
  - Ergonomics: high for enterprise apps.
  - https://ant.design/
- Material UI (MUI)
  - Language: Material Design.
  - Components: complete; DataGrid as paid or open community version.
  - Theming: excellent.
  - https://mui.com/
- Chakra UI
  - Language: accessible primitives, design system friendly.
  - Components: good; may need add-ons for complex grids.
  - Theming: easy and composable.
  - https://chakra-ui.com/
- Mantine
  - Language: modern, ergonomic.
  - Components: highly complete with hooks and utilities.
  - Theming: strong.
  - https://mantine.dev/
- PrimeVue / Element Plus (Vue)
  - Language: enterprise (Prime) / conventional (Element).
  - Components: full-featured tables, forms, dialogs.
  - Theming: available.
  - https://primefaces.org/primevue/ • https://element-plus.org/
- Tailwind CSS + Headless UI (or DaisyUI)
  - Language: utility-first + accessible primitives.
  - Components: need composition — very flexible.
  - Theming: excellent (design controlled in CSS).
  - Ergonomics: low-level but very fast once team is familiar.
  - https://tailwindcss.com/ • https://headlessui.com/

State management & data fetching
- TanStack Query (React Query)
  - Best for server state: caching, background refresh, pagination, optimistic updates, invalidation hooks.
  - Patterns: use useQuery with queryKey [resource, page, filters], keepPreviousData for pagination, useMutation with onMutate/onError/onSettled for optimistic updates and invalidation.
  - Docs: https://tanstack.com/query
- SWR
  - Simpler caching/refetch; good for small apps.
  - https://swr.vercel.app/
- Redux / Redux Toolkit
  - Best for complex client-only state; combined with RTK Query for API.
  - https://redux.js.org/
- Zustand / Jotai / Pinia (Vue)
  - Lightweight primitives for local state; Pinia is the de-facto for Vue.
  - Zustand: https://zustand-demo.pmnd.rs/ • Pinia: https://pinia.vuejs.org/
Recommendations for REST/OpenAPI:
- Use TanStack Query (or RTK Query) for server state (lists, item cache).
- For paginated lists: pageNumber/pageCursor as part of queryKey; keepPreviousData to avoid UI jumps.
- Optimistic update: useMutation.onMutate -> update cache -> rollback onError.
- Background refresh: set refetchInterval or onFocus to keep data fresh.
- Cache invalidation: call queryClient.invalidateQueries(['resource']) after mutations.

Forms & validation
- React: React Hook Form + Zod (fast, minimal re-render, schema-based validation).
  - Docs: https://react-hook-form.com/ • https://zod.dev/
- Vue: Vee-validate + Zod/Yup.
  - Docs: https://vee-validate.logaretm.com/
File uploads with presigned URLs (recommended flow)
1. Frontend validates form (React Hook Form + Zod).
2. Ask backend for a presigned URL by sending filename/content-type/size.
3. Upload file directly to S3 (PUT or POST form) using the presigned URL.
4. After successful upload, notify backend (or include S3 key in create/update API) to associate file with resource.
Security tips: short TTL for presigned URLs, enforce server-side ACLs, validate file metadata on backend.

Build & tooling
- Build: Vite recommended for fast dev and production builds.
  - Docs: https://vitejs.dev/
- Bundling & code-splitting: dynamic imports for large routes; Vite supports rollup-based code splitting.
- Env vars: use .env.[mode] files and prefix (Vite: VITE_).
- OpenAPI client generation:
  - openapi-typescript (TypeScript types): https://github.com/drwpow/openapi-typescript
  - openapi-generator or openapi-typescript-codegen to generate clients.
- TypeScript: strongly recommended for maintainability.

Testing & QA
- Unit/component tests: Vitest (Vite-friendly) or Jest.
  - Vitest: https://vitest.dev/
- Component testing: Testing Library (React Testing Library / Vue Testing Library).
  - https://testing-library.com/
- E2E: Playwright (recommended) or Cypress.
  - Playwright: https://playwright.dev/
- Accessibility: axe (jest-axe / axe-core) and automated scans.
  - axe: https://github.com/dequelabs/axe-core
- API & S3 mocks: MSW for REST and S3 endpoints; local mock server for integration tests.
  - MSW: https://mswjs.io/

Deployment options
- Static hosting (recommended for SPA): Netlify, Vercel, S3+CloudFront.
  - Netlify: https://www.netlify.com/ • Vercel: https://vercel.com/
- Dockerized app behind nginx for static assets (single VPS): build static, serve via nginx.
- Single-VPS: serve static files with nginx or simple static-server.
- CI pipeline steps: install, lint, typecheck, test (unit + e2e), build, deploy artifact.
- CORS & auth cookie notes:
  - If using bearer tokens (Authorization header), CORS must allow Authorization header.
  - If using httpOnly cookies from backend: backend & frontend may need same site or proxy (recommended: deploy frontend and backend under same domain or use reverse proxy to avoid CORS cookie issues).
  - For admin apps, Authorization header with short-lived access token + refresh token rotation is common.

Security & best practices
- Secure tokens: use httpOnly cookies for refresh tokens where possible; access tokens in memory only.
- CSRF: if using cookies, implement CSRF tokens or SameSite cookie policies.
- CORS: restrict allowed origins to admin host(s) only.
- Input sanitization: validate/escape both client and backend; treat backend as source of truth.
- RBAC: enforce on backend; surface roles in UI (hide/show actions), but never rely on client enforcement.
- Audit logs: log admin actions server-side.
- Rate limiting UX: show clear, actionable errors and countdowns if throttled.
- Protect presigned URLs: short TTL, single-use when possible.

3 Recommended minimal stacks
- A) Minimal (fast to bootstrap)
  - React + Vite + Ant Design + TanStack Query + React Hook Form + TypeScript
  - Deploy: Static deploy (Netlify)
  - Diagram (high level): Browser -> Static SPA (Netlify) -> FastAPI (OpenAPI) -> S3
- B) Robust (production-ready)
  - React + Vite/Next + Mantine + TanStack Query + Zustand + Playwright + Docker -> nginx
  - Deploy: Docker image behind nginx or cloud VM with CI pipeline
  - Diagram: Browser -> nginx (serves SPA / reverse proxy) -> FastAPI -> S3
- C) Lightweight alternative
  - Vue 3 + Vite + Element Plus + Pinia + TanStack Query (or direct fetch)
  - Deploy: Vercel/Netlify
  - Diagram: Browser -> Static SPA -> FastAPI -> S3

Links (by section)
- Frameworks: React (https://reactjs.org/), Next.js (https://nextjs.org/), Vue 3 (https://v3.vuejs.org/)
- UI libs: Ant Design (https://ant.design/), MUI (https://mui.com/), Tailwind (https://tailwindcss.com/)
- Data fetching: TanStack Query (https://tanstack.com/query), SWR (https://swr.vercel.app/)
- Forms & validation: React Hook Form (https://react-hook-form.com/), Zod (https://zod.dev/)
- Tooling: Vite (https://vitejs.dev/), openapi-typescript (https://github.com/drwpow/openapi-typescript)
- Testing: Vitest (https://vitest.dev/), Playwright (https://playwright.dev/), MSW (https://mswjs.io/)
- Deployment/security: Netlify (https://www.netlify.com/), OWASP Top 10 (https://owasp.org/www-project-top-ten/)

Final recommendation & minimal bootstrap checklist
---------------------------------------------
Preferred stack: A) React + Vite + Ant Design + TanStack Query + React Hook Form + TypeScript — best balance of speed, ecosystem, a11y, and easy static deployment.

Minimal bootstrap checklist
- Files & layout
  - src/main.tsx (React entry), src/App.tsx, src/routes (pages), src/api (OpenAPI client or fetch wrappers)
  - src/components/{Table,Form,Modal,Auth}
- Scripts (package.json)
  - "dev": "vite"
  - "build": "vite build"
  - "preview": "vite preview"
  - "lint": "eslint ."
  - "test": "vitest"
  - "openapi:gen": "openapi-typescript ./openapi.json --output src/api/openapi-types.ts"
- Env / config
  - .env.development / .env.production (VITE_API_BASE_URL)
- CI (example pipeline)
  - install deps
  - lint + typecheck
  - run unit tests
  - build (vite)
  - deploy (Netlify/Vercel/Upload artifact to server)
- Quick API integration
  - Generate types from OpenAPI
  - Create an API layer that wraps fetch / axios and sets Authorization header + error handling
  - Use TanStack Query for server data and cache control

This should get a lean, maintainable admin UI talking to your FastAPI backend quickly while preserving production concerns (a11y, security, testing, and easy deploy).
