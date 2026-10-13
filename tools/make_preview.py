"""Static previews of app.py's styled UI in both languages (visual checking only).

Renders landing + results views for EN and ZH using the app's own <style> block
and translation table, with generated PNG assets inlined.

Run:  python tools/make_preview.py
"""

import base64
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
APP = os.path.join(ROOT, "app.py")
ASSETS = os.path.join(ROOT, "assets")
OUT_DIR = os.path.join(ROOT, ".preview")
os.makedirs(OUT_DIR, exist_ok=True)


def load_translations():
    """Pull the T dict + the CSS block out of app.py without running the app."""
    src = open(APP, encoding="utf-8").read()
    ns = {}
    start = src.index("T = {")
    end = src.index("def lang_pick():")
    exec(src[start:end], ns)
    return ns["T"], re.search(r"<style>(.*?)</style>", src, re.DOTALL).group(1)


T, STYLE = load_translations()


def uri(name):
    with open(os.path.join(ASSETS, name), "rb") as fh:
        return "data:image/png;base64," + base64.b64encode(fh.read()).decode("ascii")


def img(name, cls=None):
    c = f" class='{cls}'" if cls else ""
    return f"<img src='{uri(name)}'{c} alt='' />"


def sec(title, ic_name):
    return (
        f"<div class='sec-head'>{img(ic_name, 'ic-inline')}"
        f"<span class='sec-title'>{title}</span></div>"
    )


def sub(title, ic_name):
    return f"<div class='sub-head'>{img(ic_name, 'ic-inline')}{title}</div>"


PIPELINE = [
    "icon_selection.png",
    "icon_content.png",
    "icon_compliance.png",
    "icon_jimeng.png",
]

TITLES_EN = [
    "Men's shoe rack really needs one universal pair! Matches every outfit",
    "This commuter sneaker keeps your feet happy all day long",
    "Minimalist white sneakers - how to choose? These go with everything",
]
TITLES_ZH = [
    "男生鞋柜真的要有一双万能鞋！搭遍所有衣服",
    "通勤鞋选这款！走路一整天都不累脚",
    "极简白鞋到底怎么选？这双真的百搭",
]

BASE_CSS = """
  body { margin: 0; background: #120A05; }
  .shell { display: flex; min-height: 100vh; }
  .fake-sidebar { width: 306px; flex: 0 0 306px; padding: 26px 20px;
    background: linear-gradient(180deg, #1E1209 0%, #100804 100%);
    border-right: 1px solid rgba(255,149,61,0.16); }
  .fake-sidebar h4 { margin: 6px 0 12px; font-size: 1.02rem; }
  .fake-sidebar hr { border: none; border-top: 1px solid rgba(255,149,61,0.18); margin: 1rem 0; }
  .side-caption { color: #A08573; font-size: 0.78rem; }
  .fake-main { flex: 1 1 auto; padding: 34px 46px 70px 46px; max-width: 1150px; }
  .tabbar { display: flex; gap: 8px; background: rgba(22,13,6,0.6);
    border: 1px solid rgba(255,255,255,0.08); border-radius: 16px; padding: 6px; margin-bottom: 14px; }
  .tabbar span { padding: 9px 14px; border-radius: 11px; color: #C6A995; font-weight: 600;
    font-size: 0.88rem; white-space: nowrap; }
  .tabbar span.on { background: linear-gradient(95deg, rgba(226,58,0,0.92), rgba(255,150,20,0.85)); color: #fff; }
  .field { background: rgba(22,13,6,0.78); border: 1px solid rgba(255,255,255,0.11);
    border-radius: 14px; padding: 15px 16px; color: #9C8570; font-size: 0.98rem; font-weight: 500; }
  .cols { display: flex; gap: 26px; align-items: flex-start; }
  .mediabox { background: rgba(22,13,6,0.6); border: 1px solid rgba(255,255,255,0.1);
    border-radius: 16px; height: 190px; display: flex; align-items: center; justify-content: center;
    color: #9C8570; font-weight: 600; font-size: 0.9rem; }
  .lang-btns { display: flex; gap: 8px; margin-bottom: 4px; }
  .lang-btns span { flex: 1; text-align: center; padding: 9px; border-radius: 11px;
    background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.12);
    color: #FFF6EE; font-weight: 700; font-size: 0.86rem; }
  .lang-btns span.on { background: linear-gradient(95deg, #E23A00, #FF6A00 48%, #FFA31A); border: none; }
"""


