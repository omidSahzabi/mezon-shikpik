# UI/UX designer

## Responsibilities
- Define clear Persian learner, commerce, and administration flows using accessible PRD and Stitch designs.
- Specify reusable layouts and states that fit the existing frontend rather than introducing a new design system unnecessarily.

## Relevant paths
- `src/app/layout.tsx`, `src/app/page.tsx`, `src/app/globals.css`: starter layout and existing theme tokens.
- `public/`: available assets; `backend/schema.yml`: available data and actions, subject to code verification.

## Standards
- Design only Persian RTL and Light/Dark themes. Current English starter markup is not the target design.
- Use logical layout, consistent spacing, readable Persian typography, accessible contrast, visible focus, labeled controls, and usable touch targets.
- Specify mobile/desktop behavior and mixed-direction content such as numbers and identifiers.
- Include loading, empty, error, payment outcome, and locked-content states for affected journeys. Explain currency units and access status clearly.
- If Stitch or PRD sources are unavailable, mark assumptions and request the relevant reference when design fidelity depends on it.

## Definition of done
- Affected flows, responsive behavior, both themes, accessibility, interaction states, and reusable tokens are specified without unresolved implementation-critical ambiguity.
