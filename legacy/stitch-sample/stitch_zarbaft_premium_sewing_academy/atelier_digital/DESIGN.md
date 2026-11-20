---
name: Atelier Digital
colors:
  surface: '#f8f9ff'
  surface-dim: '#ccdbf3'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e6eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d5e3fc'
  on-surface: '#0d1c2e'
  on-surface-variant: '#5b4041'
  inverse-surface: '#233144'
  inverse-on-surface: '#eaf1ff'
  outline: '#8f6f70'
  outline-variant: '#e3bdbf'
  surface-tint: '#bb0f3a'
  primary: '#95002a'
  on-primary: '#ffffff'
  primary-container: '#be123c'
  on-primary-container: '#ffd0d2'
  inverse-primary: '#ffb2b7'
  secondary: '#565e74'
  on-secondary: '#ffffff'
  secondary-container: '#dae2fd'
  on-secondary-container: '#5c647a'
  tertiary: '#44494d'
  on-tertiary: '#ffffff'
  tertiary-container: '#5c6164'
  on-tertiary-container: '#d8dce0'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#ffdadb'
  primary-fixed-dim: '#ffb2b7'
  on-primary-fixed: '#40000d'
  on-primary-fixed-variant: '#920029'
  secondary-fixed: '#dae2fd'
  secondary-fixed-dim: '#bec6e0'
  on-secondary-fixed: '#131b2e'
  on-secondary-fixed-variant: '#3f465c'
  tertiary-fixed: '#dfe3e7'
  tertiary-fixed-dim: '#c3c7cb'
  on-tertiary-fixed: '#171c1f'
  on-tertiary-fixed-variant: '#43474b'
  background: '#f8f9ff'
  on-background: '#0d1c2e'
  surface-variant: '#d5e3fc'
typography:
  display-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 60px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Plus Jakarta Sans
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Plus Jakarta Sans
    fontSize: 28px
    fontWeight: '600'
    lineHeight: 36px
  title-md:
    fontFamily: Plus Jakarta Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 30px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 26px
  label-md:
    fontFamily: Geist
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.02em
  label-sm:
    fontFamily: Geist
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 24px
  lg: 40px
  xl: 64px
  container-max: 1280px
  gutter: 24px
  sidebar-width: 280px
---

## Brand & Style

The brand identity centers on the intersection of traditional craftsmanship and modern technology. It evokes the feeling of a high-end fashion atelier—precise, curated, and exclusive—while maintaining the efficiency of a 2026 SaaS platform. The target audience is discerning creators who value both technical mastery in sewing and a sophisticated digital learning environment.

The design style is **Minimalist-Premium**. It leverages expansive white space, precise 8pt grid alignment, and subtle motion to create a "breathable" interface. While the structure is rooted in modern SaaS patterns (inspired by Linear and Apple), the execution remains soft and human-centric, avoiding the coldness of purely industrial tech aesthetics.

**Key visual principles:**
- **Intentional Restraint:** Every element must serve a functional purpose; decorative fluff is eliminated.
- **RTL-First Architecture:** The layout logic is built from right-to-left, ensuring that motion and hierarchy feel native to the Persian script.
- **High-Fidelity Finishes:** Soft blurs and micro-interactions provide a tactile, luxurious feel.

## Colors

The palette is anchored in a high-contrast "Ink and Rose" theme. The use of white is aggressive, acting as the primary canvas to allow the rich crimson accents to draw immediate focus to pedagogical actions and conversion points.

