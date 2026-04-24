# passFa.st

## Overview

passFa.st replaces paper hall passes with a real-time digital system. Teachers enter a student ID, the app resolves it to a name and profile via Convex, generates a short pass code, and the student checks out and back in from their own device. Status is tracked live across all connected clients with no polling. Convex reactive queries push updates instantly.

## Problem

Paper hall passes are slow to write, trivially forgeable, and invisible the moment a student walks out the door. Teachers have no passive awareness of who is out, for how long, or whether they are overdue without interrupting class to check. The solution needs to be faster than paper, accountable by default, and require zero teacher overhead after initial setup.

## Solution

A web app with three role-gated views served from a single Next.js deployment. Teachers enter a student ID, the system resolves the student name from Convex, sets a destination and duration, and issues a short alphanumeric pass code. The student enters that code on their device, checks out, watches a live countdown, and checks back in on return. All state lives in Convex and streams reactively to every connected client in real time.

The design takes direct inspiration from Vercel's physical/digital hybrid aesthetic: a draggable hall pass card rendered in the browser using React Three Fiber + Rapier physics, so the pass feels tangible rather than like a form submission. See [Building an Interactive 3D Event Badge with React Three Fiber](https://bri.egeuysal.com/egeuysall/building-3d-badge.md) for the design reference.

## Auth and Roles

Clerk handles all authentication. Three roles are enforced via Clerk publicMetadata:

`role: "teacher"`: can issue passes, view live status dashboard
`role: "student"`: can check out and check in on their own pass only
`role: "admin"`: read-only access to full pass log and aggregate stats

Students self-register with their school email. Teachers are provisioned by an admin. Role-based route protection is enforced both in Next.js middleware via Clerk auth() and at the Convex query/mutation layer using ctx.auth.

## Data Model

```json
{
  "students": {
    "_id": "Convex ID",
    "studentId": "string : 5-digit school ID, indexed",
    "clerkUserId": "string : linked Clerk user",
    "name": "string",
    "grade": "string",
    "email": "string"
  },
  "passes": {
    "_id": "Convex ID",
    "code": "string : short alphanumeric e.g. ABX42, indexed",
    "studentId": "string : FK to students.studentId",
    "studentName": "string : denormalized for fast reads",
    "issuedBy": "string : teacher Clerk user ID",
    "destination": "string",
    "durationSecs": "number",
    "status": "waiting | active | overdue | returned",
    "checkedOutAt": "number | null : Unix ms",
    "checkedInAt": "number | null : Unix ms",
    "createdAt": "number"
  }
}
```

Convex indexes: `by_code` on passes.code, `by_studentId` on students.studentId, `by_status` on passes.status.

## Core Flow

1. Teacher enters 5-digit student ID. Convex query `resolveStudent` returns name + grade instantly
2. Teacher sets destination and duration via dropdown and slider
3. Mutation `createPass` writes to Convex, generates a unique 5-char code
4. Pass card animates in as a draggable lanyard card using React Three Fiber + Rapier, showing student name, destination, and code
5. Student enters code on their device. Mutation `checkOut` sets status to active and records checkedOutAt
6. Timer runs client-side. Convex scheduled function via ctx.scheduler.runAfter flips status to overdue at expiry server-side
7. Student hits Check back in. Mutation `checkIn` sets status to returned and records checkedInAt
8. Teacher dashboard updates reactively via useQuery with no polling or refresh needed

## Tech Stack

