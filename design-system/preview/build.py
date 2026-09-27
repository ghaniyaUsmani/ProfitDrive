#!/usr/bin/env python3
"""Read tokens.json, resolve every alias, emit a single self-contained index.html."""
import json, os, html, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "tokens.json")
OUT = os.path.join(HERE, "index.html")

with open(SRC) as f:
    D = json.load(f)

COLLECTIONS = D["collections"]

# ---------- resolver: walk `Group/name` aliases across collections ----------

def _lookup(path: str):
    """Path is `Group/name` (e.g. `Colors/red_600`). Search every collection's
    matching group, return (value, source_collection, source_group)."""
    if "/" not in path:
        return None, None, None
    group, name = path.split("/", 1)
    for coll_name, coll in COLLECTIONS.items():
        g = coll["groups"].get(group)
        if g and name in g:
            return g[name], coll_name, group
    return None, None, None

def resolve(v, chain=None):
    """Return {'value': final, 'chain': [(collection, group, name, value), ...]}"""
    chain = chain or []
    if isinstance(v, dict) and "alias" in v:
        path = v["alias"]
        found, coll, group = _lookup(path)
        name = path.split("/", 1)[1]
        chain = chain + [(coll, group, name, found)]
        if found is None:
            return {"value": None, "chain": chain, "broken": path}
        return resolve(found, chain)
    return {"value": v, "chain": chain}


# ---------- HTML builders ----------

def esc(s): return html.escape(str(s))

def swatch(hexv, size=44):
    return f'<span class="swatch" style="background:{esc(hexv)};width:{size}px;height:{size}px"></span>'

def alias_pill(coll, group, name):
    return f'<span class="pill pill-{esc(coll.lower())}"><span class="pill-coll">{esc(coll)}</span><span class="pill-path">{esc(group)}/{esc(name)}</span></span>'

def render_chain(chain):
    if not chain: return ""
    parts=[]
    for coll, group, name, val in chain:
        parts.append(alias_pill(coll, group, name))
    return '<div class="chain">' + '<span class="arrow">→</span>'.join(parts) + '</div>'


# ---------- section renderers ----------

def render_primitive_colors(g):
    rows=[]
    for name, hexv in g.items():
        rows.append(f"""
        <div class="tok tok-color">
          {swatch(hexv, 56)}
          <div class="tok-body">
            <div class="tok-name">{esc(name)}</div>
            <div class="tok-value mono">{esc(hexv)}</div>
          </div>
        </div>""")
    return f'<div class="grid grid-color">{"".join(rows)}</div>'

def render_font_family(g):
    rows=[]
    for name, val in g.items():
        rows.append(f"""
        <div class="tok tok-font">
          <div class="tok-preview" style="font-family:{esc(val)},system-ui,sans-serif;font-size:28px">Aa Bb Cc 1234</div>
          <div class="tok-body">
            <div class="tok-name">{esc(name)}</div>
            <div class="tok-value mono">{esc(val)}</div>
          </div>
        </div>""")
    return f'<div class="grid grid-font">{"".join(rows)}</div>'

def render_font_size(g):
    rows=[]
    for name, val in g.items():
        rows.append(f"""
        <div class="tok tok-size">
          <div class="tok-preview" style="font-size:{esc(val)}px;line-height:1.15">Ag</div>
          <div class="tok-body">
            <div class="tok-name">{esc(name)}</div>
            <div class="tok-value mono">{esc(val)}px</div>
          </div>
        </div>""")
    return f'<div class="grid grid-size">{"".join(rows)}</div>'

def render_font_weight(g):
    rows=[]
    for name, val in g.items():
        rows.append(f"""
        <div class="tok tok-weight">
          <div class="tok-preview" style="font-weight:{esc(val)};font-size:22px">The quick brown fox</div>
          <div class="tok-body">
            <div class="tok-name">{esc(name)}</div>
            <div class="tok-value mono">{esc(val)}</div>
          </div>
        </div>""")
    return f'<div class="stack">{"".join(rows)}</div>'

def render_spacing(g):
    rows=[]
    for name, val in g.items():
        rows.append(f"""
        <div class="tok tok-spc">
          <div class="tok-preview spc-bar" style="width:{esc(val)}px"></div>
          <div class="tok-body">
            <div class="tok-name">{esc(name)}</div>
            <div class="tok-value mono">{esc(val)}px</div>
          </div>
        </div>""")
    return f'<div class="stack">{"".join(rows)}</div>'

def render_radius(g):
    rows=[]
    for name, val in g.items():
        rows.append(f"""
        <div class="tok tok-radius">
          <div class="tok-preview radius-demo" style="border-radius:{esc(val)}px"></div>
          <div class="tok-body">
            <div class="tok-name">{esc(name)}</div>
            <div class="tok-value mono">{esc(val)}px</div>
          </div>
        </div>""")
    return f'<div class="grid grid-radius">{"".join(rows)}</div>'

def render_strokes(g):
    rows=[]
    for name, v in g.items():
        r = resolve(v)
        color = r["value"] or "transparent"
        rows.append(f"""
        <div class="tok tok-stroke">
          <div class="tok-preview stroke-demo" style="border:2px solid {esc(color)}"></div>
          <div class="tok-body">
            <div class="tok-name">{esc(name)}</div>
            <div class="tok-value mono">{esc(color)}</div>
            {render_chain(r["chain"])}
          </div>
        </div>""")
    return f'<div class="grid grid-stroke">{"".join(rows)}</div>'

def render_symantic_colors(g):
    rows=[]
    for name, v in g.items():
        r = resolve(v)
        hexv = r["value"] or "#000"
        rows.append(f"""
        <div class="tok tok-color">
          {swatch(hexv, 56)}
          <div class="tok-body">
            <div class="tok-name">{esc(name)}</div>
            <div class="tok-value mono">{esc(hexv)}</div>
            {render_chain(r["chain"])}
          </div>
        </div>""")
    return f'<div class="grid grid-color">{"".join(rows)}</div>'

def render_symantic_sizes(g):
    rows=[]
    for name, v in g.items():
        r = resolve(v)
        val = r["value"] or 14
        rows.append(f"""
        <div class="tok tok-size">
          <div class="tok-preview" style="font-size:{esc(val)}px;line-height:1.15">Ag</div>
          <div class="tok-body">
            <div class="tok-name">{esc(name)}</div>
            <div class="tok-value mono">{esc(val)}px</div>
            {render_chain(r["chain"])}
          </div>
        </div>""")
    return f'<div class="grid grid-size">{"".join(rows)}</div>'

def render_symantic_weights(g):
    rows=[]
    for name, v in g.items():
        r = resolve(v)
        val = r["value"] or 400
        rows.append(f"""
        <div class="tok tok-weight">
          <div class="tok-preview" style="font-weight:{esc(val)};font-size:20px">The quick brown fox</div>
          <div class="tok-body">
            <div class="tok-name">{esc(name)}</div>
            <div class="tok-value mono">{esc(val)}</div>
            {render_chain(r["chain"])}
          </div>
        </div>""")
    return f'<div class="stack">{"".join(rows)}</div>'

def render_component_colors(g):
    rows=[]
    for name, v in g.items():
        r = resolve(v)
        hexv = r["value"] or "#000"
        rows.append(f"""
        <div class="tok tok-color">
          {swatch(hexv, 56)}
          <div class="tok-body">
            <div class="tok-name">{esc(name)}</div>
            <div class="tok-value mono">{esc(hexv)}</div>
            {render_chain(r["chain"])}
          </div>
        </div>""")
    return f'<div class="grid grid-color">{"".join(rows)}</div>'


# ---------- assemble collections ----------

RENDERERS = {
    ("Primitive","Colors"):       render_primitive_colors,
    ("Primitive","FontFamily"):   render_font_family,
    ("Primitive","FontSize"):     render_font_size,
    ("Primitive","FontWeights"):  render_font_weight,
    ("Primitive","Spacing"):      render_spacing,
    ("Primitive","CornerRadius"): render_radius,
    ("Primitive","Strokes"):      render_strokes,
    ("Symantic","Colors"):        render_symantic_colors,
    ("Symantic","TextSizes"):     render_symantic_sizes,
    ("Symantic","TextWeights"):   render_symantic_weights,
    ("Symantic","GradeColors"):   render_symantic_colors,
    ("components","Colors"):      render_component_colors,
}

def render_collection(coll_name):
    coll = COLLECTIONS[coll_name]
    parts=[f'<h2 class="coll-title"><span>{esc(coll_name)}</span><span class="count">{coll["count"]} variables</span></h2>']
    for group_name, group in coll["groups"].items():
        renderer = RENDERERS.get((coll_name, group_name))
        if not renderer:
            body = f'<pre>{esc(json.dumps(group, indent=2))}</pre>'
        else:
            body = renderer(group)
        parts.append(f'<section class="group" id="{esc(coll_name)}-{esc(group_name)}"><h3 class="group-title">{esc(group_name)} <span class="count">{len(group)}</span></h3>{body}</section>')
    return '<section class="collection">' + "".join(parts) + '</section>'


# ---------- usage demos (derived helpers, not new Figma tokens) ----------

def get(coll, group, name):
    """Read a resolved value out of the token graph."""
    v = COLLECTIONS[coll]["groups"][group][name]
    return resolve(v)["value"]

def usage_demos():
    # Look up the actual resolved hex values for the demos
    def c(coll, group, name): return get(coll, group, name) or "#000"
    def n(coll, group, name): return get(coll, group, name) or 14

    demo = f"""
    <section class="collection demos">
      <h2 class="coll-title"><span>In-use demos</span><span class="count">derived from your tokens</span></h2>

      <section class="group">
        <h3 class="group-title">Primary button (states)</h3>
        <div class="demo-row">
          <button class="demo-btn" style="background:{c('components','Colors','primarybutton_bg_active')};color:{c('Symantic','Colors','color_text_inverse')};padding:{get('Primitive','Spacing','spc_12')}px {get('Primitive','Spacing','spc_24')}px;border-radius:{get('Primitive','CornerRadius','radius_md')}px;font-weight:{c('Symantic','TextWeights','button_txt_weight')};font-size:{n('Symantic','TextSizes','button_txt_size')}px;font-family:{get('Primitive','FontFamily','font_family')},system-ui,sans-serif">Default</button>
          <button class="demo-btn" style="background:{c('components','Colors','primarybutton_bg_hover')};color:{c('Symantic','Colors','color_text_inverse')};padding:{get('Primitive','Spacing','spc_12')}px {get('Primitive','Spacing','spc_24')}px;border-radius:{get('Primitive','CornerRadius','radius_md')}px;font-weight:{c('Symantic','TextWeights','button_txt_weight')};font-size:{n('Symantic','TextSizes','button_txt_size')}px;font-family:{get('Primitive','FontFamily','font_family')},system-ui,sans-serif">Hover</button>
          <button class="demo-btn" style="background:{c('Symantic','Colors','color_brand_active')};color:{c('Symantic','Colors','color_text_inverse')};padding:{get('Primitive','Spacing','spc_12')}px {get('Primitive','Spacing','spc_24')}px;border-radius:{get('Primitive','CornerRadius','radius_md')}px;font-weight:{c('Symantic','TextWeights','button_txt_weight')};font-size:{n('Symantic','TextSizes','button_txt_size')}px;font-family:{get('Primitive','FontFamily','font_family')},system-ui,sans-serif">Active</button>
          <button class="demo-btn" style="background:{c('components','Colors','primarybutton_bg_disable')};color:{c('Symantic','Colors','color_text_inverse')};padding:{get('Primitive','Spacing','spc_12')}px {get('Primitive','Spacing','spc_24')}px;border-radius:{get('Primitive','CornerRadius','radius_md')}px;font-weight:{c('Symantic','TextWeights','button_txt_weight')};font-size:{n('Symantic','TextSizes','button_txt_size')}px;font-family:{get('Primitive','FontFamily','font_family')},system-ui,sans-serif;cursor:not-allowed">Disabled</button>
        </div>
      </section>

      <section class="group">
        <h3 class="group-title">Secondary button (states)</h3>
        <div class="demo-row">
          <button class="demo-btn" style="background:{c('components','Colors','secondarybutton_bg_active')};color:{c('components','Colors','body_txt_color')};border:2px solid {c('Primitive','Strokes','outline_light')};padding:{get('Primitive','Spacing','spc_12')}px {get('Primitive','Spacing','spc_24')}px;border-radius:{get('Primitive','CornerRadius','radius_md')}px;font-weight:{c('Symantic','TextWeights','button_txt_weight')};font-size:{n('Symantic','TextSizes','button_txt_size')}px;font-family:{get('Primitive','FontFamily','font_family')},system-ui,sans-serif">Default</button>
          <button class="demo-btn" style="background:{c('components','Colors','secondarybutton_bg_hover')};color:{c('components','Colors','body_txt_color')};border:2px solid {c('Primitive','Strokes','outline_regular')};padding:{get('Primitive','Spacing','spc_12')}px {get('Primitive','Spacing','spc_24')}px;border-radius:{get('Primitive','CornerRadius','radius_md')}px;font-weight:{c('Symantic','TextWeights','button_txt_weight')};font-size:{n('Symantic','TextSizes','button_txt_size')}px;font-family:{get('Primitive','FontFamily','font_family')},system-ui,sans-serif">Hover</button>
          <button class="demo-btn" style="background:{c('components','Colors','secondarybutton_bg_disable')};color:{c('components','Colors','body_txt_color')};border:2px solid {c('Primitive','Strokes','outline_regular')};padding:{get('Primitive','Spacing','spc_12')}px {get('Primitive','Spacing','spc_24')}px;border-radius:{get('Primitive','CornerRadius','radius_md')}px;font-weight:{c('Symantic','TextWeights','button_txt_weight')};font-size:{n('Symantic','TextSizes','button_txt_size')}px;font-family:{get('Primitive','FontFamily','font_family')},system-ui,sans-serif;cursor:not-allowed">Disabled</button>
        </div>
      </section>

      <section class="group">
        <h3 class="group-title">Type hierarchy</h3>
        <div class="type-stack" style="font-family:{get('Primitive','FontFamily','font_family')},system-ui,sans-serif;color:{c('Symantic','Colors','color_text_primary')}">
          <div style="font-size:{n('Symantic','TextSizes','hero_heading_size')}px;font-weight:{c('Symantic','TextWeights','hero_heading_weight')}">Hero heading</div>
          <div style="font-size:{n('Symantic','TextSizes','page_title_size')}px;font-weight:{c('Symantic','TextWeights','page_title_weight')}">Page title</div>
          <div style="font-size:{n('Symantic','TextSizes','section_heading_size')}px;font-weight:{c('Symantic','TextWeights','section_heading_weight')}">Section heading</div>
          <div style="font-size:{n('Symantic','TextSizes','card_title_size')}px;font-weight:{c('Symantic','TextWeights','card_title_weight')}">Card title</div>
          <div style="font-size:{n('Symantic','TextSizes','sub_heaidng_size')}px;font-weight:{c('Symantic','TextWeights','sub_heading_weight')}">Sub heading</div>
          <div style="font-size:{n('Symantic','TextSizes','UI_label_size')}px;font-weight:{c('Symantic','TextWeights','UI_label_weight')}">UI label</div>
          <div style="font-size:{n('Symantic','TextSizes','body_txt_size')}px;font-weight:{c('Symantic','TextWeights','body_txt_weight')}">Body text — the quick brown fox jumps over the lazy dog.</div>
          <div style="font-size:{n('Symantic','TextSizes','caption_size')}px;font-weight:{c('Symantic','TextWeights','caption_weight')}">Caption</div>
          <div style="font-size:{n('Symantic','TextSizes','micro_label_size')}px;font-weight:{c('Symantic','TextWeights','micro_label_weight')}">Micro label</div>
        </div>
      </section>

      <section class="group">
        <h3 class="group-title">Status colors</h3>
        <div class="status-row">
          <div class="status-chip" style="background:{c('Symantic','Colors','success')}">Success</div>
          <div class="status-chip" style="background:{c('Symantic','Colors','progress')}">Progress</div>
          <div class="status-chip" style="background:{c('Symantic','Colors','warning')};color:#222">Warning</div>
          <div class="status-chip" style="background:{c('Symantic','Colors','error')}">Error</div>
        </div>
      </section>
    </section>"""
    return demo


# ---------- component library ----------

# Emit CSS custom properties from every resolved token so library components
# can consume them by name (no hardcoded hex).
_UNIT_GROUPS = {"FontSize", "Spacing", "CornerRadius"}
def generate_token_css_vars():
    lines = []
    for coll_name, coll in COLLECTIONS.items():
        for group_name, group in coll["groups"].items():
            for name, v in group.items():
                r = resolve(v)
                val = r["value"]
                if val is None:
                    continue
                if isinstance(val, (int, float)) and group_name in _UNIT_GROUPS:
                    css_val = f"{val}px"
                else:
                    css_val = str(val)
                var_name = f"--{group_name.lower()}-{name.lower()}"
                lines.append(f"    {var_name}: {css_val};")
    return "\n".join(lines)

TOKEN_CSS_VARS = generate_token_css_vars()


# Helper: build a token-pill referencing a var (shown under each component card).
def tp(label):
    return f'<span class="tok-pill">{esc(label)}</span>'


# ---- Icon set: Phosphor Icons (Regular weight via CDN) ----
# Semantic name in build.py -> canonical Phosphor icon name
_PHOSPHOR_MAP = {
    "distress":     "house-line",
    "legal":        "gavel",
    "vacancy":      "envelope-simple",
    "owner":        "user",
    "camera":       "camera",
    "mic":          "microphone",
    "pin":          "map-pin",
    "phone":        "phone",
    "mail":         "envelope",
    "chevron_back": "caret-left",
    "chevron_right":"caret-right",
    "chevron_down": "caret-down",
    "more":         "dots-three",
    "close":        "x",
    "check":        "check",
    "plus":         "plus",
    "lock":         "lock-simple",
    "info":         "info",
    "warn":         "warning",
    "arrow_right":  "arrow-right",
    "back_arrow":   "arrow-left",
    "send":         "paper-plane-tilt",
    "search":       "magnifying-glass",
    "sort":         "arrows-down-up",
    "filter":       "funnel-simple",
    "secured":      "bookmark-simple",
    "bed":          "bed",
    "bath":         "bathtub",
    "ruler":        "ruler",
    "heart":        "heart",
}

def icon(name, size=16, stroke=1.75, klass=""):
    phos = _PHOSPHOR_MAP.get(name, name)
    kls = f"ph-bold ph-{phos}" + (f" {esc(klass)}" if klass else "")
    return f'<i class="{kls}" style="font-size:{size}px;line-height:1"></i>'


# ---- Voice & Agent renderers ----

def _showcase(name, body, tokens, controls="", wide=False):
    """Standard showcase card: name · stage · state toggle · token pills.
    wide=True makes the card span the full library grid row — use for
    horizontal components that need width to breathe (e.g. Lead Row)."""
    pills = "".join(tp(t) for t in tokens)
    wide_cls = " lib-card-wide" if wide else ""
    return f'''
    <div class="lib-card{wide_cls}">
      <div class="lib-card-head">
        <div class="lib-card-name">{esc(name)}</div>
        {controls}
      </div>
      <div class="lib-stage">{body}</div>
      <div class="lib-tokens">{pills}</div>
    </div>'''

def _state_toggle(target_id, states):
    btns = "".join(
        f'<button class="seg-btn{" active" if i==0 else ""}" data-state-target="{esc(target_id)}" data-state="{esc(s)}">{esc(s)}</button>'
        for i, s in enumerate(states)
    )
    return f'<div class="seg">{btns}</div>'

def render_voice_orb():
    body = '''
      <div class="orb-stage">
        <div class="voice-orb" id="orb-demo" data-state="idle">
          <div class="orb-group">
            <span class="orb-core"></span>
            <span class="orb-ring"></span>
            <span class="orb-ring orb-ring-2"></span>
          </div>
          <div class="orb-wave" aria-hidden="true">
            <span></span><span></span><span></span><span></span>
            <span></span><span></span><span></span><span></span>
          </div>
        </div>
        <div class="orb-status" data-status-target="orb-demo">Idle</div>
      </div>
    '''
    controls = _state_toggle("orb-demo", ["idle","listening","speaking","thinking","muted","error"])
    return _showcase(
        "Voice Orb", body,
        ["colors/red_600 (accent)", "colors/neutral_400 (muted)", "colors/tomato_red (error)"],
        controls,
    )

def render_status_pill():
    body = '''
      <div class="pill-row">
        <div class="status-pill status-listening"><span class="dot"></span>Listening…</div>
        <div class="status-pill status-thinking"><span class="dot"></span>Thinking…</div>
        <div class="status-pill status-speaking"><span class="dot"></span>Speaking…</div>
        <div class="status-pill status-idle"><span class="dot"></span>Tap to talk</div>
      </div>
    '''
    return _showcase("Status Pill", body, ["colors/near_black", "colors/neutral_400", "cornerradius/radius_pill"])

def render_waveform():
    bars = "".join(f'<span class="wave-bar" style="animation-delay:{-i*0.08}s"></span>' for i in range(12))
    body = f'''
      <div class="wave-stage">
        <div class="waveform" id="wave-demo" data-state="listening">{bars}</div>
      </div>
    '''
    controls = _state_toggle("wave-demo", ["listening","idle"])
    return _showcase("Waveform Ribbon", body, ["colors/red_600", "colors/neutral_400"], controls)

def render_ptt():
    body = '''
      <div class="ptt-stage">
        <button class="ptt-btn" aria-label="Push to talk">
          <svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/><path d="M19 10v2a7 7 0 0 1-14 0v-2"/><line x1="12" y1="19" x2="12" y2="23"/><line x1="8" y1="23" x2="16" y2="23"/></svg>
        </button>
      </div>
    '''
    return _showcase("Push-to-Talk", body, ["components/primarybutton_bg_active", "cornerradius/radius_pill"])

def render_transcript():
    body = '''
      <div class="lib-transcript-stage">
        <div class="convo-transcript convo-transcript-static">
          <div class="convo-line enter age-4">Planning today's route.</div>
          <div class="convo-line enter age-3">Six stops in Oak Valley — starting at 312 Trinity.</div>
          <div class="convo-line enter age-2">Approaching 123 Main St. This one looks distressed —</div>
          <div class="convo-line enter age-1">overgrown lawn, visible roof damage.</div>
          <div class="convo-line enter driver">Add it.</div>
          <div class="convo-line enter">Added with tags overgrown lawn and roof damage. Grade A.</div>
        </div>
      </div>
      <p class="lib-note">Streaming transcript used on the conversation screen. Agent lines render dark; driver replies use the primary red. Older lines "age" — shrinking and dimming as new ones stream in — instead of scrolling off. No chat bubbles: the transcript reads like a subtitle track over the mic orb.</p>
    '''
    return _showcase("Transcript · Streaming Line", body, ["textsizes/screen_title_size", "components/primarybutton_bg_active", "colors/text"], wide=True)

def render_nudge_banner():
    body = f'''
      <div class="nudge-banner">
        <span class="nudge-icon">{icon("pin", 18)}</span>
        <div class="nudge-body">
          <div class="nudge-title">Approaching 123 Main St</div>
          <div class="nudge-meta">Grade A · 0.2 mi</div>
        </div>
        <button class="nudge-dismiss" aria-label="Dismiss">{icon("close", 14)}</button>
      </div>
    '''
    return _showcase("Agent Nudge Banner", body, ["gradecolors/grade_a", "colors/near_black"])

def render_orb_dock():
    body = '''
      <div class="dock-stage">
        <div class="dock-fake-content">Screen content</div>
        <div class="dock-orb dock-orb-right">
          <div class="voice-orb" data-state="idle" style="width:56px;height:56px"><span class="orb-core"></span><span class="orb-ring"></span></div>
          <div class="orb-status">Tap to talk</div>
        </div>
      </div>
      <p class="lib-note">Docked bottom-right, thumb-anchored. Handedness flip mirrors it to bottom-left. Slides above bottom sheets. Respects safe-area.</p>
    '''
    return _showcase("Ambient Orb Dock", body, ["spacing/spc_16", "spacing/spc_24"])


# ---- Data Display renderers ----

def render_grade_ring():
    body = '''
      <div class="grade-stage" id="grade-stage">
        <div class="grade-ring grade-ring-s" data-grade-target="grade-stage" data-size="s"><span>A</span></div>
        <div class="grade-ring grade-ring-m" data-grade-target="grade-stage" data-size="m"><span>A</span></div>
        <div class="grade-ring grade-ring-l" data-grade-target="grade-stage" data-size="l"><span>A</span></div>
      </div>
    '''
    btns = "".join(
        f'<button class="seg-btn{" active" if g=="A" else ""}" data-grade-set="grade-stage" data-grade="{g}">{g}</button>'
        for g in ["A","B","C","D"]
    )
    controls = f'<div class="seg">{btns}</div>'
    return _showcase(
        "Distress Grade Ring", body,
        ["gradecolors/grade_a", "gradecolors/grade_b", "gradecolors/grade_c", "gradecolors/grade_d"],
        controls,
    )

def render_grade_badge():
    body = '''
      <div class="badge-stack">
        <span class="grade-badge grade-a"><b>A</b> Prime</span>
        <span class="grade-badge grade-b"><b>B</b> Strong</span>
        <span class="grade-badge grade-c"><b>C</b> Marginal</span>
        <span class="grade-badge grade-d"><b>D</b> Skip</span>
      </div>
    '''
    return _showcase("Grade Badge", body, ["gradecolors/grade_a…grade_d", "cornerradius/radius_pill"])

def render_stat_tile():
    body = '''
      <div class="stat-row">
        <div class="stat-tile">
          <div class="stat-num">12</div>
          <div class="stat-label">Leads today</div>
        </div>
        <div class="stat-tile">
          <div class="stat-num">A-</div>
          <div class="stat-label">Avg grade</div>
        </div>
        <div class="stat-tile">
          <div class="stat-num">5<span class="stat-sub">day</span></div>
          <div class="stat-label">Streak</div>
        </div>
      </div>
    '''
    return _showcase("Stat Tile", body, ["textsizes/hero_heading_size", "colors/near_black"])

def render_progress():
    body = '''
      <div class="progress-stack">
        <div class="progress-meta"><span>Route progress</span><span>7 / 18 stops</span></div>
        <div class="progress-bar"><div class="progress-fill" style="width:38%"></div></div>
      </div>
    '''
    return _showcase("Progress Bar", body, ["colors/red_600", "colors/neutral_200", "cornerradius/radius_pill"])

def render_address_block():
    body = '''
      <div class="addr-block">
        <div class="addr-line-1">123 Main St</div>
        <div class="addr-line-2">Austin, TX 78701</div>
        <div class="addr-meta">Travis County · APN 04-1234-56</div>
      </div>
    '''
    return _showcase("Address Block", body, ["textsizes/card_title_size", "colors/near_black"])

def render_owner_row():
    body = f'''
      <div class="owner-row">
        <div class="owner-avatar">JD</div>
        <div class="owner-body">
          <div class="owner-name">Jane Doe</div>
          <div class="owner-meta">Owner since 2003 · 22 yrs tenure</div>
        </div>
        <button class="owner-call" aria-label="Call">{icon("phone", 16)}</button>
      </div>
    '''
    return _showcase("Owner Info Row", body, ["colors/neutral_200", "textsizes/body_txt_size"])

def render_financials_row():
    body = '''
      <div class="fin-row">
        <div class="fin-cell"><div class="fin-label">ARV</div><div class="fin-value">$385k</div></div>
        <div class="fin-cell"><div class="fin-label">Equity</div><div class="fin-value">$210k</div></div>
        <div class="fin-cell fin-warn"><div class="fin-label">Tax</div><div class="fin-value">Lien</div></div>
      </div>
    '''
    return _showcase("Financials Row", body, ["colors/near_black", "colors/yellow"])


# ---- Foundation renderers (Pass 2) ----

def render_button():
    body = '''
      <div class="btn-grid">
        <div class="btn-row">
          <button class="btn btn-primary btn-m">Primary</button>
          <button class="btn btn-secondary btn-m">Secondary</button>
          <button class="btn btn-tertiary btn-m">Tertiary</button>
          <button class="btn btn-ghost btn-m">Ghost</button>
          <button class="btn btn-destructive btn-m">Destructive</button>
        </div>
        <div class="btn-row">
          <button class="btn btn-primary btn-s">Small</button>
          <button class="btn btn-primary btn-m">Medium</button>
          <button class="btn btn-primary btn-l">Large</button>
        </div>
        <div class="btn-row">
          <button class="btn btn-primary btn-m"><span class="btn-ico">＋</span>With icon</button>
          <button class="btn btn-primary btn-m" disabled>Disabled</button>
          <button class="btn btn-primary btn-m btn-loading"><span class="btn-spin"></span>Loading</button>
        </div>
      </div>
    '''
    return _showcase("Button", body, ["components/primarybutton_bg_active", "cornerradius/radius_md", "textsizes/button_txt_size"])

def render_icon_button():
    body = f'''
      <div class="icobtn-row">
        <button class="ico-btn ico-btn-m" aria-label="Camera">{icon("camera", 18)}</button>
        <button class="ico-btn ico-btn-m ico-btn-primary" aria-label="Send">{icon("send", 16)}</button>
        <button class="ico-btn ico-btn-l" aria-label="More">{icon("more", 20)}</button>
        <button class="ico-btn ico-btn-l ico-btn-primary" aria-label="Add">{icon("plus", 20)}</button>
        <button class="ico-btn ico-btn-m" disabled aria-label="Close">{icon("close", 16)}</button>
      </div>
    '''
    return _showcase("Icon Button", body, ["components/secondarybutton_bg_active", "cornerradius/radius_pill"])

def render_text_field():
    body = '''
      <div class="tf-stack">
        <label class="tf">
          <span class="tf-label">Address</span>
          <input class="tf-input" value="123 Main St" />
        </label>
        <label class="tf tf-error">
          <span class="tf-label">Owner phone</span>
          <input class="tf-input" value="(555) 12" />
          <span class="tf-hint">Doesn't look complete.</span>
        </label>
        <label class="tf">
          <span class="tf-label">Notes</span>
          <textarea class="tf-input tf-multi" rows="3" placeholder="Anything to jot down?"></textarea>
        </label>
      </div>
    '''
    return _showcase("Text Field", body, ["strokes/outline_regular", "colors/near_black", "cornerradius/radius_md"])

def render_chip_taxonomy():
    body = f'''
      <div class="chip-grid">
        <div class="chip-row">
          <span class="chip-label">agent-suggested</span>
          <span class="chip chip-suggested"><i>{icon("distress", 13)}</i>overgrown lawn<b class="chip-ico">{icon("plus", 10)}</b></span>
          <span class="chip chip-suggested"><i>{icon("legal", 13)}</i>tax lien<b class="chip-ico">{icon("plus", 10)}</b></span>
        </div>
        <div class="chip-row">
          <span class="chip-label">user-confirmed</span>
          <span class="chip chip-confirmed"><i>{icon("distress", 13)}</i>roof damage<b class="chip-ico">{icon("check", 10)}</b></span>
          <span class="chip chip-confirmed"><i>{icon("vacancy", 13)}</i>vacancy signs<b class="chip-ico">{icon("check", 10)}</b></span>
        </div>
        <div class="chip-row">
          <span class="chip-label">user-added</span>
          <span class="chip chip-added"><i>{icon("owner", 13)}</i>elderly owner<b class="chip-ico">{icon("close", 10)}</b></span>
        </div>
        <div class="chip-row">
          <span class="chip-label">system-locked</span>
          <span class="chip chip-locked"><i>{icon("legal", 13)}</i>foreclosure notice<b class="chip-ico">{icon("lock", 11)}</b></span>
        </div>
      </div>
    '''
    return _showcase("Tag / Chip", body, ["colors/red_600", "colors/neutral_200", "strokes/outline_light"])

def render_toggle():
    body = '''
      <div class="tog-row">
        <label class="tog"><input type="checkbox" checked /><span class="tog-slider"></span><span class="tog-label">On</span></label>
        <label class="tog"><input type="checkbox" /><span class="tog-slider"></span><span class="tog-label">Off</span></label>
      </div>
    '''
    return _showcase("Toggle Switch", body, ["colors/red_600", "colors/neutral_200"])

def render_checkbox():
    body = '''
      <div class="chk-stack">
        <label class="chk"><input type="checkbox" checked /><span class="chk-box"></span>Confirmed</label>
        <label class="chk"><input type="checkbox" /><span class="chk-box"></span>Unchecked</label>
        <label class="chk"><input type="checkbox" checked disabled /><span class="chk-box"></span>Disabled</label>
      </div>
    '''
    return _showcase("Checkbox", body, ["colors/red_600", "cornerradius/radius_sm"])

def render_radio():
    body = '''
      <div class="chk-stack">
        <label class="chk chk-radio"><input type="radio" name="r-demo" checked /><span class="chk-box"></span>Cash offer</label>
        <label class="chk chk-radio"><input type="radio" name="r-demo" /><span class="chk-box"></span>Rental buyout</label>
        <label class="chk chk-radio"><input type="radio" name="r-demo" /><span class="chk-box"></span>Wholesale flip</label>
      </div>
    '''
    return _showcase("Radio", body, ["colors/red_600", "cornerradius/radius_pill"])

def render_segmented():
    body = '''
      <div class="seg-demo">
        <div class="seg"><button class="seg-btn active">Compact</button><button class="seg-btn">Expanded</button></div>
        <div class="seg"><button class="seg-btn active">Portrait</button><button class="seg-btn">Landscape</button></div>
      </div>
    '''
    return _showcase("Segmented Control", body, ["colors/red_600", "cornerradius/radius_pill"])

def render_avatar():
    body = '''
      <div class="avatar-row">
        <span class="avatar avatar-s">JD</span>
        <span class="avatar avatar-m">JD</span>
        <span class="avatar avatar-l">JD</span>
        <span class="avatar avatar-m avatar-agent">AI</span>
      </div>
    '''
    return _showcase("Avatar", body, ["colors/neutral_200", "colors/red_600"])

def render_divider():
    body = '''
      <div class="div-stack">
        <div>Section A</div>
        <hr class="divider" />
        <div>Section B</div>
        <hr class="divider divider-heavy" />
        <div>Section C</div>
      </div>
    '''
    return _showcase("Divider", body, ["strokes/outline_light", "strokes/outline_regular"])

def render_search_bar():
    body = f'''
      <div class="search-row">
        <label class="search-bar">
          <span class="search-ico">{icon("search", 16)}</span>
          <input type="search" placeholder="Search by name, phone…" />
        </label>
        <button class="sort-chip" aria-label="Sort">
          {icon("sort", 14)}<span>Sort by</span>
        </button>
      </div>
      <p class="lib-note">Search + sort pair. Used at the top of list views (Secured leads, campaigns, history).</p>
    '''
    return _showcase("Search Bar + Sort", body, ["colors/neutral_100", "strokes/outline_light", "cornerradius/radius_pill"])

def render_sort_chip():
    body = f'''
      <div class="chip-row-inline">
        <button class="sort-chip">{icon("sort", 14)}<span>Sort by</span></button>
        <button class="sort-chip">{icon("filter", 14)}<span>Filter</span></button>
        <button class="sort-chip sort-chip-active">{icon("sort", 14)}<span>Newest first</span></button>
      </div>
    '''
    return _showcase("Sort / Filter Chip", body, ["colors/neutral_100", "cornerradius/radius_pill", "colors/red_600"])


# ---- Property surface renderers (Pass 2) ----

def render_property_compact():
    body = f'''
      <div class="pcard pcard-compact">
        <div class="grade-ring grade-ring-m" data-grade="A"><span>A</span></div>
        <div class="pcard-body">
          <div class="pcard-addr">123 Main St</div>
          <div class="pcard-sub">Austin, TX · 0.2 mi</div>
        </div>
        <div class="pcard-icons">
          <span class="pcat">{icon("distress", 14)}</span>
          <span class="pcat">{icon("legal", 14)}</span>
        </div>
      </div>
    '''
    return _showcase("Property Card — Compact", body, ["gradecolors/grade_a", "textsizes/card_title_size"])

def render_property_expanded():
    body = '''
      <div class="pcard pcard-expanded">
        <div class="pcard-head">
          <div class="grade-ring grade-ring-l" data-grade="A"><span>A</span></div>
          <div>
            <div class="pcard-addr">123 Main St</div>
            <div class="pcard-sub">Austin, TX 78701</div>
          </div>
        </div>

        <div class="pimg-carousel">
          <div class="pimg pimg-sat">Satellite view</div>
          <div class="pimg-dots"><span class="active"></span><span></span></div>
        </div>

        <div class="pcard-section">
          <div class="pcard-section-label">Suggested tags</div>
          <div class="chip-row-inline">
            <span class="chip chip-suggested chip-sm"><i>''' + icon("distress", 12) + '''</i>overgrown lawn<b class="chip-ico">''' + icon("plus", 9) + '''</b></span>
            <span class="chip chip-suggested chip-sm"><i>''' + icon("distress", 12) + '''</i>roof damage<b class="chip-ico">''' + icon("plus", 9) + '''</b></span>
            <span class="chip chip-suggested chip-sm"><i>''' + icon("legal", 12) + '''</i>tax lien<b class="chip-ico">''' + icon("plus", 9) + '''</b></span>
          </div>
        </div>

        <div class="pcard-section">
          <div class="pcard-section-label">Campaign fit</div>
          <div class="camp-mini">
            <div>
              <div class="camp-name">Cash-offer campaign</div>
              <div class="camp-reason">High equity, long tenure — solid fit.</div>
            </div>
            <button class="camp-swap">Swap</button>
          </div>
        </div>

        <div class="pcard-actions">
          <button class="btn btn-primary btn-m btn-block">Add as lead</button>
          <button class="btn btn-ghost btn-m">Dismiss</button>
        </div>

        <button class="pcard-details">Show details ''' + icon("chevron_down", 12) + '''</button>
      </div>
    '''
    return _showcase("Property Card — Expanded (Decision)", body, ["gradecolors/grade_a", "components/primarybutton_bg_active", "cornerradius/radius_lg"])

