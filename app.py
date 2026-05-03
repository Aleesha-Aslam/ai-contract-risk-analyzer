import streamlit as st
import streamlit.components.v1 as components
import time
import datetime
from utils.pdf_loader import load_pdf
from utils.chunker import chunk_text
from utils.embeddings import get_embeddings, get_model
from utils.vectorstore import create_index
from utils.retriever import retrieve
from utils.llm import generate_answer
from utils.risk_analyzer import analyze_risk, calculate_risk_score, calculate_category_scores
from utils.summarizer import summarize
from utils.ner_extractor import extract_entities
from utils.gemini_llm import gemini_answer, gemini_summarize, gemini_risk
from utils.translator import translate_to_urdu
from utils.pdf_report import generate_pdf_report
from utils.entity_graph import build_entity_graph

st.set_page_config(
    page_title="AI Contract Risk Analyzer",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Splash Screen ──────────────────────────────────────────
if "app_loaded" not in st.session_state:
    st.session_state.app_loaded = False

if not st.session_state.app_loaded:
    splash = st.empty()
    with splash.container():
        st.markdown("""
        <style>
        .splash-bg {
            position: fixed; top: 0; left: 0;
            width: 100vw; height: 100vh;
            background: linear-gradient(135deg, #0f0a1e, #1a0a2e, #0f0a1e);
            display: flex; flex-direction: column;
            align-items: center; justify-content: center; z-index: 9999;
        }
        .splash-title {
            font-size: 3.5rem; font-weight: 900;
            background: linear-gradient(135deg, #a855f7, #ec4899, #c084fc);
            background-size: 300% 300%;
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
            text-align: center; margin-bottom: 0.5rem;
            animation: gradientShift 3s ease infinite;
        }
        .splash-sub { color: #c084fc; font-size: 1.1rem; text-align: center; margin-bottom: 2rem; animation: fadeInUp 1s ease forwards; }
        .splash-loader { width: 200px; height: 4px; background: #3b0764; border-radius: 4px; overflow: hidden; }
        .splash-bar { height: 100%; background: linear-gradient(90deg, #7c3aed, #ec4899); border-radius: 4px; animation: load 2.5s ease forwards; }
        @keyframes load { 0% { width: 0%; } 100% { width: 100%; } }
        @keyframes gradientShift { 0% { background-position: 0% 50%; } 50% { background-position: 100% 50%; } 100% { background-position: 0% 50%; } }
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
        </style>
        <div class="splash-bg">
            <div class="splash-title">⚖️ AI Contract Risk Analyzer</div>
            <div class="splash-sub">Initializing AI Models & Loading Components...</div>
            <div class="splash-loader"><div class="splash-bar"></div></div>
        </div>
        """, unsafe_allow_html=True)
        time.sleep(2.5)
    splash.empty()
    st.session_state.app_loaded = True
    st.rerun()

# ── Session State ──────────────────────────────────────────
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = True
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "contract_history" not in st.session_state:
    st.session_state.contract_history = []

dark = st.session_state.dark_mode

# ── Purple Theme Colors ────────────────────────────────────
bg_main    = "#0f0a1e" if dark else "#f5f3ff"
bg_card    = "#1a0a2e" if dark else "#ffffff"
bg_sidebar = "#130820" if dark else "#ede9fe"
border     = "#3b0764" if dark else "#c4b5fd"
text_main  = "#f3e8ff" if dark else "#1e1b4b"
text_muted = "#c084fc" if dark else "#7c3aed"
text_input = "#1a0a2e" if dark else "#f5f3ff"
tab_bg     = "#130820" if dark else "#ddd6fe"
answer_bg  = "#1a0a2e" if dark else "#faf5ff"
summary_bg = "#1a0a2e" if dark else "#fdf4ff"
gemini_bg  = "#160920" if dark else "#faf5ff"
accent1    = "#a855f7"
accent2    = "#ec4899"
accent3    = "#c084fc"

# ── CSS + Animations ───────────────────────────────────────
st.markdown(f"""
<style>
    [data-testid="stAppViewContainer"] {{ background: {bg_main} !important; }}
    [data-testid="stSidebar"] {{ background: {bg_sidebar} !important; border-right: 1px solid {border}; }}
    .main, .block-container {{ background: {bg_main} !important; }}
    p, span, div, label, h1, h2, h3, h4, h5, li {{ color: {text_main} !important; }}

    .main-title {{
        font-size: 2.8rem; font-weight: 800;
        background: linear-gradient(135deg, #a855f7, #ec4899, #c084fc, #a855f7);
        background-size: 300% 300%;
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        text-align: center; padding: 1rem 0 0.2rem 0;
        animation: gradientShift 4s ease infinite;
    }}
    @keyframes gradientShift {{
        0%   {{ background-position: 0% 50%; }}
        50%  {{ background-position: 100% 50%; }}
        100% {{ background-position: 0% 50%; }}
    }}
    .subtitle {{
        text-align: center; color: {text_muted} !important;
        font-size: 1rem; margin-bottom: 2rem;
        animation: fadeInUp 1s ease forwards;
    }}
    @keyframes fadeInUp {{
        from {{ opacity: 0; transform: translateY(12px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes slideInUp {{
        from {{ opacity: 0; transform: translateY(20px); }}
        to   {{ opacity: 1; transform: translateY(0); }}
    }}
    @keyframes popIn {{
        from {{ opacity: 0; transform: scale(0.4) rotate(-5deg); }}
        to   {{ opacity: 1; transform: scale(1) rotate(0deg); }}
    }}
    @keyframes buttonPulse {{
        0%, 100% {{ box-shadow: 0 0 10px rgba(168,85,247,0.3); }}
        50%       {{ box-shadow: 0 0 22px rgba(236,72,153,0.6); }}
    }}

    #particles-canvas {{
        position: fixed; top: 0; left: 0;
        width: 100vw; height: 100vh;
        pointer-events: none; z-index: 0;
    }}
    .wave-container {{
        position: fixed; bottom: 0; left: 0; right: 0;
        height: 160px; pointer-events: none; z-index: 0; overflow: hidden;
    }}

    .card {{
        background: {bg_card} !important; border: 1px solid {border};
        border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem;
        transition: transform 0.3s, border-color 0.3s, box-shadow 0.3s;
        animation: slideInUp 0.5s ease forwards;
    }}
    .card:hover {{
        transform: translateY(-5px);
        border-color: {accent1} !important;
        box-shadow: 0 0 25px rgba(168,85,247,0.35), 0 0 60px rgba(168,85,247,0.1);
    }}
    .card h3 {{ color: {text_main} !important; }}
    .card p  {{ color: {text_muted} !important; }}

    .stat-box {{
        background: {bg_card} !important; border: 1px solid {border};
        border-radius: 10px; padding: 1rem; text-align: center;
        transition: transform 0.3s, border-color 0.3s, box-shadow 0.3s;
        animation: fadeInUp 0.6s ease forwards;
    }}
    .stat-box:hover {{
        transform: translateY(-4px);
        border-color: {accent1};
        box-shadow: 0 0 20px rgba(168,85,247,0.3);
    }}
    .stat-number {{ font-size: 1.8rem; font-weight: 800; color: {accent1} !important; }}
    .stat-label  {{ font-size: 0.8rem; color: {text_muted} !important; margin-top: 2px; }}

    .stProgress > div {{ background: {border} !important; border-radius: 4px; }}
    .stProgress > div > div {{
        background: linear-gradient(90deg, #7c3aed, #ec4899) !important;
        border-radius: 4px;
        animation: progressFill 1.2s ease forwards;
    }}
    @keyframes progressFill {{
        from {{ width: 0% !important; }}
        to   {{ width: 100%; }}
    }}

    .badge-pop {{
        display: inline-block;
        animation: popIn 0.4s cubic-bezier(0.34,1.56,0.64,1) forwards;
        opacity: 0;
    }}

    .stButton > button {{
        background: linear-gradient(135deg, #7c3aed, #ec4899) !important;
        color: #ffffff !important; border: none; border-radius: 8px;
        padding: 0.5rem 1.5rem; font-weight: 600; width: 100%;
        transition: transform 0.2s, box-shadow 0.2s;
        animation: buttonPulse 3s ease infinite;
    }}
    .stButton > button:hover {{
        transform: scale(1.03);
        box-shadow: 0 0 30px rgba(168,85,247,0.6) !important;
        animation: none;
    }}

    [data-testid="stDownloadButton"] button {{
        background: {bg_card} !important;
        border: 1px solid {accent1} !important;
        color: {accent1} !important;
        border-radius: 8px !important; width: 100% !important;
        transition: background 0.3s, color 0.3s, box-shadow 0.3s;
        animation: none !important;
    }}
    [data-testid="stDownloadButton"] button:hover {{
        background: {accent1} !important;
        color: #ffffff !important;
        box-shadow: 0 0 20px rgba(168,85,247,0.5);
    }}

    .answer-box {{
        background: {answer_bg} !important; border-left: 4px solid {accent1};
        border-radius: 8px; padding: 1rem 1.2rem; margin-top: 0.5rem;
        color: {text_main} !important; font-size: 0.97rem; line-height: 1.7;
        animation: fadeInUp 0.5s ease forwards;
        transition: box-shadow 0.3s;
    }}
    .answer-box:hover {{ box-shadow: 0 0 20px rgba(168,85,247,0.2); }}
    .summary-box {{
        background: {summary_bg} !important; border-left: 4px solid {accent2};
        border-radius: 8px; padding: 1rem 1.2rem; margin-top: 0.5rem;
        color: {text_main} !important; font-size: 0.97rem; line-height: 1.7;
        animation: fadeInUp 0.5s ease forwards;
    }}
    .gemini-box {{
        background: {gemini_bg} !important; border-left: 4px solid #4285f4;
        border-radius: 8px; padding: 1rem 1.2rem; margin-top: 0.5rem;
        color: {text_main} !important; font-size: 0.97rem; line-height: 1.7;
        animation: fadeInUp 0.5s ease forwards;
    }}
    .copy-box {{
        background: {bg_card} !important; border: 1px solid {border};
        border-radius: 8px; padding: 0.8rem 1rem; margin-top: 0.3rem;
        color: {accent3} !important; font-size: 0.82rem;
        font-family: monospace; line-height: 1.6; word-wrap: break-word;
        white-space: pre-wrap; transition: border-color 0.3s;
    }}
    .copy-box:hover {{ border-color: {accent1}; }}

    .history-item {{
        background: {bg_card} !important; border: 1px solid {border};
        border-radius: 8px; padding: 0.6rem 0.8rem; margin-bottom: 0.4rem;
        transition: border-color 0.3s, transform 0.2s;
    }}
    .history-item:hover {{ border-color: {accent1}; transform: translateX(4px); }}

    [data-testid="stFileUploader"] {{
        background: {bg_card} !important;
        border: 2px dashed {accent1} !important;
        border-radius: 12px !important;
        transition: box-shadow 0.3s;
    }}
    [data-testid="stFileUploader"]:hover {{ box-shadow: 0 0 20px rgba(168,85,247,0.3); }}
    [data-testid="stFileUploader"] > div,
    [data-testid="stFileUploader"] > div > div {{ background: {bg_card} !important; }}
    [data-testid="stFileUploaderDropzone"] {{ background: {bg_card} !important; border: none !important; }}
    [data-testid="stFileUploaderDropzoneInstructions"],
    [data-testid="stFileUploaderDropzoneInstructions"] span,
    [data-testid="stFileUploaderDropzoneInstructions"] small {{ color: {text_muted} !important; }}
    [data-baseweb="button"] {{
        background: {bg_card} !important;
        border: 1px solid {accent1} !important;
        color: {accent1} !important; border-radius: 8px !important;
    }}

    .stTabs [data-baseweb="tab-list"] {{ background: {tab_bg} !important; border-radius: 10px; padding: 4px; gap: 4px; }}
    .stTabs [data-baseweb="tab"] {{ border-radius: 8px; color: {text_muted} !important; font-weight: 600; transition: background 0.3s; }}
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, #7c3aed, #ec4899) !important;
        color: #ffffff !important;
        box-shadow: 0 0 15px rgba(168,85,247,0.4);
    }}

    .stTextInput > div > div > input {{
        background: {text_input} !important; border: 1px solid {border} !important;
        border-radius: 8px; color: {text_main} !important;
        transition: border-color 0.3s, box-shadow 0.3s;
    }}
    .stTextInput > div > div > input:focus {{
        border-color: {accent1} !important;
        box-shadow: 0 0 15px rgba(168,85,247,0.3);
    }}
    .stTextInput > div > div > input::placeholder {{ color: {text_muted} !important; }}

    [data-baseweb="select"] > div {{
        background: {bg_card} !important; border-color: {border} !important; color: {text_main} !important;
    }}
    [data-baseweb="select"] span {{ color: {text_main} !important; }}

    [data-testid="stAlert"] {{
        background: {bg_card} !important; border: 1px solid {border} !important;
        animation: fadeInUp 0.4s ease forwards;
    }}
    [data-testid="stAlert"] p {{ color: {text_main} !important; }}
    [data-testid="stMarkdownContainer"] p {{ color: {text_main} !important; }}

    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] div {{ color: {text_main} !important; }}
    [data-testid="stSpinner"] p {{ color: {text_muted} !important; }}

    ::-webkit-scrollbar {{ width: 6px; }}
    ::-webkit-scrollbar-track {{ background: {bg_main}; }}
    ::-webkit-scrollbar-thumb {{ background: {accent1}; border-radius: 3px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: {accent2}; }}
</style>

<canvas id="particles-canvas"></canvas>
<div class="wave-container">
    <svg width="100%" height="160" viewBox="0 0 1440 160" preserveAspectRatio="none">
        <defs>
            <linearGradient id="wg1" x1="0%" y1="0%" x2="100%" y2="0%">
                <stop offset="0%"   style="stop-color:#7c3aed;stop-opacity:0.12"/>
                <stop offset="50%"  style="stop-color:#ec4899;stop-opacity:0.08"/>
                <stop offset="100%" style="stop-color:#7c3aed;stop-opacity:0.12"/>
            </linearGradient>
        </defs>
        <path id="wave1" fill="url(#wg1)" d="M0,80 C360,20 720,140 1440,80 L1440,160 L0,160 Z"/>
        <path id="wave2" fill="rgba(168,85,247,0.06)" d="M0,100 C480,40 960,140 1440,100 L1440,160 L0,160 Z"/>
    </svg>
</div>

<script>
(function() {{
    var canvas = document.getElementById('particles-canvas');
    if (!canvas) return;
    var ctx = canvas.getContext('2d');
    var W = window.innerWidth, H = window.innerHeight;
    canvas.width = W; canvas.height = H;
    window.addEventListener('resize', function() {{
        W = canvas.width = window.innerWidth;
        H = canvas.height = window.innerHeight;
    }});
    var particles = [];
    for (var i = 0; i < 70; i++) {{
        particles.push({{
            x: Math.random()*W, y: Math.random()*H,
            r: Math.random()*2+0.5,
            dx: (Math.random()-0.5)*0.5,
            dy: (Math.random()-0.5)*0.5,
            alpha: Math.random()*0.4+0.1,
            color: Math.random()>0.5?'168,85,247':'236,72,153'
        }});
    }}
    function drawParticles() {{
        ctx.clearRect(0,0,W,H);
        particles.forEach(function(p) {{
            ctx.beginPath();
            ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
            ctx.fillStyle='rgba('+p.color+','+p.alpha+')';
            ctx.fill();
            p.x+=p.dx; p.y+=p.dy;
            if(p.x<0||p.x>W) p.dx*=-1;
            if(p.y<0||p.y>H) p.dy*=-1;
        }});
        requestAnimationFrame(drawParticles);
    }}
    drawParticles();
    var wave1=document.getElementById('wave1');
    var wave2=document.getElementById('wave2');
    function animateWaves() {{
        var t=Date.now()/1000;
        if(wave1) {{
            var o1=Math.sin(t*0.5)*25;
            wave1.setAttribute('d','M0,'+(80+o1)+' C360,'+o1+' 720,'+(140+o1)+' 1440,'+(80+o1)+' L1440,160 L0,160 Z');
        }}
        if(wave2) {{
            var o2=Math.sin(t*0.7+1)*18;
            wave2.setAttribute('d','M0,'+(100+o2)+' C480,'+(40+o2)+' 960,'+(140+o2)+' 1440,'+(100+o2)+' L1440,160 L0,160 Z');
        }}
        requestAnimationFrame(animateWaves);
    }}
    animateWaves();
}})();
</script>
""", unsafe_allow_html=True)


# ── Helper Functions ───────────────────────────────────────
def copy_box(text):
    st.markdown(f'<div class="copy-box">{text}</div>', unsafe_allow_html=True)

def animated_badges(items, bg_color, text_color, prefix="⚠️"):
    badges = "".join([
        f"<span class='badge-pop' style='background:{bg_color}; color:{text_color}; padding:3px 10px; border-radius:12px; margin:3px; display:inline-block; animation-delay:{i*0.15}s'>{prefix} {k}</span>"
        for i, k in enumerate(items)
    ])
    st.markdown(badges, unsafe_allow_html=True)


# ── Header ─────────────────────────────────────────────────
st.markdown('<div class="main-title">⚖️ AI Contract Risk Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Upload legal contracts and get instant AI-powered insights</div>', unsafe_allow_html=True)


# ── Sidebar ────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"<p style='font-size:0.85rem; color:{text_muted} !important; margin-bottom:4px'>🎨 Theme</p>", unsafe_allow_html=True)
    col_moon, col_toggle = st.columns([1, 3])
    with col_moon:
        st.markdown("🌙" if dark else "☀️")
    with col_toggle:
        toggle_theme = st.toggle("Dark Mode" if dark else "Light Mode", value=st.session_state.dark_mode, key="theme_toggle")
    if toggle_theme != st.session_state.dark_mode:
        st.session_state.dark_mode = toggle_theme
        st.rerun()

    st.markdown("---")
    st.markdown("### 📂 Upload Contracts")
    uploaded_files = st.file_uploader("Drop PDF files here", accept_multiple_files=True, type=["pdf"], label_visibility="collapsed")

    if uploaded_files:
        st.markdown("---")
        st.markdown("### 📄 Uploaded Files")
        for f in uploaded_files:
            st.markdown(f"✅ `{f.name}`")

    st.markdown("---")
    st.markdown("### 🤖 AI Model")
    use_gemini = st.toggle("Use Gemini AI", value=False)
    if use_gemini:
        gemini_api_key = st.text_input("Gemini API Key", type="password", placeholder="Paste your API key here")
        if gemini_api_key:
            st.success("✅ Gemini ready!")
        else:
            st.warning("⚠️ Enter API key to use Gemini")
    else:
        gemini_api_key = None
        st.info("⚡ Using local Flan-T5 model")

    st.markdown("---")
    st.markdown("### 📋 Contract History")
    if st.session_state.contract_history:
        for item in reversed(st.session_state.contract_history[-5:]):
            st.markdown(f"""
            <div class="history-item">
                <p style='color:{text_main} !important; font-size:0.8rem; font-weight:700; margin:0'>📄 {item['name']}</p>
                <p style='color:{text_muted} !important; font-size:0.75rem; margin:0'>{item['emoji']} {item['level']} · {item['score']}/100</p>
                <p style='color:{text_muted} !important; font-size:0.7rem; margin:0'>{item['time']}</p>
            </div>
            """, unsafe_allow_html=True)
        if st.button("🗑️ Clear History", key="clear_history"):
            st.session_state.contract_history = []
            st.rerun()
    else:
        st.markdown(f"<p style='color:{text_muted} !important; font-size:0.8rem'>No contracts analyzed yet</p>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### 📊 Features")
    st.markdown(f"""
    <div style='background:{bg_card}; border:1px solid {border}; border-radius:10px; padding:0.8rem;'>
        {''.join([f"<div style='display:flex; justify-content:space-between; margin-bottom:5px'><span style='color:{text_muted} !important; font-size:0.78rem'>{f}</span><span style='color:{accent1} !important; font-weight:700; font-size:0.78rem'>✅</span></div>" for f in ["💬 Chat + History", "🚨 Risk + Categories", "📄 AI Summary", "🏷️ NER Entities", "🌍 Urdu Translation", "📄 PDF Export", "🤖 Gemini AI", "🕸️ Entity Graph", "📊 Compare Mode"]])}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown(f"""
    <div style='background:{bg_card}; border:1px solid {border}; border-radius:10px; padding:0.8rem;'>
        <p style='color:{text_main} !important; font-size:0.85rem; font-weight:700; margin-bottom:6px'>⚖️ AI Contract Risk Analyzer</p>
        <p style='color:{text_muted} !important; font-size:0.78rem; line-height:1.6; margin-bottom:8px'>AI-powered legal contract analysis tool.</p>
        <div style='border-top:1px solid {border}; padding-top:8px'>
            <p style='color:{text_muted} !important; font-size:0.75rem; margin-bottom:3px'>🔒 100% Local & Private</p>
            <p style='color:{text_muted} !important; font-size:0.75rem; margin-bottom:3px'>⚡ Flan-T5 & BART Models</p>
            <p style='color:{text_muted} !important; font-size:0.75rem; margin-bottom:3px'>🤖 Gemini AI Optional</p>
            <p style='color:{text_muted} !important; font-size:0.75rem; margin-bottom:0'>🌍 Urdu + PDF Support</p>
        </div>
    </div>
    <div style='text-align:center; margin-top:10px'>
        <p style='color:{text_muted} !important; font-size:0.73rem'>Made with ❤️ for AI Course</p>
        <p style='background:linear-gradient(135deg,#a855f7,#ec4899); -webkit-background-clip:text; -webkit-text-fill-color:transparent; font-size:0.73rem; font-weight:700'>v3.0 — Final Version</p>
    </div>
    """, unsafe_allow_html=True)


# ── Main Content ───────────────────────────────────────────
if not uploaded_files:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(f"""<div class="card"><h3>🔍 Smart Analysis</h3><p style='color:{text_muted} !important'>Detects risky clauses, ambiguous terms, and liability issues automatically.</p></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="card"><h3>💬 Ask Anything</h3><p style='color:{text_muted} !important'>Chat with your contract in plain English and get instant answers.</p></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="card"><h3>🌍 Urdu Support</h3><p style='color:{text_muted} !important'>Translate contract analysis to Urdu — اردو میں ترجمہ۔</p></div>""", unsafe_allow_html=True)
    st.markdown(f"""<div style='text-align:center; color:{text_muted}; margin-top:3rem; font-size:0.95rem; animation: fadeInUp 1s ease forwards'>⬅️ Upload a PDF contract from the sidebar to get started</div>""", unsafe_allow_html=True)

else:
    with st.spinner("🔄 Processing documents..."):
        chunks = []
        all_text = ""
        for file in uploaded_files:
            text = load_pdf(file)
            all_text += text
            chunks += chunk_text(text)
        embeddings = get_embeddings(chunks)
        index = create_index(embeddings)

    word_count = len(all_text.split())
    reading_time = max(1, round(word_count / 200))

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""<div class="stat-box"><div class="stat-number">{len(uploaded_files)}</div><div class="stat-label">📄 Documents</div></div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""<div class="stat-box"><div class="stat-number">{word_count:,}</div><div class="stat-label">📝 Words</div></div>""", unsafe_allow_html=True)
    with col3:
        st.markdown(f"""<div class="stat-box"><div class="stat-number">{reading_time}</div><div class="stat-label">⏱️ Min Read</div></div>""", unsafe_allow_html=True)
    with col4:
        st.markdown(f"""<div class="stat-box"><div class="stat-number">{len(chunks)}</div><div class="stat-label">🧩 Chunks</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background:{bg_card}; border:1px solid {border}; border-radius:10px; padding:0.6rem 1rem; margin-bottom:1rem; animation: fadeInUp 0.6s ease forwards;'>
        <span style='font-size:1.2rem; margin-right:8px'>📖</span>
        <b style='color:{text_main} !important'>{word_count:,} words</b>
        <span style='color:{text_muted} !important'> · ~{reading_time} min read · {len(all_text):,} characters</span>
    </div>
    """, unsafe_allow_html=True)

    if use_gemini and gemini_api_key:
        st.success(f"✅ {len(uploaded_files)} document(s) processed — 🤖 Gemini AI active!")
    else:
        st.success(f"✅ {len(uploaded_files)} document(s) processed successfully!")

    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "💬  Chat", "🚨  Risk Analysis", "📄  Summary",
        "🏷️  Entities", "🌍  Urdu", "🕸️  Entity Graph", "📊  Compare"
    ])

    # ── TAB 1: CHAT ──
    with tab1:
        st.markdown("#### Ask a question about your contract")
        if use_gemini and gemini_api_key:
            st.markdown(f"<span style='background:#1e1b4b; color:#a5b4fc; padding:3px 10px; border-radius:12px; font-size:0.85rem'>🤖 Gemini AI</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span style='background:{bg_card}; color:{text_muted}; padding:3px 10px; border-radius:12px; font-size:0.85rem'>⚡ Local Model</span>", unsafe_allow_html=True)

        for chat in st.session_state.chat_history:
            st.markdown(f"""
            <div style='background:{bg_card}; border:1px solid {border}; border-radius:8px; padding:0.8rem 1rem; margin-bottom:0.5rem; animation: slideInUp 0.4s ease forwards;'>
                <span style='color:{accent1} !important; font-weight:700'>You:</span>
                <span style='color:{text_main} !important; margin-left:8px'>{chat['question']}</span>
            </div>
            """, unsafe_allow_html=True)
            box_class = "gemini-box" if chat.get("is_gemini") else "answer-box"
            icon = "🤖" if chat.get("is_gemini") else "💬"
            st.markdown(f'<div class="{box_class}">{icon} {chat["answer"]}</div>', unsafe_allow_html=True)
            copy_box(chat["answer"])
            st.markdown("<br>", unsafe_allow_html=True)

        query = st.text_input("Question", placeholder="e.g. What are the payment terms?", label_visibility="collapsed", key="chat_input")
        col_btn1, col_btn2 = st.columns([4, 1])
        with col_btn1:
            ask_clicked = st.button("🔍 Get Answer", key="chat_btn")
        with col_btn2:
            clear_clicked = st.button("🗑️ Clear", key="clear_btn")

        if clear_clicked:
            st.session_state.chat_history = []
            st.rerun()

        if ask_clicked:
            if query.strip() == "":
                st.warning("Please enter a question.")
            else:
                with st.spinner("🤔 Thinking..."):
                    model = get_model()
                    results = retrieve(query, model, index, chunks)
                    context = " ".join(results)
                    if use_gemini and gemini_api_key:
                        answer = gemini_answer(context, query, gemini_api_key)
                        st.session_state.chat_history.append({"question": query, "answer": answer, "is_gemini": True})
                    else:
                        answer = generate_answer(context, query)
                        st.session_state.chat_history.append({"question": query, "answer": answer, "is_gemini": False})
                st.rerun()

        if st.session_state.chat_history:
            st.markdown(f"<div style='text-align:right; color:{text_muted}; font-size:0.8rem'>{len(st.session_state.chat_history)} question(s) asked</div>", unsafe_allow_html=True)
            chat_export = "\n\n".join([f"Q: {c['question']}\nA: {c['answer']}" for c in st.session_state.chat_history])
            st.download_button(label="📥 Download Chat History", data=chat_export, file_name="chat_history.txt", mime="text/plain")

    # ── TAB 2: RISK ──
    with tab2:
        st.markdown("#### Automatic Risk Detection")
        st.markdown(f"<p style='color:{text_muted} !important'>Analyzes your contract for risky clauses and liability issues.</p>", unsafe_allow_html=True)

        if st.button("🚨 Analyze Risk", key="risk_btn"):
            score, level, keywords = calculate_risk_score(all_text)
            category_scores = calculate_category_scores(all_text)
            color = "#f85149" if level == "HIGH" else "#d29922" if level == "MEDIUM" else "#3fb950"
            emoji = "🔴" if level == "HIGH" else "🟡" if level == "MEDIUM" else "🟢"

            st.session_state.contract_history.append({
                "name": uploaded_files[0].name if uploaded_files else "Contract",
                "score": score, "level": level, "emoji": emoji,
                "time": datetime.datetime.now().strftime("%b %d, %H:%M")
            })

            st.markdown(f"""
            <div class="card" style="border-color:{color}; border-width:2px; animation: slideInUp 0.5s ease forwards;">
                <p style='color:{text_muted} !important; margin-bottom:4px'>Overall Risk Score</p>
                <span style='font-size:2.5rem; font-weight:800; color:{color} !important'>{score}/100</span>
                <span style='margin-left:12px; font-size:1.1rem; color:{text_main} !important'>{emoji} {level} RISK</span>
            </div>
            """, unsafe_allow_html=True)
            st.progress(score / 100)

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"<p style='font-weight:700; color:{text_main} !important'>📋 Category Breakdown</p>", unsafe_allow_html=True)
            for cat, data in category_scores.items():
                col_cat, col_bar, col_score = st.columns([3, 5, 2])
                with col_cat:
                    st.markdown(f"<p style='color:{text_main} !important; margin:0; padding-top:6px'>{cat}</p>", unsafe_allow_html=True)
                with col_bar:
                    st.progress(data["score"] / 100)
                with col_score:
                    st.markdown(f"<p style='color:{data['color']} !important; font-weight:700; margin:0; padding-top:6px'>{data['emoji']} {data['score']}/100</p>", unsafe_allow_html=True)

            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            with col1:
                st.markdown(f"""<div class="stat-box" style="border-color:#f85149"><div class="stat-number" style="color:#f85149 !important">{len(keywords['high'])}</div><div class="stat-label">🔴 High Risk</div></div>""", unsafe_allow_html=True)
            with col2:
                st.markdown(f"""<div class="stat-box" style="border-color:#d29922"><div class="stat-number" style="color:#d29922 !important">{len(keywords['medium'])}</div><div class="stat-label">🟡 Medium Risk</div></div>""", unsafe_allow_html=True)
            with col3:
                st.markdown(f"""<div class="stat-box" style="border-color:#3fb950"><div class="stat-number" style="color:#3fb950 !important">{len(keywords['low'])}</div><div class="stat-label">🟢 Low Risk</div></div>""", unsafe_allow_html=True)

            if keywords["high"]:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"<p style='color:{text_main} !important; font-weight:700'>🔴 High Risk Clauses:</p>", unsafe_allow_html=True)
                animated_badges(keywords["high"], "#4f1010", "#f85149")

            if keywords["medium"]:
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"<p style='color:{text_main} !important; font-weight:700'>🟡 Medium Risk Clauses:</p>", unsafe_allow_html=True)
                animated_badges(keywords["medium"], "#4f3800", "#d29922")

            st.markdown("<br>", unsafe_allow_html=True)
            with st.spinner("🤖 Getting AI analysis..."):
                if use_gemini and gemini_api_key:
                    risk_result = gemini_risk(all_text, gemini_api_key)
                    st.markdown(f'<div class="gemini-box">{risk_result}</div>', unsafe_allow_html=True)
                else:
                    risk_result = analyze_risk(all_text)
                    st.markdown(f'<div class="answer-box">{risk_result}</div>', unsafe_allow_html=True)
            copy_box(risk_result)

            with st.spinner("📄 Preparing PDF..."):
                pdf_summary = gemini_summarize(all_text, gemini_api_key) if use_gemini and gemini_api_key else summarize(all_text)
                pdf_entities = extract_entities(all_text)

            pdf_buffer = generate_pdf_report(
                filename="contract_risk_report.pdf",
                risk_score=score, risk_level=level, keywords=keywords,
                category_scores=category_scores, ai_analysis=risk_result,
                summary=pdf_summary, entities=pdf_entities
            )
            st.markdown("<br>", unsafe_allow_html=True)
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.download_button(label="📄 Download PDF Report", data=pdf_buffer, file_name="contract_risk_report.pdf", mime="application/pdf")
            with col_d2:
                st.download_button(label="📥 Download TXT Report", data=f"Risk Score: {score}/100\nRisk Level: {level}\n\nHigh: {', '.join(keywords['high'])}\nMedium: {', '.join(keywords['medium'])}\nLow: {', '.join(keywords['low'])}\n\nAI Analysis:\n{risk_result}", file_name="risk_report.txt", mime="text/plain")

    # ── TAB 3: SUMMARY ──
    with tab3:
        st.markdown("#### Contract Summary")
        st.markdown(f"<p style='color:{text_muted} !important'>Get a concise plain-English summary of the entire contract.</p>", unsafe_allow_html=True)
        if st.button("📄 Generate Summary", key="summary_btn"):
            with st.spinner("📝 Summarizing..."):
                if use_gemini and gemini_api_key:
                    summary = gemini_summarize(all_text, gemini_api_key)
                    st.markdown(f'<div class="gemini-box">🤖 {summary}</div>', unsafe_allow_html=True)
                else:
                    summary = summarize(all_text)
                    st.markdown(f'<div class="summary-box">📄 {summary}</div>', unsafe_allow_html=True)
            copy_box(summary)
            st.markdown("<br>", unsafe_allow_html=True)
            st.download_button(label="📥 Download Summary", data=summary, file_name="contract_summary.txt", mime="text/plain")

    # ── TAB 4: ENTITIES ──
    with tab4:
        st.markdown("#### 🏷️ Key Entity Extraction")
        st.markdown(f"<p style='color:{text_muted} !important'>Automatically extracts people, organizations, dates, amounts and more.</p>", unsafe_allow_html=True)
        if st.button("🔍 Extract Entities", key="ner_btn"):
            with st.spinner("🔍 Extracting..."):
                entities = extract_entities(all_text)
            any_found = any(len(v) > 0 for v in entities.values())
            if not any_found:
                st.warning("No entities found in this document.")
            else:
                cols = st.columns(2)
                col_index = 0
                for label, items in entities.items():
                    if items:
                        with cols[col_index % 2]:
                            badges = "".join([
                                f"<span class='badge-pop' style='background:{bg_main}; color:{text_main} !important; padding:4px 12px; border-radius:12px; margin:3px; display:inline-block; border:1px solid {border}; animation-delay:{i*0.1}s'>{item}</span>"
                                for i, item in enumerate(items)
                            ])
                            st.markdown(f"""<div class="card"><p style='font-weight:700; font-size:1rem; margin-bottom:0.8rem; color:{accent1} !important'>{label}</p>{badges}</div>""", unsafe_allow_html=True)
                        col_index += 1
                entity_export = "\n\n".join([f"{label}:\n" + "\n".join(f"  - {item}" for item in items) for label, items in entities.items() if items])
                st.markdown("<br>", unsafe_allow_html=True)
                st.download_button(label="📥 Download Entities", data=entity_export, file_name="contract_entities.txt", mime="text/plain")

    # ── TAB 5: URDU ──
    with tab5:
        st.markdown("#### 🌍 Urdu Translation — اردو ترجمہ")
        st.markdown(f"<p style='color:{text_muted} !important'>Translate contract summary and analysis to Urdu.</p>", unsafe_allow_html=True)
        translate_what = st.selectbox("What to translate?", ["📄 Contract Summary", "🚨 Risk Analysis", "📝 Full Contract Text (first 2000 chars)"], label_visibility="collapsed")
        if st.button("🌍 Translate to Urdu", key="urdu_btn"):
            with st.spinner("🌍 Translating..."):
                if translate_what == "📄 Contract Summary":
                    source_text = gemini_summarize(all_text, gemini_api_key) if use_gemini and gemini_api_key else summarize(all_text)
                elif translate_what == "🚨 Risk Analysis":
                    source_text = gemini_risk(all_text, gemini_api_key) if use_gemini and gemini_api_key else analyze_risk(all_text)
                else:
                    source_text = all_text[:2000]
                urdu_text = translate_to_urdu(source_text)

            st.markdown(f"<p style='color:{text_main} !important; font-weight:700'>Original (English):</p>", unsafe_allow_html=True)
            st.markdown(f'<div class="answer-box">{source_text}</div>', unsafe_allow_html=True)
            copy_box(source_text)
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"<p style='color:{text_main} !important; font-weight:700'>اردو ترجمہ (Urdu Translation):</p>", unsafe_allow_html=True)
            st.markdown(f"""
            <div style='background:{bg_card}; border-left:4px solid #22c55e; border-radius:8px;
                padding:1rem 1.2rem; margin-top:0.5rem; color:{text_main} !important;
                font-size:1.1rem; line-height:2; direction:rtl; text-align:right;
                font-family:"Noto Nastaliq Urdu","Jameel Noori Nastaleeq",serif;
                animation: fadeInUp 0.5s ease forwards;'>
                {urdu_text}
            </div>
            """, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.download_button(label="📥 Download English", data=source_text, file_name="contract_english.txt", mime="text/plain")
            with col_d2:
                st.download_button(label="📥 Download Urdu اردو", data=urdu_text, file_name="contract_urdu.txt", mime="text/plain")

    # ── TAB 6: ENTITY GRAPH ──
    with tab6:
        st.markdown("#### 🕸️ Named Entity Network Graph")
        st.markdown(f"<p style='color:{text_muted} !important'>Visualizes relationships between people, organizations, locations and more.</p>", unsafe_allow_html=True)
        if st.button("🕸️ Generate Graph", key="graph_btn"):
            with st.spinner("🕸️ Building entity network..."):
                entities = extract_entities(all_text)
                any_found = any(len(v) > 0 for v in entities.values())
            if not any_found:
                st.warning("No entities found to build graph.")
            else:
                st.markdown(f"""
                <div style='display:flex; gap:12px; flex-wrap:wrap; margin-bottom:1rem'>
                    {''.join([f"<span class='badge-pop' style='background:{bg_card}; padding:4px 12px; border-radius:12px; border:1px solid {border}; font-size:0.8rem; animation-delay:{i*0.1}s'><span style='color:{c}'>●</span> {l}</span>" for i,(c,l) in enumerate([('#a855f7','People'),('#ec4899','Organizations'),('#f85149','Locations'),('#22c55e','Money'),('#f59e0b','Dates'),('#c084fc','Legal')])])}
                </div>
                """, unsafe_allow_html=True)
                graph_html = build_entity_graph(entities, bg_color=bg_main)
                components.html(graph_html, height=520)
                st.markdown(f"""
                <div style='background:{bg_card}; border:1px solid {border}; border-radius:8px; padding:0.8rem 1rem; margin-top:0.5rem'>
                    <p style='color:{text_muted} !important; font-size:0.8rem; margin:0'>💡 Drag nodes · Hover for details · Scroll to zoom</p>
                </div>
                """, unsafe_allow_html=True)

    # ── TAB 7: COMPARE ──
    with tab7:
        st.markdown("#### 📊 Contract Comparison Mode")
        st.markdown(f"<p style='color:{text_muted} !important'>Upload a second contract to compare risk scores side by side.</p>", unsafe_allow_html=True)
        compare_file = st.file_uploader("Upload second contract", type=["pdf"], key="compare_upload", label_visibility="collapsed")

        if compare_file is None:
            st.markdown(f"""
            <div style='background:{bg_card}; border:2px dashed {border}; border-radius:12px; padding:2rem; text-align:center; margin-top:1rem; animation: fadeInUp 0.5s ease forwards;'>
                <p style='font-size:2rem; margin-bottom:0.5rem'>📂</p>
                <p style='color:{text_muted} !important'>Upload a second PDF contract above to compare</p>
            </div>
            """, unsafe_allow_html=True)
        else:
            if st.button("📊 Compare Contracts", key="compare_btn"):
                with st.spinner("📊 Analyzing both contracts..."):
                    score1, level1, keywords1 = calculate_risk_score(all_text)
                    cat1 = calculate_category_scores(all_text)
                    text2 = load_pdf(compare_file)
                    score2, level2, keywords2 = calculate_risk_score(text2)
                    cat2 = calculate_category_scores(text2)

                color1 = "#f85149" if level1 == "HIGH" else "#d29922" if level1 == "MEDIUM" else "#3fb950"
                color2 = "#f85149" if level2 == "HIGH" else "#d29922" if level2 == "MEDIUM" else "#3fb950"
                emoji1 = "🔴" if level1 == "HIGH" else "🟡" if level1 == "MEDIUM" else "🟢"
                emoji2 = "🔴" if level2 == "HIGH" else "🟡" if level2 == "MEDIUM" else "🟢"
                name1 = uploaded_files[0].name if uploaded_files else "Contract 1"
                name2 = compare_file.name

                winner_msg = f"⚠️ {name1} is riskier" if score1 > score2 else f"⚠️ {name2} is riskier" if score2 > score1 else "⚖️ Equal risk scores"
                winner_color = color1 if score1 > score2 else color2 if score2 > score1 else accent1

                st.markdown(f"""
                <div style='background:{bg_card}; border:2px solid {winner_color}; border-radius:12px; padding:1rem 1.5rem; margin-bottom:1.5rem; text-align:center; animation: slideInUp 0.5s ease forwards;'>
                    <p style='color:{winner_color} !important; font-size:1.1rem; font-weight:700; margin:0'>{winner_msg}</p>
                </div>
                """, unsafe_allow_html=True)

                col_left, col_mid, col_right = st.columns([5, 1, 5])
                with col_left:
                    st.markdown(f"""
                    <div class="card" style="border-color:{color1}; text-align:center">
                        <p style='color:{text_muted} !important; font-size:0.8rem; margin-bottom:4px'>📄 {name1}</p>
                        <span style='font-size:2.8rem; font-weight:900; color:{color1} !important'>{score1}/100</span>
                        <p style='color:{color1} !important; font-weight:700; margin-top:4px'>{emoji1} {level1} RISK</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.progress(score1 / 100)
                with col_mid:
                    st.markdown(f"<p style='text-align:center; color:{accent1} !important; padding-top:40px; font-size:1.5rem; font-weight:900'>VS</p>", unsafe_allow_html=True)
                with col_right:
                    st.markdown(f"""
                    <div class="card" style="border-color:{color2}; text-align:center">
                        <p style='color:{text_muted} !important; font-size:0.8rem; margin-bottom:4px'>📄 {name2}</p>
                        <span style='font-size:2.8rem; font-weight:900; color:{color2} !important'>{score2}/100</span>
                        <p style='color:{color2} !important; font-weight:700; margin-top:4px'>{emoji2} {level2} RISK</p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.progress(score2 / 100)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-weight:700; color:{text_main} !important'>📋 Category Comparison</p>", unsafe_allow_html=True)
                for cat in cat1.keys():
                    d1 = cat1[cat]; d2 = cat2[cat]
                    col_a, col_b, col_c, col_d, col_e = st.columns([3, 2, 1, 2, 3])
                    with col_a:
                        st.markdown(f"<p style='color:{d1['color']} !important; font-weight:700; text-align:right; margin:0; padding-top:6px'>{d1['score']}/100 {d1['emoji']}</p>", unsafe_allow_html=True)
                    with col_b:
                        st.progress(d1["score"] / 100)
                    with col_c:
                        st.markdown(f"<p style='color:{text_muted} !important; text-align:center; font-size:0.7rem; margin:0; padding-top:8px'>{cat.split()[0]}</p>", unsafe_allow_html=True)
                    with col_d:
                        st.progress(d2["score"] / 100)
                    with col_e:
                        st.markdown(f"<p style='color:{d2['color']} !important; font-weight:700; margin:0; padding-top:6px'>{d2['emoji']} {d2['score']}/100</p>", unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)
                col_left, col_right = st.columns(2)
                with col_left:
                    st.markdown(f"<p style='font-weight:700; color:{text_main} !important'>📄 {name1} Keywords</p>", unsafe_allow_html=True)
                    animated_badges(keywords1["high"], "#4f1010", "#f85149")
                    animated_badges(keywords1["medium"], "#4f3800", "#d29922")
                with col_right:
                    st.markdown(f"<p style='font-weight:700; color:{text_main} !important'>📄 {name2} Keywords</p>", unsafe_allow_html=True)
                    animated_badges(keywords2["high"], "#4f1010", "#f85149")
                    animated_badges(keywords2["medium"], "#4f3800", "#d29922")

                unique1 = set(keywords1["high"] + keywords1["medium"]) - set(keywords2["high"] + keywords2["medium"])
                unique2 = set(keywords2["high"] + keywords2["medium"]) - set(keywords1["high"] + keywords1["medium"])

                if unique1 or unique2:
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(f"<p style='font-weight:700; color:{text_main} !important'>🔍 Unique Risk Differences</p>", unsafe_allow_html=True)
                    col_u1, col_u2 = st.columns(2)
                    with col_u1:
                        if unique1:
                            st.markdown(f"<p style='color:{text_muted} !important; font-size:0.85rem'>Only in {name1}:</p>", unsafe_allow_html=True)
                            animated_badges(list(unique1), "#4f1010", "#f85149")
                    with col_u2:
                        if unique2:
                            st.markdown(f"<p style='color:{text_muted} !important; font-size:0.85rem'>Only in {name2}:</p>", unsafe_allow_html=True)
                            animated_badges(list(unique2), "#4f1010", "#f85149")

                rec_color = "#3fb950" if score1 != score2 else "#d29922"
                rec = f"✅ Recommend signing {name1} — lower risk ({score1}/100)" if score1 < score2 else f"✅ Recommend signing {name2} — lower risk ({score2}/100)" if score2 < score1 else "⚖️ Equal risk. Review each carefully."

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(f"""
                <div style='background:{bg_card}; border-left:4px solid {rec_color}; border-radius:8px; padding:1rem 1.2rem; animation: fadeInUp 0.5s ease forwards;'>
                    <p style='color:{text_main} !important; font-size:0.95rem; margin:0'>{rec}</p>
                </div>
                """, unsafe_allow_html=True)

                report = f"""CONTRACT COMPARISON REPORT\n{'='*50}\nCONTRACT 1: {name1}\nRisk Score: {score1}/100 | Risk Level: {level1}\nHigh: {', '.join(keywords1['high'])}\nMedium: {', '.join(keywords1['medium'])}\n\nCONTRACT 2: {name2}\nRisk Score: {score2}/100 | Risk Level: {level2}\nHigh: {', '.join(keywords2['high'])}\nMedium: {', '.join(keywords2['medium'])}\n\nUNIQUE TO {name1}: {', '.join(unique1) if unique1 else 'None'}\nUNIQUE TO {name2}: {', '.join(unique2) if unique2 else 'None'}\n\nRECOMMENDATION: {rec}"""
                st.markdown("<br>", unsafe_allow_html=True)
                st.download_button(label="📥 Download Comparison Report", data=report, file_name="contract_comparison.txt", mime="text/plain")