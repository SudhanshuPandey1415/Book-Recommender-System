import streamlit as st
import streamlit.components.v1 as components
import pickle
import numpy as np
import pandas as pd
import json
import os
from datetime import date, timedelta


# ─────────────────────────────────────────────
# Desktop notification handler (Safe import)
# ─────────────────────────────────────────────
def send_desktop_notification(title, message):
    try:
        from plyer import notification
        notification.notify(
            title=title,
            message=message,
            app_name="BookShelf",
            timeout=8
        )
    except Exception:
        pass

# ─────────────────────────────────────────────
# Page config  (MUST be first Streamlit call)
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="📚 BookShelf — Recommender & Reminder",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ─────────────────────────────────────────────
# Custom CSS  – premium glassmorphism theme
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Playfair+Display:ital,wght@0,700;1,400&display=swap');

    /* ══════════════════════════════════════
       ROOT TOKENS
    ══════════════════════════════════════ */
    :root {
        --bg-base:      #080714;
        --bg-surface:   rgba(255,255,255,0.042);
        --bg-surface2:  rgba(255,255,255,0.072);
        --accent1:      #a78bfa;
        --accent2:      #60a5fa;
        --accent3:      #f472b6;
        --accent-glow1: rgba(167,139,250,0.28);
        --accent-glow2: rgba(96,165,250,0.20);
        --text-main:    #eef2ff;
        --text-sub:     #c4c9e2;
        --text-muted:   #7c84a8;
        --border-soft:  rgba(255,255,255,0.08);
        --border-med:   rgba(255,255,255,0.14);
        --border-glow:  rgba(167,139,250,0.40);
        --blur-sm:      blur(8px);
        --blur-md:      blur(18px);
        --blur-lg:      blur(32px);
        --radius-sm:    10px;
        --radius-md:    16px;
        --radius-lg:    22px;
        --shadow-card:  0 4px 24px rgba(0,0,0,0.50), 0 1px 0 rgba(255,255,255,0.06) inset;
        --shadow-float: 0 16px 48px rgba(0,0,0,0.65), 0 0 0 1px rgba(167,139,250,0.18);
        --transition:   all 0.30s cubic-bezier(0.34,1.56,0.64,1);
        --transition-f: all 0.20s ease;
    }

    /* ══════════════════════════════════════
       ANIMATED MESH BACKGROUND
    ══════════════════════════════════════ */
    @keyframes meshShift {
        0%   { background-position: 0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    @keyframes orb1 {
        0%,100% { transform: translate(0,0) scale(1); }
        33%     { transform: translate(60px,-40px) scale(1.1); }
        66%     { transform: translate(-30px,50px) scale(0.92); }
    }
    @keyframes orb2 {
        0%,100% { transform: translate(0,0) scale(1); }
        40%     { transform: translate(-80px,30px) scale(1.12); }
        70%     { transform: translate(40px,-60px) scale(0.9); }
    }
    @keyframes shimmer {
        0%   { background-position: -200% 0; }
        100% { background-position:  200% 0; }
    }
    @keyframes fadeInUp {
        from { opacity:0; transform:translateY(18px); }
        to   { opacity:1; transform:translateY(0);    }
    }
    @keyframes pulseGlow {
        0%,100% { box-shadow: 0 0 0 0 rgba(167,139,250,0); }
        50%     { box-shadow: 0 0 24px 6px rgba(167,139,250,0.18); }
    }

    /* ── Base & mesh ── */
    html, body, [class*="css"] {
        font-family: 'Inter', system-ui, sans-serif;
        background-color: var(--bg-base) !important;
        color: var(--text-main) !important;
        -webkit-font-smoothing: antialiased;
        letter-spacing: 0.01em;
    }

    .stApp {
        background:
            radial-gradient(ellipse 80% 60% at 15% 20%,  rgba(139,92,246,0.18) 0%, transparent 55%),
            radial-gradient(ellipse 70% 55% at 85% 75%,  rgba(96,165,250,0.14) 0%, transparent 55%),
            radial-gradient(ellipse 60% 50% at 50% 100%, rgba(244,114,182,0.10) 0%, transparent 50%),
            linear-gradient(160deg, #080714 0%, #110d22 40%, #0c1528 100%);
        background-attachment: fixed;
    }

    /* floating orb pseudo-elements via stApp overlay */
    .stApp::before, .stApp::after {
        content:'';
        position: fixed;
        border-radius: 50%;
        pointer-events: none;
        z-index: 0;
        filter: blur(80px);
        opacity: 0.35;
    }
    .stApp::before {
        width: 520px; height: 520px;
        top: -120px; left: -100px;
        background: radial-gradient(circle, #7c3aed 0%, transparent 70%);
        animation: orb1 18s ease-in-out infinite;
    }
    .stApp::after {
        width: 420px; height: 420px;
        bottom: -80px; right: -80px;
        background: radial-gradient(circle, #2563eb 0%, transparent 70%);
        animation: orb2 22s ease-in-out infinite;
    }

    /* ══════════════════════════════════════
       SIDEBAR — frosted glass panel
    ══════════════════════════════════════ */
    [data-testid="stSidebar"] {
        background: rgba(10,9,20,0.72) !important;
        backdrop-filter: var(--blur-lg) saturate(180%) brightness(0.9);
        -webkit-backdrop-filter: var(--blur-lg) saturate(180%) brightness(0.9);
        border-right: 1px solid var(--border-med);
        box-shadow: 4px 0 32px rgba(0,0,0,0.45);
    }
    [data-testid="stSidebar"] > div { padding-top: 12px; }

    /* ══════════════════════════════════════
       HERO BANNER
    ══════════════════════════════════════ */
    .hero-banner {
        position: relative;
        border-radius: var(--radius-lg);
        padding: 48px 56px;
        margin-bottom: 36px;
        overflow: hidden;
        background:
            linear-gradient(135deg,
                rgba(76,29,149,0.90) 0%,
                rgba(30,58,138,0.85) 50%,
                rgba(14,116,144,0.80) 100%);
        backdrop-filter: var(--blur-md);
        border: 1px solid rgba(167,139,250,0.22);
        box-shadow:
            0 20px 60px rgba(0,0,0,0.55),
            0 0 0 1px rgba(167,139,250,0.12) inset,
            0 1px 0 rgba(255,255,255,0.10) inset;
        animation: fadeInUp 0.6s cubic-bezier(0.16,1,0.3,1) both;
    }
    .hero-banner::before {
        content:'';
        position: absolute; inset: 0;
        background:
            radial-gradient(ellipse 55% 70% at 75% 50%, rgba(167,139,250,0.22) 0%, transparent 65%),
            radial-gradient(ellipse 40% 60% at 20% 80%, rgba(96,165,250,0.18) 0%, transparent 60%);
        pointer-events: none;
    }
    /* shimmer sweep */
    .hero-banner::after {
        content:'';
        position: absolute; inset: 0;
        background: linear-gradient(105deg,
            transparent 35%,
            rgba(255,255,255,0.06) 50%,
            transparent 65%);
        background-size: 200% 100%;
        animation: shimmer 6s linear infinite;
        pointer-events: none;
    }
    .hero-title {
        font-family: 'Playfair Display', serif;
        font-size: 3rem; font-weight: 700;
        background: linear-gradient(90deg, #c4b5fd, #93c5fd, #f9a8d4);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 0 0 10px;
        line-height: 1.15;
        text-shadow: none;
        position: relative; z-index: 1;
    }
    .hero-sub {
        color: rgba(203,213,225,0.85);
        font-size: 1.05rem;
        font-weight: 400;
        letter-spacing: 0.015em;
        position: relative; z-index: 1;
    }

    /* ══════════════════════════════════════
       GLASS CARD (generic)
    ══════════════════════════════════════ */
    .glass-card {
        background: var(--bg-surface);
        backdrop-filter: var(--blur-md) saturate(160%);
        -webkit-backdrop-filter: var(--blur-md) saturate(160%);
        border: 1px solid var(--border-soft);
        border-top-color: rgba(255,255,255,0.13);
        border-radius: var(--radius-md);
        padding: 22px 24px;
        box-shadow: var(--shadow-card);
        transition: var(--transition);
    }
    .glass-card:hover {
        transform: translateY(-5px);
        border-color: var(--border-med);
        box-shadow: var(--shadow-float);
    }

    /* ══════════════════════════════════════
       BOOK CARDS
    ══════════════════════════════════════ */
    .book-card {
        position: relative;
        background:
            linear-gradient(160deg,
                rgba(255,255,255,0.08) 0%,
                rgba(255,255,255,0.02) 100%);
        backdrop-filter: var(--blur-sm);
        -webkit-backdrop-filter: var(--blur-sm);
        border: 1px solid var(--border-soft);
        border-top-color: rgba(255,255,255,0.12);
        border-radius: var(--radius-md);
        padding: 18px 14px 14px;
        text-align: center;
        overflow: hidden;
        transition: var(--transition);
        box-shadow: var(--shadow-card);
        animation: fadeInUp 0.45s cubic-bezier(0.16,1,0.3,1) both;
    }
    /* inner shimmer line */
    .book-card::before {
        content:'';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg,
            transparent, rgba(255,255,255,0.18), transparent);
        pointer-events: none;
    }
    .book-card:hover {
        transform: translateY(-8px) scale(1.025);
        border-color: rgba(167,139,250,0.45);
        box-shadow:
            0 20px 48px rgba(0,0,0,0.65),
            0 0 0 1px rgba(167,139,250,0.30),
            0 0 32px rgba(167,139,250,0.14);
        background:
            linear-gradient(160deg,
                rgba(167,139,250,0.10) 0%,
                rgba(96,165,250,0.05) 100%);
    }
    .book-card img {
        border-radius: var(--radius-sm);
        width: 100%; max-width: 130px;
        object-fit: cover;
        box-shadow: 0 8px 28px rgba(0,0,0,0.65), 0 2px 6px rgba(0,0,0,0.40);
        margin-bottom: 14px;
        transition: var(--transition-f);
    }
    .book-card:hover img {
        box-shadow: 0 12px 36px rgba(0,0,0,0.70), 0 0 16px rgba(167,139,250,0.22);
        transform: scale(1.04);
    }
    .book-title {
        font-weight: 600; font-size: 0.84rem;
        color: var(--text-main);
        margin: 4px 0; line-height: 1.35;
        letter-spacing: 0.005em;
    }
    .book-author { font-size: 0.76rem; color: var(--accent2); margin: 0 0 6px; font-weight: 500; }
    .star-badge  { font-size: 0.74rem; color: #fbbf24; letter-spacing: 1px; }
    .ratings-badge {
        display: block;
        font-size: 0.78rem;
        color: var(--text-muted);
        margin: 3px 0;
        letter-spacing: 0.01em;
    }

    /* ══════════════════════════════════════
       SECTION HEADER
    ══════════════════════════════════════ */
    .section-header {
        font-family: 'Playfair Display', serif;
        font-size: 1.65rem; font-weight: 700;
        background: linear-gradient(90deg, var(--accent1) 0%, var(--accent2) 100%);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text;
        margin: 4px 0 22px;
        line-height: 1.2;
    }

    /* ══════════════════════════════════════
       METRIC CARD (sidebar stats)
    ══════════════════════════════════════ */
    .metric-card {
        background: linear-gradient(135deg,
            rgba(167,139,250,0.12) 0%,
            rgba(96,165,250,0.07) 100%);
        backdrop-filter: var(--blur-sm);
        border: 1px solid rgba(167,139,250,0.20);
        border-top-color: rgba(167,139,250,0.32);
        border-radius: var(--radius-md);
        padding: 16px 10px;
        text-align: center;
        box-shadow: 0 4px 16px rgba(0,0,0,0.35);
        transition: var(--transition-f);
    }
    .metric-card:hover { animation: pulseGlow 1.8s ease infinite; }
    .metric-value { font-size: 1.9rem; font-weight: 700; color: var(--accent1); line-height: 1; }
    .metric-label { font-size: 0.76rem; color: var(--text-muted); margin-top: 5px; letter-spacing: 0.04em; text-transform: uppercase; }

    /* ══════════════════════════════════════
       REMINDER CARDS
    ══════════════════════════════════════ */
    .reminder-card {
        background:
            linear-gradient(140deg,
                rgba(244,114,182,0.08) 0%,
                rgba(167,139,250,0.05) 100%);
        backdrop-filter: var(--blur-sm);
        border: 1px solid rgba(244,114,182,0.18);
        border-top-color: rgba(244,114,182,0.28);
        border-radius: var(--radius-md);
        padding: 18px 20px;
        margin-bottom: 14px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.30);
        transition: var(--transition-f);
        animation: fadeInUp 0.4s cubic-bezier(0.16,1,0.3,1) both;
    }
    .reminder-card:hover { transform: translateX(4px); }
    .reminder-card.overdue {
        border-color: rgba(239,68,68,0.35);
        border-top-color: rgba(239,68,68,0.50);
        background: linear-gradient(140deg, rgba(239,68,68,0.09), rgba(239,68,68,0.04));
    }
    .reminder-card.today {
        border-color: rgba(251,191,36,0.38);
        border-top-color: rgba(251,191,36,0.55);
        background: linear-gradient(140deg, rgba(251,191,36,0.10), rgba(251,191,36,0.04));
    }
    .reminder-card.future {
        border-color: rgba(52,211,153,0.28);
        border-top-color: rgba(52,211,153,0.42);
        background: linear-gradient(140deg, rgba(52,211,153,0.07), rgba(52,211,153,0.02));
    }

    /* ══════════════════════════════════════
       BUTTONS
    ══════════════════════════════════════ */
    .stButton > button {
        background: linear-gradient(135deg, #8b5cf6, #3b82f6) !important;
        color: #fff !important;
        border: none !important;
        border-radius: var(--radius-sm) !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.02em !important;
        padding: 0.45rem 1rem !important;
        box-shadow: 0 4px 14px rgba(139,92,246,0.35), 0 1px 0 rgba(255,255,255,0.10) inset !important;
        transition: var(--transition) !important;
        position: relative;
        overflow: hidden;
    }
    .stButton > button::after {
        content:'';
        position: absolute; inset: 0;
        background: linear-gradient(135deg, rgba(255,255,255,0.12), transparent 60%);
        pointer-events: none;
    }
    .stButton > button:hover {
        transform: translateY(-2px) scale(1.03) !important;
        box-shadow: 0 8px 22px rgba(139,92,246,0.50), 0 0 0 1px rgba(167,139,250,0.30) !important;
    }
    .stButton > button:active { transform: translateY(0) scale(0.98) !important; }

    /* ══════════════════════════════════════
       FORM INPUTS — frosted glass
    ══════════════════════════════════════ */
    div[data-testid="stSelectbox"] label,
    div[data-testid="stDateInput"]  label,
    div[data-testid="stTextInput"]  label,
    div[data-testid="stTextArea"]   label,
    div[data-testid="stSlider"]     label {
        color: var(--text-muted) !important;
        font-size: 0.80rem !important;
        font-weight: 500 !important;
        letter-spacing: 0.03em !important;
        text-transform: uppercase !important;
        margin-bottom: 4px !important;
    }
    div[data-testid="stSelectbox"] > div > div,
    div[data-testid="stTextInput"]  > div > div > input,
    div[data-testid="stTextArea"]   > div > textarea,
    div[data-testid="stDateInput"]  > div > div > input {
        background: rgba(255,255,255,0.055) !important;
        backdrop-filter: var(--blur-sm) !important;
        border: 1px solid var(--border-soft) !important;
        border-top-color: rgba(255,255,255,0.11) !important;
        color: var(--text-main) !important;
        border-radius: var(--radius-sm) !important;
        font-size: 0.90rem !important;
        transition: border-color 0.18s ease, box-shadow 0.18s ease !important;
    }
    div[data-testid="stSelectbox"] > div > div:focus-within,
    div[data-testid="stTextInput"]  > div > div > input:focus,
    div[data-testid="stTextArea"]   > div > textarea:focus {
        border-color: var(--accent1) !important;
        box-shadow: 0 0 0 3px rgba(167,139,250,0.18) !important;
        outline: none !important;
    }

    /* ══════════════════════════════════════
       ALERTS / MESSAGES
    ══════════════════════════════════════ */
    div[data-testid="stAlert"] {
        backdrop-filter: var(--blur-sm);
        border-radius: var(--radius-sm) !important;
    }
    .stSuccess { background: rgba(52,211,153,0.11) !important; border-color: rgba(52,211,153,0.28) !important; }
    .stError   { background: rgba(239,68,68,0.10)  !important; border-color: rgba(239,68,68,0.28)  !important; }
    .stInfo    { background: rgba(96,165,250,0.10)  !important; border-color: rgba(96,165,250,0.28)  !important; }
    .stWarning { background: rgba(251,191,36,0.10)  !important; border-color: rgba(251,191,36,0.28)  !important; }

    /* ══════════════════════════════════════
       TABS
    ══════════════════════════════════════ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: transparent !important;
        border-bottom: 1px solid var(--border-soft) !important;
        padding-bottom: 6px;
    }
    .stTabs [data-baseweb="tab"] {
        background: rgba(255,255,255,0.04) !important;
        backdrop-filter: var(--blur-sm) !important;
        border: 1px solid var(--border-soft) !important;
        border-radius: var(--radius-sm) !important;
        color: var(--text-muted) !important;
        font-weight: 500 !important;
        font-size: 0.88rem !important;
        padding: 8px 22px !important;
        transition: var(--transition-f) !important;
        letter-spacing: 0.01em;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255,255,255,0.07) !important;
        color: var(--text-sub) !important;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg,
            rgba(139,92,246,0.22),
            rgba(59,130,246,0.16)) !important;
        border-color: rgba(167,139,250,0.38) !important;
        color: #c4b5fd !important;
        box-shadow: 0 0 16px rgba(139,92,246,0.22), 0 1px 0 rgba(255,255,255,0.08) inset !important;
    }

    /* ══════════════════════════════════════
       SLIDER THUMB
    ══════════════════════════════════════ */
    div[data-testid="stSlider"] [data-testid="stThumbValue"] { color: var(--accent1) !important; }
    div[data-testid="stSlider"] > div > div > div > div {
        background: linear-gradient(90deg, var(--accent1), var(--accent2)) !important;
    }

    /* ══════════════════════════════════════
       DATAFRAME
    ══════════════════════════════════════ */
    [data-testid="stDataFrame"] {
        border-radius: var(--radius-md) !important;
        overflow: hidden;
        border: 1px solid var(--border-soft) !important;
    }

    /* ══════════════════════════════════════
       EXPANDER
    ══════════════════════════════════════ */
    [data-testid="stExpander"] {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid var(--border-soft) !important;
        border-radius: var(--radius-sm) !important;
        backdrop-filter: var(--blur-sm);
    }

    /* ══════════════════════════════════════
       DIVIDER & MISC
    ══════════════════════════════════════ */
    hr {
        border: none !important;
        border-top: 1px solid var(--border-soft) !important;
        margin: 20px 0 !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 5px; height: 5px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb {
        background: rgba(167,139,250,0.30);
        border-radius: 99px;
    }
    ::-webkit-scrollbar-thumb:hover { background: rgba(167,139,250,0.55); }

    /* Spinner */
    .stSpinner > div { border-top-color: var(--accent1) !important; }

    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────
@st.cache_resource(show_spinner="Loading models…")
def load_data():
    with open("popular.pkl", "rb") as f:
        popular = pickle.load(f)
    with open("books.pkl", "rb") as f:
        books = pickle.load(f)
    with open("pt.pkl", "rb") as f:
        pt = pickle.load(f)
    with open("similarity_scores.pkl", "rb") as f:
        sim = pickle.load(f)
    return popular, books, pt, sim

popular, books, pt, sim = load_data()

# ─────────────────────────────────────────────
# Reading list persistence (JSON file)
# ─────────────────────────────────────────────
READING_LIST_FILE = "reading_list.json"

def load_reading_list():
    if os.path.exists(READING_LIST_FILE):
        with open(READING_LIST_FILE, "r") as f:
            return json.load(f)
    return []

def save_reading_list(lst):
    with open(READING_LIST_FILE, "w") as f:
        json.dump(lst, f, indent=2)

if "reading_list" not in st.session_state:
    st.session_state.reading_list = load_reading_list()

# ─────────────────────────────────────────────
# Notification Dispatcher (Triggered once per session)
# ─────────────────────────────────────────────
if "notified_today" not in st.session_state:
    st.session_state.notified_today = False

due_today = [
    b for b in st.session_state.reading_list
    if b.get("remind_date") == str(date.today()) and b.get("status") != "Completed"
]

if due_today and not st.session_state.notified_today:
    st.session_state.notified_today = True
    due_titles = [b["title"] for b in due_today]
    due_message = f"Time to read: {', '.join(due_titles[:3])}" + ("..." if len(due_titles) > 3 else "")
    
    # 1. Desktop Notification (Plyer)
    send_desktop_notification("📚 BookShelf Reminder", due_message)
    
    # 2. Browser HTML5 Notification
    components.html(f"""
        <script>
            function triggerNotification() {{
                if (!("Notification" in window)) return;
                if (Notification.permission === "granted") {{
                    new Notification("📚 BookShelf Reminder", {{
                        body: "{due_message}",
                        icon: "https://img.icons8.com/color/96/open-book.png"
                    }});
                }} else if (Notification.permission !== "denied") {{
                    Notification.requestPermission().then(permission => {{
                        if (permission === "granted") {{
                            new Notification("📚 BookShelf Reminder", {{
                                body: "{due_message}",
                                icon: "https://img.icons8.com/color/96/open-book.png"
                            }});
                        }}
                    }});
                }}
            }}
            if (Notification.permission !== "granted" && Notification.permission !== "denied") {{
                Notification.requestPermission().then(triggerNotification);
            }} else {{
                triggerNotification();
            }}
        </script>
    """, height=0, width=0)


# ─────────────────────────────────────────────
# Helper functions
# ─────────────────────────────────────────────
def recommend(book_name: str, n: int = 5):
    try:
        idx = np.where(pt.index == book_name)[0][0]
    except IndexError:
        return []
    distances = sorted(
        list(enumerate(sim[idx])),
        key=lambda x: x[1],
        reverse=True,
    )[1 : n + 1]
    results = []
    for i, score in distances:
        title = pt.index[i]
        row = books[books["Book-Title"] == title]
        if row.empty:
            continue
        row = row.iloc[0]
        results.append(
            {
                "title": title,
                "author": row["Book-Author"],
                "image": row["Image-URL-M"],
                "score": round(score, 3),
            }
        )
    return results


def reminder_status(remind_date_str: str):
    today = date.today()
    try:
        remind = date.fromisoformat(remind_date_str)
    except Exception:
        return "future", "📅 Date not set"
    delta = (remind - today).days
    if delta < 0:
        return "overdue", f"⚠️ Overdue by {abs(delta)} day(s)"
    elif delta == 0:
        return "today", "🔔 Remind Today!"
    else:
        return "future", f"📅 In {delta} day(s)"

def book_card_html(title, author, image_url, extra=""):
    safe_title = title[:45] + "…" if len(title) > 45 else title
    safe_author = author[:35] + "…" if len(author) > 35 else author
    return f"""
    <div class="book-card">
        <img src="{image_url}" alt="{safe_title}"
             onerror="this.src='https://via.placeholder.com/140x200?text=No+Cover'"/>
        <p class="book-title">{safe_title}</p>
        <p class="book-author">✍️ {safe_author}</p>
        {extra}
    </div>
    """

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style='text-align:center; padding: 12px 0 24px;'>
        <span style='font-size:3rem;'>📚</span>
        <h2 style='font-family:"Playfair Display",serif; color:#a78bfa; margin:8px 0 2px;'>BookShelf</h2>
        <p style='color:#64748b; font-size:0.82rem; margin:0;'>Your Personal Reading Hub</p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    total_books  = len(pt.index)
    total_remind = len(st.session_state.reading_list)
    due_today    = sum(1 for b in st.session_state.reading_list
                       if b.get("remind_date") == str(date.today()))

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_books}</div>
            <div class="metric-label">Books in DB</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{total_remind}</div>
            <div class="metric-label">Reading List</div>
        </div>""", unsafe_allow_html=True)

    if due_today:
        st.markdown(f"""
        <div style='margin-top:12px; background:rgba(251,191,36,0.15);
             border:1px solid rgba(251,191,36,0.35); border-radius:10px;
             padding:10px 14px; text-align:center;'>
            🔔 <b style='color:#fbbf24;'>{due_today} reminder(s) due today!</b>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        "<p style='color:#64748b; font-size:0.78rem; text-align:center;'>Built with ❤️ using Streamlit</p>",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
# HERO BANNER
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <h1 class="hero-title">📚 BookShelf</h1>
    <p class="hero-sub">Discover your next favourite read · Track your reading journey · Never miss a book</p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab_popular, tab_recommend, tab_reminder, tab_mylist = st.tabs([
    "🔥 Top Books",
    "🔍 Get Recommendations",
    "⏰ Add Reminder",
    "📋 My Reading List",
])

# ═══════════════ TAB 1 — Popular Books ═══════════════
with tab_popular:
    st.markdown('<p class="section-header">🔥 Trending & Top-Rated Books</p>', unsafe_allow_html=True)

    n_show = st.slider("Books to display", min_value=5, max_value=50, value=20, step=5, key="pop_slider")
    df_show = popular.head(n_show).reset_index(drop=True)

    cols_per_row = 5
    for row_start in range(0, len(df_show), cols_per_row):
        cols = st.columns(cols_per_row)
        for col_i, book_idx in enumerate(range(row_start, min(row_start + cols_per_row, len(df_show)))):
            row = df_show.iloc[book_idx]
            with cols[col_i]:
                extra = (f"<p class='ratings-badge' style='margin:8px 0 3px;'>Votes &nbsp;—&nbsp; {int(row['num_ratings'])}</p>"
                         f"<p class='ratings-badge'>Rating &nbsp;—&nbsp; {row['avg_ratings']:.2f}</p>")
                st.markdown(
                    book_card_html(row["Book-Title"], row["Book-Author"], row["Image-URL-M"], extra),
                    unsafe_allow_html=True,
                )
                if st.button("➕ Remind", key=f"pop_remind_{book_idx}", use_container_width=True):
                    titles = [b["title"] for b in st.session_state.reading_list]
                    if row["Book-Title"] not in titles:
                        entry = {
                            "title": row["Book-Title"],
                            "author": row["Book-Author"],
                            "image": row["Image-URL-M"],
                            "remind_date": str(date.today() + timedelta(days=7)),
                            "note": "",
                            "status": "To Read",
                            "added_on": str(date.today()),
                            "tags": ["Popular"],
                        }
                        st.session_state.reading_list.append(entry)
                        save_reading_list(st.session_state.reading_list)
                        st.success("Added! Reminder set for 7 days.")
                    else:
                        st.info("Already in your reading list!")

# ═══════════════ TAB 2 — Recommendations ═══════════════
with tab_recommend:
    st.markdown('<p class="section-header">🔍 Personalised Recommendations</p>', unsafe_allow_html=True)

    col_search, col_left, col_right = st.columns([1.5, 2, 1])
    with col_search:
        search_query = st.text_input("🔍 Search Database:", placeholder="e.g. Harry Potter", key="rec_search")
    with col_left:
        full_list = sorted(pt.index.tolist())
        if search_query:
            filtered_options = [b for b in full_list if search_query.lower() in b.lower()]
            if not filtered_options:
                st.warning("No matches found.")
                filtered_options = ["— Select a book —"]
            else:
                filtered_options = ["— Select a book —"] + filtered_options
        else:
            filtered_options = ["— Select a book —"] + full_list
        selected_book = st.selectbox("Choose a book you loved:", filtered_options, key="rec_select")
    with col_right:
        n_rec = st.slider("# Recommendations", 3, 10, 5, key="n_rec")

    if selected_book != "— Select a book —":
        recs = recommend(selected_book, n=n_rec)
        if recs:
            st.markdown(f"""
            <div style='background:rgba(167,139,250,0.10); border:1px solid rgba(167,139,250,0.20);
                 border-radius:12px; padding:14px 18px; margin-bottom:20px;'>
                📖 Because you liked <b style='color:#a78bfa;'>{selected_book}</b>, you might also enjoy:
            </div>
            """, unsafe_allow_html=True)
            max_cols = min(len(recs), 5)
            cols = st.columns(max_cols)
            for i, rec in enumerate(recs[:max_cols]):
                with cols[i]:
                    extra = f"<p class='ratings-badge' style='margin:8px 0 3px;'>Match &nbsp;—&nbsp; {rec['score']:.3f}</p>"
                    st.markdown(
                        book_card_html(rec["title"], rec["author"], rec["image"], extra),
                        unsafe_allow_html=True,
                    )
                    if st.button("➕ Remind", key=f"rec_remind_{i}", use_container_width=True):
                        titles = [b["title"] for b in st.session_state.reading_list]
                        if rec["title"] not in titles:
                            entry = {
                                "title": rec["title"],
                                "author": rec["author"],
                                "image": rec["image"],
                                "remind_date": str(date.today() + timedelta(days=7)),
                                "note": f"Recommended because you liked '{selected_book}'",
                                "status": "To Read",
                                "added_on": str(date.today()),
                                "tags": ["Recommended"],
                            }
                            st.session_state.reading_list.append(entry)
                            save_reading_list(st.session_state.reading_list)
                            st.success("Added!")
                        else:
                            st.info("Already in list!")
            # Second row if n > 5
            if len(recs) > 5:
                st.markdown("<div style='margin-bottom:15px;'></div>", unsafe_allow_html=True)
                cols2 = st.columns(min(len(recs) - 5, 5))
                for j, rec in enumerate(recs[5:]):
                    with cols2[j]:
                        extra = f"<p class='ratings-badge' style='margin:8px 0 3px;'>Match &nbsp;—&nbsp; {rec['score']:.3f}</p>"
                        st.markdown(
                            book_card_html(rec["title"], rec["author"], rec["image"], extra),
                            unsafe_allow_html=True,
                        )
                        if st.button("➕ Remind", key=f"rec_remind_{j+5}", use_container_width=True):
                            titles = [b["title"] for b in st.session_state.reading_list]
                            if rec["title"] not in titles:
                                entry = {
                                    "title": rec["title"],
                                    "author": rec["author"],
                                    "image": rec["image"],
                                    "remind_date": str(date.today() + timedelta(days=7)),
                                    "note": f"Recommended because you liked '{selected_book}'",
                                    "status": "To Read",
                                    "added_on": str(date.today()),
                                    "tags": ["Recommended"],
                                }
                                st.session_state.reading_list.append(entry)
                                save_reading_list(st.session_state.reading_list)
                                st.success("Added!")
                            else:
                                st.info("Already in list!")
        else:
            st.warning("Could not find recommendations for the selected book.")
    else:
        st.markdown("""
        <div style='text-align:center; padding:60px 20px; color:#475569;'>
            <div style='font-size:4rem;'>🔍</div>
            <p style='font-size:1.1rem; margin-top:12px;'>Search for a book above to get personalised recommendations.</p>
        </div>
        """, unsafe_allow_html=True)


# ═══════════════ TAB 3 — Add Reminder ═══════════════
with tab_reminder:
    st.markdown('<p class="section-header">⏰ Add a Book Reminder</p>', unsafe_allow_html=True)

    col_form, col_tip = st.columns([2, 1])

    with col_form:
        # Dynamic container allowing instant search updates
        st.markdown(
            "<p style='color:#94a3b8; font-size:0.9rem;'>Fill in details and set a reminder date 📅</p>",
            unsafe_allow_html=True,
        )
        db_search = st.text_input("🔍 Filter DB titles by text:", placeholder="e.g. Hobbit", key="form_search")
        full_list = sorted(pt.index.tolist())
        if db_search:
            filtered_db = [b for b in full_list if db_search.lower() in b.lower()]
            if not filtered_db:
                st.warning("No matching titles in database.")
                filtered_db = ["— Type or choose —"]
            else:
                filtered_db = ["— Type or choose —"] + filtered_db
        else:
            filtered_db = ["— Type or choose —"] + full_list

        form_book    = st.selectbox("Book Title (from DB)", filtered_db, key="form_book")
        custom_title = st.text_input("Or enter a custom title (overrides above):",
                                     placeholder="e.g. The Midnight Library")
        custom_author = st.text_input("Author:", placeholder="e.g. Matt Haig")
        remind_date  = st.date_input("Remind me on:",
                                      value=date.today() + timedelta(days=7),
                                      min_value=date.today())
        read_status  = st.selectbox("Reading Status",
                                    ["To Read", "Currently Reading", "Completed", "On Hold"])
        
        tags_selected = st.multiselect("Select Tags / Genres", 
                                       ["Fiction", "Non-Fiction", "Mystery", "Sci-Fi", "Fantasy", "Biography", "History", "Self-Help", "Classic", "Romance", "Thriller"],
                                       default=[])
        custom_tags = st.text_input("Or enter custom tags (comma separated):", placeholder="e.g. Adventure, Audio Book")
        
        note         = st.text_area("Personal Note (optional):",
                                    placeholder="Why do you want to read this?",
                                    max_chars=300, height=90)
        submitted = st.button("🔔 Set Reminder", use_container_width=True)

        if submitted:
            final_title = custom_title.strip() or (
                form_book if form_book != "— Type or choose —" else ""
            )
            if not final_title:
                st.error("Please select or enter a book title.")
            else:
                author_val = custom_author.strip()
                image_val  = "https://via.placeholder.com/140x200?text=No+Cover"
                if not author_val:
                    match = books[books["Book-Title"] == final_title]
                    if not match.empty:
                        author_val = match.iloc[0]["Book-Author"]
                        image_val  = match.iloc[0]["Image-URL-M"]

                # Parse tags
                parsed_custom = [t.strip() for t in custom_tags.split(",") if t.strip()]
                final_tags = list(set(tags_selected + parsed_custom))

                titles = [b["title"] for b in st.session_state.reading_list]
                if final_title in titles:
                    st.warning(f"**{final_title}** is already in your reading list. Go to 'My Reading List' to edit it.")
                else:
                    entry = {
                        "title": final_title,
                        "author": author_val or "Unknown",
                        "image": image_val,
                        "remind_date": str(remind_date),
                        "note": note,
                        "status": read_status,
                        "added_on": str(date.today()),
                        "tags": final_tags,
                    }
                    st.session_state.reading_list.append(entry)
                    save_reading_list(st.session_state.reading_list)
                    st.success(
                        f"✅ Reminder set for **{final_title}** on **{remind_date.strftime('%d %b %Y')}**!"
                    )

    with col_tip:
        st.markdown("""
        <div class="glass-card" style="margin-top: 52px;">
            <h4 style="color:#a78bfa; margin-top:0;">💡 Tips</h4>
            <ul style="color:#94a3b8; font-size:0.85rem; padding-left:16px; line-height:1.8;">
                <li>Choose from the dropdown for auto-fill</li>
                <li>Or enter any custom book not in the DB</li>
                <li>Set reminders for future dates</li>
                <li>Track status: To Read → Reading → Done</li>
                <li>Add personal notes for motivation</li>
            </ul>
            <hr style="border-color:rgba(255,255,255,0.08); margin:12px 0;"/>
            <p style="color:#64748b; font-size:0.78rem;">
                Reminders are saved locally and persist across sessions.
            </p>
        </div>
        """, unsafe_allow_html=True)

# ═══════════════ TAB 4 — My Reading List ═══════════════
with tab_mylist:
    st.markdown('<p class="section-header">📋 My Reading List</p>', unsafe_allow_html=True)

    reading_list = st.session_state.reading_list

    if not reading_list:
        st.markdown("""
        <div style='text-align:center; padding:80px 20px; color:#475569;'>
            <div style='font-size:4rem;'>📭</div>
            <p style='font-size:1.1rem; margin-top:16px;'>Your reading list is empty.</p>
            <p style='font-size:0.9rem;'>Browse <b>Top Books</b> or <b>Get Recommendations</b> and add reminders!</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Dynamic gathering of tags
        all_tags = set()
        for b in reading_list:
            for t in b.get("tags", []):
                all_tags.add(t)
        all_tags_list = sorted(list(all_tags))

        col_f1, col_f2, col_f2b, col_f3 = st.columns([1.5, 1.5, 1.5, 1])
        with col_f1:
            status_filter = st.multiselect(
                "Filter by Status",
                ["To Read", "Currently Reading", "Completed", "On Hold"],
                default=["To Read", "Currently Reading", "Completed", "On Hold"],
                key="rl_status_filter",
            )
        with col_f2:
            tags_filter = st.multiselect(
                "Filter by Tags / Genres",
                all_tags_list,
                default=all_tags_list,
                key="rl_tags_filter",
            )
        with col_f2b:
            sort_by = st.selectbox(
                "Sort by",
                ["Reminder Date (Earliest)", "Reminder Date (Latest)", "Added Date", "Title A-Z"],
                key="rl_sort",
            )
        with col_f3:
            view_mode = st.radio("View", ["Cards", "Table"], key="rl_view", horizontal=True)

        filtered = [b for b in reading_list if b.get("status", "To Read") in status_filter]
        
        # Tags filter
        if tags_filter:
            filtered = [b for b in filtered if any(t in tags_filter for t in b.get("tags", []))]
        elif all_tags_list:
            # If tag filtering is cleared completely, show books with no tags
            filtered = [b for b in filtered if not b.get("tags")]

        if sort_by == "Reminder Date (Earliest)":
            filtered.sort(key=lambda x: x.get("remind_date", "9999-12-31"))
        elif sort_by == "Reminder Date (Latest)":
            filtered.sort(key=lambda x: x.get("remind_date", "9999-12-31"), reverse=True)
        elif sort_by == "Added Date":
            filtered.sort(key=lambda x: x.get("added_on", ""), reverse=True)
        else:
            filtered.sort(key=lambda x: x.get("title", "").lower())

        st.markdown(
            f"<p style='color:#64748b; font-size:0.85rem;'>Showing {len(filtered)} of {len(reading_list)} entries</p>",
            unsafe_allow_html=True,
        )

        if view_mode == "Table":
            table_data = []
            for b in filtered:
                _, label = reminder_status(b.get("remind_date", str(date.today())))
                table_data.append({
                    "Title":    b["title"],
                    "Author":   b["author"],
                    "Status":   b.get("status", "To Read"),
                    "Reminder": b.get("remind_date", "—"),
                    "Due":      label,
                    "Tags":     ", ".join(b.get("tags", [])),
                    "Note":     (b.get("note") or "")[:60],
                })
            st.dataframe(pd.DataFrame(table_data), use_container_width=True, hide_index=True)

        else:
            cols_per_row = 3
            for row_start in range(0, len(filtered), cols_per_row):
                cols = st.columns(cols_per_row)
                for ci, bi in enumerate(range(row_start, min(row_start + cols_per_row, len(filtered)))):
                    book = filtered[bi]
                    status_cls, status_label = reminder_status(book.get("remind_date", str(date.today())))
                    pill_colors = {
                        "To Read": "#a78bfa",
                        "Currently Reading": "#60a5fa",
                        "Completed": "#34d399",
                        "On Hold": "#fb923c",
                    }
                    pill_c = pill_colors.get(book.get("status", "To Read"), "#94a3b8")

                    with cols[ci]:
                        note_html = ""
                        if book.get("note"):
                            note_html = f"<p style='font-size:0.75rem; color:#64748b; margin:6px 0 0; font-style:italic;'>{book['note'][:90]}{'…' if len(book['note'])>90 else ''}</p>"

                        tags_html = ""
                        if book.get("tags"):
                            tag_badges = "".join(f'<span style="background:rgba(255,255,255,0.06); color:var(--text-sub); border:1px solid var(--border-soft); border-radius:4px; font-size:0.65rem; padding:2px 6px; margin-right:5px; display:inline-block; margin-top:5px;">#{t}</span>' for t in book["tags"])
                            tags_html = f'<div style="margin-top:8px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap;">{tag_badges}</div>'

                        st.markdown(f"""
                        <div class="reminder-card {status_cls}">
                            <div style="display:flex; gap:12px; align-items:flex-start;">
                                <img src="{book['image']}"
                                     style="width:60px; border-radius:8px; flex-shrink:0;"
                                     onerror="this.src='https://via.placeholder.com/60x80?text=📖'"/>
                                <div style="flex:1; min-width:0;">
                                    <p style="font-weight:600; font-size:0.88rem; margin:0 0 3px;
                                               color:#e2e8f0; white-space:nowrap; overflow:hidden;
                                               text-overflow:ellipsis;" title="{book['title']}">
                                        {book['title'][:40]}{'…' if len(book['title'])>40 else ''}
                                    </p>
                                    <p style="font-size:0.78rem; color:#60a5fa; margin:0 0 8px;">
                                        ✍️ {book['author'][:32]}
                                    </p>
                                    <div style="display:flex; flex-wrap:wrap; gap:4px; align-items:center;">
                                        <span style="background:{pill_c}20; color:{pill_c};
                                                     border:1px solid {pill_c}40; border-radius:6px;
                                                     font-size:0.70rem; padding:2px 8px; font-weight:600;">
                                            {book.get('status','To Read')}
                                        </span>
                                    </div>
                                    {tags_html}
                                </div>
                            </div>
                            <p style="font-size:0.80rem; color:#94a3b8; margin:10px 0 2px;">{status_label}</p>
                            {note_html}
                        </div>
                        """, unsafe_allow_html=True)

                        btn_col1, btn_col2 = st.columns(2)
                        with btn_col1:
                            st.button("✏️ Edit", key=f"edit_{bi}", use_container_width=True)
                        with btn_col2:
                            if st.button("🗑️ Remove", key=f"del_{bi}", use_container_width=True):
                                st.session_state.reading_list = [
                                    b for b in st.session_state.reading_list
                                    if b["title"] != book["title"]
                                ]
                                save_reading_list(st.session_state.reading_list)
                                st.rerun()

                        if st.session_state.get(f"edit_{bi}"):
                            with st.expander("✏️ Edit Entry", expanded=True):
                                new_status = st.selectbox(
                                    "Status",
                                    ["To Read", "Currently Reading", "Completed", "On Hold"],
                                    index=["To Read", "Currently Reading", "Completed", "On Hold"].index(
                                        book.get("status", "To Read")
                                    ),
                                    key=f"es_{bi}",
                                )
                                new_remind = st.date_input(
                                    "Reminder Date",
                                    value=date.fromisoformat(book.get("remind_date", str(date.today()))),
                                    key=f"er_{bi}",
                                )
                                current_tags = book.get("tags", [])
                                new_tags = st.multiselect(
                                    "Tags",
                                    list(set(["Fiction", "Non-Fiction", "Mystery", "Sci-Fi", "Fantasy", "Biography", "History", "Self-Help", "Classic", "Romance", "Thriller"] + current_tags)),
                                    default=current_tags,
                                    key=f"et_{bi}",
                                )
                                new_custom_tags = st.text_input("Add Custom Tags (comma separated):", key=f"etc_{bi}")
                                new_note = st.text_area("Note", value=book.get("note", ""),
                                                        key=f"en_{bi}", height=70)
                                if st.button("💾 Save", key=f"save_{bi}", use_container_width=True):
                                    parsed_custom = [t.strip() for t in new_custom_tags.split(",") if t.strip()]
                                    final_tags = list(set(new_tags + parsed_custom))
                                    for b in st.session_state.reading_list:
                                        if b["title"] == book["title"]:
                                            b["status"]      = new_status
                                            b["remind_date"] = str(new_remind)
                                            b["note"]        = new_note
                                            b["tags"]        = final_tags
                                    save_reading_list(st.session_state.reading_list)
                                    st.rerun()

        st.markdown("---")
        col_clear, _ = st.columns([1, 4])
        with col_clear:
            if st.button("🗑️ Clear Entire List", type="secondary"):
                st.session_state.reading_list = []
                save_reading_list([])
                st.rerun()
