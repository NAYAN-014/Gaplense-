---
name: Obsidian Prism
colors:
  surface: '#101415'
  surface-dim: '#101415'
  surface-bright: '#363a3b'
  surface-container-lowest: '#0b0f10'
  surface-container-low: '#191c1e'
  surface-container: '#1d2022'
  surface-container-high: '#272a2c'
  surface-container-highest: '#323537'
  on-surface: '#e0e3e5'
  on-surface-variant: '#b9cacb'
  inverse-surface: '#e0e3e5'
  inverse-on-surface: '#2d3133'
  outline: '#849495'
  outline-variant: '#3b494b'
  surface-tint: '#00dbe9'
  primary: '#dbfcff'
  on-primary: '#00363a'
  primary-container: '#00f0ff'
  on-primary-container: '#006970'
  inverse-primary: '#006970'
  secondary: '#ebb2ff'
  on-secondary: '#520072'
  secondary-container: '#b600f8'
  on-secondary-container: '#fff6fc'
  tertiary: '#f7f4ff'
  on-tertiary: '#2f303a'
  tertiary-container: '#d9d8e6'
  on-tertiary-container: '#5e5e69'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#7df4ff'
  primary-fixed-dim: '#00dbe9'
  on-primary-fixed: '#002022'
  on-primary-fixed-variant: '#004f54'
  secondary-fixed: '#f8d8ff'
  secondary-fixed-dim: '#ebb2ff'
  on-secondary-fixed: '#320047'
  on-secondary-fixed-variant: '#74009f'
  tertiary-fixed: '#e3e1ef'
  tertiary-fixed-dim: '#c6c5d2'
  on-tertiary-fixed: '#1a1b24'
  on-tertiary-fixed-variant: '#454651'
  background: '#101415'
  on-background: '#e0e3e5'
  surface-variant: '#323537'
typography:
  display-lg:
    fontFamily: Space Grotesk
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.1'
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Space Grotesk
    fontSize: 32px
    fontWeight: '600'
    lineHeight: '1.2'
  headline-sm:
    fontFamily: Space Grotesk
    fontSize: 24px
    fontWeight: '500'
    lineHeight: '1.3'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  label-caps:
    fontFamily: Space Grotesk
    fontSize: 12px
    fontWeight: '700'
    lineHeight: '1.0'
    letterSpacing: 0.1em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  grid-gap: 1.5rem
  container-padding: 2rem
  bento-padding: 2rem
  unit-xs: 0.25rem
  unit-sm: 0.5rem
  unit-md: 1rem
  unit-lg: 2rem
---

## Brand & Style

The brand identity of this design system is rooted in technical precision, intellectual clarity, and the futuristic pursuit of mastery. It targets high-performing professionals and lifelong learners who require a diagnostic environment that feels like a sophisticated laboratory for their skills.

The design style utilizes **Glassmorphism** combined with a **Bento Grid** layout. This creates a sense of depth and modular intelligence, where information is categorized into discrete, translucent tiles that seem to float over a deep, atmospheric background. The aesthetic reflects "Academic Futurism"—where the rigor of traditional education meets the cutting edge of data science. Visual elements should feel lightweight yet grounded, using refractive properties to guide the eye toward key insights.

## Colors

The palette is built upon a foundation of **Deep Obsidian (#020408)** and **Midnight Navy (#0A1128)** to provide a canvas of infinite depth. This "dark mode first" approach reduces eye strain during intensive skill assessments.

- **Primary (Electric Cyan):** Used for critical paths, active progress indicators, and primary call-to-action buttons. It represents the "Lens" through which gaps are identified.
- **Secondary (Vibrant Purple):** Used for growth metrics, secondary highlights, and specialized data visualizations.
- **Surface:** The glass layers use a semi-transparent navy fill with a subtle white stroke to simulate the edge of a physical glass pane.
- **Typography:** Pure white is reserved for headings to ensure maximum contrast, while light grays are used for body text to maintain a sophisticated hierarchy.

## Typography

This design system employs a dual-font strategy to balance technical grit with readability. 

**Space Grotesk** is used for all headlines and labels. Its geometric quirks and "tech" influence reinforce the platform's diagnostic nature. For labels and small metadata, it should be used in uppercase with increased letter spacing to mimic laboratory equipment markings.

**Inter** is the workhorse for body copy and data entry. Its neutral, systematic design ensures that complex diagnostic results and educational content remain highly legible against dark, blurred backgrounds.

## Layout & Spacing

The layout follows a strict **Bento Grid** structure. This modular approach organizes information into rectangular "pods" of varying sizes (spanning 1x1, 2x1, or 2x2 units). 

The grid utilizes a 12-column underlying structure with a fixed 1.5rem (24px) gutter. Alignment must be absolute; every glass module should align to the grid tracks to project a feeling of mathematical order. Padding within modules is generous (typically 2rem) to ensure that data visualizations have "room to breathe" within their glass enclosures.

## Elevation & Depth

Hierarchy is achieved through **Backdrop Blurs** rather than traditional shadows. 

1.  **Base Layer:** The solid Obsidian background.
2.  **Surface Layer:** Bento grid items with a `backdrop-filter: blur(20px)` and a subtle 1px border (`glass_stroke`).
3.  **Elevated Layer:** Overlays and dropdowns use a higher blur (40px) and a slightly lighter fill to appear physically closer to the user.

Shadows, when used, are restricted to "Glows." Primary buttons do not cast black shadows; they cast a soft Cyan or Purple diffusion to simulate light emitting from the element.

## Shapes

The shape language combines the precision of a grid with the approachability of modern software. A consistent **0.5rem (8px)** corner radius is applied to all standard grid modules. For larger interactive cards, use **1rem (16px)** to emphasize their container status.

Interactive elements like buttons and input fields should strictly follow the 0.5rem radius. Progress bars and diagnostic "pills" may use a full circular radius (pill-shaped) to distinguish them from structural layout components.

## Components

### Buttons
Primary buttons use a solid gradient from Cyan to a slightly darker teal, with a white "Inner Glow" on hover. Secondary buttons are "Ghost" style, featuring only the glass border and the accent-colored text.

### Bento Cards
The core component. Each card must have a `backdrop-filter`, a `border-radius`, and a subtle `linear-gradient` border (from top-left white-alpha to bottom-right transparent) to simulate light hitting the glass edge.

### Diagnostic Inputs
Input fields are translucent with a bottom-only Cyan border that glows when focused. Typography within inputs should be monospaced where technical data is required.

### Skill Chips
Small, high-contrast badges used to denote specific skill tags. They use the Purple accent with 10% opacity for the background and 100% opacity for the text.

### Progress Orbs
A custom component for GapLens: circular glass progress indicators that fill with a liquid-like Cyan gradient as the user’s skill proficiency increases.