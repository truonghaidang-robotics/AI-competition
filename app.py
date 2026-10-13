import base64
import json
import os
import re
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
COZE_API_KEY = os.getenv("COZE_API_KEY")
COZE_WORKFLOW_ID = os.getenv("COZE_WORKFLOW_ID")
#hubzz was here
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")


def asset_img(name, **attrs):
    """Inline an asset PNG as a data URI so it survives Streamlit re-renders."""
    path = os.path.join(ASSETS_DIR, name)
    if not os.path.exists(path):
        return ""
    with open(path, "rb") as fh:
        b64 = base64.b64encode(fh.read()).decode("ascii")
    extra = "".join(f' {k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<img src="data:image/png;base64,{b64}"{extra} />'


def icon(name, cls="ic"):
    """Inline UI glyph asset."""
    return asset_img(name, **{"class": cls, "alt": ""})


def heading(title, ic_name):
    """Section heading with an inline vector glyph instead of an emoji."""
    return (
        f"<div class='sec-head'>{icon(ic_name)}<span class='sec-title'>"
        f"{title}</span></div>"
    )


# ---------------- SITE CONFIG ----------------
st.set_page_config(
    page_title="EchoCommerce - KOC Automatic Marketing Studio",
    layout="wide",
    page_icon="🛍️",
    initial_sidebar_state="expanded",
)

# ---------------- CUSTOM CSS: DARK EMBER / TAOBAO ORANGE STUDIO THEME ----------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');

    :root {
        --bg-0: #120A05;
        --bg-1: #1A1008;
        --surface: rgba(255, 255, 255, 0.045);
        --stroke: rgba(255, 149, 61, 0.22);
        --stroke-soft: rgba(255, 255, 255, 0.08);
        --text: #FFF6EE;
        --muted: #C6A995;
        --violet: #FF6A00;
        --violet-2: #FF9500;
        --pink: #FFC24A;
        --green: #34D399;
        --card-radius: 20px;
        --glow: 0 18px 40px -18px rgba(255, 106, 0, 0.75);
    }

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Microsoft YaHei', 'PingFang SC',
                     'Hiragino Sans GB', 'Noto Sans SC', sans-serif;
    }

    /* ---------- App background: layered ember / Taobao orange ---------- */
    .stApp {
        background:
            radial-gradient(1100px 720px at 88% -12%, rgba(255, 122, 0, 0.24), transparent 62%),
            radial-gradient(900px 620px at 6% 0%, rgba(255, 84, 0, 0.20), transparent 60%),
            radial-gradient(1200px 900px at 50% 118%, rgba(255, 190, 92, 0.13), transparent 66%),
            linear-gradient(168deg, var(--bg-1) 0%, var(--bg-0) 55%, #0E0703 100%);
        background-attachment: fixed;
        color: var(--text);
    }
    [data-testid="stHeader"] {
        background: transparent;
    }
    [data-testid="stHeader"] [data-testid="stDecoration"] {
        background-image: none;
    }
    [data-testid="stToolbar"],
    #MainMenu {
        visibility: hidden;
    }
    footer {
        visibility: hidden;
    }
    .block-container {
        padding-top: 2.2rem;
        padding-bottom: 4rem;
        max-width: 1360px;
    }
    [data-testid="stMainBlockContainer"] p,
    [data-testid="stMainBlockContainer"] li,
    [data-testid="stMainBlockContainer"] span,
    [data-testid="stMainBlockContainer"] label {
        color: var(--text);
    }

    /* ---------- Typography ---------- */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Sora', 'Plus Jakarta Sans', 'Microsoft YaHei', 'PingFang SC',
                     'Hiragino Sans GB', 'Noto Sans SC', sans-serif !important;
        color: var(--text) !important;
        letter-spacing: -0.4px;
    }
    a {
        color: #FFBE7A;
    }
    code {
        color: #FFE0BC;
        background: rgba(255, 122, 0, 0.16);
        border-radius: 6px;
    }

    /* ---------- Top brand bar ---------- */
    .hero-wrap {
        display: flex;
        align-items: center;
        gap: 14px;
        padding: 16px 18px;
        border: 1px solid var(--stroke);
        border-radius: var(--card-radius);
        background: linear-gradient(135deg, rgba(255, 122, 0, 0.22), rgba(38, 22, 10, 0.88) 55%, rgba(38, 22, 10, 0.88));
        box-shadow: 0 20px 50px -30px rgba(255, 106, 0, 0.9), inset 0 1px 0 rgba(255, 255, 255, 0.06);
        margin-bottom: 22px;
    }
    .hero-logo {
        width: 52px;
        height: 52px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.35rem;
        overflow: hidden;
        border: 2px solid rgba(255, 168, 88, 0.55);
        background: linear-gradient(135deg, var(--violet), var(--violet-2) 55%, var(--pink));
        box-shadow: var(--glow);
        flex: 0 0 auto;
    }
    .hero-logo img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        display: block;
    }
    .hero-name {
        font-family: 'Sora', 'Microsoft YaHei', 'PingFang SC', sans-serif;
        font-size: 1.12rem;
        font-weight: 700;
        line-height: 1.25;
        color: var(--text);
    }
    .hero-sub {
        font-size: 0.78rem;
        font-weight: 500;
        color: var(--muted);
        letter-spacing: 0.2px;
    }
    .hero-spacer {
        flex: 1 1 auto;
    }

    /* ---------- Orange hero / landing block ---------- */
    .hero-badge {
        display: inline-block;
        padding: 7px 16px;
        border-radius: 999px;
        border: 1px solid rgba(255, 178, 102, 0.38);
        background: rgba(255, 122, 0, 0.16);
        color: #FFE0BC;
        font-size: 0.74rem;
        font-weight: 700;
        letter-spacing: 1.6px;
        text-transform: uppercase;
        margin-bottom: 16px;
    }
    /* ---------- Hero: copy on top, illustration as a soft backdrop layer ---------- */
    .hero-stage {
        position: relative;
        overflow: hidden;
        border-radius: 26px;
        border: 1px solid var(--stroke);
        background:
            radial-gradient(680px 300px at 50% 100%, rgba(255, 122, 0, 0.20), transparent 70%),
            radial-gradient(760px 420px at 50% 4%, rgba(255, 122, 0, 0.12), transparent 68%),
            linear-gradient(170deg, rgba(48, 27, 12, 0.92), rgba(17, 10, 5, 0.94));
        padding: 40px 44px 76px 44px;
        min-height: 410px;
        margin-bottom: 22px;
    }
    .hero-inner {
        position: relative;
        z-index: 2;
    }
    /* illustration sits behind the words, low opacity, faded at the edges */
    .hero-stage::after {
        content: "";
        position: absolute;
        left: 50%;
        top: 20%;
        width: 112%;
        height: 118%;
        transform: translateX(-50%);
        background-image: var(--hero-art);
        background-repeat: no-repeat;
        background-position: center center;
        background-size: contain;
        opacity: 0.34;
        filter: saturate(1.15);
        pointer-events: none;
        -webkit-mask-image: radial-gradient(52% 62% at 50% 66%, #000 30%, transparent 100%);
        mask-image: radial-gradient(52% 62% at 50% 66%, #000 30%, transparent 100%);
        z-index: 1;
    }
    /* keeps the headline / paragraph area clean over the artwork */
    .hero-stage::before {
        content: "";
        position: absolute;
        inset: 0;
        background: linear-gradient(
            180deg,
            rgba(28, 16, 8, 0.97) 0%,
            rgba(28, 16, 8, 0.93) 40%,
            rgba(24, 14, 6, 0.52) 66%,
            rgba(24, 14, 6, 0.12) 100%
        );
        pointer-events: none;
        z-index: 1;
    }
    .hero-title {
        font-family: 'Sora', 'Microsoft YaHei', 'PingFang SC', sans-serif;
        font-size: clamp(2rem, 4.1vw, 3.05rem);
        font-weight: 800;
        line-height: 1.1;
        margin: 0;
        background: linear-gradient(100deg, #FFFFFF 0%, #FFF1E2 42%, var(--violet-2) 100%);
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        color: #FFFFFF;
    }
    .hero-lead {
        color: var(--muted);
        font-size: 1.02rem;
        font-weight: 500;
        line-height: 1.6;
        max-width: 60ch;
        margin: 14px 0 4px 0;
    }

    /* ---------- Section headings with vector glyphs ---------- */
    .sec-head {
        display: flex;
        align-items: center;
        gap: 11px;
        margin: 2px 0 16px 0;
    }
    .sec-head img.ic {
        width: 30px;
        height: 30px;
        border-radius: 9px;
        flex: 0 0 auto;
        box-shadow: 0 8px 20px -10px rgba(255, 106, 0, 0.95);
    }
    .sec-title {
        font-family: 'Sora', 'Microsoft YaHei', 'PingFang SC', sans-serif;
        font-size: 1.16rem;
        font-weight: 700;
        color: var(--text);
        letter-spacing: -0.2px;
    }
    .sec-title .ic-inline {
        width: 22px;
        height: 22px;
        border-radius: 7px;
        vertical-align: -5px;
        display: inline-block;
        margin-right: 6px;
    }
    .sub-head {
        display: flex;
        align-items: center;
        gap: 10px;
        margin: 16px 0 12px 0;
        font-family: 'Sora', 'Microsoft YaHei', 'PingFang SC', sans-serif;
        font-size: 1.02rem;
        font-weight: 700;
        color: var(--text);
    }
    .sub-head img.ic {
        width: 26px;
        height: 26px;
        border-radius: 8px;
        flex: 0 0 auto;
        box-shadow: 0 8px 20px -10px rgba(255, 106, 0, 0.9);
    }
    .ic-inline {
        width: 20px;
        height: 20px;
        border-radius: 6px;
        vertical-align: -4px;
        display: inline-block;
    }

    /* ---------- Language toggle ---------- */
    .lang-label {
        font-family: 'Sora', 'Microsoft YaHei', 'PingFang SC', sans-serif;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1.7px;
        text-transform: uppercase;
        color: var(--muted);
        margin: 2px 0 8px 0;
    }
    section[data-testid="stSidebar"] .stButton > button {
        min-height: 2.4rem;
        font-size: 0.86rem;
        border-radius: 11px;
    }
    section[data-testid="stSidebar"] .stButton > button p {
        font-size: 0.86rem;
    }

    /* ---------- Decorative wave motif ---------- */
    .wave-foot {
        display: block;
        width: 100%;
        max-width: 1180px;
        margin: 34px auto 0 auto;
        opacity: 0.3;
        pointer-events: none;
    }
    .stButton > button .ic-inline {
        width: 19px;
        height: 19px;
        border-radius: 6px;
        vertical-align: -4px;
        margin-right: 8px;
        display: inline-block;
    }

    /* ---------- Glass cards ---------- */
    .glass-card,
    .studio-card {
        background: linear-gradient(160deg, rgba(255, 255, 255, 0.075), rgba(255, 255, 255, 0.025));
        border: 1px solid var(--stroke);
        border-radius: var(--card-radius);
        padding: 22px 24px;
        box-shadow: 0 24px 60px -40px rgba(0, 0, 0, 0.9), inset 0 1px 0 rgba(255, 255, 255, 0.05);
        margin-bottom: 18px;
    }
    .section-label {
        font-family: 'Sora', 'Microsoft YaHei', 'PingFang SC', sans-serif;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1.7px;
        text-transform: uppercase;
        color: var(--muted);
        margin-bottom: 10px;
    }
    .badge-status {
        display: inline-block;
        background: linear-gradient(90deg, var(--violet), var(--violet-2) 60%, var(--pink));
        color: #FFFFFF;
        padding: 5px 14px;
        border-radius: 999px;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 1.1px;
        text-transform: uppercase;
        box-shadow: 0 10px 26px -12px rgba(255, 122, 0, 0.95);
        margin-bottom: 12px;
    }

    /* ---------- Pill rows (suggested titles, pipeline steps) ---------- */
    .title-pill {
        background: linear-gradient(90deg, rgba(255, 122, 0, 0.22), rgba(255, 194, 74, 0.07));
        border: 1px solid var(--stroke);
        border-left: 4px solid var(--violet-2);
        color: var(--text);
        padding: 13px 16px;
        border-radius: 12px;
        font-weight: 600;
        font-size: 0.95rem;
        margin-bottom: 10px;
        line-height: 1.45;
    }

    /* ---------- Buttons ---------- */
    .stButton {
        width: 100%;
    }
    .stButton > button,
    .stDownloadButton > button,
    .stFormSubmitButton > button {
        width: 100%;
        background: linear-gradient(95deg, #E23A00 0%, #FF6A00 48%, #FFA31A 100%);
        color: #FFFFFF !important;
        font-weight: 700;
        font-size: 0.95rem;
        white-space: nowrap;
        border: none;
        border-radius: 14px;
        padding: 0.8rem 1rem;
        min-height: 3.05rem;
        box-shadow: 0 16px 40px -18px rgba(255, 106, 0, 0.95);
        transition: transform 0.16s ease, box-shadow 0.16s ease, filter 0.16s ease;
    }
    .stButton > button p,
    .stDownloadButton > button p {
        font-weight: 700;
        color: #FFFFFF !important;
    }
    .stButton > button:hover,
    .stDownloadButton > button:hover,
    .stFormSubmitButton > button:hover {
        filter: brightness(1.09);
        transform: translateY(-2px);
        box-shadow: 0 22px 52px -18px rgba(255, 150, 30, 0.95);
        color: #FFFFFF !important;
    }
    .stButton > button:focus,
    .stButton > button:active {
        color: #FFFFFF !important;
        border: none;
        outline: none;
        box-shadow: 0 0 0 3px rgba(255, 178, 102, 0.35);
    }
    .stButton > button:disabled {
        opacity: 0.5;
        filter: grayscale(0.3);
    }

    /* ---------- Text inputs / textareas ---------- */
    .stTextInput input,
    .stTextArea textarea,
    .stNumberInput input,
    [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea,
    [data-baseweb="base-input"] input {
        background: rgba(22, 13, 6, 0.78) !important;
        border: 1px solid rgba(255, 255, 255, 0.11) !important;
        border-radius: 14px !important;
        color: var(--text) !important;
        caret-color: var(--violet-2) !important;
        font-size: 0.98rem !important;
    }
    [data-baseweb="input"],
    [data-baseweb="textarea"],
    [data-baseweb="base-input"] {
        background: transparent !important;
        border: none !important;
        border-radius: 14px !important;
    }
    .stTextInput input::placeholder,
    .stTextArea textarea::placeholder {
        color: #9C8570 !important;
        opacity: 1 !important;
    }
    .stTextInput input:focus,
    .stTextArea textarea:focus {
        border-color: rgba(255, 122, 0, 0.85) !important;
        box-shadow: 0 0 0 3px rgba(255, 122, 0, 0.24) !important;
    }
    [data-testid="stWidgetLabel"] label p,
    [data-testid="stWidgetLabel"] p {
        color: var(--muted) !important;
        font-weight: 600 !important;
        font-size: 0.86rem !important;
    }
    .stTextArea textarea {
        line-height: 1.65 !important;
    }

    /* ---------- Tabs ---------- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: rgba(22, 13, 6, 0.6);
        border: 1px solid var(--stroke-soft);
        border-radius: 16px;
        padding: 6px;
        margin-bottom: 14px;
    }
    .stTabs [data-baseweb="tab"] {
        height: auto;
        background: transparent;
        border-radius: 11px;
        padding: 9px 14px;
        color: var(--muted);
        font-weight: 600;
        font-size: 0.88rem;
        white-space: nowrap;
        transition: background 0.16s ease, color 0.16s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255, 122, 0, 0.16);
        color: var(--text);
    }
    .stTabs [data-baseweb="tab"] p {
        color: inherit !important;
        font-weight: 600 !important;
        font-size: 0.9rem !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(95deg, rgba(226, 58, 0, 0.92), rgba(255, 150, 20, 0.85));
        color: #FFFFFF;
        box-shadow: 0 12px 28px -16px rgba(255, 122, 0, 1);
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] p {
        color: #FFFFFF !important;
    }
    .stTabs [data-baseweb="tab-highlight"],
    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }
    .stTabs [data-baseweb="tab-panel"] {
        padding-top: 6px;
    }

    /* ---------- Expanders ---------- */
    [data-testid="stExpander"] {
        border: 1px solid var(--stroke-soft) !important;
        border-radius: 16px !important;
        background: rgba(255, 255, 255, 0.035) !important;
        overflow: hidden;
    }
    [data-testid="stExpander"] details {
        background: transparent !important;
        border: none !important;
    }
    [data-testid="stExpander"] summary,
    [data-testid="stExpander"] summary:hover,
    [data-testid="stExpander"] summary:focus {
        background: transparent !important;
        color: var(--text) !important;
    }
    [data-testid="stExpander"] summary p {
        color: var(--text) !important;
        font-weight: 600 !important;
    }
    [data-testid="stExpander"] svg {
        fill: var(--muted) !important;
    }

    /* ---------- Status chips / info panels ---------- */
    .status-chip {
        display: inline-flex;
        align-items: center;
        gap: 9px;
        background: rgba(52, 211, 153, 0.12);
        border: 1px solid rgba(52, 211, 153, 0.34);
        color: #D1FAE5;
        padding: 8px 15px;
        border-radius: 999px;
        font-size: 0.82rem;
        font-weight: 600;
        margin: 0 6px 8px 0;
    }
    .status-chip .dot,
    .status-pill .dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--green);
        box-shadow: 0 0 0 4px rgba(52, 211, 153, 0.16);
        flex: 0 0 auto;
    }
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 9px;
        background: rgba(52, 211, 153, 0.12);
        border: 1px solid rgba(52, 211, 153, 0.34);
        color: #D1FAE5;
        padding: 9px 17px;
        border-radius: 999px;
        font-size: 0.84rem;
        font-weight: 600;
        white-space: nowrap;
    }
    .side-title {
        font-family: 'Sora', 'Microsoft YaHei', 'PingFang SC', sans-serif;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 1.7px;
        text-transform: uppercase;
        color: var(--muted);
        margin: 4px 0 12px 0;
    }

    /* ---------- Pipeline rows (sidebar agent monitor) ---------- */
    .pipeline-row {
        display: flex;
        align-items: center;
        gap: 13px;
        padding: 11px 13px;
        margin-bottom: 9px;
        border-radius: 14px;
        border: 1px solid rgba(255, 149, 61, 0.18);
        background: linear-gradient(95deg, rgba(255, 122, 0, 0.13), rgba(255, 255, 255, 0.025));
    }
    .pipeline-row img {
        width: 46px;
        height: 46px;
        flex: 0 0 auto;
        display: block;
        filter: drop-shadow(0 6px 14px rgba(255, 106, 0, 0.38));
    }
    .pipeline-row .p-name {
        display: block;
        color: #FFF6EE;
        font-weight: 700;
        font-size: 0.9rem;
        line-height: 1.25;
    }
    .pipeline-row .p-role {
        display: block;
        color: #BE9F8A;
        font-size: 0.76rem;
        font-weight: 500;
        margin-top: 2px;
    }
    [data-testid="stAlert"] {
        background: rgba(255, 122, 0, 0.12) !important;
        border: 1px solid var(--stroke) !important;
        border-left: 4px solid var(--violet-2) !important;
        border-radius: 14px !important;
        color: var(--text) !important;
    }
    [data-testid="stAlert"] p,
    [data-testid="stAlert"] div {
        color: var(--text) !important;
    }
    [data-testid="stAlertContainer"] {
        background: transparent !important;
    }

    /* ---------- Progress bar ---------- */
    [data-testid="stProgress"] > div > div > div > div {
        background: linear-gradient(90deg, var(--violet), var(--pink)) !important;
    }

    /* ---------- Media ---------- */
    [data-testid="stImage"] img,
    [data-testid="stVideo"] video {
        border-radius: 16px;
        border: 1px solid var(--stroke);
        box-shadow: 0 26px 60px -34px rgba(0, 0, 0, 0.95);
    }
    [data-testid="stCaptionContainer"] p {
        color: var(--muted) !important;
    }

    /* ---------- Sidebar ---------- */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1E1209 0%, #100804 100%);
        border-right: 1px solid rgba(255, 149, 61, 0.16);
    }
    section[data-testid="stSidebar"] > div {
        padding-top: 1.6rem;
    }
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        font-size: 1.02rem !important;
        letter-spacing: 0.2px;
    }
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] li {
        color: #E7D3C2;
    }
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
        color: #A08573 !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255, 149, 61, 0.18);
        margin: 1rem 0;
    }
    section[data-testid="stSidebar"] [data-testid="stAlert"] {
        background: linear-gradient(90deg, rgba(255, 122, 0, 0.20), rgba(255, 122, 0, 0.05)) !important;
        border: 1px solid rgba(255, 149, 61, 0.26) !important;
        border-left: 4px solid var(--violet-2) !important;
        border-radius: 12px !important;
        padding: 12px 14px !important;
        margin-bottom: 10px !important;
    }
    section[data-testid="stSidebar"] [data-testid="stAlert"] p {
        color: #FFE6CE !important;
        font-size: 0.87rem !important;
        font-weight: 600 !important;
        margin: 0 !important;
    }
    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="stSidebarCollapsedControl"] button,
    [data-testid="stExpandSidebarButton"] button {
        color: var(--muted) !important;
    }

    /* ---------- Scrollbar ---------- */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.03);
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 122, 0, 0.45);
        border-radius: 999px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 160, 40, 0.65);
    }
    </style>
