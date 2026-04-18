# Axono Igloo Style 3D Website Plan

Domain: axono.so  
Style: Swiss design with dither and grain with a subtle neobrutalist layer  
Core idea is 3D first, interaction first, no demo feel

## Principles

Keep the color palette minimal and mostly grayscale. Depth should always exist through fog and layering. Motion stays slow and smooth. Layouts avoid perfect centering and instead feel intentionally offset. Interaction matters more than scroll. Everything should feel alive through motion, hover, or parallax. 3D is not decoration, it acts as the interface itself.

- Minimal grayscale palette
- Constant depth using fog and layering
- Slow and smooth motion
- Asymmetrical layout
- Interaction over scroll
- 3D acts as the UI layer

## Core Experience

### Hero Skyscraper System

The main object is a wireframe skyscraper inspired by Merdeka 118. It loads as a thin wireframe and reveals itself from top to bottom like it is being constructed in real time. On hover, the structure becomes solid and gains a grain or dither material. When the hover ends, it collapses back into wireframe.

The object should feel alive even when idle. Mouse movement drives parallax across both the object and surrounding text so the entire hero responds naturally.

- Wireframe by default
- Top to bottom reveal
- Hover switches to solid with grain
- Collapse back on leave
- Subtle idle motion

Basic scene structure

```tsx
"use client"

import { useRef } from "react"

import { Canvas, useFrame } from "@react-three/fiber"

function Tower() {
  const ref = useRef<any>()

  useFrame(() => {
    if (!ref.current) return
    ref.current.rotation.y += 0.002
  })

  return (
    <mesh ref={ref}>
      <boxGeometry args={[1.5, 4, 1.5]} />
      <meshStandardMaterial wireframe color="#888" />
    </mesh>
  )
}

export default function Scene() {
  return (
    <Canvas camera={{ position: [0, 2, 6], fov: 60 }}>
      <color attach="background" args={["#f5f5f5"]} />
      <fog attach="fog" args={["#f5f5f5", 5, 20]} />

      <ambientLight intensity={0.4} />
      <directionalLight position={[5, 5, 5]} intensity={1} />

      <Tower />
    </Canvas>
  )
}
```

### Loader

The loader is minimal and cream colored. The logo appears first in a reduced form, then the scene opens into the main page smoothly.

- Cream palette
- Minimal logo
- Smooth reveal into scene

### Layout System

Text sits beside or below the 3D object depending on composition. The layout should feel balanced but not centered.

Typography uses mono for small UI elements and a clean geometric sans for primary text. The sans font should feel more modern and structured than Inter.

- Text beside or below object
- Mono for small UI
- Clean geometric sans for main text

### Background System

The background is near white with a subtle dithering noise pattern. This adds texture without distracting from the content. It can remain a simple 2D layer.

Example shader idea for grain

```glsl
float noise(vec2 uv) {
  return fract(sin(dot(uv, vec2(12.9898,78.233))) * 43758.5453);
}
```

- Near white base
- Subtle dither texture
- Lightweight

### Parallax System

Mouse position drives depth across the entire page. The 3D object shifts slightly. Text layers move at different speeds. UI elements respond subtly.

```tsx
useFrame(({ mouse, camera }) => {
  camera.position.x = mouse.x * 0.5
  camera.position.y = mouse.y * 0.3
})
```

- Mouse controls depth
- Object and text move differently
- Constant subtle motion

## Interaction Design

### Global Behavior

Transitions should always be smooth and continuous. Avoid hard scroll triggered animations. The scroll system loops so reaching the end continues back to the start. Interaction through hover and movement is more important than scroll position.

- No abrupt transitions
- No hard scroll triggers
- Infinite scroll loop
- Hover and movement first

### Projects Section Hand System

This section introduces a wireframe hand in grayscale. The hand follows the cursor slightly and feels responsive. Hovering over parts of the hand reveals projects through a minimal popover.

The same visual logic applies. Wireframe transitions into solid with grain on interaction.

- Wireframe hand object
- Follows cursor slightly
- Hover reveals project popover
- Consistent material system

### Cursor System

A custom cursor is required. It should match the system visually and react subtly to interaction.

### Sound Design

Sound is minimal and reinforces interaction. It should feel intentional and never distracting.

## Visual System

Wireframe is the base state. Solid grayscale appears on interaction. Grain or dither overlays unify the look across all elements.

Effects like chromatic aberration or frost can be used lightly but should remain subtle and rare.

- Wireframe base
- Solid on interaction
- Grain overlay throughout

## Additional Pages

### Photos Page

The photos page follows the same system. Mostly wireframe visuals, minimal layout, consistent parallax.

### Mixed 2D and 3D Elements

Some UI elements that appear flat should actually be 3D planes. These respond to mouse movement and maintain depth consistency.

## Animation System

All animation is real time. Nothing is pre rendered. Everything is built directly in the engine. Transitions should feel continuous and tied to user input rather than timelines.

- Real time rendering only
- Smooth continuous transitions
- Reactive systems over timelines

## Tech Stack

- Next.js
- React Three Fiber
- drei
- GSAP for controlled motion
- Custom shaders for dither and grain

## Build Philosophy

Work directly in the browser and iterate fast. Start with rough previews to validate ideas, then refine. Measure performance continuously and adjust early.

- Build in browser
- Iterate fast
- Use rough previews first
- Measure performance continuously

## Performance Rules

Geometry should stay optimized. Shader complexity should be controlled. Use DPR scaling to balance quality and performance.

```tsx
<Canvas dpr={[1, 2]} />
```

- Optimize geometry
- Control shader cost
- Keep load time minimal

## Final Outcome

The result is a 3D native landing experience where interaction drives navigation. The layout stays clean through Swiss design principles while depth and motion create a strong identity. The wireframe to solid transitions define the system and make it feel cohesive.

## References

- https://4wide.jp/
- https://ascendmarketing.xyz/
- https://srg.ava-digital.site/en

## Reminder

This is not a traditional website.

It is an interactive system where state is visual, interaction is navigation, and 3D acts as the interface layer.
