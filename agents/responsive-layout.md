# Responsive layout

[responsive-layout.ts](../src/lib/responsive-layout.ts) owns the ordered breakpoint keys, responsive normalization, grid defaults, and validation. [globals.css](../src/app/globals.css) owns the static layout rules. Use the [Layout showcase](../src/app/review-ui/responsive-layout-showcase.tsx) to inspect those rules at the active viewport.

## Breakpoints and inheritance

- The public order is `base`, `sm`, `md`, `lg`, `xl`, `xxl`. Tailwind supplies the thresholds. `base` has no width boundary and `xxl` uses Tailwind’s `2xl` variant.
- `Responsive<T>` accepts a scalar or a sparse breakpoint object. Scalars apply everywhere. Sparse inputs carry the previous resolved value forward. Before the first supplied key, use the property’s base fallback.
- An omitted grid `columns` option uses the full exported default. Explicit sparse columns start at one before their first supplied value. To change one breakpoint in the default sequence, spread the exported defaults into the override.

## Production APIs

| Resolver | Options and defaults | Returned behavior |
| --- | --- | --- |
| `resolveGrid` | `columns` defaults to 1 / 2 / 4 / 6 / 8 / 12. `gap` defaults to spacing step 4. `visibility` defaults to visible. | Static grid class, resolved column counts, and typed responsive style properties. Columns and visible item counts are independent. |
| `resolveGridItem` | Takes its owning grid. `span` defaults to 1, `start` to auto, `order` to 0, and `visibility` to visible. | Static item class and placement values resolved against the parent at every breakpoint. Full span requires auto start and covers the explicit grid. |
| `resolveFlex` | `direction` defaults to row, `align` to stretch, `justify` to start, `wrap` to nowrap, `gap` to step 4, and `visibility` to visible. | Responsive row or column flow with logical alignment and wrapping. |
| `resolveVisibility` | Responsive visible or hidden. Default is visible. | Block wrapper display. Grid and flex callers use their own resolver to restore the expected display type. |
| `resolveContainer` | `width` is page, reading, or fluid. Default is page with gutters. | Centered inline width using the existing foundation width and gutter utilities. |
| `resolveSection` | `spacing` is section, none, or an approved spacing step. Default is section. | Responsive foundation section padding or explicit block-axis padding. |

Use the exported spacing steps. Column, numeric span, and numeric start values must be positive safe integers. Order accepts signed safe integers. The resolver rejects out-of-bounds spans and explicit placements, including at inherited breakpoints. Errors identify the affected property and breakpoint. A valid grid can exceed 12 columns. Grid item visibility does not waive placement validation. Resolve each nested grid separately and pass its result to its own item resolvers.

## Direction, accessibility, and extension

- Inherit document RTL by default. Set `dir` when content genuinely needs a different direction. Grid line 1 is at the inline start. Use inline and block spacing so RTL and LTR work through the same rules.
- Keep meaningful content, focusable controls, and reading sequences in DOM order. Reserve CSS order and explicit visual placement for cases where the change does not alter the expected reading or focus sequence. Responsive hidden removes the element from layout and interaction. Use a separate accessibility pattern for visually hidden text that must remain available.
- Apply each resolver’s static class with its complete style map. Keep breakpoint widths in Tailwind, use the named CSS variants, and avoid dynamic Tailwind class names or local copies of the default grid.
- Future AppContainer and AppSection own width/gutters and block spacing respectively. AppSectionBox composes them. AppBox is a neutral logical wrapper. AppRow, AppColumn, and AppStack share flex and visibility options. AppGrid owns the resolved columns and AppGridItem validates against that owner. These contracts are available for composing those components when their phase begins.

In Test, cover every breakpoint, sparse inheritance, grids above 12 columns, invalid placements, nested grids, both directions, visibility and keyboard order, and narrow-screen overflow. Confirm foundation typography and spacing values still change at the same thresholds.
