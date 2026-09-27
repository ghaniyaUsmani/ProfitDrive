# Product

## Register

product

## Users

**Drive-for-Dollars scouts in the field.** They're driving assigned zip codes to find distressed properties (visible neglect, vacancy signals, tax/legal cues, dated exteriors) that can be turned into leads for real estate agents to close.

Their context is unforgiving: hands on the wheel, eyes on the road, phone dashboard-mounted. The job is repetitive but requires judgment — spotting the difference between "just an old house" and "an owner who's ready to sell." A typical drive runs 2–8 hours across dozens of streets. Manual capture today is slow, dangerous, and easy to forget.

**The job to be done:** cover more ground per drive, capture more qualified leads, and never lose a promising property to fumbled data entry — without taking eyes off the road.

## Product Purpose

Profit Drive replaces manual property hunting with an intelligent agent. The agent pre-scouts each driver's assigned zip using web listings and satellite imagery, generates a **distress grade (A → D)** for every property, and shortlists the highest-signal ones. When the driver taps **Start drive**, the agent runs a conversational route-planning step, then narrates each stop — announcing arrival, showing captured details, suggesting tags, and confirming as a lead in one bulk-accept motion.

**Success looks like:** the driver captures 3× more qualified leads per drive than the manual flow, without touching a keyboard while moving.

## Brand Personality

**Confident · warm · human.**

The agent is a **field partner sitting shotgun** — a smart friend riding with the driver, not a corporate voice or a checklist reader. It speaks in contractions ("this one's a fit"), acknowledges before advancing ("got it — added"), and takes small conversational risks ("quieter street," "looks rough"). It celebrates the driver's wins without turning the app into a game.

The visual language matches the voice: warm coral accent (the brand's heartbeat), plenty of white space, generous typography, no enterprise chrome, no gamification confetti, no data-dense dashboards.

## Anti-references

**CRM software (Salesforce, HubSpot, Zoho dashboards).** Profit Drive is the opposite of a real-estate CRM. No sidebar navigation stuffed with modules, no dense data grids, no blue-and-white enterprise chrome, no dropdown menus for every action, no configurable columns, no bureaucratic form layouts. The user is behind a wheel, not at a desk with a mouse.

Also avoid, by extension:
- Consumer-app gamification (streaks-and-badges dopamine loops turning real work into a game)
- Full-screen chat-transcript UIs (walls of text — the agent is a partner, not a text interface)
- Consumer real-estate marketplace vibes (Zillow/Redfin marketing chrome)

## Design Principles

1. **Voice-first, cards-secondary.** The agent narrates; the screen confirms. Cards exist for decisions the driver has to make, never for information the agent is already speaking.
2. **Glanceable in motion, rich when parked.** Every card has two states. Compact = big touch targets, minimum info, safe to look at for one second. Expanded = full profile, editable, appears when the driver stops moving.
3. **Suggestion, not automation.** The agent proposes tags, campaigns, and lead decisions. The driver confirms with a word or a tap. No silent auto-actions.
4. **Warmth carries the brand, not the chrome.** Coral is used sparingly and deliberately — the CTA, the active state, the "hot lead" grade. Not gradients-on-everything. Warmth also comes from copy tone and generous spacing, not from tinted backgrounds.
5. **Safety-first micro-affordances.** In-drive touch targets ≥ 56 px, high contrast, no more than three actions per card, everything voice-reachable. A tap must never be required to complete a stop-interaction while moving.

## Accessibility & Inclusion

**WCAG 2.2 AA + hands-free-while-driving critical.**

- Contrast ratios ≥ 4.5:1 for body, ≥ 3:1 for large text, verified against every background (including the coral accent).
- **Every in-drive action reachable by voice alone.** Tap fallbacks exist for parked use only; the drive itself never requires a tap.
- Semantic HTML throughout; screen-reader clean; focus states visible on every interactive element.
- `prefers-reduced-motion` honored — animations degrade to instant transitions or crossfades.
- Grade colors always paired with a letter (A/B/C/D) so color-blind drivers get the signal from shape/text, not hue.
- Touch targets ≥ 56 px in the in-drive view (larger than the standard 44 px minimum) to account for driver hand tremor and dashboard mounting angle.
- Language kept plain and short; the agent never uses jargon the driver hasn't already opted into.
