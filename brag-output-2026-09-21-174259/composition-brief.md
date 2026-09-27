# Hyperframes Composition Brief: Profit Drive

## Objective
Create a 21s launch-style brag video for Profit Drive — voice-first field agent for real-estate scouts.

## Output
- Composition directory: `brag-output-2026-09-21-174259/composition/`
- Rendered video: `brag-output-2026-09-21-174259/brag.mp4`
- Format: landscape — 1920x1080
- Duration: 21.5s

## Source Material
- Project root: `/Users/ghaniya.usmani/Desktop/Profit Drive`
- Primary files read: `PRODUCT.md`, `design-system/tokens.json`, `design-system/preview/index.html`, `design-system/preview/property-card-lead.html`
- Product name: **Profit Drive**
- Tagline / strongest claim: *"A field partner in your passenger seat."* + *"3× more qualified leads per drive."*
- Key UI moment to recreate: **home screen** (greeting + "10 new leads scouted" callout + Oak Valley property panel with A/B/C/D grade rows) and the **drive sheet** (voice orb + "Approaching …" + coral toast "Saved as potential lead").
- Copy that must appear verbatim:
  - "PROFIT DRIVE"
  - "A field partner. Shotgun seat."
  - "Morning, Joe — welcome to your territory."
  - "10 new leads scouted"
  - "Oak Valley · 6 properties"
  - "312 Trinity St" (A), "514 Red River St" (A), "227 E 4th St" (B), "118 Neches St" (C)
  - "Approaching 312 Trinity St"
  - "Saved as potential lead"
  - "3× more qualified leads per drive"
  - "Hands on the wheel. Leads in the bag."

## Creative Direction
- Tone preset: `app-store`
- Creative direction: quiet product film for a warm, human field partner; one earnest coral moment
- Interpretation: snap-in-then-hold, generous negative space, one bell at the payoff, no strobing
- Angle: not a CRM; the agent is the partner. Show the app *working the drive*.
- Hook: coral wordmark stamp with soft coral halo
- Outro / punchline: *"Hands on the wheel. Leads in the bag."*
- Avoid: enterprise chrome, generic SaaS language, waveform bars, dashboards, sidebar navs, feature-list slabs.

## Visual Identity
- Background: `#FFFFFF` (canvas) / `#F7F7F7` (panel bg)
- Text: `#222222` primary, `#717171` muted, `#B0B0B0` soft
- Accent: `#E96A6A` (brand coral). Grade colors: `#1A7F42` A, `#E8A317` B, `#D93025` C
- Display font: Inter 600–700
- Body font: Inter 400–500
- Visual references from the project: coral pill CTA, `plead` card structure, `home-callout` big-number tile, `pcard-grade-badge` letter badges, `voice-orb` breathing rings.

## Storyboard
See `brag-plan.md`. Six scenes on a single 1920x1080 composition, cross-cutting via GSAP timeline (`paused: true`, registered on `window.__timelines.root`).

Scene summary:
1. Hook: Wordmark stamp — 3.5s — "PROFIT DRIVE" + "A field partner. Shotgun seat."
2. Home reveal — 4.0s — phone with greeting + "10 new leads scouted" callout
3. Graded properties — 4.0s — Oak Valley panel with 4 grade-badge rows appearing on beats 5.80/6.34/6.86/7.38
4. Drive view + toast — 4.0s — full-bleed map, voice orb, "Approaching 312 Trinity St" + coral "Saved as potential lead" toast
5. Deadpan stat — 3.0s — "3×" coral huge, caption below
6. Outro — 3.0s — wordmark + "Hands on the wheel. Leads in the bag." + bell

## Audio
- Audio role: warm bed + sparse professional accents
- Audio arc: fade in 0–0.4s → hold at 0.30 → duck to 0.20 at 17.9s under bell → cut at 19.8s
- Music: `assets/music/happy-beats-business-moves-vol-11-by-ende-dot-app.mp3`
- Music treatment: 0.30 volume; ducks to 0.20 under the outro bell
- Music cue guidance: preset at `assets/music/cues/happy-beats-business-moves-vol-11-by-ende-dot-app.music-cues.json`. Strong cues in-window: 1.60, 3.70, 5.80, 6.34, 8.96, 12.65, 17.91. Beat grid ~0.53s apart.
- Audio-reactive treatment: subtle — the coral halo behind the hook wordmark uses a slow CSS opacity/scale pulse tuned to ~114 BPM as a stand-in for RMS (Hyperframes audio-reactive extraction skipped — no `hyperframes-creative` skill available; documented, not blocking).
- Audio-coupled moments:
  - Scene 1 wordmark stamp — `impact/impactSoft_medium_001` at 1.55s (near 1.60s strong cue)
  - Scene 2 phone landing — `interface/drop_002` at 3.65s (near 3.70s)
  - Scene 2 callout tile — `interface/click_002` at 4.20s
  - Scene 3 grade rows — `casino/card-place-{1,2,3,4}` at 5.80, 6.34, 6.86, 7.38 (beat grid)
  - Scene 4 drive sheet — `interface/drop_001` at 8.50s
  - Scene 4 toast — `interface/click_002` at 8.92s (near 8.96s)
  - Scene 5 "3×" reveal — `interface/bong_001` at 12.60s (near 12.65s)
  - Scene 6 outro — `impact/impactBell_heavy_000` at 17.85s (near 17.91s)
- SFX selection guidance: soft and warm; nothing punchy. Match `casino/card-place-*` to the four grade-row entries; keep them at 0.55 volume.
- SFX analysis guidance: not read (skill has an analysis file, but the selections here are all low-HF-risk families per `audio.md`).
- Exact SFX choice: locked above; volumes 0.55–0.75.
- Audio files: already copied into `composition/assets/music/` and `composition/assets/sfx/{interface,impact,casino}/`.

## Hyperframes Instructions
Companion skills (`hyperframes-core`, `hyperframes-animation`, `hyperframes-creative`, `hyperframes-keyframes`, `hyperframes-cli`) are not installed on this machine — the Hyperframes CLI (v0.8.58) is. Composition follows the CLI's own docs (`data-attributes`, `compositions`, `gsap`) and the audio contract in `audio.md`.

- Show real product moments — home + drive UIs are recreated inline in HTML/CSS/SVG (no external images), using the exact copy and colors from the source.
- Every text element has a reading-time floor (≥0.8s for short labels, ≥1.2s for sentences).
- Music always present; SFX motion-matched at 0.55–0.75 volume; music ducks under the outro bell.
- Beat locks: wordmark 1.55/1.60, phone 3.65/3.70, four grade rows 5.80/6.34/6.86/7.38, toast 8.92/8.96, stat 12.60/12.65, bell 17.85/17.91.
- `hyperframes check` must pass before render.
