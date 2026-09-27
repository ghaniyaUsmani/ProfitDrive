# Profit Drive — Component Library (AI-native, voice-first)

## Context
Profit Drive is a Drive-for-Dollars scouting app. Drivers get assigned a zip, hunt for distressed properties (visible neglect, vacancy signals, tax/legal cues, dated exteriors), and turn qualifying ones into leads for real estate agents to work.

A manual app already exists in Figma (`EpRoi6bketzxX87Z2SEsFN`, node `487-9997`). It's dangerous to use while driving, requires domain expertise to spot distress, and has a crash-prone capture flow that loses pinned properties.

We're introducing an **intelligent agent** that:
1. Pre-scans each driver's zip using web listings + satellite imagery, generates a **distress score** per property, and shortlists the highest-signal ones so the driver never wanders blind.
2. Runs a **conversational route-planning** step (Start Drive → constraints → optimized route).
3. Runs an **in-drive conversational capture** loop (arrive → fetch details → suggest tags → draft note → suggest campaign → confirm as lead) — all voice-first, cards-secondary.

This planning session covers **the component library only** — the reusable UI atoms/molecules the AI-native app will be built from. Screens, flows, and the "Design" page of the preview site are out of scope for now. The library will be designed **fresh** (not extended from the existing manual app), because the interaction model is fundamentally different.

Deliverable: the Component Library tab of the preview site (`scratchpad/preview/index.html`, currently a placeholder) filled with a renderable inventory of the components, using tokens already loaded in the Variables tab.

## Design principles (drive the whole library)
- **Voice-first, cards-secondary.** Cards exist for confirmation, glance-value, and after-stop review — never as the primary way to make decisions in motion.
- **Glanceable while driving, rich when parked.** Every card has a compact "in-motion" state (score + address + agent verdict) and an expanded "parked" state (full details + editable actions).
- **Agent presence is ambient, not modal.** A persistent voice indicator (orb + status pill) — no full-screen chat takeovers that hide the road.
- **Suggestion, not automation.** Agent proposes tags / notes / campaigns; the driver confirms with a tap or "yes." No silent auto-actions.
- **Safety-first micro-affordances.** Anything requiring visual attention has a large touch target (≥ 56 px), high contrast, and no more than three actions per card.

## Locked decisions

### From the initial scoping session
1. **Scope:** Component library only (no screens/flows yet).
2. **Design origin:** Fresh — not extended from the existing manual app.
3. **Interaction mode:** Voice-first, cards-secondary.
4. **Agent presence:** Always-visible ambient voice orb.
5. **Preview rendering:** Live interactive HTML — every component is real, clickable, and cycles through its states in the preview.
6. **Project mirroring:** Preview source and plan also live under `Profit Drive/design-system/` and `Profit Drive/docs/component-library-plan.md` so nothing important is trapped in scratchpad.

