# 🧊 Igloo-Style 3D Website Plan (Aggressive Build) - domain as axono.so - important

You are already a full stack dev. This is build-first. No theory, just execution.

---

## Day 1 — Full 3D Hero (No Basics)

### Goal

A fullscreen animated 3D landing

### Setup

```bash
npx create-next-app@latest
npm install three @react-three/fiber @react-three/drei gsap
```

### Create Scene

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

### Replace cube with structure

- Stack boxes
- Offset positions
- Think “igloo / tower”

---

## Day 2 — Kill Demo Look

### Goal

Make it feel premium

### Changes

- Use softer color (`#888` not white)
- Add ground plane
- Adjust lighting contrast

```tsx
<mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -1, 0]}>
  <planeGeometry args={[50, 50]} />
  <meshStandardMaterial color="#111" />
</mesh>
```

### Add subtle camera motion

```tsx
useFrame(({ camera, clock }) => {
  camera.position.x = Math.sin(clock.elapsedTime * 0.2) * 0.5
})
```

---

## Day 3 — Scroll Controls Everything

### Goal

Scroll = motion

### Install

```bash
npm install gsap
```

### Basic scroll mapping

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

---

## Day 4 — Atmosphere

### Goal

Cinematic depth

### Do

- Tune fog range
- Add second light (low intensity)

```tsx
<pointLight position={[-5, 2, -5]} intensity={0.5} color="#4040ff" />
```

---

## Day 5 — Composition

### Goal

Make it look designed

### Do

- Move object off-center

```tsx
<group position={[1.5, 0, 0]}>
```

- Adjust camera angle
- Leave empty space

---

## Day 6 — Micro Interactions

### Goal

Make it feel alive

### Mouse parallax

```tsx
useFrame(({ mouse }) => {
  camera.position.x = mouse.x * 0.5
  camera.position.y = mouse.y * 0.3
})
```

---

## Day 7 — Polish

### Goal

Production feel

### Optimize

```tsx
<Canvas dpr={[1, 2]}>
```

- Clean structure
- Remove unnecessary re-renders

---

## Final Outcome

You will have:

- Fullscreen 3D landing
- Scroll-driven camera
- Smooth motion
- Clean structure

---

## Rules

- Keep colors minimal
- Always use fog
- Slow animations only
- Avoid centering everything
- Think design, not demo