def render_property_hero():
    """
    Vertical hero variant. Large photo with grade-pill overlay (top-left)
    and bookmark save (top-right); title + est. value row; distress-signal
    tagline; three stats with icons. Used on the property-detail screen
    and in featured/curated lists.
    """
    body = f'''
      <article class="pfeat" tabindex="0"
               aria-label="1247 Elm St, Austin TX. Grade A prime lead. Est. value $182,000.">
        <div class="pfeat-media">
          <img
            src="https://images.unsplash.com/photo-1568605114967-8130f3a36994?auto=format&fit=crop&w=800&h=560&q=70"
            alt="Two-story home with covered porch"
            loading="lazy"
            onerror="this.parentElement.classList.add('pfeat-media-fallback');this.remove()">
          <span class="pfeat-pill" data-grade="A">
            <span class="pfeat-pill-dot">A</span>Prime Lead
          </span>
          <button class="pfeat-save" aria-pressed="false" aria-label="Save as lead"
                  onclick="this.setAttribute('aria-pressed', this.getAttribute('aria-pressed')==='true'?'false':'true')">
            {icon("secured", 18)}
          </button>
        </div>
        <div class="pfeat-body">
          <div class="pfeat-title-row">
            <h4 class="pfeat-title">1247 Elm St</h4>
            <div class="pfeat-price">$182k<span class="pfeat-unit">/ARV</span></div>
          </div>
          <p class="pfeat-tag">Overgrown, roof looks rough, tax lien on file.</p>
        </div>
        <div class="pfeat-stats">
          <div class="pfeat-stat">
            <span class="pfeat-stat-ico">{icon("bed", 16)}</span>
            Bed: <b>3</b>
          </div>
          <div class="pfeat-stat">
            <span class="pfeat-stat-ico">{icon("bath", 16)}</span>
            Baths: <b>2</b>
          </div>
          <div class="pfeat-stat">
            <span class="pfeat-stat-ico">{icon("ruler", 16)}</span>
            Sqft: <b>1,410</b>
          </div>
        </div>
      </article>
    '''
    return _showcase(
        "Property Card — Hero",
        body,
        ["gradecolors/grade_a", "components/primarybutton_bg_active",
         "cornerradius/radius_2xl", "textsizes/card_title_size"],
    )

def render_property_lead():
    """
    Horizontal lead-row variant. Small square photo, brand-color est. value,
    full-address title, stats row with dividers, owner-name + phone footer,
    chevron for detail navigation. Used in list views (Today's Drive,
    Saved Leads, Search results).
    """
    def _row(price, address, bds, ba, sqft, owner, phone, img_url, img_alt):
        phone_html = (
            f'<a class="plead-owner-phone" href="tel:{esc(phone.replace(" ", ""))}">{esc(phone)}</a>'
            if phone else
            '<span class="plead-owner-phone">No phone on file</span>'
        )
        return f'''
      <article class="plead" tabindex="0"
               aria-label="{esc(address)}. Est. value {esc(price)}.">
        <div class="plead-media">
          <img src="{esc(img_url)}" alt="{esc(img_alt)}" loading="lazy"
               onerror="this.parentElement.classList.add('plead-media-fallback');this.remove()">
        </div>
        <div class="plead-body">
          <div class="plead-price-row">
            <span class="plead-price">{esc(price)}</span>
            <span class="plead-price-label">Est. Value</span>
          </div>
          <h4 class="plead-address">{esc(address)}</h4>
          <div class="plead-stats">
            <span class="stat"><span class="stat-value">{esc(bds)}</span> Bds</span>
            <span class="plead-divider"></span>
            <span class="stat"><span class="stat-value">{esc(ba)}</span> Ba</span>
            <span class="plead-divider"></span>
            <span class="stat"><span class="stat-value">{esc(sqft)}</span> sqft</span>
          </div>
          <div class="plead-owner">
            <span class="plead-owner-label">Owned By:</span>
            <span class="plead-owner-name">{esc(owner)}</span>
            {phone_html}
          </div>
        </div>
        <span class="plead-chevron" aria-hidden="true">{icon("chevron_right", 18)}</span>
      </article>
    '''
    # Unsplash source URLs — cropped square, ~300px, fall back to
    # neutral gradient if offline (see .plead-media-fallback).
    img1 = "https://images.unsplash.com/photo-1568605114967-8130f3a36994?auto=format&fit=crop&w=400&h=400&q=70"
    img2 = "https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&w=400&h=400&q=70"
    img3 = "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=400&h=400&q=70"
    body = (
        _row("$1,164,000", "2720 Black Cherry OFallon, MO 63368",
             "3", "4", "3,123", "Ann B Hadley", "(669) 878 9978",
             img1, "Two-story home with covered porch")
        + _row("$412,000", "88 Cypress Ave Austin, TX 78702",
             "2", "1", "980", "Marcus Vela", "(512) 555 0142",
             img2, "Small bungalow with peeling paint")
        + _row("$675,500", "502 Riverside Dr Miami, FL 33101",
             "4", "2", "1,820", "R. Okafor", "",
             img3, "Older single-story home")
    )
    return _showcase(
        "Property Card — Lead Row",
        body,
        ["components/primarybutton_bg_active", "cornerradius/radius_2xl",
         "textsizes/card_title_size", "colors/neutral_600"],
        wide=True,
    )

def render_imagery_carousel():
    body = '''
      <div class="pimg-carousel pimg-lg">
        <div class="pimg pimg-sat">
          <div class="pimg-label">Satellite</div>
        </div>
        <div class="pimg-dots"><span class="active"></span><span></span><span></span></div>
      </div>
      <p class="lib-note">Swipe between satellite view and distress-area shots. Agent auto-cycles while narrating.</p>
    '''
    return _showcase("Imagery Carousel", body, ["cornerradius/radius_lg", "colors/near_black"])

def render_tag_suggestion_row():
    body = f'''
      <div class="chip-row-inline">
        <span class="chip chip-suggested chip-sm"><i>{icon("distress", 12)}</i>overgrown lawn<b class="chip-ico">{icon("plus", 9)}</b></span>
        <span class="chip chip-suggested chip-sm"><i>{icon("distress", 12)}</i>peeling paint<b class="chip-ico">{icon("plus", 9)}</b></span>
        <span class="chip chip-suggested chip-sm"><i>{icon("vacancy", 12)}</i>overflowing mail<b class="chip-ico">{icon("plus", 9)}</b></span>
        <span class="chip chip-suggested chip-sm"><i>{icon("legal", 12)}</i>tax lien<b class="chip-ico">{icon("plus", 9)}</b></span>
      </div>
      <p class="lib-note">Say "yes" to accept all, or name exceptions ("skip the tax lien").</p>
    '''
    return _showcase("Tag Suggestion Row", body, ["strokes/outline_regular", "colors/red_600"])

def render_note_composer():
    body = f'''
      <div class="note-composer">
        <div class="note-prompt">Anything to jot down?</div>
        <div class="note-input">
          <input placeholder="Speak or type…" />
          <button class="ico-btn ico-btn-m ico-btn-primary" aria-label="Dictate">{icon("mic", 16)}</button>
        </div>
      </div>
    '''
    return _showcase("Note Composer", body, ["colors/near_black", "components/primarybutton_bg_active"])

def render_campaign_suggestion():
    body = f'''
      <div class="camp-card">
        <div class="camp-head">
          <div class="camp-icon">{icon("mail", 22)}</div>
          <div>
            <div class="camp-name">Cash-offer campaign</div>
            <div class="camp-reason">This one's a fit — high equity, long tenure.</div>
          </div>
        </div>
        <div class="camp-actions">
          <button class="btn btn-primary btn-s">Add</button>
          <button class="btn btn-secondary btn-s">Swap</button>
          <button class="btn btn-ghost btn-s">Skip</button>
        </div>
      </div>
    '''
    return _showcase("Campaign Suggestion Card", body, ["components/primarybutton_bg_active", "cornerradius/radius_md"])

def render_lead_added():
    body = f'''
      <div class="lead-added">
        <div class="lead-check">{icon("check", 16)}</div>
        <div class="lead-body">
          <div class="lead-title">Got it — added.</div>
          <div class="lead-sub">Next one's a couple minutes up the road.</div>
        </div>
      </div>
    '''
    return _showcase("Lead-Added Confirmation", body, ["colors/green", "colors/near_black"])

def render_route_card():
    body = f'''
      <div class="route-card">
        <div class="route-map">
          <svg viewBox="0 0 320 200" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
            <rect width="320" height="200" fill="var(--panel-2, #F5F1EA)"/>
            <path d="M 0 0 L 100 0 L 70 70 L 0 90 Z" fill="var(--colors-neutral_100, #EDEBE6)" opacity=".7"/>
            <path d="M 230 150 L 320 130 L 320 200 L 210 200 Z" fill="var(--colors-neutral_100, #EDEBE6)" opacity=".9"/>
            <path d="M 20 70 C 100 90, 180 40, 310 80" stroke="#fff" stroke-width="6" fill="none"/>
            <path d="M 40 180 C 120 160, 200 200, 300 170" stroke="#fff" stroke-width="6" fill="none"/>
            <path d="M 70 20 L 90 195" stroke="#fff" stroke-width="4" fill="none"/>
            <path d="M 200 10 L 180 200" stroke="#fff" stroke-width="4" fill="none"/>
            <path d="M 40 155 C 80 135, 100 115, 140 95 S 220 120, 258 62" stroke="var(--colors-primarybutton_bg_active, #D93131)" stroke-width="3" stroke-linecap="round" stroke-dasharray="1 6" fill="none"/>
            <circle cx="40" cy="155" r="8" fill="var(--colors-primarybutton_bg_active, #D93131)"/><circle cx="40" cy="155" r="3" fill="#fff"/>
            <circle cx="90" cy="125" r="8" fill="#fff"/><circle cx="90" cy="125" r="5" fill="var(--gradecolors-grade_a, #1A7F42)"/>
            <circle cx="140" cy="95" r="8" fill="#fff"/><circle cx="140" cy="95" r="5" fill="var(--gradecolors-grade_a, #1A7F42)"/>
            <circle cx="195" cy="108" r="8" fill="#fff"/><circle cx="195" cy="108" r="5" fill="var(--gradecolors-grade_b, #E8A317)"/>
            <circle cx="230" cy="88" r="8" fill="#fff"/><circle cx="230" cy="88" r="5" fill="var(--gradecolors-grade_c, #D93025)"/>
            <path d="M 258 50 C 251 50, 246 55, 246 62 C 246 72, 258 84, 258 84 C 258 84, 270 72, 270 62 C 270 55, 265 50, 258 50 Z" fill="var(--colors-primarybutton_bg_active, #D93131)"/><circle cx="258" cy="62" r="3" fill="#fff"/>
          </svg>
        </div>
        <div class="route-info">
          <div class="route-info-head">{icon("pin", 12)}<span>Route area</span></div>
          <div class="route-info-title">78701 · East Austin loop</div>
          <div class="route-info-meta"><span>12 properties</span><span class="route-info-dot"></span><span>4.2 mi</span></div>
        </div>
      </div>
      <p class="lib-note">Rendered inline in the "start-drive" conversation after the agent finishes planning. Reused in the drive → inspection handoff.</p>
    '''
    return _showcase("Route Card", body, ["colors/panel", "gradecolors/grade_a", "components/primarybutton_bg_active"])

def render_action_rail():
    body = f'''
      <div class="rail-stage">
        <div class="rail-fake">Property review view</div>
        <div class="action-rail">
          <button class="ico-btn ico-btn-l" aria-label="Camera" title="Tap or say 'open camera'">{icon("camera", 20)}</button>
        </div>
      </div>
      <p class="lib-note">Persistent camera during a stop. Tap or voice: "open camera". More persistent actions dock here in later passes.</p>
    '''
    return _showcase("Persistent Action Rail", body, ["cornerradius/radius_pill", "components/secondarybutton_bg_active"])

# ---- Listing (Route + Secured screens) ----

def render_listing_header():
    body = f'''
      <div class="lib-listing-stage">
        <div class="listing-title-row">
          <div>
            <div class="listing-title">Today's Route</div>
            <div class="listing-sub">Zip 78701 · Oak Valley loop</div>
          </div>
          <button class="ico-btn ico-btn-m" aria-label="Filter route">{icon("filter", 16)}</button>
        </div>
      </div>
      <p class="lib-note">Title + subtitle + filter action. Used at the top of Route and Secured listing screens.</p>
    '''
    return _showcase("Listing Header", body, ["textsizes/screen_title_size", "colors/text", "colors/text_dim"])

def render_listing_summary():
    body = f'''
      <div class="lib-listing-stage">
        <div class="listing-summary">
          <div class="listing-summary-item"><div class="listing-summary-num">6</div><div class="listing-summary-label">stops</div></div>
          <div class="listing-summary-item"><div class="listing-summary-num">4.2</div><div class="listing-summary-label">miles</div></div>
          <div class="listing-summary-item"><div class="listing-summary-num">1h 40m</div><div class="listing-summary-label">est.</div></div>
          <div class="listing-summary-item"><div class="listing-summary-num">3–5</div><div class="listing-summary-label">leads</div></div>
        </div>
      </div>
      <p class="lib-note">4-column stat strip. Sits under listing headers to give the driver a glanceable summary.</p>
    '''
    return _showcase("Listing Summary Strip", body, ["colors/panel", "cornerradius/radius_lg", "strokes/outline_light"])

def render_listing_row_stop():
    body = f'''
      <div class="lib-listing-stage">
        <div class="listing-list">
          <div class="listing-row">
            <div class="listing-row-index">1</div>
            <div class="prop-row-thumb" aria-hidden="true" style="background-image:url('https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=120&h=120&fit=crop&q=80')"></div>
            <div class="prop-row-body">
              <div class="prop-row-addr-row">
                <span class="prop-row-addr">312 Trinity St</span>
                <span class="pcard-grade-badge" data-grade="A">A</span>
              </div>
              <div class="prop-row-meta">0.2 mi · 1st · 2 min</div>
            </div>
            <i class="ph-bold ph-caret-right prop-row-chev" style="font-size:14px;line-height:1"></i>
          </div>
          <div class="listing-row">
            <div class="listing-row-index">2</div>
            <div class="prop-row-thumb" aria-hidden="true" style="background-image:url('https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=120&h=120&fit=crop&q=80')"></div>
            <div class="prop-row-body">
              <div class="prop-row-addr-row">
                <span class="prop-row-addr">514 Red River St</span>
                <span class="pcard-grade-badge" data-grade="A">A</span>
              </div>
              <div class="prop-row-meta">0.4 mi · 2nd · 5 min</div>
            </div>
            <i class="ph-bold ph-caret-right prop-row-chev" style="font-size:14px;line-height:1"></i>
          </div>
        </div>
      </div>
      <p class="lib-note">Numbered route row. Position badge + thumb + address + grade + distance/ETA meta.</p>
    '''
    return _showcase("Listing Row · Route Stop", body, ["colors/panel", "components/primarybutton_bg_active", "gradecolors/grade_a"], wide=True)

def render_listing_row_lead():
    body = f'''
      <div class="lib-listing-stage">
        <div class="listing-list">
          <div class="listing-row">
            <div class="prop-row-thumb listing-row-thumb-sq" aria-hidden="true" style="background-image:url('https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=120&h=120&fit=crop&q=80')"></div>
            <div class="prop-row-body">
              <div class="prop-row-addr-row">
                <span class="prop-row-addr">123 Main St</span>
                <span class="pcard-grade-badge" data-grade="A">A</span>
                <span class="listing-row-badge">Latest</span>
              </div>
              <div class="prop-row-meta">Austin, TX 78701</div>
              <div class="listing-row-foot">
                <span class="listing-row-chip">Cash-offer</span>
                <span class="listing-row-time">Sep 12 · 2:14 pm</span>
              </div>
            </div>
            <i class="ph-bold ph-caret-right prop-row-chev" style="font-size:14px;line-height:1"></i>
          </div>
        </div>
      </div>
      <p class="lib-note">Secured lead row. Square thumb + address + grade + optional "Latest" badge + campaign chip + secured-time.</p>
    '''
    return _showcase("Listing Row · Secured Lead", body, ["colors/panel", "gradecolors/grade_a", "cornerradius/radius_pill"], wide=True)


# ---- Property Details (single-lead detail page) ----

def render_details_hero():
    body = f'''
      <div class="lib-details-stage">
        <div class="details-carousel" data-carousel>
          <div class="details-carousel-track" data-carousel-track>
            <div class="details-carousel-slide"><div class="pimg pimg-photo" style="background-image:url('https://images.unsplash.com/photo-1568605114967-8130f3a36994?auto=format&fit=crop&w=1000&q=80')"></div></div>
            <div class="details-carousel-slide"><div class="pimg pimg-photo" style="background-image:url('https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&w=1000&q=80')"></div></div>
            <div class="details-carousel-slide"><div class="pimg pimg-photo" style="background-image:url('https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1000&q=80')"></div></div>
            <div class="details-carousel-slide"><div class="pimg pimg-photo" style="background-image:url('https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1000&q=80')"></div></div>
            <div class="details-carousel-slide"><div class="pimg pimg-photo" style="background-image:url('https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=1000&q=80')"></div></div>
            <div class="details-carousel-slide"><div class="pimg pimg-photo" style="background-image:url('https://images.unsplash.com/photo-1502005229762-cf1b2da7c5d6?auto=format&fit=crop&w=1000&q=80')"></div></div>
          </div>
          <button class="details-carousel-btn details-carousel-prev" type="button" aria-label="Previous image" data-carousel-prev>{icon("chevron_back", 14)}</button>
          <button class="details-carousel-btn details-carousel-next" type="button" aria-label="Next image" data-carousel-next>{icon("chevron_right", 14)}</button>
          <div class="details-carousel-count" data-carousel-count>1 / 6</div>
          <div class="details-hero-dots" data-carousel-dots>
            <span class="active" data-carousel-dot="0"></span>
            <span data-carousel-dot="1"></span>
            <span data-carousel-dot="2"></span>
            <span data-carousel-dot="3"></span>
            <span data-carousel-dot="4"></span>
            <span data-carousel-dot="5"></span>
          </div>
        </div>
      </div>
      <p class="lib-note">Swipeable image carousel with grade-badge overlay, page counter, prev/next controls and dot indicators. Top of the Property Details page. Uses native scroll-snap for swipe on touch devices.</p>
    '''
    return _showcase("Details Image Carousel", body, ["gradecolors/grade_a", "cornerradius/radius_lg", "colors/panel_2"])

def render_stat_strip():
    body = f'''
      <div class="lib-details-stage">
        <div class="details-stats">
          <div class="dstat-money-row">
            <div class="dstat-money">
              <div class="dstat-money-label">Est. price</div>
              <div class="dstat-money-num">$180k</div>
            </div>
            <div class="dstat-money-divider" aria-hidden="true"></div>
            <div class="dstat-money">
              <div class="dstat-money-label">ARV</div>
              <div class="dstat-money-value">
                <div class="dstat-money-num">$275k</div>
                <div class="dstat-money-delta"><i class="ph-bold ph-trend-up" style="font-size:9px;line-height:1"></i>+$95k</div>
              </div>
            </div>
          </div>
          <div class="dstat-specs">
            <div class="dspec"><i class="ph-bold ph-bed" style="font-size:14px;line-height:1"></i><span><b>3</b> bd</span></div>
            <div class="dspec"><i class="ph-bold ph-bathtub" style="font-size:14px;line-height:1"></i><span><b>2</b> ba</span></div>
            <div class="dspec"><i class="ph-bold ph-ruler" style="font-size:14px;line-height:1"></i><span><b>1,420</b> sqft</span></div>
          </div>
        </div>
      </div>
      <p class="lib-note">5-column mini stats: price · ARV · beds · baths · sqft. Sits under the details hero.</p>
    '''
    return _showcase("Property Stat Strip", body, ["colors/panel", "cornerradius/radius_lg", "textsizes/body_txt_size"])

def render_owner_details_card():
    body = f'''
      <div class="lib-details-stage">
        <div class="details-owner">
          <div class="details-owner-row">
            <span class="details-owner-ico">{icon("owner", 14)}</span>
            <div>
              <div class="details-owner-name">Alice Cordova</div>
              <div class="details-owner-meta">Owned 14 years · On-site</div>
            </div>
          </div>
          <div class="details-owner-row">
            <span class="details-owner-ico">{icon("phone", 14)}</span>
            <div class="details-owner-name">(512) 555-0182</div>
          </div>
        </div>
      </div>
      <p class="lib-note">Multi-row owner block with icons. Details page — differs from the compact Owner Info Row used in scouting.</p>
    '''
    return _showcase("Owner Details Card", body, ["colors/panel", "colors/text", "colors/text_dim"])

def render_note_card():
    body = f'''
      <div class="lib-details-stage">
        <div class="details-note">Dog in yard — approached from side gate. Owner mentioned she's considering selling within 6 months and wants a cash offer. Roof visibly worn on south side.</div>
      </div>
      <p class="lib-note">Read-only notes card. Displays a driver's saved notes on the Property Details page (Note Composer is the entry variant).</p>
    '''
    return _showcase("Driver Notes Card", body, ["colors/panel", "cornerradius/radius_lg", "textsizes/body_txt_size"])

def render_voice_memo_playback():
    wave_spans = "".join("<span></span>" for _ in range(20))
    body = f'''
      <div class="lib-details-stage">
        <div class="details-voice">
          <button class="details-voice-play" aria-label="Play memo">{icon("play", 14)}</button>
          <div class="details-voice-wave">{wave_spans}</div>
          <div class="details-voice-time">0:24</div>
        </div>
      </div>
      <p class="lib-note">Voice-memo playback card. Distinct from the live Waveform component: this is a saved recording with playback + duration.</p>
    '''
    return _showcase("Voice Memo Playback", body, ["colors/panel", "components/primarybutton_bg_active"])

def render_timeline():
    body = f'''
      <div class="lib-details-stage">
        <div class="details-timeline">
          <div class="dtl-row">
            <span class="dtl-dot"></span>
            <div class="dtl-body">
              <div class="dtl-title">Secured as lead</div>
              <div class="dtl-time">Sep 12 · 2:14 pm</div>
            </div>
          </div>
          <div class="dtl-row">
            <span class="dtl-dot"></span>
            <div class="dtl-body">
              <div class="dtl-title">Voice memo added</div>
              <div class="dtl-time">Sep 12 · 2:15 pm</div>
            </div>
          </div>
          <div class="dtl-row">
            <span class="dtl-dot"></span>
            <div class="dtl-body">
              <div class="dtl-title">Assigned to Cash-offer campaign</div>
              <div class="dtl-time">Sep 12 · 2:14 pm</div>
            </div>
          </div>
          <div class="dtl-row">
            <span class="dtl-dot"></span>
            <div class="dtl-body">
              <div class="dtl-title">Scouted by agent</div>
              <div class="dtl-time">Sep 12 · 9:02 am</div>
            </div>
          </div>
        </div>
      </div>
      <p class="lib-note">Vertical event timeline. Shows the history of a secured lead: scouted → assigned → secured → memo added.</p>
    '''
    return _showcase("Activity Timeline", body, ["colors/panel", "components/primarybutton_bg_active", "colors/text_dim"])

def render_details_tabs():
    body = f'''
      <div class="lib-details-stage">
        <div class="dtabs" data-dtabs>
          <div class="dtabs-bar" role="tablist">
            <button class="dtabs-btn active" type="button" role="tab" aria-selected="true" data-dtab="notes">Notes</button>
            <button class="dtabs-btn" type="button" role="tab" aria-selected="false" data-dtab="campaign">Campaign</button>
            <button class="dtabs-btn" type="button" role="tab" aria-selected="false" data-dtab="activity">Activity</button>
          </div>
          <div class="dtabs-panel active" data-dtab-panel="notes" role="tabpanel">
            <div class="dtabs-sub-label">Text note</div>
            <div class="details-note">Dog in yard — approached from side gate. Owner considering selling within 6 months.</div>
            <div class="dtabs-sub-label">Voice note</div>
            <div class="details-voice">
              <button class="details-voice-play" aria-label="Play memo">{icon("play", 14)}</button>
              <div class="details-voice-wave">{"<span></span>" * 20}</div>
              <div class="details-voice-time">0:24</div>
            </div>
          </div>
          <div class="dtabs-panel" data-dtab-panel="campaign" role="tabpanel" hidden>
            <div class="camp-mini"><div><div class="camp-name">Cash-offer campaign</div><div class="camp-reason">High equity, long tenure.</div></div><span class="listing-row-chip">Assigned</span></div>
          </div>
          <div class="dtabs-panel" data-dtab-panel="activity" role="tabpanel" hidden>
            <div class="details-timeline">
              <div class="dtl-row"><span class="dtl-dot"></span><div class="dtl-body"><div class="dtl-title">Secured as lead</div><div class="dtl-time">Sep 12 · 2:14 pm</div></div></div>
              <div class="dtl-row"><span class="dtl-dot"></span><div class="dtl-body"><div class="dtl-title">Scouted by agent</div><div class="dtl-time">Sep 12 · 9:02 am</div></div></div>
            </div>
          </div>
        </div>
      </div>
      <p class="lib-note">Tab switcher inside the Property Details page. Notes holds both the text note and the voice memo; Campaign shows the fit and offer; Activity shows the timeline. Segmented pill style — one tab visible at a time.</p>
    '''
    return _showcase("Details Tabs", body, ["colors/panel_2", "cornerradius/radius_pill", "colors/text"], wide=True)

def render_details_action_row():
    body = f'''
      <div class="lib-details-stage">
        <div class="details-actions">
          <button class="btn btn-primary btn-m">{icon("phone", 14)}<span>Call owner</span></button>
          <button class="btn btn-ghost btn-m">{icon("pin", 14)}<span>Open in maps</span></button>
        </div>
      </div>
      <p class="lib-note">Two-up action row at the bottom of the details page. Primary + ghost for hierarchy.</p>
    '''
    return _showcase("Details Action Row", body, ["components/primarybutton_bg_active", "cornerradius/radius_md"])

def render_bottom_nav():
    body = f'''
      <div class="lib-nav-stage">
        <nav class="home-nav" style="position:relative">
          <button class="home-nav-btn active" aria-label="Home">{icon("distress", 20)}<span>Home</span></button>
          <button class="home-nav-btn" aria-label="Route">{icon("pin", 20)}<span>Route</span></button>
          <div class="home-nav-orb-slot"></div>
          <button class="home-nav-btn" aria-label="Secured">{icon("secured", 20)}<span>Secured</span></button>
          <button class="home-nav-btn" aria-label="You">{icon("owner", 20)}<span>You</span></button>
          <button class="home-nav-orb" aria-label="Talk to agent">{icon("mic", 26)}</button>
        </nav>
      </div>
      <p class="lib-note">5-slot bottom nav with elevated voice orb in the center. Present on Home, Route, and Secured screens.</p>
    '''
    return _showcase("Bottom Nav", body, ["colors/panel", "components/primarybutton_bg_active", "cornerradius/radius_pill"], wide=True)


# ---- Framing renderers (Pass 3) ----

def render_bottom_sheet():
    body = '''
      <div class="frame-stage">
        <div class="frame-content">Drive view</div>
        <div class="sheet-backdrop"></div>
        <div class="bottom-sheet sheet-half">
          <div class="sheet-handle"></div>
          <div class="sheet-body">
            <div class="pcard-section-label">Next stop</div>
            <div class="pcard-addr" style="font-size:15px">123 Main St</div>
            <div class="pcard-sub">Austin, TX · 0.2 mi · Grade A</div>
          </div>
        </div>
        <div class="dock-orb dock-orb-right frame-orb">
          <div class="voice-orb" data-state="idle" style="width:44px;height:44px"><span class="orb-core"></span><span class="orb-ring"></span></div>
        </div>
      </div>
      <p class="lib-note">Peek / half / full snap points. Drag handle at top, backdrop dims content. Orb slides above the sheet.</p>
    '''
    return _showcase("Bottom Sheet", body, ["cornerradius/radius_lg", "colors/white", "spacing/spc_16"])

def render_modal():
    body = '''
      <div class="frame-stage">
        <div class="frame-content">Screen behind</div>
        <div class="sheet-backdrop"></div>
        <div class="modal">
          <div class="modal-head">
            <div class="modal-title">End drive?</div>
            <button class="modal-close" aria-label="Close">''' + icon("close", 14) + '''</button>
          </div>
          <div class="modal-body">
            You've added 7 leads today. We'll save everything before closing.
          </div>
          <div class="modal-foot">
            <button class="btn btn-ghost btn-s">Keep going</button>
            <button class="btn btn-primary btn-s">End drive</button>
          </div>
        </div>
      </div>
      <p class="lib-note">Centered, backdropped. Use sparingly — only for decisions that can't wait.</p>
    '''
    return _showcase("Modal", body, ["cornerradius/radius_lg", "components/primarybutton_bg_active"])

def render_toast():
    body = f'''
      <div class="toast-stack">
        <div class="toast toast-success"><span class="toast-ico">{icon("check", 12)}</span>Got it — added.</div>
        <div class="toast toast-info"><span class="toast-ico">{icon("info", 12)}</span>Rerouted — quieter street ahead.</div>
        <div class="toast toast-warning"><span class="toast-ico">{icon("warn", 12)}</span>Losing signal for a sec.</div>
        <div class="toast toast-error"><span class="toast-ico">{icon("close", 12)}</span>Missed that — say it again?</div>
      </div>
      <p class="lib-note">Auto-dismiss after ~4s. Uses natural copy — never "success" / "error" labels.</p>
    '''
    return _showcase("Toast", body, ["colors/green", "colors/blue", "colors/yellow", "colors/tomato_red"])

def render_safety_banner():
    body = '''
      <div class="frame-stage frame-stage-tall">
        <div class="safety-banner">
          <span class="safety-dot"></span>
          Driving — voice only right now.
        </div>
        <div class="frame-content" style="padding-top:36px">
          <div class="pcard pcard-compact" style="margin:16px">
            <div class="grade-ring grade-ring-m" data-grade="A"><span>A</span></div>
            <div class="pcard-body">
              <div class="pcard-addr">Approaching 123 Main St</div>
              <div class="pcard-sub">Say "tell me more" to hear the summary.</div>
            </div>
          </div>
        </div>
        <div class="dock-orb dock-orb-right frame-orb">
          <div class="voice-orb" data-state="listening" style="width:44px;height:44px"><span class="orb-core"></span><span class="orb-ring"></span></div>
        </div>
      </div>
      <p class="lib-note">Shown while GPS reports the car is in motion. Any tap-only affordances gray out; voice remains fully live.</p>
    '''
    return _showcase("Safety Banner", body, ["components/primarybutton_bg_active", "colors/white"])

def render_top_app_bar():
    body = f'''
      <div class="frame-stage frame-stage-short">
        <div class="app-bar">
          <button class="app-bar-back" aria-label="Back">{icon("back_arrow", 18)}</button>
          <div class="app-bar-title">Today's drive</div>
          <button class="ico-btn ico-btn-m app-bar-action" aria-label="More">{icon("more", 16)}</button>
        </div>
        <div class="frame-content" style="padding-top:56px">Screen body</div>
      </div>
      <div class="frame-stage frame-stage-short" style="margin-top:12px">
        <div class="app-bar">
          <div class="app-bar-title">Property review</div>
          <button class="ico-btn ico-btn-m app-bar-action" aria-label="Camera">{icon("camera", 16)}</button>
        </div>
        <div class="frame-content" style="padding-top:56px">Review body</div>
      </div>
    '''
    return _showcase("Top App Bar", body, ["colors/white", "textsizes/card_title_size", "strokes/outline_light"])


# ---- library assembly ----

LIB_SECTIONS = [
    ("voice", "Voice & Agent", [
        render_voice_orb,
        render_orb_dock,
        render_status_pill,
        render_waveform,
        render_ptt,
        render_transcript,
        render_nudge_banner,
        render_action_rail,
    ]),
    ("data",  "Data Display", [
        render_grade_ring,
        render_grade_badge,
        render_stat_tile,
        render_progress,
        render_address_block,
        render_owner_row,
        render_financials_row,
    ]),
    ("foundation", "Foundation", [
        render_button,
        render_icon_button,
        render_text_field,
        render_search_bar,
        render_sort_chip,
        render_chip_taxonomy,
        render_toggle,
        render_checkbox,
        render_radio,
        render_segmented,
        render_avatar,
        render_divider,
    ]),
    ("property",   "Property",   [
        render_property_compact,
        render_property_expanded,
        render_property_hero,
        render_route_card,
        render_imagery_carousel,
        render_tag_suggestion_row,
        render_note_composer,
        render_campaign_suggestion,
        render_lead_added,
        render_property_lead,
        render_details_hero,
        render_stat_strip,
        render_owner_details_card,
        render_details_tabs,
        render_note_card,
        render_voice_memo_playback,
        render_timeline,
    ]),
    ("listing",    "Listing",    [
        render_listing_header,
        render_listing_summary,
        render_listing_row_stop,
        render_listing_row_lead,
        render_details_action_row,
    ]),
    ("framing",    "Framing",    [
        render_top_app_bar,
        render_bottom_nav,
        render_bottom_sheet,
        render_modal,
        render_toast,
        render_safety_banner,
    ]),
]

def render_library():
    sub_btns = "".join(
        f'<button class="lib-tab{" active" if i==0 else ""}" data-lib-tab="{esc(pid)}">{esc(label)}</button>'
        for i, (pid, label, _) in enumerate(LIB_SECTIONS)
    )
    sub_panels = []
    for i, (pid, label, renderers) in enumerate(LIB_SECTIONS):
        if renderers:
            cards = "".join(r() for r in renderers)
            inner = f'<div class="lib-grid">{cards}</div>'
        else:
            inner = f'<div class="lib-empty">{esc(label)} components arrive in a later pass.</div>'
        sub_panels.append(
            f'<div class="lib-panel{" active" if i==0 else ""}" data-lib-tab="{esc(pid)}">'
            f'<h2 class="coll-title"><span>{esc(label)}</span><span class="count">{len(renderers)} components</span></h2>'
            f'{inner}</div>'
        )
    return f'<div class="lib-tabs">{sub_btns}</div>' + "".join(sub_panels)


# ---------- template ----------

TABS = [
    ("Primitive",  render_collection("Primitive")),
    ("Symantic",   render_collection("Symantic")),
    ("components", render_collection("components")),
]

tab_buttons = "".join(
    f'<button class="tab-btn{" active" if i==0 else ""}" data-tab="{esc(name)}">{esc(name)}</button>'
    for i, (name, _) in enumerate(TABS)
)
file_link = f'<div class="file">Figma file: <a href="https://www.figma.com/design/{esc(D["fileKey"])}/{esc(D["file"].replace(" ","-"))}?view=variables" style="color:var(--text-dim)">{esc(D["fileKey"])}</a></div>'
tab_panels = "".join(
    f'<div class="tab-panel{" active" if i==0 else ""}" data-tab="{esc(name)}">{body}</div>'
    for i, (name, body) in enumerate(TABS)
)

VARIABLES_PAGE = f'<div class="tabs">{tab_buttons}{file_link}</div><div class="tab-panels">{tab_panels}</div>'

LIBRARY_PAGE = render_library()

def _phone_frame(label, body, caption=""):
    """Wrap screen content in a mobile-device frame."""
    cap = f'<div class="phone-caption">{esc(caption)}</div>' if caption else ""
    return f'''
    <div class="phone-col">
      <div class="phone-label">{esc(label)}</div>
      <div class="phone">
        <div class="phone-notch"></div>
        <div class="phone-statusbar">
          <span>9:41</span>
          <span class="phone-signal"></span>
        </div>
        <div class="phone-screen">{body}</div>
      </div>
      {cap}
    </div>'''

def _mini_orb(state="idle"):
    return f'''
      <div class="dock-orb dock-orb-right frame-orb" style="bottom:16px;right:16px">
        <div class="voice-orb" data-state="{state}" style="width:48px;height:48px">
          <span class="orb-core"></span><span class="orb-ring"></span>
        </div>
      </div>'''

def screen_home():
    return _phone_frame(
        "1 · Home",
        f'''
          <div class="scr-home">
            <div class="scr-head">
              <div>
                <div class="scr-hi">Morning, Joe</div>
                <div class="scr-date">Fri · Sep 12</div>
              </div>
              <div class="avatar avatar-m">GU</div>
            </div>

            <div class="stat-row" style="margin-top:16px">
              <div class="stat-tile"><div class="stat-num">12</div><div class="stat-label">Leads today</div></div>
              <div class="stat-tile"><div class="stat-num">B+</div><div class="stat-label">Avg grade</div></div>
              <div class="stat-tile"><div class="stat-num">5<span class="stat-sub">day</span></div><div class="stat-label">Streak</div></div>
            </div>

            <div class="agent-brief">
              <div class="agent-brief-head">
                <div class="avatar avatar-s avatar-agent">AI</div>
                <div class="scr-hi" style="font-size:14px">Here's what I found</div>
              </div>
              <div class="agent-brief-body">
                Scouted <b>24 properties</b> in 78701 overnight. <b>8 grade A</b>, 6 grade B. Best cluster is around East Cesar Chavez — mostly aging homes with tax activity.
              </div>
              <div class="grade-mini-row">
                <span class="grade-badge grade-a"><b>A</b>8</span>
                <span class="grade-badge grade-b"><b>B</b>6</span>
                <span class="grade-badge grade-c"><b>C</b>7</span>
                <span class="grade-badge grade-d"><b>D</b>3</span>
              </div>
            </div>

            <button class="btn btn-primary btn-l scr-cta">{icon("arrow_right", 18)}Start drive</button>
          </div>
          {_mini_orb("idle")}
        ''',
        "Landing after login. Ambient orb docked bottom-right. Big Start CTA."
    )

