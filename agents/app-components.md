# Base App Components

Product UI composes App Components. Private shadcn adapters sit behind this boundary. Native semantic elements, Next Image and Next Link belong inside the App layer when they serve an App Component's contract. App Components depend on approved production tokens and responsive resolvers. Keep Feature Components and pages out of primitive internals.

## Files and public APIs

Every directory under `src/components/app/` owns exactly three files. The `.tsx` module contains the public component, props, semantic markup, accessibility behavior and ref handling. The `.styles.ts` module contains CVA recipes or production resolver mappings and the supported style axes. The `.md` file explains defaults, accessibility and usage. Import directly from the public component module.

Use explicit named props. Public components do not accept unrestricted `className`, `style`, or `asChild`. Apply responsive style maps only inside the layout layer. Keep all visual values in the existing Color, Typography, Spacing, Sizing and Effects contracts. Avoid arbitrary values and direct palette classes.

Only AppIcon imports Lucide. Import AppIcon or AppIconButton and pass a registry name. Add approved names to the centralized registry instead of authoring SVG in product UI or importing Lucide from pages and features.

## Colors and states

Color and variant are independent. Raw color uses neutral tokens for decorated variants. Raw variant keeps the inherited foreground and removes decorative fill and borders from surfaces and actions. Raw links retain an underline cue. Static text and surfaces use static token roles. AppButton uses the existing interaction resolver for semantic colors. CVA provides component-specific classes for visual axes such as size or radius.

Use real disabled semantics for controls and preserve the accessible action name during loading. Use `aria-pressed` for toggle actions and keep a persistent visual cue. Keep focus visible. Form validation belongs with future field components. Use AppLink for navigation and AppButton for actions. An icon-only action needs an accessible name.

## Layout and review

AppSectionBox composes section rhythm, one container gutter, and inner padding. Disable its gutters when nested within an already guttered container. Use the same resolved grid owner for AppGrid and AppGridItem. Use a separate owner for a nested grid. Keep keyboard and reading order in meaningful DOM order.

Register each production component in the [single playground](../src/app/review-ui/app-components-showcase.tsx). Show all supported style combinations in both themes and label applicable state examples. Use real interactions for hover, focus and active. See the [playground contract](../src/app/review-ui/README.md).

In Test, run the scoped ESLint rules and `npm run check:app-components`. The structure check verifies file ownership and registration. Browser checks verify the rendered matrices, contrast, keyboard behavior and RTL/LTR. The starter Home, framework infrastructure, and Development specimens have explicit lint exceptions for their existing responsibilities.