""",
    unsafe_allow_html=True,
)


# ---------------- HÀM BÓC TÁCH URL TỪ COZE OBJECT/DICT/ARRAY ----------------
def extract_url_from_coze(val):
  """Giải mã thông minh đường dẫn URL từ chuỗi, Dict hay Array của Coze API"""
  if not val:
    return ""
  if isinstance(val, str):
    return val.strip()
  if isinstance(val, dict):
    return (
        val.get("url")
        or val.get("image_url")
        or val.get("uri")
        or val.get("href")
        or ""
    )
  if isinstance(val, list) and len(val) > 0:
    return extract_url_from_coze(val[0])
  return ""


# ---------------- HÀM BÓC TÁCH BÀI VIẾT PR ----------------
def parse_koc_response(text):
  if not isinstance(text, str):
    return {"titles": "", "body": "", "comment": "", "full_clean": ""}

  clean_text = re.sub(
      r"---?\s*IMAGE_PROMPT:.*", "", text, flags=re.DOTALL | re.IGNORECASE
  )
  clean_text = re.sub(
      r"IMAGE_PROMPT:.*", "", clean_text, flags=re.DOTALL | re.IGNORECASE
  )

  if "### 【转化率评分" in clean_text:
    clean_text = clean_text.split("### 【转化率评分")[0]
  if "【广告法合规审查】" in clean_text and "爆款标题备选" in clean_text:
    clean_text = "爆款标题备选" + clean_text.split("爆款标题备选", 1)[1]

  titles, body, comment = "", "", ""

  titles_match = re.search(
      r"(?:#####|###|#)?\s*爆款标题备选(.*?)(?=(?:#####|###|#)?\s*正文/口播|\Z)",
      clean_text,
      re.DOTALL,
  )
  if titles_match:
    titles = titles_match.group(1).strip()

  body_match = re.search(
      r"(?:#####|###|#)?\s*正文/口播(.*?)(?=(?:#####|###|#)?\s*互动/置顶评论|\Z)",
      clean_text,
      re.DOTALL,
  )
  if body_match:
    body = body_match.group(1).strip()

  comment_match = re.search(
      r"(?:#####|###|#)?\s*互动/置顶评论(.*)", clean_text, re.DOTALL
  )
  if comment_match:
    comment = comment_match.group(1).strip()

  if not body and not titles:
    body = clean_text

  titles = re.sub(r"#{1,6}\s*", "", titles).strip()
  body = re.sub(r"#{1,6}\s*", "", body).strip()
  comment = re.sub(r"#{1,6}\s*", "", comment).strip()

  full_clean_parts = []
  if titles:
    full_clean_parts.append("📌 [TOP 3 HOOK TITLES]\n" + titles)
  if body:
    full_clean_parts.append("✍️ [MAIN PR BODY]\n" + body)
  if comment:
    full_clean_parts.append("💬 [PINNED COMMENT / CTA]\n" + comment)

  full_clean = (
      "\n\n".join(full_clean_parts)
      if full_clean_parts
      else re.sub(r"#{1,6}\s*", "", clean_text).strip()
  )

  return {
      "titles": titles,
      "body": body,
      "comment": comment,
      "full_clean": full_clean,
  }


# ---------------- BILINGUAL UI (EN / 中文) ----------------
T = {
    "en": {
        "brand": "EchoCommerce Studio",
        "brand_sub": "KOC Automatic Marketing Studio &middot; Coze AI Engine",
        "systems_online": "All Systems Online",
        "hero_badge": "Unleash Your Creative Potential",
        "hero_title": "Fastest &amp; Easiest Way to Generate Viral KOC Content",
        "hero_lead": (
            "Paste one product link and Coze AI writes the full PR script, suggests "
            "high-converting titles, renders 3D product visuals and produces the AI "
            "commercial video &mdash; automatically, in a single click."
        ),
        "lang_label": "Language",
        "control_center": "Control Center",
        "system_status": "System Status",
        "chip_coze": "Coze API: Active",
        "chip_jimeng": "Jimeng AI Engine: Connected",
        "pipeline_title": "Agents Pipeline Monitor",
        "caption": "EchoCommerce Studio v4.0 | Pure Coze Engine",
        "input_label": "Product link or product text (Taobao / 1688 / TikTok Shop):",
        "placeholder": "Paste a Taobao link or sharing text here...",
        "btn_run": "Generate 1-Click Content",
        "warn_no_input": "Please enter a product link or product information first.",
        "status_running": (
            "Coze Workflow is analyzing data, writing the PR script & rendering media"
            " with Jimeng AI..."
        ),
        "success": "Done! All marketing assets are ready.",
        "results_title": "KOC-Ready Marketing Content",
        "tab_titles": "Top 3 Hot Titles",
        "tab_body": "PR Article",
        "tab_comment": "Comment & CTA",
        "tab_copy": "1-Click Copy",
        "badge_titles": "TITLE SUGGESTIONS",
        "badge_body": "PR BODY CONTENT",
        "badge_comment": "PINNED COMMENT",
        "info_no_titles": "No title suggestions yet.",
        "clean_text_label": "100% clean text (junk & prompts removed):",
        "visual_title": "3D Visual Asset (Jimeng AI)",
        "img_caption": "3D product concept image from Coze Jimeng AI",
        "info_no_image": "No image URL received from Coze yet.",
        "video_title": "Commercial Video (Jimeng AI Video)",
        "video_caption": "AI video rendered automatically by Coze.",
        "info_no_video": "No video_url data from Coze yet.",
        "err_workflow": "Workflow error: ",
        "err_api": "API connection error: ",
        "debug_label": "Debug",
        "debug_toggle": "Show raw Coze response",
        "debug_raw": "Raw response from the Coze Workflow",
        "agents": [
            ("Selection Agent", "Data Cleansing"),
            ("Content Agent", "PR Scripting"),
            ("Visual Guard Agent", "Compliance Check"),
            ("Jimeng Node", "AI Visual &amp; Video"),
        ],
    },
    "zh": {
        "brand": "EchoCommerce 智能营销工作台",
        "brand_sub": "KOC 自动化营销工作室 &middot; Coze AI 引擎",
        "systems_online": "系统运行正常",
        "hero_badge": "释放你的创意潜能",
        "hero_title": "最快、最简单的爆款 KOC 内容生成方式",
        "hero_lead": (
            "粘贴一个商品链接，Coze AI 自动撰写完整种草文案、生成高转化标题、渲染 3D "
            "商品视觉图，并产出 AI 商业视频 &mdash; 一键完成，全程自动化。"
        ),
        "lang_label": "语言 / Language",
        "control_center": "控制中心",
        "system_status": "系统状态",
        "chip_coze": "Coze API：已连接",
        "chip_jimeng": "即梦 AI 引擎：已连接",
        "pipeline_title": "AI Agent 流水线监控",
        "caption": "EchoCommerce Studio v4.0 | 纯 Coze 引擎驱动",
        "input_label": "商品链接或商品文字（淘宝 / 1688 / 抖音小店）：",
        "placeholder": "在此粘贴淘宝链接或分享文案...",
        "btn_run": "一键生成营销内容",
        "warn_no_input": "请先输入商品链接或商品信息。",
        "status_running": "Coze 工作流正在分析数据、撰写种草文案并使用即梦 AI 渲染素材...",
        "success": "完成！全部营销素材已就绪。",
        "results_title": "KOC 级营销内容",
        "tab_titles": "3 个爆款标题",
        "tab_body": "种草正文",
        "tab_comment": "评论与引导",
        "tab_copy": "一键复制",
        "badge_titles": "推荐标题",
        "badge_body": "正文内容",
        "badge_comment": "置顶评论",
        "info_no_titles": "暂无推荐标题。",
        "clean_text_label": "纯净文本（已去除冗余与提示词）：",
        "visual_title": "3D 视觉素材（即梦 AI）",
        "img_caption": "由 Coze 即梦 AI 生成的 3D 商品概念图",
        "info_no_image": "暂未收到 Coze 返回的图片链接。",
        "video_title": "商业视频（即梦 AI 视频）",
        "video_caption": "由 Coze 自动渲染的 AI 视频。",
        "info_no_video": "暂未收到 Coze 返回的视频数据。",
        "err_workflow": "工作流错误：",
        "err_api": "接口连接错误：",
        "debug_label": "调试",
        "debug_toggle": "显示 Coze 原始返回数据",
        "debug_raw": "Coze 工作流原始返回数据",
        "agents": [
            ("选品 Agent", "数据清洗"),
            ("内容 Agent", "文案撰写"),
            ("视觉风控 Agent", "合规审查"),
            ("即梦节点", "AI 视觉与视频"),
        ],
    },
}


def lang_pick():
  """Keeps the chosen language across widget re-runs."""
  if "lang" not in st.session_state:
    st.session_state.lang = "en"
  return st.session_state.lang


LANG = lang_pick()


def tr(key):
  return T[LANG][key]


# ---------------- SIDEBAR MONITOR ----------------
with st.sidebar:
  st.markdown(
      f"<div class='lang-label'>{tr('lang_label')}</div>",
      unsafe_allow_html=True,
  )
  lang_cols = st.columns(2)
  for _col, _code in zip(lang_cols, ("en", "zh")):
    with _col:
      _active = LANG == _code
      if st.button(
          "English" if _code == "en" else "中文",
          key=f"lang_{_code}",
          type="primary" if _active else "secondary",
          use_container_width=True,
      ):
        if st.session_state.lang != _code:
          st.session_state.lang = _code
          st.rerun()

  st.divider()
  st.markdown(
      f"<div class='side-title'>{tr('control_center')}</div>",
      unsafe_allow_html=True,
  )
  st.markdown(f"#### {tr('system_status')}")
  st.markdown(
      f"<div class='status-chip'><span class='dot'></span>{tr('chip_coze')}</div>"
      f"<div class='status-chip'><span class='dot'></span>{tr('chip_jimeng')}</div>",
      unsafe_allow_html=True,
  )

  st.divider()
  st.markdown(f"#### {tr('pipeline_title')}")

  pipeline = [
      ("icon_selection.png",),
      ("icon_content.png",),
      ("icon_compliance.png",),
      ("icon_jimeng.png",),
  ]
  rows = ""
  for (icon_file,), (name, role) in zip(pipeline, tr("agents")):
    rows += (
        "<div class='pipeline-row'>"
        + asset_img(icon_file)
        + f"<div><span class='p-name'>{name}</span>"
        + f"<span class='p-role'>{role}</span></div></div>"
    )
  st.markdown(rows, unsafe_allow_html=True)

  st.divider()
  st.caption(tr("caption"))

  # Raw Coze output, hidden unless explicitly switched on (demo-safe).
  with st.expander(tr("debug_label"), expanded=False):
    st.checkbox(tr("debug_toggle"), key="show_debug_json")


# ---------------- MAIN SCREEN ----------------
hero_b64 = ""
hero_path = os.path.join(ASSETS_DIR, "hero_ai_robot.png")
if os.path.exists(hero_path):
  with open(hero_path, "rb") as _fh:
    hero_b64 = base64.b64encode(_fh.read()).decode("ascii")

brand_avatar = asset_img("robot_avatar.png", alt="EchoCommerce AI robot")
wave_motif = asset_img("motif_waves.png", alt="")
st.markdown(
    f"""
    <style>
    .hero-stage {{ --hero-art: url("data:image/png;base64,{hero_b64}"); }}
    </style>

    <div class="hero-stage">
      <div class="hero-inner">
        <div class="hero-badge">{tr('hero_badge')}</div>
        <h1 class="hero-title">{tr('hero_title')}</h1>
        <p class="hero-lead">{tr('hero_lead')}</p>
      </div>
    </div>

    <div class="hero-wrap">
      <div class="hero-logo">{brand_avatar}</div>
      <div>
        <div class="hero-name">{tr('brand')}</div>
        <div class="hero-sub">{tr('brand_sub')}</div>
      </div>
      <div class="hero-spacer"></div>
      <div class="status-pill"><span class="dot"></span>{tr('systems_online')}</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