def screen_start_conversation():
    return _phone_frame(
        "2 · Start-drive conversation",
        f'''
          <div class="scr-convo">
            <div class="app-bar" style="position:relative;height:auto;padding:14px 16px">
              <button class="app-bar-back" aria-label="Back">{icon("back_arrow", 18)}</button>
              <div class="app-bar-title">Planning today's route</div>
            </div>
            <div class="convo-stack">
              <div class="bubble bubble-agent">Morning. I've got 24 in your zip. How much time do you have?</div>
              <div class="bubble bubble-driver">About two hours.</div>
              <div class="bubble bubble-agent">Cool. Any area you want to stay in?</div>
              <div class="bubble bubble-driver">East side, quieter streets.</div>
              <div class="bubble bubble-agent">Got it. I'll thread 14 stops — mostly Grade A and B, staying east of I-35. Sound good?</div>
            </div>
            <div class="convo-cta">
              <button class="btn btn-ghost btn-m">Tweak it</button>
              <button class="btn btn-primary btn-m btn-block">Let's go</button>
            </div>
          </div>
          {_mini_orb("listening")}
        ''',
        "Agent proposes; driver adjusts by voice or tap. No forms."
    )

def screen_in_drive():
    return _phone_frame(
        "3 · In-drive · approaching",
        f'''
          <div class="scr-drive">
            <div class="safety-banner">
              <span class="safety-dot"></span>Driving — voice only right now.
            </div>
            <div class="scr-map">
              <div class="map-tile"></div>
              <div class="map-pin map-pin-a" style="top:30%;left:35%">A</div>
              <div class="map-pin map-pin-a" style="top:52%;left:60%">A</div>
              <div class="map-pin map-pin-b" style="top:66%;left:28%">B</div>
              <div class="map-pin map-pin-c" style="top:22%;left:70%">C</div>
              <div class="map-you"></div>
            </div>

            <div class="nudge-banner nudge-inline">
              <span class="nudge-icon">{icon("pin", 18)}</span>
              <div class="nudge-body">
                <div class="nudge-title">Approaching 123 Main St</div>
                <div class="nudge-meta">Grade A · 0.2 mi · quieter street</div>
              </div>
            </div>

            <div class="drive-progress">
              <div class="progress-meta"><span>Route progress</span><span>3 / 14 stops</span></div>
              <div class="progress-bar"><div class="progress-fill" style="width:22%"></div></div>
            </div>
          </div>
          {_mini_orb("listening")}
        ''',
        "Safety banner locks tap input. Nudge banner appears on approach; agent narrates."
    )

def screen_property_stop():
    return _phone_frame(
        "4 · At the property · Decision Card",
        f'''
          <div class="scr-stop">
            <div class="app-bar" style="position:relative;height:auto;padding:12px 14px">
              <button class="app-bar-back" aria-label="Back">{icon("back_arrow", 18)}</button>
              <div class="app-bar-title">123 Main St</div>
              <button class="ico-btn ico-btn-m app-bar-action" aria-label="Camera">{icon("camera", 16)}</button>
            </div>

            <div class="scr-stop-body">
              <div class="pcard pcard-expanded" style="border:0; padding:0; max-width:none">
                <div class="pcard-head">
                  <div class="grade-ring grade-ring-l" data-grade="A"><span>A</span></div>
                  <div>
                    <div class="pcard-addr">123 Main St</div>
                    <div class="pcard-sub">Austin, TX 78701</div>
                  </div>
                </div>

                <div class="pimg-carousel">
                  <div class="pimg pimg-sat"><div class="pimg-label">Satellite</div></div>
                  <div class="pimg-dots"><span class="active"></span><span></span><span></span></div>
                </div>

                <div class="pcard-section">
                  <div class="pcard-section-label">Suggested tags</div>
                  <div class="chip-row-inline">
                    <span class="chip chip-suggested chip-sm"><i>{icon("distress", 12)}</i>overgrown lawn<b class="chip-ico">{icon("plus", 9)}</b></span>
                    <span class="chip chip-suggested chip-sm"><i>{icon("distress", 12)}</i>roof damage<b class="chip-ico">{icon("plus", 9)}</b></span>
                    <span class="chip chip-suggested chip-sm"><i>{icon("legal", 12)}</i>tax lien<b class="chip-ico">{icon("plus", 9)}</b></span>
                  </div>
                </div>

                <div class="pcard-section">
                  <div class="pcard-section-label">Campaign fit</div>
                  <div class="camp-mini">
                    <div>
                      <div class="camp-name">Cash-offer campaign</div>
                      <div class="camp-reason">High equity, long tenure — solid fit.</div>
                    </div>
                    <button class="camp-swap">Swap</button>
                  </div>
                </div>

                <div class="pcard-actions">
                  <button class="btn btn-primary btn-m btn-block">Add as lead</button>
                  <button class="btn btn-ghost btn-m">Dismiss</button>
                </div>

                <button class="pcard-details">Show details {icon("chevron_down", 12)}</button>
              </div>
            </div>
          </div>
          {_mini_orb("speaking")}
        ''',
        "Decision Card. Agent narrates while these appear; driver says 'yes' or names exceptions."
    )

def _proto_screen(id_, body):
    return f'<div class="proto-screen" data-screen="{esc(id_)}">{body}</div>'

def _proto_screens():
    home = f'''
      <div class="scr-home">
        <div class="home-header">
          <div class="zip-pill">{icon("pin", 14)}<span>Zip · 78701</span></div>
          <h1 class="home-hi">Morning, <b>Joe</b> — welcome to your territory.</h1>
          <div class="home-callout">
            <div class="home-callout-num">10</div>
            <div class="home-callout-body">
              <div class="home-callout-title">new leads scouted</div>
              <div class="home-callout-sub">Ready when you are.</div>
            </div>
          </div>
          <div class="home-recap">
            <span class="recap-dot"></span>
            <span><b>3 leads</b> won last drive · 2 hrs</span>
          </div>
        </div>

        <div class="home-map">
          <div id="home-real-map"></div>
          <button type="button" class="map-zone-label" id="home-zone-chip" aria-expanded="false" aria-controls="home-properties-panel">Oak Valley · 6 properties</button>
        </div>

        <nav class="home-nav">
          <button class="home-nav-btn active" data-nav="home" aria-label="Home">{icon("distress", 20)}<span>Home</span></button>
          <button class="home-nav-btn" data-nav="route-list" aria-label="Route">{icon("pin", 20)}<span>Route</span></button>
          <div class="home-nav-orb-slot"></div>
          <button class="home-nav-btn" data-nav="secured-list" aria-label="Secured leads">{icon("secured", 20)}<span>Secured</span></button>
          <button class="home-nav-btn" data-nav="home" aria-label="Profile">{icon("owner", 20)}<span>You</span></button>
          <button class="home-nav-orb ptt-btn" data-nav="convo" aria-label="Talk to agent">
            {icon("mic", 26)}
          </button>
        </nav>

        <section class="home-properties-panel" id="home-properties-panel" aria-label="Oak Valley properties">
          <div class="properties-panel-head">
            <div class="properties-panel-title">
              <span class="properties-panel-title-main">Oak Valley</span>
              <span class="properties-panel-sub">6 properties scouted by agent</span>
            </div>
            <button type="button" class="properties-close" id="home-properties-close" aria-label="Close properties list">
              {icon("close", 16)}
            </button>
          </div>
          <div class="properties-panel-list">
            <div class="prop-row">
              <div class="prop-row-thumb" aria-hidden="true" style="background-image:url('https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=120&amp;h=120&amp;fit=crop&amp;q=80')"></div>
              <div class="prop-row-body">
                <div class="prop-row-addr-row">
                  <span class="prop-row-addr">312 Trinity St</span>
                  <span class="pcard-grade-badge" data-grade="A">A</span>
                </div>
                <div class="prop-row-meta">0.2 mi · quiet street</div>
              </div>
              <i class="ph-bold ph-caret-right prop-row-chev" style="font-size:14px;line-height:1"></i>
            </div>
            <div class="prop-row">
              <div class="prop-row-thumb" aria-hidden="true" style="background-image:url('https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=120&amp;h=120&amp;fit=crop&amp;q=80')"></div>
              <div class="prop-row-body">
                <div class="prop-row-addr-row">
                  <span class="prop-row-addr">514 Red River St</span>
                  <span class="pcard-grade-badge" data-grade="A">A</span>
                </div>
                <div class="prop-row-meta">0.4 mi · fresh paint</div>
              </div>
              <i class="ph-bold ph-caret-right prop-row-chev" style="font-size:14px;line-height:1"></i>
            </div>
            <div class="prop-row">
              <div class="prop-row-thumb" aria-hidden="true" style="background-image:url('https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=120&amp;h=120&amp;fit=crop&amp;q=80')"></div>
              <div class="prop-row-body">
                <div class="prop-row-addr-row">
                  <span class="prop-row-addr">227 E 4th St</span>
                  <span class="pcard-grade-badge" data-grade="B">B</span>
                </div>
                <div class="prop-row-meta">0.5 mi · owner on site</div>
              </div>
              <i class="ph-bold ph-caret-right prop-row-chev" style="font-size:14px;line-height:1"></i>
            </div>
            <div class="prop-row">
              <div class="prop-row-thumb" aria-hidden="true" style="background-image:url('https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=120&amp;h=120&amp;fit=crop&amp;q=80')"></div>
              <div class="prop-row-body">
                <div class="prop-row-addr-row">
                  <span class="prop-row-addr">905 E 3rd St</span>
                  <span class="pcard-grade-badge" data-grade="B">B</span>
                </div>
                <div class="prop-row-meta">0.6 mi · corner lot</div>
              </div>
              <i class="ph-bold ph-caret-right prop-row-chev" style="font-size:14px;line-height:1"></i>
            </div>
            <div class="prop-row">
              <div class="prop-row-thumb" aria-hidden="true" style="background-image:url('https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=120&amp;h=120&amp;fit=crop&amp;q=80')"></div>
              <div class="prop-row-body">
                <div class="prop-row-addr-row">
                  <span class="prop-row-addr">118 Neches St</span>
                  <span class="pcard-grade-badge" data-grade="C">C</span>
                </div>
                <div class="prop-row-meta">0.7 mi · needs approach</div>
              </div>
              <i class="ph-bold ph-caret-right prop-row-chev" style="font-size:14px;line-height:1"></i>
            </div>
            <div class="prop-row">
              <div class="prop-row-thumb" aria-hidden="true" style="background-image:url('https://images.unsplash.com/photo-1502005229762-cf1b2da7c5d6?w=120&amp;h=120&amp;fit=crop&amp;q=80')"></div>
              <div class="prop-row-body">
                <div class="prop-row-addr-row">
                  <span class="prop-row-addr">741 E Cesar Chavez</span>
                  <span class="pcard-grade-badge" data-grade="D">D</span>
                </div>
                <div class="prop-row-meta">0.9 mi · low priority</div>
              </div>
              <i class="ph-bold ph-caret-right prop-row-chev" style="font-size:14px;line-height:1"></i>
            </div>
          </div>
        </section>
      </div>
    '''

    convo = f'''
      <div class="scr-convo scr-convo-v2">
        <button class="convo-close" data-nav="home" aria-label="Close">{icon("close", 20)}</button>
        <div class="convo-transcript" id="convo-transcript"></div>
        <div class="convo-foot">
          <div class="convo-status" id="convo-status">Listening</div>
          <button class="convo-orb-btn" id="convo-orb-btn" aria-label="Continue">
            <div class="voice-orb convo-voice-orb" id="convo-voice-orb" data-state="idle">
              <div class="orb-group">
                <span class="orb-core"></span>
                <span class="orb-ring"></span>
                <span class="orb-ring orb-ring-2"></span>
              </div>
              <div class="orb-wave" aria-hidden="true">
                <span></span><span></span><span></span><span></span>
                <span></span><span></span><span></span><span></span>
              </div>
            </div>
          </button>
          <button class="btn btn-primary btn-l convo-cta-btn" id="convo-cta-btn" data-nav="drive-start" hidden>Let's Go</button>
        </div>
      </div>
    '''

    drive = f'''
      <div class="scr-drive scr-drive-v2">
        <div class="drive-map-full" id="drive-real-map"></div>
        <div class="drive-toast" id="drive-toast" hidden>
          <span class="drive-toast-icon">{icon("check", 14)}</span>
          <span class="drive-toast-text">Property saved as potential lead</span>
        </div>
        <div class="drive-sheet" id="drive-sheet">
          <div class="drive-sheet-header">
            <div class="drive-sheet-status">
              <span class="drive-status-dot"></span>
              <span id="drive-status-text">En route</span>
            </div>
            <button class="drive-sheet-close" data-nav="home" aria-label="End drive">{icon("close", 16)}</button>
          </div>
          <div class="drive-sheet-progress-row">
            <span>Route progress</span>
            <span class="drive-sheet-progress-count"><b id="drive-progress-idx">1</b> / <span id="drive-progress-total">12</span> stops</span>
          </div>
          <div class="drive-sheet-progress-bar">
            <div class="drive-sheet-progress-fill" id="drive-progress-fill" style="width:8%"></div>
          </div>
          <div class="drive-sheet-next-label">Next stop</div>
          <div class="drive-sheet-next-card">
            <div class="drive-sheet-next-thumb" id="drive-next-thumb" aria-hidden="true" style="background-image:url('https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=160&amp;h=160&amp;fit=crop&amp;q=80')"></div>
            <div class="drive-sheet-next-body">
              <div class="drive-sheet-next-addr">
                <span id="drive-next-addr">123 Main St</span>
                <span class="pcard-grade-badge" id="drive-next-grade" data-grade="A">A</span>
              </div>
              <div class="drive-sheet-next-meta" id="drive-next-meta">Austin, TX · 0.2 mi · 2 min</div>
            </div>
          </div>
          <div class="drive-sheet-orb-wrap">
            <div class="drive-sheet-orb-status" id="drive-orb-status">Speaking</div>
            <button class="drive-sheet-orb" id="drive-orb-btn" aria-label="Voice assistant" data-nav="inspect">
              <div class="voice-orb drive-voice-orb" id="drive-voice-orb" data-state="idle">
                <div class="orb-group">
                  <span class="orb-core"></span>
                  <span class="orb-ring"></span>
                  <span class="orb-ring orb-ring-2"></span>
                </div>
              </div>
            </button>
          </div>
        </div>
      </div>
    '''

    stop = f'''
      <div class="scr-stop">
        <div class="app-bar" style="position:relative;height:auto;padding:12px 14px">
          <button class="app-bar-back" data-nav="drive" aria-label="Back">{icon("back_arrow", 18)}</button>
          <div class="app-bar-title">123 Main St</div>
          <button class="ico-btn ico-btn-m app-bar-action" aria-label="Camera">{icon("camera", 16)}</button>
        </div>
        <div class="scr-stop-body">
          <div class="pcard pcard-expanded" style="border:0; padding:0; max-width:none">
            <div class="pcard-head">
              <div class="grade-ring grade-ring-l" data-grade="A"><span>A</span></div>
              <div>
                <div class="pcard-addr">123 Main St</div>
                <div class="pcard-sub">Austin, TX 78701</div>
              </div>
            </div>
            <div class="pimg-carousel">
              <div class="pimg pimg-sat"><div class="pimg-label">Satellite</div></div>
              <div class="pimg-dots"><span class="active"></span><span></span><span></span></div>
            </div>
            <div class="pcard-section">
              <div class="pcard-section-label">Suggested tags</div>
              <div class="chip-row-inline" id="proto-tags">
                <button class="chip chip-suggested chip-sm chip-toggle" data-toggle><i>{icon("distress", 12)}</i>overgrown lawn<b class="chip-ico">{icon("plus", 9)}</b></button>
                <button class="chip chip-suggested chip-sm chip-toggle" data-toggle><i>{icon("distress", 12)}</i>roof damage<b class="chip-ico">{icon("plus", 9)}</b></button>
                <button class="chip chip-suggested chip-sm chip-toggle" data-toggle><i>{icon("legal", 12)}</i>tax lien<b class="chip-ico">{icon("plus", 9)}</b></button>
              </div>
            </div>
            <div class="pcard-section">
              <div class="pcard-section-label">Campaign fit</div>
              <div class="camp-mini">
                <div>
                  <div class="camp-name">Cash-offer campaign</div>
                  <div class="camp-reason">High equity, long tenure — solid fit.</div>
                </div>
                <button class="camp-swap">Swap</button>
              </div>
            </div>
            <div class="pcard-actions">
              <button class="btn btn-primary btn-m btn-block" data-nav="added">Add as lead</button>
              <button class="btn btn-ghost btn-m" data-nav="drive-next">Dismiss</button>
            </div>
            <button class="pcard-details">Show details {icon("chevron_down", 12)}</button>
          </div>
        </div>
      </div>
    '''

    added = f'''
      <div class="scr-added">
        <div class="added-hero">
          <div class="lead-check" style="width:56px;height:56px;font-size:28px">{icon("check", 28)}</div>
          <div class="added-title">Got it — added.</div>
          <div class="added-sub">123 Main St · Grade A · Cash-offer campaign.</div>
        </div>
        <div class="added-next">
          <div class="added-next-label">Next up</div>
          <div class="added-next-body">
            <div class="grade-ring grade-ring-m" data-grade="B"><span>B</span></div>
            <div>
              <div class="pcard-addr" style="font-size:15px">4471 E Cesar Chavez</div>
              <div class="pcard-sub">0.8 mi · 3 minutes</div>
            </div>
          </div>
        </div>
        <button class="btn btn-primary btn-l btn-block" data-nav="drive-next">Keep going</button>
      </div>
    '''

    def _list_nav(active):
        def cls(name):
            return "home-nav-btn active" if active == name else "home-nav-btn"
        return f'''
        <nav class="home-nav">
          <button class="{cls("home")}" data-nav="home" aria-label="Home">{icon("distress", 20)}<span>Home</span></button>
          <button class="{cls("route")}" data-nav="route-list" aria-label="Route">{icon("pin", 20)}<span>Route</span></button>
          <div class="home-nav-orb-slot"></div>
          <button class="{cls("secured")}" data-nav="secured-list" aria-label="Secured leads">{icon("secured", 20)}<span>Secured</span></button>
          <button class="{cls("you")}" data-nav="home" aria-label="Profile">{icon("owner", 20)}<span>You</span></button>
          <button class="home-nav-orb ptt-btn" data-nav="convo" aria-label="Talk to agent">
            {icon("mic", 26)}
          </button>
        </nav>
        '''

    route_history = [
        ("Oak Valley loop",        "6 properties · 4.2 mi · 78701",  "today",  "6",  True,  "Today"),
        ("East Austin loop",       "9 properties · 5.8 mi · Sep 14", "week",   "9",  True,  None),
        ("Bouldin Creek sweep",    "4 properties · 2.9 mi · Sep 13", "week",   "4",  False, None),
        ("Cesar Chavez corridor",  "12 properties · 6.4 mi · Sep 09","month",  "12", True,  None),
        ("Manor Rd sweep",         "7 properties · 4.1 mi · Sep 05", "month",  "7",  True,  None),
        ("Chicon St quick loop",   "3 properties · 1.8 mi · Sep 02", "month",  "3",  False, None),
        ("Willow Creek pass",      "10 properties · 5.2 mi · Aug 28","older",  "10", True,  None),
        ("Zilker outer loop",      "8 properties · 4.7 mi · Aug 22", "older",  "8",  True,  None),
        ("Rosedale sweep",         "5 properties · 3.1 mi · Aug 18", "older",  "5",  False, None),
    ]
    def _route_row(name, meta, when, props, high, badge):
        badge_html = f'<span class="listing-row-badge">{esc(badge)}</span>' if badge else ''
        return f'''
            <div class="listing-row" data-nav="property-details" data-when="{when}" data-props="{props}" data-high="{'true' if high else 'false'}">
              <div class="route-row-icon">{icon("map", 16) if False else '<i class="ph-bold ph-map-trifold" style="font-size:16px;line-height:1"></i>'}</div>
              <div class="prop-row-body">
                <div class="prop-row-addr-row">
                  <span class="prop-row-addr">{esc(name)}</span>
                  {badge_html}
                </div>
                <div class="prop-row-meta">{esc(meta)}</div>
              </div>
              <i class="ph-bold ph-caret-right prop-row-chev" style="font-size:14px;line-height:1"></i>
            </div>
        '''
    route_rows = "".join(_route_row(*args) for args in route_history)

    route_list = f'''
      <div class="scr-listing">
        <div class="listing-header">
          <div class="listing-title-row">
            <div>
              <div class="listing-title">Your Routes</div>
              <div class="listing-sub">Every route you've driven</div>
            </div>
          </div>
          <div class="search-row listing-search-row">
            <label class="search-bar">
              <span class="search-ico">{icon("search", 16)}</span>
              <input type="search" placeholder="Search routes by area, zip…" data-search-scope="route-list" />
            </label>
            <button class="listing-filter-btn" type="button" aria-label="Filter routes" aria-expanded="false" data-filter-toggle="route-list">{icon("filter", 16)}<span class="listing-filter-count" hidden>1</span></button>
            <div class="filter-dd" data-filter-panel="route-list" role="dialog" aria-label="Filter routes" hidden>
              <div class="filter-dd-group">
                <div class="filter-dd-title">Time</div>
                <div class="filter-dd-list" data-filter-scope="route-list" data-filter-group="time">
                  <button class="filter-dd-row filter-dd-row-all is-active" type="button" data-filter="all">
                    <span class="filter-dd-check filter-dd-check-all">{icon("minus", 12)}</span>
                    <span class="filter-dd-label">All time</span>
                  </button>
                  <div class="filter-dd-sep"></div>
                  <button class="filter-dd-row" type="button" data-filter="today">
                    <span class="filter-dd-check">{icon("check", 12)}</span>
                    <span class="filter-dd-label">Today</span>
                  </button>
                  <button class="filter-dd-row" type="button" data-filter="week">
                    <span class="filter-dd-check">{icon("check", 12)}</span>
                    <span class="filter-dd-label">This week</span>
                  </button>
                  <button class="filter-dd-row" type="button" data-filter="month">
                    <span class="filter-dd-check">{icon("check", 12)}</span>
                    <span class="filter-dd-label">This month</span>
                  </button>
                  <button class="filter-dd-row" type="button" data-filter="high-yield">
                    <span class="filter-dd-check">{icon("check", 12)}</span>
                    <span class="filter-dd-label">High-yield only</span>
                  </button>
                </div>
              </div>
              <div class="filter-dd-actions">
                <button class="btn btn-ghost btn-s" type="button" data-filter-reset="route-list">Reset</button>
                <button class="btn btn-primary btn-s" type="button" data-filter-close="route-list">Done</button>
              </div>
            </div>
          </div>
        </div>
        <div class="listing-body">
          <div class="listing-section-label">Route history</div>
          <div class="listing-list" data-filter-target="route-list">
            {route_rows}
          </div>
          <div class="listing-empty" hidden>No routes match this filter.</div>
        </div>
        {_list_nav("route")}
      </div>
    '''

    secured_leads = [
        ("123 Main St",       "Austin, TX 78701",    "A", "Cash-offer",    "Sep 12 · 2:14 pm",  "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=120&h=120&fit=crop&q=80",     True),
        ("4471 E Cesar Chavez","Austin, TX 78702",   "B", "Foreclosure",   "Sep 12 · 12:48 pm", "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=120&h=120&fit=crop&q=80",    False),
        ("208 Willow Creek",  "Austin, TX 78704",    "A", "Cash-offer",    "Sep 11 · 4:02 pm",  "https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?w=120&h=120&fit=crop&q=80",   False),
        ("910 Bouldin Ave",   "Austin, TX 78704",    "B", "Rehab",         "Sep 11 · 10:31 am", "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=120&h=120&fit=crop&q=80",   False),
        ("6203 Manor Rd",     "Austin, TX 78723",    "C", "Rental",        "Sep 10 · 3:22 pm",  "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=120&h=120&fit=crop&q=80",   False),
        ("1104 Chicon St",    "Austin, TX 78702",    "A", "Cash-offer",    "Sep 10 · 11:05 am", "https://images.unsplash.com/photo-1502005229762-cf1b2da7c5d6?w=120&h=120&fit=crop&q=80",   False),
    ]
    def _sec_row(addr, city, grade, camp, when, img, is_top):
        top_badge = '<span class="listing-row-badge">Latest</span>' if is_top else ''
        camp_slug = camp.lower().replace(' ', '-')
        return f'''
            <div class="listing-row" data-nav="property-details" data-grade="{grade}" data-campaign="{camp_slug}">
              <div class="prop-row-thumb listing-row-thumb-sq" aria-hidden="true" style="background-image:url('{img}')"></div>
              <div class="prop-row-body">
                <div class="prop-row-addr-row">
                  <span class="prop-row-addr">{addr}</span>
                  <span class="pcard-grade-badge" data-grade="{grade}">{grade}</span>
                  {top_badge}
                </div>
                <div class="prop-row-meta">{city}</div>
                <div class="listing-row-foot">
                  <span class="listing-row-chip">{camp}</span>
                  <span class="listing-row-time">{when}</span>
                </div>
              </div>
              <i class="ph-bold ph-caret-right prop-row-chev" style="font-size:14px;line-height:1"></i>
            </div>
        '''
    secured_rows = "".join(_sec_row(*args) for args in secured_leads)

    secured_list = f'''
      <div class="scr-listing">
        <div class="listing-header">
          <div class="listing-title-row">
            <div>
              <div class="listing-title">Secured leads</div>
              <div class="listing-sub">Sorted by newest · This week</div>
            </div>
          </div>
          <div class="search-row listing-search-row">
            <label class="search-bar">
              <span class="search-ico">{icon("search", 16)}</span>
              <input type="search" placeholder="Search by address, owner…" data-search-scope="secured-list" />
            </label>
            <button class="listing-filter-btn" type="button" aria-label="Filter leads" aria-expanded="false" data-filter-toggle="secured-list">{icon("filter", 16)}<span class="listing-filter-count" hidden>1</span></button>
            <div class="filter-dd" data-filter-panel="secured-list" role="dialog" aria-label="Filter leads" hidden>
              <div class="filter-dd-group">
                <div class="filter-dd-title">Grade</div>
                <div class="filter-dd-list" data-filter-scope="secured-list" data-filter-group="grade">
                  <button class="filter-dd-row filter-dd-row-all is-active" type="button" data-filter="all">
                    <span class="filter-dd-check filter-dd-check-all">{icon("minus", 12)}</span>
                    <span class="filter-dd-label">All grades</span>
                  </button>
                  <div class="filter-dd-sep"></div>
                  <button class="filter-dd-row" type="button" data-filter="grade-a">
                    <span class="filter-dd-check">{icon("check", 12)}</span>
                    <span class="filter-dd-label">Grade A</span>
                  </button>
                  <button class="filter-dd-row" type="button" data-filter="grade-b">
                    <span class="filter-dd-check">{icon("check", 12)}</span>
                    <span class="filter-dd-label">Grade B</span>
                  </button>
                  <button class="filter-dd-row" type="button" data-filter="grade-c">
                    <span class="filter-dd-check">{icon("check", 12)}</span>
                    <span class="filter-dd-label">Grade C</span>
                  </button>
                </div>
              </div>
              <div class="filter-dd-group">
                <div class="filter-dd-title">Campaign</div>
                <div class="filter-dd-list" data-filter-scope="secured-list" data-filter-group="campaign">
                  <button class="filter-dd-row filter-dd-row-all is-active" type="button" data-filter="all">
                    <span class="filter-dd-check filter-dd-check-all">{icon("minus", 12)}</span>
                    <span class="filter-dd-label">All campaigns</span>
                  </button>
                  <div class="filter-dd-sep"></div>
                  <button class="filter-dd-row" type="button" data-filter="cash-offer">
                    <span class="filter-dd-check">{icon("check", 12)}</span>
                    <span class="filter-dd-label">Cash-offer</span>
                  </button>
                  <button class="filter-dd-row" type="button" data-filter="foreclosure">
                    <span class="filter-dd-check">{icon("check", 12)}</span>
                    <span class="filter-dd-label">Foreclosure</span>
                  </button>
                  <button class="filter-dd-row" type="button" data-filter="rehab">
                    <span class="filter-dd-check">{icon("check", 12)}</span>
                    <span class="filter-dd-label">Rehab</span>
                  </button>
                  <button class="filter-dd-row" type="button" data-filter="rental">
                    <span class="filter-dd-check">{icon("check", 12)}</span>
                    <span class="filter-dd-label">Rental</span>
                  </button>
                </div>
              </div>
              <div class="filter-dd-actions">
                <button class="btn btn-ghost btn-s" type="button" data-filter-reset="secured-list">Reset</button>
                <button class="btn btn-primary btn-s" type="button" data-filter-close="secured-list">Done</button>
              </div>
            </div>
          </div>
        </div>
        <div class="listing-body">
          <div class="listing-section-label">Recent</div>
          <div class="listing-list" data-filter-target="secured-list">
            {secured_rows}
          </div>
          <div class="listing-empty" hidden>No leads match this filter.</div>
        </div>
        {_list_nav("secured")}
      </div>
    '''

    property_details = f'''
      <div class="scr-details">
        <div class="app-bar" style="position:relative;height:auto;padding:12px 14px">
          <button class="app-bar-back" data-nav="secured-list" aria-label="Back">{icon("back_arrow", 18)}</button>
          <div class="app-bar-title">123 Main St</div>
          <button class="ico-btn ico-btn-m app-bar-action" aria-label="More">{icon("more", 16)}</button>
        </div>
        <div class="details-body">
          <div class="details-carousel" data-carousel>
            <div class="details-carousel-track" data-carousel-track>
              <div class="details-carousel-slide">
                <div class="pimg pimg-photo" style="background-image:url('https://images.unsplash.com/photo-1568605114967-8130f3a36994?auto=format&fit=crop&w=1000&q=80')"></div>
              </div>
              <div class="details-carousel-slide">
                <div class="pimg pimg-photo" style="background-image:url('https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&w=1000&q=80')"></div>
              </div>
              <div class="details-carousel-slide">
                <div class="pimg pimg-photo" style="background-image:url('https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1000&q=80')"></div>
              </div>
              <div class="details-carousel-slide">
                <div class="pimg pimg-photo" style="background-image:url('https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=1000&q=80')"></div>
              </div>
              <div class="details-carousel-slide">
                <div class="pimg pimg-photo" style="background-image:url('https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=1000&q=80')"></div>
              </div>
              <div class="details-carousel-slide">
                <div class="pimg pimg-photo" style="background-image:url('https://images.unsplash.com/photo-1502005229762-cf1b2da7c5d6?auto=format&fit=crop&w=1000&q=80')"></div>
              </div>
            </div>
            <button class="details-carousel-btn details-carousel-prev" type="button" aria-label="Previous image" data-carousel-prev>{icon("chevron_back", 14)}</button>
            <button class="details-carousel-btn details-carousel-next" type="button" aria-label="Next image" data-carousel-next>{icon("chevron_right", 14)}</button>
            <div class="details-carousel-count" data-carousel-count>1 / 6</div>
            <div class="details-hero-dots" data-carousel-dots>
              <span class="active" data-carousel-dot="0"></span>
              <span data-carousel-dot="1"></span>
              <span data-carousel-dot="2"></span>
              <span data-carousel-dot="3"></span>
              <span data-carousel-dot="4"></span>
              <span data-carousel-dot="5"></span>
            </div>
          </div>
          <div class="details-head">
            <div class="details-addr">123 Main St</div>
            <div class="details-sub">Austin, TX 78701 · Secured Sep 12, 2:14 pm</div>
          </div>
          <div class="details-stats">
            <div class="dstat-money-row">
              <div class="dstat-money">
                <div class="dstat-money-label">Est. price</div>
                <div class="dstat-money-num">$180k</div>
              </div>
              <div class="dstat-money-divider" aria-hidden="true"></div>
              <div class="dstat-money">
                <div class="dstat-money-label">ARV</div>
                <div class="dstat-money-value">
                  <div class="dstat-money-num">$275k</div>
                  <div class="dstat-money-delta"><i class="ph-bold ph-trend-up" style="font-size:9px;line-height:1"></i>+$95k</div>
                </div>
              </div>
            </div>
            <div class="dstat-specs">
              <div class="dspec"><i class="ph-bold ph-bed" style="font-size:14px;line-height:1"></i><span><b>3</b> bd</span></div>
              <div class="dspec"><i class="ph-bold ph-bathtub" style="font-size:14px;line-height:1"></i><span><b>2</b> ba</span></div>
              <div class="dspec"><i class="ph-bold ph-ruler" style="font-size:14px;line-height:1"></i><span><b>1,420</b> sqft</span></div>
            </div>
          </div>

          <div class="details-section">
            <div class="details-section-label">Applied tags</div>
            <div class="chip-row-inline">
              <span class="chip chip-suggested chip-sm chip-on"><i>{icon("distress", 12)}</i>overgrown lawn</span>
              <span class="chip chip-suggested chip-sm chip-on"><i>{icon("distress", 12)}</i>roof damage</span>
              <span class="chip chip-suggested chip-sm chip-on"><i>{icon("legal", 12)}</i>tax lien</span>
            </div>
          </div>

          <div class="details-section">
            <div class="details-section-label">Owner</div>
            <div class="details-owner">
              <div class="details-owner-row">
                <span class="details-owner-ico">{icon("owner", 14)}</span>
                <div>
                  <div class="details-owner-name">Alice Cordova</div>
                  <div class="details-owner-meta">Owned 14 years · On-site</div>
                </div>
              </div>
              <div class="details-owner-row">
                <span class="details-owner-ico">{icon("phone", 14)}</span>
                <div class="details-owner-name">(512) 555-0182</div>
              </div>
            </div>
          </div>

          <div class="dtabs" data-dtabs>
            <div class="dtabs-bar" role="tablist">
              <button class="dtabs-btn active" type="button" role="tab" aria-selected="true" data-dtab="notes">Notes</button>
              <button class="dtabs-btn" type="button" role="tab" aria-selected="false" data-dtab="campaign">Campaign</button>
              <button class="dtabs-btn" type="button" role="tab" aria-selected="false" data-dtab="activity">Activity</button>
            </div>

            <div class="dtabs-panel active" data-dtab-panel="notes" role="tabpanel">
              <div class="dtabs-sub-label">Text note</div>
              <div class="details-note">Dog in yard — approached from side gate. Owner mentioned she's considering selling within 6 months and wants a cash offer. Roof visibly worn on south side.</div>
              <div class="dtabs-sub-label">Voice note</div>
              <div class="details-voice">
                <button class="details-voice-play" aria-label="Play memo">{icon("play", 14)}</button>
                <div class="details-voice-wave">
                  <span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span><span></span>
                </div>
                <div class="details-voice-time">0:24</div>
              </div>
            </div>

            <div class="dtabs-panel" data-dtab-panel="campaign" role="tabpanel" hidden>
              <div class="camp-mini">
                <div>
                  <div class="camp-name">Cash-offer campaign</div>
                  <div class="camp-reason">High equity, long tenure — solid fit.</div>
                </div>
                <span class="listing-row-chip">Assigned</span>
              </div>
              <div class="dtabs-kv">
                <div class="dtabs-kv-row"><span class="dtabs-kv-k">Fit score</span><span class="dtabs-kv-v">92 · Strong</span></div>
                <div class="dtabs-kv-row"><span class="dtabs-kv-k">Est. offer</span><span class="dtabs-kv-v">$142k – $158k</span></div>
                <div class="dtabs-kv-row"><span class="dtabs-kv-k">Next step</span><span class="dtabs-kv-v">Offer letter</span></div>
                <div class="dtabs-kv-row"><span class="dtabs-kv-k">Assigned to</span><span class="dtabs-kv-v">Joe R.</span></div>
              </div>
            </div>

            <div class="dtabs-panel" data-dtab-panel="activity" role="tabpanel" hidden>
              <div class="details-timeline">
                <div class="dtl-row">
                  <span class="dtl-dot"></span>
                  <div class="dtl-body">
                    <div class="dtl-title">Secured as lead</div>
                    <div class="dtl-time">Sep 12 · 2:14 pm</div>
                  </div>
                </div>
                <div class="dtl-row">
                  <span class="dtl-dot"></span>
                  <div class="dtl-body">
                    <div class="dtl-title">Voice memo added</div>
                    <div class="dtl-time">Sep 12 · 2:15 pm</div>
                  </div>
                </div>
                <div class="dtl-row">
                  <span class="dtl-dot"></span>
                  <div class="dtl-body">
                    <div class="dtl-title">Assigned to Cash-offer campaign</div>
                    <div class="dtl-time">Sep 12 · 2:14 pm</div>
                  </div>
                </div>
                <div class="dtl-row">
                  <span class="dtl-dot"></span>
                  <div class="dtl-body">
                    <div class="dtl-title">Scouted by agent</div>
                    <div class="dtl-time">Sep 12 · 9:02 am</div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div class="details-actions">
            <button class="btn btn-primary btn-m">{icon("phone", 14)}<span>Call owner</span></button>
            <button class="btn btn-ghost btn-m">{icon("pin", 14)}<span>Open in maps</span></button>
          </div>
        </div>
      </div>
    '''

    return (
        _proto_screen("home", home)
        + _proto_screen("convo", convo)
        + _proto_screen("drive", drive)
        + _proto_screen("stop", stop)
        + _proto_screen("added", added)
        + _proto_screen("route-list", route_list)
        + _proto_screen("secured-list", secured_list)
        + _proto_screen("property-details", property_details)
    )

