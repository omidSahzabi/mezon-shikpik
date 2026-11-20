<!-- BEGIN:nextjs-agent-rules -->
# This is NOT the Next.js you know

This version has breaking changes — APIs, conventions, and file structure may all differ from your training data. Read the relevant guide in `node_modules/next/dist/docs/` before writing any code. Heed deprecation notices.
<!-- END:nextjs-agent-rules -->

## Project

Mezon Shik Pik is a Persian RTL LMS and digital commerce platform for sewing courses, patterns, and bundles. Support Persian only and Light/Dark themes; exclude AI product features from the MVP.

Preserve the Next.js App Router + TypeScript + Tailwind frontend (`src/app/`) and Django/DRF REST backend (`backend/`). PostgreSQL, Redis, Celery, Docker Compose, and Nginx support the backend. The frontend is currently a starter, not a completed RTL product.

## Working rules

- Before implementation, inspect only relevant files and applicable instructions. Prefer actual code over stale README claims; flag requirement conflicts.
- Follow the PRD and Stitch designs when accessible. Neither is present locally; request the relevant source when needed rather than inventing requirements or design decisions.
- Prefer existing components and established patterns. Keep code clean, reusable, and narrowly scoped; avoid unnecessary dependencies, refactoring, and abstractions.
- Prioritize accessibility, security, performance, SEO, and developer experience. Validate inputs and enforce permissions on the backend.
- Never expose secrets or modify production data. Do not read or print secret files, credentials, tokens, or database dumps.
- For simple terminal checks, give the developer scoped commands instead of expensive analysis. Report checks actually run, deferred checks, and limitations; never claim unperformed validation.
- These role files are references, not automatically activated agents. Load only the role file(s) relevant to the task. Do not configure experimental multi-agent execution or external tools.

## Git branch policy

- Before making the first change for a new task, check the current branch. Start or reuse a branch dedicated to that task. Use a descriptive prefix such as `feature/`, `fix/`, `docs/`, or `chore/`, as appropriate.
- Do not implement or commit new task work directly on the default branch (`master` in this repository, or `main` if renamed). If you are on the default branch or a branch for an unrelated task, switch to the appropriate task branch before editing.
- In Review and Plan, inspect the current branch without changing it. Create or switch branches when implementation begins.

## User-controlled workflow stages

- The user names the active stage in their prompt. Carry it across turns until the user changes it. The user may select any stage directly. Stages have no required order or prerequisites. Finishing one stage does not activate another. If no stage has been established and the request needs one, ask which stage applies before taking stage-specific action.
- **Review:** Read and inspect relevant files and evidence. Report findings, risks, and open questions. Do not write code, edit files, run tests, or build.
- **Plan:** Read and inspect relevant files and evidence. Do not write code, edit files, run tests, or build. End with a numbered list of concrete implementation steps for the user to review.
- **Steps:** Execute only the current step in the plan agreed with the user. After each step, report what changed and any remaining issues. Ask for confirmation before starting the next step and wait for an explicit response. After the last step, report completion and wait for the user to select a stage.
- **Test:** Run all tests and test-related checks for the task in this stage. Report what passed, failed, or could not run. Record any fixes needed for the user to authorize in Steps.
- **Build:** Run the requested build in this stage and report its result and any blockers.

- **Plan acceptance criteria:** For each step, identify the affected area, the observable outcome, and how it will be verified in Test. If an unresolved question affects product behavior, an API contract, or data, ask the user before finalizing the plan.
- **Steps scope:** Limit changes to the approved step. If new work becomes necessary, such as a migration or an API contract change outside the approved scope, explain the impact and get the user's approval before adding it to the plan or carrying it out.
- **Completion claims:** Report implementation, test verification, and build success separately. Claim each only when that work actually happened. State any checks that remain pending.

Keep work clean, maintainable, and aligned with established project conventions and best practices in every stage. If a requested approach is poor practice or would make the code harder to maintain, flag it before proceeding. Explain the concrete downside and suggest a cleaner approach. Keep the warning within the permissions of the active stage.

## Role routing

| Task | Reference |
| --- | --- |
| Scope, requirements, acceptance criteria | [Product owner](agents/product-owner.md) |
| Architecture, boundaries, API contracts | [Software architect](agents/software-architect.md) |
| Next.js UI and API integration | [Frontend engineer](agents/frontend-engineer.md) |
| Color tokens, variants, or color consistency checks | [Color system](agents/color-system.md) |
| Typography, spacing, sizing, shape, or effects tokens | [Foundation tokens](agents/foundation-tokens.md) |
| Breakpoints, responsive grid, or layout contracts | [Responsive layout](agents/responsive-layout.md) |
| Base App Components, UI layer boundaries, or component preview coverage | [Base App Components](agents/app-components.md) |
| Django APIs, domain logic, persistence | [Backend engineer](agents/backend-engineer.md) |
| RTL flows, visual design, accessibility | [UI/UX designer](agents/ui-ux-designer.md) |
| Infrastructure, configuration, delivery | [DevOps engineer](agents/devops-engineer.md) |
| Acceptance, regression, validation | [QA engineer](agents/qa-engineer.md) |
| Database schema, relationships, integrity, RBAC, reporting, migrations | [Database references](agents/database.md) |