def page(title, lang, main):
    d = T[lang]
    rows = "".join(
        f"<div class='pipeline-row'>{img(i)}<div><span class='p-name'>{n}</span>"
        f"<span class='p-role'>{r}</span></div></div>"
        for i, (n, r) in zip(PIPELINE, d["agents"])
    )
    sidebar = f"""
      <aside class="fake-sidebar">
        <div class="lang-label">{d['lang_label']}</div>
        <div class="lang-btns">
          <span class="{'on' if lang == 'en' else ''}">English</span>
          <span class="{'on' if lang == 'zh' else ''}">&#20013;&#25991;</span>
        </div>
        <hr />
        <div class="side-title">{d['control_center']}</div>
        <h4>{d['system_status']}</h4>
        <div class="status-chip"><span class="dot"></span>{d['chip_coze']}</div>
        <div class="status-chip"><span class="dot"></span>{d['chip_jimeng']}</div>
        <hr />
        <h4>{d['pipeline_title']}</h4>
        {rows}
        <hr />
        <p class="side-caption">{d['caption']}</p>
      </aside>
    """
    return f"""<!doctype html>
<html lang="{lang}"><head><meta charset="utf-8" /><title>{title}</title>
<style>{STYLE}</style>
<style>{BASE_CSS}</style>
</head><body><div class="shell">{sidebar}<main class="fake-main">{main}</main></div></body></html>
"""


def brand_bar(d, avatar):
    return f"""
    <div class="hero-wrap">
      <div class="hero-logo">{avatar}</div>
      <div>
        <div class="hero-name">{d['brand']}</div>
        <div class="hero-sub">{d['brand_sub']}</div>
      </div>
      <div class="hero-spacer"></div>
      <div class="status-pill"><span class="dot"></span>{d['systems_online']}</div>
    </div>"""


def landing(lang):
    d = T[lang]
    return page(
        f"EchoCommerce landing ({lang})",
        lang,
        f"""
    <style>.hero-stage {{ --hero-art: url("{uri('hero_ai_robot.png')}"); }}</style>
    <div class="hero-stage">
      <div class="hero-inner">
        <div class="hero-badge">{d['hero_badge']}</div>
        <h1 class="hero-title">{d['hero_title']}</h1>
        <p class="hero-lead">{d['hero_lead']}</p>
      </div>
    </div>
    {brand_bar(d, img('robot_avatar.png'))}
    <div class="cols" style="margin-top:6px;">
      <div class="field" style="flex:3.5;">{d['placeholder']}</div>
      <div class="stButton" style="flex:1.2;"><button>{img('ic_bolt.png', 'ic-inline')}{d['btn_run']}</button></div>
    </div>
    <img class="wave-foot" src="{uri('motif_waves.png')}" alt="" />
    """,
    )


def results(lang):
    d = T[lang]
    titles = TITLES_EN if lang == "en" else TITLES_ZH
    left = f"""
      {sec(d['results_title'], 'ic_doc.png')}
      <div class="tabbar"><span class="on">{d['tab_titles']}</span><span>{d['tab_body']}</span>
        <span>{d['tab_comment']}</span><span>{d['tab_copy']}</span></div>
      <div class="badge-status">{d['badge_titles']}</div>
      {''.join(f"<div class='title-pill'>{x}</div>" for x in titles)}
    """
    right = f"""
      {sec(d['visual_title'], 'ic_image.png')}
      <div class="mediabox">{d['img_caption']}</div>
      <hr style="border:none;border-top:1px solid rgba(255,255,255,0.1);margin:22px 0;" />
      {sub(d['video_title'], 'ic_video.png')}
      <div class="mediabox">{d['video_caption']}</div>
    """
    return page(
        f"EchoCommerce results ({lang})",
        lang,
        f"""
    {brand_bar(d, img('robot_avatar.png'))}
    <p style="color:#9C8570;font-size:0.92rem;margin:0 0 18px 0;">{d['success']}</p>
    <div class="cols">
      <div style="flex:1.2;"><div class="glass-card">{left}</div></div>
      <div style="flex:1;"><div class="glass-card">{right}</div></div>
    </div>
    """,
    )


for lang in ("en", "zh"):
    for view, fn in (("landing", landing), ("results", results)):
        out = os.path.join(OUT_DIR, f"{view}_{lang}.html")
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(fn(lang))
        print("preview:", out)