def _proto_nav():
    steps = [
        ("home","Home"),("convo","Convo"),("drive","Drive"),("stop","Stop"),("added","Added"),
        ("route-list","Route"),("secured-list","Secured"),("property-details","Details"),
    ]
    return '<div class="proto-nav">' + "".join(
        f'<button class="proto-nav-btn{" active" if i==0 else ""}" data-nav="{esc(sid)}">{esc(label)}</button>'
        for i, (sid, label) in enumerate(steps)
    ) + '</div>'

DESIGN_PAGE = f'''
<section class="design-page">
  <div class="proto-stage">
    <div class="phone proto-phone">
      <div class="phone-statusbar">
        <span>9:41</span>
        <span class="phone-signal"></span>
      </div>
      <div class="phone-screen proto-screens" id="proto-screens">
        {_proto_screens()}
      </div>
    </div>
  </div>
</section>
'''

PAGES = [
    ("variables", "Variables",         VARIABLES_PAGE),
    ("library",   "Component Library", LIBRARY_PAGE),
    ("design",    "Design",            DESIGN_PAGE),
]

page_nav = "".join(
    f'<button class="page-btn{" active" if i==0 else ""}" data-page="{esc(pid)}">{esc(label)}</button>'
    for i, (pid, label, _) in enumerate(PAGES)
)
page_panels = "".join(
    f'<div class="page{" active" if i==0 else ""}" data-page="{esc(pid)}">{body}</div>'
    for i, (pid, _, body) in enumerate(PAGES)
)

PAGE_NAV_HTML = f'<nav class="page-nav">{page_nav}</nav>'
BODY = f'<div class="pages">{page_panels}</div>'

# stats for header
totals = {k: v["count"] for k, v in COLLECTIONS.items()}
total = sum(totals.values())

