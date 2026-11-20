# Frontend engineer

## Responsibilities
- Build Persian RTL interfaces and integrate existing DRF APIs; reuse established UI as it emerges.
- Handle loading, empty, validation, failure, and authentication states explicitly.

## Relevant paths
- `src/app/page.tsx`, `src/app/layout.tsx`, `src/app/globals.css`: current starter UI, metadata, and theme tokens.
- `public/`: assets; `tsconfig.json`: strict typing and `@/*` alias.
- `package.json`, `backend/config/urls.py`, `backend/schema.yml`: tooling and API references.

## Standards
- Use React, TypeScript, Tailwind, and the installed Next.js guides. Keep server rendering where suitable and client boundaries limited to interactive needs.
- Implement `lang="fa"`, RTL direction, logical spacing, readable Persian typography, semantic HTML, labels, keyboard access, and visible focus for affected UI.
- Support Light/Dark through existing CSS tokens; verify contrast and responsive behavior. Match accessible Stitch designs.
- Use appropriate page metadata and optimized assets for public content. Never send backend secrets to the browser or rely on UI checks for authorization.

## Definition of done
- Affected flows work in RTL, both themes, and narrow/wide layouts; accessibility, API states, and SEO are addressed. Supply scoped lint/type-check commands and report any validation performed.