### From the grill (locked decisions that reshape Pass 2)
7. **App theme:** **Light mode.** Preview flipped to light so every contrast / shadow / border decision happens against the real target ground.
8. **Distress grade color language — inverted:**
   - A = **tomato red** (hot lead — the driver's money target)
   - B = **coral** (still hot)
   - C = **yellow** (marginal)
   - D = **neutral gray** (skip)
   Rationale: the driver is a bounty hunter, not a safety inspector. Visual reward should fire when the high-value prey is on screen.
9. **Voice orb docking:** **Bottom-right, thumb-anchored**, with a one-time handedness flip during onboarding. Works in portrait and landscape mounts; avoids OS-gesture zones.
10. **Property card state trigger:** **Automatic on the agent's arrival announcement.** Card expands the moment the agent says "we're here." Collapses when the driver moves > N meters away. No manual toggle. GPS-speed and manual-tap were both rejected.
11. **Tag/Chip taxonomy — source-primary, category-as-icon:**
    - **Source axis** (drives visual state): agent-suggested (dashed) · user-confirmed (solid) · user-added (solid, distinct icon) · system-locked (solid + lock icon, not removable)
    - **Category axis** (drives the leading icon only): distress (🏚) · legal (⚖️) · vacancy (📭) · owner (👤)
    - **No severity dimension** — the property Grade already carries it.
12. **Property card content model — Decision Card:** The card shows *only what needs the driver's input* (confirmable tags, campaign fit, add-as-lead, dismiss). Full profile (owner, financials, comps, tenure) lives behind a single **Show details** reveal — never on the front of the card.
13. **Confirmation flow at each stop — bulk with named exceptions:**
    1. Agent arrives → announces address + grade
    2. Agent **bulk-shows** tags + campaign fit + captured imagery in one breath, asks *"Continue with these, or make changes?"*
    3. Driver says "yes" / names exceptions ("swap campaign to X" / "remove the tax lien tag")
    4. Agent **separately** asks *"Want me to jot anything down?"* — driver either declines or dictates. **Notes are never agent-drafted.**
    5. Add as lead / dismiss
14. **Persistent stop-interaction control:** **Camera button** always visible during a stop (tap or voice: "open camera") — for driver-captured photos of anything the agent missed.
15. **Back button:** Deferred to a later pass. When built, it lives in the drive-view header as a **"End drive, save everything"** affordance — never as a stop-level cancel/undo.
16. **Captured imagery:** **Single swipeable Imagery Carousel** (satellite ↔ distress shots), not side-by-side thumbnails. Agent can auto-cycle while narrating; driver can swipe.
17. **Copy tone — "field partner sitting shotgun":** Contractions, transitions that acknowledge the previous beat, small conversational risks ("looks rough," "quieter street"). No robotic phrasing — "next / confirm / action required / lead created / arriving at property" are all banned. Field-name jargon ("distress score 87", "campaign_id 12") never leaks into voice; only human-friendly summaries do ("Grade A", "cash-offer campaign"). See the **Voice & Copy Principles** section below.
18. **Naming convention:** Title Case for design/prose labels ("Voice Orb"). kebab-case for CSS classes (`.voice-orb`). snake_case for tokens (`primarybutton_bg_active` — matches Figma source). Translates 1:1 to PascalCase framework components when we port later.
19. **Iconography — no emojis, ever.** All pictorial icons are inline SVG line icons (1.75px stroke, `currentColor`, 12–22 px depending on context). Emojis look juvenile in a professional B2B app. The library exposes a canonical set: `distress`, `legal`, `vacancy`, `owner`, `camera`, `mic`, `pin`, `phone`, `mail`, `back_arrow`, `chevron_back`, `chevron_down`, `more`, `close`, `check`, `plus`, `lock`, `info`, `warn`, `send`, `arrow_right`. Any new component that needs an icon must add it to this set — never inline an emoji.

## Voice & Copy Principles

The agent talks like a partner in the passenger seat, not a checklist.

**Rules of thumb:**
- **Use contractions.** "This one's a fit" not "This one is a fit".
- **Acknowledge before advancing.** "Got it — added." not "Confirmed. Next.".
- **Frame with everyday phrases.** "Looks like a good candidate" not "High distress score detected".
- **Speak in observations, not fields.** "Roof looks rough, there's a tax lien" not "Tags suggested: roof_damage, tax_lien".
- **Take small conversational risks.** "Quieter street" / "Nice one" / "Losing signal for a sec — hold on".
- **Never announce the interaction itself.** "Adding as lead in 3, 2, 1" is robotic; "Got it — added" is not.

**Before / after examples:**

| Robotic (banned) | Natural (target) |
|---|---|
| "Arriving at property. Grade A." | "This one's a good sign — Grade A." |
| "Suggested tags: overgrown lawn, roof damage, tax lien. Confirm?" | "Overgrown, roof looks rough, and there's a tax lien. Want me to tag all that?" |
| "Next question. Add a note?" | "Anything you want me to jot down?" |
| "Lead created. Moving to next stop." | "Got it — added. Next one's a couple minutes up the road." |
| "Action required: campaign selection." | "Looks like a fit for the cash-offer campaign — okay to add it?" |
| "Error. GPS signal lost." | "Losing signal for a sec — hold on." |
| "Command not recognized." | "Missed that — say it again?" |

## Component inventory
Six groups, prioritized P0 → P2. P0 is what we build first; P1 fills the library; P2 waits until we start screen work.

### Group 1 — Foundation (atoms) [P0]
Reusable primitives that consume the existing tokens.
- **Button** — Primary / Secondary / Tertiary / Ghost / Destructive · sizes S/M/L · with/without leading icon · loading state
- **Icon Button** — round, sizes M/L, states (default/hover/active/disabled)
- **Text Field** — single line + multi-line, label, hint, error, success (used mostly as the tap-fallback under voice; not the primary input surface)
- **Tag / Chip** — see decision 11 above. Dimensions:
  - Source (visual state): agent-suggested (dashed) · user-confirmed (solid) · user-added (solid + user icon) · system-locked (solid + lock icon, not removable)
  - Category (leading icon only): distress 🏚 · legal ⚖️ · vacancy 📭 · owner 👤
  - Interaction: default · selected · disabled
- **Toggle switch, Checkbox, Radio, Segmented control**
- **Avatar, Divider, Icon set** (curated system icons)

### Group 2 — Data display [P0]
- **Distress Grade Ring** — letter (A / B / C / D) inside a colored ring. Sizes S/M/L. Colors map to a token band: A → green, B → amber, C → orange, D → red.
- **Grade Badge** — compact pill showing the letter + a semantic word (`A · Prime`, `D · Critical`).
- **Stat Tile** — big number + label for home KPIs (leads captured, streak, avg grade).
- **Progress Bar** — route progress (X of Y stops).
- **Address Block** — street + city + zip with copy affordance.
- **Owner Info Row** — name, tenure length, quick-dial.
- **Financials Row** — ARV, equity, tax status inline.

### Group 3 — Voice & agent presence [P0 · critical]
The distinctive layer for this app. Because the orb is ambient and appears on every screen, this group is the highest-priority build.
- **Voice Orb** — states: idle · listening · thinking · speaking · muted · error. Docked at **bottom-right, thumb-anchored** (per decision 9), with a handedness flip config. Never covers primary content. Breathing / pulse micro-motion per state.
- **Ambient Orb Dock** — positioning frame that keeps the orb visible above every other UI layer; specifies bottom-right default anchor, left-mirror for left-handed drivers, safe-area handling, and how it interacts with bottom sheets (slides above them).
- **Waveform / VU Ribbon** — real-time voice-activity indicator surrounding the orb during listening.
- **Status Pill** — attached to the orb: `Listening…` / `Thinking…` / `Speaking…` / `Tap to talk` (using natural copy per decision 17).
- **Push-to-Talk Button** — larger orb variant for manual capture bursts.
- **Transcript Bubble** — agent / driver; short-lived (auto-dismiss during motion), stackable in a review pane when parked.
- **Agent Nudge Banner** — top-of-screen, non-blocking (`Approaching 123 Main St · Grade A` — natural-language variant preferred).
- **Persistent Action Rail** [NEW] — always visible during a stop interaction. Ships with **Camera** in Pass 2. Structured so we can drop additional persistent actions in later (End Drive lives here in a later pass).

### Group 4 — Property surfaces [P0]
- **Property Card — Compact** — Grade Ring + address + top 2 suggested tag icons. Auto-shown when driving toward the property (per decision 10).
- **Property Card — Expanded** — **Decision Card** per decision 12. Shows: tag chips (confirmable), campaign fit block (confirmable), swipeable imagery, and primary actions (Add as lead / Dismiss). Full profile hides behind a **Show details** reveal. Auto-expands on agent arrival announcement; auto-collapses on driver departure.
- **Imagery Carousel** [renamed from Satellite Imagery Card] — single swipeable card cycling between satellite view and distress-area shots (per decision 16). Agent can auto-cycle while narrating; driver can swipe manually.
- **Tag Suggestion Row** — horizontal row of chips using the source-primary taxonomy (decision 11). Agent's proposals appear in the `agent-suggested` (dashed) state; bulk-accept via voice or tap-and-hold gesture flips them all to `user-confirmed`.
- **Note Composer** [replaces Note Card] — empty state ("Anything to jot down?") plus a dictation surface. Driver-initiated only; never agent-drafted (per decision 13).
- **Campaign Suggestion Card** — recommended campaign + one-line human reason ("This one's a fit for the cash-offer campaign" — natural copy per decision 17), with accept / swap / skip actions.
- **Lead-Added Confirmation** — brief success card, natural copy ("Got it — added. Next one's a couple minutes up the road.").

### Group 5 — Framing & delivery surfaces [P1]
- **Bottom Sheet** — peek / half / full, drag-handle, backdrop
- **Modal** — centered, with header + footer actions
- **Toast** — brief non-blocking feedback
- **Safety Banner** — appears while car is in motion, blocks any action requiring text input
- **Top App Bar** — screen title + context actions

### Group 6 — Route & map [P2]
- **Route Card** — day's plan summary: N stops, est time, est leads
- **Route Stop Preview** — upcoming property with ETA
- **Mini Map + Pins** — route with distress-color pins
- **Distress Heatmap Legend**
- **ETA Chip**

## Delivery plan
The build happens in three passes. Each pass finishes end-to-end (spec + implementation + preview integration) before the next begins, so the library is usable early even if we stop mid-way.

**Pass 1 — Voice & data-display core (Groups 2 + 3, P0 critical)**
This is the differentiated layer of the app and blocks everything else.
1. Add a **Distress Grade** color band (A/B/C/D) to `tokens.json` under a new `Symantic/GradeColors` group, aliasing to existing primitives (green → red). Rebuild the Variables tab so the grade colors are visible.
2. Extend `scratchpad/preview/build.py` with a `render_library()` function analogous to `render_collection()`. It renders inside the existing `library` page (which currently holds a placeholder).
3. Build components in this order: Voice Orb (all 6 states), Ambient Orb Dock spec, Status Pill, Waveform Ribbon, PTT Button, Transcript Bubble, Agent Nudge Banner, Grade Ring, Grade Badge, Stat Tile, Progress Bar, Address Block, Owner Info Row, Financials Row.
4. For each, expose a small state toggle (segmented control) inside the preview so the driver-experience states cycle without touching code.

**Pass 2 — Foundation + Property surfaces (Groups 1 + 4)**
5. Build Group 1 atoms (Button, Icon Button, Text Field, Tag/Chip, Toggle, Checkbox, Radio, Segmented Control, Avatar, Divider, Icon set).
6. Build Group 4 property surfaces (Compact/Expanded Property Card, Satellite Imagery Card, Tag Suggestion Row, Note Card, Campaign Suggestion Card, Lead-Added Confirmation), consuming Group 1 + 2 components.

**Pass 3 — Framing surfaces (Group 5, P1)**
7. Build Bottom Sheet, Modal, Toast, Safety Banner, Top App Bar. These wait until we have real content to house.

_Group 6 (route & map) is P2 and waits for the screen-work planning pass._

## Rendering pattern in the preview
- `Component Library` page uses the same sub-tab pattern as the Variables page: sub-tabs for `Voice & Agent` · `Data Display` · `Foundation` · `Property` · `Framing`.
- Inside each sub-tab, components are cards in a responsive grid. Each card shows: component name · a live rendered instance · a state toggle · the tokens it consumes (as small pill labels linking to the Variables tab).
- All colors/spacing/radius/type come from CSS variables named after the Figma tokens (mirroring `tokens.json`). No hardcoded hex except demo swatches.

## Files that will be touched
- `scratchpad/tokens.json` — add `Symantic/GradeColors` group (A/B/C/D → alias into primitives).
- `scratchpad/preview/build.py` — add `render_library()`, wire it into the `library` page, replacing the current placeholder.
- `scratchpad/preview/index.html` — regenerated by `build.py` (never hand-edited).
- New: `scratchpad/preview/components/` (optional) — if any component's markup grows past ~40 lines, split it into its own file loaded by `build.py`.

## Verification
- `http://127.0.0.1:8765/#library` renders the Component Library page with 5 sub-tabs; each contains every P0 component with all states cycleable via its toggle.
- Voice Orb visibly animates through idle → listening → thinking → speaking; Status Pill text updates in sync.
- Grade Ring cycles A → B → C → D and each grade uses its band color from `Symantic/GradeColors`.
- Property Card cycles Compact ↔ Expanded inline (no navigation).
- `grep -iE '#[0-9a-f]{3,8}' scratchpad/preview/index.html | grep -v 'swatch\|tokens.json'` returns nothing — proves no hardcoded colors leaked in.
- Variables tab still works unchanged.