col_url, col_btn = st.columns([3.5, 1.2], vertical_alignment="bottom")
with col_url:
  product_url = st.text_input(
      f"{icon('ic_bolt', cls='ic-inline')} {tr('input_label')}",
      placeholder=tr("placeholder"),
      label_visibility="collapsed",
  )
with col_btn:
  btn_run = st.button(
      f"{icon('ic_bolt', cls='ic-inline')} {tr('btn_run')}",
      type="primary",
  )

if btn_run:
  if not product_url:
    st.warning(tr("warn_no_input"))
  else:
    progress_bar = st.progress(0)
    status_text = st.empty()

    status_text.text(tr("status_running"))
    progress_bar.progress(40)

    try:
      url = "https://api.coze.cn/v1/workflow/run"
      headers = {
          "Authorization": f"Bearer {COZE_API_KEY}",
          "Content-Type": "application/json",
      }
      payload = {
          "workflow_id": COZE_WORKFLOW_ID,
          "parameters": {"input": product_url.strip()},
      }

      res = requests.post(url, headers=headers, json=payload, timeout=180)
      result = res.json()

      if res.status_code == 200 and result.get("code") == 0:
        data = result.get("data", {})
        if isinstance(data, str):
          try:
            data = json.loads(data)
          except Exception:
            pass

        # 1. Trích xuất Bài viết PR KOC
        raw_koc_text = (
            data.get("koc_content", "")
            or data.get("content", "")
            or "No content returned from the workflow."
        )
        parsed = parse_koc_response(raw_koc_text)

        # 2. Giải mã URL Ảnh và Video thông minh từ mọi cấu trúc JSON của Coze
        raw_img_val = (
            data.get("image_url")
            or data.get("image")
            or data.get("img_url")
            or data.get("url")
        )
        raw_vid_val = (
            data.get("video_url")
            or data.get("video")
            or data.get("mp4_url")
        )

        image_url = extract_url_from_coze(raw_img_val)
        video_url = extract_url_from_coze(raw_vid_val)

        progress_bar.progress(100)
        status_text.empty()
        progress_bar.empty()

        st.success(tr("success"))

        # ---------------- KHU VỰC HIỂN THỊ KẾT QUẢ ----------------
        st.session_state["last_raw"] = data
        col_left, col_right = st.columns([1.2, 1])

        # CỘT TRÁI: BÀI VIẾT PR KOC
        with col_left:
          st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
          st.markdown(
              "<div class='sec-head'>"
              + icon("ic_doc", cls="ic-inline")
              + f"<span class='sec-title'>{tr('results_title')}</span></div>",
              unsafe_allow_html=True,
          )

          tab1, tab2, tab3, tab4 = st.tabs([
              tr("tab_titles"),
              tr("tab_body"),
              tr("tab_comment"),
              tr("tab_copy"),
          ])

          with tab1:
            st.markdown(
                f"<div class='badge-status'>{tr('badge_titles')}</div>",
                unsafe_allow_html=True,
            )
            if parsed["titles"]:
              for t in parsed["titles"].split("\n"):
                if t.strip():
                  st.markdown(
                      f"<div class='title-pill'>{t.strip()}</div>",
                      unsafe_allow_html=True,
                  )
            else:
              st.info(tr("info_no_titles"))

          with tab2:
            st.markdown(
                f"<div class='badge-status'>{tr('badge_body')}</div>",
                unsafe_allow_html=True,
            )
            st.write(parsed["body"])

          with tab3:
            st.markdown(
                f"<div class='badge-status'>{tr('badge_comment')}</div>",
                unsafe_allow_html=True,
            )
            st.write(parsed["comment"])

          with tab4:
            st.text_area(
                tr("clean_text_label"),
                value=parsed["full_clean"],
                height=350,
            )

          st.markdown("</div>", unsafe_allow_html=True)

        # CỘT PHẢI: ASSET VISUAL (HIỂN THỊ TRỰC TIẾP TỪ COZE)
        with col_right:
          st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
          st.markdown(
              "<div class='sec-head'>"
              + icon("ic_image", cls="ic-inline")
              + f"<span class='sec-title'>{tr('visual_title')}</span></div>",
              unsafe_allow_html=True,
          )

          if image_url:
            st.image(
                image_url,
                caption=tr("img_caption"),
                use_container_width=True,
            )
          else:
            st.info(tr("info_no_image"))

          st.markdown("---")
          st.markdown(
              "<div class='sub-head'>"
              + icon("ic_video", cls="ic-inline")
              + f"{tr('video_title')}</div>",
              unsafe_allow_html=True,
          )

          if video_url:
            st.video(video_url)
            st.caption(tr("video_caption"))
          else:
            st.info(tr("info_no_video"))

          st.markdown("</div>", unsafe_allow_html=True)

      else:
        st.error(f"{tr('err_workflow')}{result.get('msg')}")
        st.session_state["last_raw"] = result
    except Exception as e:
      st.error(f"{tr('err_api')}{e}")
      st.session_state["last_raw"] = {"error": str(e)}


# ---------------- DEBUG: RAW COZE RESPONSE (off by default) ----------------
if st.session_state.get("show_debug_json"):
  raw = st.session_state.get("last_raw")
  with st.expander(tr("debug_raw"), expanded=True):
    if raw:
      st.json(raw)
    else:
      st.caption("—")


# ---------------- FOOTER DECOR ----------------
if wave_motif:
  st.markdown(
      wave_motif.replace("<img ", "<img class='wave-foot' "),
      unsafe_allow_html=True,
  )
