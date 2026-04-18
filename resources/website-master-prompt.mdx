# Master AI Prompt — Axono Website Plan (Swiss + Dither + 3D)

Use this as the single source prompt for building the website.

## Role

You are a senior creative web engineer and technical artist.
Build a production-quality website for **axono.so** with a strong Swiss design system, grayscale 3D interactions, dither/grain atmosphere, and premium motion.

No shallow demo output. Build an intentional experience.

## Core Outcome

Ship a fullscreen, high-performance 3D-first website with:

- Wireframe-to-solid skyscraper hero interaction
- Infinite smooth scroll (not solely scroll-trigger gimmicks)
- Mouse-driven parallax across 3D and text layers
- Swiss editorial layout with selective neobrutalist chaos accents
- Projects section with interactive wireframe hand/finger reveal behavior
- Photos/media section consistent with the same visual language
- Sound design, custom cursor, and subtle cinematic polish

## Art Direction (Non-Negotiable)

- Primary style: Swiss design
- Secondary accent style: controlled neobrutalist moments
- Color: light mode, near-white background, grayscale system
- Texture: dither shader + grain overlay across the whole experience
- Motion feel: smooth, restrained, premium, never jerky
- Composition: asymmetric, intentional negative space
- Typography:
- Clean geometric sans (more modern than Inter) for main copy
- Monospace for micro labels and metadata

## Hero Concept

- Hero object: a **Merdeka 118-inspired** skyscraper in wireframe
- Entry animation: structure draws from top to bottom
- Idle state: thin/skeletal wireframe
- Hover state: transitions to fuller solid skyscraper with grain/dither detail
- Unhover: collapses back to wireframe
- All transitions should feel physically coherent and reversible

## Loader + First Impression

- Loader is minimal and cream-toned
- Show logo in restrained style first
- Transition from loader into the main near-white scene
- Opening should feel seamless and real-time (not video pre-render)

## Interaction Model

- Mouse position influences:
- Hero/parallax offsets
- Text geometry depth behavior
- Supporting section micro-shifts
- Add custom cursor that matches the identity
- Keep scroll continuous/infinite (looping top/bottom behavior)
- Do not rely only on scroll-triggered events; blend hover, mouse, and ambient movement

## Section Requirements

1. Hero Section

- 3D skyscraper + typography placed below or on both sides (layout inspiration similar to the AVA reference)

2. Projects Section

- Wireframe hand/finger element (grayscale)
- On hover, reveal project details in minimal popover UI
- Hand/finger can subtly follow cursor
- Keep grain/dither continuity

3. Photos / Media Section

- Mostly wireframed visual treatment
- Include 2D-looking elements that are actually 3D-aware where useful

## Technical Stack and Baseline

- Framework: Next.js
- 3D: Three.js + @react-three/fiber + @react-three/drei
- Motion: GSAP
- Build-first approach; no long theory detours

### Setup

```bash
npx create-next-app@latest
npm install three @react-three/fiber @react-three/drei gsap
```

## Implementation Roadmap (7-Day Execution)

### Day 1 — Full 3D Hero

Goal: fullscreen animated 3D landing.

Start with base scene and camera:

```tsx
"use client"

import { useRef } from "react"

import { Canvas, useFrame } from "@react-three/fiber"

function Box() {
  const ref = useRef<any>()

  useFrame(() => {
    if (!ref.current) return
    ref.current.rotation.y += 0.003
  })

  return (
    <mesh ref={ref}>
      <boxGeometry args={[2, 2, 2]} />
      <meshStandardMaterial color="#aaaaaa" />
    </mesh>
  )
}

export default function Scene() {
  return (
    <Canvas
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100vw",
        height: "100vh"
      }}
      camera={{ position: [0, 2, 6], fov: 60 }}
    >
      <color attach="background" args={["#0a0a0a"]} />
      <fog attach="fog" args={["#0a0a0a", 5, 20]} />

      <ambientLight intensity={0.4} />
      <directionalLight position={[5, 5, 5]} intensity={1} />

      <Box />
    </Canvas>
  )
}
```