| Layer               | Choice                     | Why                                                                           |
| ------------------- | -------------------------- | ----------------------------------------------------------------------------- |
| Framework           | Next.js 14 App Router      | File-based routing, RSC, middleware for auth                                  |
| Mobile              | React Native + Expo        | Primary student-facing app, QR scanning via expo-camera                       |
| Auth                | Clerk                      | Role metadata, school email restrictions, prebuilt UI for both web and native |
| Transactional Email | Resend                     | Overdue alerts and pass receipts triggered from Convex actions                |
| Database + API      | Convex                     | Reactive queries, scheduled functions, no REST layer needed                   |
| 3D / Physics        | React Three Fiber + Rapier | Interactive pass card with lanyard physics on web                             |
| Styling             | Tailwind CSS + NativeWind  | Shared utility classes across web and native                                  |
| Hosting             | Vercel                     | Zero-config Next.js deploy, edge middleware                                   |

Convex functions run in Convex's own runtime, deployed separately from Vercel. Next.js server components call Convex via the HTTP client for SSR where needed. Client components use useQuery and useMutation from convex/react directly. The React Native app shares the same Convex backend via convex/react-native, giving students a native checkout experience with QR scanning via expo-camera. Resend is called from Convex actions, triggered on overdue and return events.

## Design Direction

The UI takes direct cues from the [Vercel Ship 2024 badge](https://bri.egeuysal.com/egeuysall/building-3d-badge.md). The hall pass is rendered as a physical card hanging from a lanyard using React Three Fiber. When a teacher issues a pass, the card drops into frame with full physics simulation: Rapier rope joints connecting the fixed anchor to the card, with a CatmullRomCurve3 fed through MeshLine for the lanyard geometry. The student name and pass code are rendered dynamically onto the card surface via Drei RenderTexture.

Outside the 3D card, the rest of the UI is flat and minimal: high contrast, monospaced code display, large countdown typography, thin 0.5px borders, no decoration. Black/white base with a single accent color, geometric sans-serif, generous whitespace.

## Convex Scheduled Functions

Overdue detection is authoritative server-side, not client-dependent. When a pass is checked out, a Convex scheduled function is registered:

```ts
await ctx.scheduler.runAfter(pass.durationSecs * 1000, api.passes.markOverdue, {
  passId
})
```

markOverdue checks if the pass is still active before writing. It is a no-op if the student already returned. This means overdue state is correct even if no client is connected.

## Key Convex Mutations

`resolveStudent`: teacher-only query, returns name + grade from students table

`createPass`: resolves student by ID, generates unique code, writes pass, registers overdue scheduler, returns code

`checkOut`: validates code exists and is in waiting state, sets status to active + checkedOutAt, registers overdue scheduler

`checkIn`: validates student identity via ctx.auth, sets status to returned + checkedInAt

## CAC Alignment

| Requirement           | How passFa.st meets it                                             |
| --------------------- | ------------------------------------------------------------------ |
| Solves a real problem | Hall pass accountability is a universal daily classroom pain point |
| Completable in scope  | Three views, one data model, one deployment                        |
| No AI required        | Fully deterministic: auth, scheduling, reactive queries            |
| Privacy-conscious     | No location data, no surveillance, Clerk handles all PII           |
| Explainable to judges | Full pass lifecycle is demonstrable in under 3 minutes             |

## Timeline

### Week 1: Build

| Day     | Task                                                                             |
| ------- | -------------------------------------------------------------------------------- |
| Mon     | Scaffold Next.js + Convex + Clerk, define schema, seed student data              |
| Tue     | resolveStudent query, createPass mutation, code generation logic                 |
| Wed     | React Three Fiber pass card: Rapier joints, MeshLine lanyard, RenderTexture name |
| Thu     | Student checkout/checkin flow, live countdown UI, markOverdue scheduler          |
| Fri     | Admin log view, reactive stats, role-gated middleware                            |
| Weekend | Polish, edge cases, mobile layout                                                |

### Week 2: Demo and Submit

| Day | Task                                                                   |
| --- | ---------------------------------------------------------------------- |
| Mon | Record demo video: full pass cycle across all three roles, under 3 min |
| Tue | Write CAC project description                                          |
| Wed | Final Vercel + Convex production deploy                                |
| Thu | Submit                                                                 |
| Fri | Buffer                                                                 |
