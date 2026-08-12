# Co-located CSS refactor spec

Goal: every `.jsx` file in `frontend/src` gets a co-located `.css` file (same directory, same base name, e.g. `SignupPage.jsx` -> `SignupPage.css`). Move the major styled elements (cards, buttons, inputs, headings, layout wrappers, nav, table cells, modal panels) out of `className` strings into named CSS classes defined with `@apply`. Simple one-off utilities (e.g. `mt-2`, `gap-2`, `text-xs`, `flex`) may stay inline.

## Reference implementation (copy these patterns exactly)
- `frontend/src/pages/LoginPage.css` — the CSS file
- `frontend/src/pages/LoginPage.jsx` — how the JSX imports it and uses the classes

## CSS file rules
1. NO `@tailwind` directives. NO `@layer` wrappers — plain top-level rules only.
2. Use `@apply` with the exact Tailwind utilities that were in the original JSX className. Preserve ALL utilities verbatim; do not invent new ones.
3. Class names must be globally unique across the whole app (all CSS is global). Prefix every class with a short per-file slug, e.g. `signup-card`, `side-nav-item`, `dash-stat-card`.
4. The `material-symbols-outlined` class is a plain CSS class, NOT a Tailwind utility — it cannot be used inside `@apply`. Keep `material-symbols-outlined` in the JSX className and move only the Tailwind utilities into the CSS class.
5. Do NOT define classes for elements that use inline `style={{}}`; keep the inline style.
6. Dynamic/conditional classes (ternaries inside template literals): extract the shared base into a CSS class, keep the conditional variant as an inline utility string OR define both variants as CSS classes and switch the class name. Pick whichever reads cleaner.
7. Keep `disabled:`, `hover:`, `active:`, `focus:`, responsive (`sm:`, `lg:`, `md:`), and dark-mode variants inside `@apply` exactly as written in the original.
8. Order rules roughly in document order of the JSX so it's easy to diff.

## JSX file rules
1. Add `import "./LoginPage.css";` (matching base name) at the top with the other imports.
2. Replace the big/major className strings with the new CSS class names. Keep short one-off utilities inline.
3. Do NOT change any logic, props, handlers, text, imports (other than adding the css import), or component structure. ONLY change className strings and add the css import.
4. The `<style>` or className that references GLASS_* constants from `../constants/auth` may stay as-is (those are JS constants, not inline class strings).

## Verification
After editing each file (or at the end of your batch), run from `frontend`:
`npm run build`
It must succeed. Fix any `@apply` errors (usually an unknown utility — double check the class name in the source JSX). If a rule fails because a utility is genuinely unknown, drop that utility from the @apply and leave it inline in JSX instead.

## Do not touch
- `src/index.css`, `tailwind.config.js`, any config
- Files not assigned to you
