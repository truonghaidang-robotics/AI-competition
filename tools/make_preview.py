"""Build static previews of app.py's styled views (visual checking only).

Renders the landing view and the (post-generation) results view using the app's
own <style> block and markup shapes, with generated PNG assets inlined.

Run:  python tools/make_preview.py
"""

import base64
import html
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, "app.py")
ASSETS = os.path.join(ROOT, "assets")
OUT_DIR = os.path.join(ROOT, ".preview")
os.makedirs(OUT_DIR, exist_ok=True)

src = open(APP, encoding="utf-8").read()
style = re.search(r"<style>(.*?)</style>", src, re.DOTALL).group(1)


def uri(name):
    with open(os.path.join(ASSETS, name), "rb") as fh:
        return "data:image/png;base64," + base64.b64encode(fh.read()).decode("ascii")


def img(name, cls=None, alt=""):
    c = f" class='{cls}'" if cls else ""
    return f"<img src='{uri(name)}'{c} alt='{alt}' />"


def sec(title, ic_name):
    return (
        f"<div class='sec-head'>{img(ic_name, 'ic-inline')}"
        f"<span class='sec-title'>{title}</span></div>"
    )


def sub(title, ic_name):
    return (
        f"<div class='sub-head'>{img(ic_name, 'ic-inline')}{title}</div>"
    )


PIPELINE = [
    ("icon_selection.png", "Selection Agent", "Data Cleansing"),
    ("icon_content.png", "Content Agent", "PR Scripting"),
    ("icon_compliance.png", "Visual Guard Agent", "Compliance Check"),
    ("icon_jimeng.png", "Jimeng Node", "AI Visual &amp; Video"),
]

TITLES = [
    "Men's shoe rack really needs one universal pair! Matches every outfit",
    "This commuter sneaker keeps your feet happy all day long",
    "Minimalist white sneakers — how to choose? These go with everything",
]

SIDEBAR = f"""
  <aside class="fake-sidebar">
    <div class="side-title">Control Center</div>
    <h4>System Status</h4>
    <div class="status-chip"><span class="dot"></span>Coze API: Active</div>
    <div class="status-chip"><span class="dot"></span>Jimeng AI Engine: Connected</div>
    <hr />
    <h4>Agents Pipeline Monitor</h4>
    {''.join(f"<div class='pipeline-row'>{img(i)}<div><span class='p-name'>{n}</span><span class='p-role'>{r}</span></div></div>" for i, n, r in PIPELINE)}
    <hr />
    <p class="side-caption">EchoCommerce Studio v4.0 | Pure Coze Engine</p>
  </aside>
"""

BRAND_BAR = f"""
    <div class="hero-wrap">
      <div class="hero-logo">{img('robot_avatar.png', alt='avatar')}</div>
      <div>
        <div class="hero-name">EchoCommerce Studio</div>
        <div class="hero-sub">KOC Automatic Marketing Studio &middot; Coze AI Engine</div>
      </div>
      <div class="hero-spacer"></div>
      <div class="status-pill"><span class="dot"></span>All Systems Online</div>
    </div>
"""

HERO_TEXT = """
    <div class="hero-badge">Unleash Your Creative Potential</div>
    <h1 class="hero-title">Fastest &amp; Easiest Way to Generate Viral KOC Content</h1>
    <p class="hero-lead">Paste one product link and Coze AI writes the full PR script,
      suggests high-converting titles, renders 3D product visuals and produces the AI
      commercial video &mdash; automatically, in a single click.</p>
"""

BASE_CSS = f"""
  body {{ margin: 0; background: #120A05; }}
  .shell {{ display: flex; min-height: 100vh; }}
  .fake-sidebar {{ width: 306px; flex: 0 0 306px; padding: 26px 20px;
    background: linear-gradient(180deg, #1E1209 0%, #100804 100%);
    border-right: 1px solid rgba(255,149,61,0.16); }}
  .fake-sidebar h4 {{ margin: 6px 0 12px; font-size: 1.02rem; }}
  .fake-sidebar hr {{ border: none; border-top: 1px solid rgba(255,149,61,0.18); margin: 1rem 0; }}
  .side-caption {{ color: #A08573; font-size: 0.78rem; }}
  .fake-main {{ flex: 1 1 auto; padding: 34px 46px 70px 46px; max-width: 1150px; }}
  .tabbar {{ display: flex; gap: 8px; background: rgba(22,13,6,0.6);
    border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 6px; margin-bottom: 14px; }}
  .tabbar span {{ padding: 9px 15px; border-radius: 11px; color: #C6A995; font-weight: 600; font-size: 0.9rem; }}
  .tabbar span.on {{ background: linear-gradient(95deg, rgba(226,58,0,0.92), rgba(255,150,20,0.85)); color: #fff; }}
  .field {{ background: rgba(22,13,6,0.78); border: 1px solid rgba(255,255,255,0.11);
    border-radius: 14px; padding: 15px 16px; color: #9C8570; font-size: 0.98rem; font-weight: 600; }}
  .cols {{ display: flex; gap: 26px; align-items: flex-start; }}
  .mediabox {{ background: rgba(22,13,6,0.6); border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px; height: 190px; display: flex; align-items: center; justify-content: center;
    color: #9C8570; font-weight: 600; font-size: 0.9rem; }}
"""