- **Primary (#BE123C):** A sophisticated deep rose/red. Used exclusively for primary calls to action, active states, and critical brand highlights.
- **Neutral High (#0F172A):** An "Ink" black used for headings and primary navigation to ensure maximum legibility for Persian glyphs.
- **Neutral Mid (#475569):** A "Slate" gray for body copy, providing enough contrast for long-form educational reading without the harshness of pure black.
- **Surface (#F9FAFB):** A very subtle off-white used for card backgrounds and section containers to create depth against the pure white (#FFFFFF) page background.

## Typography

While the variables specify Latin fallback fonts, the implementation must use **Peyda** or **Estedad** for Persian text. These fonts feature the modern, high-x-height, and balanced curves required for a luxury SaaS aesthetic.

- **Headlines:** Use semi-bold weights with tight tracking. Headlines should feel authoritative yet graceful.
- **Body:** Prioritize line height (1.6x minimum) for Persian script to prevent overlapping "dots" and accents, which is crucial for educational content.
- **Monospace/Labels:** Use **Geist** for UI labels, metadata, and measurements in the sewing patterns. Its technical precision complements the artisanal nature of the platform.
- **RTL Alignment:** All text-alignments must be `right` by default. Ensure that numerical values (measurements/steps) are rendered with Persian numerals where appropriate for the locale.

## Layout & Spacing

The layout utilizes a **12-column fluid grid** for the main content area, with a fixed-width RTL sidebar for dashboard views. 

- **8pt Grid:** All dimensions, padding, and margins must be multiples of 8px to maintain mathematical harmony.
- **RTL Flow:** The primary navigation resides on the right. Content "starts" from the right and flows left. Breadcrumbs, back buttons, and chevron icons must be mirrored (e.g., a "back" arrow points right `→`).
- **The "Master" View:** For course players, use a "theater mode" layout where the video takes precedence, with a scrollable curriculum list on the left (the secondary position in RTL).
- **Responsive Behavior:** 
    - **Desktop:** Sidebar visible, 40px page margins.
    - **Tablet:** Sidebar collapses to a rail or hamburger menu, 24px margins.
    - **Mobile:** Single column flow, 16px margins, bottom-sheet patterns for filters and AI chat.

## Elevation & Depth

Depth is achieved through a combination of **Tonal Layering** and **Soft Ambient Shadows**. We avoid heavy borders in favor of subtle contrast.

- **Level 0 (Background):** Pure white (#FFFFFF).
- **Level 1 (Cards/Sidebar):** Off-white (#F9FAFB) with a 1px border of #F1F5F9.
- **Level 2 (Dropdowns/Modals):** Pure white with a "Lux Shadow": `0 10px 15px -3px rgba(15, 23, 42, 0.05), 0 4px 6px -4px rgba(15, 23, 42, 0.05)`.
- **Glassmorphism:** Use `backdrop-filter: blur(12px)` with a 70% white tint for sticky headers and the AI Assistant chat bubble to maintain a sense of lightness and transparency.

## Shapes

The shape language is generous and "friendly-professional." 

- **Standard Elements:** Buttons and input fields use a `0.5rem` (8px) radius.
- **Containers:** Content cards and feature blocks use a `1rem` (16px) radius to feel more substantial.
- **Large Sections:** Hero areas or dashboard panels use a `1.5rem` (24px) radius.
- **AI Chat:** Bubbles for the AI assistant should have an asymmetric rounding (e.g., 16px on three corners and 4px on the corner pointing to the avatar) to distinguish speakers clearly in RTL flow.

## Components

### Buttons
- **Primary:** Background #BE123C, Text #FFFFFF. No border. Smooth 200ms transition on hover to a slightly darker shade.
- **Secondary:** Background #F1F5F9, Text #0F172A. High-end, "ghost" feel.
- **Tertiary:** Text #BE123C with an underline that appears on hover.

### Cards
- White background, 1px #F1F5F9 border. 
- On hover: Apply the Level 2 shadow and shift the card -2px vertically.
- Use generous internal padding (min 24px).

### Input Fields
- Subtle #F9FAFB background with a bottom-only 2px border that turns #BE123C on focus. This mimics the "sketching" feel of sewing patterns.
- Labels should be small, bold, and placed above the field, right-aligned.

### AI Assistant (Tailor AI)
- Floating action button in the bottom-left (opposite of the primary navigation flow).
- Chat interface uses a "blurred pane" aesthetic.
- Use a distinct typeface (Geist) for AI-generated code or sewing measurements to differentiate from human conversation.

### Navigation (Sidebar)
- Active states indicated by a thick 4px vertical bar on the **right** edge of the menu item and a soft #F1F5F9 background tint.
- Icons should be "duotone" style, using #475569 with a secondary primary-colored accent within the icon.