# Forge

TUI dashboard for the Serre AI research platform (Forge). See `ARCHITECTURE.md` for full details.

## Stack
Next.js 16 (App Router), React 19, TanStack Query 5, Tailwind CSS 4, NextAuth v5.

## Critical: React Version Conflict

This repo is an npm workspace. The root `node_modules/` has React 18 (from orchestrator/cli), while `forge/node_modules/` has React 19. This causes runtime errors when packages resolve the wrong copy.

**For tests**: Vitest setup mocks `lucide-react` and `next/link` globally in `src/test/setup.ts` to avoid the conflict. If you add a new test that renders a component importing from a package with React internals, you may need to add it to the mock list.

**For builds**: `next build` resolves correctly — this is only a test-time issue.

## Auth

Sign-in is **hard-coded** to a single owner in `src/lib/auth.ts`:
- GitHub login: `oddurs`
- Email: `oddurs@gmail.com`

This is intentional. There is no env-var-based allowlist — the restriction is in code.

## API Data Contract

The frontend type definitions (in hooks and `*-types.ts` files) describe the *ideal* API shape. The backend may not implement all fields yet. **Always guard optional/array fields** with `?? []` or `?.` before calling `.map()`, `.length`, etc.

```tsx
// BAD — will crash if backend doesn't return checks
{quality.checks.map(...)}

// GOOD
{(quality.checks ?? []).map(...)}
```

## Testing

```bash
npm run test        # vitest run (CI mode)
npm run test:watch  # vitest (watch mode)
```

- **Framework**: Vitest 3 + React Testing Library + jest-dom
- **Config**: `vitest.config.ts`
- **Setup**: `src/test/setup.ts` — jest-dom matchers + global mocks
- **Test utils**: `src/test/utils.tsx` — custom `render()` with QueryClientProvider
- **Convention**: `__tests__/` directories next to the code they test
- Pure function tests use `@testing-library/react` directly; component tests that don't need QueryClient also use it directly. Only use the custom `render()` from `src/test/utils.tsx` when the component needs React Query.

## Key Patterns

### Data fetching
All client data goes through TanStack Query hooks in `src/hooks/`. Every hook calls `apiFetch()` which routes through the Next.js proxy at `/proxy/[...path]` — the browser never holds the API key.

### Adding a new page
1. Create route in `src/app/(app)/<section>/page.tsx` (client component)
2. Add hook in `src/hooks/use-<domain>.ts` wrapping `apiFetch`
3. Export hook from `src/hooks/index.ts`
4. Add nav item in `src/lib/nav-items.ts` if top-level

### Component library
Base primitives in `src/components/ui/` — `Card`, `Button`, `Badge`, `StatusBadge`, `Skeleton`, etc. Domain components go in feature directories (`collective/`, `knowledge/`, etc.).

### Design
Neo-brutalist: sharp corners, monospace (IBM Plex Mono), dark-only, high contrast. CSS tokens in `src/styles/tokens.css`.

## Deploy

```bash
# On VPS after pushing:
cd ~/deepwork/forge && npm run build
sudo systemctl restart deepwork-site
```

Service: `forge-site.service` on port 3000 behind nginx at `forge.serre.ai`.

@AGENTS.md
