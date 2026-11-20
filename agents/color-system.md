# Color system

The production palette, theme mappings, shadcn aliases, and Tailwind aliases live in [globals.css](../src/app/globals.css). Keep one literal per swatch and reference shared values through CSS variables. `--brand-primary` identifies the brand in either theme. `--primary` and `--primary-solid` follow the active theme. The root follows system preference unless it carries an explicit theme class. A nested `.light` or `.dark` scope resolves its own colors.

## Semantic mappings

| Purpose | Use |
| --- | --- |
| Canvas and elevated surfaces | `bg-background text-foreground`, `bg-surface`, `bg-card text-card-foreground`, `bg-popover text-popover-foreground` |
| Quiet surfaces and copy | `bg-muted text-muted-foreground`, `text-copy-primary`, `text-copy-secondary`, `text-copy-muted`, `text-copy-disabled` |
| Boundaries and overlays | `border-border` for decoration, `border-input` for functional input boundaries, `outline-ring` for focus, `bg-overlay` for dialog backdrops |
| Solid shadcn actions | `bg-primary text-primary-foreground`, `bg-secondary text-secondary-foreground`, `bg-destructive text-destructive-foreground` |
| Accent and status | shadcn accent maps to soft and strong. Use the explicit solid and on-solid roles for full fills. Success, error, warning, and info use the same role names. Destructive aliases the error palette. |

## Variants and states

Use the typed resolver and exported axes from [color-variants.ts](../src/lib/color-variants.ts). Keep complete Tailwind classes in source so Tailwind can discover them.

- `raw` inherits text and keeps a transparent fill and border, including hover and active. Keyboard focus retains a visible outline.
- `outline` pairs a solid semantic border with strong text. `filled` pairs a soft fill and soft edge with strong text. Use a stronger edge when it is essential to identify a control.
- `fullFilled` pairs a solid fill with on-solid text. Hover and active change the fill and border while preserving the contrasting text role.
- Use native disabled semantics or the appropriate ARIA contract and pass the disabled state to the resolver. For ARIA-disabled interactions, the caller must prevent activation. Add selected semantics and a visible check or marker in the caller. The shared toggle styling reads `aria-pressed`.
- On an invalid field, set `aria-invalid`, pass the invalid state to the resolver, and associate the error message with the field. The colored variants use an error border and preserve the focus outline. Use a colored variant for a validation boundary.

## Consistency and verification

Keep hex values, direct Tailwind palette classes, and arbitrary color values out of component styles. During Test, search `src/` for color literals and direct palette utilities, excluding the canonical declarations in `globals.css`. Review matches in inline styles, SVG fills and strokes, and utility class strings. Keep historical Stitch exports outside this audit.

Verify the production tokens and all supported combinations in both themes on the development showcase. Check hover, active, keyboard focus, selected, disabled, and invalid behavior. Target at least 4.5:1 for normal text and 3:1 for functional boundaries and indicators where required. Check actual adjacent surfaces and keep selection and validation understandable without hue alone. Follow the [playground contract](../src/app/review-ui/README.md) when adding production components.
