# Brag Plan: Profit Drive

## What is this app?
A voice-first field agent for "Drive-for-Dollars" real-estate scouts — the agent pre-scouts each zip using web listings + satellite imagery, grades every property A→D, narrates each stop from the shotgun seat, and confirms leads with one word or one tap so the driver never takes eyes off the road.

## The angle
Not "yet another CRM for realtors." A **partner in the passenger seat** — warm, human, coral instead of enterprise blue. Show the app *working the drive*: the morning greeting, the graded map, the voice orb narrating a stop, the "saved as potential lead" toast. Restraint and warmth over feature bombardment.

## Hook (first 2-3 seconds)
Silent white. Coral wordmark **Profit Drive** stamps in with a soft coral halo — feels like a car key clicking. Then the tagline snaps under it: *"A field partner. Shotgun seat."*

## Key moments (the middle)
- Phone tilts up on the home screen: *"Morning, **Joe** — welcome to your territory · 10 new leads scouted."*
- Map fills with property pins; four grade badges (A, A, B, C) pop in one-by-one along an Oak Valley street row.
- Drive view: voice orb pulses, status flips to *"Approaching 312 Trinity St"*, then a coral toast confirms *"Saved as potential lead."*
- One deadpan stat card: **3× more qualified leads per drive.**

## Outro / punchline
Coral wordmark returns on white. Under it: *"Hands on the wheel. Leads in the bag."* Soft bell settles.

## User flow worth showing
Real driver arc from the prototype:
1. Home → greeting + "10 new leads scouted" callout + Oak Valley property panel with A/B/C/D badges.
2. Tap the mic orb → agent-planned route → **Start drive**.
3. Drive view: agent announces next stop → toast confirms save → progress bar advances.

## Tone
- Preset: `app-store`
- Creative direction: quiet product film for a warm, human field partner — restraint with one earnest coral moment.
- Interpretation: smooth feature-card reveals, generous negative space, snap-in then long hold, no strobing, one bell at the payoff. The video should feel like the product's own voice — confident, warm, no enterprise chrome.

## Format: landscape — 1920x1080
## Duration: 20s

## Visual identity (from the project)
- Background: `#FFFFFF` (canvas) with `#F7F7F7` (neutral_50) for panel scenes
- Accent: `#E96A6A` (brand coral); grade colors `#1A7F42` (A green), `#E8A317` (B amber), `#D93025` (C tomato), `#9D2525` (D deep red) — from `design-system/tokens.json`
- Text: `#222222` (near_black); muted `#717171` (neutral_600)
- Display font: Inter, 600–700 weight, tight letter-spacing (-0.01em)
- Body font: Inter, 400–500
- Strongest visual element: the phone mockup from `design-system/preview/index.html` — home screen with map + grade-badge property rows, plus the drive sheet with voice orb.

## Share copy (draft)
Profit Drive: the field partner in your passenger seat. Zip pre-scouted, properties graded A→D, every stop confirmed by voice. Hands on the wheel. Leads in the bag.

## Audio direction
- Role: warm bed with sparse professional accents
- Music: `happy-beats-business-moves-vol-11-by-ende-dot-app.mp3` (warm, business-y, 114.84 BPM)
- Music treatment: fade in over 0.4s, sit at 0.30 volume, dip to 0.20 under the closing bell, cut clean at the end
- Music cue guidance: preset available at `assets/music/cues/happy-beats-business-moves-vol-11-by-ende-dot-app.music-cues.json`. Strong cues in-window: 1.60, 3.70, 5.80, 6.34, 8.96, 12.65, 17.91. Beat grid ~0.53s apart. Lock hook stamp near 1.60s, phone reveal near 3.70s, grade badges across beats 5.80/6.34/6.86/7.38, drive toast near 8.96s, stat card near 12.65s, outro bell near 17.91s.
- Audio-reactive treatment: subtle; a soft coral halo behind the wordmark breathes with RMS. No waveforms, no bars.
- SFX posture: sparse, motion-matched, restrained (~0.6 volume, softer for drops)
- Audio-coupled moments: wordmark stamp (soft impact), phone tilt-in (drop), grade badges (card-place fan), toast (click), stat card (soft impact), outro (bell)
- Restraint rule: no more than one accent per moment; nothing on beats 2/4 just because they exist.

