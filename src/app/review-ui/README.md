# Design System playground

`/review-ui` is a development route for reviewing the real Design System in one place. The server page returns a not-found response outside Development. Keep the page Persian and RTL, and keep technical token and variant names isolated in LTR text. Follow the app’s production theme for Light and Dark previews.

## Sources and sections

- Consume production CSS variables and utilities through the app stylesheet. The Colors section resolves swatches in explicit Light and Dark scopes and imports the shared color variant contract. Add new swatches alongside the corresponding production token changes. Import production token metadata directly where available.
- Import original App Components and any exported variant options or types from their production modules. Never copy or mock a component, hardcode color values, or maintain a second palette. Preview data can represent supported use cases, while the rendered component and its styles must come from production.
- Keep Colors, Typography, Spacing & Sizing, Shape & Effects, Layout, and App Components as reusable sections on this route. Add a section when its production source exists. Use one compact responsive grid per group with visible names and labels. Keep combinations visible together without tabs or dropdowns. Keep preview layout styles separate from the component’s own styles.
- For foundation tokens, use neutral specimens with real production utility classes. List the class names and read CSS values from the rendered specimens. Include responsive measurements, both theme contexts for color-dependent effects, and a reduced-motion check. A specimen button can demonstrate an effect without standing in for an App Component. See the [foundation contract](../../../agents/foundation-tokens.md).
- For Layout, import the production resolvers and breakpoint keys. Use neutral content to demonstrate inheritance, logical placement, nesting, flex flow, and visibility. Use the production CSS breakpoint marker instead of a second width table in the showcase. Keep RTL and LTR cases visible together, and demonstrate visual reordering only with non-interactive specimens. See the [responsive layout contract](../../../agents/responsive-layout.md).

## Registering an App Component

1. Add the direct production import and a named entry to `appPreviews` in `app-components-showcase.tsx`. Use a local client preview section only when interactive examples need client state. During Test, run `npm run check:app-components` to verify the three-file structure and registry coverage. Review the [Base App Component contract](../../../agents/app-components.md).
2. Show the full supported color × variant × size matrix, with every combination visible at once. Use production metadata for the axes when available. Document which combinations are unsupported if the production contract excludes them.
3. Include default and raw where supported. Show hover, active, and focus through the real interactions or a production-supported state API. Show disabled, loading, and error through the real props or usage paths where applicable. Never add review-only states to a production component just to render a preview.
4. Verify both themes, narrow and wide viewports, RTL, accessible names, keyboard operation, visible focus, and text and control contrast. Make loading and error understandable without relying on color alone.

Adding or changing an App Component includes updating its preview matrix in the same task. Keep labels, supported axes, and examples aligned with its production contract. During Test, verify the development route renders and a direct request to `/review-ui` on the production build returns HTTP 404. Keep build execution in the Build stage.
