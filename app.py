"""
ReleaseGuardian v10 — Expert UI Designer Build
Dark premium theme. Space Grotesk. No sidebar. No duplicates.
Designed like Linear/Raycast — rich dark, vibrant accents, readable.
"""

import streamlit as st
import streamlit.components.v1 as components
import json
import html as html_lib
import math
from agents.context_builder import build_release_context
from agents.risk_analyst import analyze_risk
from agents.recovery_planner import generate_recovery_plan
from data.demo_scenarios import get_demo_scenarios

st.set_page_config(page_title="ReleaseGuardian", page_icon="🛡️", layout="wide", initial_sidebar_state="collapsed")

# ──────────────────────────────────────
# DESIGN SYSTEM — One place, one truth
# ──────────────────────────────────────
# bg-base: #111118  (deep navy, not pure black)
# bg-card: #1a1a24  (elevated surface)
# bg-input: #222230 (input fields)
# border: #2a2a3a   (subtle)
# border-hover: #3a3a50
# text-primary: #ececf1 (high contrast)
# text-secondary: #8e8ea0
# text-muted: #5a5a6e
# accent: #7c5cfc (vibrant purple)
# accent-light: #9d85ff
# success: #3ecf8e
# warning: #f5a623
# danger: #ef4444
# info: #4aa4f5

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

