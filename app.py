import streamlit as st
import numpy as np
from PIL import Image
import io
import matplotlib.pyplot as plt
import hashlib

from elgamal import ElGamalDH
from steganography import LSBSteganography
import importlib
import analysis
importlib.reload(analysis)
from analysis import (plot_histogram_comparison, plot_histogram_difference, 
                      plot_difference_heatmap, plot_chi_square_analysis,
                      simulate_jpeg_compression, calculate_statistical_metrics, close_figure)
import reedsolo

# ------------------------------------------------------------
# PAGE CONFIGURATION
# ------------------------------------------------------------
st.set_page_config(
    page_title="StegoCipher — Ancient Egyptian Cryptographic Sanctuary",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ------------------------------------------------------------
# CUSTOM DESIGN SYSTEM: ANCIENT EGYPTIAN RUINS × MODERN CRYPTOGRAPHY
# ------------------------------------------------------------
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;700;800;900&family=Outfit:wght@500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        /* Core Palette: Ancient Egyptian Ruins */
        --bg: #13110E;
        --surface: #1E1A15;
        --surface-ground: #13110E;
        --surface-card: #201B15;
        --surface-low: #171410;
        --surface-high: #2A241D;
        --surface-elevated: #332B22;
        
        /* Stone Masonry & Borders */
        --border: #3D3428;
        --border-subtle: #2A241C;
        --border-light: #524637;
        
        /* Sandstone & Gold */
        --sandstone: #C6A66B;
        --sandstone-light: #D8BC82;
        --gold: #B9964F;
        --gold-light: #D0AE62;
        --gold-soft: rgba(208, 174, 98, 0.12);
        --gold-glow: rgba(208, 174, 98, 0.22);
        
        /* Papyrus & Reading Surfaces */
        --papyrus: #F1E6C8;
        --papyrus-dark: #E8D9B5;
        --papyrus-muted: #D1C3A3;
        
        /* Deep Stone / Obsidian */
        --obsidian: #171512;
        --obsidian-card: #24201A;
        --obsidian-high: #302A21;
        
        /* Lapis Lazuli (Secondary Accent) */
        --lapis: #214C70;
        --lapis-hover: #2E6388;
        --lapis-light: #3D7EA8;
        --lapis-soft: rgba(33, 76, 112, 0.22);
        --lapis-border: rgba(46, 99, 136, 0.45);
        
        /* Egyptian Turquoise (Status / Success / Highlight) */
        --turquoise: #2F7F78;
        --turquoise-hover: #3C9A91;
        --turquoise-soft: rgba(47, 127, 120, 0.16);
        --turquoise-border: rgba(60, 154, 145, 0.4);
        
        /* Muted Copper & Red Jasper (Warning / Error) */
        --copper: #9A6844;
        --copper-light: #B17B52;
        --copper-soft: rgba(177, 123, 82, 0.18);
        --jasper-red: #C25B45;
        --jasper-soft: rgba(194, 91, 69, 0.18);
        
        /* Neutral Typography */
        --text: #F1E6C8;
        --text-secondary: #D8BC82;
        --muted: #A3937F;
        --muted-light: #736758;
    }

    * {
        box-sizing: border-box;
    }

    html, body, [class*="css"] {
        font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        background-color: var(--bg);
        color: var(--text);
    }

    /* Atmospheric Stone Background Texture with Subtle Architectural Vignette */
    .stApp {
        background-color: var(--bg);
        background-image: 
            radial-gradient(circle at 50% 0%, rgba(198, 166, 107, 0.05) 0%, transparent 60%),
            radial-gradient(circle at 100% 100%, rgba(33, 76, 112, 0.04) 0%, transparent 50%),
            linear-gradient(180deg, #16130F 0%, #13110E 40%, #0E0C0A 100%);
        background-attachment: fixed;
        color: var(--text);
    }

    /* Streamlit Chrome Styling */
    [data-testid="stHeader"] {
        background: transparent !important;
        color: var(--text) !important;
        z-index: 1001 !important;
        height: 54px !important;
        pointer-events: none !important;
    }

    [data-testid="stToolbar"] {
        background: transparent !important;
        pointer-events: none !important;
        visibility: visible !important;
        display: flex !important;
        height: 54px !important;
        padding-left: 10px !important;
    }

    [data-testid="stToolbar"] > div:last-child:not(:first-child),
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    [data-testid="stMainMenu"] {
        display: none !important;
    }

    [data-testid="stExpandSidebarButton"],
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"] {
        pointer-events: auto !important;
        visibility: visible !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        z-index: 1002 !important;
    }

    [data-testid="stExpandSidebarButton"] {
        position: fixed !important;
        top: 6px !important;
        left: 10px !important;
        z-index: 1002 !important;
    }

    [data-testid="stExpandSidebarButton"] button,
    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="collapsedControl"] button {
        background: var(--obsidian-card) !important;
        border: 1px solid var(--border) !important;
        color: var(--sandstone) !important;
        border-radius: 6px !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.5) !important;
        width: 44px !important;
        height: 44px !important;
        min-width: 44px !important;
        min-height: 44px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
    }

    [data-testid="stExpandSidebarButton"] button:hover,
    [data-testid="stSidebarCollapseButton"] button:hover,
    [data-testid="collapsedControl"] button:hover {
        background: var(--surface-high) !important;
        border-color: var(--sandstone) !important;
        color: var(--gold-light) !important;
    }

    [data-testid="stExpandSidebarButton"] svg,
    [data-testid="stSidebarCollapseButton"] svg,
    [data-testid="collapsedControl"] svg {
        fill: var(--sandstone) !important;
        stroke: var(--sandstone) !important;
        color: var(--sandstone) !important;
        width: 20px !important;
        height: 20px !important;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 4.8rem;
        padding-bottom: 4.5rem;
        padding-left: 2rem;
        padding-right: 2rem;
    }

    /* Headings with Archaeological Inscription Font (Cinzel) */
    h1, h2, h3, h4, .cinzel-title {
        font-family: "Cinzel", Georgia, serif !important;
        color: var(--papyrus) !important;
        font-weight: 700;
        letter-spacing: 0.03em;
    }

    p, span, label, div {
        color: var(--text);
    }

    .mono {
        font-family: "JetBrains Mono", monospace !important;
        font-variant-numeric: tabular-nums;
    }

    /* ---------------- TOPBAR NAVIGATION ---------------- */
    .topbar {
        position: fixed;
        z-index: 99;
        top: 0;
        left: 0;
        right: 0;
        height: 54px;
        padding-left: 64px;
        padding-right: 2rem;
        background: rgba(19, 17, 14, 0.95);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border-bottom: 1px solid var(--border);
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.4);
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: padding-left 0.3s ease;
    }

    @media (min-width: 769px) {
        .stApp:has(section[data-testid="stSidebar"][aria-expanded="true"]) .topbar {
            padding-left: 310px;
        }
    }

    .topbar-left {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .topbar-title {
        font-family: "Cinzel", Georgia, serif;
        font-size: 0.95rem;
        font-weight: 700;
        color: var(--sandstone-light);
        letter-spacing: 0.05em;
    }

    .topbar-sep {
        color: var(--muted-light);
        font-size: 0.8rem;
    }

    .topbar-sub {
        font-family: "Inter", sans-serif;
        font-size: 0.82rem;
        color: var(--muted);
    }

    .topbar-badge {
        font-family: "JetBrains Mono", monospace;
        font-size: 0.7rem;
        font-weight: 600;
        padding: 0.25rem 0.75rem;
        border-radius: 4px;
        background: var(--turquoise-soft);
        border: 1px solid var(--turquoise-border);
        color: var(--turquoise-hover);
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        letter-spacing: 0.04em;
    }

    .topbar-badge-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background-color: var(--turquoise-hover);
        box-shadow: 0 0 6px var(--turquoise-hover);
    }

    /* ---------------- TEMPLE HERO PORTAL ---------------- */
    .hero-container {
        margin-bottom: 2.2rem;
        padding: 2rem 2.2rem;
        background: linear-gradient(135deg, rgba(30, 26, 21, 0.95) 0%, rgba(23, 20, 16, 0.98) 100%);
        border: 1px solid var(--border);
        border-top: 2px solid var(--sandstone);
        border-radius: 8px;
        box-shadow: 0 6px 24px rgba(0, 0, 0, 0.45), inset 0 1px 0 rgba(216, 188, 130, 0.1);
        position: relative;
        overflow: hidden;
    }

    /* Subtle temple architectural corner motif */
    .hero-container::before {
        content: "";
        position: absolute;
        top: 0;
        right: 0;
        width: 120px;
        height: 120px;
        background: radial-gradient(circle at top right, rgba(198, 166, 107, 0.12), transparent 70%);
        pointer-events: none;
    }

    .hero-tagline {
        font-family: "JetBrains Mono", monospace;
        font-size: 0.72rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: var(--sandstone);
        margin-bottom: 0.65rem;
        display: inline-flex;
        align-items: center;
        gap: 0.45rem;
    }

    .hero-title {
        font-family: "Cinzel", Georgia, serif;
        font-size: 2rem;
        font-weight: 800;
        margin: 0 0 0.85rem 0;
        color: var(--papyrus);
        letter-spacing: 0.02em;
        line-height: 1.25;
    }

    .hero-accent {
        color: var(--sandstone-light);
        background: linear-gradient(135deg, #F1E6C8 0%, #D8BC82 50%, #B9964F 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-desc {
        color: var(--papyrus-muted);
        font-size: 0.88rem;
        line-height: 1.7;
        margin: 0 0 1.35rem 0;
        max-width: 920px;
    }

    .hero-chips {
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
    }

    .hero-chip {
        font-family: "JetBrains Mono", monospace;
        font-size: 0.72rem;
        font-weight: 500;
        padding: 0.3rem 0.75rem;
        border-radius: 4px;
        background: var(--obsidian);
        border: 1px solid var(--border);
        color: var(--text-secondary);
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
    }

    .hero-chip strong {
        color: var(--sandstone);
    }

    /* ---------------- SIDEBAR (SANCTUARY CONTROL) ---------------- */
    section[data-testid="stSidebar"] {
        background-color: var(--obsidian) !important;
        border-right: 1px solid var(--border);
        z-index: 100;
    }

    section[data-testid="stSidebar"] > div {
        padding: 1.4rem 1.25rem;
    }

    .brand-wrap {
        padding-bottom: 1.2rem;
        border-bottom: 1px solid var(--border);
        margin-bottom: 1.35rem;
    }

    .brand-title {
        font-family: "Cinzel", Georgia, serif !important;
        font-size: 1.28rem;
        font-weight: 800;
        letter-spacing: 0.06em;
        color: var(--papyrus) !important;
        display: flex;
        align-items: center;
        gap: 0.45rem;
    }

    .brand-accent {
        color: var(--sandstone-light) !important;
    }

    .brand-subtitle {
        color: var(--muted);
        font-size: 0.76rem;
        margin-top: 0.35rem;
        font-family: "Inter", sans-serif;
        letter-spacing: 0.02em;
    }

    .sidebar-section-title {
        font-family: "Cinzel", Georgia, serif;
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--sandstone);
        margin-bottom: 0.6rem;
    }

    .param-box {
        background: var(--surface-low);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.85rem;
        font-size: 0.82rem;
        box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.4);
        transition: border-color 0.25s ease;
    }

    .param-box:hover {
        border-color: var(--sandstone);
    }

    .param-label {
        font-family: "Cinzel", Georgia, serif;
        font-size: 0.74rem;
        color: var(--sandstone);
        letter-spacing: 0.03em;
        font-weight: 700;
    }

    .param-val {
        font-family: "JetBrains Mono", monospace;
        font-size: 0.78rem;
        color: var(--papyrus);
        word-break: break-all;
        margin-top: 0.3rem;
        line-height: 1.5;
        font-variant-numeric: tabular-nums;
    }

    /* ---------------- CARDS & TEMPLE BLOCKS ---------------- */
    .stego-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-top: 2px solid var(--sandstone);
        border-radius: 8px;
        padding: 1.45rem 1.65rem;
        box-shadow: 0 4px 18px rgba(0, 0, 0, 0.35);
        margin-bottom: 1.35rem;
        transition: border-color 0.25s ease;
    }

    .stego-card:hover {
        border-color: var(--sandstone);
    }

    .card-title {
        font-family: "Cinzel", Georgia, serif !important;
        font-size: 1.16rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        color: var(--papyrus) !important;
    }

    .card-subtitle {
        margin-top: 0.4rem;
        color: var(--papyrus-muted);
        font-size: 0.84rem;
        line-height: 1.65;
    }

    .notice-box {
        margin-top: 0.95rem;
        padding: 0.85rem 1.1rem;
        background: var(--surface-low);
        border: 1px solid var(--border);
        border-left: 3px solid var(--lapis-light);
        border-radius: 6px;
        font-size: 0.84rem;
        color: var(--papyrus-dark);
        line-height: 1.6;
        display: flex;
        gap: 0.85rem;
        align-items: flex-start;
    }

    .notice-icon {
        font-weight: 700;
        font-size: 1rem;
        color: var(--sandstone);
        flex-shrink: 0;
        line-height: 1.2;
    }

    .badge-tag {
        font-family: "JetBrains Mono", monospace;
        font-size: 0.72rem;
        font-weight: 600;
        padding: 0.28rem 0.75rem;
        border-radius: 4px;
        letter-spacing: 0.04em;
    }

    .badge-success {
        background: var(--turquoise-soft);
        color: var(--turquoise-hover);
        border: 1px solid var(--turquoise-border);
    }

    /* ---------------- STONE TABLET TABS ---------------- */
    [data-testid="stTabs"] {
        margin-top: 1rem;
    }

    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        background-color: var(--obsidian);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 5px;
        gap: 6px;
    }

    [data-testid="stTabs"] [data-baseweb="tab"] {
        border-radius: 6px !important;
        font-family: "Cinzel", Georgia, serif !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
        color: var(--muted) !important;
        padding: 0.65rem 1.7rem !important;
        border: 1px solid transparent !important;
        background: transparent !important;
        letter-spacing: 0.04em !important;
        transition: all 0.25s ease !important;
    }

    [data-testid="stTabs"] [data-baseweb="tab"]:hover {
        color: var(--papyrus) !important;
        background: var(--surface-high) !important;
    }

    [data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
        background: var(--surface) !important;
        border: 1px solid var(--sandstone) !important;
        color: var(--sandstone-light) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(216, 188, 130, 0.15) !important;
    }

    /* ---------------- FORM & BUTTONS ---------------- */
    [data-testid="stFileUploader"] {
        margin-bottom: 0.65rem;
    }

    [data-testid="stFileUploaderDropzone"] {
        padding: 2rem 1.4rem !important;
        background-color: var(--surface-low) !important;
        border: 1.5px dashed var(--sandstone) !important;
        border-radius: 8px !important;
        transition: all 0.25s ease !important;
    }

    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: var(--gold-light) !important;
        background-color: rgba(198, 166, 107, 0.06) !important;
        box-shadow: 0 0 12px rgba(198, 166, 107, 0.12) !important;
    }

    [data-testid="stFileUploaderDropzone"] div {
        color: var(--papyrus) !important;
    }

    [data-testid="stFileUploaderDropzone"] small {
        color: var(--muted) !important;
        font-family: "Inter", sans-serif !important;
        font-size: 0.78rem !important;
    }

    [data-testid="stFileUploaderDropzone"] button {
        background: var(--obsidian-card) !important;
        color: var(--papyrus) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        font-size: 0.84rem !important;
        min-height: 40px !important;
        font-weight: 500 !important;
        font-family: "Outfit", sans-serif !important;
        transition: all 0.25s ease !important;
    }

    [data-testid="stFileUploaderDropzone"] button:hover {
        border-color: var(--sandstone) !important;
        color: var(--sandstone-light) !important;
        background: var(--surface-high) !important;
    }

    [data-testid="stWidgetLabel"] p {
        color: var(--text-secondary) !important;
        font-family: "Cinzel", Georgia, serif !important;
        font-size: 0.82rem !important;
        letter-spacing: 0.03em !important;
        font-weight: 700 !important;
    }

    /* Primary Button: Sandstone / Gold Ingot */
    .stButton > button {
        border-radius: 6px !important;
        min-height: 46px !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        font-family: "Cinzel", Georgia, serif !important;
        transition: all 0.25s ease !important;
        letter-spacing: 0.04em !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #D0AE62 0%, #B9964F 100%) !important;
        border: 1px solid #D8BC82 !important;
        color: #171512 !important;
        box-shadow: 0 3px 12px rgba(185, 150, 79, 0.3) !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #E8D9B5 0%, #D0AE62 100%) !important;
        border-color: #F1E6C8 !important;
        color: #0E0C0A !important;
        box-shadow: 0 4px 18px rgba(208, 174, 98, 0.45) !important;
        transform: translateY(-1px) !important;
    }

    .stButton > button[kind="secondary"] {
        background: var(--obsidian-card) !important;
        border: 1px solid var(--border) !important;
        color: var(--papyrus) !important;
    }

    .stButton > button[kind="secondary"]:hover {
        border-color: var(--lapis-hover) !important;
        color: var(--papyrus) !important;
        background: var(--lapis) !important;
    }

    /* Download Button: Lapis Lazuli with Gold Border */
    .stDownloadButton > button {
        background: linear-gradient(135deg, #2E6388 0%, #214C70 100%) !important;
        border: 1px solid var(--sandstone) !important;
        color: #F1E6C8 !important;
        border-radius: 6px !important;
        min-height: 46px !important;
        font-weight: 700 !important;
        font-size: 0.9rem !important;
        font-family: "Cinzel", Georgia, serif !important;
        letter-spacing: 0.04em !important;
        transition: all 0.25s ease !important;
        box-shadow: 0 3px 12px rgba(33, 76, 112, 0.4) !important;
    }

    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #3D7EA8 0%, #2E6388 100%) !important;
        border-color: #F1E6C8 !important;
        color: #ffffff !important;
        box-shadow: 0 4px 18px rgba(46, 99, 136, 0.5) !important;
        transform: translateY(-1px) !important;
    }

    .stTextArea textarea, .stTextInput input {
        font-family: "JetBrains Mono", monospace !important;
        background: var(--surface) !important;
        color: var(--papyrus) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        font-size: 0.85rem !important;
        transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
    }

    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: var(--sandstone) !important;
        box-shadow: 0 0 0 1px var(--sandstone) !important;
    }

    /* Metrics Grid in Archaeological Stone Block */
    [data-testid="stMetric"] {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-top: 2px solid var(--sandstone) !important;
        border-radius: 6px !important;
        padding: 1.1rem 1.25rem !important;
        transition: border-color 0.25s ease !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3) !important;
    }

    [data-testid="stMetric"]:hover {
        border-color: var(--sandstone-light) !important;
    }

    [data-testid="stMetricLabel"] p {
        font-family: "Cinzel", Georgia, serif !important;
        font-size: 0.8rem !important;
        color: var(--sandstone) !important;
        font-weight: 700 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
    }

    [data-testid="stMetricValue"] div {
        font-family: "JetBrains Mono", monospace !important;
        font-size: 1.45rem !important;
        font-weight: 700 !important;
        color: var(--papyrus) !important;
        font-variant-numeric: tabular-nums !important;
    }

    [data-testid="stAlert"] {
        background-color: var(--surface-low) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        color: var(--papyrus) !important;
    }

    .footer-wrap {
        margin-top: 4.5rem;
        padding-top: 1.8rem;
        border-top: 1px solid var(--border);
        text-align: center;
        font-size: 0.82rem;
        color: var(--muted);
    }

    .stone-divider {
        height: 1px;
        background: var(--border);
        margin: 1.3rem 0;
    }

    /* Archaeological Pipeline Flow Stepper */
    .pipeline-container {
        display: flex;
        align-items: center;
        justify-content: flex-start;
        background: var(--obsidian);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 0.85rem 1.15rem;
        margin-bottom: 1.35rem;
        flex-wrap: wrap;
        gap: 0.7rem 0.95rem;
    }

    .pipeline-step {
        display: flex;
        align-items: center;
        gap: 0.55rem;
    }

    .pipeline-num {
        font-family: "Cinzel", Georgia, serif;
        font-size: 0.76rem;
        font-weight: 800;
        width: 24px;
        height: 24px;
        border-radius: 4px;
        background: var(--lapis-soft);
        border: 1px solid var(--lapis-border);
        color: var(--sandstone-light);
        display: inline-flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }

    .pipeline-label {
        font-size: 0.82rem;
        color: var(--papyrus);
        font-weight: 600;
        letter-spacing: 0.02em;
    }

    .pipeline-arrow {
        color: var(--sandstone);
        font-size: 0.9rem;
    }

    /* Sandstone Capacity Gauge */
    .capacity-gauge {
        background: var(--surface-low);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 0.8rem 0.95rem;
        margin-top: 0.65rem;
        margin-bottom: 0.85rem;
    }

    .gauge-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }

    .gauge-track {
        height: 7px;
        background: var(--obsidian);
        border-radius: 3px;
        overflow: hidden;
        border: 1px solid var(--border);
    }

    .gauge-fill {
        height: 100%;
        background: linear-gradient(90deg, var(--lapis-light) 0%, var(--sandstone) 100%);
        border-radius: 3px;
        transition: width 0.3s ease;
    }

    .gauge-fill-full {
        background: var(--jasper-red) !important;
    }

    /* Temple Inscription Inspector Details */
    .inspector-box {
        background: var(--surface-low);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 1.2rem;
        margin-top: 0.85rem;
        font-size: 0.82rem;
    }

    .inspector-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 0.85rem;
        margin-top: 0.75rem;
    }

    .inspector-item {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 0.75rem 0.95rem;
        transition: border-color 0.25s ease;
    }

    .inspector-item:hover {
        border-color: var(--sandstone);
    }

    .inspector-label {
        font-family: "Cinzel", Georgia, serif;
        font-size: 0.74rem;
        color: var(--sandstone);
        letter-spacing: 0.03em;
        font-weight: 700;
    }

    .inspector-val {
        font-family: "JetBrains Mono", monospace;
        font-size: 0.78rem;
        color: var(--papyrus);
        word-break: break-all;
        margin-top: 0.3rem;
        line-height: 1.5;
        font-variant-numeric: tabular-nums;
    }

    [data-testid="stExpander"] {
        border: 1px solid var(--border) !important;
        border-radius: 8px !important;
        background: var(--surface) !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3) !important;
    }

    [data-testid="stExpander"] summary {
        font-family: "Cinzel", Georgia, serif !important;
        font-weight: 700 !important;
        color: var(--papyrus) !important;
        letter-spacing: 0.03em !important;
    }

    .stSlider [data-baseweb="slider"] [role="slider"] {
        background: var(--sandstone) !important;
    }

    .stSlider [data-baseweb="slider"] div[data-testid="stTickBar"] {
        background: var(--sandstone) !important;
    }

    [data-testid="stSelectSlider"] {
        color: var(--papyrus) !important;
    }

    [data-testid="stImage"] > div > div > p {
        font-family: "Inter", sans-serif !important;
        font-size: 0.78rem !important;
        color: var(--sandstone) !important;
    }

    .field-btn-align {
        margin-top: 1.7rem;
    }

    .form-section-label {
        font-family: "Cinzel", Georgia, serif;
        font-size: 0.88rem;
        font-weight: 700;
        color: var(--sandstone);
        margin-bottom: 0.5rem;
        letter-spacing: 0.03em;
    }

    /* Accessibility Focus Ring in Sandstone Gold */
    *:focus-visible {
        outline: 2px solid var(--sandstone) !important;
        outline-offset: 2px !important;
    }

    .stButton > button:focus-visible,
    .stDownloadButton > button:focus-visible {
        outline: 2px solid var(--sandstone-light) !important;
        outline-offset: 2px !important;
        box-shadow: 0 0 0 4px var(--gold-soft) !important;
    }

    [data-testid="stFileUploaderDropzone"]:focus-within {
        border-color: var(--sandstone) !important;
        box-shadow: 0 0 0 2px var(--gold-soft) !important;
    }

    .stTextArea textarea:focus-visible,
    .stTextInput input:focus-visible {
        outline: none !important;
        border-color: var(--sandstone) !important;
        box-shadow: 0 0 0 2px var(--gold-soft) !important;
    }

    .stButton > button:active,
    .stDownloadButton > button:active {
        transform: translateY(1px) !important;
    }

    html {
        scroll-behavior: smooth;
    }

    /* Responsive Architecture (antislop-layoutmobile) */
    @media (max-width: 768px) {
        .block-container {
            padding-top: 4.4rem !important;
            padding-bottom: 2.5rem !important;
            padding-left: 1.1rem !important;
            padding-right: 1.1rem !important;
        }

        .topbar {
            padding-left: 60px !important;
            padding-right: 1rem !important;
        }

        .topbar-sub, .topbar-sep {
            display: none !important;
        }

        .hero-title {
            font-size: 1.5rem !important;
        }

        .field-btn-align {
            margin-top: 0 !important;
        }

        .pipeline-container {
            flex-direction: column;
            align-items: flex-start;
            gap: 0.45rem;
        }

        .pipeline-arrow {
            display: none !important;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# TOPBAR NAVIGATION
# ------------------------------------------------------------
st.markdown(
    """
    <nav class="topbar" aria-label="Navigasi Utama">
        <div class="topbar-left">
            <span class="topbar-title">&#9889; KHNUM &bull; STEGOCIPHER</span>
            <span class="topbar-sep">/</span>
            <span class="topbar-sub">Ancient Egyptian Cryptographic Sanctuary</span>
        </div>
        <div class="topbar-badge">
            <span class="topbar-badge-dot"></span>
            <span>SANCTUARY SECURE &bull; 1024-BIT</span>
        </div>
    </nav>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# TEMPLE HERO PORTAL
# ------------------------------------------------------------
st.markdown(
    """
    <header class="hero-container" role="banner">
        <div class="hero-tagline">
            <span>&#9670;</span>
            <span>Santuari Kriptografi Kuno &bull; Keamanan Informasi</span>
            <span>&#9670;</span>
        </div>
        <h1 class="hero-title">
            Steganografi Citra Digital dengan Enkripsi <span class="hero-accent">ElGamal</span> berbasis Diffie-Hellman
        </h1>
        <p class="hero-desc">
            Sistem transmisi rahasia berkekuatan tinggi yang menggabungkan kesakralan perlindungan informasi peradaban kuno dengan sains kriptografi modern: pertukaran kunci Diffie-Hellman 1024-bit, enkripsi asimetris ElGamal, proteksi integritas Reed-Solomon RS(255,223), serta penyisipan spasial LSB teracak berbasis Pseudo-Random Number Generator (PRNG).
        </p>
        <div class="hero-chips">
            <span class="hero-chip"><strong>Kriptografi:</strong> ElGamal Asimetris</span>
            <span class="hero-chip"><strong>Pertukaran Kunci:</strong> Diffie-Hellman 1024-bit</span>
            <span class="hero-chip"><strong>Koreksi Galat:</strong> Reed-Solomon RS(255,223)</span>
            <span class="hero-chip"><strong>Steganografi:</strong> Spatial LSB-PRNG</span>
        </div>
    </header>
    """,
    unsafe_allow_html=True,
)

# ------------------------------------------------------------
# CRYPTOGRAPHIC ENGINE INITIALIZATION
# ------------------------------------------------------------
@st.cache_resource
def get_elgamal_instance():
    """Menginisialisasi instance ElGamalDH dengan safe prime 1024-bit."""
    return ElGamalDH()

# Inisialisasi session state inti
if 'elgamal' not in st.session_state:
    st.session_state.elgamal = get_elgamal_instance()
if 'private_key' not in st.session_state:
    st.session_state.private_key, st.session_state.public_key = st.session_state.elgamal.generate_keypair()

# ------------------------------------------------------------
# SIDEBAR SANCTUARY CONTROL
# ------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
        <div class="brand-wrap">
            <div class="brand-title">
                <span>STEGO</span><span class="brand-accent">CIPHER</span>
            </div>
            <div class="brand-subtitle">Egyptian Cryptographic Relic &bull; LSB-PRNG</div>
        </div>
        <div class="sidebar-section-title">Parameter Modulus Kuil</div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        f"""
        <div class="param-box">
            <div class="param-label">Prime Modulus (p) &bull; 1024 bit</div>
            <div class="param-val">{st.session_state.elgamal.p}</div>
            <div class="param-label" style="margin-top:0.55rem;">Generator Kuil (g)</div>
            <div class="param-val">{st.session_state.elgamal.g}</div>
        </div>

        <div class="sidebar-section-title" style="margin-top:1rem;">Pasangan Kunci Suci</div>
        <div class="param-box">
            <div class="param-label">Private Key (x) &bull; Rahasia Santuari</div>
            <div class="param-val">{st.session_state.private_key}</div>
            <div class="param-label" style="margin-top:0.55rem;">Public Key (y) &bull; Kunci Terbuka</div>
            <div class="param-val">{st.session_state.public_key}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("Bangkitkan Kunci Baru", type="secondary", use_container_width=True):
        st.cache_resource.clear()
        st.session_state.elgamal = get_elgamal_instance()
        st.session_state.private_key, st.session_state.public_key = st.session_state.elgamal.generate_keypair()
        st.success("Pasangan kunci kriptografi kuil berhasil dibangkitkan ulang!")
        st.rerun()

    st.markdown(
        """
        <div style="margin-top:2.6rem; padding-top:1.1rem; border-top:1px solid var(--border); font-size:0.74rem; color:var(--muted);">
            <div style="font-family:'Cinzel', Georgia, serif; font-size:0.7rem; font-weight:700; text-transform:uppercase; letter-spacing:0.08em; color:var(--sandstone);">Keamanan Informasi</div>
            <div style="color:var(--muted); font-size:0.7rem; margin-top:0.25rem;">Semester 5 &bull; Ujian Tengah Semester</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ------------------------------------------------------------
# MAIN APPLICATION TABS
# ------------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["Enkripsi & Penyisipan", "Ekstraksi & Dekripsi", "Analisis Citra & Keamanan"])

# ============================================================
# TAB 1: ENKRIPSI & PENYISIPAN
# ============================================================
with tab1:
    st.markdown(
        """
        <div class="stego-card">
            <div class="card-title">Penyembunyian Pesan Rahasia ke dalam Relief Citra</div>
            <div class="card-subtitle">Unggah citra cover asli pembawa pesan, masukkan inskripsi rahasia, dan tentukan stego seed PRNG untuk melakukan enkripsi ElGamal serta penyisipan bit LSB teracak.</div>
        </div>
        <div class="pipeline-container">
            <div class="pipeline-step">
                <span class="pipeline-num">I</span>
                <span class="pipeline-label">Inskripsi Plaintext</span>
            </div>
            <span class="pipeline-arrow">&rarr;</span>
            <div class="pipeline-step">
                <span class="pipeline-num">II</span>
                <span class="pipeline-label">Sandi ElGamal (c1, c2)</span>
            </div>
            <span class="pipeline-arrow">&rarr;</span>
            <div class="pipeline-step">
                <span class="pipeline-num">III</span>
                <span class="pipeline-label">Reed-Solomon ECC</span>
            </div>
            <span class="pipeline-arrow">&rarr;</span>
            <div class="pipeline-step">
                <span class="pipeline-num">IV</span>
                <span class="pipeline-label">Penyisipan LSB-PRNG</span>
            </div>
            <span class="pipeline-arrow">&rarr;</span>
            <div class="pipeline-step">
                <span class="pipeline-num">V</span>
                <span class="pipeline-label">Artefak Stego Tersegel</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(
            """
            <div class="form-section-label">
                Citra Cover (Artefak Dinding Asli)
            </div>
            """,
            unsafe_allow_html=True,
        )
        cover_file = st.file_uploader("Upload Citra Cover", type=['png', 'jpg', 'jpeg', 'bmp'], key="cover_uploader")
        
        capacity = 0
        cover_array = None
        if cover_file:
            cover_image = Image.open(cover_file)
            cover_array = np.array(cover_image)
            
            if len(cover_array.shape) == 2:
                cover_array = np.stack([cover_array] * 3, axis=2)
            elif cover_array.shape[2] == 4:
                cover_array = cover_array[:, :, :3]
            
            st.image(cover_image, caption=f"Artefak Cover Asli ({cover_array.shape[1]}x{cover_array.shape[0]} px)", use_container_width=True)
            stego_calc = LSBSteganography()
            capacity = stego_calc.calculate_capacity(cover_array)
            st.markdown(
                f"""
                <div class="notice-box">
                    <span class="notice-icon">&#10022;</span>
                    <span><strong>Daya Muat Relief Citra:</strong> {capacity:,} bytes ({capacity * 8:,} bit LSB)</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col2:
        st.markdown(
            """
            <div class="form-section-label">
                Inskripsi Rahasia (Plaintext)
            </div>
            """,
            unsafe_allow_html=True,
        )
        message = st.text_area("Inskripsi Pesan", height=130, placeholder="Tuliskan inskripsi pesan rahasia yang hendak disembunyikan ke dalam hieroglif citra...", key="msg_input")
        
        # Real-time Capacity Gauge
        msg_raw_bytes = len(message.encode('utf-8')) if message else 0
        if capacity > 0:
            est_encoded = (msg_raw_bytes * 2 + 36) if msg_raw_bytes > 0 else 0
            used_pct = (est_encoded / capacity) * 100
            bar_pct = min(100.0, max(0.8 if msg_raw_bytes > 0 else 0.0, used_pct))
            is_full = est_encoded > capacity
            fill_class = "gauge-fill gauge-fill-full" if is_full else "gauge-fill"
            
            st.markdown(
                f"""
                <div class="capacity-gauge">
                    <div class="gauge-header">
                        <span style="font-size:0.75rem; color:var(--sandstone); font-weight:700; letter-spacing:0.04em; font-family:'Cinzel', Georgia, serif;">Beban Muatan Relief</span>
                        <span class="mono" style="font-size:0.78rem; color:{'var(--jasper-red)' if is_full else 'var(--papyrus)'};">{est_encoded:,} / {capacity:,} Bytes ({used_pct:.3f}%)</span>
                    </div>
                    <div class="gauge-track">
                        <div class="{fill_class}" style="width: {bar_pct:.2f}%;"></div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        
        st.markdown(
            """
            <div class="form-section-label" style="margin-top:0.45rem;">
                Kunci Stego Suci (Seed PRNG)
            </div>
            """,
            unsafe_allow_html=True,
        )
        stego_key = st.text_input("Kunci Stego", value="12345", key="stego_key_input", help="Seed acak PRNG yang menentukan koordinat sebaran bit pada relief citra")
        
        encrypt_btn = st.button("Enkripsi & Sembunyikan ke Citra", type="primary", use_container_width=True)

    # Pemrosesan Enkripsi dan Penyisipan
    if encrypt_btn:
        if cover_file and message.strip():
            try:
                # 1. Enkripsi pesan menggunakan ElGamal
                message_bytes = message.encode('utf-8')
                encrypted_message = st.session_state.elgamal.encrypt_bytes(
                    message_bytes, 
                    st.session_state.public_key
                )
                
                # 2. Validasi kapasitas payload citra
                if len(encrypted_message) > capacity:
                    st.error(f"Inskripsi melebihi kapasitas relief citra! Kapasitas: {capacity} bytes, Ukuran Data Terenkripsi: {len(encrypted_message)} bytes.")
                else:
                    # 3. Penyisipan LSB berbasis PRNG
                    seed_val = int(stego_key) if stego_key.isdigit() else int(hashlib.sha256(stego_key.encode()).hexdigest(), 16) % (2**31 - 1)
                    stego = LSBSteganography(seed=seed_val)
                    stego_array = stego.embed(cover_array, encrypted_message)
                    
                    # 4. Kalkulasi kualitas imperceptibility citra (PSNR)
                    psnr = stego.calculate_psnr(cover_array, stego_array)
                    
                    # 5. Konversi hasil array ke format gambar
                    stego_image = Image.fromarray(stego_array)
                    
                    st.markdown(
                        f"""
                        <div class="stego-card" style="margin-top:1.5rem; border-color: var(--turquoise-hover);">
                            <div style="display:flex; justify-content:space-between; align-items:center;">
                                <div class="card-title">Penyisipan Berhasil Disegel</div>
                                <span class="badge-tag badge-success">PSNR: {psnr:.2f} dB (Imperceptible)</span>
                            </div>
                            <div style="color:var(--papyrus-muted); font-size:0.86rem; margin-top:0.4rem;">
                                Inskripsi rahasia ({len(encrypted_message):,} bytes terenkripsi) berhasil disebarkan ke dalam bitplane LSB citra tanpa meninggalkan distorsi visual kasat mata.
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                    col_res1, col_res2 = st.columns(2, gap="large")
                    with col_res1:
                        st.image(stego_image, caption="Artefak Stego Tersegel (Format Lossless PNG)", use_container_width=True)
                    
                    with col_res2:
                        buf = io.BytesIO()
                        stego_image.save(buf, format='PNG')
                        buf.seek(0)
                        st.download_button(
                            label="Unduh Artefak Stego (PNG)",
                            data=buf,
                            file_name="stego_image.png",
                            mime="image/png",
                            use_container_width=True
                        )
                        st.markdown(
                            """
                            <div class="notice-box">
                                <span class="notice-icon">&#10022;</span>
                                <span>Pertahankan file PNG lossless ini untuk proses ekstraksi santuari. Kompresi lossy JPEG pada aplikasi chat dapat merusak integritas bit LSB.</span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )

                    # Inspeksi Matematis dan Parameter Kriptografi
                    with st.expander("Inspeksi Matematis & Parameter Kriptografi Santuari", expanded=False):
                        st.html(
                            f"""
                            <div class="inspector-box">
                                <div style="font-weight:700; color:var(--sandstone); font-family:'Cinzel', Georgia, serif; font-size:0.9rem; margin-bottom:0.45rem;">
                                    Parameter Enkripsi ElGamal-DH
                                </div>
                                <div class="inspector-grid">
                                    <div class="inspector-item">
                                        <div class="inspector-label">Safe Prime Modulus (p)</div>
                                        <div class="inspector-val">{st.session_state.elgamal.p} ({st.session_state.elgamal.p.bit_length()} bit)</div>
                                    </div>
                                    <div class="inspector-item">
                                        <div class="inspector-label">Generator Santuari (g)</div>
                                        <div class="inspector-val">{st.session_state.elgamal.g}</div>
                                    </div>
                                    <div class="inspector-item">
                                        <div class="inspector-label">Public Key Penerima (y)</div>
                                        <div class="inspector-val">{st.session_state.public_key}</div>
                                    </div>
                                    <div class="inspector-item">
                                        <div class="inspector-label">Ukuran Inskripsi Asli</div>
                                        <div class="inspector-val">{len(message_bytes):,} bytes ({len(message_bytes)*8:,} bits)</div>
                                    </div>
                                </div>

                                <div class="stone-divider"></div>

                                <div style="font-weight:700; color:var(--sandstone); font-family:'Cinzel', Georgia, serif; font-size:0.9rem; margin-bottom:0.45rem;">
                                    Proteksi Invarian Reed-Solomon &amp; Steganografi PRNG
                                </div>
                                <div class="inspector-grid">
                                    <div class="inspector-item">
                                        <div class="inspector-label">Skema Reed-Solomon</div>
                                        <div class="inspector-val">RS(255, 223) &bull; 32 Parity Bytes / Chunk</div>
                                    </div>
                                    <div class="inspector-item">
                                        <div class="inspector-label">Total Muatan Terenkripsi</div>
                                        <div class="inspector-val">{len(encrypted_message):,} bytes ({len(encrypted_message)*8:,} bits LSB)</div>
                                    </div>
                                    <div class="inspector-item">
                                        <div class="inspector-label">Stego Seed PRNG (s)</div>
                                        <div class="inspector-val">{seed_val} (SHA-256 derived)</div>
                                    </div>
                                    <div class="inspector-item">
                                        <div class="inspector-label">Indeks Kualitas PSNR</div>
                                        <div class="inspector-val">{psnr:.2f} dB (Imperceptible)</div>
                                    </div>
                                </div>
                            </div>
                            """
                        )
                    
                    # Simpan data array ke session state untuk kebutuhan analisis
                    st.session_state.stego_array = stego_array
                    st.session_state.cover_array = cover_array
                    st.session_state.stego_key = stego_key
                    
            except Exception as e:
                st.error(f"Terjadi kesalahan saat enkripsi/penyisipan: {str(e)}")
        else:
            st.warning("Silakan unggah citra cover dan masukkan inskripsi pesan terlebih dahulu!")

# ============================================================
# TAB 2: EKSTRAKSI & DEKRIPSI
# ============================================================
with tab2:
    st.markdown(
        """
        <div class="stego-card">
            <div class="card-title">Ekstraksi &amp; Dekripsi Inskripsi Rahasia</div>
            <div class="card-subtitle">Unggah artefak citra stego (PNG) dan masukkan stego key yang sesuai untuk menelusuri koordinat LSB-PRNG, mengaktifkan koreksi Reed-Solomon, serta mendekripsi pasangan ciphertext ElGamal.</div>
        </div>
        <div class="pipeline-container">
            <div class="pipeline-step">
                <span class="pipeline-num">I</span>
                <span class="pipeline-label">Artefak Stego</span>
            </div>
            <span class="pipeline-arrow">&rarr;</span>
            <div class="pipeline-step">
                <span class="pipeline-num">II</span>
                <span class="pipeline-label">Ekstraksi LSB-PRNG</span>
            </div>
            <span class="pipeline-arrow">&rarr;</span>
            <div class="pipeline-step">
                <span class="pipeline-num">III</span>
                <span class="pipeline-label">Koreksi Reed-Solomon</span>
            </div>
            <span class="pipeline-arrow">&rarr;</span>
            <div class="pipeline-step">
                <span class="pipeline-num">IV</span>
                <span class="pipeline-label">Dekripsi ElGamal (p, x)</span>
            </div>
            <span class="pipeline-arrow">&rarr;</span>
            <div class="pipeline-step">
                <span class="pipeline-num">V</span>
                <span class="pipeline-label">Inskripsi Asli Terbuka</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_dec1, col_dec2 = st.columns(2, gap="large")

    with col_dec1:
        st.markdown(
            """
            <div class="form-section-label">
                Artefak Citra Stego
            </div>
            """,
            unsafe_allow_html=True,
        )
        stego_file = st.file_uploader("Upload Artefak Stego", type=['png', 'jpg', 'jpeg', 'bmp'], key='stego_upload')
        
        stego_array = None
        if stego_file:
            stego_image = Image.open(stego_file)
            stego_array = np.array(stego_image)
            
            if len(stego_array.shape) == 2:
                stego_array = np.stack([stego_array] * 3, axis=2)
            elif stego_array.shape[2] == 4:
                stego_array = stego_array[:, :, :3]
            
            st.image(stego_image, caption="Artefak Stego yang Diperiksa", use_container_width=True)
            
            stego_file.seek(0)
            file_hash = hashlib.sha256(stego_file.read()).hexdigest()
            st.markdown(
                f"""
                <div class="notice-box">
                    <span class="notice-icon">&#9670;</span>
                    <span style="word-break:break-all;"><strong>SHA-256 Fingerprint:</strong> {file_hash}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col_dec2:
        st.markdown(
            """
            <div class="form-section-label">
                Kunci Stego Suci (Seed Verifikasi)
            </div>
            """,
            unsafe_allow_html=True,
        )
        extract_stego_key = st.text_input("Kunci Stego", value="12345", key='extract_key', help="Masukkan stego key yang identik dengan saat proses penyisipan")
        
        decrypt_btn = st.button("Ekstrak & Pulihkan Inskripsi", type="primary", use_container_width=True)

    # Pemrosesan Ekstraksi dan Dekripsi
    if decrypt_btn:
        if stego_file and stego_array is not None:
            try:
                # 1. Ekstraksi bit LSB berbasis PRNG
                seed_val = int(extract_stego_key) if extract_stego_key.isdigit() else int(hashlib.sha256(extract_stego_key.encode()).hexdigest(), 16) % (2**31 - 1)
                stego = LSBSteganography(seed=seed_val)
                encrypted_message = stego.extract(stego_array)
                
                # 2. Dekripsi ElGamal
                decrypted_bytes = st.session_state.elgamal.decrypt_bytes(
                    encrypted_message,
                    st.session_state.private_key
                )
                decrypted_message = decrypted_bytes.decode('utf-8')
                
                st.markdown(
                    """
                    <div class="stego-card" style="margin-top:1.5rem; border-color: var(--turquoise-hover);">
                        <div class="card-title" style="margin-bottom:0.4rem;">Inskripsi Rahasia Berhasil Dipulihkan</div>
                        <div style="color:var(--papyrus-muted); font-size:0.86rem; margin-bottom:0.9rem;">
                            Seluruh bit pesan berhasil direkonstruksi secara lossless melalui penelusuran seed PRNG dan dekripsi asimetris ElGamal.
                        </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.text_area("Inskripsi Terbuka", decrypted_message, height=140, key='decrypted_output', label_visibility="collapsed")
                st.markdown("</div>", unsafe_allow_html=True)

                # Inspeksi Verifikasi Dekripsi
                with st.expander("Inspeksi Matematis & Verifikasi Dekripsi", expanded=False):
                    st.html(
                        f"""
                        <div class="inspector-box">
                            <div style="font-weight:700; color:var(--sandstone); font-family:'Cinzel', Georgia, serif; font-size:0.9rem; margin-bottom:0.45rem;">
                                Status Rekonstruksi &amp; Integritas Data
                            </div>
                            <div class="inspector-grid">
                                <div class="inspector-item">
                                    <div class="inspector-label">Verifikasi Reed-Solomon</div>
                                    <div class="inspector-val" style="color:var(--turquoise-hover);">Integritas Valid &bull; Galat Terkoreksi Otomatis</div>
                                </div>
                                <div class="inspector-item">
                                    <div class="inspector-label">Private Key Dekripsi (x)</div>
                                    <div class="inspector-val">{st.session_state.private_key}</div>
                                </div>
                                <div class="inspector-item">
                                    <div class="inspector-label">Ukuran Inskripsi Terekstrak</div>
                                    <div class="inspector-val">{len(decrypted_bytes):,} bytes ({len(decrypted_bytes)*8:,} bits)</div>
                                </div>
                                <div class="inspector-item">
                                    <div class="inspector-label">Seed Ekstraksi PRNG</div>
                                    <div class="inspector-val">{seed_val} (Cocok dengan Stego Key)</div>
                                </div>
                            </div>
                        </div>
                        """
                    )
                
            except reedsolo.ReedSolomonError as e:
                st.error(f"Koreksi Galat Reed-Solomon Gagal: {str(e)}")
                st.markdown(
                    """
                    <div class="notice-box" style="border-left-color:var(--jasper-red);">
                        <span class="notice-icon" style="color:var(--jasper-red);">&times;</span>
                        <span>Citra stego kemungkinan mengalami modifikasi piksel atau kompresi lossy. Pastikan menggunakan file asli hasil unduhan PNG.</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            except Exception as e:
                st.error(f"Gagal merekonstruksi inskripsi: {str(e)}")
                st.info("Pastikan stego key yang dimasukkan sudah benar dan citra memang mengandung data rahasia.")
        else:
            st.warning("Silakan unggah citra stego terlebih dahulu!")

# ============================================================
# TAB 3: ANALISIS CITRA & KEAMANAN
# ============================================================
with tab3:
    st.markdown(
        """
        <div class="stego-card">
            <div class="card-title">Analisis Kualitas Relik &amp; Uji Steganalisis Kuil</div>
            <div class="card-subtitle">Pengujian komprehensif terhadap imperceptibility dan ketahanan steganografi: metrik objektif (MSE, PSNR, MAE, Korelasi), komparasi histogram warna mineral, heatmap sebaran spasial LSB, uji kerapuhan JPEG, dan Uji Chi-Square.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if 'stego_array' in st.session_state and 'cover_array' in st.session_state:
        stego_arr = st.session_state.stego_array
        cover_arr = st.session_state.cover_array
        
        col_img1, col_img2 = st.columns(2, gap="large")
        with col_img1:
            st.image(Image.fromarray(cover_arr), caption="Citra Cover (Asli)", use_container_width=True)
        with col_img2:
            st.image(Image.fromarray(stego_arr), caption="Citra Stego (Hasil Penyisipan)", use_container_width=True)

        # Dashboard Metrik Statistik Kualitas Citra
        st.markdown(
            """
            <div class="stego-card" style="margin-top:1.5rem;">
                <div class="card-title" style="margin-bottom:0.85rem;">Metrik Statistik Kualitas Citra (Imperceptibility)</div>
            """,
            unsafe_allow_html=True,
        )
        metrics = calculate_statistical_metrics(cover_arr, stego_arr)
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        with col_m1:
            st.metric("MSE", f"{metrics['MSE']:.4f}")
        with col_m2:
            st.metric("PSNR", f"{metrics['PSNR']:.2f} dB")
        with col_m3:
            st.metric("MAE", f"{metrics['MAE']:.4f}")
        with col_m4:
            st.metric("Korelasi", f"{metrics['Correlation']:.4f}")
        st.markdown("</div>", unsafe_allow_html=True)

        # Komparasi Histogram Frekuensi
        st.markdown(
            """
            <div class="stego-card">
                <div class="card-title" style="margin-bottom:0.85rem;">Perbandingan Histogram Spektrum (Cover vs Stego)</div>
            """,
            unsafe_allow_html=True,
        )
        hist_fig = plot_histogram_comparison(cover_arr, stego_arr, "Histogram Spektrum: Cover vs Stego")
        st.pyplot(hist_fig, use_container_width=True)
        close_figure(hist_fig)
        st.markdown("</div>", unsafe_allow_html=True)

        # Perbedaan Histogram
        st.markdown(
            """
            <div class="stego-card">
                <div class="card-title" style="margin-bottom:0.85rem;">Perbedaan Histogram (Selisih Frekuensi Piksel)</div>
            """,
            unsafe_allow_html=True,
        )
        diff_fig = plot_histogram_difference(cover_arr, stego_arr, "Perbedaan Histogram Spektrum")
        st.pyplot(diff_fig, use_container_width=True)
        close_figure(diff_fig)
        st.markdown("</div>", unsafe_allow_html=True)

        # Visual Steganalysis - Bidang Bit LSB
        st.markdown(
            """
            <div class="stego-card">
                <div class="card-title" style="margin-bottom:0.5rem;">Visual Steganalysis &mdash; Bidang Bit LSB (Bitplane 0)</div>
                <div style="color:var(--papyrus-muted); font-size:0.84rem; margin-bottom:0.9rem;">
                    Visualisasi bit terendah (LSB) untuk mengevaluasi sifat keacakan sebaran spasial bit yang dihasilkan oleh algoritma PRNG.
                </div>
            """,
            unsafe_allow_html=True,
        )
        stego_eng = LSBSteganography()
        lsb_plane = stego_eng.get_lsb_plane(stego_arr)
        lsb_image = Image.fromarray(lsb_plane)
        st.image(lsb_image, caption="Enhanced LSB Plane (Bitplane 0)", use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Difference Heatmap (Peta Perbedaan Spasial)
        st.markdown(
            """
            <div class="stego-card">
                <div class="card-title" style="margin-bottom:0.45rem;">Peta Perbedaan Spasial (Difference Heatmap)</div>
                <div style="color:var(--papyrus-muted); font-size:0.84rem; margin-bottom:0.9rem;">
                    Visualisasi spasial lokasi piksel yang mengalami modifikasi akibat penyisipan data. Spektrum gradien mineral (Obsidian &rarr; Lapis Lazuli &rarr; Turquoise &rarr; Sandstone &rarr; Papyrus) memperlihatkan amplifikasi selisih nilai piksel.
                </div>
            """,
            unsafe_allow_html=True,
        )
        
        col_h1, col_h2 = st.columns([2, 1], gap="medium")
        with col_h1:
            amp_factor = st.slider("Faktor Amplifikasi Perbedaan (Multiplier)", min_value=10, max_value=255, value=100, step=10, key="heatmap_amp")
        with col_h2:
            st.markdown("<div class='field-btn-align'></div>", unsafe_allow_html=True)
            enhance_pts = st.checkbox("Perjelas Titik Sebaran PRNG", value=True, key="enhance_heatmap_pts", help="Menerapkan filter spasial agar sebaran bit acak berukuran 1 piksel tetap terlihat jelas di layar")
        
        heat_fig, heat_stats = plot_difference_heatmap(cover_arr, stego_arr, amplification=amp_factor, enhance_visibility=enhance_pts)
        st.pyplot(heat_fig, use_container_width=True)
        close_figure(heat_fig)
        
        st.markdown(
            f"""
            <div class="notice-box">
                <span class="notice-icon">&#10022;</span>
                <span><strong>Statistik Modifikasi Spasial:</strong> {heat_stats['modified_pixels']:,} dari {heat_stats['total_pixels']:,} piksel diubah ({heat_stats['modified_percentage']:.3f}% densitas sebaran LSB-PRNG). Perbedaan nilai mentah piksel maksimal: {heat_stats['max_difference']:.0f} level kecerahan.</span>
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Uji Kerapuhan Kompresi JPEG (JPEG Fragility Test)
        st.markdown(
            """
            <div class="stego-card">
                <div class="card-title" style="margin-bottom:0.45rem;">Uji Kerapuhan Kompresi JPEG (JPEG Fragility Test)</div>
                <div style="color:var(--papyrus-muted); font-size:0.84rem; margin-bottom:0.9rem;">
                    Pengujian sifat kerapuhan (*fragility*) metode LSB terhadap kompresi lossy JPEG. Kuantisasi koefisien DCT pada JPEG mendistorsi bit LSB sehingga pesan rahasia tidak dapat dipulihkan secara lossless.
                </div>
            """,
            unsafe_allow_html=True,
        )

        col_q1, col_q2 = st.columns([1, 1], gap="medium")
        with col_q1:
            jpeg_q = st.select_slider("Kualitas Kompresi JPEG (Quality Factor)", options=[90, 80, 70, 50, 30], value=70, key="jpeg_quality_slider")
        with col_q2:
            st.markdown("<div class='field-btn-align'></div>", unsafe_allow_html=True)
            test_jpeg_btn = st.button("Jalankan Uji Kerapuhan JPEG", type="primary", use_container_width=True, key="run_jpeg_test")

        if test_jpeg_btn or 'jpeg_tested' in st.session_state:
            st.session_state.jpeg_tested = True
            jpeg_arr, jpeg_size = simulate_jpeg_compression(stego_arr, quality=jpeg_q)
            jpeg_metrics = calculate_statistical_metrics(stego_arr, jpeg_arr)
            
            col_jp1, col_jp2 = st.columns(2, gap="large")
            with col_jp1:
                st.image(Image.fromarray(jpeg_arr), caption=f"Citra Stego setelah Kompresi JPEG (Q={jpeg_q})", use_container_width=True)
            with col_jp2:
                st.markdown(
                    f"""
                    <div class="param-box">
                        <div class="param-label">Ukuran File JPEG Terkompresi</div>
                        <div class="param-val">{jpeg_size:,} bytes</div>
                        <div class="param-label" style="margin-top:0.55rem;">PSNR terhadap Citra Stego Asli</div>
                        <div class="param-val">{jpeg_metrics['PSNR']:.2f} dB</div>
                        <div class="param-label" style="margin-top:0.55rem;">MSE (Mean Squared Error)</div>
                        <div class="param-val">{jpeg_metrics['MSE']:.4f}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                
                st.markdown("<div class='form-section-label'>Hasil Uji Ekstraksi dari Citra JPEG:</div>", unsafe_allow_html=True)
                stego_key_val = st.session_state.get('stego_key', '12345')
                seed_val = int(stego_key_val) if stego_key_val.isdigit() else int(hashlib.sha256(stego_key_val.encode()).hexdigest(), 16) % (2**31 - 1)
                
                extraction_failed = False
                extracted_result = None
                error_msg = ""
                try:
                    stego_test = LSBSteganography(seed=seed_val)
                    extracted_raw = stego_test.extract(jpeg_arr)
                    decrypted_res = st.session_state.elgamal.decrypt_bytes(extracted_raw, st.session_state.private_key)
                    extracted_result = decrypted_res.decode('utf-8')
                except reedsolo.ReedSolomonError as e:
                    extraction_failed = True
                    error_msg = f"Reed-Solomon ECC mendeteksi korupsi data melebihi batas toleransi koreksi ({str(e)})"
                except Exception as e:
                    extraction_failed = True
                    error_msg = f"Gagal merekonstruksi bit LSB akibat distorsi kuantisasi DCT JPEG ({str(e)})"
                
                if extraction_failed:
                    st.markdown(
                        f"""
                        <div class="notice-box" style="border-left-color:var(--jasper-red);">
                            <span class="notice-icon" style="color:var(--jasper-red);">&times;</span>
                            <div>
                                <strong style="color:var(--jasper-red);">Ekstraksi Gagal (Sifat Kerapuhan / Fragility Terbukti)</strong><br>
                                <span style="font-size:0.8rem; color:var(--muted);">{error_msg}</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"""
                        <div class="notice-box" style="border-left-color:var(--turquoise-hover);">
                            <span class="notice-icon" style="color:var(--turquoise-hover);">&#10003;</span>
                            <div>
                                <strong style="color:var(--turquoise-hover);">Terkoreksi Sempurna oleh Reed-Solomon</strong><br>
                                <span style="font-size:0.8rem; color:var(--papyrus);">Pesan: "{extracted_result}"</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

        st.markdown("</div>", unsafe_allow_html=True)

        # Steganalisis Statistik Uji Chi-Square (Westfeld & Pfitzmann Attack)
        st.markdown(
            """
            <div class="stego-card">
                <div class="card-title" style="margin-bottom:0.45rem;">Steganalisis Statistik Uji Chi-Square (Westfeld &amp; Pfitzmann Attack)</div>
                <div style="color:var(--papyrus-muted); font-size:0.84rem; margin-bottom:0.9rem;">
                    Analisis statistik pasangan nilai piksel (*Pairs of Values - PoVs*) untuk menguji probabilitas deteksi keberadaan pesan tersembunyi pada citra secara matematis.
                </div>
            """,
            unsafe_allow_html=True,
        )
        
        chi_fig, chi_stats = plot_chi_square_analysis(cover_arr, stego_arr, num_points=60)
        st.pyplot(chi_fig, use_container_width=True)
        close_figure(chi_fig)
        
        st.markdown(
            f"""
            <div class="notice-box">
                <span class="notice-icon">&#10022;</span>
                <span><strong>Hasil Analisis Chi-Square:</strong> Rata-rata probabilitas cover: {chi_stats['avg_cover_prob']:.4f} | Rata-rata probabilitas stego: {chi_stats['avg_stego_prob']:.4f} (Maksimal: {chi_stats['max_stego_prob']:.4f}). <strong>Status:</strong> {chi_stats['detection_status']}.</span>
            </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        
    else:
        st.markdown(
            """
            <div class="notice-box">
                <span class="notice-icon">&#10022;</span>
                <span>Silakan lakukan enkripsi dan penyisipan pada tab <strong>Enkripsi &amp; Penyisipan</strong> terlebih dahulu untuk melihat perbandingan citra, heatmap spasial mineral, dan analisis statistik keamanan.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ------------------------------------------------------------
# SEMANTIC FOOTER
# ------------------------------------------------------------
st.markdown(
    """
    <footer class="footer-wrap" role="contentinfo">
        <p style="margin:0 0 0.35rem 0; font-weight:700; color:var(--sandstone); font-family:'Cinzel', Georgia, serif; font-size:0.92rem; letter-spacing:0.06em;">
            KHNUM &bull; STEGOCIPHER &bull; SANCTUARY OF ANCIENT CRYPTOGRAPHY
        </p>
        <p style="margin:0; font-size:0.76rem; color:var(--muted); font-family:'Inter', sans-serif;">
            Keamanan Informasi &bull; Asymmetric ElGamal Cryptography &bull; 1024-bit Diffie-Hellman &bull; Reed-Solomon RS(255,223) &bull; LSB-PRNG Steganalysis
        </p>
    </footer>
    """,
    unsafe_allow_html=True,
)
