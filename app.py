"""AI Meeting Assistant — Streamlit UI (single file).

Run:   streamlit run app.py
Demo:  DEMO_MODE=1 streamlit run app.py     (no backend / keys needed)

Tip: this design is light. If you still have the old .streamlit/config.toml
with base = "dark", delete it (or set base = "light") for the cleanest result.
"""
import html as _html
import os
import re
import tempfile
import time
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Meeting Assistant", page_icon="🎙️", layout="wide",
                   initial_sidebar_state="auto")

# ───────────────────────── Backend (your existing modules) ─────────────────────────
DEMO = os.getenv("DEMO_MODE") == "1"

if not DEMO:
    from utils.audio_processor import process_input
    from core.transcriber import transcribe_all
    from core.summarizer import summarize, generate_title
    from core.extractor import extract_action_items, extract_key_decision, extract_questions
    from core.rag_engine import build_rag_chain, ask_question
else:
    def process_input(s): time.sleep(1.1); return ["chunk"]
    def transcribe_all(c):
        time.sleep(1.6)
        return ("Welcome everyone. Today we review the Q4 launch plan. Sarah will finalize the pricing page by Friday. "
                "We decided to ship the beta to 200 customers first. Mark asked whether legal has approved the new terms. "
                "Engineering needs two more weeks for the analytics dashboard. ") * 6
    def generate_title(t): time.sleep(.7); return "Q4 Launch Planning Sync"
    def summarize(t):
        time.sleep(1.2)
        return ("The team reviewed readiness for the Q4 launch. Pricing is nearly final, the beta rollout was scoped "
                "to 200 customers, and engineering flagged a two-week risk on the analytics dashboard.")
    def extract_action_items(t):
        time.sleep(.9)
        return "- Sarah: finalize pricing page by Friday\n- Mark: confirm legal approval of new terms\n- Dev team: deliver analytics dashboard in two weeks"
    def extract_key_decision(t):
        time.sleep(.8); return "- Ship beta to 200 customers first\n- Delay public launch until dashboard is ready"
    def extract_questions(t):
        time.sleep(.8); return "- Has legal approved the new terms?\n- Who owns customer onboarding emails?"
    def build_rag_chain(t): time.sleep(.8); return "demo"
    def ask_question(chain, q): time.sleep(.8); return (f"Here's what the meeting says about **{q}**. Sarah owns the pricing page and it is due Friday. "
                                                          "The beta goes to 200 customers first, and the public launch waits on the analytics dashboard.")

# ───────────────────────── Design system ─────────────────────────
BARS = "".join(f'<i style="--i:{i}"></i>' for i in range(56))

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,600;12..96,700&family=Hanken+Grotesk:wght@400;500;600&family=Hind+Siliguri:wght@400;500;600&display=swap');

:root{
  color-scheme:light;
  --bg:#F4F5F7; --surface:#FFFFFF; --ink:#0E1116; --ink2:#3A4150; --muted:#778093;
  --line:#E4E7EC; --line2:#D5D9E0; --accent:#2447F5; --accent-soft:#E9EDFF; --ok:#12A150; --ok-soft:#E3F6EB;
  --warn:#B7791F; --warn-soft:#FBF1DC;
  --ease:cubic-bezier(.22,1,.36,1);
  --shadow:0 1px 2px rgba(16,24,40,.04),0 8px 24px -8px rgba(16,24,40,.08);
  --shadow-lg:0 2px 4px rgba(16,24,40,.04),0 24px 56px -16px rgba(16,24,40,.18);
}
html,body,.stApp,[data-testid="stAppViewContainer"],[data-testid="stMain"]{background:var(--bg)!important;color:var(--ink)!important}
html,body,[class*="css"],.stApp,button,input,textarea{font-family:'Hanken Grotesk','Hind Siliguri',system-ui,sans-serif!important}
h1,h2,h3,h4,.display{font-family:'Bricolage Grotesque','Hind Siliguri',sans-serif!important;letter-spacing:-.025em;color:var(--ink)!important}
p,li,span,label,div{color:inherit}
#MainMenu,footer,[data-testid="stToolbarActions"],[data-testid="stMainMenu"],[data-testid="stAppDeployButton"],.stDeployButton,[data-testid="stDecoration"],[data-testid="stStatusWidget"]{display:none!important}
[data-testid="stHeader"]{background:transparent!important;height:3.4rem!important;pointer-events:none}
[data-testid="stHeader"] *{pointer-events:auto}
[data-testid="stExpandSidebarButton"],[data-testid="stSidebarCollapsedControl"],[data-testid="stSidebarCollapseButton"] button{
  background:var(--surface)!important;border:1px solid var(--line2)!important;border-radius:12px!important;color:var(--ink)!important;
  box-shadow:var(--shadow)!important;transition:all .25s var(--ease)}
[data-testid="stExpandSidebarButton"]:hover,[data-testid="stSidebarCollapsedControl"]:hover{transform:translateY(-1px);border-color:var(--ink)!important}
[data-testid="stExpandSidebarButton"] *,[data-testid="stSidebarCollapsedControl"] *,[data-testid="stSidebarCollapseButton"] *{color:var(--ink)!important;fill:var(--ink)!important}
[data-testid="stSidebarCollapsedControl"],[data-testid="stExpandSidebarButton"]{position:fixed!important;top:14px;left:14px;z-index:1000000;
  width:42px!important;height:42px!important;min-width:42px;display:inline-flex!important;align-items:center;justify-content:center;pointer-events:auto!important;cursor:pointer}