/* Reset Streamlit */
#MainMenu,footer,header,.stDeployButton,section[data-testid="stSidebar"]{display:none!important;}
.block-container{padding:1rem 2rem!important;max-width:1120px!important;}
div[data-testid="stAppViewBlockContainer"]{background:#111118!important;}
.stApp{background:#111118!important;}

/* Typography */
*{font-family:'Space Grotesk',sans-serif!important;}
h1,h2,h3{color:#ececf1!important;}
p,li,span,div{color:#ececf1;}

/* Inputs */
.stSelectbox>div>div{
    background:#222230!important;border:1px solid #2a2a3a!important;
    color:#ececf1!important;border-radius:10px!important;
}
.stSelectbox label{color:#8e8ea0!important;font-size:12px!important;font-weight:600!important;}
.stFileUploader label{color:#8e8ea0!important;font-size:12px!important;font-weight:600!important;}
.stFileUploader>div>div{
    background:#1a1a24!important;border:1px dashed #2a2a3a!important;border-radius:10px!important;
}
.stFileUploader>div>div:hover{border-color:#7c5cfc!important;}
/* FIX: Upload button duplicate text — hide original, show custom via ::after */
[data-testid="stFileUploaderDropzone"] [data-testid="stBaseButton-secondary"]{
    text-indent:-9999px!important;line-height:0!important;
    background:#222230!important;border:1px solid #3a3a50!important;
    border-radius:8px!important;padding:8px 16px!important;
    color:transparent!important;overflow:hidden!important;
}
[data-testid="stFileUploaderDropzone"] [data-testid="stBaseButton-secondary"]::after{
    content:"Browse files";
    text-indent:0!important;display:block!important;
    line-height:normal!important;font-size:13px!important;
    color:#ececf1!important;font-weight:500!important;
    font-family:'Space Grotesk',sans-serif!important;
}
[data-testid="stFileUploaderDropzone"] [data-testid="stBaseButton-secondary"]:hover{
    border-color:#7c5cfc!important;background:#2a2a3a!important;
}
/* File uploader drop text */
[data-testid="stFileUploaderDropzone"] span{color:#5a5a6e!important;font-size:12px!important;}
[data-testid="stFileUploaderDropzone"] small{color:#3a3a50!important;font-size:11px!important;}

/* Buttons */
.stButton>button{
    background:linear-gradient(135deg,#7c5cfc,#6246ea)!important;
    border:none!important;color:white!important;
    font-weight:600!important;font-size:15px!important;
    border-radius:10px!important;padding:14px 24px!important;
    transition:all .25s!important;
    box-shadow:0 4px 15px rgba(124,92,252,0.3)!important;
}
.stButton>button:hover{
    transform:translateY(-1px)!important;
    box-shadow:0 8px 25px rgba(124,92,252,0.4)!important;
    background:linear-gradient(135deg,#8b6fff,#7c5cfc)!important;
}

/* Progress */
.stProgress>div>div{background:linear-gradient(90deg,#7c5cfc,#4aa4f5)!important;border-radius:6px!important;}

/* Alerts */
.stAlert{background:#1a1a24!important;border:1px solid #2a2a3a!important;border-radius:10px!important;color:#ececf1!important;}

/* Tabs */
.stTabs [data-baseweb="tab-list"]{
    background:#1a1a24!important;border-radius:12px!important;
    padding:4px!important;gap:2px!important;
    border:1px solid #2a2a3a!important;
}
.stTabs [data-baseweb="tab"]{
    border-radius:8px!important;color:#5a5a6e!important;
    font-weight:600!important;font-size:13px!important;padding:10px 16px!important;
}
.stTabs [aria-selected="true"]{
    background:#222230!important;color:#ececf1!important;
    box-shadow:0 2px 8px rgba(0,0,0,0.2)!important;
}
.stTabs [data-baseweb="tab-panel"]{padding-top:16px!important;}

/* Expanders */
.streamlit-expanderHeader,
[data-testid="stExpander"] summary{
    background:#1a1a24!important;border:1px solid #2a2a3a!important;
    border-radius:10px!important;color:#ececf1!important;font-weight:600!important;
}
[data-testid="stExpander"] summary span{color:#ececf1!important;}
[data-testid="stExpander"] [data-testid="stExpanderDetails"]{background:#1a1a24!important;border:1px solid #2a2a3a!important;border-top:none!important;border-radius:0 0 10px 10px!important;}
.streamlit-expanderContent{background:#1a1a24!important;border:1px solid #2a2a3a!important;border-top:none!important;border-radius:0 0 10px 10px!important;}

/* Checkboxes */
.stCheckbox label{color:#ececf1!important;}
.stCheckbox label span{color:#c0c0d0!important;font-size:14px!important;}

/* Code blocks */
.stCodeBlock{border-radius:10px!important;}

/* Divider */
hr{border-color:#2a2a3a!important;}

/* Markdown text */
.stMarkdown p{color:#c0c0d0!important;}
.stMarkdown strong{color:#ececf1!important;}
.stMarkdown a{color:#7c5cfc!important;}

/* JSON viewer */
.stJson{background:#1a1a24!important;border-radius:10px!important;}

/* Download button */
.stDownloadButton>button{
    background:#1a1a24!important;border:1px solid #2a2a3a!important;
    color:#ececf1!important;border-radius:10px!important;
}
.stDownloadButton>button:hover{border-color:#7c5cfc!important;}
</style>
"""

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

# === STATE ===
if "results" not in st.session_state: st.session_state.results = None
if "agent_phase" not in st.session_state: st.session_state.agent_phase = None
if "_inp" not in st.session_state: st.session_state._inp = None
if "_pf" not in st.session_state: st.session_state._pf = None
if "_rk" not in st.session_state: st.session_state._rk = None
if "splash_done" not in st.session_state: st.session_state.splash_done = False

def esc(v):
    if not v: return ""
    return html_lib.escape(str(v)).replace("\n","\\n").replace("`","\\`")

# ──────────────────────────────────────
# SPLASH SCREEN (only on first load)
# ──────────────────────────────────────
if not st.session_state.splash_done:
    components.html("""<!DOCTYPE html><html><head>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box;}
body{font-family:'Space Grotesk',sans-serif;background:#111118;overflow:hidden;height:100vh;}

.splash{position:fixed;inset:0;background:#111118;z-index:999;display:flex;flex-direction:column;align-items:center;justify-content:center;}

/* Particle canvas behind everything */
canvas{position:absolute;inset:0;z-index:0;}

/* Content */
.content{position:relative;z-index:1;text-align:center;}

/* Logo container with orbit rings */
.logo-wrap{position:relative;width:120px;height:120px;margin:0 auto 24px;}
.orbit{position:absolute;border-radius:50%;border:1px solid transparent;animation-timing-function:linear;animation-iteration-count:infinite;}
.orbit-1{inset:-10px;border-top-color:rgba(124,92,252,0.3);border-right-color:rgba(124,92,252,0.05);animation:orbitSpin 3s linear infinite;}
.orbit-2{inset:-24px;border-bottom-color:rgba(74,164,245,0.2);border-left-color:rgba(74,164,245,0.03);animation:orbitSpin 5s linear infinite reverse;}
.orbit-3{inset:-38px;border-top-color:rgba(62,207,142,0.15);animation:orbitSpin 7s linear infinite;}

/* Logo itself */
.logo{
    width:80px;height:80px;border-radius:22px;
    background:linear-gradient(135deg,#7c5cfc,#6246ea);
    display:flex;align-items:center;justify-content:center;
    font-size:36px;position:absolute;top:20px;left:20px;
    box-shadow:0 0 40px rgba(124,92,252,0.3),0 0 80px rgba(124,92,252,0.1);
    opacity:0;
    animation:logoIn 0.8s 0.2s cubic-bezier(.16,1,.3,1) forwards;
}

/* Title */
.title{
    font-size:38px;font-weight:700;color:#ececf1;
    letter-spacing:-1px;opacity:0;
    animation:slideUp 0.6s 0.8s cubic-bezier(.16,1,.3,1) forwards;
}

/* Subtitle */
.subtitle{
    font-size:14px;color:#5a5a6e;margin-top:6px;opacity:0;
    animation:slideUp 0.5s 1.1s cubic-bezier(.16,1,.3,1) forwards;
}

/* Divider line */
.line{
    width:0;height:2px;margin:20px auto;
    background:linear-gradient(90deg,transparent,#7c5cfc,transparent);
    animation:lineGrow 0.6s 1.5s ease forwards;
}

/* Tagline */
.tagline{max-width:480px;text-align:center;opacity:0;animation:slideUp 0.6s 1.8s cubic-bezier(.16,1,.3,1) forwards;}
.tagline h2{font-size:22px;font-weight:600;color:#c0c0d0;line-height:1.5;margin-bottom:6px;}
.tagline p{font-size:13px;color:#5a5a6e;line-height:1.6;}

/* Loading bar at bottom */
.loader{
    position:absolute;bottom:60px;left:50%;transform:translateX(-50%);
    width:200px;height:3px;background:#222230;border-radius:2px;overflow:hidden;
    opacity:0;animation:fadeIn 0.3s 2.2s forwards;
}
.loader-fill{
    height:100%;width:0;border-radius:2px;
    background:linear-gradient(90deg,#7c5cfc,#4aa4f5,#3ecf8e);
    animation:loadFill 1.5s 2.4s ease forwards;
}
.loader-text{
    position:absolute;bottom:38px;left:50%;transform:translateX(-50%);
    font-size:11px;color:#3a3a50;letter-spacing:1px;
    opacity:0;animation:fadeIn 0.3s 2.2s forwards;
}

/* Exit animation on entire splash */
.splash{animation:splashOut 0.8s 4.2s cubic-bezier(.4,0,1,1) forwards;}

@keyframes orbitSpin{to{transform:rotate(360deg)}}
@keyframes logoIn{from{opacity:0;transform:scale(0.3) rotate(-10deg)}to{opacity:1;transform:scale(1) rotate(0deg)}}
@keyframes slideUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}
@keyframes lineGrow{from{width:0}to{width:80px}}
@keyframes fadeIn{to{opacity:1}}
@keyframes loadFill{from{width:0}to{width:100%}}
@keyframes splashOut{
    0%{opacity:1;transform:scale(1);}
    50%{opacity:1;transform:scale(1.02);}
    100%{opacity:0;transform:scale(0.95);pointer-events:none;}
}
</style></head><body>
<div class="splash">
<canvas id="pcanvas"></canvas>
<div class="content">
<div class="logo-wrap">
<div class="orbit orbit-1"></div>
<div class="orbit orbit-2"></div>
<div class="orbit orbit-3"></div>
<div class="logo">🛡️</div>
</div>
<div class="title">ReleaseGuardian</div>
<div class="subtitle">Change-Risk & Rollback Copilot</div>
<div class="line"></div>
<div class="tagline">
<h2>Don't let risky deploys go live without context.</h2>
<p>Analyze code changes, tickets, incident history & operational signals. Predict risk. Map blast radius. Generate rollback plans.</p>
</div>
</div>
<div class="loader"><div class="loader-fill"></div></div>
<div class="loader-text">INITIALIZING</div>
</div>

<script>
// Particle background
const c=document.getElementById('pcanvas'),x=c.getContext('2d');
let w=c.width=innerWidth,h=c.height=innerHeight;
const pts=[];
for(let i=0;i<40;i++){
    pts.push({
        x:Math.random()*w, y:Math.random()*h,
        r:Math.random()*1.5+0.5,
        dx:(Math.random()-0.5)*0.3,
        dy:(Math.random()-0.5)*0.3,
        o:Math.random()*0.15+0.03
    });
}
function draw(){
    x.clearRect(0,0,w,h);
    pts.forEach(p=>{
        p.x+=p.dx; p.y+=p.dy;
        if(p.x<0||p.x>w)p.dx*=-1;
        if(p.y<0||p.y>h)p.dy*=-1;
        x.beginPath();x.arc(p.x,p.y,p.r,0,Math.PI*2);
        x.fillStyle=`rgba(124,92,252,${p.o})`;x.fill();
    });
    for(let i=0;i<pts.length;i++){
        for(let j=i+1;j<pts.length;j++){
            const d=Math.hypot(pts[i].x-pts[j].x,pts[i].y-pts[j].y);
            if(d<100){
                x.beginPath();x.moveTo(pts[i].x,pts[i].y);x.lineTo(pts[j].x,pts[j].y);
                x.strokeStyle=`rgba(124,92,252,${0.04*(1-d/100)})`;
                x.lineWidth=0.5;x.stroke();
            }
        }
    }
    requestAnimationFrame(draw);
}
draw();
</script>
</body></html>""", height=650)

    import time
    time.sleep(5)
    st.session_state.splash_done = True
    st.rerun()

# ──────────────────────────────────────
# HEADER — animated entry after splash
# ──────────────────────────────────────
st.markdown("""
<style>
@keyframes headerDrop{from{opacity:0;transform:translateY(-20px)}to{opacity:1;transform:translateY(0)}}
@keyframes revealUp{from{opacity:0;transform:translateY(30px)}to{opacity:1;transform:translateY(0)}}
@keyframes revealScale{from{opacity:0;transform:scale(0.95) translateY(20px)}to{opacity:1;transform:scale(1) translateY(0)}}
@keyframes shimmer{0%{background-position:-200% 0}100%{background-position:200% 0}}
@keyframes cardFloat{0%,100%{transform:translateY(0)}50%{transform:translateY(-3px)}}
@keyframes glowPulse{0%,100%{box-shadow:0 4px 12px rgba(124,92,252,0.2)}50%{box-shadow:0 4px 24px rgba(124,92,252,0.35)}}
@keyframes gradientShift{0%{background-position:0% 50%}50%{background-position:100% 50%}100%{background-position:0% 50%}}
@keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
@keyframes resultFade{from{opacity:0;transform:translateY(16px)}to{opacity:1;transform:translateY(0)}}
@keyframes successPulse{0%,100%{box-shadow:0 0 20px rgba(62,207,142,0.08)}50%{box-shadow:0 0 40px rgba(62,207,142,0.18)}}
</style>

<div style="display:flex;justify-content:space-between;align-items:center;padding:14px 20px;background:#1a1a24;border:1px solid #2a2a3a;border-radius:14px;margin-bottom:24px;animation:headerDrop 0.6s 0.1s cubic-bezier(.16,1,.3,1) both;">
<div style="display:flex;align-items:center;gap:12px;">
<div style="width:38px;height:38px;background:linear-gradient(135deg,#7c5cfc,#6246ea);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;animation:glowPulse 3s ease-in-out infinite;">🛡️</div>
<div>
<div style="font-size:17px;font-weight:700;color:#ececf1;letter-spacing:-0.3px;">ReleaseGuardian</div>
<div style="font-size:11px;color:#5a5a6e;font-weight:500;">Change-Risk & Rollback Copilot</div>
</div></div>
<div style="display:flex;gap:6px;">
<span style="font-size:11px;padding:5px 11px;border-radius:7px;background:rgba(124,92,252,0.12);color:#9d85ff;font-weight:600;border:1px solid rgba(124,92,252,0.2);">⚡ 3-Agent Pipeline</span>
<span style="font-size:11px;padding:5px 11px;border-radius:7px;background:rgba(74,164,245,0.1);color:#4aa4f5;font-weight:600;border:1px solid rgba(74,164,245,0.15);">✦ Gemini 2.5</span>
</div></div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────
# INPUT PAGE
# ──────────────────────────────────────
if st.session_state.results is None and st.session_state.agent_phase is None:
    scenarios = get_demo_scenarios()

    # HERO — enhanced with gradient text, floating orbs, stat counters
    st.markdown("""
    <div style="text-align:center;padding:52px 20px 44px;position:relative;overflow:hidden;
    background:linear-gradient(135deg,#14142a 0%,#181828 50%,#14142a 100%);
    border:1px solid #2a2a3a;border-radius:24px;margin-bottom:28px;
    animation:revealScale 0.7s 0.3s cubic-bezier(.16,1,.3,1) both;">

    <div style="position:absolute;top:-60px;left:-60px;width:300px;height:300px;background:radial-gradient(circle,rgba(124,92,252,0.08),transparent 60%);pointer-events:none;animation:float 8s ease-in-out infinite;"></div>
    <div style="position:absolute;top:20px;right:-40px;width:250px;height:250px;background:radial-gradient(circle,rgba(74,164,245,0.06),transparent 60%);pointer-events:none;animation:float 10s 2s ease-in-out infinite;"></div>
    <div style="position:absolute;bottom:-40px;left:40%;width:200px;height:200px;background:radial-gradient(circle,rgba(62,207,142,0.04),transparent 60%);pointer-events:none;animation:float 12s 4s ease-in-out infinite;"></div>
    <div style="position:absolute;inset:0;background-image:radial-gradient(rgba(124,92,252,0.02) 1px,transparent 1px);background-size:28px 28px;pointer-events:none;"></div>

    <div style="position:relative;z-index:1;">
    <div style="width:68px;height:68px;background:linear-gradient(135deg,#7c5cfc,#6246ea);border-radius:20px;display:flex;align-items:center;justify-content:center;font-size:32px;margin:0 auto 22px;box-shadow:0 10px 35px rgba(124,92,252,0.3);animation:glowPulse 3s ease-in-out infinite;">🛡️</div>
    <h1 style="font-size:36px;font-weight:700;color:#ececf1;letter-spacing:-0.8px;margin:0 0 14px;line-height:1.25;">Don't let risky deploys go live<br>without <span style='background:linear-gradient(90deg,#7c5cfc,#4aa4f5,#3ecf8e);background-size:200% auto;-webkit-background-clip:text;-webkit-text-fill-color:transparent;animation:gradientShift 4s linear infinite;'>context</span>.</h1>
    <p style="font-size:15px;color:#8e8ea0;max-width:500px;margin:0 auto 28px;line-height:1.7;">Analyze code changes, tickets, incident history & operational signals before deployment. Predict risk, map blast radius, generate rollback plans.</p>

    <div style="display:flex;justify-content:center;gap:36px;">
    <div style="text-align:center;"><div style="font-family:'JetBrains Mono',monospace;font-size:24px;font-weight:700;color:#7c5cfc;">3</div><div style="font-size:11px;color:#5a5a6e;">AI Agents</div></div>
    <div style="text-align:center;"><div style="font-family:'JetBrains Mono',monospace;font-size:24px;font-weight:700;color:#4aa4f5;">6</div><div style="font-size:11px;color:#5a5a6e;">Risk Dimensions</div></div>
    <div style="text-align:center;"><div style="font-family:'JetBrains Mono',monospace;font-size:24px;font-weight:700;color:#3ecf8e;">&lt;60s</div><div style="font-size:11px;color:#5a5a6e;">Analysis Time</div></div>
    <div style="text-align:center;"><div style="font-family:'JetBrains Mono',monospace;font-size:24px;font-weight:700;color:#f5a623;">5</div><div style="font-size:11px;color:#5a5a6e;">Output Types</div></div>
    </div></div></div>
    """, unsafe_allow_html=True)

    # HOW IT WORKS — colored top borders, step labels
    st.markdown("""
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:28px;">
    <div style="padding:24px 18px;background:#1a1a24;border:1px solid #2a2a3a;border-radius:16px;text-align:center;transition:all .3s;cursor:default;position:relative;overflow:hidden;animation:revealUp 0.5s 0.5s cubic-bezier(.16,1,.3,1) both;"
    onmouseover="this.style.borderColor='rgba(124,92,252,0.25)';this.style.transform='translateY(-4px)';this.style.boxShadow='0 8px 30px rgba(124,92,252,0.08)'"
    onmouseout="this.style.borderColor='#2a2a3a';this.style.transform='none';this.style.boxShadow='none'">
    <div style="position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#7c5cfc,#9d85ff);"></div>
    <div style="width:44px;height:44px;background:rgba(124,92,252,0.08);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:20px;margin:0 auto 12px;border:1px solid rgba(124,92,252,0.12);">📄</div>
    <div style="font-size:10px;font-weight:600;color:#7c5cfc;letter-spacing:1px;margin-bottom:4px;">STEP 1</div>
    <div style="font-size:15px;font-weight:600;color:#ececf1;margin-bottom:5px;">Select or Upload</div>
    <div style="font-size:12px;color:#5a5a6e;line-height:1.5;">Pick a demo scenario or upload your own PR diff & artifacts</div></div>

    <div style="padding:24px 18px;background:#1a1a24;border:1px solid #2a2a3a;border-radius:16px;text-align:center;transition:all .3s;cursor:default;position:relative;overflow:hidden;animation:revealUp 0.5s 0.65s cubic-bezier(.16,1,.3,1) both;"
    onmouseover="this.style.borderColor='rgba(74,164,245,0.25)';this.style.transform='translateY(-4px)';this.style.boxShadow='0 8px 30px rgba(74,164,245,0.08)'"
    onmouseout="this.style.borderColor='#2a2a3a';this.style.transform='none';this.style.boxShadow='none'">
    <div style="position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#4aa4f5,#6dc0ff);"></div>
    <div style="width:44px;height:44px;background:rgba(74,164,245,0.08);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:20px;margin:0 auto 12px;border:1px solid rgba(74,164,245,0.12);">🤖</div>
    <div style="font-size:10px;font-weight:600;color:#4aa4f5;letter-spacing:1px;margin-bottom:4px;">STEP 2</div>
    <div style="font-size:15px;font-weight:600;color:#ececf1;margin-bottom:5px;">AI Analyzes</div>
    <div style="font-size:12px;color:#5a5a6e;line-height:1.5;">3 specialized agents evaluate risk, map blast radius & plan recovery</div></div>

    <div style="padding:24px 18px;background:#1a1a24;border:1px solid #2a2a3a;border-radius:16px;text-align:center;transition:all .3s;cursor:default;position:relative;overflow:hidden;animation:revealUp 0.5s 0.8s cubic-bezier(.16,1,.3,1) both;"
    onmouseover="this.style.borderColor='rgba(62,207,142,0.25)';this.style.transform='translateY(-4px)';this.style.boxShadow='0 8px 30px rgba(62,207,142,0.08)'"
    onmouseout="this.style.borderColor='#2a2a3a';this.style.transform='none';this.style.boxShadow='none'">
    <div style="position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,#3ecf8e,#5ee8a8);"></div>
    <div style="width:44px;height:44px;background:rgba(62,207,142,0.08);border-radius:12px;display:flex;align-items:center;justify-content:center;font-size:20px;margin:0 auto 12px;border:1px solid rgba(62,207,142,0.12);">📊</div>
    <div style="font-size:10px;font-weight:600;color:#3ecf8e;letter-spacing:1px;margin-bottom:4px;">STEP 3</div>
    <div style="font-size:15px;font-weight:600;color:#ececf1;margin-bottom:5px;">Review & Act</div>
    <div style="font-size:12px;color:#5a5a6e;line-height:1.5;">Get risk scores, rollback plans, Slack messages & handoff notes</div></div>
    </div>
    """, unsafe_allow_html=True)

    # SCENARIO PREVIEW CARDS + dropdown
    st.markdown("""
    <div style="animation:revealUp 0.5s 0.95s cubic-bezier(.16,1,.3,1) both;">
    <p style="font-size:11px;font-weight:600;color:#7c5cfc;letter-spacing:1.5px;margin-bottom:12px;">⚡ TRY A DEMO SCENARIO</p>
    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:14px;">
    <div style="padding:14px 16px;background:#1a1a24;border:1px solid #2a2a3a;border-radius:12px;transition:all .3s;"
    onmouseover="this.style.borderColor='rgba(239,68,68,0.3)';this.style.transform='translateY(-2px)'" onmouseout="this.style.borderColor='#2a2a3a';this.style.transform='none'">
    <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;"><div style="width:7px;height:7px;border-radius:50%;background:#ef4444;box-shadow:0 0 6px rgba(239,68,68,0.4);"></div><span style="font-size:10px;font-weight:700;color:#ef4444;letter-spacing:0.5px;">HIGH RISK</span></div>
    <div style="font-size:13px;font-weight:600;color:#ececf1;">Payment Timeout</div>
    <div style="font-size:11px;color:#5a5a6e;margin-top:3px;">Matches past outage pattern</div></div>
    <div style="padding:14px 16px;background:#1a1a24;border:1px solid #2a2a3a;border-radius:12px;transition:all .3s;"
    onmouseover="this.style.borderColor='rgba(234,179,8,0.3)';this.style.transform='translateY(-2px)'" onmouseout="this.style.borderColor='#2a2a3a';this.style.transform='none'">
    <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;"><div style="width:7px;height:7px;border-radius:50%;background:#eab308;box-shadow:0 0 6px rgba(234,179,8,0.4);"></div><span style="font-size:10px;font-weight:700;color:#eab308;letter-spacing:0.5px;">MEDIUM RISK</span></div>
    <div style="font-size:13px;font-weight:600;color:#ececf1;">New API Field</div>
    <div style="font-size:11px;color:#5a5a6e;margin-top:3px;">New shipping dependency</div></div>
    <div style="padding:14px 16px;background:#1a1a24;border:1px solid #2a2a3a;border-radius:12px;transition:all .3s;"
    onmouseover="this.style.borderColor='rgba(62,207,142,0.3)';this.style.transform='translateY(-2px)'" onmouseout="this.style.borderColor='#2a2a3a';this.style.transform='none'">
    <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px;"><div style="width:7px;height:7px;border-radius:50%;background:#3ecf8e;box-shadow:0 0 6px rgba(62,207,142,0.4);"></div><span style="font-size:10px;font-weight:700;color:#3ecf8e;letter-spacing:0.5px;">LOW RISK</span></div>
    <div style="font-size:13px;font-weight:600;color:#ececf1;">Copy Update</div>
    <div style="font-size:11px;color:#5a5a6e;margin-top:3px;">Email template change only</div></div>
    </div></div>
    """, unsafe_allow_html=True)

    scenario_choice = st.selectbox("scenario", ["-- Choose a demo scenario --","High Risk: Payment Timeout Change","Medium Risk: New API Field","Low Risk: Copy Update"], label_visibility="collapsed")

    # DIVIDER
    st.markdown("""
    <div style="display:flex;align-items:center;gap:14px;margin:20px 0 16px;">
    <div style="flex:1;height:1px;background:linear-gradient(90deg,transparent,#2a2a3a,transparent);"></div>
    <div style="padding:5px 14px;background:#1a1a24;border:1px solid #2a2a3a;border-radius:8px;">
    <span style="font-size:10px;color:#5a5a6e;font-weight:600;letter-spacing:1.5px;">OR UPLOAD YOUR OWN</span></div>
    <div style="flex:1;height:1px;background:linear-gradient(90deg,transparent,#2a2a3a,transparent);"></div>
    </div>
    """, unsafe_allow_html=True)

    # UPLOADS
    c1, c2 = st.columns(2)
    with c1:
        pr_upload = st.file_uploader("📄 PR Diff / Code Change *", type=["txt","md","diff"], key="pr_up")
        runbook_upload = st.file_uploader("📋 Service Runbook (optional)", type=["txt","md","json"], key="rb_up")
    with c2:
        jira_upload = st.file_uploader("🎫 Jira Ticket / Release Note *", type=["txt","md","json"], key="ji_up")
        incident_uploads = st.file_uploader("🚨 Past Incidents (optional)", type=["txt","md","json"], accept_multiple_files=True, key="inc_up")

    st.markdown("")
    if st.button("🔍  Analyze Release", use_container_width=True):
        use_demo = scenario_choice != "-- Choose a demo scenario --"
        use_upload = pr_upload is not None and jira_upload is not None
        if not use_demo and not use_upload:
            st.error("Please select a demo scenario or upload at least a PR diff and Jira ticket.")
        else:
            if use_demo:
                sd = scenarios[scenario_choice]
                st.session_state._inp = {"pr_diff":sd["pr_diff"],"jira_ticket":sd["jira_ticket"],"runbook":sd.get("runbook"),"incidents":sd.get("incidents",[]),"screenshot_desc":sd.get("screenshot_description")}
            else:
                st.session_state._inp = {"pr_diff":pr_upload.read().decode("utf-8"),"jira_ticket":jira_upload.read().decode("utf-8"),"runbook":runbook_upload.read().decode("utf-8") if runbook_upload else None,"incidents":[f.read().decode("utf-8") for f in incident_uploads] if incident_uploads else [],"screenshot_desc":None}
            st.session_state.agent_phase = "agent1"
            st.rerun()

    # FOOTER
    st.markdown("""
    <div style="text-align:center;padding:24px 0 8px;margin-top:16px;border-top:1px solid #1a1a24;">
    <p style="font-size:11px;color:#3a3a50;">Built with Google Gemini 2.5 Flash · Multi-Agent Architecture · Python + Streamlit</p>
    </div>
    """, unsafe_allow_html=True)
# ──────────────────────────────────────
elif st.session_state.agent_phase is not None:
    inp = st.session_state._inp
    phase = st.session_state.agent_phase

    def render_agent(num, color, emoji, title, subtitle, done_tasks, active_tasks, pending_tasks, pct):
        badges = "".join(f'<span style="display:inline-block;font-size:11px;padding:4px 10px;border-radius:6px;background:rgba(62,207,142,0.1);color:#3ecf8e;font-weight:600;margin-right:4px;border:1px solid rgba(62,207,142,0.15);">✓ Agent {i}</span>' for i in range(1,num))
        task_html = ""
        for t in done_tasks:
            task_html += f'<div style="display:flex;align-items:center;gap:10px;padding:7px 0;"><div style="width:22px;height:22px;border-radius:6px;background:rgba(62,207,142,0.1);display:flex;align-items:center;justify-content:center;flex-shrink:0;"><span style="font-size:12px;color:#3ecf8e;">✓</span></div><span style="font-size:13px;color:#3ecf8e;font-weight:500;">{t}</span></div>'
        for t in active_tasks:
            task_html += f'<div style="display:flex;align-items:center;gap:10px;padding:7px 0;"><div style="width:22px;height:22px;border-radius:6px;background:rgba(124,92,252,0.1);display:flex;align-items:center;justify-content:center;flex-shrink:0;"><div style="width:8px;height:8px;border-radius:50%;background:{color};animation:pulse 1.2s infinite;"></div></div><span style="font-size:13px;color:#ececf1;font-weight:600;">{t}</span></div>'
        for t in pending_tasks:
            task_html += f'<div style="display:flex;align-items:center;gap:10px;padding:7px 0;"><div style="width:22px;height:22px;border-radius:6px;background:#222230;flex-shrink:0;"></div><span style="font-size:13px;color:#3a3a50;font-weight:400;">{t}</span></div>'

        st.markdown(f"""
<style>@keyframes pulse{{0%,100%{{opacity:1;transform:scale(1)}}50%{{opacity:.3;transform:scale(.7)}}}}@keyframes spin{{to{{transform:rotate(360deg)}}}}@keyframes grow{{from{{width:0}}to{{width:{pct}%}}}}</style>
<div style="min-height:520px;display:flex;align-items:center;justify-content:center;">
<div style="text-align:center;max-width:440px;width:100%;padding:36px 28px;background:#1a1a24;border:1px solid #2a2a3a;border-radius:20px;box-shadow:0 12px 48px rgba(0,0,0,0.3);">
<div style="margin-bottom:8px;">{badges}</div>
<div style="position:relative;width:88px;height:88px;margin:14px auto 22px;">
<div style="position:absolute;inset:0;border-radius:50%;border:3px solid #222230;"></div>
<div style="position:absolute;inset:0;border-radius:50%;border:3px solid transparent;border-top-color:{color};animation:spin 1s linear infinite;"></div>
<div style="position:absolute;inset:0;display:flex;align-items:center;justify-content:center;font-size:30px;">{emoji}</div>
</div>
<div style="font-size:10px;font-weight:600;color:{color};letter-spacing:2px;margin-bottom:4px;">AGENT {num} OF 3</div>
<div style="font-size:20px;font-weight:700;color:#ececf1;margin-bottom:4px;letter-spacing:-0.3px;">{title}</div>
<div style="font-size:13px;color:#5a5a6e;margin-bottom:20px;line-height:1.5;">{subtitle}</div>
<div style="text-align:left;padding:0 8px;margin-bottom:20px;">{task_html}</div>
<div style="height:5px;background:#222230;border-radius:3px;overflow:hidden;">
<div style="height:100%;background:linear-gradient(90deg,{color},{color}99);border-radius:3px;animation:grow 1.5s ease-out forwards;"></div>
</div>
<div style="font-family:'JetBrains Mono',monospace;font-size:11px;color:#5a5a6e;margin-top:8px;">{pct}% complete</div>
</div></div>
""", unsafe_allow_html=True)

    if phase == "agent1":
        render_agent(1,"#7c5cfc","🔍","Context Builder","Reading artifacts and extracting structured context...",[],["Parsing PR diff & code changes","Extracting Jira ticket context"],["Mapping service dependencies","Scanning for risky patterns","Matching past incidents"],15)
        pf = build_release_context(pr_diff=inp["pr_diff"],jira_ticket=inp["jira_ticket"],runbook=inp.get("runbook"),incidents=inp.get("incidents") or None,screenshot_description=inp.get("screenshot_desc"))
        print(f"\n[DEBUG AGENT 1] Type: {type(pf)}, Value: {str(pf)[:300]}")
        if pf is None: pf = {}
        st.session_state._pf = pf; st.session_state.agent_phase = "agent2"; st.rerun()

    elif phase == "agent2":
        render_agent(2,"#f5a623","⚠️","Risk Analyst","Evaluating risk dimensions and mapping blast radius...",["Context built successfully"],["Scoring code change scope","Evaluating dependency risk"],["Matching historical patterns","Mapping blast radius","Ranking failure modes"],48)
        raw = f"PR:\n{inp['pr_diff']}\n\nJIRA:\n{inp['jira_ticket']}"
        if inp.get("runbook"): raw += f"\n\nRUNBOOK:\n{inp['runbook']}"
        if inp.get("incidents"):
            for i,inc in enumerate(inp["incidents"],1): raw += f"\n\nINCIDENT {i}:\n{inc}"
        if inp.get("screenshot_desc"): raw += f"\n\nDASH:\n{inp['screenshot_desc']}"
        rk = analyze_risk(release_profile=st.session_state._pf,raw_artifacts=raw)
        print(f"\n[DEBUG AGENT 2] Type: {type(rk)}, Value: {str(rk)[:300]}")
        if rk is None: rk = {}
        st.session_state._rk = rk; st.session_state.agent_phase = "agent3"; st.rerun()

    elif phase == "agent3":
        render_agent(3,"#4aa4f5","🔄","Recovery Planner","Generating rollback plan and stakeholder communications...",["Context built","Risk analyzed"],["Writing rollback procedures","Building pre-deploy checklist"],["Generating Slack message","Creating handoff note"],78)
        plan = generate_recovery_plan(release_profile=st.session_state._pf,risk_assessment=st.session_state._rk,runbook=inp.get("runbook"))
        print(f"\n[DEBUG AGENT 3] Type: {type(plan)}, Value: {str(plan)[:300]}")
        if plan is None: plan = {}
        st.session_state.results = {"release_profile":st.session_state._pf or {},"risk_assessment":st.session_state._rk or {},"recovery_plan":plan}
        st.session_state.agent_phase = None; st.session_state._inp = None; st.session_state._pf = None; st.session_state._rk = None; st.rerun()


# ──────────────────────────────────────
# RESULTS PAGE
# ──────────────────────────────────────
else:
    res = st.session_state.results
    pf = (res.get("release_profile") if res else {}) or {}
    rk = (res.get("risk_assessment") if res else {}) or {}
    pl = (res.get("recovery_plan") if res else {}) or {}
    
    print(f"\n[DEBUG RESULTS] rk type={type(rk)}, keys={list(rk.keys()) if isinstance(rk,dict) else 'NOT A DICT'}")
    print(f"[DEBUG RESULTS] risk_score={rk.get('risk_score','MISSING')}, risk_score_numeric={rk.get('risk_score_numeric','MISSING')}")

    # Success banner
    st.markdown("""
    <div style="display:flex;align-items:center;justify-content:space-between;padding:14px 20px;
    background:linear-gradient(135deg,rgba(62,207,142,0.06),rgba(74,164,245,0.04));
    border:1px solid rgba(62,207,142,0.15);border-radius:14px;margin-bottom:16px;
    animation:resultFade 0.5s cubic-bezier(.16,1,.3,1), successPulse 3s 0.5s ease-in-out infinite;">
    <div style="display:flex;align-items:center;gap:12px;">
    <div style="width:36px;height:36px;background:rgba(62,207,142,0.1);border-radius:10px;display:flex;align-items:center;justify-content:center;font-size:18px;border:1px solid rgba(62,207,142,0.2);">✅</div>
    <div><div style="font-size:14px;font-weight:600;color:#3ecf8e;">Analysis Complete</div>
    <div style="font-size:12px;color:#5a5a6e;">All 3 agents finished · Results ready</div></div></div>
    <div style="display:flex;gap:6px;">
    <span style="font-size:10px;padding:4px 10px;border-radius:6px;background:rgba(62,207,142,0.08);color:#3ecf8e;font-weight:600;border:1px solid rgba(62,207,142,0.12);">✓ Context</span>
    <span style="font-size:10px;padding:4px 10px;border-radius:6px;background:rgba(62,207,142,0.08);color:#3ecf8e;font-weight:600;border:1px solid rgba(62,207,142,0.12);">✓ Risk</span>
    <span style="font-size:10px;padding:4px 10px;border-radius:6px;background:rgba(62,207,142,0.08);color:#3ecf8e;font-weight:600;border:1px solid rgba(62,207,142,0.12);">✓ Plan</span>
    </div></div>
    """, unsafe_allow_html=True)

    if st.button("← New Analysis"):
        st.session_state.results = None
        st.session_state.agent_phase = None
        st.session_state._inp = None
        st.session_state._pf = None
        st.session_state._rk = None
        st.rerun()

    # === BULLETPROOF DATA EXTRACTION ===
    # Gemini returns inconsistent JSON — protect every single field
    def safe_str(val, default=""): 
        if val is None: return default
        return str(val)
    def safe_list(val):
        if isinstance(val, list): return val
        return []
    def safe_dict(val):
        if isinstance(val, dict): return val
        return {}

    rs = safe_str(rk.get("risk_score"), "UNKNOWN").upper()
    try: rn = int(float(rk.get("risk_score_numeric",0) or 0))
    except: rn = 50
    try: conf = float(rk.get("confidence",0) or 0)
    except: conf = 0

    br = safe_dict(rk.get("blast_radius"))
    sa = safe_list(br.get("services_affected"))
    uf = safe_list(br.get("user_flows_affected"))
    fms = safe_list(rk.get("failure_modes"))
    dims = safe_dict(rk.get("risk_dimensions"))
    ms_l = safe_list(rk.get("missing_safeguards"))
    si_l = safe_list(pf.get("similar_incidents"))
    rp_l = safe_list(pf.get("risky_patterns"))
    mi_l = safe_list(pf.get("missing_items"))
    cl_l = safe_list(pl.get("pre_deploy_checklist"))
    rb_o = safe_dict(pl.get("rollback_plan"))
    mo_o = safe_dict(pl.get("monitoring_plan"))
    summ = safe_str(rk.get("summary"), "No summary available.")

    rc_map = {"CRITICAL":"#ef4444","HIGH":"#f97316","MEDIUM":"#eab308","LOW":"#3ecf8e","UNKNOWN":"#5a5a6e"}
    sc_map = {"LOW":25,"MEDIUM":50,"HIGH":75,"CRITICAL":100}
    rc = rc_map.get(rs,"#5a5a6e")

    # === METRICS — staggered animation ===
    st.markdown(f"""
    <div style="display:grid;grid-template-columns:1.4fr repeat(4,1fr);gap:10px;margin-bottom:20px;">
    <div style="background:#1a1a24;border:2px solid {rc};border-radius:14px;padding:18px;text-align:center;animation:resultFade 0.4s 0.1s both;">
    <div style="font-size:24px;font-weight:700;color:{rc};letter-spacing:1px;">{rs}</div>
    <div style="font-size:10px;color:#5a5a6e;margin-top:4px;font-weight:600;letter-spacing:1px;">RISK LEVEL</div></div>
    <div style="background:#1a1a24;border:1px solid #2a2a3a;border-radius:14px;padding:18px;text-align:center;animation:resultFade 0.4s 0.2s both;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:26px;font-weight:700;color:#ececf1;">{rn}<span style="font-size:13px;color:#5a5a6e;">/100</span></div>
    <div style="font-size:10px;color:#5a5a6e;margin-top:4px;font-weight:600;letter-spacing:1px;">SCORE</div></div>
    <div style="background:#1a1a24;border:1px solid #2a2a3a;border-radius:14px;padding:18px;text-align:center;animation:resultFade 0.4s 0.3s both;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:26px;font-weight:700;color:#ececf1;">{len(sa)}</div>
    <div style="font-size:10px;color:#5a5a6e;margin-top:4px;font-weight:600;letter-spacing:1px;">SERVICES</div></div>
    <div style="background:#1a1a24;border:1px solid #2a2a3a;border-radius:14px;padding:18px;text-align:center;animation:resultFade 0.4s 0.4s both;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:26px;font-weight:700;color:#ececf1;">{int(conf*100)}<span style="font-size:13px;color:#5a5a6e;">%</span></div>
    <div style="font-size:10px;color:#5a5a6e;margin-top:4px;font-weight:600;letter-spacing:1px;">CONFIDENCE</div></div>
    <div style="background:#1a1a24;border:1px solid #2a2a3a;border-radius:14px;padding:18px;text-align:center;animation:resultFade 0.4s 0.5s both;">
    <div style="font-family:'JetBrains Mono',monospace;font-size:26px;font-weight:700;color:#ececf1;">{len(fms)}</div>
    <div style="font-size:10px;color:#5a5a6e;margin-top:4px;font-weight:600;letter-spacing:1px;">FAILURES</div></div>
    </div>
    """, unsafe_allow_html=True)

    # Release info
    st.markdown(f"""
    <div style="background:#1a1a24;border:1px solid #2a2a3a;border-radius:12px;padding:14px 18px;margin-bottom:16px;">
    <span style="font-family:'JetBrains Mono',monospace;font-size:13px;color:#7c5cfc;font-weight:600;">{esc(pf.get("release_id","N/A"))}</span>
    <span style="font-size:13px;color:#8e8ea0;margin-left:8px;">{esc(pf.get("summary",""))}</span>
    </div>
    """, unsafe_allow_html=True)

    # TABS
    tab1,tab2,tab3,tab4,tab5 = st.tabs(["📊 Overview","💥 Blast Radius","⚠️ Failures","🔄 Recovery","📨 Comms"])

    # ─── TAB 1 ───
    with tab1:
      try:
        st.markdown(f"""
        <div style="background:#1a1a24;border:1px solid #2a2a3a;border-radius:14px;padding:22px;margin-bottom:14px;">
        <div style="font-size:14px;font-weight:700;color:#ececf1;margin-bottom:10px;">📝 Assessment Summary</div>
        <p style="font-size:14px;color:#c0c0d0;line-height:1.8;">{esc(summ)}</p>
        </div>
        """, unsafe_allow_html=True)

        dim_html = ""
        for k,v in dims.items():
            if not isinstance(v,dict): continue
            label = k.replace("_"," ").title()
            score = safe_str(v.get("score"), "LOW").upper()
            pct = sc_map.get(score,25)
            dcolor = rc_map.get(score,"#5a5a6e")
            expl = safe_str(v.get("explanation"))
            dim_html += f'''<div style="padding:10px 0;border-bottom:1px solid #222230;">
            <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
            <span style="width:140px;font-size:13px;color:#8e8ea0;font-weight:500;flex-shrink:0;">{label}</span>
            <div style="flex:1;height:6px;background:#222230;border-radius:3px;overflow:hidden;">
            <div style="width:{pct}%;height:100%;background:{dcolor};border-radius:3px;"></div></div>
            <span style="width:60px;text-align:right;font-family:JetBrains Mono;font-size:11px;font-weight:600;color:{dcolor};flex-shrink:0;">{score}</span></div>
            <div style="padding-left:150px;font-size:12px;color:#5a5a6e;line-height:1.4;">{esc(expl)}</div></div>'''

        st.markdown(f"""
        <div style="background:#1a1a24;border:1px solid #2a2a3a;border-radius:14px;padding:22px;margin-bottom:14px;">
        <div style="font-size:14px;font-weight:700;color:#ececf1;margin-bottom:14px;">📏 Risk Dimensions</div>
        {dim_html if dim_html else '<p style="font-size:13px;color:#5a5a6e;">No dimension data.</p>'}
        </div>
        """, unsafe_allow_html=True)

        if rp_l:
            tags = "".join(f'<span style="display:inline-block;padding:5px 12px;margin:3px;border-radius:7px;font-size:12px;font-weight:500;background:rgba(245,166,35,0.1);border:1px solid rgba(245,166,35,0.2);color:#f5a623;">{esc(p)}</span>' for p in rp_l if isinstance(p, str))
            if tags:
                st.markdown(f'<div style="background:#1a1a24;border:1px solid #2a2a3a;border-radius:14px;padding:22px;margin-bottom:14px;"><div style="font-size:14px;font-weight:700;color:#ececf1;margin-bottom:12px;">🚩 Risky Patterns</div>{tags}</div>', unsafe_allow_html=True)

        if mi_l:
            items = "".join(f'<div style="display:flex;align-items:center;gap:8px;padding:8px 12px;margin-bottom:4px;background:rgba(245,166,35,0.06);border:1px solid rgba(245,166,35,0.1);border-radius:8px;font-size:12px;color:#f5a623;">⚠️ {esc(m)}</div>' for m in mi_l if isinstance(m, str))
            if items:
                st.markdown(f'<div style="background:#1a1a24;border:1px solid #2a2a3a;border-radius:14px;padding:22px;"><div style="font-size:14px;font-weight:700;color:#ececf1;margin-bottom:12px;">❌ Missing Items</div>{items}</div>', unsafe_allow_html=True)
      except Exception as e:
        st.error(f"Error rendering Overview tab: {e}")

    # ─── TAB 2 ───
    with tab2:
      try:
        base_svcs = ["auth-service","checkout-service","notification-service","payment-gateway","redis-cache","inventory-service"]
        sa_clean = [s for s in sa if isinstance(s, str)]
        all_svc = sorted(set(sa_clean + base_svcs))
        svc_cards = ""
        for sv in all_svc:
            hit = any(s.lower()==sv.lower() for s in sa_clean)
            bg = "rgba(239,68,68,0.08)" if hit else "#222230"
            bd = "1px solid rgba(239,68,68,0.3)" if hit else "1px solid #2a2a3a"
            tc = "#ef4444" if hit else "#5a5a6e"
            icon = "🔴" if hit else "⚪"
            name = sv.replace("-service","").replace("-"," ").title()
            svc_cards += f'<div style="padding:14px;background:{bg};border:{bd};border-radius:12px;text-align:center;min-width:90px;"><div style="font-size:18px;margin-bottom:4px;">{icon}</div><div style="font-size:11px;font-weight:600;color:{tc};">{name}</div></div>'
        st.markdown(f'<div style="background:#1a1a24;border:1px solid #2a2a3a;border-radius:14px;padding:22px;margin-bottom:14px;"><div style="font-size:14px;font-weight:700;color:#ececf1;margin-bottom:14px;">🕸 Service Map</div><div style="display:flex;flex-wrap:wrap;gap:8px;justify-content:center;">{svc_cards}</div></div>', unsafe_allow_html=True)

        c1,c2 = st.columns(2)
        with c1:
            user_impact = esc(br.get("estimated_user_impact","Unknown"))
            sla_risk = esc(br.get("sla_risk","None"))
            uf_html = "".join(f'<div style="padding:6px 10px;margin-top:4px;background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.12);border-radius:8px;font-size:12px;color:#ef4444;">⊘ {esc(f)}</div>' for f in uf if isinstance(f, str))
            st.markdown(f"""<div style="background:#1a1a24;border:1px solid #2a2a3a;border-radius:14px;padding:22px;">
            <div style="font-size:14px;font-weight:700;color:#ececf1;margin-bottom:12px;">💥 Impact</div>
            <p style="font-size:13px;color:#c0c0d0;margin-bottom:8px;"><strong style="color:#ececf1;">User Impact:</strong> {user_impact}</p>
            <p style="font-size:13px;color:#c0c0d0;margin-bottom:12px;"><strong style="color:#ececf1;">SLA Risk:</strong> {sla_risk}</p>
            {uf_html}
            </div>""", unsafe_allow_html=True)
        with c2:
            si_html = ""
            for inc in si_l:
                if not isinstance(inc,dict): continue
                si_html += f'<div style="padding:10px;margin-bottom:6px;background:rgba(245,166,35,0.06);border:1px solid rgba(245,166,35,0.1);border-radius:10px;"><div style="font-family:JetBrains Mono;font-size:11px;color:#f5a623;font-weight:600;">{esc(inc.get("incident_id",""))}</div><div style="font-size:12px;color:#c0c0d0;margin-top:4px;line-height:1.5;">{esc(inc.get("similarity",""))}</div></div>'
            st.markdown(f"""<div style="background:#1a1a24;border:1px solid #2a2a3a;border-radius:14px;padding:22px;">
            <div style="font-size:14px;font-weight:700;color:#ececf1;margin-bottom:12px;">📜 Past Incidents</div>
            {si_html if si_html else '<p style="font-size:13px;color:#5a5a6e;">No similar incidents found.</p>'}
            </div>""", unsafe_allow_html=True)
      except Exception as e:
        st.error(f"Error rendering Blast Radius tab: {e}")

    # ─── TAB 3 ───
    with tab3:
      try:
        if fms:
            for i,fm in enumerate(fms):
                if not isinstance(fm,dict): continue
                sev = safe_str(fm.get("severity"), "UNKNOWN").upper()
                sc = rc_map.get(sev,"#5a5a6e")
                desc = esc(fm.get("description",""))
                lk = esc(fm.get("likelihood",""))
                ev = esc(fm.get("evidence",""))
                st.markdown(f"""
                <div style="background:#1a1a24;border:1px solid #2a2a3a;border-radius:14px;padding:20px;margin-bottom:12px;">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
                <span style="font-family:JetBrains Mono;font-size:12px;color:#5a5a6e;background:#222230;padding:3px 10px;border-radius:6px;">#{i+1}</span>
                <span style="font-size:14px;font-weight:700;color:#ececf1;">{desc}</span></div>
                <div style="display:flex;gap:10px;margin-bottom:12px;">
                <span style="font-size:10px;font-weight:700;padding:3px 10px;border-radius:6px;color:{sc};background:rgba(100,100,100,0.1);border:1px solid rgba(100,100,100,0.2);">{sev}</span>
                <span style="font-size:12px;color:#8e8ea0;">Likelihood: {lk}</span></div>
                <div style="background:#222230;border-left:3px solid #7c5cfc;padding:12px 16px;border-radius:0 10px 10px 0;">
                <div style="font-size:10px;font-weight:700;color:#7c5cfc;letter-spacing:1px;margin-bottom:4px;">EVIDENCE</div>
                <div style="font-size:13px;color:#c0c0d0;line-height:1.6;">{ev}</div>
                </div></div>""", unsafe_allow_html=True)
        else:
            st.info("No failure modes identified.")

        if ms_l:
            items = "".join(f'<div style="display:flex;align-items:center;gap:8px;padding:8px 12px;margin-bottom:4px;background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.1);border-radius:8px;font-size:12px;color:#ef4444;">✕ {esc(s)}</div>' for s in ms_l if isinstance(s, str))
            if items:
                st.markdown(f'<div style="background:#1a1a24;border:1px solid #2a2a3a;border-radius:14px;padding:22px;"><div style="font-size:14px;font-weight:700;color:#ececf1;margin-bottom:12px;">🛡 Missing Safeguards</div>{items}</div>', unsafe_allow_html=True)
      except Exception as e:
        st.error(f"Error rendering Failures tab: {e}")

    # ─── TAB 4 ───
    with tab4:
      try:
        st.markdown("### ✅ Pre-Deploy Checklist")
        if cl_l:
            for idx, item in enumerate(cl_l):
                if not isinstance(item,dict): continue
                action = safe_str(item.get('action'), 'Action')
                reason = safe_str(item.get('reason'), '')
                st.checkbox(f"**{action}** — _{reason}_", key=f"cl_{idx}")
        else:
            st.info("No checklist generated.")

        st.markdown("---")
        trigger = esc(rb_o.get("trigger_criteria","Not defined"))
        st.markdown(f"""
        <div style="background:rgba(239,68,68,0.06);border:1px solid rgba(239,68,68,0.12);border-radius:12px;padding:16px 18px;margin-bottom:14px;">
        <div style="font-size:10px;font-weight:700;color:#ef4444;letter-spacing:1px;margin-bottom:4px;">🚨 ROLLBACK TRIGGER</div>
        <div style="font-size:13px;color:#fca5a5;line-height:1.5;">{trigger}</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"**⏱ Estimated:** `{safe_str(rb_o.get('total_estimated_time'), 'Unknown')}`")
        for step in safe_list(rb_o.get("steps")):
            if not isinstance(step,dict): continue
            with st.expander(f"Step {safe_str(step.get('step'),'?')}: {safe_str(step.get('action'),'')}"): 
                st.markdown(f"**Expected:** {safe_str(step.get('expected_result'),'N/A')}")
                st.markdown(f"**Time:** `{safe_str(step.get('time_estimate'),'N/A')}`")
        st.markdown(f"✅ **Verification:** {safe_str(rb_o.get('verification'),'N/A')}")

        st.markdown("---")
        st.markdown("### 📈 Monitoring Plan")
        st.markdown(f"**Duration:** `{safe_str(mo_o.get('monitoring_duration'), 'Unknown')}`")
        for m in safe_list(mo_o.get("key_metrics")):
            if not isinstance(m,dict): continue
            with st.expander(f"📏 {safe_str(m.get('metric'),'')}"):
                st.markdown(f"✅ Normal: `{safe_str(m.get('normal_range'),'N/A')}`")
                st.markdown(f"⚡ Alert: `{safe_str(m.get('alert_threshold'),'N/A')}`")
                st.markdown(f"🔥 Critical: `{safe_str(m.get('critical_threshold'),'N/A')}`")
      except Exception as e:
        st.error(f"Error rendering Recovery tab: {e}")

    # ─── TAB 5 ───
    with tab5:
      try:
        st.markdown("### 💬 Slack Message")
        st.code(safe_str(pl.get("slack_message"), "Not generated."), language=None)
        st.markdown("---")
        st.markdown("### 📧 Email Summary")
        st.code(safe_str(pl.get("email_summary"), "Not generated."), language=None)
        st.markdown("---")
        st.markdown("### 📋 On-Call Handoff")
        st.code(safe_str(pl.get("oncall_handoff"), "Not generated."), language=None)
      except Exception as e:
        st.error(f"Error rendering Comms tab: {e}")

    # Footer
    st.markdown("""
    <div style="text-align:center;padding:24px 0 8px;margin-top:16px;border-top:1px solid #1a1a24;">
    <p style="font-size:11px;color:#3a3a50;">Built with Google Gemini 2.5 Flash · Multi-Agent Architecture · Python + Streamlit</p>
    </div>
    """, unsafe_allow_html=True)