Then replace primitive cube logic with a stacked/offset tower composition that evolves into the skyscraper behavior.

### Day 2 — Remove Demo Feel

Goal: premium material/light/composition quality.

- Use softer grays (`#888` range)
- Add ground plane
- Tune lighting contrast

```tsx
<mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -1, 0]}>
  <planeGeometry args={[50, 50]} />
  <meshStandardMaterial color="#111" />
</mesh>
```

Add subtle camera drift:

```tsx
useFrame(({ camera, clock }) => {
  camera.position.x = Math.sin(clock.elapsedTime * 0.2) * 0.5
})
```

### Day 3 — Scroll + System Motion

Goal: scroll contributes to depth but does not dominate UX.

```tsx
import { useEffect } from "react"

import gsap from "gsap"

useEffect(() => {
  window.addEventListener("scroll", () => {
    const scrollY = window.scrollY
    camera.position.z = 6 - scrollY * 0.002
  })
}, [])
```

Also implement non-scroll motion channels (hover/mouse/ambient).

### Day 4 — Atmosphere

Goal: cinematic but clean depth.

- Tune fog and grain intensity
- Add a secondary low-intensity accent light

```tsx
<pointLight position={[-5, 2, -5]} intensity={0.5} color="#4040ff" />
```

### Day 5 — Composition

Goal: designed layout, not centered demo.

- Offset hero object
- Use asymmetrical copy blocks
- Preserve negative space

```tsx
<group position={[1.5, 0, 0]}>
```

### Day 6 — Micro Interactions

Goal: make the environment feel alive.

```tsx
useFrame(({ mouse }) => {
  camera.position.x = mouse.x * 0.5
  camera.position.y = mouse.y * 0.3
})
```

Add custom cursor, hover states, and subtle text parallax.

### Day 7 — Production Polish

Goal: optimized, stable, shippable.

```tsx
<Canvas dpr={[1, 2]}>
```

- Reduce unnecessary re-renders
- Keep animation timing slow and intentional
- Validate desktop + mobile behavior

## Design Rules

- Keep colors minimal
- Always include fog/depth strategy
- Slow animations only
- Avoid over-centering
- Think design system, not visual effects demo

## Performance + Accessibility Guardrails

- Optimize geometry/material counts and shader cost
- Lazy-load non-critical heavy sections
- Respect `prefers-reduced-motion`
- Maintain readable contrast in light mode
- Provide keyboard and focus-visible behavior for interactive UI
- Keep interaction states understandable without sound

## Security + Engineering Guardrails

- Validate/sanitize any external content before rendering
- If loading remote assets, enforce trusted domain allowlist
- Avoid inline script injection patterns
- Do not expose secrets in client bundles
- Keep dependencies current and pinned where needed

## Igloo-Inspired Process Principles (Apply to Build)

- Use fast previs and gray-blocking early
- Iterate in-browser for shader/model/timing tuning
- Measure performance continuously during development
- Prefer real-time transitions over pre-rendered video tricks

## References (Keep These Fetchable)

### Website references

- https://4wide.jp/
- https://ascendmarketing.xyz/
- https://srg.ava-digital.site/en

### Visual assets

![](https://cdn.egeuysal.com/content/2026/04/15/asset-01.jpeg)

![](https://cdn.egeuysal.com/content/2026/04/15/asset-02.jpeg)

![](https://cdn.egeuysal.com/content/2026/04/15/asset-03.png)

### Motion reference

![vid](https://cdn.dribbble.com/userupload/13555619/file/original-201878a57e6c96368911d57fd5451ef8.mp4)

## Final Deliverable Expectation

Return:

1. A full implementation plan mapped to pages/sections/components.
2. A concrete build order with milestones.
3. Key scene/component code scaffolds.
4. Performance strategy and fallback behavior.
5. A final QA checklist for interaction, visuals, accessibility, and responsiveness.