HTML = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Profit Drive — Design Tokens</title>
<link rel="stylesheet" type="text/css" href="https://unpkg.com/@phosphor-icons/web@2.1.1/src/bold/style.css">
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" crossorigin="" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" crossorigin="" defer></script>
<style>
  i[class*="ph-"] {{ display: inline-flex; line-height: 1; vertical-align: middle; }}
  .leaflet-container {{ font-family: var(--sans); background: #f2efe9; }}
  .leaflet-control-attribution {{ display: none; }}
  .lpin {{
    width: 26px !important; height: 26px !important; border-radius: 50%;
    display: inline-flex !important; align-items: center; justify-content: center;
    font-weight: 700; font-size: 12px; color: #fff;
    box-shadow: 0 2px 6px rgba(0,0,0,.25), 0 0 0 2px rgba(255,255,255,.9);
  }}
  .lpin.g-a {{ background: var(--gradecolors-grade_a, #1A7F42); }}
  .lpin.g-b {{ background: var(--gradecolors-grade_b, #E8A317); color: #222; }}
  .lpin.g-c {{ background: var(--gradecolors-grade_c, #D93025); }}
  .lpin.g-d {{ background: var(--gradecolors-grade_d, #9D2525); }}
  .lyou {{
    width: 16px !important; height: 16px !important; border-radius: 50%;
    background: var(--colors-blue, #1A73E8);
    box-shadow: 0 0 0 5px rgba(26,115,232,.25), 0 0 0 12px rgba(26,115,232,.12);
  }}
</style>
<style>
  :root {{
    --bg: #ffffff;
    --panel: #ffffff;
    --panel-2: #f7f7f7;
    --border: #e6e8ec;
    --text: #222222;
    --text-dim: #6b7280;
    --accent: #E96A6A;
    --mono: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
    --sans: Inter, -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
{TOKEN_CSS_VARS}
  }}
  * {{ box-sizing: border-box; }}
  html, body {{ margin:0; padding:0; }}
  body {{
    font-family: var(--sans);
    background: var(--bg);
    color: var(--text);
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
  }}
  header.page {{
    padding: 28px 40px;
    border-bottom: 1px solid var(--border);
    display: flex; justify-content: space-between; align-items: flex-end;
    flex-wrap: wrap; gap: 16px;
  }}
  header.page h1 {{ margin: 0; font-size: 22px; font-weight: 600; }}
  .tabs .file {{
    margin-left: auto;
    align-self: center;
    color: var(--text-dim);
    font-size: 12px;
    font-family: var(--mono);
    padding-bottom: 12px;
  }}
  header.page .totals {{ display: flex; gap: 20px; font-size: 13px; color: var(--text-dim); }}
  header.page .totals strong {{ color: var(--text); font-weight: 600; }}

  main {{ padding: 32px 40px 80px; }}

  .collection {{ margin-bottom: 56px; }}
  .coll-title {{
    font-size: 28px; margin: 24px 0 4px;
    display: flex; align-items: baseline; gap: 12px;
    padding-bottom: 12px; border-bottom: 2px solid var(--border);
  }}
  .coll-title .count {{ font-size: 12px; color: var(--text-dim); font-weight: 400; }}

  .group {{ margin-top: 32px; }}
  .group-title {{
    font-size: 14px; text-transform: uppercase; letter-spacing: .08em;
    color: var(--text-dim); margin: 0 0 16px; font-weight: 600;
  }}
  .group-title .count {{
    font-size: 11px; background: var(--panel-2); color: var(--text-dim);
    padding: 2px 8px; border-radius: 999px; margin-left: 8px;
  }}

  .grid {{ display: grid; gap: 12px; }}
  .grid-color {{ grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); }}
  .grid-size {{ grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); }}
  .grid-font {{ grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); }}
  .grid-radius {{ grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); }}
  .grid-stroke {{ grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); }}
  .stack {{ display: flex; flex-direction: column; gap: 8px; }}

  .tok {{
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px;
    display: flex; align-items: center; gap: 14px;
  }}
  .tok-body {{ flex: 1; min-width: 0; }}
  .tok-name {{ font-size: 14px; font-weight: 500; word-break: break-all; }}
  .tok-value {{ font-size: 12px; color: var(--text-dim); margin-top: 2px; }}
  .mono {{ font-family: var(--mono); }}

  .swatch {{
    display: inline-block; border-radius: 8px; flex-shrink: 0;
    border: 1px solid rgba(0,0,0,.08);
    box-shadow: 0 1px 3px rgba(0,0,0,.3);
  }}

  .tok-preview {{ flex-shrink: 0; }}
  .spc-bar {{ height: 24px; background: var(--accent); border-radius: 4px; }}
  .tok-spc {{ align-items: center; }}
  .tok-spc .tok-preview {{ min-width: 4px; }}

  .radius-demo {{ width: 72px; height: 72px; background: var(--accent); }}
  .tok-radius {{ flex-direction: column; text-align: left; align-items: flex-start; }}
  .tok-radius .tok-body {{ text-align: left; }}

  .stroke-demo {{ width: 60px; height: 40px; border-radius: 6px; background: transparent; }}

  .tok-font .tok-preview,
  .tok-weight .tok-preview,
  .tok-size .tok-preview {{ color: var(--text); min-width: 100px; }}
  .tok-size {{ flex-direction: column; align-items: flex-start; }}
  .tok-size .tok-preview {{ min-height: 50px; display: flex; align-items: flex-end; }}
  .tok-size .tok-body {{ width: 100%; }}

  .chain {{
    margin-top: 8px; display: flex; flex-wrap: wrap; align-items: center;
    gap: 4px; font-size: 11px;
  }}
  .arrow {{ color: var(--text-dim); padding: 0 2px; }}
  .pill {{
    display: inline-flex; align-items: center; overflow: hidden;
    border-radius: 4px; font-family: var(--mono); font-size: 10px;
    border: 1px solid var(--border);
  }}
  .pill-coll {{ padding: 2px 6px; background: var(--panel-2); color: var(--text-dim); }}
  .pill-path {{ padding: 2px 6px; color: var(--text); }}
  .pill-primitive .pill-coll {{ background: #2a3a2e; color: #7bd88f; }}
  .pill-symantic  .pill-coll {{ background: #2a2a4a; color: #a29bfe; }}
  .pill-components .pill-coll {{ background: #4a2a2a; color: #ff9a9a; }}

  /* demos */
  .demos {{ margin-top: 72px; }}
  .demo-row {{ display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }}
  .demo-btn {{ border: 0; cursor: pointer; }}
  .type-stack {{
    background: var(--panel); border: 1px solid var(--border);
    border-radius: 12px; padding: 28px 32px; display: flex;
    flex-direction: column; gap: 14px;
  }}
  .status-row {{ display: flex; gap: 12px; flex-wrap: wrap; }}
  .status-chip {{
    color: white; padding: 8px 16px; border-radius: 999px;
    font-weight: 600; font-size: 13px;
  }}

  /* page-level nav — pill segmented control */
  .page-nav {{
    display: flex;
    width: fit-content;
    gap: 4px;
    padding: 5px;
    background: var(--panel-2);
    border: 1px solid var(--border);
    border-radius: 999px;
    box-shadow: 0 1px 2px rgba(0,0,0,.3);
  }}
  .page-btn {{
    background: transparent; color: var(--text-dim); border: 0;
    padding: 8px 18px;
    font: inherit; font-size: 13px; font-weight: 600;
    cursor: pointer; border-radius: 999px;
    transition: background .15s, color .15s;
    letter-spacing: .01em;
    white-space: nowrap;
  }}
  .page-btn:hover:not(.active) {{ color: var(--text); background: rgba(0,0,0,.04); }}
  .page-btn.active {{
    background: var(--accent);
    color: #ffffff;
  }}

  .page {{ display: none; }}
  .page.active {{ display: block; }}

  /* ==================== component library ==================== */
  .lib-tabs {{
    display: flex; gap: 4px; padding: 12px 0 0 0;
    border-bottom: 1px solid var(--border);
    position: sticky; top: 0;
    background: rgba(255,255,255,.9); backdrop-filter: blur(8px);
    z-index: 5;
  }}
  .lib-tab {{
    background: transparent; color: var(--text-dim); border: 0;
    padding: 12px 20px; font: inherit; font-size: 14px; font-weight: 500;
    cursor: pointer; border-bottom: 2px solid transparent;
    margin-bottom: -1px; transition: color .15s, border-color .15s;
  }}
  .lib-tab:first-child {{ padding-left: 0; }}
  .lib-tab:hover {{ color: var(--text); }}
  .lib-tab.active {{ color: var(--accent); border-bottom-color: var(--accent); }}

  .lib-panel {{ display: none; }}
  .lib-panel.active {{ display: block; padding-bottom: 60px; }}
  .lib-empty {{ padding: 40px; color: var(--text-dim); text-align: center; font-style: italic; }}

  .lib-grid {{
    display: grid; grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
    gap: 16px; margin-top: 20px;
  }}
  .lib-card {{
    background: var(--panel); border: 1px solid var(--border);
    border-radius: var(--cornerradius-radius_lg, 16px);
    padding: 20px;
    display: flex; flex-direction: column; gap: 14px;
  }}
  .lib-card-wide {{ grid-column: 1 / -1; }}
  .lib-card-head {{
    display: flex; justify-content: space-between; align-items: center; gap: 12px;
    flex-wrap: wrap;
  }}
  .lib-card-name {{
    font-size: var(--textsizes-card_title_size, 20px);
    font-weight: var(--textweights-card_title_weight, 600);
  }}
  .lib-stage {{
    background: var(--bg); border: 1px solid var(--border);
    border-radius: var(--cornerradius-radius_md, 12px);
    padding: 24px; min-height: 120px;
    display: flex; flex-direction: column; align-items: flex-start; justify-content: flex-start;
    gap: 14px;
  }}
  .lib-note {{ color: var(--text-dim); font-size: 12px; margin: 0; text-align: left; max-width: 100%; line-height: 1.45; }}
  .lib-tokens {{ display: flex; flex-wrap: wrap; gap: 4px; }}
  .tok-pill {{
    font-family: var(--mono); font-size: 10px;
    padding: 3px 8px; border-radius: 4px;
    background: var(--panel-2); border: 1px solid var(--border); color: var(--text-dim);
  }}
  .lib-note {{ color: var(--text-dim); font-size: 12px; margin: 0; text-align: left; max-width: 100%; line-height: 1.45; }}

  /* segmented control (state toggle) */
  .seg {{
    display: inline-flex; background: var(--panel-2);
    border: 1px solid var(--border);
    border-radius: var(--cornerradius-radius_pill, 999px);
    padding: 4px; gap: 0; overflow: hidden;
  }}
  .seg-btn {{
    background: transparent; color: var(--text-dim); border: 0;
    padding: 4px 10px; font: inherit; font-size: 11px; font-weight: 500;
    cursor: pointer; border-radius: 999px;
    text-transform: capitalize; white-space: nowrap;
    line-height: 1.4;
  }}
  .seg-btn:hover:not(.active) {{ color: var(--text); }}
  .seg-btn.active {{ background: var(--accent); color: #fff; }}

  /* ---- Voice Orb ---- */
  .orb-stage {{ display: flex; flex-direction: column; align-items: flex-start; gap: 12px; }}
  .voice-orb {{
    position: relative; width: 80px; height: 80px;
    display: inline-flex; align-items: center; justify-content: center;
  }}
  .orb-core {{
    position: absolute; inset: 22%; border-radius: 50%;
    background: radial-gradient(circle at 30% 30%, #ff8a8a, var(--colors-red_600, #E96A6A) 60%, var(--colors-red_800, #9D2525));
    box-shadow: 0 0 24px rgba(233,106,106,.45);
    transition: background .3s, box-shadow .3s;
  }}
  .orb-ring {{
    position: absolute; inset: 0; border-radius: 50%;
    border: 2px solid var(--colors-red_600, #E96A6A);
    opacity: .35;
  }}
  .orb-ring-2 {{ inset: 10%; opacity: .2; }}

  .voice-orb[data-state="idle"] .orb-core {{ animation: orbBreath 3.2s ease-in-out infinite; }}

  /* Orb-group wrapper so we can morph the whole orb into a waveform smoothly */
  .voice-orb .orb-group {{
    position: absolute; inset: 0;
    transition: transform .4s cubic-bezier(.34,1.16,.64,1), opacity .28s ease-out;
    transform-origin: center;
  }}
  .voice-orb .orb-wave {{
    position: absolute; inset: 0;
    display: flex; align-items: center; justify-content: center;
    gap: 8%;
    opacity: 0;
    transform: scaleX(0.4);
    transform-origin: center;
    transition: opacity .28s ease-out, transform .4s cubic-bezier(.34,1.16,.64,1);
    pointer-events: none;
  }}
  .voice-orb .orb-wave span {{
    display: inline-block;
    width: 5%; min-width: 3px;
    background: var(--colors-red_600, #E96A6A);
    border-radius: 999px;
    height: 22%;
    animation: orbWaveDance 900ms ease-in-out infinite;
    animation-play-state: paused;
  }}
  .voice-orb .orb-wave span:nth-child(1) {{ animation-delay: 0ms;   }}
  .voice-orb .orb-wave span:nth-child(2) {{ animation-delay: 90ms;  }}
  .voice-orb .orb-wave span:nth-child(3) {{ animation-delay: 50ms;  }}
  .voice-orb .orb-wave span:nth-child(4) {{ animation-delay: 180ms; }}
  .voice-orb .orb-wave span:nth-child(5) {{ animation-delay: 30ms;  }}
  .voice-orb .orb-wave span:nth-child(6) {{ animation-delay: 130ms; }}
  .voice-orb .orb-wave span:nth-child(7) {{ animation-delay: 80ms;  }}
  .voice-orb .orb-wave span:nth-child(8) {{ animation-delay: 210ms; }}
  @keyframes orbWaveDance {{
    0%,100% {{ height: 10%; }}
    50%     {{ height: 32%; }}
  }}

  /* Listening: orb collapses to nothing, waveform bars scale in and dance */
  .voice-orb[data-state="listening"] .orb-group {{ transform: scale(0); opacity: 0; }}
  .voice-orb[data-state="listening"] .orb-wave  {{ opacity: 1; transform: scaleX(1); }}
  .voice-orb[data-state="listening"] .orb-wave span {{ animation-play-state: running; }}

  /* Speaking: rings emanate outward (sound waves radiating from the orb) */
  .voice-orb[data-state="speaking"] .orb-ring {{ animation: orbPulse 1.2s ease-out infinite; }}
  .voice-orb[data-state="speaking"] .orb-ring-2 {{ animation: orbPulse 1.2s ease-out .4s infinite; }}
  .voice-orb[data-state="speaking"] .orb-core {{ background: radial-gradient(circle at 30% 30%, #ff9a9a, var(--colors-red_600, #E96A6A) 60%, var(--colors-red_700, #D83131)); }}

  .voice-orb[data-state="thinking"] .orb-core {{ animation: orbSpin 1.4s linear infinite; background: conic-gradient(from 0deg, var(--colors-red_600, #E96A6A), var(--colors-red_200, #DDAABB), var(--colors-red_600, #E96A6A)); }}

  /* Speaking: audio-output equalizer bars inside the orb */
  .voice-orb .orb-bars {{
    position: absolute; inset: 0;
    display: none; align-items: center; justify-content: center;
    gap: 6%;
  }}
  .voice-orb .orb-bars i {{
    display: inline-block;
    width: 6%; height: 20%;
    background: #fff; border-radius: 999px;
    animation: orbBar 620ms ease-in-out infinite;
  }}
  .voice-orb .orb-bars i:nth-child(1) {{ animation-delay: 0ms;   }}
  .voice-orb .orb-bars i:nth-child(2) {{ animation-delay: 110ms; }}
  .voice-orb .orb-bars i:nth-child(3) {{ animation-delay: 55ms;  }}
  .voice-orb .orb-bars i:nth-child(4) {{ animation-delay: 180ms; }}
  @keyframes orbBar {{
    0%,100% {{ height: 14%; }}
    50%     {{ height: 52%; }}
  }}
  .voice-orb[data-state="speaking"] .orb-bars {{ display: inline-flex; }}
  .voice-orb[data-state="speaking"] .orb-core {{ animation: orbBreath 1.6s ease-in-out infinite; }}
  .voice-orb[data-state="muted"] .orb-core {{ background: var(--colors-neutral_400, #B0B0B0); box-shadow: none; }}
  .voice-orb[data-state="muted"] .orb-ring, .voice-orb[data-state="muted"] .orb-ring-2 {{ border-color: var(--colors-neutral_400, #B0B0B0); }}
  .voice-orb[data-state="error"] .orb-core {{ background: radial-gradient(circle at 30% 30%, #ff6b6b, var(--colors-tomato_red, #D93025)); animation: orbShake .5s ease-in-out infinite; }}
  .voice-orb[data-state="error"] .orb-ring, .voice-orb[data-state="error"] .orb-ring-2 {{ border-color: var(--colors-tomato_red, #D93025); }}

  @keyframes orbBreath  {{ 0%,100%{{transform:scale(1);opacity:.9}} 50%{{transform:scale(1.06);opacity:1}} }}
  @keyframes orbPulse   {{ 0%{{transform:scale(1);opacity:.55}} 100%{{transform:scale(1.6);opacity:0}} }}
  @keyframes orbSpin    {{ to {{ transform: rotate(360deg); }} }}
  @keyframes orbSpeak   {{ from {{ transform: scaleY(1) scaleX(1); }} to {{ transform: scaleY(1.15) scaleX(.95); }} }}
  @keyframes orbShake   {{ 0%,100%{{transform:translateX(0)}} 25%{{transform:translateX(-3px)}} 75%{{transform:translateX(3px)}} }}

  .orb-status {{ font-size: 12px; color: var(--text-dim); font-weight: 500; }}

  /* ---- Ambient Orb Dock ---- */
  .dock-stage {{
    position: relative; width: 100%; height: 200px;
    background: var(--panel-2); border-radius: var(--cornerradius-radius_md, 12px);
    overflow: hidden;
  }}
  .dock-fake-content {{ padding: 16px; color: var(--text-dim); font-size: 12px; }}
  .dock-orb {{
    position: absolute; bottom: 12px; right: 16px;
    display: flex; flex-direction: column; align-items: center; gap: 6px;
  }}
  .dock-orb-right {{ right: 16px; left: auto; }}
  .dock-orb-left  {{ left: 16px; right: auto; }}

  /* ---- Status Pill ---- */
  .pill-row {{ display: flex; flex-wrap: wrap; gap: 8px; }}
  .status-pill {{
    display: inline-flex; align-items: center; gap: 8px;
    background: var(--colors-near_black, #222);
    color: #fff; padding: 8px 14px;
    border-radius: var(--cornerradius-radius_pill, 999px);
    font-size: 12px; font-weight: 500;
  }}
  .status-pill .dot {{ width: 8px; height: 8px; border-radius: 50%; background: currentColor; }}
  .status-listening .dot {{ background: var(--colors-red_600, #E96A6A); animation: dotPulse 1.2s ease-in-out infinite; }}
  .status-thinking .dot {{ background: var(--colors-yellow, #E8A317); animation: dotPulse 1.2s ease-in-out infinite; }}
  .status-speaking .dot {{ background: var(--colors-green, #1A7F42); animation: dotPulse 0.6s ease-in-out infinite; }}
  .status-idle .dot {{ background: var(--colors-neutral_400, #B0B0B0); }}
  @keyframes dotPulse {{ 0%,100%{{opacity:.4}} 50%{{opacity:1}} }}

  /* ---- Waveform ---- */
  .wave-stage {{ width: 100%; display: flex; justify-content: flex-start; }}
  .waveform {{ display: flex; gap: 4px; align-items: center; height: 48px; }}
  .wave-bar {{
    width: 4px; height: 8px; background: var(--colors-red_600, #E96A6A);
    border-radius: 2px;
  }}
  .waveform[data-state="listening"] .wave-bar {{ animation: waveBounce 1s ease-in-out infinite; }}
  .waveform[data-state="idle"] .wave-bar {{ background: var(--colors-neutral_400, #B0B0B0); height: 6px; }}
  @keyframes waveBounce {{ 0%,100%{{height:8px}} 50%{{height:40px}} }}

  /* ---- Push-to-Talk ---- */
  .ptt-stage {{ padding: 12px; }}
  .ptt-btn {{
    width: 72px; height: 72px; border-radius: 50%; border: 0;
    background: radial-gradient(circle at 30% 30%, #ff8a8a, var(--colors-red_600, #E96A6A) 60%, var(--colors-red_800, #9D2525));
    color: #fff; cursor: pointer;
    box-shadow: 0 4px 20px rgba(233,106,106,.5), inset 0 -3px 8px rgba(0,0,0,.2);
    display: inline-flex; align-items: center; justify-content: center;
    transition: transform .15s;
  }}
  .ptt-btn:hover {{ transform: scale(1.05); }}
  .ptt-btn:active {{ transform: scale(.95); }}

  /* ---- Transcript Bubble ---- */
  .transcript-stack {{ display: flex; flex-direction: column; gap: 8px; width: 100%; align-items: stretch; }}
  .bubble {{
    padding: 10px 14px; border-radius: var(--cornerradius-radius_lg, 16px);
    font-size: var(--textsizes-body_txt_size, 14px);
    line-height: 1.4; max-width: 85%;
  }}
  .bubble-agent {{
    background: var(--panel-2); color: var(--text); align-self: flex-start;
    border: 1px solid var(--border); border-bottom-left-radius: 4px;
  }}
  .bubble-driver {{
    background: var(--colors-red_600, #E96A6A); color: #fff; align-self: flex-end;
    border-bottom-right-radius: 4px;
  }}
  .bubble em {{ font-style: normal; padding: 1px 6px; border-radius: 4px; background: rgba(0,0,0,.06); }}
  .bubble-driver em {{ background: rgba(255,255,255,.2); }}

  /* ---- Nudge Banner ---- */
  .nudge-banner {{
    display: flex; align-items: center; gap: 12px;
    background: var(--panel-2); border: 1px solid var(--border);
    border-left: 4px solid var(--gradecolors-grade_a, #D93025);
    padding: 12px 14px; border-radius: var(--cornerradius-radius_md, 12px);
    width: 100%; max-width: 360px;
  }}
  .nudge-icon {{ font-size: 22px; }}
  .nudge-body {{ flex: 1; }}
  .nudge-title {{ font-size: 14px; font-weight: 600; color: var(--text); }}
  .nudge-meta {{ font-size: 12px; color: var(--text-dim); margin-top: 2px; }}
  .nudge-dismiss {{ background: transparent; border: 0; color: var(--text-dim); cursor: pointer; font-size: 14px; }}

  /* ---- Grade Ring ---- */
  .grade-stage {{ display: flex; gap: 24px; align-items: center; justify-content: flex-start; }}
  .grade-ring {{
    border-radius: 50%; display: inline-flex; align-items: center; justify-content: center;
    font-weight: 700; color: var(--gradecolors-grade_a, #1A7F42);
    border: 4px solid currentColor;
    background: color-mix(in srgb, currentColor 8%, transparent);
    transition: color .3s;
  }}
  .grade-ring-s {{ width: 36px; height: 36px; font-size: 14px; border-width: 3px; }}
  .grade-ring-m {{ width: 56px; height: 56px; font-size: 22px; border-width: 4px; }}
  .grade-ring-l {{ width: 80px; height: 80px; font-size: 32px; border-width: 5px; }}
  .grade-ring span {{ color: currentColor; }}
  .grade-ring[data-grade="A"] {{ color: var(--gradecolors-grade_a, #1A7F42); }}
  .grade-ring[data-grade="B"] {{ color: var(--gradecolors-grade_b, #E8A317); }}
  .grade-ring[data-grade="C"] {{ color: var(--gradecolors-grade_c, #D93025); }}
  .grade-ring[data-grade="D"] {{ color: var(--gradecolors-grade_d, #9D2525); }}

  /* ---- Grade Badge ---- */
  .badge-stack {{ display: flex; flex-wrap: wrap; gap: 8px; justify-content: flex-start; }}
  .grade-badge {{
    display: inline-flex; align-items: center; gap: 6px;
    padding: 4px 12px 4px 4px;
    border-radius: var(--cornerradius-radius_pill, 999px);
    background: var(--panel-2); font-size: 12px; font-weight: 500; color: var(--text);
  }}
  .grade-badge b {{
    display: inline-flex; align-items: center; justify-content: center;
    width: 22px; height: 22px; border-radius: 50%; font-size: 12px; color: #fff;
  }}
  .grade-badge.grade-a b {{ background: var(--gradecolors-grade_a, #D93025); }}
  .grade-badge.grade-b b {{ background: var(--gradecolors-grade_b, #E96A6A); }}
  .grade-badge.grade-c b {{ background: var(--gradecolors-grade_c, #E8A317); color: #222; }}
  .grade-badge.grade-d b {{ background: var(--gradecolors-grade_d, #B0B0B0); }}

  /* ---- Stat Tile ---- */
  .stat-row {{ display: flex; gap: 12px; width: 100%; }}
  .stat-tile {{
    flex: 1; padding: 14px 16px;
    background: var(--panel-2); border: 1px solid var(--border);
    border-radius: var(--cornerradius-radius_md, 12px);
  }}
  .stat-num {{ font-size: 28px; font-weight: 700; color: var(--text); line-height: 1.1; }}
  .stat-sub {{ font-size: 12px; font-weight: 500; color: var(--text-dim); margin-left: 4px; }}
  .stat-label {{ font-size: 11px; color: var(--text-dim); margin-top: 4px; text-transform: uppercase; letter-spacing: .05em; }}

  /* ---- Progress ---- */
  .progress-stack {{ width: 100%; display: flex; flex-direction: column; gap: 8px; }}
  .progress-meta {{ display: flex; justify-content: space-between; font-size: 12px; color: var(--text-dim); }}
  .progress-bar {{ height: 8px; background: var(--colors-neutral_200, #E0E0E0); border-radius: var(--cornerradius-radius_pill, 999px); overflow: hidden; }}
  .progress-fill {{ height: 100%; background: var(--colors-red_600, #E96A6A); border-radius: inherit; transition: width .3s; }}

  /* ---- Address Block ---- */
  .addr-block {{ text-align: left; }}
  .addr-line-1 {{ font-size: 20px; font-weight: 600; color: var(--text); }}
  .addr-line-2 {{ font-size: 14px; color: var(--text-dim); margin-top: 2px; }}
  .addr-meta {{ font-size: 11px; color: var(--text-dim); margin-top: 8px; font-family: var(--mono); }}

  /* ---- Owner Row ---- */
  .owner-row {{ display: flex; align-items: center; gap: 12px; width: 100%; }}
  .owner-avatar {{
    width: 40px; height: 40px; border-radius: 50%;
    background: var(--colors-neutral_200, #E0E0E0); color: var(--colors-near_black, #222);
    display: inline-flex; align-items: center; justify-content: center;
    font-weight: 600; font-size: 13px;
  }}
  .owner-body {{ flex: 1; min-width: 0; }}
  .owner-name {{ font-size: 14px; font-weight: 600; }}
  .owner-meta {{ font-size: 12px; color: var(--text-dim); }}
  .owner-call {{ background: var(--panel-2); border: 1px solid var(--border); border-radius: 50%; width: 36px; height: 36px; cursor: pointer; font-size: 16px; }}

  /* ---- Financials Row ---- */
  .fin-row {{ display: flex; gap: 8px; width: 100%; }}
  .fin-cell {{ flex: 1; padding: 10px 12px; background: var(--panel-2); border-radius: var(--cornerradius-radius_md, 12px); border: 1px solid var(--border); }}
  .fin-label {{ font-size: 10px; color: var(--text-dim); text-transform: uppercase; letter-spacing: .05em; }}
  .fin-value {{ font-size: 16px; font-weight: 600; color: var(--text); margin-top: 2px; }}
  .fin-warn {{ border-color: var(--colors-yellow, #E8A317); }}
  .fin-warn .fin-value {{ color: var(--colors-yellow, #E8A317); }}

  /* ==================== Foundation ==================== */
  /* Button */
  .btn-grid {{ display: flex; flex-direction: column; gap: 10px; width: 100%; }}
  .btn-row {{ display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }}
  .btn {{
    display: inline-flex; align-items: center; justify-content: center; gap: 6px;
    border: 0; cursor: pointer; font: inherit; font-weight: 600;
    border-radius: var(--cornerradius-radius_md, 12px);
    font-family: var(--fontfamily-font_family), system-ui, sans-serif;
    transition: filter .15s, transform .05s;
  }}
  .btn:active {{ transform: translateY(1px); }}
  .btn:disabled {{ opacity: .5; cursor: not-allowed; }}
  .btn-s {{ padding: 6px 12px; font-size: 12px; }}
  .btn-m {{ padding: 10px 18px; font-size: 14px; }}
  .btn-l {{ padding: 14px 24px; font-size: 16px; }}
  .btn-block {{ flex: 1; }}
  .btn-primary   {{ background: var(--colors-primarybutton_bg_active, #E96A6A); color: #fff; }}
  .btn-primary:hover:not(:disabled) {{ background: var(--colors-primarybutton_bg_hover, #D83131); }}
  .btn-secondary {{ background: transparent; color: var(--text); border: 1.5px solid var(--strokes-outline_regular, #B0B0B0); }}
  .btn-secondary:hover:not(:disabled) {{ background: var(--panel-2); }}
  .btn-tertiary  {{ background: transparent; color: var(--colors-primarybutton_bg_active, #E96A6A); text-decoration: underline; text-underline-offset: 3px; }}
  .btn-ghost     {{ background: transparent; color: var(--text-dim); }}
  .btn-ghost:hover:not(:disabled) {{ color: var(--text); background: var(--panel-2); }}
  .btn-destructive {{ background: var(--colors-tomato_red, #D93025); color: #fff; }}
  .btn-loading {{ opacity: .7; }}
  .btn-ico {{ font-weight: 700; }}
  .btn-spin {{
    width: 12px; height: 12px; border: 2px solid rgba(255,255,255,.5);
    border-top-color: #fff; border-radius: 50%; animation: btnSpin .8s linear infinite;
  }}
  @keyframes btnSpin {{ to {{ transform: rotate(360deg); }} }}

  /* Icon Button */
  .icobtn-row {{ display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }}
  .ico-btn {{
    border: 1px solid var(--border); background: var(--panel);
    border-radius: 50%; cursor: pointer; color: var(--text);
    display: inline-flex; align-items: center; justify-content: center;
    transition: background .15s, transform .05s;
  }}
  .ico-btn:hover:not(:disabled) {{ background: var(--panel-2); }}
  .ico-btn:active {{ transform: scale(.94); }}
  .ico-btn:disabled {{ opacity: .4; cursor: not-allowed; }}
  .ico-btn-m {{ width: 40px; height: 40px; font-size: 16px; }}
  .ico-btn-l {{ width: 52px; height: 52px; font-size: 20px; }}
  .ico-btn-primary {{
    background: var(--colors-primarybutton_bg_active, #E96A6A); color: #fff; border-color: transparent;
  }}
  .ico-btn-primary:hover:not(:disabled) {{ background: var(--colors-primarybutton_bg_hover, #D83131); }}

  /* Text Field */
  .tf-stack {{ display: flex; flex-direction: column; gap: 14px; width: 100%; }}
  .tf {{ display: flex; flex-direction: column; gap: 6px; }}
  .tf-label {{ font-size: 12px; font-weight: 500; color: var(--text-dim); }}
  .tf-input {{
    font: inherit; font-size: 14px; padding: 10px 12px;
    background: var(--panel); color: var(--text);
    border: 1.5px solid var(--strokes-outline_light, #E0E0E0);
    border-radius: var(--cornerradius-radius_md, 12px);
    outline: none; transition: border-color .15s;
  }}
  .tf-input:focus {{ border-color: var(--colors-primarybutton_bg_active, #E96A6A); }}
  .tf-multi {{ resize: vertical; min-height: 60px; font-family: inherit; }}
  .tf-hint {{ font-size: 11px; color: var(--text-dim); }}
  .tf-error .tf-input {{ border-color: var(--colors-tomato_red, #D93025); }}
  .tf-error .tf-hint {{ color: var(--colors-tomato_red, #D93025); }}

  /* Chip */
  .chip-grid {{ display: flex; flex-direction: column; gap: 8px; width: 100%; }}
  .chip-row {{ display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }}
  .chip-label {{ font-size: 10px; color: var(--text-dim); text-transform: uppercase; letter-spacing: .05em; min-width: 110px; }}
  .chip-row-inline {{ display: flex; gap: 6px; flex-wrap: wrap; }}
  .chip {{
    display: inline-flex; align-items: center; gap: 6px;
    padding: 5px 4px 5px 10px; font-size: 12px; font-weight: 500;
    border-radius: var(--cornerradius-radius_pill, 999px);
    border: 1.5px solid var(--strokes-outline_light, #E0E0E0);
    background: var(--panel);
    color: var(--text);
    line-height: 1;
  }}
  .chip.chip-sm {{ font-size: 11px; padding: 4px 4px 4px 9px; }}
  .chip i {{ font-style: normal; font-size: 12px; }}
  .chip .chip-ico {{
    display: inline-flex; align-items: center; justify-content: center;
    width: 18px; height: 18px; border-radius: 50%;
    font-size: 10px; font-weight: 700;
    background: var(--panel-2); color: var(--text-dim);
  }}
  .chip.chip-suggested {{ border-style: dashed; color: var(--text-dim); }}
  .chip.chip-suggested .chip-ico {{ background: var(--colors-primarybutton_bg_active, #E96A6A); color: #fff; }}
  .chip.chip-confirmed {{ background: var(--colors-primarybutton_bg_active, #E96A6A); color: #fff; border-color: transparent; }}
  .chip.chip-confirmed .chip-ico {{ background: rgba(255,255,255,.25); color: #fff; }}
  .chip.chip-added    {{ background: var(--panel-2); border-color: var(--strokes-outline_regular, #B0B0B0); }}
  .chip.chip-added .chip-ico {{ background: var(--colors-neutral_200, #E0E0E0); }}
  .chip.chip-locked   {{ background: var(--panel-2); }}
  .chip.chip-locked .chip-ico {{ background: transparent; color: var(--text-dim); font-size: 12px; }}

  /* Toggle switch */
  .tog-row {{ display: flex; gap: 20px; flex-wrap: wrap; }}
  .tog {{ display: inline-flex; align-items: center; gap: 10px; cursor: pointer; }}
  .tog input {{ display: none; }}
  .tog-slider {{
    width: 44px; height: 24px; border-radius: 999px;
    background: var(--colors-neutral_200, #E0E0E0); position: relative;
    transition: background .2s;
  }}
  .tog-slider::after {{
    content: ''; position: absolute; top: 2px; left: 2px;
    width: 20px; height: 20px; border-radius: 50%;
    background: #fff; box-shadow: 0 1px 3px rgba(0,0,0,.2);
    transition: transform .2s;
  }}
  .tog input:checked + .tog-slider {{ background: var(--colors-primarybutton_bg_active, #E96A6A); }}
  .tog input:checked + .tog-slider::after {{ transform: translateX(20px); }}
  .tog-label {{ font-size: 13px; }}

  /* Checkbox + Radio */
  .chk-stack {{ display: flex; flex-direction: column; gap: 10px; }}
  .chk {{ display: inline-flex; align-items: center; gap: 10px; cursor: pointer; font-size: 13px; }}
  .chk input {{ display: none; }}
  .chk-box {{
    width: 18px; height: 18px;
    border: 1.5px solid var(--strokes-outline_regular, #B0B0B0);
    border-radius: var(--cornerradius-radius_sm, 4px);
    display: inline-flex; align-items: center; justify-content: center;
    background: var(--panel); transition: background .15s, border-color .15s;
  }}
  .chk-radio .chk-box {{ border-radius: 50%; }}
  .chk input:checked + .chk-box {{
    background: var(--colors-primarybutton_bg_active, #E96A6A);
    border-color: var(--colors-primarybutton_bg_active, #E96A6A);
  }}
  .chk input:checked + .chk-box::after {{
    content: ''; width: 6px; height: 10px; border: solid #fff;
    border-width: 0 2px 2px 0; transform: rotate(45deg) translate(-1px,-1px);
  }}
  .chk-radio input:checked + .chk-box::after {{
    content: ''; width: 8px; height: 8px; border: 0; border-radius: 50%;
    background: #fff; transform: none;
  }}
  .chk input:disabled + .chk-box {{ opacity: .4; }}

  /* Segmented Control demo */
  .seg-demo {{ display: flex; gap: 12px; flex-wrap: wrap; align-items: center; }}

  /* Avatar */
  .avatar-row {{ display: flex; align-items: center; gap: 12px; }}
  .avatar {{
    display: inline-flex; align-items: center; justify-content: center;
    background: var(--colors-neutral_200, #E0E0E0);
    color: var(--colors-near_black, #222);
    font-weight: 600; border-radius: 50%;
  }}
  .avatar-s {{ width: 28px; height: 28px; font-size: 11px; }}
  .avatar-m {{ width: 40px; height: 40px; font-size: 14px; }}
  .avatar-l {{ width: 56px; height: 56px; font-size: 18px; }}
  .avatar-agent {{ background: var(--colors-primarybutton_bg_active, #E96A6A); color: #fff; }}

  /* Divider */
  .div-stack {{ width: 100%; display: flex; flex-direction: column; gap: 8px; font-size: 12px; color: var(--text-dim); }}
  .divider {{ border: 0; border-top: 1px solid var(--strokes-outline_light, #E0E0E0); margin: 4px 0; width: 100%; }}
  .divider-heavy {{ border-top: 2px solid var(--strokes-outline_regular, #B0B0B0); }}

  /* Search Bar + Sort Chip */
  .search-row {{ display: flex; gap: 8px; width: 100%; align-items: center; }}
  .search-bar {{
    flex: 1; display: inline-flex; align-items: center; gap: 8px;
    padding: 10px 14px;
    background: var(--colors-neutral_100, #F2F2F2);
    border: 1px solid transparent;
    border-radius: var(--cornerradius-radius_pill, 999px);
    transition: border-color .15s, background .15s;
  }}
  .search-bar:focus-within {{
    background: var(--panel);
    border-color: var(--strokes-outline_regular, #B0B0B0);
  }}
  .search-ico {{
    color: var(--text-dim); display: inline-flex; align-items: center;
  }}
  .search-bar input {{
    flex: 1; border: 0; outline: 0; background: transparent;
    font: inherit; font-size: 14px; color: var(--text);
    min-width: 0;
  }}
  .search-bar input::placeholder {{ color: var(--text-dim); }}
  /* Kill webkit search UI */
  .search-bar input::-webkit-search-decoration,
  .search-bar input::-webkit-search-cancel-button {{ -webkit-appearance: none; }}

  .sort-chip {{
    display: inline-flex; align-items: center; gap: 6px;
    padding: 10px 14px;
    background: var(--colors-neutral_100, #F2F2F2);
    color: var(--text);
    border: 1px solid transparent;
    border-radius: var(--cornerradius-radius_pill, 999px);
    font: inherit; font-size: 13px; font-weight: 600;
    cursor: pointer;
    white-space: nowrap;
    transition: background .15s, color .15s, border-color .15s;
  }}
  .sort-chip:hover {{ background: var(--colors-neutral_200, #E0E0E0); }}
  .sort-chip-active {{
    background: var(--colors-primarybutton_bg_active);
    color: #fff;
  }}
  .sort-chip-active:hover {{ background: var(--colors-primarybutton_bg_hover, #D83131); }}

  /* ==================== Property surfaces ==================== */
  .pcard {{
    background: var(--panel); border: 1px solid var(--border);
    border-radius: var(--cornerradius-radius_lg, 16px);
    width: 100%; overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,.05);
  }}
  .pcard-compact {{
    display: flex; align-items: center; gap: 12px; padding: 12px 14px;
  }}
  .pcard-body {{ flex: 1; min-width: 0; }}
  .pcard-addr {{ font-size: 15px; font-weight: 600; color: var(--text); }}
  .pcard-sub  {{ font-size: 12px; color: var(--text-dim); }}
  .pcard-icons {{ display: flex; gap: 4px; }}
  .pcat {{
    width: 26px; height: 26px; border-radius: 50%;
    background: var(--panel-2); display: inline-flex;
    align-items: center; justify-content: center; font-size: 13px;
  }}

  .pcard-expanded {{ padding: 16px; display: flex; flex-direction: column; gap: 14px; max-width: 380px; }}
  .pcard-head {{ display: flex; align-items: center; gap: 14px; }}
  .pcard-head .pcard-addr {{ font-size: 18px; }}
  .pcard-section {{ display: flex; flex-direction: column; gap: 6px; }}
  .pcard-section-label {{
    font-size: 10px; text-transform: uppercase; letter-spacing: .05em;
    color: var(--text-dim); font-weight: 600;
  }}
  .pcard-actions {{ display: flex; gap: 8px; }}
  .pcard-details {{
    background: transparent; border: 0; color: var(--text-dim);
    font: inherit; font-size: 12px; cursor: pointer;
    padding: 6px 0; align-self: flex-start;
    display: inline-flex; align-items: center; gap: 4px;
  }}
  .pcard-details:hover {{ color: var(--text); }}

  /* Imagery Carousel */
  .pimg-carousel {{ position: relative; width: 100%; border-radius: var(--cornerradius-radius_md, 12px); overflow: hidden; }}
  .pimg {{
    height: 140px; display: flex; align-items: center; justify-content: center;
    background: linear-gradient(135deg, #4a5568, #2d3748);
    color: rgba(255,255,255,.9); font-size: 13px; font-weight: 500;
    background-image:
      linear-gradient(135deg, rgba(0,0,0,0), rgba(0,0,0,.35)),
      repeating-linear-gradient(45deg, #4a7c59 0 24px, #3a6247 24px 48px);
  }}
  .pimg-lg {{ max-width: 400px; }}
  .pimg-lg .pimg {{ height: 200px; }}
  .pimg-label {{ background: rgba(0,0,0,.55); padding: 4px 10px; border-radius: 999px; font-size: 11px; }}
  .pimg-dots {{
    position: absolute; bottom: 8px; left: 50%; transform: translateX(-50%);
    display: flex; gap: 6px;
  }}
  .pimg-dots span {{
    width: 6px; height: 6px; border-radius: 50%;
    background: rgba(255,255,255,.4);
  }}
  .pimg-dots .active {{ background: #fff; }}

  /* Campaign mini + card */
  .camp-mini {{
    display: flex; align-items: center; gap: 10px;
    padding: 10px 12px; background: var(--panel-2);
    border-radius: var(--cornerradius-radius_md, 12px);
  }}
  .camp-mini > div:first-child {{ flex: 1; }}
  .camp-name {{ font-size: 13px; font-weight: 600; color: var(--text); }}
  .camp-reason {{ font-size: 11px; color: var(--text-dim); margin-top: 1px; }}
  .camp-swap {{
    background: transparent; border: 1px solid var(--strokes-outline_light, #E0E0E0);
    color: var(--text); padding: 6px 10px;
    border-radius: var(--cornerradius-radius_sm, 4px);
    cursor: pointer; font-size: 11px; font-weight: 500;
  }}
  .camp-card {{
    display: flex; flex-direction: column; gap: 12px;
    padding: 14px; background: var(--panel);
    border: 1px solid var(--border);
    border-radius: var(--cornerradius-radius_md, 12px);
    width: 100%; max-width: 340px;
  }}
  .camp-head {{ display: flex; gap: 10px; align-items: flex-start; }}
  .camp-icon {{ font-size: 22px; }}
  .camp-actions {{ display: flex; gap: 6px; }}

  /* Note composer */
  .note-composer {{
    width: 100%; max-width: 320px;
    background: var(--panel-2);
    border-radius: var(--cornerradius-radius_md, 12px);
    padding: 12px 14px;
    display: flex; flex-direction: column; gap: 10px;
  }}
  .note-prompt {{ font-size: 13px; color: var(--text-dim); }}
  .note-input {{ display: flex; gap: 8px; align-items: center; }}
  .note-input input {{
    flex: 1; padding: 10px 12px; font: inherit; font-size: 13px;
    background: var(--panel); color: var(--text);
    border: 1px solid var(--border);
    border-radius: var(--cornerradius-radius_md, 12px); outline: none;
  }}

  /* Lead added */
  .lead-added {{
    display: flex; align-items: center; gap: 12px;
    padding: 12px 14px; background: var(--panel);
    border: 1px solid var(--colors-green, #1A7F42); border-left-width: 4px;
    border-radius: var(--cornerradius-radius_md, 12px);
    max-width: 340px;
  }}
  .lead-check {{
    width: 32px; height: 32px; border-radius: 50%;
    background: var(--colors-green, #1A7F42); color: #fff;
    display: inline-flex; align-items: center; justify-content: center;
    font-weight: 700;
  }}
  .lead-title {{ font-size: 14px; font-weight: 600; color: var(--text); }}
  .lead-sub {{ font-size: 12px; color: var(--text-dim); margin-top: 2px; }}

  /* Property Card — Lead Row */
  .plead {{
    background: var(--panel); border: 1px solid var(--strokes-outline_extra_light, #F2F2F2);
    border-radius: var(--cornerradius-radius_2xl, 24px);
    padding: 16px 20px;
    display: grid; grid-template-columns: 108px 1fr auto;
    align-items: center; gap: 20px;
    box-shadow: 0 1px 2px rgba(34,34,34,.04);
    transition: box-shadow 160ms ease, border-color 160ms ease;
    cursor: pointer; width: 100%; max-width: 640px;
  }}
  .plead + .plead {{ margin-top: 12px; }}
  .plead:hover {{
    box-shadow: 0 6px 20px rgba(34,34,34,.08);
    border-color: var(--strokes-outline_light, #E0E0E0);
  }}
  .plead:focus-visible {{
    outline: 2px solid var(--colors-color_brand_default, #E96A6A);
    outline-offset: 2px;
  }}
  .plead-media {{
    width: 108px; height: 108px;
    border-radius: var(--cornerradius-radius_lg, 16px);
    overflow: hidden; background: var(--colors-neutral_100, #F2F2F2);
    flex-shrink: 0;
  }}
  .plead-media img {{
    width: 100%; height: 100%; object-fit: cover; display: block;
  }}
  .plead-media-fallback {{
    background: linear-gradient(135deg,
      var(--colors-neutral_100, #F2F2F2),
      var(--colors-neutral_200, #E0E0E0));
  }}
  .plead-body {{
    display: flex; flex-direction: column; gap: 8px; min-width: 0;
  }}
  .plead-price-row {{
    display: flex; align-items: baseline; gap: 8px;
  }}
  .plead-price {{
    font-size: var(--textsizes-section_heading_size, 24px);
    font-weight: var(--textweights-hero_heading_weight, 700);
    color: var(--colors-color_brand_default, #E96A6A);
    letter-spacing: -0.01em; line-height: 1;
  }}
  .plead-price-label {{
    font-size: var(--textsizes-body_txt_size, 14px);
    color: var(--colors-neutral_600, #717171);
    font-weight: var(--textweights-body_txt_weight, 400);
  }}
  .plead-address {{
    font-size: var(--textsizes-sub_heaidng_size, 18px);
    font-weight: var(--textweights-card_title_weight, 600);
    color: var(--colors-near_black, #222);
    line-height: 1.3; margin: 0; letter-spacing: -0.005em;
  }}
  .plead-stats {{
    display: inline-flex; align-items: center; gap: 12px;
    font-size: var(--textsizes-body_txt_size, 14px);
    color: var(--colors-neutral_600, #717171);
    margin-top: 4px;
  }}
  .plead-stats .stat {{ display: inline-flex; align-items: baseline; gap: 4px; }}
  .plead-stats .stat-value {{
    color: var(--colors-near_black, #222);
    font-weight: var(--textweights-card_title_weight, 600);
  }}
  .plead-divider {{
    width: 1px; height: 14px;
    background: var(--strokes-outline_light, #E0E0E0);
    align-self: center;
  }}
  .plead-owner {{
    display: flex; align-items: center; gap: 8px; flex-wrap: wrap;
    font-size: var(--textsizes-body_txt_size, 14px);
    color: var(--colors-neutral_600, #717171);
    margin-top: 8px; padding-top: 12px;
    border-top: 1px solid var(--strokes-outline_extra_light, #F2F2F2);
  }}
  .plead-owner-label {{ color: var(--colors-neutral_600, #717171); }}
  .plead-owner-name {{
    color: var(--colors-near_black, #222);
    font-weight: var(--textweights-card_title_weight, 600);
  }}
  .plead-owner-phone {{
    color: var(--colors-neutral_400, #B0B0B0);
    font-variant-numeric: tabular-nums;
    text-decoration: none;
  }}
  a.plead-owner-phone:hover {{
    color: var(--colors-color_brand_default, #E96A6A);
    text-decoration: underline;
  }}
  .plead-chevron {{
    color: var(--colors-neutral_400, #B0B0B0);
    align-self: center; display: inline-flex;
    align-items: center; justify-content: center; padding: 4px;
    transition: color 120ms ease, transform 120ms ease;
  }}
  .plead:hover .plead-chevron {{
    color: var(--colors-near_black, #222);
    transform: translateX(2px);
  }}
  @media (max-width: 520px) {{
    .plead {{ grid-template-columns: 88px 1fr auto; gap: 16px; padding: 12px; }}
    .plead-media {{ width: 88px; height: 88px; }}
    .plead-price {{ font-size: 20px; }}
    .plead-address {{ font-size: 16px; }}
    .plead-owner {{ font-size: 12px; }}
  }}

  /* Property Card — Hero (vertical) */
  .pfeat {{
    background: var(--panel);
    border: 1px solid var(--strokes-outline_extra_light, #F2F2F2);
    border-radius: var(--cornerradius-radius_2xl, 24px);
    padding: 12px;
    display: flex; flex-direction: column;
    box-shadow: 0 1px 2px rgba(34,34,34,.04);
    transition: box-shadow 160ms ease, border-color 160ms ease;
    cursor: pointer; width: 100%; max-width: 360px;
  }}
  .pfeat:hover {{
    box-shadow: 0 8px 24px rgba(34,34,34,.08);
    border-color: var(--strokes-outline_light, #E0E0E0);
  }}
  .pfeat:focus-visible {{
    outline: 2px solid var(--colors-color_brand_default, #E96A6A);
    outline-offset: 2px;
  }}

  /* --- Media --- */
  .pfeat-media {{
    position: relative;
    border-radius: var(--cornerradius-radius_xl, 20px);
    overflow: hidden;
    aspect-ratio: 4 / 3;
    background: var(--colors-neutral_100, #F2F2F2);
  }}
  .pfeat-media img {{
    width: 100%; height: 100%; object-fit: cover; display: block;
  }}
  .pfeat-media-fallback {{
    background: linear-gradient(135deg,
      var(--colors-neutral_100, #F2F2F2),
      var(--colors-neutral_200, #E0E0E0));
  }}

  /* Grade pill overlay (top-left) — replaces "Guest Favourite" */
  .pfeat-pill {{
    position: absolute; top: 12px; left: 12px;
    display: inline-flex; align-items: center; gap: 8px;
    padding: 6px 12px 6px 6px;
    background: var(--panel);
    border-radius: var(--cornerradius-radius_pill, 99px);
    box-shadow: 0 2px 8px rgba(34,34,34,.15);
    font-size: var(--textsizes-caption_size, 12px);
    font-weight: var(--textweights-caption_weight, 500);
    color: var(--colors-near_black, #222);
    letter-spacing: 0.02em;
  }}
  .pfeat-pill-dot {{
    width: 20px; height: 20px; border-radius: 50%;
    background: var(--gradecolors-grade_a, #D93025);
    color: var(--colors-white, #fff);
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 700; line-height: 1;
  }}
  .pfeat-pill[data-grade="B"] .pfeat-pill-dot {{ background: var(--gradecolors-grade_b, #E96A6A); }}
  .pfeat-pill[data-grade="C"] .pfeat-pill-dot {{ background: var(--gradecolors-grade_c, #E8A317); color: var(--colors-near_black, #222); }}
  .pfeat-pill[data-grade="D"] .pfeat-pill-dot {{ background: var(--gradecolors-grade_d, #B0B0B0); }}

  /* Save button (top-right) — bookmark, not heart */
  .pfeat-save {{
    position: absolute; top: 12px; right: 12px;
    width: 36px; height: 36px; border-radius: 50%;
    background: var(--panel); border: 0;
    display: inline-flex; align-items: center; justify-content: center;
    cursor: pointer; color: var(--colors-near_black, #222);
    box-shadow: 0 2px 8px rgba(34,34,34,.15);
    transition: color 120ms ease, transform 120ms ease;
  }}
  .pfeat-save:hover {{ color: var(--colors-color_brand_default, #E96A6A); }}
  .pfeat-save:active {{ transform: scale(0.94); }}
  .pfeat-save[aria-pressed="true"] {{ color: var(--colors-color_brand_default, #E96A6A); }}
  .pfeat-save i {{ line-height: 1; }}

  /* --- Body --- */
  .pfeat-body {{
    padding: 14px 8px 6px;
    display: flex; flex-direction: column; gap: 6px;
  }}
  .pfeat-title-row {{
    display: flex; align-items: baseline; justify-content: space-between; gap: 12px;
  }}
  .pfeat-title {{
    font-size: var(--textsizes-card_title_size, 20px);
    font-weight: var(--textweights-card_title_weight, 600);
    color: var(--colors-near_black, #222);
    letter-spacing: -0.01em; line-height: 1.2; margin: 0;
  }}
  .pfeat-price {{
    font-size: var(--textsizes-card_title_size, 20px);
    font-weight: var(--textweights-card_title_weight, 600);
    color: var(--colors-near_black, #222);
    white-space: nowrap; line-height: 1.2;
  }}
  .pfeat-unit {{
    font-size: var(--textsizes-caption_size, 12px);
    font-weight: var(--textweights-caption_weight, 500);
    color: var(--colors-neutral_600, #717171);
    margin-left: 2px;
  }}
  .pfeat-tag {{
    font-size: var(--textsizes-body_txt_size, 14px);
    color: var(--colors-neutral_600, #717171);
    margin: 0;
    display: -webkit-box; -webkit-line-clamp: 1; -webkit-box-orient: vertical;
    overflow: hidden;
  }}

  /* --- Stats row --- */
  .pfeat-stats {{
    display: grid; grid-template-columns: 1fr 1fr 1fr;
    align-items: center;
    padding: 14px 8px 4px;
    border-top: 1px solid var(--strokes-outline_extra_light, #F2F2F2);
    margin-top: 8px;
  }}
  .pfeat-stat {{
    display: inline-flex; align-items: center; justify-content: center;
    gap: 8px;
    font-size: var(--textsizes-body_txt_size, 14px);
    color: var(--colors-neutral_600, #717171);
    padding: 0 4px;
  }}
  .pfeat-stat + .pfeat-stat {{
    border-left: 1px solid var(--strokes-outline_extra_light, #F2F2F2);
  }}
  .pfeat-stat b {{
    color: var(--colors-near_black, #222);
    font-weight: var(--textweights-card_title_weight, 600);
  }}
  .pfeat-stat-ico {{
    color: var(--colors-neutral_600, #717171);
    display: inline-flex; align-items: center;
  }}

  /* Persistent Action Rail (showcase stage) */
  .rail-stage {{
    position: relative; width: 100%; height: 180px;
    background: var(--panel-2); border-radius: var(--cornerradius-radius_md, 12px);
    overflow: hidden;
  }}
  .rail-fake {{ padding: 14px; color: var(--text-dim); font-size: 12px; }}
  .action-rail {{
    position: absolute; top: 12px; right: 12px;
    display: flex; flex-direction: column; gap: 8px;
  }}
  .action-rail .ico-btn {{ box-shadow: 0 2px 8px rgba(0,0,0,.15); }}

  /* ==================== Framing surfaces ==================== */
  .frame-stage {{
    position: relative; width: 100%; max-width: 320px;
    height: 260px;
    background: var(--panel-2); border-radius: 20px;
    border: 1px solid var(--border);
    overflow: hidden;
  }}
  .frame-stage-tall {{ height: 320px; }}
  .frame-stage-short {{ height: 160px; }}
  .frame-content {{
    padding: 14px; color: var(--text-dim); font-size: 12px;
  }}
  .frame-orb {{ bottom: 12px !important; right: 12px !important; z-index: 4; }}

  /* Bottom sheet */
  .sheet-backdrop {{
    position: absolute; inset: 0;
    background: rgba(0,0,0,.35);
    z-index: 1;
  }}
  .bottom-sheet {{
    position: absolute; left: 0; right: 0; bottom: 0;
    background: var(--panel);
    border-top-left-radius: 20px; border-top-right-radius: 20px;
    box-shadow: 0 -4px 20px rgba(0,0,0,.15);
    z-index: 2;
    display: flex; flex-direction: column;
    padding-bottom: 8px;
  }}
  .sheet-half {{ height: 55%; }}
  .sheet-full {{ height: 90%; }}
  .sheet-peek {{ height: 22%; }}
  .sheet-handle {{
    width: 40px; height: 4px; border-radius: 2px;
    background: var(--colors-neutral_200, #E0E0E0);
    margin: 8px auto 4px;
  }}
  .sheet-body {{ padding: 12px 16px; }}

  /* Modal */
  .modal {{
    position: absolute; left: 50%; top: 50%;
    transform: translate(-50%, -50%);
    width: 84%; max-width: 260px;
    background: var(--panel);
    border-radius: var(--cornerradius-radius_lg, 16px);
    box-shadow: 0 8px 24px rgba(0,0,0,.25);
    z-index: 2;
    display: flex; flex-direction: column;
    overflow: hidden;
  }}
  .modal-head {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 14px 16px 6px;
  }}
  .modal-title {{ font-size: 15px; font-weight: 600; color: var(--text); }}
  .modal-close {{
    background: transparent; border: 0; color: var(--text-dim);
    font-size: 14px; cursor: pointer;
  }}
  .modal-body {{ padding: 4px 16px 14px; color: var(--text-dim); font-size: 12px; line-height: 1.45; }}
  .modal-foot {{
    display: flex; gap: 6px; justify-content: flex-end;
    padding: 8px 12px 12px; border-top: 1px solid var(--border);
  }}

  /* Toast */
  .toast-stack {{ display: flex; flex-direction: column; gap: 8px; width: 100%; max-width: 340px; }}
  .toast {{
    display: flex; align-items: center; gap: 10px;
    padding: 10px 14px; border-radius: var(--cornerradius-radius_md, 12px);
    background: var(--panel); border: 1px solid var(--border);
    box-shadow: 0 2px 8px rgba(0,0,0,.06);
    font-size: 13px; color: var(--text);
  }}
  .toast-ico {{
    width: 22px; height: 22px; border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    color: #fff; font-size: 12px; font-weight: 700; flex-shrink: 0;
  }}
  .toast-success .toast-ico {{ background: var(--colors-green, #1A7F42); }}
  .toast-success {{ border-left: 3px solid var(--colors-green, #1A7F42); }}
  .toast-info .toast-ico {{ background: var(--colors-blue, #1A73E8); }}
  .toast-info {{ border-left: 3px solid var(--colors-blue, #1A73E8); }}
  .toast-warning .toast-ico {{ background: var(--colors-yellow, #E8A317); color: #222; }}
  .toast-warning {{ border-left: 3px solid var(--colors-yellow, #E8A317); }}
  .toast-error .toast-ico {{ background: var(--colors-tomato_red, #D93025); }}
  .toast-error {{ border-left: 3px solid var(--colors-tomato_red, #D93025); }}

  /* Safety banner */
  .safety-banner {{
    position: absolute; top: 0; left: 0; right: 0;
    display: flex; align-items: center; justify-content: center; gap: 8px;
    padding: 8px 14px;
    background: var(--colors-primarybutton_bg_active, #E96A6A);
    color: #fff; font-size: 13px; font-weight: 600;
    z-index: 3;
  }}
  .safety-dot {{
    width: 8px; height: 8px; border-radius: 50%; background: #fff;
    animation: safetyPulse 1.6s ease-in-out infinite;
  }}
  @keyframes safetyPulse {{ 0%,100%{{opacity:.4}} 50%{{opacity:1}} }}

  /* Top app bar */
  .app-bar {{
    position: absolute; top: 0; left: 0; right: 0;
    display: flex; align-items: center; gap: 10px;
    padding: 10px 14px; height: 56px;
    background: var(--panel);
    border-bottom: 1px solid var(--strokes-outline_light, #E0E0E0);
    z-index: 2;
  }}
  .app-bar-back {{
    background: transparent; border: 0; cursor: pointer;
    font-size: 22px; color: var(--text); padding: 0 6px;
    line-height: 1;
  }}
  .app-bar-title {{
    flex: 1; font-size: 15px; font-weight: 600; color: var(--text);
  }}
  .app-bar-action {{ width: 36px; height: 36px; font-size: 14px; }}

  /* ==================== Design page ==================== */
  .design-intro {{ color: var(--text-dim); font-size: 14px; margin: 0 0 32px; max-width: 720px; }}

  .phone-row {{
    display: flex; gap: 20px; align-items: flex-start; overflow-x: auto;
    padding-bottom: 24px;
  }}
  .phone-col {{ display: flex; flex-direction: column; gap: 10px; flex-shrink: 0; width: 320px; }}
  .phone-label {{
    font-size: 11px; font-weight: 600; color: var(--text-dim);
    text-transform: uppercase; letter-spacing: .08em;
  }}
  .phone-caption {{ font-size: 12px; color: var(--text-dim); line-height: 1.45; max-width: 320px; }}
  .flow-arrow {{
    color: var(--text-dim); align-self: center; flex-shrink: 0;
    padding-top: 260px;
  }}

  .phone {{
    position: relative;
    width: 400px; height: 800px;
    background: var(--bg);
    border-radius: 28px;
    overflow: hidden;
    border: 1px solid var(--border);
    box-shadow:
      0 0 0 1px rgba(0,0,0,.02),
      0 0 24px 4px rgba(0,0,0,.06),
      0 0 64px 8px rgba(0,0,0,.08);
  }}
  .phone-statusbar {{
    position: absolute; top: 18px; left: 0; right: 0;
    display: flex; justify-content: space-between; align-items: center;
    padding: 0 24px; height: 14px;
    color: var(--text); font-size: 11px; font-weight: 600;
    z-index: 21;
  }}
  .phone-signal {{
    width: 26px; height: 10px;
    background:
      linear-gradient(90deg, currentColor 0, currentColor 20%, transparent 20%, transparent 27%,
                            currentColor 27%, currentColor 47%, transparent 47%, transparent 54%,
                            currentColor 54%, currentColor 74%, transparent 74%, transparent 81%,
                            currentColor 81%);
    opacity: .85;
  }}
  .phone-screen {{
    position: absolute; inset: 0;
    background: var(--bg);
    border-radius: inherit;
    overflow: hidden;
    display: flex; flex-direction: column;
  }}
  .phone-screen > *:first-child {{ padding-top: 36px; }}

  /* ---- Screen: Home (redesigned) ---- */
  .scr-home {{
    flex: 1; display: flex; flex-direction: column;
    background: transparent;
    padding-top: 0 !important;
  }}
  .proto-screen[data-screen="home"] {{
    padding-top: 0 !important;
    background: linear-gradient(
      180deg,
      color-mix(in srgb, var(--colors-primarybutton_bg_active) 10%, var(--bg)) 0%,
      var(--bg) 320px
    );
  }}
  .home-header {{
    padding: 52px 16px 20px;
    background: transparent;
    display: flex; flex-direction: column; gap: 14px;
  }}
  .zip-pill {{
    align-self: flex-start;
    display: inline-flex; align-items: center; gap: 5px;
    padding: 0;
    background: transparent;
    color: var(--colors-red_600);
    font-size: 12px; font-weight: 700;
  }}
  .zip-pill i, .zip-pill span {{ color: var(--colors-red_600); }}
  .home-hi {{
    margin: 0;
    font-size: 22px; font-weight: 400; line-height: 1.25;
    color: var(--text);
    letter-spacing: -0.01em;
    text-wrap: balance;
  }}
  .home-hi b {{ font-weight: 700; }}

  .home-callout {{
    display: flex; align-items: flex-start; gap: 14px;
    padding: 20px;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: var(--cornerradius-radius_lg, 16px);
    box-shadow: 0 2px 8px rgba(0,0,0,.04);
  }}
  .home-callout-num {{
    font-size: 34px; font-weight: 700; line-height: 0.85;
    color: var(--colors-primarybutton_bg_active);
    letter-spacing: -0.02em;
    margin-top: 2px;
  }}
  .home-callout-title {{ font-size: 14px; font-weight: 600; color: var(--text); }}
  .home-callout-sub   {{ font-size: 12px; color: var(--text-dim); margin-top: 2px; }}

  .home-recap {{
    display: inline-flex; align-items: center; gap: 8px;
    padding: 8px 12px;
    align-self: flex-start;
    background: color-mix(in srgb, var(--colors-green) 10%, transparent);
    color: color-mix(in srgb, var(--colors-green) 90%, var(--text));
    border-radius: var(--cornerradius-radius_pill, 999px);
    font-size: 12px; font-weight: 500;
  }}
  .recap-dot {{
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--colors-green);
  }}

  /* Home map (real Leaflet map surface) */
  .home-map {{
    position: relative; flex: 1; min-height: 0;
    margin: 0 16px 12px;
    overflow: hidden;
    border-radius: var(--cornerradius-radius_sm, 8px);
    background: #f2efe9;
    border: 1px solid var(--border);
    z-index: 1;
  }}
  #home-real-map {{
    position: absolute; inset: 0; z-index: 1;
  }}
  .home-map .map-zone-label {{ z-index: 5; }}
  .home-map .map-tile {{
    position: absolute; inset: 0;
    background-image:
      linear-gradient(90deg, rgba(0,0,0,.06) 1px, transparent 1px),
      linear-gradient(rgba(0,0,0,.06) 1px, transparent 1px);
    background-size: 32px 32px;
    opacity: .8;
  }}
  .map-zone {{
    position: absolute; top: 18%; left: 10%; right: 12%; bottom: 22%;
    border: 1.5px dashed color-mix(in srgb, var(--colors-primarybutton_bg_active) 60%, transparent);
    background: color-mix(in srgb, var(--colors-primarybutton_bg_active) 5%, transparent);
    border-radius: var(--cornerradius-radius_md, 12px);
  }}
  .map-zone-label {{
    position: absolute; top: 10px; left: 10px;
    background: var(--panel);
    color: var(--text);
    padding: 5px 10px;
    border-radius: var(--cornerradius-radius_pill, 999px);
    font-size: 11px; font-weight: 600;
    box-shadow: 0 1px 3px rgba(0,0,0,.15);
    display: inline-flex; align-items: center; gap: 5px;
    border: 0; cursor: pointer; font-family: inherit;
    transition: transform .12s ease-out, box-shadow .12s ease-out;
  }}
  .map-zone-label:hover {{ box-shadow: 0 2px 6px rgba(0,0,0,.2); transform: translateY(-1px); }}
  .map-zone-label:active {{ transform: translateY(0); }}
  .map-zone-label::before {{
    content: '';
    width: 6px; height: 6px; border-radius: 50%;
    background: var(--colors-primarybutton_bg_active);
  }}

  /* Properties panel — replaces nav when zone chip is tapped */
  .home-properties-panel {{
    display: none;
    position: relative;
    z-index: 5;
    flex: 0 0 auto;
    flex-direction: column;
    background: var(--panel);
    border-top: 1px solid var(--border);
    border-top-left-radius: var(--cornerradius-radius_lg, 16px);
    border-top-right-radius: var(--cornerradius-radius_lg, 16px);
    box-shadow: 0 -8px 24px rgba(0,0,0,.08);
    padding-bottom: env(safe-area-inset-bottom, 0px);
    /* header (~62px) + 3 rows (~62px each) + list padding (~18px) ≈ 3-row view */
    height: 266px;
    overflow: hidden;
  }}
  .scr-home.properties-open .home-header {{ display: none; }}
  .scr-home.properties-open .home-nav {{ display: none; }}
  .scr-home.properties-open .home-properties-panel {{ display: flex; }}
  .scr-home.properties-open .home-map {{ margin-top: 44px; }}

  .properties-panel-head {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 14px 16px 10px;
    border-bottom: 1px solid var(--border);
  }}
  .properties-panel-title {{
    display: flex; flex-direction: column; gap: 2px; min-width: 0;
  }}
  .properties-panel-title-main {{
    display: inline-flex; align-items: center; gap: 6px;
    font-size: 15px; font-weight: 700; color: var(--text);
  }}
  .properties-panel-title-main::before {{
    content: '';
    width: 7px; height: 7px; border-radius: 50%;
    background: var(--colors-primarybutton_bg_active);
  }}
  .properties-panel-sub {{
    font-size: 11px; color: var(--text-dim); font-weight: 500;
  }}
  .properties-close {{
    width: 32px; height: 32px; border-radius: 50%;
    background: var(--panel-2); border: 0; cursor: pointer;
    display: inline-flex; align-items: center; justify-content: center;
    color: var(--text); flex-shrink: 0;
    transition: background .12s;
  }}
  .properties-close:hover {{ background: var(--colors-neutral_200, #E0E0E0); }}

  .properties-panel-list {{
    flex: 1; overflow-y: auto;
    padding: 6px 12px 12px;
    display: flex; flex-direction: column;
    -webkit-overflow-scrolling: touch;
  }}
  .properties-panel-list::-webkit-scrollbar {{ width: 4px; }}
  .properties-panel-list::-webkit-scrollbar-thumb {{
    background: var(--colors-neutral_200, #E0E0E0); border-radius: 2px;
  }}
  .prop-row {{
    display: flex; align-items: center; gap: 12px;
    padding: 12px 6px;
    border-bottom: 1px solid var(--border);
    cursor: pointer;
    transition: background .1s;
  }}
  .prop-row:last-child {{ border-bottom: 0; }}
  .prop-row:hover {{ background: var(--panel-2); }}
  .prop-row-body {{ flex: 1; min-width: 0; }}
  .prop-row-addr-row {{
    display: flex; align-items: center; gap: 6px; min-width: 0;
  }}
  .prop-row-addr {{
    font-size: 14px; font-weight: 600; color: var(--text);
    white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    min-width: 0;
  }}
  .prop-row-meta {{
    font-size: 11px; color: var(--text-dim); margin-top: 2px;
  }}
  .prop-row-chev {{
    color: var(--text-dim); flex-shrink: 0;
  }}
  .prop-row-thumb {{
    flex: 0 0 auto;
    width: 40px; height: 40px; border-radius: 50%; overflow: hidden;
    background-color: #4a7c59;
    background-image:
      linear-gradient(135deg, rgba(0,0,0,0), rgba(0,0,0,.28)),
      repeating-linear-gradient(45deg, #4a7c59 0 10px, #3a6247 10px 20px);
    background-size: cover; background-position: center;
  }}

  /* Bottom nav with elevated orb */
  .home-nav {{
    position: relative;
    z-index: 5;
    display: grid;
    grid-template-columns: 1fr 1fr auto 1fr 1fr;
    align-items: center;
    padding: 10px 16px calc(10px + env(safe-area-inset-bottom, 0px));
    background: var(--panel);
    border-top: 1px solid var(--border);
    box-shadow: 0 -4px 20px rgba(0,0,0,.04);
  }}
  .home-nav-orb-slot {{ width: 68px; }}
  .home-nav-btn {{
    background: transparent; border: 0; cursor: pointer;
    display: inline-flex; flex-direction: column; align-items: center; gap: 3px;
    color: var(--text-dim); font: inherit; font-size: 10px; font-weight: 500;
    padding: 6px 4px;
  }}
  .home-nav-btn.active {{ color: var(--colors-primarybutton_bg_active); }}
  .home-nav-btn:hover {{ color: var(--text); }}
  .home-nav-btn.active:hover {{ color: var(--colors-primarybutton_bg_active); }}

  .home-nav-orb {{
    position: absolute;
    left: 50%; top: -22px; transform: translateX(-50%);
    z-index: 10;
    width: 64px; height: 64px; border-radius: 50%;
    background: radial-gradient(circle at 30% 30%, #ff8a8a, var(--colors-primarybutton_bg_active) 60%, var(--colors-red_800));
    border: 0; cursor: pointer;
    color: #fff;
    box-shadow: 0 6px 22px color-mix(in srgb, var(--colors-primarybutton_bg_active) 45%, transparent),
                inset 0 -3px 8px rgba(0,0,0,.15);
    display: inline-flex; align-items: center; justify-content: center;
    transition: transform .18s ease-out, box-shadow .2s;
  }}
  .home-nav-orb::after {{
    content: '';
    position: absolute; inset: -6px; border-radius: 50%;
    border: 2px solid color-mix(in srgb, var(--colors-primarybutton_bg_active) 40%, transparent);
    animation: orbPulse 2.2s ease-out infinite;
    pointer-events: none;
  }}
  .home-nav-orb:hover {{
    transform: translateX(-50%) scale(1.05);
    box-shadow: 0 8px 28px color-mix(in srgb, var(--colors-primarybutton_bg_active) 60%, transparent),
                inset 0 -3px 8px rgba(0,0,0,.15);
  }}
  .home-nav-orb:active {{ transform: translateX(-50%) scale(.96); }}

  /* ---- Screen: Conversation ---- */
  .scr-convo {{ display: flex; flex-direction: column; flex: 1; }}

  /* Conversation v2 (streaming transcript) */
  .scr-convo-v2 {{
    position: relative; padding: 0 !important;
    background:
      radial-gradient(ellipse 120% 60% at 50% 0%,
        color-mix(in srgb, var(--colors-primarybutton_bg_active) 10%, transparent) 0%,
        transparent 60%),
      var(--bg);
  }}
  .convo-close {{
    position: absolute; top: 50px; right: 16px; z-index: 20;
    background: transparent; border: 0; cursor: pointer;
    color: var(--text-dim);
    width: 40px; height: 40px; border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
  }}
  .convo-close:hover {{ background: var(--panel-2); color: var(--text); }}
  .convo-camera {{
    position: absolute; top: 50px; left: 16px; z-index: 20;
    background: var(--colors-neutral_100, #F2F2F2); border: 0; cursor: pointer;
    color: var(--text-dim);
    width: 40px; height: 40px; border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
  }}
  .convo-camera:hover {{ background: var(--panel-2); color: var(--text); }}
  .convo-transcript {{
    flex: 1; min-height: 0;
    padding: 20px 24px 24px;
    display: flex; flex-direction: column; justify-content: flex-end;
    gap: 12px;
    -webkit-mask-image: linear-gradient(180deg, transparent 0%, black 14%, black 100%);
            mask-image: linear-gradient(180deg, transparent 0%, black 14%, black 100%);
    overflow: hidden;
  }}
  .convo-line {{
    font-family: var(--fontfamily-font_family), system-ui, sans-serif;
    color: var(--text);
    font-size: 24px; font-weight: 600; line-height: 1.25;
    letter-spacing: -0.015em;
    opacity: 0; transform: translateY(12px);
    transition: opacity .4s ease-out, transform .4s ease-out, font-size .3s;
  }}
  .convo-line.enter {{ opacity: 1; transform: none; }}
  .convo-line.driver {{ color: var(--colors-primarybutton_bg_active); }}
  /* Aging: older lines shrink slightly and keep readable opacity */
  .convo-line.age-1 {{ opacity: 0.78; font-size: 22px; }}
  .convo-line.age-2 {{ opacity: 0.58; font-size: 20px; }}
  .convo-line.age-3 {{ opacity: 0.40; font-size: 19px; }}
  .convo-line.age-4 {{ opacity: 0.24; font-size: 18px; }}

  .convo-foot {{
    padding: 16px 16px calc(28px + env(safe-area-inset-bottom, 0px));
    display: flex; flex-direction: column; align-items: center; gap: 14px;
  }}
  .convo-status {{
    font-size: 11px; font-weight: 700; letter-spacing: 0.14em;
    color: var(--text-dim); text-transform: uppercase;
  }}
  .convo-orb-btn {{
    background: transparent; border: 0; padding: 0; cursor: pointer;
    display: inline-flex; align-items: center; justify-content: center;
    transition: transform .18s ease-out;
  }}
  .convo-orb-btn:hover {{ transform: scale(1.04); }}
  .convo-orb-btn:active {{ transform: scale(.96); }}
  .convo-voice-orb {{ width: 112px !important; height: 112px !important; }}
  .convo-voice-orb .orb-core {{ inset: 20%; }}
  .convo-voice-orb .orb-ring {{ inset: 0; }}
  .convo-voice-orb .orb-ring-2 {{ inset: 8%; }}

  /* ---- Screen: In-drive ---- */
  .scr-drive {{ position: relative; display: flex; flex-direction: column; flex: 1; padding-top: 0 !important; }}
  .scr-drive .safety-banner {{ position: relative; margin-top: 36px; z-index: 3; }}
  .scr-map {{
    position: relative; flex: 1;
    background:
      linear-gradient(135deg, #dbe8dd 0%, #c7dbc9 40%, #b9d0bc 100%);
    overflow: hidden;
  }}
  .map-tile {{
    position: absolute; inset: 0;
    background-image:
      linear-gradient(90deg, rgba(0,0,0,.06) 1px, transparent 1px),
      linear-gradient(rgba(0,0,0,.06) 1px, transparent 1px);
    background-size: 28px 28px;
    opacity: .8;
  }}
  .map-pin {{
    position: absolute; width: 22px; height: 22px; border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    font-weight: 700; font-size: 11px; color: #fff;
    box-shadow: 0 2px 6px rgba(0,0,0,.25);
    transform: translate(-50%,-50%);
  }}
  .map-pin-a {{ background: var(--gradecolors-grade_a, #D93025); }}
  .map-pin-b {{ background: var(--gradecolors-grade_b, #E96A6A); }}
  .map-pin-c {{ background: var(--gradecolors-grade_c, #E8A317); color: #222; }}
  .map-you {{
    position: absolute; top: 78%; left: 45%; transform: translate(-50%,-50%);
    width: 16px; height: 16px; border-radius: 50%; background: var(--colors-blue, #1A73E8);
    box-shadow: 0 0 0 5px rgba(26,115,232,.25), 0 0 0 12px rgba(26,115,232,.12);
  }}
  .nudge-inline {{
    position: absolute; left: 16px; right: 16px; bottom: 92px; z-index: 4;
    background: var(--panel); box-shadow: 0 4px 20px rgba(0,0,0,.15);
  }}
  .drive-progress {{
    background: var(--panel); border-top: 1px solid var(--border);
    padding: 14px 16px 20px;
  }}

  /* ---- Screen: Property stop ---- */
  .scr-stop {{ display: flex; flex-direction: column; flex: 1; padding-top: 0 !important; }}
  .scr-stop .app-bar {{ margin-top: 36px; height: auto !important; }}
  .scr-stop-body {{ flex: 1; overflow-y: auto; padding: 14px 16px 100px; }}

  /* ==================== Interactive prototype ==================== */
  .design-head {{
    display: flex; justify-content: space-between; align-items: flex-end;
    flex-wrap: wrap; gap: 20px; margin-bottom: 24px;
  }}
  .proto-nav {{
    display: inline-flex; background: var(--panel-2);
    border: 1px solid var(--border);
    border-radius: 999px; padding: 4px; overflow: hidden;
  }}
  .proto-nav-btn {{
    background: transparent; color: var(--text-dim); border: 0;
    padding: 6px 14px; font: inherit; font-size: 12px; font-weight: 600;
    cursor: pointer; border-radius: 999px; white-space: nowrap;
  }}
  .proto-nav-btn:hover:not(.active) {{ color: var(--text); }}
  .proto-nav-btn.active {{ background: var(--accent); color: #fff; }}

  .proto-stage {{
    display: flex; flex-direction: column; align-items: center; gap: 12px;
    padding: 0;
  }}
  .design-page {{ padding: 0; margin-top: 28px; }}
  .proto-hint {{
    color: var(--text-dim); font-size: 12px; margin-top: 8px;
    max-width: 320px; line-height: 1.5;
  }}

  .proto-phone .phone-screen {{
    position: absolute; inset: 0; overflow: hidden;
  }}
  .proto-screens {{ position: relative; }}
  .proto-screen {{
    position: absolute; inset: 0;
    display: none; flex-direction: column;
    background: var(--bg);
    opacity: 0; transition: opacity .2s;
  }}
  .proto-screen.active {{ display: flex; opacity: 1; }}
  .proto-screen > *:first-child {{ padding-top: 46px; }}
  .proto-screen .scr-home {{ height: 100%; }}
  .proto-screen .scr-convo {{ height: 100%; }}
  .proto-screen .scr-drive {{ height: 100%; }}
  .proto-screen .scr-stop {{ height: 100%; }}
  .proto-screen .scr-added {{ height: 100%; padding: 60px 20px 24px; display: flex; flex-direction: column; gap: 24px; }}
  .proto-screen .scr-listing {{ height: 100%; }}
  .proto-screen .scr-details {{ height: 100%; padding-top: 0 !important; }}

  /* ---- Screen: Listing (route + secured) ---- */
  .scr-listing {{
    flex: 1; display: flex; flex-direction: column;
    background: transparent;
    padding-top: 0 !important;
  }}
  .listing-header {{
    padding: 52px 16px 12px;
  }}
  .listing-title-row {{
    display: flex; align-items: flex-start; justify-content: space-between; gap: 12px;
  }}
  .listing-title {{
    font-size: 22px; font-weight: 700; letter-spacing: -0.01em;
    color: var(--text);
  }}
  .listing-sub {{
    font-size: 12px; color: var(--text-dim); margin-top: 4px;
  }}
  .listing-summary {{
    display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px;
    margin: 4px 16px 12px;
    padding: 12px;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: var(--cornerradius-radius_lg, 16px);
  }}
  .listing-summary-item {{
    display: flex; flex-direction: column; align-items: center; gap: 2px;
    text-align: center;
  }}
  .listing-summary-num {{
    font-size: 15px; font-weight: 700; color: var(--text);
    letter-spacing: -0.01em; font-variant-numeric: tabular-nums;
  }}
  .listing-summary-label {{
    font-size: 10px; color: var(--text-dim);
    text-transform: uppercase; letter-spacing: 0.04em;
  }}
  .listing-body {{
    flex: 1 1 0;
    min-height: 0;
    overflow-y: auto;
    -webkit-overflow-scrolling: touch;
    padding: 4px 16px 8px;
    display: flex; flex-direction: column; gap: 8px;
  }}
  .listing-filters {{
    display: flex; align-items: center; gap: 8px;
    overflow-x: auto;
    scrollbar-width: none;
    flex: 0 0 auto;
  }}
  .listing-filters::-webkit-scrollbar {{ display: none; }}
  .listing-filters .sort-chip {{
    flex: 0 0 auto;
    padding: 8px 14px;
    font-size: 12px;
  }}

  /* ---- Listing search row + filter dropdown ---- */
  .listing-search-row {{
    position: relative;
    margin-top: 12px;
    align-items: stretch;
    width: 100%;
  }}
  .listing-search-row .search-bar {{
    flex: 1 1 auto;
    width: 100%;
    min-width: 0;
  }}
  .listing-filter-btn {{
    position: relative;
    flex: 0 0 auto;
    width: 40px; height: 40px;
    border-radius: 999px;
    display: inline-flex; align-items: center; justify-content: center;
    background: var(--panel);
    border: 1px solid var(--border);
    color: var(--text-dim);
    cursor: pointer;
    transition: background .15s, color .15s, border-color .15s;
  }}
  .listing-filter-btn:hover {{ color: var(--text); background: var(--panel-2); }}
  .listing-filter-btn.has-active {{
    color: var(--colors-primarybutton_bg_active);
    border-color: color-mix(in srgb, var(--colors-primarybutton_bg_active) 40%, var(--border));
    background: color-mix(in srgb, var(--colors-primarybutton_bg_active) 8%, var(--panel));
  }}
  .listing-filter-btn[aria-expanded="true"] {{
    color: var(--colors-primarybutton_bg_active);
    border-color: color-mix(in srgb, var(--colors-primarybutton_bg_active) 55%, transparent);
  }}
  .listing-filter-count {{
    position: absolute; top: -4px; right: -4px;
    min-width: 16px; height: 16px; padding: 0 4px;
    border-radius: 999px;
    background: var(--colors-primarybutton_bg_active);
    color: #fff;
    font-size: 10px; font-weight: 700; line-height: 16px;
    text-align: center;
    box-shadow: 0 0 0 2px var(--panel);
  }}

  /* Overlay dropdown — sits absolutely under the search row, does NOT push the list */
  .filter-dd {{
    position: absolute;
    top: calc(100% + 8px);
    left: 0; right: 0;
    z-index: 40;
    padding: 6px;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: var(--cornerradius-radius_lg, 16px);
    box-shadow: 0 12px 32px rgba(0,0,0,.12), 0 2px 6px rgba(0,0,0,.06);
    display: flex; flex-direction: column;
    max-height: calc(100vh - 200px);
    overflow-y: auto;
  }}
  .filter-dd[hidden] {{ display: none; }}
  .filter-dd-group {{
    display: flex; flex-direction: column;
    padding: 4px 4px 8px;
  }}
  .filter-dd-group + .filter-dd-group {{
    border-top: 1px solid var(--border);
    margin-top: 2px;
    padding-top: 8px;
  }}
  .filter-dd-title {{
    padding: 6px 10px 8px;
    font-size: 11px; color: var(--text-dim);
    text-transform: uppercase; letter-spacing: 0.06em;
    font-weight: 600;
  }}
  .filter-dd-list {{
    display: flex; flex-direction: column;
  }}
  .filter-dd-row {{
    display: inline-flex; align-items: center; gap: 12px;
    padding: 10px 10px;
    background: transparent;
    border: 0;
    border-radius: 10px;
    cursor: pointer;
    font: inherit;
    color: var(--text);
    text-align: left;
    transition: background .12s;
  }}
  .filter-dd-row:hover {{ background: var(--panel-2); }}
  .filter-dd-row .filter-dd-label {{
    flex: 1;
    font-size: 15px; font-weight: 500;
  }}
  .filter-dd-check {{
    flex: 0 0 auto;
    width: 22px; height: 22px; border-radius: 6px;
    display: inline-flex; align-items: center; justify-content: center;
    background: transparent;
    border: 1.5px solid var(--border);
    color: transparent;
    transition: background .12s, border-color .12s, color .12s;
  }}
  .filter-dd-row.is-active .filter-dd-check {{
    background: var(--colors-green, #1A7F42);
    border-color: var(--colors-green, #1A7F42);
    color: #fff;
  }}
  .filter-dd-sep {{
    height: 1px;
    background: var(--border);
    margin: 2px 4px;
  }}
  .filter-dd-actions {{
    display: flex; justify-content: space-between; align-items: center;
    padding: 8px 6px 4px;
    margin-top: 2px;
    border-top: 1px solid var(--border);
    gap: 8px;
  }}
  .filter-dd-actions .btn {{ min-width: 0; }}
  .route-row-icon {{
    flex: 0 0 auto;
    width: 40px; height: 40px; border-radius: 10px;
    display: inline-flex; align-items: center; justify-content: center;
    color: var(--colors-primarybutton_bg_active, #D93131);
    background: color-mix(in srgb, var(--colors-primarybutton_bg_active, #D93131) 10%, transparent);
  }}
  .listing-empty {{
    padding: 24px 12px;
    text-align: center;
    font-size: 13px;
    color: var(--text-dim);
    background: var(--panel);
    border: 1px dashed var(--border);
    border-radius: var(--cornerradius-radius_lg, 16px);
  }}
  .listing-section-label {{
    font-size: 11px; color: var(--text-dim);
    text-transform: uppercase; letter-spacing: 0.06em;
    padding: 4px 2px;
  }}
  .listing-list {{
    flex: 0 0 auto;
    display: flex; flex-direction: column;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: var(--cornerradius-radius_lg, 16px);
    overflow: hidden;
  }}
  .listing-row {{
    display: flex; align-items: center; gap: 12px;
    padding: 12px;
    border-bottom: 1px solid var(--border);
    cursor: pointer;
    transition: background .1s;
  }}
  .listing-row:last-child {{ border-bottom: 0; }}
  .listing-row:hover {{ background: var(--panel-2); }}
  .listing-row[hidden] {{ display: none; }}
  .listing-row-index {{
    flex: 0 0 auto;
    width: 22px; height: 22px; border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 700;
    color: var(--colors-primarybutton_bg_active);
    background: color-mix(in srgb, var(--colors-primarybutton_bg_active) 12%, transparent);
  }}
  .listing-row-thumb-sq {{
    border-radius: 50% !important;
  }}
  .listing-row .prop-row-body {{ flex: 1; min-width: 0; }}
  .listing-row .prop-row-addr-row {{
    display: flex; align-items: center; gap: 6px;
  }}
  .listing-row-badge {{
    font-size: 9px; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.05em;
    padding: 2px 6px; border-radius: 999px;
    color: var(--colors-primarybutton_bg_active);
    background: color-mix(in srgb, var(--colors-primarybutton_bg_active) 12%, transparent);
  }}
  .listing-row-foot {{
    margin-top: 4px;
    display: flex; align-items: center; gap: 8px;
    font-size: 11px;
  }}
  .listing-row-chip {{
    font-size: 10px; font-weight: 600;
    padding: 2px 8px; border-radius: 999px;
    color: var(--text);
    background: var(--panel-2);
    border: 1px solid var(--border);
  }}
  .listing-row-time {{
    color: var(--text-dim);
    font-variant-numeric: tabular-nums;
  }}
  .listing-cta {{
    margin-top: 4px;
  }}

  /* ---- Screen: Property Details ---- */
  .scr-details {{
    display: flex; flex-direction: column; flex: 1;
    background: var(--bg);
  }}
  .scr-details .app-bar {{ margin-top: 36px; height: auto !important; }}
  .details-body {{
    flex: 1; overflow-y: auto;
    padding: 12px 16px 32px;
    display: flex; flex-direction: column; gap: 16px;
  }}
  .details-carousel {{
    position: relative;
    flex: 0 0 auto;
    height: 200px;
    min-height: 200px;
    width: 100%;
    border-radius: var(--cornerradius-radius_lg, 16px);
    overflow: hidden;
    background: var(--panel-2);
    isolation: isolate;
  }}
  .details-carousel-track {{
    display: flex;
    height: 100%;
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    scroll-behavior: smooth;
    scrollbar-width: none;
    -webkit-overflow-scrolling: touch;
  }}
  .details-carousel-track::-webkit-scrollbar {{ display: none; }}
  .details-carousel-slide {{
    flex: 0 0 100%;
    scroll-snap-align: center;
    scroll-snap-stop: always;
    position: relative;
    height: 100%;
  }}
  .details-carousel-slide .pimg {{
    width: 100%; height: 100%;
    border-radius: 0;
  }}
  .pimg-photo {{
    background-color: #4a5568 !important;
    background-size: cover !important;
    background-position: center !important;
    background-repeat: no-repeat !important;
  }}
  .pimg-street {{
    background-image:
      linear-gradient(160deg, rgba(0,0,0,.15), rgba(0,0,0,.55)),
      linear-gradient(180deg, #7a9ec0 0%, #7a9ec0 55%, #6b8b6f 55%, #6b8b6f 68%, #3e3a36 68%, #4a463f 100%) !important;
  }}
  .pimg-yard {{
    background-image:
      linear-gradient(180deg, rgba(0,0,0,.05), rgba(0,0,0,.45)),
      repeating-linear-gradient(65deg, #5f7a3d 0 8px, #4a6432 8px 16px, #6b8946 16px 24px) !important;
  }}
  .pimg-roof {{
    background-image:
      linear-gradient(180deg, rgba(0,0,0,.1), rgba(0,0,0,.5)),
      repeating-linear-gradient(90deg, #6b4a3a 0 20px, #4a3628 20px 40px),
      linear-gradient(180deg, #7fa0c4 0%, #7fa0c4 30%, #6b4a3a 30%) !important;
  }}
  .details-hero-badge {{
    position: absolute; top: 10px; left: 10px;
    padding: 4px 10px; border-radius: 999px;
    background: rgba(0,0,0,0.55);
    backdrop-filter: blur(6px);
    z-index: 2;
    pointer-events: none;
  }}
  .details-hero-badge .pcard-grade-badge {{
    color: #fff !important;
    font-size: 13px; font-weight: 700;
  }}
  .details-carousel-btn {{
    position: absolute; top: 50%; transform: translateY(-50%);
    width: 30px; height: 30px; border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    background: rgba(0,0,0,0.45);
    backdrop-filter: blur(6px);
    color: #fff;
    border: 0; cursor: pointer;
    z-index: 2;
    transition: opacity .15s, background .15s;
  }}
  .details-carousel-btn:hover {{ background: rgba(0,0,0,0.65); }}
  .details-carousel-prev {{ left: 8px; }}
  .details-carousel-next {{ right: 8px; }}
  .details-carousel-btn[hidden] {{ display: none; }}
  .details-carousel-count {{
    position: absolute; top: 10px; right: 10px;
    padding: 4px 10px; border-radius: 999px;
    background: rgba(0,0,0,0.55);
    backdrop-filter: blur(6px);
    color: #fff;
    font-size: 11px; font-weight: 600;
    font-variant-numeric: tabular-nums;
    z-index: 2;
    pointer-events: none;
  }}
  .details-hero-dots {{
    position: absolute; bottom: 10px; left: 50%; transform: translateX(-50%);
    display: flex; gap: 5px;
    z-index: 2;
  }}
  .details-hero-dots span {{
    width: 6px; height: 6px; border-radius: 50%;
    background: rgba(255,255,255,0.5);
    cursor: pointer;
    transition: width .18s ease, background .18s ease;
    border: 0;
  }}
  .details-hero-dots span.active {{
    background: #fff;
    width: 16px; border-radius: 3px;
  }}
  .details-head {{
    display: flex; flex-direction: column; gap: 4px;
  }}
  .details-addr {{
    font-size: 20px; font-weight: 700; letter-spacing: -0.01em;
    color: var(--text);
  }}
  .details-sub {{
    font-size: 12px; color: var(--text-dim);
  }}
  .details-stats {{
    flex: 0 0 auto;
    display: flex; flex-direction: column;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: var(--cornerradius-radius_lg, 16px);
    overflow: hidden;
  }}
  .dstat-money-row {{
    display: flex; align-items: center;
    padding: 14px 16px;
    gap: 16px;
  }}
  .dstat-money {{
    flex: 1 1 0;
    display: flex; flex-direction: column; gap: 4px;
    min-width: 0;
  }}
  .dstat-money + .dstat-money-divider + .dstat-money {{ align-items: flex-start; }}
  .dstat-money-label {{
    font-size: 10px; color: var(--text-dim);
    text-transform: uppercase; letter-spacing: 0.06em; font-weight: 600;
  }}
  .dstat-money-value {{
    display: inline-flex; align-items: center; gap: 8px;
  }}
  .dstat-money-num {{
    font-size: 20px; font-weight: 700; color: var(--text);
    letter-spacing: -0.02em; font-variant-numeric: tabular-nums;
    line-height: 1.05;
  }}
  .dstat-money-delta {{
    display: inline-flex; align-items: center; gap: 3px;
    font-size: 10px; font-weight: 700;
    color: #1A7F42;
    background: rgba(26, 127, 66, 0.12);
    padding: 2px 6px; border-radius: 999px;
    white-space: nowrap;
  }}
  .dstat-money-divider {{
    width: 1px; align-self: stretch;
    background: var(--border);
    margin: 4px 0;
  }}
  .dstat-specs {{
    display: grid; grid-template-columns: repeat(3, 1fr);
    border-top: 1px solid var(--border);
    background: var(--panel-2);
  }}
  .dspec {{
    display: inline-flex; align-items: center; justify-content: center;
    gap: 6px;
    padding: 10px 6px;
    font-size: 12px; color: var(--text-dim);
    border-left: 1px solid var(--border);
  }}
  .dspec:first-child {{ border-left: 0; }}
  .dspec b {{ color: var(--text); font-weight: 700; font-variant-numeric: tabular-nums; }}
  .dspec i {{ color: var(--text-dim); }}
  .details-section {{
    display: flex; flex-direction: column; gap: 8px;
  }}
  .details-section-label {{
    font-size: 11px; color: var(--text-dim);
    text-transform: uppercase; letter-spacing: 0.06em;
  }}
  .details-owner {{
    padding: 12px 14px;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: var(--cornerradius-radius_lg, 16px);
    display: flex; flex-direction: column; gap: 10px;
  }}
  .details-owner-row {{
    display: flex; align-items: center; gap: 10px;
  }}
  .details-owner-ico {{
    width: 26px; height: 26px; border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    background: var(--panel-2);
    color: var(--text-dim);
  }}
  .details-owner-name {{
    font-size: 14px; font-weight: 600; color: var(--text);
  }}
  .details-owner-meta {{
    font-size: 11px; color: var(--text-dim); margin-top: 1px;
  }}
  .details-note {{
    padding: 12px 14px;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: var(--cornerradius-radius_lg, 16px);
    font-size: 13px; line-height: 1.5; color: var(--text);
  }}
  .details-voice {{
    display: flex; align-items: center; gap: 10px;
    padding: 10px 12px;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: var(--cornerradius-radius_lg, 16px);
  }}
  .details-voice-play {{
    flex: 0 0 auto;
    width: 32px; height: 32px; border-radius: 50%;
    display: inline-flex; align-items: center; justify-content: center;
    background: var(--colors-primarybutton_bg_active);
    color: #fff;
    border: 0; cursor: pointer;
  }}
  .details-voice-wave {{
    flex: 1;
    display: flex; align-items: center; gap: 2px;
    height: 24px;
  }}
  .details-voice-wave span {{
    display: inline-block; width: 3px; border-radius: 2px;
    background: color-mix(in srgb, var(--colors-primarybutton_bg_active) 60%, transparent);
  }}
  .details-voice-wave span:nth-child(3n)   {{ height: 14px; }}
  .details-voice-wave span:nth-child(3n+1) {{ height: 20px; }}
  .details-voice-wave span:nth-child(3n+2) {{ height: 8px; }}
  .details-voice-time {{
    font-size: 11px; color: var(--text-dim);
    font-variant-numeric: tabular-nums;
    flex: 0 0 auto;
  }}
  .details-timeline {{
    padding: 12px 14px;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: var(--cornerradius-radius_lg, 16px);
    display: flex; flex-direction: column; gap: 12px;
    position: relative;
  }}
  .dtl-row {{
    display: flex; align-items: flex-start; gap: 10px;
    position: relative;
  }}
  .dtl-row:not(:last-child)::before {{
    content: '';
    position: absolute;
    left: 4px; top: 14px; bottom: -12px;
    width: 1px;
    background: var(--border);
  }}
  .dtl-dot {{
    flex: 0 0 auto;
    width: 9px; height: 9px; border-radius: 50%;
    background: var(--colors-primarybutton_bg_active);
    margin-top: 4px;
    position: relative; z-index: 1;
  }}
  .dtl-body {{ flex: 1; }}
  .dtl-title {{ font-size: 13px; font-weight: 600; color: var(--text); }}
  .dtl-time  {{ font-size: 11px; color: var(--text-dim); margin-top: 2px; }}
  .details-actions {{
    display: grid; grid-template-columns: 1fr 1fr; gap: 8px;
    margin-top: 4px;
  }}
  .details-actions .btn {{
    display: inline-flex; align-items: center; justify-content: center; gap: 6px;
  }}
  .chip.chip-on {{
    background: color-mix(in srgb, var(--colors-primarybutton_bg_active) 12%, transparent);
    border-color: color-mix(in srgb, var(--colors-primarybutton_bg_active) 30%, transparent);
    color: var(--text);
  }}

  /* ---- Details tabs (Notes / Campaign / Activity) ---- */
  .dtabs {{
    display: flex; flex-direction: column; gap: 12px;
    flex: 0 0 auto;
  }}
  .dtabs-bar {{
    display: grid; grid-template-columns: repeat(3, 1fr);
    gap: 4px;
    padding: 4px;
    background: var(--panel-2);
    border: 1px solid var(--border);
    border-radius: var(--cornerradius-radius_pill, 999px);
  }}
  .dtabs-btn {{
    background: transparent; border: 0; cursor: pointer;
    padding: 8px 12px;
    font: inherit; font-size: 12px; font-weight: 600;
    color: var(--text-dim);
    border-radius: 999px;
    transition: color .15s, background .15s, box-shadow .15s;
  }}
  .dtabs-btn:hover:not(.active) {{ color: var(--text); }}
  .dtabs-btn.active {{
    background: var(--panel);
    color: var(--text);
    box-shadow: 0 1px 3px rgba(0,0,0,.06);
  }}
  .dtabs-panel {{
    display: flex; flex-direction: column; gap: 10px;
  }}
  .dtabs-panel[hidden] {{ display: none; }}
  .dtabs-sub-label {{
    font-size: 11px; color: var(--text-dim);
    text-transform: uppercase; letter-spacing: 0.06em;
  }}
  .dtabs-kv {{
    padding: 4px 4px 0;
    display: flex; flex-direction: column;
  }}
  .dtabs-kv-row {{
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 0;
    border-bottom: 1px solid var(--border);
    font-size: 13px;
  }}
  .dtabs-kv-row:last-child {{ border-bottom: 0; }}
  .dtabs-kv-k {{ color: var(--text-dim); }}
  .dtabs-kv-v {{ color: var(--text); font-weight: 600; }}

  /* ---- Library stage wrapper for the transcript showcase ---- */
  .lib-transcript-stage {{
    width: 100%;
    padding: 20px 24px;
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: var(--cornerradius-radius_md, 12px);
  }}
  .convo-transcript-static {{
    /* Override the live transcript's mask + flex-end pinning */
    justify-content: flex-start;
    -webkit-mask-image: none;
            mask-image: none;
    padding: 0;
    gap: 10px;
    min-height: 0;
    overflow: visible;
    flex: none;
  }}

  /* ---- Library stage wrappers for listing + details components ---- */
  .lib-listing-stage, .lib-details-stage, .lib-nav-stage {{
    width: 100%;
    display: flex; flex-direction: column; gap: 12px;
    background: var(--panel-2);
    padding: 16px;
    border-radius: var(--cornerradius-radius_md, 12px);
    max-width: 420px;
  }}
  .lib-listing-stage .listing-title-row,
  .lib-listing-stage .listing-summary,
  .lib-listing-stage .listing-list {{
    margin: 0;
  }}
  .lib-listing-stage .listing-summary,
  .lib-details-stage .details-stats,
  .lib-details-stage .details-owner,
  .lib-details-stage .details-note,
  .lib-details-stage .details-voice,
  .lib-details-stage .details-timeline,
  .lib-details-stage .details-hero {{
    width: 100%;
  }}
  .lib-nav-stage {{
    padding: 24px 16px 12px;
  }}

  .proto-orb {{ position: absolute !important; bottom: 20px !important; right: 20px !important; z-index: 30; }}

  /* Quick-chip choices in conversation */
  .convo-quickchips {{
    padding: 0 16px 12px; display: flex; gap: 6px; flex-wrap: wrap;
    border-top: 1px solid var(--border);
    padding-top: 12px;
  }}
  .chip-quick {{
    background: var(--panel); color: var(--text);
    border: 1px solid var(--strokes-outline_light, #E0E0E0);
    padding: 8px 14px; font-size: 12px; font-weight: 500;
    border-radius: 999px; cursor: pointer;
    font-family: inherit;
  }}
  .chip-quick:hover {{ background: var(--panel-2); }}

  /* Chip toggle (property stop) */
  .chip-toggle {{
    cursor: pointer; font-family: inherit;
  }}

  /* End drive button in progress bar */
  .proto-end {{
    margin-top: 8px; width: 100%;
    background: transparent; color: var(--text-dim);
  }}

  /* Added screen */
  .added-hero {{
    display: flex; flex-direction: column; align-items: flex-start; gap: 10px;
  }}
  .added-hero .lead-check {{
    background: var(--colors-green, #1A7F42); color: #fff;
    display: inline-flex; align-items: center; justify-content: center; border-radius: 50%;
  }}
  .added-title {{ font-size: 22px; font-weight: 700; color: var(--text); }}
  .added-sub {{ font-size: 14px; color: var(--text-dim); }}

  .added-next {{
    background: var(--panel-2); border: 1px solid var(--border);
    border-radius: var(--cornerradius-radius_lg, 16px);
    padding: 14px; display: flex; flex-direction: column; gap: 8px;
  }}
  .added-next-label {{
    font-size: 10px; text-transform: uppercase; letter-spacing: .05em;
    color: var(--text-dim); font-weight: 600;
  }}
  .added-next-body {{ display: flex; align-items: center; gap: 12px; }}


  /* placeholder pages */
  .placeholder {{ padding: 32px 40px 80px; max-width: 900px; }}
  .placeholder-card {{
    background: var(--panel); border: 1px solid var(--border);
    border-radius: 12px; padding: 28px 32px;
    color: var(--text-dim); font-size: 15px; line-height: 1.6;
  }}
  .placeholder-card p {{ margin: 0 0 12px; }}
  .placeholder-card p:last-child {{ margin-bottom: 0; }}
  .placeholder-hint {{
    padding-top: 12px; margin-top: 12px;
    border-top: 1px solid var(--border);
    font-size: 13px; color: var(--text-dim);
  }}
  .placeholder .coll-title {{ margin: 0 0 24px; }}

  /* tabs */
  .tabs {{
    position: sticky; top: 0; z-index: 10;
    display: flex; gap: 4px; padding: 12px 40px 0 0;
    background: rgba(255,255,255,.9); backdrop-filter: blur(8px);
    border-bottom: 1px solid var(--border);
  }}
  .tab-btn {{
    background: transparent; color: var(--text-dim); border: 0;
    padding: 12px 20px; font: inherit; font-size: 14px; font-weight: 500;
    cursor: pointer; border-bottom: 2px solid transparent;
    margin-bottom: -1px; transition: color .15s, border-color .15s;
    text-transform: capitalize;
  }}
  .tabs .tab-btn:first-child {{ padding-left: 0; }}
  .tab-btn:hover {{ color: var(--text); }}
  .tab-btn.active {{ color: var(--accent); border-bottom-color: var(--accent); }}

  .tab-panel {{ display: none; }}
  .tab-panel.active {{ display: block; }}
  .tab-panel .collection {{ margin-bottom: 0; }}

  pre {{
    background: var(--panel-2); padding: 12px; border-radius: 6px;
    overflow: auto; font-family: var(--mono); font-size: 12px;
  }}

  /* --- Route Card component --- */
  .route-card {{
    width: 100%; max-width: 320px;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: var(--cornerradius-radius_lg, 16px);
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,.05);
  }}
  .route-map {{
    position: relative; width: 100%;
    aspect-ratio: 16 / 10;
    background: var(--panel-2);
  }}
  .route-map svg {{ display: block; width: 100%; height: 100%; }}
  .route-info {{
    padding: 14px 16px 16px;
    display: flex; flex-direction: column; gap: 6px;
    border-top: 1px solid var(--border);
  }}
  .route-info-head {{
    display: inline-flex; align-items: center; gap: 6px;
    color: var(--text-dim);
    font-size: 10px; letter-spacing: .06em;
    text-transform: uppercase; font-weight: 700;
  }}
  .route-info-head .ph-bold,
  .route-info-head svg {{ color: var(--colors-primarybutton_bg_active, #D93131); }}
  .route-info-title {{
    font-size: 15px; font-weight: 700; color: var(--text);
    line-height: 1.35;
  }}
  .route-info-meta {{
    font-size: 12px; color: var(--text-dim);
    display: inline-flex; align-items: center; gap: 6px;
  }}
  .route-info-dot {{
    width: 4px; height: 4px; border-radius: 50%;
    background: var(--text-dim); opacity: .5;
  }}

  /* ==================== v2 additions (convo runner, drive sheet, inspection) ==================== */

  /* --- Property card compact: circular thumb + inline grade badge --- */
  .pcard-thumb {{
    position: relative; flex: 0 0 auto;
    width: 48px; height: 48px; border-radius: 50%; overflow: hidden;
    background-color: #4a7c59;
    background-image:
      linear-gradient(135deg, rgba(0,0,0,0), rgba(0,0,0,.28)),
      repeating-linear-gradient(45deg, #4a7c59 0 12px, #3a6247 12px 24px);
    background-size: cover; background-position: center;
  }}
  .pcard-addr-row {{
    display: inline-flex; align-items: center; gap: 6px; flex-wrap: wrap;
  }}
  .pcard-grade-badge {{
    min-width: 18px; height: 18px; padding: 0 6px;
    border-radius: 999px;
    background: color-mix(in srgb, currentColor 12%, transparent);
    color: var(--gradecolors-grade_a, #1A7F42);
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 10px; font-weight: 700; line-height: 1;
  }}
  .pcard-grade-badge[data-grade="A"] {{ color: var(--gradecolors-grade_a, #1A7F42); }}
  .pcard-grade-badge[data-grade="B"] {{ color: var(--gradecolors-grade_b, #E8A317); }}
  .pcard-grade-badge[data-grade="C"] {{ color: var(--gradecolors-grade_c, #D93025); }}
  .pcard-grade-badge[data-grade="D"] {{ color: var(--gradecolors-grade_d, #9D2525); }}

  /* --- Smooth crossfade between proto-screens (visibility + opacity) --- */
  .proto-screen {{
    display: flex !important;
    opacity: 0; visibility: hidden;
    pointer-events: none;
    transition: opacity .35s ease, visibility 0s linear .35s;
    z-index: 0;
  }}
  .proto-screen.active {{
    opacity: 1; visibility: visible;
    pointer-events: auto;
    transition: opacity .35s ease, visibility 0s linear 0s;
    z-index: 1;
  }}

  /* --- Convo transcript aging + top mask (base size 20px) --- */
  .convo-line {{ font-size: 20px !important; line-height: 1.3 !important; }}
  .convo-transcript {{
    -webkit-mask-image: linear-gradient(180deg, transparent 0%, transparent 6%, black 30%, black 100%);
            mask-image: linear-gradient(180deg, transparent 0%, transparent 6%, black 30%, black 100%);
  }}
  .convo-line.age-1 {{ opacity: 0.65 !important; font-size: 18px !important; }}
  .convo-line.age-2 {{ opacity: 0.40 !important; font-size: 16px !important; }}
  .convo-line.age-3 {{ opacity: 0.20 !important; font-size: 15px !important; }}
  .convo-line.age-4 {{ opacity: 0.08 !important; font-size: 14px !important; }}
  .convo-line.age-5 {{ opacity: 0.02 !important; font-size: 13px !important; }}
  .convo-line.age-6 {{ display: none !important; }}

  /* --- Live caption bubble while listening --- */
  .convo-live-caption {{
    align-self: flex-start;
    display: inline-flex; align-items: center; gap: 10px;
    padding: 10px 16px;
    background: color-mix(in srgb, var(--colors-primarybutton_bg_active, #D93131) 12%, transparent);
    border-radius: 20px;
    color: var(--colors-primarybutton_bg_active, #D93131);
    font-size: 15px; font-weight: 600; line-height: 1.35;
    max-width: 92%;
    opacity: 0;
    animation: convoListenIn .25s ease-out forwards;
  }}
  .convo-live-caption .dots {{ display: inline-flex; gap: 5px; }}
  .convo-live-caption .dots span {{
    width: 6px; height: 6px; border-radius: 50%;
    background: currentColor;
    animation: convoListenPulse 1.2s ease-in-out infinite;
  }}
  .convo-live-caption .dots span:nth-child(2) {{ animation-delay: .18s; }}
  .convo-live-caption .dots span:nth-child(3) {{ animation-delay: .36s; }}
  @keyframes convoListenIn {{ to {{ opacity: 1; }} }}
  @keyframes convoListenPulse {{
    0%, 100% {{ transform: scale(.7); opacity: .55; }}
    50%      {{ transform: scale(1);  opacity: 1;   }}
  }}

  /* --- Convo CTA button: replaces orb+status when a screen concludes --- */
  .convo-orb-btn[hidden] {{ display: none; }}
  .convo-cta-btn {{ min-width: 240px; display: none; }}
  .convo-cta-btn:not([hidden]) {{ display: inline-flex; }}
  .convo-foot.convo-foot-cta {{
    flex-direction: row-reverse; align-items: center; gap: 12px;
  }}
  .convo-foot.convo-foot-cta .convo-cta-btn {{ flex: 1; min-width: 0; }}
  .convo-voice-orb.convo-voice-orb-sm {{ width: 48px !important; height: 48px !important; }}

  /* --- Inline route card + property card in convo transcript --- */
  .convo-route-card, .convo-prop-card, .convo-scan-card, .convo-tags-card, .convo-note-card {{
    align-self: stretch;
    opacity: 0; transform: translateY(8px);
    transition: opacity .4s ease-out, transform .4s ease-out;
  }}
  .convo-route-card.enter,
  .convo-prop-card.enter,
  .convo-scan-card.enter,
  .convo-tags-card.enter,
  .convo-note-card.enter {{ opacity: 1; transform: none; }}
  .convo-prop-card .pcard {{ max-width: none; }}

  /* --- Scanning bubble --- */
  .convo-scan-line {{
    align-self: flex-start;
    display: inline-flex; align-items: center; gap: 10px;
    padding: 10px 16px;
    background: color-mix(in srgb, var(--colors-primarybutton_bg_active, #D93131) 8%, transparent);
    border-radius: 20px;
    color: var(--text-dim);
    font-size: 13px; font-weight: 600; letter-spacing: .01em;
    opacity: 0;
    animation: convoListenIn .25s ease-out forwards;
  }}
  .convo-scan-line .scan-spinner {{
    width: 14px; height: 14px; border-radius: 50%;
    border: 2px solid color-mix(in srgb, var(--colors-primarybutton_bg_active, #D93131) 25%, transparent);
    border-top-color: var(--colors-primarybutton_bg_active, #D93131);
    animation: scanSpin .8s linear infinite;
  }}
  @keyframes scanSpin {{ to {{ transform: rotate(360deg); }} }}

  /* --- Findings card: imagery carousel + skip-trace details --- */
  .findings-card {{
    background: var(--panel); border: 1px solid var(--border);
    border-radius: var(--cornerradius-radius_lg, 16px);
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,.05);
  }}
  .findings-carousel {{
    position: relative; width: 100%;
    aspect-ratio: 16/10;
    overflow: hidden;
    background: var(--panel-2);
  }}
  .findings-photo {{
    position: absolute; inset: 0;
    width: 100%; height: 100%;
    object-fit: cover;
    opacity: 0;
    transition: opacity .45s ease;
  }}
  .findings-photo.active {{ opacity: 1; }}
  .findings-dots {{
    position: absolute; bottom: 10px; left: 50%;
    transform: translateX(-50%);
    display: flex; gap: 6px;
    z-index: 2;
  }}
  .findings-dots span {{
    width: 6px; height: 6px; border-radius: 50%;
    background: rgba(255,255,255,.5);
    transition: background .2s;
  }}
  .findings-dots span.active {{ background: #fff; }}
  .findings-body {{
    padding: 14px 16px; display: flex; flex-direction: column; gap: 10px;
  }}
  .finding-row {{
    display: flex; align-items: flex-start; gap: 10px;
    font-size: 13px; color: var(--text);
  }}
  .finding-row .ph-bold {{
    color: var(--colors-primarybutton_bg_active, #D93131);
    font-size: 14px; line-height: 1.2; margin-top: 2px;
  }}
  .findings-label {{
    font-size: 10px; letter-spacing: .06em; text-transform: uppercase;
    color: var(--text-dim); font-weight: 700;
    display: block; margin-bottom: 2px;
  }}
  .findings-value {{ color: var(--text); font-weight: 500; }}

  /* Property hero card override for convo transcript (fill width) */
  .convo-prop-card .pfeat {{ max-width: none; }}

  /* --- Summary card: what will be saved as a lead --- */
  .summary-card {{
    background: var(--panel); border: 1px solid var(--border);
    border-radius: var(--cornerradius-radius_lg, 16px);
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,.05);
  }}
  .summary-card-hero {{
    position: relative;
    aspect-ratio: 16/9;
    background-color: #b9d0bc;
    background-size: cover; background-position: center;
  }}
  .summary-card-check {{
    position: absolute; top: 12px; right: 12px;
    width: 28px; height: 28px; border-radius: 50%;
    background: var(--colors-green, #1A7F42); color: #fff;
    display: inline-flex; align-items: center; justify-content: center;
    box-shadow: 0 2px 8px rgba(0,0,0,.15);
  }}
  .summary-card-body {{
    padding: 14px 16px 16px;
    display: flex; flex-direction: column; gap: 8px;
  }}
  .summary-card-title {{
    font-size: 17px; font-weight: 700; color: var(--text);
    line-height: 1.25;
  }}
  .summary-card-sub {{
    font-size: 12px; color: var(--text-dim);
  }}
  .summary-rows {{
    margin-top: 6px; display: flex; flex-direction: column; gap: 8px;
    padding-top: 10px; border-top: 1px solid var(--border);
  }}
  .summary-row {{
    display: flex; justify-content: space-between; gap: 12px;
    font-size: 13px;
  }}
  .summary-label {{
    color: var(--text-dim); font-weight: 600;
    text-transform: uppercase; font-size: 10px; letter-spacing: .06em;
    flex-shrink: 0; padding-top: 3px;
  }}
  .summary-value {{ color: var(--text); font-weight: 500; text-align: right; flex: 1; }}
  .convo-summary-card {{
    align-self: stretch;
    opacity: 0; transform: translateY(8px);
    transition: opacity .4s ease-out, transform .4s ease-out;
  }}
  .convo-summary-card.enter {{ opacity: 1; transform: none; }}

  /* --- Drive toast (property saved) --- */
  .drive-toast {{
    position: absolute; top: 44px; left: 16px; right: 16px;
    z-index: 30;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 10px 14px;
    display: flex; align-items: center; gap: 10px;
    font-size: 13px; font-weight: 600; color: var(--text);
    box-shadow: 0 6px 22px rgba(0,0,0,.14);
    transform: translateY(-16px); opacity: 0;
    transition: opacity .3s ease, transform .3s ease;
  }}
  .drive-toast[hidden] {{ display: none; }}
  .drive-toast.show {{ transform: translateY(0); opacity: 1; }}
  .drive-toast-icon {{
    width: 22px; height: 22px; border-radius: 50%;
    background: var(--colors-green, #1A7F42); color: #fff;
    display: inline-flex; align-items: center; justify-content: center;
    flex-shrink: 0;
  }}

  /* --- Tags + Campaign card --- */
  .tags-card {{
    background: var(--panel); border: 1px solid var(--border);
    border-radius: var(--cornerradius-radius_lg, 16px);
    padding: 14px 16px;
    display: flex; flex-direction: column; gap: 12px;
  }}
  .tags-card-section-label {{
    font-size: 10px; letter-spacing: .06em; text-transform: uppercase;
    color: var(--text-dim); font-weight: 700;
  }}
  .tags-card-chips {{
    display: flex; flex-wrap: wrap; gap: 6px;
  }}
  .tag-chip {{
    display: inline-flex; align-items: center; gap: 6px;
    padding: 6px 10px 6px 12px;
    background: color-mix(in srgb, var(--colors-primarybutton_bg_active, #D93131) 8%, transparent);
    color: var(--colors-primarybutton_bg_active, #D93131);
    border-radius: 999px;
    font-size: 12px; font-weight: 600;
    border: 0; cursor: pointer;
  }}
  .tag-chip .tag-x {{
    width: 16px; height: 16px; border-radius: 50%;
    background: color-mix(in srgb, var(--colors-primarybutton_bg_active, #D93131) 18%, transparent);
    display: inline-flex; align-items: center; justify-content: center;
    font-size: 9px;
  }}
  .tag-chip.tag-add {{
    background: var(--panel-2); color: var(--text-dim);
    border: 1px dashed var(--border);
  }}
  .tags-card-campaign {{
    display: flex; align-items: center; gap: 10px;
    padding: 10px 12px; background: var(--panel-2);
    border-radius: 12px;
  }}
  .tags-card-campaign-body {{ flex: 1; }}
  .tags-card-campaign-name {{ font-size: 13px; font-weight: 700; color: var(--text); }}
  .tags-card-campaign-reason {{ font-size: 11px; color: var(--text-dim); margin-top: 1px; }}

  /* --- Note composer card --- */
  .note-card {{
    background: var(--panel); border: 1px solid var(--border);
    border-radius: var(--cornerradius-radius_lg, 16px);
    padding: 14px 16px;
    display: flex; flex-direction: column; gap: 10px;
  }}
  .note-card-label {{
    font-size: 10px; letter-spacing: .06em; text-transform: uppercase;
    color: var(--text-dim); font-weight: 700;
  }}
  .note-card-text {{
    font-size: 14px; color: var(--text); font-weight: 500;
    min-height: 44px; line-height: 1.4;
  }}
  .note-card-text.empty {{ color: var(--text-dim); font-weight: 400; font-style: italic; }}

  /* --- Drive screen v2 (full map + compact 400px sheet) --- */
  .scr-drive-v2 {{
    position: relative;
    display: block !important;
    padding-top: 0 !important;
    height: 100%;
    overflow: hidden;
  }}
  .drive-map-full {{
    position: absolute; inset: 0; z-index: 1;
    background: var(--panel-2);
    isolation: isolate;
  }}
  .drive-sheet {{
    position: absolute; left: 0; right: 0; bottom: 0; z-index: 20;
    height: 400px;
    background: var(--panel);
    border-top-left-radius: 24px; border-top-right-radius: 24px;
    padding: 16px 20px calc(18px + env(safe-area-inset-bottom, 0px));
    box-shadow: 0 -6px 22px rgba(0,0,0,.10);
    display: flex; flex-direction: column;
    overflow: hidden;
  }}
  .drive-sheet-header {{
    display: flex; justify-content: space-between; align-items: center;
    gap: 12px;
  }}
  .drive-sheet-status {{
    display: inline-flex; align-items: center; gap: 8px;
    font-size: 11px; letter-spacing: .12em; text-transform: uppercase;
    color: var(--text-dim); font-weight: 700;
  }}
  .drive-sheet-status .drive-status-dot {{
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--colors-primarybutton_bg_active, #D93131);
    box-shadow: 0 0 0 4px color-mix(in srgb, var(--colors-primarybutton_bg_active, #D93131) 18%, transparent);
  }}
  .drive-sheet-close {{
    width: 32px; height: 32px; border-radius: 50%;
    background: var(--panel-2); color: var(--text-dim); border: 0;
    display: inline-flex; align-items: center; justify-content: center;
    cursor: pointer; flex-shrink: 0;
  }}
  .drive-sheet-close:hover {{ background: var(--colors-neutral_200, #E0E0E0); color: var(--text); }}
  .drive-sheet-progress-row {{
    display: flex; justify-content: space-between; align-items: baseline;
    margin-top: 12px;
    font-size: 12px; font-weight: 600; color: var(--text-dim);
  }}
  .drive-sheet-progress-count b {{ color: var(--text); }}
  .drive-sheet-progress-bar {{
    height: 6px; background: var(--colors-neutral_100, #F2F2F2);
    border-radius: 999px; overflow: hidden;
    margin-top: 6px;
  }}
  .drive-sheet-progress-fill {{
    height: 100%; background: var(--colors-primarybutton_bg_active, #D93131);
    border-radius: 999px;
    transition: width .5s ease-out;
  }}
  .drive-sheet-next-label {{
    margin-top: 18px;
    font-size: 10px; letter-spacing: .08em; text-transform: uppercase;
    color: var(--text-dim); font-weight: 700;
  }}
  .drive-sheet-next-card {{
    margin-top: 8px;
    display: flex; align-items: center; gap: 14px;
    padding: 12px 14px;
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 16px;
    box-shadow: 0 2px 10px rgba(0,0,0,.04);
  }}
  .drive-sheet-next-body {{ flex: 1; min-width: 0; }}
  .drive-sheet-next-addr {{
    font-size: 16px; font-weight: 700; color: var(--text);
    display: inline-flex; align-items: center; gap: 8px;
  }}
  .drive-sheet-next-meta {{
    margin-top: 2px;
    font-size: 12px; color: var(--text-dim);
  }}
  .drive-sheet-next-thumb {{
    width: 44px; height: 44px; border-radius: 50%;
    background-color: #4a7c59;
    background-size: cover; background-position: center;
    flex-shrink: 0;
  }}
  .drive-sheet-orb-wrap {{
    margin-top: auto;
    display: flex; flex-direction: column; align-items: center; gap: 10px;
    padding-top: 14px;
  }}
  .drive-sheet-orb-status {{
    font-size: 11px; letter-spacing: .14em; text-transform: uppercase;
    color: var(--text-dim); font-weight: 700;
  }}
  .drive-sheet-orb {{
    background: transparent; border: 0; padding: 0; cursor: pointer;
    display: inline-flex; align-items: center; justify-content: center;
    transition: transform .18s ease-out;
  }}
  .drive-sheet-orb:hover {{ transform: scale(1.04); }}
  .drive-sheet-orb:active {{ transform: scale(.96); }}
  .drive-voice-orb {{ width: 96px !important; height: 96px !important; }}
  .drive-voice-orb .orb-core {{ inset: 20%; }}
  .drive-voice-orb .orb-ring {{ inset: 0; }}
  .drive-voice-orb .orb-ring-2 {{ inset: 8%; }}

  /* --- Convo screen used as rising sheet over the drive screen (inspection) --- */
  .proto-screen[data-screen="convo"].as-sheet {{
    z-index: 5;
    opacity: 1 !important;
    visibility: visible !important;
    pointer-events: auto !important;
    transform: translateY(100%);
    transition: transform .55s cubic-bezier(.22,.9,.3,1), opacity 0s;
    border-top-left-radius: 28px;
    border-top-right-radius: 28px;
    overflow: hidden;
    box-shadow: 0 -12px 32px rgba(0,0,0,.18);
  }}
  .proto-screen[data-screen="convo"].as-sheet.risen {{
    transform: translateY(0);
  }}

</style>
</head>
<body>
<header class="page">
  <div>
    <h1>Profit Drive</h1>
  </div>
  <nav class="page-nav">{page_nav}</nav>
</header>
<main>
{BODY}
</main>
<script>
  (function () {{
    const pageBtns  = document.querySelectorAll('.page-btn');
    const pageEls   = document.querySelectorAll('.page');
    const tabBtns   = document.querySelectorAll('.tab-btn');
    const tabPanels = document.querySelectorAll('.tab-panel');

    function setPage(pid) {{
      pageBtns.forEach(b => b.classList.toggle('active', b.dataset.page === pid));
      pageEls.forEach(p => p.classList.toggle('active', p.dataset.page === pid));
    }}
    function setTab(name) {{
      tabBtns.forEach(b => b.classList.toggle('active', b.dataset.tab === name));
      tabPanels.forEach(p => p.classList.toggle('active', p.dataset.tab === name));
    }}
    function parseHash() {{
      const raw = location.hash.replace(/^#/, '');
      const [page, tab] = raw.split('/');
      return {{ page, tab }};
    }}
    function writeHash(page, tab) {{
      const h = tab ? `#${{page}}/${{tab}}` : `#${{page}}`;
      if (location.hash !== h) history.replaceState(null, '', h);
    }}
    function current() {{
      const activePage = document.querySelector('.page-btn.active')?.dataset.page || 'variables';
      const activeTab  = document.querySelector('.tab-btn.active')?.dataset.tab;
      return {{ page: activePage, tab: activeTab }};
    }}
    pageBtns.forEach(b => b.addEventListener('click', () => {{
      setPage(b.dataset.page);
      const t = current().tab;
      writeHash(b.dataset.page, b.dataset.page === 'variables' ? t : null);
      window.scrollTo({{ top: 0 }});
    }}));
    tabBtns.forEach(b => b.addEventListener('click', () => {{
      setTab(b.dataset.tab);
      writeHash('variables', b.dataset.tab);
      window.scrollTo({{ top: 0 }});
    }}));
    // initial route
    const {{ page, tab }} = parseHash();
    if (page && document.querySelector(`.page[data-page="${{page}}"]`)) setPage(page);
    if (tab && document.querySelector(`.tab-panel[data-tab="${{tab}}"]`)) setTab(tab);
    window.addEventListener('hashchange', () => {{
      const {{ page, tab }} = parseHash();
      if (page) setPage(page);
      if (tab)  setTab(tab);
    }});
  }})();

  // ---- library sub-tabs ----
  (function () {{
    const btns = document.querySelectorAll('.lib-tab');
    const panels = document.querySelectorAll('.lib-panel');
    btns.forEach(b => b.addEventListener('click', () => {{
      const id = b.dataset.libTab;
      btns.forEach(x => x.classList.toggle('active', x.dataset.libTab === id));
      panels.forEach(p => p.classList.toggle('active', p.dataset.libTab === id));
    }}));
  }})();

  // ---- state toggles: swap [data-state] on a target orb/waveform ----
  document.addEventListener('click', (e) => {{
    const btn = e.target.closest('[data-state-target]');
    if (!btn) return;
    const target = document.getElementById(btn.dataset.stateTarget);
    if (!target) return;
    target.setAttribute('data-state', btn.dataset.state);
    // update sibling status text if any
    const status = document.querySelector(`[data-status-target="${{btn.dataset.stateTarget}}"]`);
    if (status) {{
      const label = btn.dataset.state.charAt(0).toUpperCase() + btn.dataset.state.slice(1);
      status.textContent = label === 'Idle' ? 'Idle' : (label === 'Muted' ? 'Muted' : label + '…');
    }}
    // sync sibling seg-btns in the same seg group
    btn.parentElement.querySelectorAll('.seg-btn').forEach(s => s.classList.toggle('active', s === btn));
  }});

  // ---- grade ring cycling ----
  document.addEventListener('click', (e) => {{
    const btn = e.target.closest('[data-grade-set]');
    if (!btn) return;
    const stage = document.getElementById(btn.dataset.gradeSet);
    if (!stage) return;
    const g = btn.dataset.grade;
    stage.querySelectorAll('.grade-ring').forEach(r => {{
      r.setAttribute('data-grade', g);
      r.querySelector('span').textContent = g;
    }});
    btn.parentElement.querySelectorAll('.seg-btn').forEach(s => s.classList.toggle('active', s === btn));
  }});

  // ==================== Interactive prototype (v2) ====================
  (function () {{
    const stage = document.getElementById('proto-screens');
    if (!stage) return;

    const state = {{
      progress: 1,
      total: 12,
      stops: [
        {{ addr: '123 Main St',         meta: '0.2 mi · 2 min', grade: 'A', thumb: 'https://images.unsplash.com/photo-1568605114967-8130f3a36994?w=160&h=160&fit=crop&q=80', hero: 'https://images.unsplash.com/photo-1568605114967-8130f3a36994?auto=format&fit=crop&w=800&h=560&q=70', price: '$182k', arv: 'ARV', desc: 'Overgrown, roof looks rough, tax lien on file.', bed: 3, bath: 2, sqft: '1,410', tags: ['overgrown lawn', 'roof damage'], campaign: 'Cash-offer', reason: 'High equity, long tenure — solid fit.' }},
        {{ addr: '4471 E Cesar Chavez', meta: '0.8 mi · 3 min', grade: 'B', thumb: 'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?w=160&h=160&fit=crop&q=80', hero: 'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=800&h=560&q=70', price: '$146k', arv: 'ARV', desc: 'Peeling paint, older HVAC, absentee owner.', bed: 3, bath: 1, sqft: '1,180', tags: ['peeling paint'], campaign: 'Cash-offer', reason: 'Owner-occupant, mid-tenure.' }},
        {{ addr: '212 Pedernales St',   meta: '1.1 mi · 4 min', grade: 'A', thumb: 'https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=160&h=160&fit=crop&q=80', hero: 'https://images.unsplash.com/photo-1570129477492-45c003edd2be?auto=format&fit=crop&w=800&h=560&q=70', price: '$210k', arv: 'ARV', desc: 'Boarded window, notice on door, high distress.', bed: 4, bath: 2, sqft: '1,720', tags: ['boarded window', 'notice on door'], campaign: 'Distress outreach', reason: 'Multiple distress signals stacked.' }},
        {{ addr: '907 Willow St',       meta: '0.6 mi · 2 min', grade: 'A', thumb: 'https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=160&h=160&fit=crop&q=80', hero: 'https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=800&h=560&q=70', price: '$168k', arv: 'ARV', desc: 'Vacant + absent owner, overgrown lot.', bed: 3, bath: 2, sqft: '1,320', tags: ['vacant', 'overgrown lawn'], campaign: 'Cash-offer', reason: 'Vacant + absent owner.' }},
      ],
    }};
    function currentStop() {{ return state.stops[0]; }}
    let currentConvoMode = 'intro'; // 'intro' | 'inspect'

    function updateNav(id) {{
      document.querySelectorAll('.proto-nav-btn').forEach(b => b.classList.toggle('active', b.dataset.nav === id));
    }}
    function updateDriveSheet() {{
      const s = currentStop(); if (!s) return;
      const set = (id, v) => {{ const el = document.getElementById(id); if (el) el.textContent = v; }};
      const addr = document.getElementById('drive-next-addr');
      const grade = document.getElementById('drive-next-grade');
      const meta = document.getElementById('drive-next-meta');
      const thumb = document.getElementById('drive-next-thumb');
      const fill = document.getElementById('drive-progress-fill');
      const status = document.getElementById('drive-status-text');
      if (addr) addr.textContent = s.addr;
      if (grade) {{ grade.textContent = s.grade; grade.dataset.grade = s.grade; }}
      if (meta) meta.textContent = 'Austin, TX · ' + s.meta;
      if (thumb) thumb.style.backgroundImage = "url('" + s.thumb + "')";
      set('drive-progress-idx', state.progress);
      set('drive-progress-total', state.total);
      if (fill) fill.style.width = ((state.progress/state.total)*100).toFixed(0) + '%';
      if (status) status.textContent = 'En route';
    }}
    function markCurrentStopArrived() {{
      const status = document.getElementById('drive-status-text');
      if (status) status.textContent = 'Arrived';
    }}
    function advanceStop() {{
      if (state.progress < state.total) state.progress++;
      state.stops.push(state.stops.shift());
      updateDriveSheet();
    }}

    // ---------- Drive sequence ----------
    let driveArrivalTimer = null;
    let pendingDriveToast = null;
    function scheduleDriveToast(text) {{ pendingDriveToast = text; }}
    function showDriveToast(text) {{
      const toast = document.getElementById('drive-toast');
      if (!toast) return;
      const tx = toast.querySelector('.drive-toast-text');
      if (tx) tx.textContent = text;
      toast.hidden = false;
      requestAnimationFrame(() => toast.classList.add('show'));
      setTimeout(() => {{
        toast.classList.remove('show');
        setTimeout(() => {{ toast.hidden = true; }}, 320);
      }}, 3400);
    }}
    function setDriveOrb(s) {{
      const orb = document.getElementById('drive-voice-orb');
      if (orb) orb.setAttribute('data-state', s);
      const lbl = {{speaking:'Speaking', listening:'Listening', thinking:'Thinking', idle:'Tap to talk'}}[s] || '';
      const status = document.getElementById('drive-orb-status');
      if (status) status.textContent = lbl;
    }}
    function stopDriveSequence() {{
      if (driveArrivalTimer) {{ clearTimeout(driveArrivalTimer); driveArrivalTimer = null; }}
    }}
    function startDriveSequence() {{
      stopDriveSequence();
      updateDriveSheet();
      setDriveOrb('speaking');
      initDriveMap();
      const s = currentStop();
      speak('En route to ' + s.addr + '.', () => setDriveOrb('idle'));
      // Any pending "X saved as potential lead" toast from the last inspection
      if (pendingDriveToast) {{
        showDriveToast(pendingDriveToast);
        pendingDriveToast = null;
      }}
      // Simulate arrival after a few seconds
      driveArrivalTimer = setTimeout(onArriveAtStop, 4000);
    }}
    function onArriveAtStop() {{
      markCurrentStopArrived();
      setDriveOrb('thinking');
      // Sheet rises straight away; the arrival line is spoken inside the convo.
      setTimeout(riseSheetToConvo, 600);
    }}
    function initDriveMap() {{
      if (typeof L === 'undefined') return;
      const el = document.getElementById('drive-real-map');
      if (!el) return;
      if (el.dataset.ready !== '1') {{
        el.dataset.ready = '1';
        const map = L.map(el, {{
          center: [30.2672, -97.7431], zoom: 15,
          zoomControl: false, attributionControl: false,
          dragging: true, tap: true,
          scrollWheelZoom: true, doubleClickZoom: true,
          touchZoom: true, boxZoom: false, keyboard: false,
        }});
        L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_smooth/{{z}}/{{x}}/{{y}}{{r}}.png', {{ maxZoom: 20, crossOrigin: true }}).addTo(map);
        const pin = (grade) => L.divIcon({{ className: 'lpin g-' + grade.toLowerCase(), html: grade, iconSize: [26,26], iconAnchor: [13,13] }});
        const you = L.divIcon({{ className: 'lyou', html: '', iconSize: [16,16], iconAnchor: [8,8] }});
        const pinCoords = [
          ['A', 30.2688, -97.7452], ['A', 30.2665, -97.7418],
          ['B', 30.2680, -97.7405], ['B', 30.2650, -97.7440],
          ['C', 30.2645, -97.7415], ['D', 30.2695, -97.7425],
        ];
        pinCoords.forEach(([g,lat,lng]) => L.marker([lat,lng], {{icon: pin(g)}}).addTo(map));
        L.polyline(pinCoords.map(([_,lat,lng]) => [lat,lng]), {{ color: '#D93131', weight: 3, opacity: 0.75, dashArray: '3 7' }}).addTo(map);
        L.marker([30.2660, -97.7430], {{icon: you}}).addTo(map);
        el._leaflet_map = map;
      }}
      setTimeout(() => {{ try {{ el._leaflet_map && el._leaflet_map.invalidateSize(); }} catch(_) {{}} }}, 400);
    }}

    // ---------- Rise/sink sheet transitions (drive ⇄ inspect convo) ----------
    function riseSheetToConvo() {{
      const convoScr = document.querySelector('[data-screen="convo"]');
      const driveScr = document.querySelector('[data-screen="drive"]');
      if (!convoScr || !driveScr) return;
      currentConvoMode = 'inspect';
      driveScr.classList.add('active'); // keep the map alive underneath
      stopConvoSequence();
      convoScr.classList.add('as-sheet');
      convoScr.classList.remove('risen');
      void convoScr.offsetWidth;
      requestAnimationFrame(() => {{
        convoScr.classList.add('risen');
        runConvoSequence('inspect');
      }});
    }}
    function sinkSheetToDrive() {{
      const convoScr = document.querySelector('[data-screen="convo"]');
      if (!convoScr) return;
      stopConvoSequence();
      convoScr.classList.remove('risen');
      setTimeout(() => {{
        convoScr.classList.remove('as-sheet');
        advanceStop();
        startDriveSequence();
      }}, 520);
    }}

    // ---------- Details tabs (Notes / Campaign / Activity) ----------
    document.querySelectorAll('[data-dtabs]').forEach((wrap) => {{
      const btns   = wrap.querySelectorAll('.dtabs-btn[data-dtab]');
      const panels = wrap.querySelectorAll('.dtabs-panel[data-dtab-panel]');
      btns.forEach((b) => {{
        b.addEventListener('click', () => {{
          const id = b.dataset.dtab;
          btns.forEach((x) => {{
            const on = x === b;
            x.classList.toggle('active', on);
            x.setAttribute('aria-selected', on ? 'true' : 'false');
          }});
          panels.forEach((p) => {{
            const on = p.dataset.dtabPanel === id;
            p.classList.toggle('active', on);
            p.hidden = !on;
          }});
        }});
      }});
    }});

    // ---------- Image carousel (property details) ----------
    document.querySelectorAll('[data-carousel]').forEach((car) => {{
      const track = car.querySelector('[data-carousel-track]');
      const dots  = Array.from(car.querySelectorAll('[data-carousel-dot]'));
      const count = car.querySelector('[data-carousel-count]');
      const prev  = car.querySelector('[data-carousel-prev]');
      const next  = car.querySelector('[data-carousel-next]');
      if (!track) return;
      const total = track.children.length;

      function currentIndex() {{
        const w = track.clientWidth;
        if (!w) return 0;
        return Math.round(track.scrollLeft / w);
      }}
      function setActive(idx) {{
        idx = Math.max(0, Math.min(total - 1, idx));
        dots.forEach((d, i) => d.classList.toggle('active', i === idx));
        if (count) count.textContent = (idx + 1) + ' / ' + total;
        if (prev) prev.hidden = idx === 0;
        if (next) next.hidden = idx === total - 1;
      }}
      function goTo(idx) {{
        idx = Math.max(0, Math.min(total - 1, idx));
        track.scrollTo({{ left: idx * track.clientWidth, behavior: 'smooth' }});
        setActive(idx);
      }}

      track.addEventListener('scroll', () => setActive(currentIndex()), {{ passive: true }});
      dots.forEach((d) => d.addEventListener('click', () => goTo(parseInt(d.dataset.carouselDot, 10) || 0)));
      if (prev) prev.addEventListener('click', () => goTo(currentIndex() - 1));
      if (next) next.addEventListener('click', () => goTo(currentIndex() + 1));

      setActive(0);
    }});

    // ---------- Navigation ----------
    function go(id) {{
      if (id === 'inspect')     {{ riseSheetToConvo(); return; }}
      if (id === 'drive-next')  {{ sinkSheetToDrive(); return; }}
      if (id === 'drive-start') {{ id = 'drive'; }}
      const convoScr = document.querySelector('[data-screen="convo"]');
      if (convoScr) convoScr.classList.remove('as-sheet', 'risen');
      document.querySelectorAll('.proto-screen').forEach(s => s.classList.toggle('active', s.dataset.screen === id));
      updateNav(id);
      stopDriveSequence();
      stopConvoSequence();
      if (id === 'convo') {{
        const mode = currentConvoMode; currentConvoMode = 'intro';
        runConvoSequence(mode);
      }} else if (id === 'drive') {{
        startDriveSequence();
      }}
    }}
    stage.parentElement.parentElement.addEventListener('click', (e) => {{
      const btn = e.target.closest('[data-nav]');
      if (!btn) return;
      go(btn.dataset.nav);
    }});

    // ---------- Listing search + filter (Route + Secured) ----------
    const listingState = {{}}; // scope -> {{ q: '', filters: {{ groupName: value }} }}
    function scopeState(scope) {{
      if (!listingState[scope]) listingState[scope] = {{ q: '', filters: {{}} }};
      return listingState[scope];
    }}
    function chipMatch(scope, row, filter) {{
      if (!filter || filter === 'all') return true;
      if (scope === 'route-list') {{
        if (filter === 'today')      return row.dataset.when === 'today';
        if (filter === 'week')       return row.dataset.when === 'today' || row.dataset.when === 'week';
        if (filter === 'month')      return row.dataset.when !== 'older';
        if (filter === 'high-yield') return row.dataset.high === 'true';
        return true;
      }}
      if (scope === 'secured-list') {{
        if (filter === 'grade-a')     return row.dataset.grade === 'A';
        if (filter === 'grade-b')     return row.dataset.grade === 'B';
        if (filter === 'grade-c')     return row.dataset.grade === 'C';
        if (filter === 'cash-offer')  return row.dataset.campaign === 'cash-offer';
        if (filter === 'foreclosure') return row.dataset.campaign === 'foreclosure';
        if (filter === 'rehab')       return row.dataset.campaign === 'rehab';
        if (filter === 'rental')      return row.dataset.campaign === 'rental';
        return true;
      }}
      return true;
    }}
    function applyListing(scope) {{
      const list = stage.querySelector('[data-filter-target="' + scope + '"]');
      if (!list) return;
      const st = scopeState(scope);
      const q = (st.q || '').trim().toLowerCase();
      const activeFilters = Object.values(st.filters).filter((v) => v && v !== 'all');
      let visible = 0;
      list.querySelectorAll('.listing-row').forEach((row) => {{
        let show = true;
        if (q) show = show && (row.textContent || '').toLowerCase().includes(q);
        for (const f of activeFilters) show = show && chipMatch(scope, row, f);
        row.hidden = !show;
        if (show) visible++;
      }});
      const empty = list.parentElement.querySelector('.listing-empty');
      if (empty) empty.hidden = visible > 0;
      const btn = stage.querySelector('[data-filter-toggle="' + scope + '"]');
      if (btn) {{
        const count = activeFilters.length;
        btn.classList.toggle('has-active', count > 0);
        const badge = btn.querySelector('.listing-filter-count');
        if (badge) {{
          badge.textContent = String(count);
          badge.hidden = count === 0;
        }}
      }}
    }}
    // Row click inside a filter dropdown — one selection per group
    stage.addEventListener('click', (e) => {{
      const row = e.target.closest('.filter-dd-list .filter-dd-row');
      if (!row) return;
      const list = row.closest('.filter-dd-list');
      const scope = list.dataset.filterScope;
      const group = list.dataset.filterGroup || 'default';
      list.querySelectorAll('.filter-dd-row').forEach((r) => r.classList.toggle('is-active', r === row));
      scopeState(scope).filters[group] = row.dataset.filter;
      applyListing(scope);
    }});
    // Search input
    stage.addEventListener('input', (e) => {{
      const input = e.target.closest('input[data-search-scope]');
      if (!input) return;
      const scope = input.dataset.searchScope;
      scopeState(scope).q = input.value || '';
      applyListing(scope);
    }});
    // Filter dropdown toggle — also closes any other open dropdown
    stage.addEventListener('click', (e) => {{
      const toggle = e.target.closest('[data-filter-toggle]');
      if (!toggle) return;
      const scope = toggle.dataset.filterToggle;
      const panel = stage.querySelector('[data-filter-panel="' + scope + '"]');
      if (!panel) return;
      const opening = panel.hasAttribute('hidden');
      // close others
      stage.querySelectorAll('.filter-dd').forEach((p) => p.setAttribute('hidden', ''));
      stage.querySelectorAll('[data-filter-toggle]').forEach((t) => t.setAttribute('aria-expanded', 'false'));
      if (opening) {{
        panel.removeAttribute('hidden');
        toggle.setAttribute('aria-expanded', 'true');
      }}
    }});
    // Close dropdown on outside click
    document.addEventListener('click', (e) => {{
      if (e.target.closest('.filter-dd')) return;
      if (e.target.closest('[data-filter-toggle]')) return;
      stage.querySelectorAll('.filter-dd').forEach((p) => p.setAttribute('hidden', ''));
      stage.querySelectorAll('[data-filter-toggle]').forEach((t) => t.setAttribute('aria-expanded', 'false'));
    }});
    // Done button — close only
    stage.addEventListener('click', (e) => {{
      const done = e.target.closest('[data-filter-close]');
      if (!done) return;
      const scope = done.dataset.filterClose;
      const panel = stage.querySelector('[data-filter-panel="' + scope + '"]');
      const toggle = stage.querySelector('[data-filter-toggle="' + scope + '"]');
      if (panel) panel.setAttribute('hidden', '');
      if (toggle) toggle.setAttribute('aria-expanded', 'false');
    }});
    // Reset button — clear filters within this dropdown (search stays)
    stage.addEventListener('click', (e) => {{
      const reset = e.target.closest('[data-filter-reset]');
      if (!reset) return;
      const scope = reset.dataset.filterReset;
      const panel = stage.querySelector('[data-filter-panel="' + scope + '"]');
      if (!panel) return;
      panel.querySelectorAll('.filter-dd-list').forEach((list) => {{
        list.querySelectorAll('.filter-dd-row').forEach((r) => r.classList.toggle('is-active', r.classList.contains('filter-dd-row-all')));
      }});
      scopeState(scope).filters = {{}};
      applyListing(scope);
    }});
    document.querySelectorAll('.proto-nav-btn').forEach(b => {{
      b.addEventListener('click', () => go(b.dataset.nav));
    }});

    // ---------- Voice: TTS ----------
    let _voice = null;
    function pickVoice() {{
      if (_voice || !window.speechSynthesis) return _voice;
      const voices = speechSynthesis.getVoices();
      _voice = voices.find(v => v.lang.startsWith('en') && /samantha|karen|susan|natural|nicky|serena|allison|zoe/i.test(v.name))
            || voices.find(v => v.lang.startsWith('en-US'))
            || voices.find(v => v.lang.startsWith('en'))
            || voices[0];
      return _voice;
    }}
    if (window.speechSynthesis) {{
      speechSynthesis.addEventListener?.('voiceschanged', pickVoice);
      pickVoice();
    }}
    function speak(text, onend) {{
      if (!window.speechSynthesis) {{ onend && onend(); return null; }}
      const u = new SpeechSynthesisUtterance(text);
      const v = pickVoice();
      if (v) u.voice = v;
      u.rate = 1.02; u.pitch = 1.02; u.volume = 1;
      if (onend) u.onend = onend;
      speechSynthesis.speak(u);
      return u;
    }}
    function stopSpeaking() {{ if (window.speechSynthesis) speechSynthesis.cancel(); }}

    // ---------- Voice: SpeechRecognition (mic) ----------
    let convoTimer = null;
    let convoTypeTimer = null;
    let convoAwaiting = false;
    let convoResumeFn = null;
    let convoRecognition = null;
    let convoRecognitionActive = false;
    function getRecognition() {{
      const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
      if (!SR) return null;
      if (!convoRecognition) {{
        convoRecognition = new SR();
        convoRecognition.lang = 'en-US';
        convoRecognition.interimResults = true;
        convoRecognition.continuous = false;
      }}
      return convoRecognition;
    }}

    // ---------- Convo UI helpers ----------
    function setConvoOrb(s) {{
      const orb = document.getElementById('convo-voice-orb');
      if (orb) orb.setAttribute('data-state', s);
    }}
    function setConvoStatus(text) {{
      const s = document.getElementById('convo-status');
      if (s) s.textContent = text;
    }}
    function showOrbFoot() {{
      const s = document.getElementById('convo-status');
      const orb = document.getElementById('convo-orb-btn');
      const cta = document.getElementById('convo-cta-btn');
      const foot = document.querySelector('.convo-foot');
      const voiceOrb = document.getElementById('convo-voice-orb');
      if (s) s.hidden = false;
      if (orb) orb.hidden = false;
      if (cta) cta.hidden = true;
      if (foot) foot.classList.remove('convo-foot-cta');
      if (voiceOrb) voiceOrb.classList.remove('convo-voice-orb-sm');
    }}
    function showCtaFoot() {{
      const s = document.getElementById('convo-status');
      const orb = document.getElementById('convo-orb-btn');
      const cta = document.getElementById('convo-cta-btn');
      const foot = document.querySelector('.convo-foot');
      const voiceOrb = document.getElementById('convo-voice-orb');
      if (s) s.hidden = true;
      if (orb) orb.hidden = false;
      if (voiceOrb) voiceOrb.classList.add('convo-voice-orb-sm');
      if (cta) cta.hidden = false;
      if (foot) foot.classList.add('convo-foot-cta');
    }}
    function showLiveCaption(text) {{
      const t = document.getElementById('convo-transcript');
      if (!t) return;
      let el = document.getElementById('convo-live-cap');
      if (!el) {{
        el = document.createElement('div');
        el.id = 'convo-live-cap';
        el.className = 'convo-live-caption';
        t.appendChild(el);
      }}
      if (text && text.trim().length) el.textContent = text;
      else el.innerHTML = '<span class="dots"><span></span><span></span><span></span></span>';
    }}
    function hideLiveCaption() {{
      const el = document.getElementById('convo-live-cap');
      if (el) el.remove();
    }}
    function ageOlderLines(t) {{
      const lines = [...t.querySelectorAll('.convo-line')];
      lines.slice(0, -1).forEach((el, idx) => {{
        const revIdx = lines.length - 1 - idx - 1;
        el.classList.remove('age-1','age-2','age-3','age-4','age-5','age-6');
        el.classList.add('age-' + Math.min(revIdx + 1, 6));
      }});
    }}
    // Strip leading "yes/sure/please note that" filler and return the remaining note content.
    function extractNoteFromResponse(text) {{
      let t = (text || '').trim();
      // Strip up to two levels of affirmative + connector words
      for (let k = 0; k < 3; k++) {{
        t = t.replace(/^(yes|yeah|yep|sure|definitely|absolutely|okay|ok|please)\b[,.\s]*/i, '');
        t = t.replace(/^(and|then|so|also)\b[,.\s]*/i, '');
        t = t.replace(/^(note that|note|add note|add that|add|write down|write|save that|save|remember that|remember|please note)\b[,.\s]*/i, '');
      }}
      return t.replace(/^[,.\s]+/, '').trim();
    }}

    // Detect "no / nope / nothing / not needed / no thanks / not necessary" style
    // replies so the agent doesn't dutifully write "no" into the note card.
    function isNegativeResponse(text) {{
      const t = (text || '').toLowerCase().trim().replace(/[.!?,]+/g, ' ').replace(/\s+/g, ' ');
      if (!t) return true;
      const words = t.split(/\s+/).filter(Boolean);
      // Positive kickoff means the user is dictating real content — never treat as negative
      if (/^(yes\b|yeah\b|yep\b|sure\b|definitely\b|absolutely\b|of course\b|add\b|note\b|write\b|save\b|please\b)/.test(t) && words.length > 2) return false;
      // Explicit short negatives
      if (/^(no|nope|nah|nothing|none|skip|pass|no way|not now|not really|no ?nothing)$/.test(t.replace(/\s+/g, ' '))) return true;
      // Common negation phrases anywhere in a short reply
      if (/\b(no need|not needed|not necessary|not required|nothing (to add|to say|else|much|here|important)|don'?t (need|add|bother|want)|no thanks?|no thank you|no notes?|no note|skip (it|this)|move on|next|all good|we'?re good|good to go|nevermind|never mind)\b/.test(t)) return true;
      // Very short response dominated by negation words
      const negWords = new Set(['no','not','nope','nah','nothing','none','skip','pass',"don't",'dont','nevermind','never','required','necessary','needed','now']);
      const hits = words.filter(w => negWords.has(w)).length;
      if (words.length <= 10 && hits >= 2) return true;
      if (words.length <= 4 && hits >= 1) return true;
      return false;
    }}
    // Detect "let's go / go / yes / start / ready / ok" style replies so the
    // driver can advance a CTA hands-free instead of tapping the button.
    function isGoResponse(text) {{
      const t = (text || '').toLowerCase().trim().replace(/[.!?,]+$/g, '');
      if (!t) return false;
      if (/^(go|yes|yep|yeah|yup|sure|ok|okay|ready|start|begin|proceed|continue|drive|roll)$/.test(t)) return true;
      if (/(let'?s go|let'?s do (it|this)|let'?s roll|let'?s ride|let'?s drive|let'?s start|let'?s begin|lets go|start (the )?(ride|drive|trip)|start driving|begin (the )?(ride|drive)|i'?m ready|ready to go|sounds good|looks good|good to go|go ahead|kick it off|fire it up|hit it|do it|send it|take me there|take off)/.test(t)) return true;
      return false;
    }}
    function appendConvoLine(item) {{
      const t = document.getElementById('convo-transcript');
      if (!t) return null;
      const line = document.createElement('div');
      line.className = 'convo-line' + (item.who === 'driver' ? ' driver' : '');
      if (item.text) line.textContent = item.text;
      const cap = document.getElementById('convo-live-cap');
      if (cap) t.insertBefore(line, cap); else t.appendChild(line);
      ageOlderLines(t);
      requestAnimationFrame(() => line.classList.add('enter'));
      return line;
    }}
    function appendPropertyCard() {{
      const t = document.getElementById('convo-transcript');
      if (!t) return;
      const s = currentStop(); if (!s) return;
      const wrap = document.createElement('div');
      wrap.className = 'convo-prop-card';
      const leadLabel = s.grade === 'A' ? 'Prime Lead' : s.grade === 'B' ? 'Strong Lead' : s.grade === 'C' ? 'Watchlist' : 'Low priority';
      wrap.innerHTML =
        '<article class="pfeat" tabindex="0" aria-label="'+s.addr+', Austin TX. Grade '+s.grade+' '+leadLabel+'. Est. value '+s.price+'.">'
      +   '<div class="pfeat-media">'
      +     '<img src="'+s.hero+'" alt="Property at '+s.addr+'" loading="lazy" onerror="this.parentElement.classList.add(\\'pfeat-media-fallback\\');this.remove()">'
      +     '<span class="pfeat-pill" data-grade="'+s.grade+'"><span class="pfeat-pill-dot">'+s.grade+'</span>'+leadLabel+'</span>'
      +     '<button class="pfeat-save" aria-pressed="false" aria-label="Save as lead" onclick="this.setAttribute(\\'aria-pressed\\', this.getAttribute(\\'aria-pressed\\')===\\'true\\'?\\'false\\':\\'true\\')">'
      +       '<i class="ph-bold ph-bookmark-simple" style="font-size:18px;line-height:1"></i>'
      +     '</button>'
      +   '</div>'
      +   '<div class="pfeat-body">'
      +     '<div class="pfeat-title-row"><h4 class="pfeat-title">'+s.addr+'</h4><div class="pfeat-price">'+s.price+'<span class="pfeat-unit">/'+s.arv+'</span></div></div>'
      +     '<p class="pfeat-tag">'+s.desc+'</p>'
      +   '</div>'
      +   '<div class="pfeat-stats">'
      +     '<div class="pfeat-stat"><span class="pfeat-stat-ico"><i class="ph-bold ph-bed" style="font-size:16px;line-height:1"></i></span>Bed: <b>'+s.bed+'</b></div>'
      +     '<div class="pfeat-stat"><span class="pfeat-stat-ico"><i class="ph-bold ph-bathtub" style="font-size:16px;line-height:1"></i></span>Baths: <b>'+s.bath+'</b></div>'
      +     '<div class="pfeat-stat"><span class="pfeat-stat-ico"><i class="ph-bold ph-ruler" style="font-size:16px;line-height:1"></i></span>Sqft: <b>'+s.sqft+'</b></div>'
      +   '</div>'
      + '</article>';
      const cap = document.getElementById('convo-live-cap');
      if (cap) t.insertBefore(wrap, cap); else t.appendChild(wrap);
      requestAnimationFrame(() => wrap.classList.add('enter'));
    }}
    function appendScanningLine() {{
      const t = document.getElementById('convo-transcript');
      if (!t) return;
      const el = document.createElement('div');
      el.id = 'convo-scan-line';
      el.className = 'convo-scan-line';
      el.innerHTML = '<span class="scan-spinner"></span><span>Scanning property</span>';
      const cap = document.getElementById('convo-live-cap');
      if (cap) t.insertBefore(el, cap); else t.appendChild(el);
    }}
    function removeScanningLine() {{
      const el = document.getElementById('convo-scan-line');
      if (el) el.remove();
    }}
    function appendScanResultsCard() {{
      const t = document.getElementById('convo-transcript');
      if (!t) return;
      const s = currentStop(); if (!s) return;
      const wrap = document.createElement('div');
      wrap.className = 'convo-scan-card';
      const photos = [
        'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=800&h=500&q=70',
        'https://images.unsplash.com/photo-1600596542815-ffad4c1539a9?auto=format&fit=crop&w=800&h=500&q=70',
        'https://images.unsplash.com/photo-1502005229762-cf1b2da7c5d6?auto=format&fit=crop&w=800&h=500&q=70',
      ];
      const tagStr = (s.tags || []).join(', ');
      const imgs = photos.map((p, i) =>
        '<img class="findings-photo'+(i===0?' active':'')+'" src="'+p+'" alt="Scan finding" loading="lazy">'
      ).join('');
      const dots = photos.map((_, i) => '<span'+(i===0?' class="active"':'')+'></span>').join('');
      wrap.innerHTML =
        '<div class="findings-card">'
      + '<div class="findings-carousel">'
      +   imgs
      +   '<div class="findings-dots">'+dots+'</div>'
      + '</div>'
      + '<div class="findings-body">'
      +   '<div class="finding-row"><i class="ph-bold ph-house-line"></i><div><span class="findings-label">Condition</span><span class="findings-value">Distressed — '+tagStr+'</span></div></div>'
      +   '<div class="finding-row"><i class="ph-bold ph-user"></i><div><span class="findings-label">Owner</span><span class="findings-value">Absent · 14 yr tenure · 62% equity</span></div></div>'
      +   '<div class="finding-row"><i class="ph-bold ph-gavel"></i><div><span class="findings-label">Records</span><span class="findings-value">Tax lien filed 2024 · no active listing</span></div></div>'
      +   '<div class="finding-row"><i class="ph-bold ph-phone"></i><div><span class="findings-label">Skip trace</span><span class="findings-value">2 numbers · 1 email on file</span></div></div>'
      + '</div>'
      + '</div>';
      const cap = document.getElementById('convo-live-cap');
      if (cap) t.insertBefore(wrap, cap); else t.appendChild(wrap);
      requestAnimationFrame(() => wrap.classList.add('enter'));
      // Auto-rotate carousel every 2.4s
      const photoEls = wrap.querySelectorAll('.findings-photo');
      const dotEls   = wrap.querySelectorAll('.findings-dots span');
      let idx = 0;
      wrap._interval = setInterval(() => {{
        idx = (idx + 1) % photoEls.length;
        photoEls.forEach((el, i) => el.classList.toggle('active', i === idx));
        dotEls.forEach((el, i) => el.classList.toggle('active', i === idx));
      }}, 2400);
    }}
    function appendTagsCampaignCard() {{
      const t = document.getElementById('convo-transcript');
      if (!t) return;
      const s = currentStop(); if (!s) return;
      const wrap = document.createElement('div');
      wrap.className = 'convo-tags-card';
      const chips = (s.tags || []).map(tag =>
        '<button class="tag-chip" data-tag="'+tag+'">'+tag+'<span class="tag-x">×</span></button>'
      ).join('');
      wrap.innerHTML =
        '<div class="tags-card">'
      + '<div>'
      +   '<div class="tags-card-section-label">Suggested tags</div>'
      +   '<div class="tags-card-chips" id="tags-card-chips">'+chips+'<button class="tag-chip tag-add">+ add</button></div>'
      + '</div>'
      + '<div>'
      +   '<div class="tags-card-section-label">Campaign fit</div>'
      +   '<div class="tags-card-campaign"><div class="tags-card-campaign-body"><div class="tags-card-campaign-name">'+s.campaign+' campaign</div><div class="tags-card-campaign-reason">'+s.reason+'</div></div></div>'
      + '</div>'
      + '</div>';
      const cap = document.getElementById('convo-live-cap');
      if (cap) t.insertBefore(wrap, cap); else t.appendChild(wrap);
      requestAnimationFrame(() => wrap.classList.add('enter'));
      // Wire chip removal
      wrap.addEventListener('click', (e) => {{
        const chip = e.target.closest('.tag-chip:not(.tag-add)');
        if (!chip) return;
        if (e.target.closest('.tag-x')) chip.remove();
      }});
    }}
    function appendSummaryCard() {{
      const t = document.getElementById('convo-transcript');
      if (!t) return;
      const s = currentStop(); if (!s) return;
      // Snapshot current tag chips (may have been edited by user).
      const chips = [...document.querySelectorAll('#tags-card-chips .tag-chip:not(.tag-add)')];
      const tags = chips.map(c => (c.textContent || '').replace(/\s*×\s*$/, '').trim()).filter(Boolean);
      const noteEl = document.getElementById('convo-note-text');
      const hasNote = noteEl && !noteEl.classList.contains('empty');
      const noteText = hasNote ? noteEl.textContent : '';
      const wrap = document.createElement('div');
      wrap.className = 'convo-summary-card';
      wrap.innerHTML =
        '<div class="summary-card">'
      + '<div class="summary-card-hero" style="background-image:url(\\''+s.hero+'\\')">'
      +   '<span class="summary-card-check"><i class="ph-bold ph-check" style="font-size:14px;line-height:1"></i></span>'
      + '</div>'
      + '<div class="summary-card-body">'
      +   '<div class="summary-card-title">'+s.addr+'</div>'
      +   '<div class="summary-card-sub">Austin, TX · '+s.price+'/'+s.arv+'</div>'
      +   '<div class="summary-rows">'
      +     '<div class="summary-row"><span class="summary-label">Tags</span><span class="summary-value">'+(tags.join(', ') || 'None')+'</span></div>'
      +     '<div class="summary-row"><span class="summary-label">Campaign</span><span class="summary-value">'+s.campaign+'</span></div>'
      +     '<div class="summary-row"><span class="summary-label">Photos</span><span class="summary-value">3 attached</span></div>'
      +     (hasNote ? '<div class="summary-row"><span class="summary-label">Note</span><span class="summary-value">'+noteText+'</span></div>' : '')
      +   '</div>'
      + '</div>'
      + '</div>';
      const cap = document.getElementById('convo-live-cap');
      if (cap) t.insertBefore(wrap, cap); else t.appendChild(wrap);
      requestAnimationFrame(() => wrap.classList.add('enter'));
    }}

    function appendNoteCard() {{
      const t = document.getElementById('convo-transcript');
      if (!t) return;
      const wrap = document.createElement('div');
      wrap.className = 'convo-note-card';
      wrap.id = 'convo-note-card';
      wrap.innerHTML =
        '<div class="note-card">'
      + '<div class="note-card-label">Your note</div>'
      + '<div class="note-card-text empty" id="convo-note-text">Listening…</div>'
      + '</div>';
      const cap = document.getElementById('convo-live-cap');
      if (cap) t.insertBefore(wrap, cap); else t.appendChild(wrap);
      requestAnimationFrame(() => wrap.classList.add('enter'));
      return wrap;
    }}
    function setNoteText(text) {{
      const el = document.getElementById('convo-note-text');
      if (!el) return;
      if (text && text.trim()) {{
        el.textContent = text.trim();
        el.classList.remove('empty');
      }} else {{
        el.textContent = 'Listening…';
        el.classList.add('empty');
      }}
    }}

    // ---------- Awaiting real driver speech (never fabricated) ----------
    function awaitDriverInput(done, opts) {{
      opts = opts || {{}};
      const showAsNote = !!opts.asNote; // if true, write final into the note card
      showLiveCaption('');
      setConvoOrb('listening');
      const rec = getRecognition();
      let captured = '';
      let finished = false;
      const finish = (text) => {{
        if (finished) return;
        const clean = (text || '').trim();
        if (!clean) return;
        finished = true;
        convoRecognitionActive = false;
        convoAwaiting = false;
        convoResumeFn = null;
        hideLiveCaption();
        try {{ rec && rec.stop(); }} catch(_) {{}}
        done(clean);
      }};
      if (rec) {{
        setConvoStatus('Listening…');
        rec.onresult = (e) => {{
          let final = '', interim = '';
          for (let k = e.resultIndex; k < e.results.length; k++) {{
            const r = e.results[k];
            if (r.isFinal) final += r[0].transcript;
            else interim += r[0].transcript;
          }}
          captured += final;
          const combined = (captured + ' ' + interim).trim();
          if (showAsNote) setNoteText(combined);
          else showLiveCaption(combined);
        }};
        rec.onerror = (ev) => {{
          if (ev && ev.error === 'not-allowed') {{
            setConvoStatus('Mic permission needed to continue');
            convoRecognitionActive = false;
          }}
        }};
        rec.onend = () => {{
          convoRecognitionActive = false;
          const text = captured.trim();
          if (text) {{ finish(text); return; }}
          if (finished) return;
          setTimeout(() => {{
            if (finished) return;
            try {{ rec.start(); convoRecognitionActive = true; }} catch(_) {{}}
          }}, 200);
        }};
        try {{ rec.start(); convoRecognitionActive = true; }}
        catch(_) {{ setConvoStatus('Voice input unavailable'); }}
      }} else {{
        setConvoStatus('Voice input not supported here');
      }}
      convoAwaiting = true;
      convoResumeFn = () => {{
        const text = captured.trim();
        if (!text) return; // still waiting
        if (rec && convoRecognitionActive) {{ try {{ rec.stop(); }} catch(_) {{ finish(text); }} }}
        else finish(text);
      }};
    }}

    // ---------- Word-by-word agent typing, TTS-paced ----------
    const CONVO_FALLBACK_WPM = 155;
    function typeAndSpeakAgentLine(item, done) {{
      const line = appendConvoLine({{ who: 'agent', text: '' }});
      if (!line) {{ done && done(); return; }}
      const text = item.text;
      const words = text.split(/(\\s+)/);
      let typingDone = false, ttsDone = false, doneCalled = false;
      let boundaryFired = false;
      let idx = 0;
      const tryFinish = () => {{
        if (doneCalled) return;
        if (typingDone && ttsDone) {{
          doneCalled = true;
          line.textContent = text;
          done && done();
        }}
      }};
      const perWordMs = Math.round(60000 / CONVO_FALLBACK_WPM);
      const tick = () => {{
        if (boundaryFired) return;
        if (idx >= words.length) {{ typingDone = true; tryFinish(); return; }}
        line.textContent += words[idx++];
        convoTypeTimer = setTimeout(tick, perWordMs);
      }};
      setConvoOrb('speaking');
      setConvoStatus('Speaking');
      const u = speak(text, () => {{
        ttsDone = true;
        line.textContent = text;
        typingDone = true;
        if (convoTypeTimer) {{ clearTimeout(convoTypeTimer); convoTypeTimer = null; }}
        tryFinish();
      }});
      if (u) {{
        u.onboundary = (e) => {{
          if (e.name && e.name !== 'word') return;
          boundaryFired = true;
          if (convoTypeTimer) {{ clearTimeout(convoTypeTimer); convoTypeTimer = null; }}
          const end = e.charIndex + (e.charLength || 0);
          line.textContent = text.slice(0, end);
        }};
      }}
      tick();
    }}

    // ---------- Scripts ----------
    const introScript = [
      {{ who: 'agent', text: "Morning Joe. Before I map out your drive today — are there any constraints I should know about?", awaitInput: true }},
      {{ who: 'agent', text: "Thank you for letting me know. Planning the route for you accordingly." }},
      {{ type: 'thinking', duration: 2600 }},
      {{ type: 'route-card' }},
      {{ who: 'agent', text: "Here's the devised plan. Ready to start the ride?", final: true, ctaText: "Let's Go", ctaNav: 'drive-start' }},
    ];
    function buildInspectScript() {{
      const s = currentStop();
      return [
        {{ type: 'property-card' }},
        {{ who: 'agent', text: "Reached at " + s.addr + "." }},
        {{ type: 'pause', duration: 1200 }},
        {{ who: 'agent', text: "Let me scan the property for you." }},
        {{ type: 'scanning', duration: 3200 }},
        {{ type: 'scan-results' }},
        {{ who: 'agent', text: "Here are further details about the property. Would you like to continue working on it as a potential lead?", awaitInput: true }},
        {{ who: 'agent', text: "Great. Here are the tags and campaign I'm suggesting." }},
        {{ type: 'tags-card' }},
        {{ who: 'agent', text: "Any adjustments?", awaitInput: true }},
        {{ type: 'note-flow' }},
        {{ type: 'summary-card' }},
        {{ type: 'save-confirm' }},
      ];
    }}
    function appendRouteCard() {{
      const t = document.getElementById('convo-transcript');
      if (!t) return;
      const wrap = document.createElement('div');
      wrap.className = 'convo-route-card';
      wrap.innerHTML =
        '<div class="route-card">'
      + '<div class="route-map">'
      +   '<svg viewBox="0 0 320 200" xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="xMidYMid slice" aria-hidden="true">'
      +   '<rect width="320" height="200" fill="var(--panel-2, #F5F1EA)"/>'
      +   '<path d="M 0 0 L 100 0 L 70 70 L 0 90 Z" fill="var(--colors-neutral_100, #EDEBE6)" opacity=".7"/>'
      +   '<path d="M 230 150 L 320 130 L 320 200 L 210 200 Z" fill="var(--colors-neutral_100, #EDEBE6)" opacity=".9"/>'
      +   '<path d="M 20 70 C 100 90, 180 40, 310 80" stroke="#fff" stroke-width="6" fill="none"/>'
      +   '<path d="M 40 180 C 120 160, 200 200, 300 170" stroke="#fff" stroke-width="6" fill="none"/>'
      +   '<path d="M 70 20 L 90 195" stroke="#fff" stroke-width="4" fill="none"/>'
      +   '<path d="M 200 10 L 180 200" stroke="#fff" stroke-width="4" fill="none"/>'
      +   '<path d="M 40 155 C 80 135, 100 115, 140 95 S 220 120, 258 62" stroke="var(--colors-primarybutton_bg_active, #D93131)" stroke-width="3" stroke-linecap="round" stroke-dasharray="1 6" fill="none"/>'
      +   '<circle cx="40" cy="155" r="8" fill="var(--colors-primarybutton_bg_active, #D93131)"/><circle cx="40" cy="155" r="3" fill="#fff"/>'
      +   '<circle cx="90" cy="125" r="8" fill="#fff"/><circle cx="90" cy="125" r="5" fill="var(--gradecolors-grade_a, #1A7F42)"/>'
      +   '<circle cx="140" cy="95" r="8" fill="#fff"/><circle cx="140" cy="95" r="5" fill="var(--gradecolors-grade_a, #1A7F42)"/>'
      +   '<circle cx="195" cy="108" r="8" fill="#fff"/><circle cx="195" cy="108" r="5" fill="var(--gradecolors-grade_b, #E8A317)"/>'
      +   '<circle cx="230" cy="88" r="8" fill="#fff"/><circle cx="230" cy="88" r="5" fill="var(--gradecolors-grade_c, #D93025)"/>'
      +   '<path d="M 258 50 C 251 50, 246 55, 246 62 C 246 72, 258 84, 258 84 C 258 84, 270 72, 270 62 C 270 55, 265 50, 258 50 Z" fill="var(--colors-primarybutton_bg_active, #D93131)"/><circle cx="258" cy="62" r="3" fill="#fff"/>'
      +   '</svg>'
      + '</div>'
      + '<div class="route-info"><div class="route-info-head"><i class="ph-bold ph-map-trifold" style="font-size:12px;line-height:1"></i><span>Route area</span></div><div class="route-info-title">78701 · East Austin loop</div><div class="route-info-meta"><span>12 properties</span><span class="route-info-dot"></span><span>4.2 mi</span></div></div>'
      + '</div>';
      const cap = document.getElementById('convo-live-cap');
      if (cap) t.insertBefore(wrap, cap); else t.appendChild(wrap);
      requestAnimationFrame(() => wrap.classList.add('enter'));
    }}

    // ---------- Runner ----------
    function stopConvoSequence() {{
      if (convoTimer) {{ clearTimeout(convoTimer); convoTimer = null; }}
      if (convoTypeTimer) {{ clearTimeout(convoTypeTimer); convoTypeTimer = null; }}
      if (convoRecognition && convoRecognitionActive) {{ try {{ convoRecognition.abort(); }} catch(_) {{}} }}
      convoRecognitionActive = false;
      convoAwaiting = false;
      convoResumeFn = null;
      hideLiveCaption();
      removeScanningLine();
      showOrbFoot();
      stopSpeaking();
    }}
    function runConvoSequence(mode) {{
      stopConvoSequence();
      showOrbFoot();
      const script = (mode === 'inspect') ? buildInspectScript() : introScript;
      const t = document.getElementById('convo-transcript');
      if (!t) return;
      t.innerHTML = '';
      let i = 0;
      function next() {{
        if (i >= script.length) {{
          setConvoOrb('idle'); setConvoStatus('Tap to talk');
          return;
        }}
        const item = script[i++];
        if (item.type === 'thinking') {{
          setConvoOrb('thinking'); setConvoStatus('Planning route');
          convoTimer = setTimeout(next, item.duration || 2200);
          return;
        }}
        if (item.type === 'route-card')     {{ appendRouteCard();     convoTimer = setTimeout(next, 600); return; }}
        if (item.type === 'property-card')  {{ appendPropertyCard();  convoTimer = setTimeout(next, 500); return; }}
        if (item.type === 'pause')          {{ setConvoOrb('idle'); setConvoStatus(''); convoTimer = setTimeout(next, item.duration || 2000); return; }}
        if (item.type === 'scan-results')   {{ appendScanResultsCard(); convoTimer = setTimeout(next, 600); return; }}
        if (item.type === 'tags-card')      {{ appendTagsCampaignCard(); convoTimer = setTimeout(next, 500); return; }}
        if (item.type === 'note-card')      {{ appendNoteCard(); convoTimer = setTimeout(next, 400); return; }}
        if (item.type === 'scanning') {{
          setConvoOrb('thinking'); setConvoStatus('Scanning property');
          convoTimer = setTimeout(next, item.duration || 2500);
          return;
        }}
        if (item.type === 'note-flow') {{
          // Single question: "Any note?" — intelligently act on the reply.
          // • Pure negation → skip.
          // • Reply contains an actual note ("yes, owner is retiring") → save the note part.
          // • Bare "yes"/"sure" → open the note card and quietly listen for more.
          typeAndSpeakAgentLine({{ text: "Would you like to add any note?" }}, () => {{
            awaitDriverInput((response) => {{
              appendConvoLine({{ who: 'driver', text: response }});
              if (isNegativeResponse(response)) {{
                setConvoOrb('thinking'); setConvoStatus('Thinking');
                convoTimer = setTimeout(next, 700);
                return;
              }}
              appendNoteCard();
              const inline = extractNoteFromResponse(response);
              if (inline) {{
                setNoteText(inline);
                setConvoOrb('thinking'); setConvoStatus('Thinking');
                convoTimer = setTimeout(next, 900);
              }} else {{
                // Just "yes" / "sure" — keep listening silently until they say the note.
                awaitDriverInput((dictated) => {{
                  if (isNegativeResponse(dictated)) {{
                    document.getElementById('convo-note-card')?.remove();
                    setConvoOrb('thinking'); setConvoStatus('Thinking');
                    convoTimer = setTimeout(next, 700);
                    return;
                  }}
                  setNoteText(dictated);
                  setConvoOrb('thinking'); setConvoStatus('Thinking');
                  convoTimer = setTimeout(next, 900);
                }}, {{ asNote: true }});
              }}
            }});
          }});
          return;
        }}
        if (item.type === 'summary-card')  {{ appendSummaryCard(); convoTimer = setTimeout(next, 500); return; }}
        if (item.type === 'save-confirm') {{
          typeAndSpeakAgentLine({{ text: "Property created. Should I go ahead and save it as a potential lead?" }}, () => {{
            awaitDriverInput((response) => {{
              appendConvoLine({{ who: 'driver', text: response }});
              if (isNegativeResponse(response)) {{
                // Discard — just advance without saving.
                typeAndSpeakAgentLine({{ text: "No problem. Moving on." }}, () => {{
                  setTimeout(() => go('drive-next'), 500);
                }});
                return;
              }}
              const savedAddr = currentStop().addr;
              typeAndSpeakAgentLine({{ text: "Saved as a potential lead." }}, () => {{
                scheduleDriveToast(savedAddr + ' saved as potential lead');
                setTimeout(() => go('drive-next'), 500);
              }});
            }});
          }});
          return;
        }}
        if (item.who === 'agent') {{
          typeAndSpeakAgentLine(item, () => {{
            if (item.final) {{
              setConvoOrb('idle');
              const cta = document.getElementById('convo-cta-btn');
              if (cta) {{ cta.textContent = item.ctaText || "Let's Go"; cta.dataset.nav = item.ctaNav || 'drive-start'; }}
              showCtaFoot();
              const navTarget = (cta && cta.dataset.nav) || item.ctaNav || 'drive-start';
              const listenForGo = () => {{
                awaitDriverInput((spoken) => {{
                  appendConvoLine({{ who: 'driver', text: spoken }});
                  if (isGoResponse(spoken)) {{
                    stopConvoSequence();
                    go(navTarget);
                  }} else {{
                    // Not a go command — keep the CTA on-screen and re-arm the mic.
                    setConvoOrb('idle');
                    convoTimer = setTimeout(listenForGo, 300);
                  }}
                }});
              }};
              listenForGo();
              return;
            }}
            if (item.awaitInput) {{
              awaitDriverInput((spoken) => {{
                appendConvoLine({{ who: 'driver', text: spoken }});
                setConvoOrb('thinking'); setConvoStatus('Thinking');
                convoTimer = setTimeout(next, 900);
              }});
            }} else if (item.awaitInputAsNote) {{
              awaitDriverInput((spoken) => {{
                setNoteText(spoken);
                setConvoOrb('thinking'); setConvoStatus('Thinking');
                convoTimer = setTimeout(next, 900);
              }}, {{ asNote: true }});
            }} else {{
              setConvoOrb('idle'); setConvoStatus('');
              convoTimer = setTimeout(next, item.pause || 400);
            }}
          }});
        }} else {{
          setConvoOrb('thinking'); setConvoStatus('Thinking');
          appendConvoLine(item);
          convoTimer = setTimeout(next, 900);
        }}
      }}
      next();
    }}

    // Orb tap: force-finish listening only if we have captured speech
    document.getElementById('convo-orb-btn')?.addEventListener('click', (e) => {{
      if (!convoAwaiting) return;
      if (convoResumeFn === 'nav') {{ convoAwaiting = false; convoResumeFn = null; return; }}
      e.preventDefault(); e.stopPropagation();
      const fn = convoResumeFn;
      if (typeof fn === 'function') fn();
    }}, true);

    // Chip toggle at property stop (legacy)
    stage.addEventListener('click', (e) => {{
      const c = e.target.closest('.chip-toggle');
      if (!c) return;
      c.classList.toggle('chip-suggested');
      c.classList.toggle('chip-confirmed');
    }});

    // init
    go('home');
  }})();

  // ==================== Real map (Leaflet) ====================
  function initHomeMap() {{
    if (typeof L === 'undefined') return;
    const el = document.getElementById('home-real-map');
    if (!el || el.dataset.ready === '1') return;
    el.dataset.ready = '1';
    const map = L.map(el, {{
      center: [30.2672, -97.7431],
      zoom: 16,
      zoomControl: false,
      attributionControl: false,
      dragging: true, tap: true,
      scrollWheelZoom: true, doubleClickZoom: true,
      touchZoom: true, boxZoom: false, keyboard: false,
    }});
    L.tileLayer('https://tiles.stadiamaps.com/tiles/alidade_smooth/{{z}}/{{x}}/{{y}}{{r}}.png', {{
      maxZoom: 20, crossOrigin: true,
    }}).addTo(map);
    const pin = (grade) => L.divIcon({{
      className: 'lpin g-' + grade.toLowerCase(),
      html: grade, iconSize: [26, 26], iconAnchor: [13, 13],
    }});
    const you = L.divIcon({{
      className: 'lyou', html: '', iconSize: [16, 16], iconAnchor: [8, 8],
    }});
    // 6 properties clustered around downtown Austin (matches "Oak Valley · 6 properties" pill)
    const pins = [
      ['A', 30.2688, -97.7452],
      ['A', 30.2665, -97.7418],
      ['B', 30.2680, -97.7405],
      ['B', 30.2650, -97.7440],
      ['C', 30.2645, -97.7415],
      ['D', 30.2695, -97.7425],
    ];
    pins.forEach(([g, lat, lng]) => L.marker([lat, lng], {{icon: pin(g)}}).addTo(map));
    L.marker([30.2660, -97.7430], {{icon: you}}).addTo(map);
    el._leaflet_map = map;
    // Recompute after layout settles
    setTimeout(() => map.invalidateSize(), 100);
  }}
  if (document.readyState === 'complete') initHomeMap();
  else window.addEventListener('load', initHomeMap);

  // ==================== Zone chip → properties panel ====================
  (function () {{
    const chip = document.getElementById('home-zone-chip');
    const closeBtn = document.getElementById('home-properties-close');
    if (!chip || !closeBtn) return;
    const home = chip.closest('.scr-home');
    if (!home) return;
    const invalidate = () => {{
      const el = document.getElementById('home-real-map');
      if (el && el._leaflet_map) el._leaflet_map.invalidateSize();
    }};
    const setOpen = (open) => {{
      home.classList.toggle('properties-open', open);
      chip.setAttribute('aria-expanded', open ? 'true' : 'false');
      setTimeout(invalidate, 60);
    }};
    chip.addEventListener('click', (e) => {{ e.stopPropagation(); setOpen(!home.classList.contains('properties-open')); }});
    closeBtn.addEventListener('click', (e) => {{ e.stopPropagation(); setOpen(false); }});
  }})();

  // ==================== live-reload (dev only) ====================
  (function () {{
    let lastMod = null;
    setInterval(async () => {{
      try {{
        const r = await fetch(location.pathname, {{ method: 'HEAD', cache: 'no-store' }});
        const m = r.headers.get('last-modified');
        if (lastMod && m && m !== lastMod) location.reload();
        lastMod = m;
      }} catch (e) {{}}
    }}, 800);
  }})();
</script>
</body>
</html>
"""

with open(OUT, "w") as f:
    f.write(HTML)

print(f"wrote {OUT} ({len(HTML):,} bytes)")
