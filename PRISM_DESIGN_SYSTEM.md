# Tekshila Prism - Design System Documentation

## Overview

**Prism** is the "Refracted Intelligence" design system for Tekshila - a cinematic engineering aesthetic that transforms the UI into precision optical components.

## Design Philosophy

We treat the UI as a series of precision lenses and glass plates:
- **Refracted Glass**: Panels distort what's behind them
- **Dark Lab Aesthetic**: Deep void backgrounds with subtle noise
- **Laser Crimson**: Reserved exclusively for primary actions
- **Micro-Interactions**: Every interaction has purpose and polish

## Color Palette

### Canvas (Backgrounds)
- `--void`: `#050505` - Deep Void (darker than Onyx)
- `--surface`: `#0A0A0A` - Surface cards with 3% noise texture

### Accents
- **Laser Crimson**: `#F43F5E` to `#E11D48` - Primary actions only
- **Electric Quicksilver**: Grayscale gradients for metallic feel

### Glass Effects
- `--glass-stroke`: `rgba(255, 255, 255, 0.08)` - Subtle borders
- `--glass-highlight`: `rgba(255, 255, 255, 0.2)` - Top-light reflection

## Typography

### Font Stack
- **Display/Headers**: `Space Grotesk` (500, 700) - Letter-spacing: -0.03em
- **UI/Body**: `Plus Jakarta Sans` (400, 500) - High readability
- **Code/Data**: `JetBrains Mono` - Essential for dev tools
- **Micro-Labeling**: Uppercase, 0.2em spacing, 10px size

## Components

### GlassCard
Refracted glass panel with spotlight hover effect:
```tsx
<GlassCard spotlight className="p-6">
  Content here
</GlassCard>
```

### MagneticButton
Button with magnetic hover effect and glow:
```tsx
<MagneticButton variant="primary" size="lg">
  Click me
</MagneticButton>
```

Variants: `primary` | `secondary` | `ghost`
Sizes: `sm` | `md` | `lg`

### GlassSidebar
Fixed glass navigation sidebar:
```tsx
<GlassSidebar />
```

## File Structure

```
app/
├── globals.css          # Design system CSS variables
├── layout.tsx           # Root layout with noise overlay
├── page.tsx             # Landing page with hero
└── dashboard/
    ├── layout.tsx       # Dashboard shell
    └── page.tsx         # Documentation generator

components/
├── GlassCard.tsx        # Refracted glass card
├── MagneticButton.tsx   # Magnetic hover button
├── GlassSidebar.tsx     # Glass navigation
├── HeroScene.tsx        # Three.js liquid chrome torus
└── WaveformVisualizer.tsx # Audio waveform animation

hooks/
└── useSound.ts          # UI sound effects

lib/
└── utils.ts             # Utility functions (cn, etc.)
```

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Run development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000)

## Tech Stack

- **Next.js 15** (App Router)
- **Tailwind CSS 3.4**
- **Framer Motion** - Layout transitions
- **Three.js / React Three Fiber** - 3D scene
- **@react-three/drei** - MeshTransmissionMaterial

## Key Features

### 1. Liquid Chrome Hero
- Floating torus knot with MeshTransmissionMaterial
- Mouse-interactive lighting
- Performance monitoring for adaptive quality

### 2. Spotlight Reveal Cards
- Invisible borders until hover
- Radial gradient mask follows cursor
- CSS custom properties for position tracking

### 3. Focus Mode
- Dims all UI except active section
- Toggle in dashboard documentation view
- Smooth opacity transitions

### 4. Sound Design
- Camera shutter clicks
- Luxury car switch toggles
- Soft swooshes for transitions
- Success chimes (C major chord)
- Synthesized via Web Audio API (no external files)

### 5. Grain Overlay
- SVG noise texture at 3% opacity
- Animated with 8s loop
- `pointer-events: none` for interaction pass-through

## Accessibility

- `prefers-reduced-motion` support
- `aria-label` on all interactive elements
- Keyboard navigation support
- Focus visible states
- High contrast text ratios

## Performance

- `drei/PerformanceMonitor` lowers resolution on frame drops
- Dynamic imports for Three.js scene
- CSS animations where possible
- Reduced motion for accessibility

## Customization

The design system uses CSS custom properties for easy theming:

```css
:root {
  --void: #050505;
  --surface: #0A0A0A;
  --crimson: #F43F5E;
  /* ... etc */
}
```

## License

MIT - Tekshila Team