def page(title, main, extra_css=""):
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8" /><title>{title}</title>
<style>{style}</style>
<style>{BASE_CSS}{extra_css}</style>
</head><body>
<div class="shell">{SIDEBAR}<main class="fake-main">{main}</main></div>
</body></html>
"""


# ------------------------------------------------------------------ landing view
landing = page(
    "EchoCommerce — landing",
    f"""
    <style>.hero-stage {{ --hero-art: url("{uri('hero_ai_robot.png')}"); }}</style>
    <div class="hero-stage">
      <div class="hero-inner">
        <div class="hero-badge">Unleash Your Creative Potential</div>
        <h1 class="hero-title">Fastest &amp; Easiest Way to Generate Viral KOC Content</h1>
        <p class="hero-lead">Paste one product link and Coze AI writes the full PR script,
          suggests high-converting titles, renders 3D product visuals and produces the AI
          commercial video &mdash; automatically, in a single click.</p>
      </div>
    </div>
    {BRAND_BAR}
    <div class="cols" style="margin-top:6px;">
      <div class="field" style="flex:3.5; font-weight:500;">Paste a Taobao link or sharing text here...</div>
      <div class="stButton" style="flex:1.2;"><button>{img('ic_bolt.png', 'ic-inline')}Generate 1-Click Content</button></div>
    </div>
    <img class="wave-foot" src="{uri('motif_waves.png')}" alt="" />
    """,
)

# ------------------------------------------------------------------ results view
left_card = f"""
      {sec('KOC-Ready Marketing Content', 'ic_doc.png')}
      <div class="tabbar"><span class="on">Top 3 Hot Titles</span><span>PR Article</span><span>Comment &amp; CTA</span><span>1-Click Copy</span></div>
      <div class="badge-status">TITLE SUGGESTIONS</div>
      {''.join(f"<div class='title-pill'>{t}</div>" for t in TITLES)}
      <hr style="border:none;border-top:1px solid rgba(255,255,255,0.1);margin:22px 0;" />
      {sub('CS Bot Agent Script (Auto-Reply to Clients)', 'ic_bot.png')}
      <p style="color:#C6A995;">Auto-reply mode for comments is enabled.</p>
      <div class="stButton" style="margin-top:14px;"><button>{img('ic_bot.png', 'ic-inline')}{html.unescape('Auto-Publish Post &amp; Enable Live Comment Bot')}</button></div>
"""

right_card = f"""
      {sec('3D Visual Asset (Jimeng AI)', 'ic_image.png')}
      <div class="mediabox">3D product concept image from Coze Jimeng AI</div>
      <hr style="border:none;border-top:1px solid rgba(255,255,255,0.1);margin:22px 0;" />
      {sub('Commercial Video (Jimeng AI Video)', 'ic_video.png')}
      <div class="mediabox">AI video rendered automatically by Coze</div>
"""

results = page(
    "EchoCommerce — results",
    f"""
    {BRAND_BAR}
    <p style="color:#9C8570;font-size:0.92rem;margin:0 0 18px 0;">🔗 Taobao product link pasted · Coze Workflow completed</p>
    <div class="cols">
      <div style="flex:1.2;"><div class="glass-card">{left_card}</div></div>
      <div style="flex:1;"><div class="glass-card">{right_card}</div></div>
    </div>
    <div class="glass-card" style="margin-top:18px;color:#C6A995;">
      {img('ic_copy.png', 'ic-inline')} <b style="color:#FFF6EE;">[Technical Report]</b> Detailed JSON log from the Coze Workflow
    </div>
    """,
)

for name, content in (("landing", landing), ("results", results)):
    out = os.path.join(OUT_DIR, f"{name}.html")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(content)
    print("preview:", out, len(content), "chars")
