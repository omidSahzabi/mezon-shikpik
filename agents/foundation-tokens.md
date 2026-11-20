# Design System foundation tokens

The [global stylesheet](../src/app/globals.css) owns production typography, spacing, sizing, shape, and effects. The [root layout](../src/app/layout.tsx) registers the local fonts and sets the Persian RTL document context. Use the [Design System playground](../src/app/review-ui/README.md) to inspect the actual utility output. Read the [Color System contract](color-system.md) for semantic colors.

## Typography

- Apply the semantic `text-display`, `text-heading`, `text-heading-sm`, `text-title`, `text-body-lg`, `text-body`, `text-label`, `text-caption`, and `text-helper` utilities. Pick semantic HTML heading levels from document structure.
- Use `font-sans` for Persian, Latin, and technical text. The root layout loads the full Shabnam WOFF2 faces in weights 400, 500, and 700. Apply direction separately from the font.
- Keep Persian tracking neutral and avoid fixed-height text boxes. Use logical alignment and isolate embedded IDs, URLs, and technical strings with `bdi` or an explicit LTR context. Localize displayed measurements, dates, and quantities when applicable. Preserve original identifier and raw form values.

## Spacing and sizing

- Prefer Tailwind steps 0, 1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, and 24. Use multiples of the 8 px design rhythm for regular composition and the 4 px increments for compact details.
- Use `max-w-page`, `max-w-reading`, and `w-sidebar` as width contracts. Use `px-page-gutter`, `py-section`, and `gap-section` for shared responsive spacing. These roles carry dimensions and can be used independently of page layout.
- Use `p-density-*` and `gap-density-*` for density, and `min-h-control-*` or `min-w-control-*` for control minimums. Use `size-control-*` for square specimens or intrinsically square affordances. Keep targets usable and let text controls grow or wrap.

## Shape and effects

- Use `rounded-md` for controls, `rounded-xl` for cards, `rounded-section` for large sections, and `rounded-pill` for the declared pill radius. Use `border`, `border-2`, and `border-4` for standard, emphasis, and marker widths. Pair functional boundaries with the appropriate semantic border color.
- Use `shadow-surface`, `shadow-floating`, or `shadow-modal` where elevation helps. Use `bg-overlay` for backdrops and `surface-glass` for glass with an opaque fallback. Keep `opacity-muted` for decorative content. Use text tokens for readable text.
- Opt into motion with named duration and easing utilities and limit transitions to the affected properties. `effect-hover-lift` and `effect-active-press` respect reduced motion. Keep keyboard focus, contrast, and state cues visible in both themes.

## Extending and verifying

Reuse existing named utilities and aliases before adding values. Keep numeric and color literals in production token declarations. Avoid arbitrary Tailwind values and duplicate registries in the showcase. Add a labeled specimen when a foundation token is introduced or changes behavior.

In Test, inspect type, spacing, and effect measurements at relevant viewport sizes. Check Persian glyphs and mixed direction, text resizing, narrow viewport overflow, theme isolation, glass contrast, keyboard focus, and reduced motion. Keep app-wide source audits scoped to the affected code and report unrelated findings separately.