## Storyboard

### Scene 1 — Hook: Wordmark stamp — 3.5s
White canvas. **PROFIT DRIVE** scales in from 0.98→1.0 with soft coral halo breathing behind. Tagline snaps in below: *"A field partner. Shotgun seat."* Halo pulses gently to the music RMS through this scene.
Sequential/interaction: none.
Audio intent: warm start, one dry stamp.
Audio-coupled idea: `impact/impactSoft_medium_001` at 1.55s to sit inside the 1.60s strong cue.
Music: fades in, warm bed.
Transition mood: clean cut → Scene 2

### Scene 2 — Home reveal — 4s
Phone shell tilts in from below (12° → 0°, 480ms). Home screen shows: zip pill *"Zip · 78701"*, greeting **"Morning, Joe — welcome to your territory."**, big callout **"10  new leads scouted · Ready when you are."** Callout number 10 counts up 0→10 in 900ms.
Sequential/interaction: yes — greeting fades in, then callout tile lifts up.
Audio intent: soft landing, no drama.
Audio-coupled idea: `interface/drop_002` at phone landing (3.65s → near 3.70s strong cue). Faint `interface/click_002` on callout tile.
Music: bed continues.
Transition mood: soft slide-up → Scene 3

### Scene 3 — Graded properties — 4s
Camera pushes into the phone map region. Oak Valley property panel slides up. Four `prop-row` cards arrive in sequence with grade badges: **A** (312 Trinity St · 0.2 mi), **A** (514 Red River · 0.4 mi), **B** (227 E 4th · 0.5 mi), **C** (118 Neches · 0.7 mi). Each card slides right→center and its grade badge pops last with a subtle bounce.
Sequential/interaction: yes — 4 cards on beats 5.80, 6.34, 6.86, 7.38.
Audio intent: satisfying stacking rhythm.
Audio-coupled idea: `casino/card-place-1..4` in sequence on those beats (0.55 volume).
Music: bed continues.
Transition mood: quick wipe → Scene 4

### Scene 4 — Drive view + toast — 4s
Full-bleed map behind. Voice orb pulses (coral inner + outer ring breathing). Drive sheet slides up: **"Approaching 312 Trinity St"**. A moment later a coral toast slides in from the top: ✓ **"Saved as potential lead."** Progress bar fills 8% → 25%.
Sequential/interaction: yes — sheet up, orb pulse, toast slam in.
Audio intent: quiet competence + one small win.
Audio-coupled idea: `interface/drop_001` on sheet, `interface/click_002` on toast (~8.9s near 8.96s strong cue).
Music: bed continues.
Transition mood: clean wipe → Scene 5

### Scene 5 — Deadpan stat — 3s
White canvas. Enormous coral number **3×** scales in. Under it, thin near-black type: *"more qualified leads per drive."* Number holds for 1.8s.
Sequential/interaction: yes — number pops, caption fades in 200ms later.
Audio intent: dry, confident.
Audio-coupled idea: `interface/bong_001` at 12.60s near the 12.65s strong cue.
Music: bed continues.
Transition mood: crossfade → Scene 6

### Scene 6 — Outro — 3s
Wordmark **PROFIT DRIVE** returns on white with a subtle coral underline that draws left→right in 500ms. Tagline: *"Hands on the wheel. Leads in the bag."* Music ducks to 0.20, bell rings, then music cuts clean.
Sequential/interaction: none.
Audio intent: warm exhale.
Audio-coupled idea: `impact/impactBell_heavy_000` at 17.85s near the 17.91s strong cue.
Music: fade to 0.20 at 17.9s, cut at 19.8s.
Transition mood: hold on final frame.

Total: 3.5 + 4.0 + 4.0 + 4.0 + 3.0 + 3.0 = **21.5s** (a hair over target for outro breathing room — inside 15–25s).

**Music mood for this video:** warm, business-y, upbeat but restrained.
**Audio summary:** warm bed under the entire piece, four sparse motion-matched accents (stamp, cards, toast, bong), one bell at the outro; music ducks under the bell then cuts clean.