.block-container{max-width:1040px!important;padding:3.4rem 2rem 6rem!important}
::selection{background:var(--accent);color:#fff}
*{scroll-behavior:smooth}

/* ── sidebar ── */
section[data-testid="stSidebar"]{background:var(--surface)!important;border-right:1px solid var(--line)}
section[data-testid="stSidebar"] .block-container{padding:1.6rem 1.1rem!important}
.brand{display:flex;align-items:center;gap:10px;font-family:'Bricolage Grotesque',sans-serif;font-weight:600;font-size:17px;letter-spacing:-.02em}
.mark{display:flex;gap:2.5px;align-items:center;height:24px;padding:0 7px;border-radius:8px;background:var(--ink)}
.mark b{width:2.5px;border-radius:2px;background:#fff;animation:eq 1.3s ease-in-out infinite}
.mark b:nth-child(1){height:8px}.mark b:nth-child(2){height:15px;animation-delay:.15s}
.mark b:nth-child(3){height:10px;animation-delay:.3s}.mark b:nth-child(4){height:13px;animation-delay:.45s}
@keyframes eq{50%{transform:scaleY(.45)}}
.side-h{font-size:12.5px;font-weight:600;color:var(--muted);margin:26px 0 6px}
.side-note{font-size:13px;color:var(--muted);line-height:1.55}
section[data-testid="stSidebar"] .stButton>button{width:100%;justify-content:flex-start;text-align:left;background:transparent;border:0;
  box-shadow:none;color:var(--ink2);font-weight:500;padding:.55rem .7rem;border-radius:10px;overflow:hidden}
section[data-testid="stSidebar"] .stButton>button:hover{background:var(--bg);transform:none;color:var(--ink)}
section[data-testid="stSidebar"] .stButton>button[kind="primary"]{background:var(--ink);color:#fff;justify-content:center;box-shadow:none}
section[data-testid="stSidebar"] .stButton>button[kind="primary"]:hover{background:var(--accent);color:#fff}

/* ── hero ── */
.hero{padding:.5rem 0 1.6rem}
.hero h1{font-size:clamp(40px,6.2vw,68px);line-height:1.02;font-weight:700;margin:0 0 20px;max-width:760px}
.hero p{font-size:18px;line-height:1.6;color:var(--ink2);max-width:520px;margin:0}
.wave{display:flex;align-items:center;gap:5px;height:84px;margin:34px 0 8px;mask-image:linear-gradient(90deg,transparent,#000 12%,#000 88%,transparent);
  -webkit-mask-image:linear-gradient(90deg,transparent,#000 12%,#000 88%,transparent)}
.wave i{flex:1;min-width:3px;border-radius:3px;background:var(--ink);opacity:.9;height:calc(14% + 80% * abs(sin(var(--i) * .42)) * abs(cos(var(--i) * .11)));
  transform-origin:center;animation:breathe 2.6s ease-in-out infinite;animation-delay:calc(var(--i) * -.09s)}
.wave i:nth-child(7n){background:var(--accent)}
@keyframes breathe{0%,100%{transform:scaleY(1)}50%{transform:scaleY(.38)}}
.rise{animation:rise .9s var(--ease) both}.rise.d1{animation-delay:.08s}.rise.d2{animation-delay:.16s}.rise.d3{animation-delay:.26s}
@keyframes rise{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}

/* ── inputs ── */
.stTabs [data-baseweb="tab-list"]{gap:4px;background:#E9EBEF;padding:4px;border-radius:12px;width:fit-content;border:0}
.stTabs [data-baseweb="tab"]{height:38px;padding:0 18px;border-radius:9px;color:var(--ink2);font-weight:500;font-size:14.5px;background:transparent;transition:all .25s var(--ease)}
.stTabs [aria-selected="true"]{background:var(--surface)!important;color:var(--ink)!important;box-shadow:0 1px 3px rgba(16,24,40,.12)}
.stTabs [data-baseweb="tab-highlight"],.stTabs [data-baseweb="tab-border"]{display:none}
[role="tabpanel"]{animation:fade .45s var(--ease)}
@keyframes fade{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}

.stTextInput input{background:var(--surface)!important;color:var(--ink)!important;border:1px solid var(--line2)!important;border-radius:14px!important;
  padding:17px 18px!important;font-size:16px!important;box-shadow:var(--shadow);transition:all .25s var(--ease)}
.stTextInput input::placeholder{color:#A3AAB8!important}
.stTextInput input:focus{border-color:var(--accent)!important;box-shadow:0 0 0 4px rgba(36,71,245,.14),var(--shadow)!important}
.stTextInput [data-baseweb="input"],.stTextInput [data-baseweb="base-input"]{background:transparent!important;border:0!important}
[data-testid="stFileUploaderDropzone"]{background:var(--surface)!important;border:1.5px dashed var(--line2)!important;border-radius:16px;padding:34px;
  transition:all .3s var(--ease)}
[data-testid="stFileUploaderDropzone"]:hover{border-color:var(--accent)!important;background:#FAFBFF!important;transform:translateY(-2px);box-shadow:var(--shadow)}
[data-testid="stFileUploaderDropzone"] *{color:var(--ink2)!important}
[data-testid="stFileUploaderDropzone"] button{background:var(--ink)!important;color:#fff!important;border:0!important;border-radius:10px!important}
[data-testid="stFileUploaderDropzone"] button *{color:#fff!important}

/* ── buttons ── */
.stButton>button,.stDownloadButton>button{border-radius:12px;font-weight:600;font-size:14.5px;border:1px solid var(--line2);background:var(--surface);
  color:var(--ink);padding:.62rem 1.15rem;transition:all .25s var(--ease);box-shadow:0 1px 2px rgba(16,24,40,.05)}
.stButton>button:hover,.stDownloadButton>button:hover{border-color:var(--ink);transform:translateY(-1px);color:var(--ink);box-shadow:var(--shadow)}
.stButton>button:active{transform:scale(.98)}
.stButton>button[kind="primary"]{background:var(--ink);color:#fff;border:0;padding:.85rem 1.7rem;font-size:15.5px;border-radius:14px;box-shadow:0 10px 24px -8px rgba(14,17,22,.5)}
.stButton>button[kind="primary"] *{color:#fff!important}
.stButton>button[kind="primary"]:hover{background:var(--accent);color:#fff;box-shadow:0 14px 30px -8px rgba(36,71,245,.55)}
.stButton>button:disabled{opacity:.4;transform:none;box-shadow:none}

/* ── processing ── */
.proc{background:var(--surface);border:1px solid var(--line);border-radius:24px;padding:44px 48px;box-shadow:var(--shadow-lg);animation:rise .7s var(--ease) both}
.proc h2{font-size:34px;margin:0 0 6px;font-weight:700}
.proc .sub{color:var(--muted);font-size:15.5px;margin:0 0 26px;min-height:24px}
.proc .wave{height:70px;margin:0 0 30px}
.proc .wave i{background:var(--accent);animation-duration:1.15s}
.bar{height:6px;border-radius:6px;background:var(--bg);overflow:hidden;margin-bottom:26px}
.bar span{display:block;height:100%;border-radius:6px;background:var(--ink);transition:width .9s var(--ease)}
.steps{display:grid;grid-template-columns:1fr 1fr;gap:4px 36px}
.s{display:flex;align-items:center;gap:12px;padding:9px 0;font-size:15px;color:#A3AAB8;transition:color .4s}
.s .d{flex:none;width:22px;height:22px;border-radius:50%;border:1.5px solid var(--line2);display:grid;place-items:center;font-size:12px;transition:all .4s var(--ease)}
.s.on{color:var(--ink);font-weight:600}
.s.on .d{border-color:var(--accent);border-top-color:transparent;animation:spin .8s linear infinite}
.s.ok{color:var(--ink2)}
.s.ok .d{background:var(--ok);border-color:var(--ok);color:#fff}
@keyframes spin{to{transform:rotate(360deg)}}

/* ── results ── */
.reveal{animation:reveal 1s var(--ease) both}
@keyframes reveal{from{opacity:0;transform:translateY(24px);filter:blur(6px)}to{opacity:1;transform:none;filter:blur(0)}}
.res-meta{color:var(--muted);font-size:14px;margin-bottom:10px}
.res-title{font-family:'Bricolage Grotesque','Hind Siliguri',sans-serif;font-size:clamp(32px,4.4vw,48px);line-height:1.06;font-weight:700;letter-spacing:-.03em;margin:0 0 26px;max-width:800px}
.lead{font-family:'Bricolage Grotesque','Hind Siliguri',sans-serif;font-size:clamp(21px,2.5vw,27px);line-height:1.42;font-weight:500;letter-spacing:-.015em;color:var(--ink);
  margin:12px 0 38px;max-width:820px;text-wrap:pretty}
.sec-h{display:flex;align-items:baseline;gap:10px;margin:6px 0 14px}
.sec-h b{font-family:'Bricolage Grotesque',sans-serif;font-size:20px;font-weight:600;letter-spacing:-.02em}
.sec-h span{font-size:13.5px;color:var(--muted)}
.row{display:flex;gap:14px;padding:16px 18px;background:var(--surface);border:1px solid var(--line);border-radius:14px;margin-bottom:10px;
  transition:all .3s var(--ease);box-shadow:0 1px 2px rgba(16,24,40,.03)}
.row:hover{transform:translateY(-2px);box-shadow:var(--shadow);border-color:var(--line2)}
.row .t{font-size:15.5px;line-height:1.6;color:var(--ink);padding-top:1px}
.row .k{flex:none;width:24px;height:24px;border-radius:7px;display:grid;place-items:center;font-size:13px;font-weight:700}
.row.dec{border-left:3px solid var(--accent)}
.row.dec .k{background:var(--accent-soft);color:var(--accent)}
.row.q .k{background:var(--warn-soft);color:var(--warn)}
.empty{padding:34px;text-align:center;color:var(--muted);border:1.5px dashed var(--line2);border-radius:16px;font-size:15px}

.stCheckbox{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:14px 18px;margin-bottom:10px;transition:all .3s var(--ease);box-shadow:0 1px 2px rgba(16,24,40,.03)}
.stCheckbox:hover{transform:translateY(-2px);box-shadow:var(--shadow);border-color:var(--line2)}
.stCheckbox label{align-items:flex-start;gap:8px}
.stCheckbox p{font-size:15.5px!important;line-height:1.55;color:var(--ink)!important;transition:color .3s}
.stCheckbox [data-baseweb="checkbox"] span:first-child{border-radius:7px!important}
.stCheckbox:has(input:checked) p{color:var(--muted)!important;text-decoration:line-through;text-decoration-color:var(--line2)}
.stCheckbox:has(input:checked){background:#FAFBFC}
.progress{font-size:13.5px;color:var(--muted);margin:-4px 0 16px}
.progress b{color:var(--ok);font-weight:600}

.doc{background:var(--surface);border:1px solid var(--line);border-radius:18px;padding:30px 34px;font-size:16px;line-height:1.85;color:var(--ink2);box-shadow:var(--shadow)}
.doc p{margin:0 0 1.1em;max-width:70ch}.doc p:last-child{margin:0}
.doc mark{background:#FFE98A;color:var(--ink);border-radius:4px;padding:0 2px}

/* ── chat ── */
[data-testid="stChatMessage"]{background:var(--surface)!important;border:1px solid var(--line);border-radius:16px;padding:16px 18px;animation:fade .5s var(--ease);box-shadow:0 1px 2px rgba(16,24,40,.03)}
[data-testid="stChatMessage"] p{font-size:15.5px;line-height:1.7;color:var(--ink)!important}
[data-testid="stChatInput"]{border-radius:16px!important;border:1px solid var(--line2)!important;background:var(--surface)!important;box-shadow:var(--shadow-lg)}
[data-testid="stChatInput"] textarea{color:var(--ink)!important;font-size:15.5px}
[data-testid="stBottom"],[data-testid="stBottom"]>div{background:linear-gradient(0deg,var(--bg) 60%,transparent)!important}
.hint{color:var(--muted);font-size:14px;margin:4px 0 12px}

.stAlert{border-radius:14px}
[data-testid="stSpinner"] *{color:var(--ink2)!important}
@media(max-width:760px){.steps{grid-template-columns:1fr}.proc{padding:28px 22px}.block-container{padding:2rem 1.1rem 5rem!important}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
/* hard overrides so a leftover dark theme can't leak through */
.brand,.brand *{color:var(--ink)!important}
.stTabs [data-baseweb="tab-list"]{background:#E9EBEF!important}
.stTabs [data-baseweb="tab"] p,.stTabs [data-baseweb="tab"] span{color:inherit!important;font-weight:inherit}
.stTabs [data-baseweb="tab"]{color:var(--ink2)!important}
.stTabs [aria-selected="true"]{color:var(--ink)!important;background:var(--surface)!important}
.stButton>button p,.stDownloadButton>button p{color:inherit!important}
.stButton>button[kind="primary"] p{color:#fff!important}
.stButton>button:disabled{background:#E3E6EB!important;color:#9AA2B1!important;box-shadow:none!important}
.stButton>button:disabled p{color:#9AA2B1!important}
section[data-testid="stSidebar"] .stButton>button>div{justify-content:flex-start;width:100%}
section[data-testid="stSidebar"] .stButton>button[kind="primary"]>div{justify-content:center}
section[data-testid="stSidebar"] .stButton>button p{color:var(--ink2)!important}
section[data-testid="stSidebar"] .stButton>button[kind="primary"] p{color:#fff!important}
.stCheckbox{width:100%!important}.stCheckbox label{width:100%}
.stCheckbox [data-baseweb="checkbox"]>span:first-child{background:#fff!important;border:1.5px solid var(--line2)!important}
.stCheckbox [data-baseweb="checkbox"]:has(input:checked)>span:first-child{background:var(--ok)!important;border-color:var(--ok)!important}
.stCheckbox p,.stCheckbox label{color:var(--ink)!important}
[data-testid="stChatMessage"] *{color:var(--ink)}
[data-testid="stChatInput"],[data-testid="stChatInput"]>div,[data-testid="stChatInput"] textarea{background:var(--surface)!important}
[data-testid="stChatInput"] textarea::placeholder{color:#A3AAB8!important}
[data-testid="stChatInput"] button{background:var(--ink)!important}
[data-testid="stChatInput"] button svg{fill:#fff!important}
[data-testid="stChatMessageAvatarUser"],[data-testid="stChatMessageAvatarAssistant"]{background:var(--bg)!important}
.stTextInput input{-webkit-text-fill-color:var(--ink)}
.stTextInput input::placeholder{-webkit-text-fill-color:#A3AAB8}
/* streamlit >=1.5x DOM */
[role="tablist"]{background:#E9EBEF!important;padding:4px!important;border-radius:12px!important;width:fit-content!important;gap:4px!important;border:0!important;box-shadow:none!important}
[role="tablist"] ~ div:not([role="tabpanel"]){display:none!important}
[role="tab"]{height:38px!important;padding:0 18px!important;border-radius:9px!important;color:var(--ink2)!important;background:transparent!important;border:0!important;
  transition:all .25s var(--ease)!important;box-shadow:none!important}
[role="tab"] p,[role="tab"] span{color:inherit!important;font-size:14.5px!important;font-weight:500!important}
[role="tab"][aria-selected="true"]{background:var(--surface)!important;color:var(--ink)!important;box-shadow:0 1px 3px rgba(16,24,40,.12)!important}
[role="tab"][aria-selected="true"]::after,[role="tab"]::after,[role="tab"]::before{display:none!important}
[data-testid="stCheckbox"],.stElementContainer:has([data-testid="stCheckbox"]){width:100%!important}
[role="tablist"]::after,[role="tablist"]::before{display:none!important}
[role="tablist"] + *:not([role="tabpanel"]){display:none!important}
[data-baseweb="tab-highlight"],[data-testid="stTabHighlight"]{display:none!important}
[data-testid="stCheckbox"] label{width:100%!important;display:flex;align-items:center;gap:12px}
[data-testid="stCheckbox"] label>div:nth-of-type(1){background:#fff!important;border:1.5px solid var(--line2)!important;border-radius:7px!important;width:22px!important;height:22px!important;flex:none;transition:all .25s var(--ease)}
[data-testid="stCheckbox"] label:has(input:checked)>div:nth-of-type(1){background:var(--ok)!important;border-color:var(--ok)!important}
[data-testid="stCheckbox"] p{margin:0}
/* decisions */
[class*="st-key-dec"]{background:var(--surface);border:1px solid var(--line);border-left:3px solid var(--accent);border-radius:16px;padding:20px 24px 14px;margin-bottom:14px;
  box-shadow:0 1px 2px rgba(16,24,40,.03);transition:all .3s var(--ease)}
[class*="st-key-dec"]:hover{transform:translateY(-2px);box-shadow:var(--shadow);border-color:var(--line2);border-left-color:var(--accent)}
.dec-top{display:flex;align-items:center;gap:10px;margin-bottom:8px}
.dec-n{font-size:12.5px;font-weight:600;color:var(--accent);background:var(--accent-soft);padding:3px 10px;border-radius:999px}
.dec-t{font-family:'Bricolage Grotesque','Hind Siliguri',sans-serif;font-size:20px;line-height:1.3;font-weight:600;letter-spacing:-.02em;color:var(--ink);margin:0}
.dec-d{font-size:15.5px;line-height:1.65;color:var(--ink2);margin:8px 0 0}
.dec-ctx{margin:10px 0 6px;padding:14px 16px;background:var(--accent-soft);border-radius:12px;font-size:15px;line-height:1.7;color:var(--ink)}
[class*="st-key-dec"] .stButton>button{background:transparent;border:0;box-shadow:none;color:var(--accent)!important;padding:.3rem 0;font-size:14px}
[class*="st-key-dec"] .stButton>button p{color:var(--accent)!important}
[class*="st-key-dec"] .stButton>button:hover{transform:none;box-shadow:none;text-decoration:underline}
.dec-bar{display:flex;justify-content:space-between;align-items:center;margin:4px 0 16px}
.dec-bar span{color:var(--muted);font-size:14.5px}

/* ask */
.ask-hero{padding:18px 0 22px;max-width:620px}
.ask-hero h3{font-size:30px;font-weight:700;margin:0 0 8px}
.ask-hero p{color:var(--ink2);font-size:16px;line-height:1.6;margin:0}
.orb{width:46px;height:46px;border-radius:14px;background:var(--ink);display:flex;gap:3px;align-items:center;justify-content:center;margin-bottom:16px;box-shadow:0 10px 24px -8px rgba(14,17,22,.5)}
.orb b{width:3px;border-radius:2px;background:#fff;animation:eq 1.2s ease-in-out infinite}
.orb b:nth-child(1){height:10px}.orb b:nth-child(2){height:20px;animation-delay:.15s}.orb b:nth-child(3){height:14px;animation-delay:.3s}.orb b:nth-child(4){height:18px;animation-delay:.45s}
[class*="st-key-sg"] button{min-height:84px;height:auto;padding:16px 18px;border-radius:16px;white-space:normal;justify-content:flex-start;text-align:left;font-weight:500;
  background:var(--surface);align-items:flex-start}
[class*="st-key-sg"] button>div{justify-content:flex-start;text-align:left;width:100%}
[class*="st-key-sg"] button p{text-align:left;font-size:15px;line-height:1.45}
[class*="st-key-sg"] button:hover{border-color:var(--accent);box-shadow:0 12px 28px -12px rgba(36,71,245,.35)}
[class*="st-key-chip"] button{border-radius:999px;padding:.32rem .95rem;font-size:13.5px;font-weight:500;background:var(--surface);min-height:0}
[class*="st-key-chip"] button:hover{border-color:var(--accent);color:var(--accent)!important}
.chat-head{display:flex;align-items:center;gap:10px;font-family:'Bricolage Grotesque',sans-serif;font-size:19px;font-weight:600;letter-spacing:-.02em}
.chat-head small{font-family:'Hanken Grotesk',sans-serif;font-size:13.5px;font-weight:400;color:var(--muted);letter-spacing:0}
.live{width:8px;height:8px;border-radius:50%;background:var(--ok);box-shadow:0 0 0 4px var(--ok-soft)}
[data-testid="stChatMessage"]:has([aria-label="Chat message from user"]){flex-direction:row-reverse;margin-left:auto;width:fit-content;max-width:78%;
  background:var(--ink)!important;border:0!important;border-radius:20px 20px 6px 20px;padding:12px 18px}
[data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) *{color:#fff!important}
[data-testid="stChatMessage"]:has([aria-label="Chat message from user"])>div:first-child{display:none!important}
[data-testid="stChatMessage"]:has([aria-label="Chat message from assistant"]){background:transparent!important;border:0!important;box-shadow:none!important;padding:8px 0}
[data-testid="stChatMessage"]:has([aria-label="Chat message from assistant"]) p,[data-testid="stChatMessage"]:has([aria-label="Chat message from assistant"]) li{font-size:16px;line-height:1.78}
[data-testid="stChatMessage"]:has([aria-label="Chat message from assistant"])>div:first-child{background:var(--ink)!important;border-radius:11px!important;width:34px;height:34px;display:grid;place-items:center;flex:none}
.typing{display:flex;gap:5px;padding:10px 2px}
.typing i{width:8px;height:8px;border-radius:50%;background:var(--accent);animation:bounce 1.1s ease-in-out infinite}
.typing i:nth-child(2){animation-delay:.15s}.typing i:nth-child(3){animation-delay:.3s}
@keyframes bounce{0%,80%,100%{transform:translateY(0);opacity:.35}40%{transform:translateY(-6px);opacity:1}}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ───────────────────────── State & helpers ─────────────────────────
ss = st.session_state
ss.setdefault("results", None)
ss.setdefault("chat", [])
ss.setdefault("history", [])
ss.setdefault("active", None)
ss.setdefault("fresh", False)

BULLET = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+")


def esc(t) -> str:
    return _html.escape(str(t))


def to_items(text) -> list:
    if not text:
        return []
    if isinstance(text, (list, tuple)):
        return [str(x).strip() for x in text if str(x).strip()]
    items = []
    for l in (l for l in str(text).splitlines() if l.strip()):
        if BULLET.match(l):
            items.append(BULLET.sub("", l).strip().replace("**", ""))
        elif items and l.startswith(" "):
            items[-1] += " " + l.strip()
        else:
            items.append(l.strip().replace("**", ""))
    return items


def rows(text, cls, mark, empty):
    items = to_items(text)
    if not items:
        st.markdown(f'<div class="empty">{empty}</div>', unsafe_allow_html=True)
        return
    st.markdown("".join(f'<div class="row {cls}"><div class="k">{mark}</div><div class="t">{esc(i)}</div></div>'
                        for i in items), unsafe_allow_html=True)


def split_title(t: str):
    m = re.match(r"^(.{3,90}?)\s*(?::|—|–|\s-\s)\s*(.+)$", t)
    return (m.group(1).strip(), m.group(2).strip()) if m else (t, "")


def fmt_ctx(text: str) -> str:
    out = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", esc(text))
    return out.replace("\n", "<br>")


def ask_safe(chain, q):
    try:
        return str(ask_question(chain, q))
    except Exception as e:
        return f"Couldn't get an answer: {e}. Try asking again."


def head(title, sub=""):
    st.markdown(f'<div class="sec-h"><b>{title}</b><span>{sub}</span></div>', unsafe_allow_html=True)


def build_markdown(r) -> str:
    def sec(h, t):
        its = to_items(t)
        return f"## {h}\n" + ("\n".join(f"- {i}" for i in its) if its else "_None_") + "\n\n"
    return (f"# {r['title']}\n\n## Summary\n{r['summary']}\n\n" + sec("Action items", r["action_items"])
            + sec("Decisions", r["key_decissions"]) + sec("Open questions", r["open_questions"])
            + f"## Transcript\n{r['transcript']}\n")


STEPS = [
    ("Preparing audio", "Extracting and splitting the audio."),
    ("Transcribing", "Turning speech into text. Long recordings take a little longer."),
    ("Naming the meeting", "Finding a clear title."),
    ("Writing the summary", "Condensing the conversation."),
    ("Finding action items", "Looking for who owns what."),
    ("Capturing decisions", "Noting what was agreed."),
    ("Listing open questions", "Spotting what's still unresolved."),
    ("Preparing Q&A", "Indexing the transcript so you can ask questions."),
]


def proc_html(i: int) -> str:
    done = i / len(STEPS)
    items = "".join(
        f'<div class="s {"ok" if n < i else "on" if n == i else ""}"><span class="d">{"✓" if n < i else ""}</span>{lab}</div>'
        for n, (lab, _) in enumerate(STEPS))
    sub = STEPS[i][1] if i < len(STEPS) else "All done."
    title = "Reading your meeting" if i < len(STEPS) else "Your brief is ready"
    return (f'<div class="proc"><h2>{title}</h2><p class="sub">{sub}</p><div class="wave">{BARS}</div>'
            f'<div class="bar"><span style="width:{max(done * 100, 4):.0f}%"></span></div><div class="steps">{items}</div></div>')


def run_pipeline_ui(source: str, slot):
    t0 = time.time()
    slot.markdown(proc_html(0), unsafe_allow_html=True)
    chunks = process_input(source)
    slot.markdown(proc_html(1), unsafe_allow_html=True)
    transcript = transcribe_all(chunks)
    slot.markdown(proc_html(2), unsafe_allow_html=True)
    title = generate_title(transcript)
    slot.markdown(proc_html(3), unsafe_allow_html=True)
    summary = summarize(transcript)
    slot.markdown(proc_html(4), unsafe_allow_html=True)
    actions = extract_action_items(transcript)
    slot.markdown(proc_html(5), unsafe_allow_html=True)
    decisions = extract_key_decision(transcript)
    slot.markdown(proc_html(6), unsafe_allow_html=True)
    questions = extract_questions(transcript)
    slot.markdown(proc_html(7), unsafe_allow_html=True)
    chain = build_rag_chain(transcript)
    slot.markdown(proc_html(8), unsafe_allow_html=True)
    time.sleep(.7)
    return {"title": title, "transcript": transcript, "summary": summary, "action_items": actions,
            "key_decissions": decisions, "open_questions": questions, "rag_chain": chain,
            "created": datetime.now(), "duration": time.time() - t0, "chat": []}


def stream_words(text: str):
    for w in re.findall(r"\S+\s*", text):
        yield w
        time.sleep(0.025)


# ───────────────────────── Sidebar ─────────────────────────
with st.sidebar:
    st.markdown('<div class="brand"><div class="mark"><b></b><b></b><b></b><b></b></div>Meeting Assistant</div>',
                unsafe_allow_html=True)
    st.write("")
    if st.button("New meeting", type="primary", use_container_width=True):
        ss.results, ss.chat, ss.active = None, [], None
        st.rerun()
    st.markdown('<div class="side-h">Recent</div>', unsafe_allow_html=True)
    if not ss.history:
        st.markdown('<div class="side-note">Meetings you analyze show up here, so you can jump back to them.</div>',
                    unsafe_allow_html=True)
    for idx in range(len(ss.history) - 1, max(len(ss.history) - 9, -1), -1):
        h = ss.history[idx]
        t = h["title"] if len(h["title"]) < 30 else h["title"][:28] + "…"
        if st.button(t, key=f"h{idx}", use_container_width=True):
            ss.results, ss.active, ss.chat, ss.fresh = h, idx, h.get("chat", []), True
            st.rerun()
    if DEMO:
        st.markdown('<div class="side-h">Mode</div><div class="side-note">Demo data. No audio is processed.</div>',
                    unsafe_allow_html=True)

# ───────────────────────── Landing ─────────────────────────
if ss.results is None:
    stage = st.empty()
    with stage.container():
        st.markdown(f"""
        <div class="hero">
          <h1 class="rise">Every meeting,<br>understood in minutes.</h1>
          <p class="rise d1">Add a YouTube link or a recording. You get the summary, who owes what, what was decided, and a chat that answers questions about it.</p>
          <div class="wave rise d2" aria-hidden="true">{BARS}</div>
        </div>""", unsafe_allow_html=True)

        st.markdown('<div class="rise d3">', unsafe_allow_html=True)
        tab_url, tab_file = st.tabs(["YouTube link", "Upload recording"])
        source = None
        with tab_url:
            st.write("")
            url = st.text_input("URL", placeholder="Paste a YouTube link", label_visibility="collapsed")
            if url.strip():
                source = url.strip()
        with tab_file:
            st.write("")
            up = st.file_uploader("File", type=["mp3", "wav", "m4a", "mp4", "mov", "mkv", "webm", "ogg", "flac"],
                                  label_visibility="collapsed")
            if up:
                source = up
        st.write("")
        go = st.button("Analyze meeting", type="primary", disabled=source is None)
        st.markdown("</div>", unsafe_allow_html=True)

    if go and source is not None:
        stage.empty()
        slot = st.empty()
        try:
            if isinstance(source, str):
                src, label = source, source
            else:
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(source.name)[1]) as tmp:
                    tmp.write(source.getbuffer())
                    src, label = tmp.name, source.name
            res = run_pipeline_ui(src, slot)
            res["source"] = label
            ss.history.append(res)
            ss.results, ss.active, ss.chat, ss.fresh = res, len(ss.history) - 1, [], True
            st.rerun()
        except Exception as e:
            slot.empty()
            st.error(f"Couldn't finish the analysis: {e}. Check the link or file and try again.")
            if st.button("Back"):
                st.rerun()

# ───────────────────────── Results ─────────────────────────
else:
    r = ss.results
    acts, decs, qs = to_items(r["action_items"]), to_items(r["key_decissions"]), to_items(r["open_questions"])
    words = len(str(r["transcript"]).split())
    wrap = "reveal" if ss.fresh else ""
    ss.fresh = False

    c1, c2 = st.columns([5, 1.6], vertical_alignment="bottom")
    with c1:
        st.markdown(f'<div class="{wrap}"><div class="res-meta">{r["created"]:%b %d, %Y} &nbsp;·&nbsp; {max(words // 150, 1)} min read '
                    f'&nbsp;·&nbsp; analyzed in {r["duration"]:.0f}s</div><h1 class="res-title">{esc(r["title"])}</h1></div>',
                    unsafe_allow_html=True)
    with c2:
        slug = re.sub(r"[^A-Za-z0-9]+", "-", r["title"]).strip("-").lower() or "meeting"
        st.download_button("Export report", build_markdown(r), file_name=f"{slug}.md", use_container_width=True)

    t1, t2, t3, t4, t5 = st.tabs(["Overview", f"Actions · {len(acts)}", f"Decisions · {len(decs)}",
                                  "Transcript", "Ask"])

    with t1:
        st.markdown(f'<p class="lead">{esc(r["summary"])}</p>', unsafe_allow_html=True)
        a, b = st.columns(2, gap="large")
        with a:
            head("Action items", f"{len(acts)} to follow up")
            rows(r["action_items"], "", "✓", "No action items came up.")
        with b:
            head("Decisions", f"{len(decs)} agreed")
            rows(r["key_decissions"], "dec", "◆", "No decisions were made.")
        if qs:
            st.write("")
            head("Still open", f"{len(qs)} questions")
            rows(r["open_questions"], "q", "?", "")

    with t2:
        if not acts:
            st.markdown('<div class="empty">No action items came up in this meeting.</div>', unsafe_allow_html=True)
        else:
            k = f"done_{id(r)}"
            done = sum(bool(ss.get(f"{k}_{i}")) for i in range(len(acts)))
            st.markdown(f'<div class="progress"><b>{done}</b> of {len(acts)} done. Tick items off as you go.</div>',
                        unsafe_allow_html=True)
            for i, it in enumerate(acts):
                st.checkbox(it, key=f"{k}_{i}")

    with t3:
        if not decs:
            st.markdown('<div class="empty">No decisions were made in this meeting.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="dec-bar"><span>{len(decs)} decision{"s" if len(decs) != 1 else ""} agreed in this meeting. '
                        f'Open any one to see the context behind it.</span></div>', unsafe_allow_html=True)
            ctx = ss.setdefault("dec_ctx", {})
            for i, d in enumerate(decs):
                ttl, det = split_title(d)
                ck = f"{id(r)}_{i}"
                with st.container(key=f"dec{i}"):
                    st.markdown(f'<div class="dec-top"><span class="dec-n">Decision {i + 1}</span></div>'
                                f'<p class="dec-t">{esc(ttl)}</p>' + (f'<p class="dec-d">{esc(det)}</p>' if det else ""),
                                unsafe_allow_html=True)
                    if ck in ctx:
                        st.markdown('<div class="dec-ctx">' + fmt_ctx(ctx[ck]) + '</div>', unsafe_allow_html=True)
                    elif r.get("rag_chain") and st.button("Why was this decided?", key=f"why{ck}"):
                        with st.spinner("Checking the transcript…"):
                            ctx[ck] = ask_safe(r["rag_chain"], f"Briefly explain the context and reasoning behind this decision, "
                                                               f"using only what was said in the meeting: {d}")
                        st.rerun()
            st.download_button("Export decisions", "# Decisions\n\n" + "\n".join(f"- {d}" for d in decs),
                               file_name="decisions.md")
        if qs:
            st.write("")
            head("Still open", "Questions nobody answered")
            rows(r["open_questions"], "q", "?", "")

    with t4:
        q = st.text_input("Search", placeholder="Search the transcript", label_visibility="collapsed", key="tsearch")
        sentences = re.split(r"(?<=[.!?।])\s+", str(r["transcript"]).strip())
        if q.strip():
            pat = re.compile(re.escape(q.strip()), re.I)
            hits = [s for s in sentences if pat.search(s)]
            st.markdown(f'<div class="progress">{len(hits)} matching lines</div>', unsafe_allow_html=True)
            body = "".join(f"<p>{pat.sub(lambda m: f'<mark>{esc(m.group(0))}</mark>', esc(s))}</p>" for s in hits) \
                or '<p>Nothing matches that search.</p>'
        else:
            body = "".join("<p>" + esc(" ".join(sentences[i:i + 4])) + "</p>" for i in range(0, len(sentences), 4))
        st.markdown(f'<div class="doc">{body}</div>', unsafe_allow_html=True)
        st.write("")
        st.download_button("Download transcript", str(r["transcript"]), file_name="transcript.txt")

    with t5:
        if not r.get("rag_chain"):
            st.warning("Questions aren't available for this meeting because the search index couldn't be built.")
        else:
            msgs = st.container()
            chips = st.container()
            prompt = st.chat_input("Ask about this meeting") or ss.pop("pending", None)

            with msgs:
                if ss.chat or prompt:
                    h1, h2 = st.columns([5, 1.3], vertical_alignment="center")
                    h1.markdown(f'<div class="chat-head"><span class="live"></span>Ask this meeting '
                                f'<small>Answers come from the transcript</small></div>', unsafe_allow_html=True)
                    if h2.button("Clear chat", key="clr", use_container_width=True):
                        ss.chat = []
                        if ss.active is not None:
                            ss.history[ss.active]["chat"] = []
                        st.rerun()
                    st.write("")
                else:
                    st.markdown('<div class="ask-hero"><div class="orb"><b></b><b></b><b></b><b></b></div>'
                                '<h3>Ask this meeting anything</h3>'
                                '<p>Get answers grounded in what was actually said. Pick a starting point or type your own question below.</p></div>',
                                unsafe_allow_html=True)
                    starters = ["Summarize this meeting in three bullets", "What was decided, and why?",
                                "Who owns which tasks, and by when?", "What risks or blockers came up?",
                                "Which questions are still unanswered?", "Draft a follow-up email to attendees"]
                    for row in (starters[:3], starters[3:]):
                        for col, q_ in zip(st.columns(3, gap="medium"), row):
                            if col.button(q_, key=f"sg_{q_}", use_container_width=True):
                                ss.pending = q_
                                st.rerun()

                for m in ss.chat:
                    with st.chat_message(m["role"], avatar="🧑" if m["role"] == "user" else "🎙️"):
                        st.markdown(m["content"])

                if prompt:
                    ss.chat.append({"role": "user", "content": prompt})
                    with st.chat_message("user", avatar="🧑"):
                        st.markdown(prompt)
                    with st.chat_message("assistant", avatar="🎙️"):
                        ph = st.empty()
                        ph.markdown('<div class="typing"><i></i><i></i><i></i></div>', unsafe_allow_html=True)
                        ans = ask_safe(r["rag_chain"], prompt)
                        ph.empty()
                        st.write_stream(stream_words(ans))
                    ss.chat.append({"role": "assistant", "content": ans})
                    if ss.active is not None:
                        ss.history[ss.active]["chat"] = ss.chat

            if ss.chat and ss.chat[-1]["role"] == "assistant":
                with chips:
                    cc = st.columns([1, 1.7, 1.4, 3])
                    for n, (col, q_) in enumerate(zip(cc, ["Go deeper", "Turn into action items", "Make it shorter"])):
                        if col.button(q_, key=f"chip{n}{len(ss.chat)}"):
                            ss.pending = {"Go deeper": "Go into more detail on your last answer.",
                                          "Turn into action items": "Turn your last answer into a short list of action items.",
                                          "Make it shorter": "Say your last answer again in one or two sentences."}[q_]
                            st.rerun()