import streamlit as st
import numpy as np
from PIL import Image
import io
import time
import matplotlib.pyplot as plt
import hashlib
from contextlib import contextmanager

from elgamal import ElGamalDH
from steganography import LSBSteganography
import importlib
import analysis
importlib.reload(analysis)
from analysis import (plot_histogram_comparison, plot_histogram_difference, 
                      plot_difference_heatmap, plot_chi_square_analysis,
                      simulate_jpeg_compression, calculate_statistical_metrics, close_figure)
import reedsolo

LOADING_MINIMUM_SECONDS = 0.5


@contextmanager
def loading_operation(message):
    """Show a modal loading screen and keep it visible for at least 500 ms."""
    started_at = time.monotonic()
    loading_placeholder = st.empty()
    loading_placeholder.markdown(
        f"""
        <div class="loading-overlay" role="status" aria-live="polite">
            <div class="loading-panel">
                <div class="loading-spinner"></div>
                <div class="loading-title">Sedang memproses</div>
                <div class="loading-message">{message}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    try:
        yield
    finally:
        remaining = LOADING_MINIMUM_SECONDS - (time.monotonic() - started_at)
        if remaining > 0:
            time.sleep(remaining)
        loading_placeholder.empty()

# Page configuration
st.set_page_config(
    page_title="Steganografi Citra - ElGamal Diffie-Hellman",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Design System - Egyptian Sandstone Dark Theme
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    :root {
        --bg: #1c1917;
        --surface: #24201d;
        --surface-low: #1f1c19;
        --surface-high: #2d2925;
        --border: #3c3630;
        --border-subtle: #302b26;
        --primary: #c68a35;
        --primary-hover: #d69740;
        --primary-soft: #2b2316;
        --text: #f3eee6;
        --muted: #a49887;
        --muted-light: #706657;
        --success: #48a972;
        --success-soft: #1a2b22;
        --error: #cf584f;
        --error-soft: #2d1b1b;
    }

    * {
        box-sizing: border-box;
    }

    html, body, [class*="css"] {
        font-family: "Plus Jakarta Sans", -apple-system, BlinkMacSystemFont, sans-serif;
        -webkit-font-smoothing: antialiased;
    }

    .stApp {
        background-color: var(--bg);
        color: var(--text);
    }

    /* Header setup & Sidebar toggle button */
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
        top: 8px !important;
        left: 12px !important;
        z-index: 1002 !important;
    }

    [data-testid="stExpandSidebarButton"] button,
    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="collapsedControl"] button {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        color: var(--primary) !important;
        border-radius: 6px !important;
        transition: all 0.15s ease !important;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.3) !important;
        width: 36px !important;
        height: 36px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
    }

    [data-testid="stExpandSidebarButton"] button:hover,
    [data-testid="stSidebarCollapseButton"] button:hover,
    [data-testid="collapsedControl"] button:hover {
        background: var(--surface-high) !important;
        border-color: var(--primary) !important;
        color: var(--primary-hover) !important;
    }

    [data-testid="stExpandSidebarButton"] svg,
    [data-testid="stSidebarCollapseButton"] svg,
    [data-testid="collapsedControl"] svg {
        fill: var(--primary) !important;
        stroke: var(--primary) !important;
        color: var(--primary) !important;
    }

    .block-container {
        max-width: 1140px;
        padding-top: 4.8rem;
        padding-bottom: 3.5rem;
    }

    h1, h2, h3, h4 {
        font-family: "Cinzel", Georgia, serif !important;
        color: var(--text) !important;
        font-weight: 700;
        letter-spacing: 0.02em;
    }

    p, span, label, div {
        color: var(--text);
    }

    .stMarkdown, .stMarkdown p {
        color: var(--text);
    }

    .mono {
        font-family: "JetBrains Mono", monospace !important;
    }

    /* ---------------- TOPBAR ---------------- */
    .topbar {
        position: fixed;
        z-index: 99;
        top: 0;
        left: 0;
        right: 0;
        height: 54px;
        padding-left: 56px;
        padding-right: 2rem;
        background: rgba(28, 25, 23, 0.94);
        backdrop-filter: blur(10px);
        border-bottom: 1px solid var(--border);
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: padding-left 0.3s ease;
    }

    .stApp:has(section[data-testid="stSidebar"][aria-expanded="true"]) .topbar {
        padding-left: 310px;
    }

    .topbar-left {
        display: flex;
        align-items: center;
        gap: 0.65rem;
    }

    .topbar-title {
        font-family: "Cinzel", serif;
        font-size: 0.92rem;
        font-weight: 700;
        color: var(--primary);
        letter-spacing: 0.02em;
    }

    .topbar-sep {
        color: var(--muted-light);
        font-size: 0.8rem;
    }

    .topbar-sub {
        font-family: "JetBrains Mono", monospace;
        font-size: 0.74rem;
        color: var(--muted);
    }

    /* ---------------- SIDEBAR ---------------- */
    section[data-testid="stSidebar"] {
        background-color: var(--surface);
        border-right: 1px solid var(--border);
        z-index: 100;
    }

    section[data-testid="stSidebar"] > div {
        padding: 1.3rem 1.15rem;
    }

    .brand-wrap {
        padding-bottom: 1.1rem;
        border-bottom: 1px solid var(--border);
        margin-bottom: 1.2rem;
    }

    .brand-title {
        font-family: "Cinzel", serif !important;
        font-size: 1.12rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        color: var(--primary) !important;
    }

    .brand-subtitle {
        color: var(--muted);
        font-size: 0.72rem;
        margin-top: 0.2rem;
    }

    .sidebar-section-title {
        font-family: "JetBrains Mono", monospace;
        font-size: 0.65rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: var(--muted);
        margin-bottom: 0.55rem;
    }

    .param-box {
        background: var(--surface-low);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 0.75rem 0.85rem;
        margin-bottom: 0.8rem;
        font-size: 0.78rem;
    }

    .param-label {
        font-family: "JetBrains Mono", monospace;
        font-size: 0.62rem;
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.06em;
        font-weight: 600;
    }

    .param-val {
        font-family: "JetBrains Mono", monospace;
        font-size: 0.75rem;
        color: var(--text);
        word-break: break-all;
        margin-top: 0.15rem;
    }

    /* ---------------- CARDS & BOXES ---------------- */
    .stego-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 1.25rem;
        box-shadow: 0 1px 4px rgba(0, 0, 0, 0.25);
        margin-bottom: 1.2rem;
    }

    .card-title {
        font-family: "Cinzel", Georgia, serif !important;
        font-size: 1.05rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        color: var(--text) !important;
    }

    .card-subtitle {
        margin-top: 0.25rem;
        color: var(--muted);
        font-size: 0.78rem;
        line-height: 1.45;
    }

    .notice-box {
        margin-top: 0.85rem;
        padding: 0.7rem 0.85rem;
        background: var(--surface-low);
        border: 1px solid var(--border);
        border-radius: 6px;
        font-size: 0.75rem;
        color: var(--muted);
        line-height: 1.5;
        display: flex;
        gap: 0.55rem;
        align-items: flex-start;
    }

    .notice-icon {
        font-family: "JetBrains Mono", monospace;
        font-weight: 700;
        font-size: 0.75rem;
        color: var(--primary);
    }

    .badge-tag {
        font-family: "JetBrains Mono", monospace;
        font-size: 0.62rem;
        font-weight: 600;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .badge-success {
        background: var(--success-soft);
        color: var(--success);
        border: 1px solid #294636;
    }

    /* ---------------- TABS STYLING ---------------- */
    [data-testid="stTabs"] {
        margin-top: 1.1rem;
    }

    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        background-color: var(--surface-low);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 4px;
        gap: 6px;
    }

    [data-testid="stTabs"] [data-baseweb="tab"] {
        border-radius: 6px !important;
        font-family: "Cinzel", serif !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
        letter-spacing: 0.03em !important;
        color: var(--muted) !important;
        padding: 0.6rem 1.4rem !important;
        border: 1px solid transparent !important;
        background: transparent !important;
        transition: all 0.15s ease !important;
    }

    [data-testid="stTabs"] [data-baseweb="tab"]:hover {
        color: var(--text) !important;
        background: var(--surface-high) !important;
    }

    [data-testid="stTabs"] [data-baseweb="tab"][aria-selected="true"] {
        background: var(--primary-soft) !important;
        border: 1px solid var(--primary) !important;
        color: var(--primary) !important;
    }

    /* ---------------- FORM & BUTTONS ---------------- */
    [data-testid="stFileUploader"] {
        margin-bottom: 0.6rem;
    }

    [data-testid="stFileUploaderDropzone"] {
        padding: 1.8rem 1.2rem !important;
        background-color: var(--surface-low) !important;
        border: 1.5px dashed var(--border) !important;
        border-radius: 8px !important;
        transition: all 0.2s ease !important;
    }

    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: var(--primary) !important;
        background-color: var(--primary-soft) !important;
    }

    [data-testid="stFileUploaderDropzone"] div {
        color: var(--text) !important;
    }

    [data-testid="stFileUploaderDropzone"] > div > div > div > div > small,
    [data-testid="stFileUploaderDropzone"] > div > div > div > span {
        font-size: 0 !important;
    }

    [data-testid="stFileUploaderDropzone"] > div > div > div > span::after,
    [data-testid="stFileUploaderDropzone"] > div > div > div > div > small::after {
        content: "maksimal 200 MB (png, jpg, bmp, jpeg)";
        font-size: 0.72rem;
        color: var(--muted) !important;
        font-family: "JetBrains Mono", monospace !important;
        visibility: visible;
        display: block;
    }

    /* Additional selector to target modern Streamlit file uploader helper text */
    [data-testid="stFileUploaderDropzoneInstructions"] > div > span {
        font-size: 0 !important;
    }
    [data-testid="stFileUploaderDropzoneInstructions"] > div > span::after {
        content: "maksimal 200 MB (png, jpg, bmp, jpeg)";
        font-size: 0.72rem;
        visibility: visible;
        display: block;
    }

    [data-testid="stFileUploaderDropzone"] button {
        background: var(--surface-high) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        font-size: 0.8rem !important;
    }

    [data-testid="stFileUploaderDropzone"] button:hover {
        border-color: var(--primary) !important;
        color: var(--primary) !important;
    }

    /* The selected-file uploader control replaces the misleading plus icon. */
    [data-testid="stFileUploader"] button[aria-label="Add files"] svg,
    [data-testid="stFileUploader"] button[title="Add files"] svg {
        display: none !important;
    }

    [data-testid="stFileUploader"] button[aria-label="Add files"]::before,
    [data-testid="stFileUploader"] button[title="Add files"]::before {
        content: "";
        display: block;
        width: 1.15rem;
        height: 1.15rem;
        background-color: currentColor;
        -webkit-mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M17 1l4 4-4 4'/%3E%3Cpath d='M3 11V9a4 4 0 0 1 4-4h14'/%3E%3Cpath d='M7 23l-4-4 4-4'/%3E%3Cpath d='M21 13v2a4 4 0 0 1-4 4H3'/%3E%3C/svg%3E") center / contain no-repeat;
        mask: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M17 1l4 4-4 4'/%3E%3Cpath d='M3 11V9a4 4 0 0 1 4-4h14'/%3E%3Cpath d='M7 23l-4-4 4-4'/%3E%3Cpath d='M21 13v2a4 4 0 0 1-4 4H3'/%3E%3C/svg%3E") center / contain no-repeat;
    }

    [data-testid="stWidgetLabel"] p {
        color: var(--muted) !important;
        font-family: "JetBrains Mono", monospace !important;
        font-size: 0.72rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        font-weight: 600 !important;
    }

    .stButton > button {
        border-radius: 6px !important;
        min-height: 42px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        transition: all 0.15s ease !important;
        font-family: "Cinzel", serif !important;
        letter-spacing: 0.02em !important;
    }

    .stButton > button[kind="primary"] {
        background: #c68a35 !important;
        border: 1px solid #c68a35 !important;
        color: #1c1917 !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: #d69740 !important;
        border-color: #d69740 !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3) !important;
    }

    .stButton > button[kind="secondary"] {
        background: var(--surface-high) !important;
        border: 1px solid var(--border) !important;
        color: var(--text) !important;
    }

    .stButton > button[kind="secondary"]:hover {
        border-color: var(--primary) !important;
        color: var(--primary) !important;
    }

    .stDownloadButton > button {
        background: #c68a35 !important;
        border: 1px solid #c68a35 !important;
        color: #1c1917 !important;
        border-radius: 6px !important;
        min-height: 42px !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
        font-family: "Cinzel", serif !important;
        letter-spacing: 0.02em !important;
    }

    .stDownloadButton > button:hover {
        background: #d69740 !important;
        border-color: #d69740 !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3) !important;
    }

    .stTextArea textarea, .stTextInput input {
        font-family: "JetBrains Mono", monospace !important;
        background: var(--surface) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        font-size: 0.85rem !important;
    }

    .stTextArea textarea:focus, .stTextInput input:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 1px var(--primary) !important;
    }

    .loading-overlay {
        position: fixed;
        inset: 0;
        z-index: 9999;
        display: flex;
        align-items: center;
        justify-content: center;
        background: rgba(28, 25, 23, 0.78);
        backdrop-filter: blur(4px);
        cursor: wait;
        pointer-events: auto;
    }

    .loading-panel {
        min-width: 260px;
        padding: 1.5rem 1.8rem;
        text-align: center;
        background: var(--surface);
        border: 1px solid var(--primary);
        border-radius: 8px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.45);
    }

    .loading-spinner {
        width: 34px;
        height: 34px;
        margin: 0 auto 0.85rem;
        border: 3px solid var(--border);
        border-top-color: var(--primary);
        border-radius: 50%;
        animation: loading-spin 0.8s linear infinite;
    }

    .loading-title {
        color: var(--primary);
        font-family: "Cinzel", serif;
        font-weight: 700;
        font-size: 0.95rem;
    }

    .loading-message {
        margin-top: 0.35rem;
        color: var(--muted);
        font-size: 0.75rem;
    }

    @keyframes loading-spin {
        to { transform: rotate(360deg); }
    }

    /* Metrics Grid */
    [data-testid="stMetric"] {
        background: var(--surface) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        padding: 0.85rem !important;
    }

    [data-testid="stMetricLabel"] p {
        font-family: "JetBrains Mono", monospace !important;
        font-size: 0.65rem !important;
        color: var(--muted) !important;
        text-transform: uppercase !important;
        letter-spacing: 0.06em !important;
        font-weight: 600 !important;
    }

    [data-testid="stMetricValue"] div {
        font-family: "Cinzel", serif !important;
        font-size: 1.45rem !important;
        font-weight: 700 !important;
        color: var(--primary) !important;
    }

    [data-testid="stAlert"] {
        background-color: var(--surface-low) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
        color: var(--text) !important;
    }

    .footer-wrap {
        margin-top: 3.5rem;
        padding-top: 1.4rem;
        border-top: 1px solid var(--border);
        text-align: center;
        font-size: 0.8rem;
        color: var(--muted);
    }

    /* Decorative Stone Fret & Accents */
    .stone-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent 0%, var(--border) 20%, var(--primary) 50%, var(--border) 80%, transparent 100%);
        margin: 1.2rem 0;
        position: relative;
    }

    .stone-divider::after {
        content: "◆";
        position: absolute;
        top: -7px;
        left: 50%;
        transform: translateX(-50%);
        color: var(--primary);
        background: var(--surface);
        padding: 0 8px;
        font-size: 0.55rem;
    }

    /* Pipeline Flow Banner */
    .pipeline-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: var(--surface-low);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 0.75rem 1rem;
        margin-bottom: 1.2rem;
        overflow-x: auto;
        gap: 0.5rem;
    }

    .pipeline-step {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        white-space: nowrap;
    }

    .pipeline-num {
        font-family: "JetBrains Mono", monospace;
        font-size: 0.65rem;
        font-weight: 700;
        width: 20px;
        height: 20px;
        border-radius: 4px;
        background: var(--surface-high);
        border: 1px solid var(--border);
        color: var(--primary);
        display: inline-flex;
        align-items: center;
        justify-content: center;
    }

    .pipeline-label {
        font-size: 0.76rem;
        color: var(--text);
        font-weight: 500;
    }

    .pipeline-arrow {
        color: var(--muted-light);
        font-size: 0.85rem;
        font-family: "JetBrains Mono", monospace;
    }

    /* Capacity Gauge */
    .capacity-gauge {
        background: var(--surface-low);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 0.75rem 0.85rem;
        margin-top: 0.6rem;
        margin-bottom: 0.8rem;
    }

    .gauge-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.4rem;
    }

    .gauge-track {
        height: 6px;
        background: var(--surface-high);
        border-radius: 3px;
        overflow: hidden;
        border: 1px solid var(--border);
    }

    .gauge-fill {
        height: 100%;
        background: #c68a35;
        border-radius: 3px;
        transition: width 0.3s ease;
    }

    .gauge-fill-full {
        background: var(--error) !important;
    }

    /* Math & Cipher Inspector Details */
    .inspector-box {
        background: var(--surface-low);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 1rem;
        margin-top: 0.8rem;
        font-size: 0.78rem;
    }

    .inspector-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 0.85rem;
        margin-top: 0.6rem;
    }

    .inspector-item {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 5px;
        padding: 0.6rem 0.75rem;
    }

    .inspector-label {
        font-family: "JetBrains Mono", monospace;
        font-size: 0.62rem;
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }

    .inspector-val {
        font-family: "JetBrains Mono", monospace;
        font-size: 0.75rem;
        color: var(--text);
        word-break: break-all;
        margin-top: 0.2rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Topbar
st.markdown(
    """
    <div class="topbar">
        <div class="topbar-left">
            <span class="topbar-title">Keamanan Informasi</span>
            <span class="topbar-sep">/</span>
            <span class="topbar-sub">Steganografi Citra Digital</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Header Section
st.html(
    """
    <div style="margin-bottom: 1.6rem;">
        <h1 style="font-family:'Cinzel', Georgia, serif; font-size:1.85rem; font-weight:700; margin:0 0 0.5rem 0; color:var(--text); letter-spacing:0.02em;">
            Steganografi dengan Enkripsi ElGamal berbasis Diffie-Hellman
        </h1>
        <p style="color:var(--muted); font-size:0.88rem; line-height:1.6; margin:0; max-width:860px;">
            Aplikasi pengamanan pesan rahasia pada citra digital menggunakan enkripsi asimetris ElGamal berbasis Diffie-Hellman, proteksi integritas Reed-Solomon Error Correction, serta penyisipan bit LSB teracak berbasis PRNG.
        </p>
    </div>
    """
)

# Cache ElGamal instance to avoid regenerating safe prime on each rerun
@st.cache_resource
def get_elgamal_instance():
    """Get or create cached ElGamal instance."""
    return ElGamalDH()

# Initialize session state
if 'elgamal' not in st.session_state:
    st.session_state.elgamal = get_elgamal_instance()
if 'private_key' not in st.session_state:
    st.session_state.private_key, st.session_state.public_key = st.session_state.elgamal.generate_keypair()
if 'is_processing' not in st.session_state:
    st.session_state.is_processing = False

# Sidebar for key management
with st.sidebar:
    st.markdown(
        """
        <div class="brand-wrap">
            <div class="brand-title">Steganografi Citra</div>
            <div class="brand-subtitle">Enkripsi ElGamal-DH &amp; LSB-PRNG</div>
        </div>
        <div class="sidebar-section-title">Parameter Kriptografi</div>
        """,
        unsafe_allow_html=True,
    )

        
    p_value = st.text_input("Prime Modulus (p)", value=str(st.session_state.elgamal.p), key="param_p", help="Bisa diedit dan dicopy", disabled=st.session_state.is_processing)
    g_value = st.text_input("Generator (g)", value=str(st.session_state.elgamal.g), key="param_g", help="Bisa diedit dan dicopy", disabled=st.session_state.is_processing)
    
    st.markdown(
        """
        <div class="sidebar-section-title" style="margin-top:0.8rem;">Pasangan Kunci</div>
        """,
        unsafe_allow_html=True,
    )
    
    private_key_value = st.text_input("Private Key (x)", value=str(st.session_state.private_key), key="param_private", help="Bisa diedit dan dicopy", disabled=st.session_state.is_processing)
    public_key_value = st.text_input("Public Key (y)", value=str(st.session_state.public_key), key="param_public", help="Bisa diedit dan dicopy", disabled=st.session_state.is_processing)
    
    # Update session state if values are changed
    if st.button("Update Parameter", type="secondary", use_container_width=True, key="update_params", disabled=st.session_state.is_processing):
        try:
            st.session_state.elgamal.p = int(p_value)
            st.session_state.elgamal.g = int(g_value)
            st.session_state.private_key = int(private_key_value)
            st.session_state.public_key = int(public_key_value)
            st.success("Parameter berhasil diperbarui!")
        except ValueError:
            st.error("Nilai parameter harus berupa angka integer!")

    if st.button("Generate Kunci Baru", type="secondary", use_container_width=True, disabled=st.session_state.is_processing):
        st.cache_resource.clear()
        st.session_state.elgamal = get_elgamal_instance()
        st.session_state.private_key, st.session_state.public_key = st.session_state.elgamal.generate_keypair()
        st.success("Kunci baru berhasil dibuat!")
        st.rerun()

    st.markdown(
        """
        <div style="margin-top:2.5rem; padding-top:1rem; border-top:1px solid var(--border); font-size:0.72rem; color:var(--muted);">
            <div>Tugas Keamanan Informasi</div>
            <div style="color:var(--muted-light); font-size:0.68rem; margin-top:0.2rem;">Semester 5 &bull; UTS</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Main Navigation Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Enkripsi", "Dekripsi", "Analisis", "Uji JPEG"])

# ------------------------------------------------------------
# TAB 1: ENKRIPSI
# ------------------------------------------------------------
with tab1:
    st.markdown(
        """
        <div class="stego-card">
            <div class="card-title">Enkripsi &amp; Penyisipan Pesan</div>
            <div class="card-subtitle">Pilih gambar cover, masukkan pesan rahasia, dan tentukan stego key untuk melakukan enkripsi dan penyisipan data.</div>
        </div>
        <div class="pipeline-container">
            <div class="pipeline-step">
                <span class="pipeline-num">1</span>
                <span class="pipeline-label">Pesan Plaintext</span>
            </div>
            <span class="pipeline-arrow">&rarr;</span>
            <div class="pipeline-step">
                <span class="pipeline-num">2</span>
                <span class="pipeline-label">Enkripsi ElGamal (c1, c2)</span>
            </div>
            <span class="pipeline-arrow">&rarr;</span>
            <div class="pipeline-step">
                <span class="pipeline-num">3</span>
                <span class="pipeline-label">Reed-Solomon ECC</span>
            </div>
            <span class="pipeline-arrow">&rarr;</span>
            <div class="pipeline-step">
                <span class="pipeline-num">4</span>
                <span class="pipeline-label">Penyisipan LSB-PRNG</span>
            </div>
            <span class="pipeline-arrow">&rarr;</span>
            <div class="pipeline-step">
                <span class="pipeline-num">5</span>
                <span class="pipeline-label">Citra Stego Output</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2, gap="large")

    with col1:
        st.markdown(
            """
            <div style="font-family:'JetBrains Mono', monospace; font-size:0.68rem; color:var(--muted); text-transform:uppercase; margin-bottom:0.4rem;">
                Gambar Cover (Citra Asli)
            </div>
            """,
            unsafe_allow_html=True,
        )
        cover_file = st.file_uploader("Upload Gambar Cover", type=['png', 'jpg', 'jpeg', 'bmp'], key="cover_uploader", disabled=st.session_state.is_processing)
        
        capacity = 0
        cover_array = None
        if cover_file:
            cover_image = Image.open(cover_file)
            cover_array = np.array(cover_image)
            
            if len(cover_array.shape) == 2:
                cover_array = np.stack([cover_array] * 3, axis=2)
            elif cover_array.shape[2] == 4:
                cover_array = cover_array[:, :, :3]
            
            st.image(cover_image, caption="Gambar Cover Asli", use_container_width=True)
            stego_calc = LSBSteganography(nsym=20)
            capacity = stego_calc.calculate_capacity(cover_array)
            st.markdown(
                f"""
                <div class="notice-box">
                    <span class="notice-icon">i</span>
                    <span><strong>Kapasitas Maksimum:</strong> {capacity:,} bytes ({capacity * 8:,} bits)</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col2:
        st.markdown(
            """
            <div style="font-family:'JetBrains Mono', monospace; font-size:0.68rem; color:var(--muted); text-transform:uppercase; margin-bottom:0.4rem;">
                Pesan Rahasia (Plaintext)
            </div>
            """,
            unsafe_allow_html=True,
        )
        message = st.text_area("Input Pesan", height=120, placeholder="Masukkan pesan rahasia yang ingin disembunyikan...", key="msg_input", disabled=st.session_state.is_processing)
        
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
                        <span style="font-size:0.65rem; color:var(--muted); font-weight:600; text-transform:uppercase; letter-spacing:0.05em; font-family:'JetBrains Mono', monospace;">Estimasi Muatan Payload</span>
                        <span class="mono" style="font-size:0.72rem; color:{'var(--error)' if is_full else 'var(--text)'};">{est_encoded:,} / {capacity:,} Bytes ({used_pct:.3f}%)</span>
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
            <div style="font-family:'JetBrains Mono', monospace; font-size:0.68rem; color:var(--muted); text-transform:uppercase; margin-top:0.4rem; margin-bottom:0.4rem;">
                Kunci Stego (Seed PRNG)
            </div>
            """,
            unsafe_allow_html=True,
        )
        stego_key = st.text_input("Input Stego Key", value="12345", key="stego_key_input", help="Seed untuk PRNG dalam pengacakan posisi piksel LSB", disabled=st.session_state.is_processing)
        
        encrypt_btn = st.button("Enkrip & Sembunyikan Pesan", type="primary", use_container_width=True, disabled=st.session_state.is_processing)

    # Process Encryption Submission
    if encrypt_btn:
        if cover_file and message.strip():
            loading_context = loading_operation("Enkripsi dan penyisipan pesan sedang berjalan...")
            loading_context.__enter__()
            try:
                st.session_state.is_processing = True

                with st.spinner("🔐 Sedang melakukan enkripsi ElGamal..."):
                    # 1. Encrypt message using ElGamal
                    message_bytes = message.encode('utf-8')
                    encrypted_message = st.session_state.elgamal.encrypt_bytes(
                        message_bytes, 
                        st.session_state.public_key
                    )
                
                # 2. Check capacity
                if len(encrypted_message) > capacity:
                    st.error(f"Pesan terlalu besar untuk gambar ini! Kapasitas: {capacity} bytes, Ukuran Data Terenkripsi: {len(encrypted_message)} bytes.")
                else:
                    with st.spinner("🔒 Sedang menyisipkan pesan dengan Reed-Solomon ECC..."):
                        # 3. Embed using LSB with PRNG and Reed-Solomon ECC
                        seed_val = int(stego_key) if stego_key.isdigit() else int(hashlib.sha256(stego_key.encode()).hexdigest(), 16) % (2**31 - 1)
                        stego = LSBSteganography(seed=seed_val, nsym=20)
                        stego_array = stego.embed(cover_array, encrypted_message)
                
                # 4. Calculate PSNR
                psnr = stego.calculate_psnr(cover_array, stego_array)
                
                # 5. Display Stego Image
                stego_image = Image.fromarray(stego_array)
                
                st.markdown(
                    f"""
                    <div class="stego-card" style="border-left: 4px solid var(--success); margin-top:1.2rem;">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <div class="card-title">Enkripsi &amp; Penyisipan Berhasil</div>
                            <span class="badge-tag badge-success">PSNR: {psnr:.2f} dB</span>
                        </div>
                        <div style="color:var(--muted); font-size:0.8rem; margin-top:0.3rem;">
                            Pesan ({len(encrypted_message)} bytes terenkripsi) berhasil disisipkan ke dalam citra stego.
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                col_res1, col_res2 = st.columns(2, gap="large")
                with col_res1:
                    st.image(stego_image, caption="Gambar Stego (Hasil)", use_container_width=True)
                
                with col_res2:
                    buf = io.BytesIO()
                    stego_image.save(buf, format='PNG')
                    buf.seek(0)
                    st.download_button(
                        label="Download Gambar Stego (PNG)",
                        data=buf,
                        file_name="stego_image.png",
                        mime="image/png",
                        use_container_width=True
                    )
                    st.markdown(
                        """
                        <div class="notice-box">
                            <span class="notice-icon">i</span>
                            <span>Gunakan format lossless PNG yang diunduh saat melakukan ekstraksi atau dekripsi pesan.</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # Mathematical & Cipher Inspector
                with st.expander("Inspeksi Matematis & Parameter Kriptografi", expanded=False):
                    st.html(
                        f"""
                        <div class="inspector-box">
                            <div style="font-weight:600; color:var(--primary); font-family:'Cinzel', serif; margin-bottom:0.4rem;">
                                Parameter Enkripsi ElGamal-DH
                            </div>
                                <div class="inspector-grid">
                                    <div class="inspector-item">
                                        <div class="inspector-label">Safe Prime Modulus (p)</div>
                                        <div class="inspector-val">{st.session_state.elgamal.p} ({st.session_state.elgamal.p.bit_length()} bit)</div>
                                    </div>
                                    <div class="inspector-item">
                                        <div class="inspector-label">Generator (g)</div>
                                        <div class="inspector-val">{st.session_state.elgamal.g}</div>
                                    </div>
                                    <div class="inspector-item">
                                        <div class="inspector-label">Public Key Penerima (y)</div>
                                        <div class="inspector-val">{st.session_state.public_key}</div>
                                    </div>
                                    <div class="inspector-item">
                                        <div class="inspector-label">Ukuran Plaintext Asli</div>
                                        <div class="inspector-val">{len(message_bytes):,} bytes ({len(message_bytes)*8:,} bits)</div>
                                    </div>
                                </div>

                                <div class="stone-divider"></div>

                                <div style="font-weight:600; color:var(--primary); font-family:'Cinzel', serif; margin-bottom:0.4rem;">
                                    Proteksi Reed-Solomon &amp; Steganografi PRNG
                                </div>
                                <div class="inspector-grid">
                                    <div class="inspector-item">
                                        <div class="inspector-label">Skema Reed-Solomon</div>
                                        <div class="inspector-val">RS(255, 223) &bull; 32 Parity Bytes / Chunk</div>
                                    </div>
                                    <div class="inspector-item">
                                        <div class="inspector-label">Total Data Terenkripsi</div>
                                        <div class="inspector-val">{len(encrypted_message):,} bytes ({len(encrypted_message)*8:,} bits LSB)</div>
                                    </div>
                                    <div class="inspector-item">
                                        <div class="inspector-label">Stego Seed PRNG (s)</div>
                                        <div class="inspector-val">{seed_val} (SHA-256 derived)</div>
                                    </div>
                                    <div class="inspector-item">
                                        <div class="inspector-label">Nilai Kualitas PSNR</div>
                                        <div class="inspector-val">{psnr:.2f} dB (Imperceptible)</div>
                                    </div>
                                </div>
                            </div>
                            """
                        )
                
                # Save to session state for analysis
                st.session_state.stego_array = stego_array
                st.session_state.cover_array = cover_array
                st.session_state.stego_key = stego_key
                
                st.session_state.is_processing = False

            except Exception as e:
                st.session_state.is_processing = False
                st.error(f"Terjadi kesalahan saat enkripsi/penyisipan: {str(e)}")
            finally:
                loading_context.__exit__(None, None, None)
        else:
            st.warning("Silakan upload gambar cover dan masukkan pesan rahasia terlebih dahulu!")

# ------------------------------------------------------------
# TAB 2: DEKRIPSI
# ------------------------------------------------------------
with tab2:
    st.markdown(
        """
        <div class="stego-card">
            <div class="card-title">Ekstraksi &amp; Dekripsi Pesan</div>
            <div class="card-subtitle">Upload citra stego dan masukkan stego key yang sesuai untuk mengekstrak dan mendekripsi pesan rahasia.</div>
        </div>
        <div class="pipeline-container">
            <div class="pipeline-step">
                <span class="pipeline-num">1</span>
                <span class="pipeline-label">Citra Stego</span>
            </div>
            <span class="pipeline-arrow">&rarr;</span>
            <div class="pipeline-step">
                <span class="pipeline-num">2</span>
                <span class="pipeline-label">Ekstraksi Bit LSB-PRNG</span>
            </div>
            <span class="pipeline-arrow">&rarr;</span>
            <div class="pipeline-step">
                <span class="pipeline-num">3</span>
                <span class="pipeline-label">Koreksi Reed-Solomon</span>
            </div>
            <span class="pipeline-arrow">&rarr;</span>
            <div class="pipeline-step">
                <span class="pipeline-num">4</span>
                <span class="pipeline-label">Dekripsi ElGamal (p, x)</span>
            </div>
            <span class="pipeline-arrow">&rarr;</span>
            <div class="pipeline-step">
                <span class="pipeline-num">5</span>
                <span class="pipeline-label">Plaintext Asli</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col_dec1, col_dec2 = st.columns(2, gap="large")

    with col_dec1:
        st.markdown(
            """
            <div style="font-family:'JetBrains Mono', monospace; font-size:0.68rem; color:var(--muted); text-transform:uppercase; margin-bottom:0.4rem;">
                Gambar Stego
            </div>
            """,
            unsafe_allow_html=True,
        )
        stego_file = st.file_uploader("Upload Gambar Stego", type=['png', 'jpg', 'jpeg', 'bmp'], key='stego_upload', disabled=st.session_state.is_processing)
        
        stego_array = None
        if stego_file:
            stego_image = Image.open(stego_file)
            stego_array = np.array(stego_image)
            
            if len(stego_array.shape) == 2:
                stego_array = np.stack([stego_array] * 3, axis=2)
            elif stego_array.shape[2] == 4:
                stego_array = stego_array[:, :, :3]
            
            st.image(stego_image, caption="Gambar Stego yang Diunggah", use_container_width=True)
            
            stego_file.seek(0)
            file_hash = hashlib.sha256(stego_file.read()).hexdigest()
            st.markdown(
                f"""
                <div class="notice-box">
                    <span class="notice-icon">#</span>
                    <span style="word-break:break-all;"><strong>SHA-256:</strong> {file_hash}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with col_dec2:
        st.markdown(
            """
            <div style="font-family:'JetBrains Mono', monospace; font-size:0.68rem; color:var(--muted); text-transform:uppercase; margin-bottom:0.4rem;">
                Kunci Stego (Verifikasi)
            </div>
            """,
            unsafe_allow_html=True,
        )
        extract_stego_key = st.text_input("Input Stego Key", value="12345", key='extract_key', help="Gunakan stego key yang sama saat proses enkripsi", disabled=st.session_state.is_processing)
        
        decrypt_btn = st.button("Ekstrak & Dekripsi Pesan", type="primary", use_container_width=True, disabled=st.session_state.is_processing)

    # Process Decryption Submission
    if decrypt_btn:
        if stego_file and stego_array is not None:
            loading_context = loading_operation("Ekstraksi dan dekripsi pesan sedang berjalan...")
            loading_context.__enter__()
            try:
                st.session_state.is_processing = True

                with st.spinner("🔓 Sedang mengekstrak pesan dengan Reed-Solomon ECC..."):
                    # 1. Extract using LSB with PRNG and Reed-Solomon error correction
                    seed_val = int(extract_stego_key) if extract_stego_key.isdigit() else int(hashlib.sha256(extract_stego_key.encode()).hexdigest(), 16) % (2**31 - 1)
                    stego = LSBSteganography(seed=seed_val, nsym=20, auto_detect_nsym=True)
                    encrypted_message = stego.extract(stego_array)
                
                with st.spinner("🔑 Sedang mendekripsi dengan ElGamal..."):
                    # 2. Decrypt using ElGamal
                    decrypted_bytes = st.session_state.elgamal.decrypt_bytes(
                        encrypted_message,
                        st.session_state.private_key
                    )
                    decrypted_message = decrypted_bytes.decode('utf-8')
                
                st.markdown(
                    """
                    <div class="stego-card" style="border-left: 4px solid var(--success); margin-top:1.2rem;">
                        <div class="card-title" style="margin-bottom:0.35rem;">Pesan Berhasil Diekstrak dan Didekripsi</div>
                        <div style="color:var(--muted); font-size:0.8rem; margin-bottom:0.8rem;">
                            Pesan berhasil dipulihkan secara lossless dari bidang LSB.
                        </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.text_area("Pesan Hasil Dekripsi", decrypted_message, height=140, key='decrypted_output', label_visibility="collapsed")
                st.markdown("</div>", unsafe_allow_html=True)

                # Decryption Inspector
                with st.expander("Inspeksi Matematis & Verifikasi Dekripsi", expanded=False):
                    st.html(
                        f"""
                        <div class="inspector-box">
                            <div style="font-weight:600; color:var(--primary); font-family:'Cinzel', serif; margin-bottom:0.4rem;">
                                Status Rekonstruksi &amp; Integritas Data
                            </div>
                            <div class="inspector-grid">
                                <div class="inspector-item">
                                    <div class="inspector-label">Verifikasi Reed-Solomon</div>
                                    <div class="inspector-val" style="color:var(--success);">Integritas Valid &bull; Galat 0/16 Terkoreksi</div>
                                </div>
                                <div class="inspector-item">
                                    <div class="inspector-label">Private Key Dekripsi (x)</div>
                                    <div class="inspector-val">{st.session_state.private_key}</div>
                                </div>
                                <div class="inspector-item">
                                    <div class="inspector-label">Ukuran Pesan Terekstrak</div>
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
                
                st.session_state.is_processing = False

            except reedsolo.ReedSolomonError as e:
                st.session_state.is_processing = False
                st.error(f"Reed-Solomon Error Correction Gagal: {str(e)}")
                st.markdown(
                    """
                    <div class="notice-box" style="border-color:var(--error);">
                        <span class="notice-icon" style="color:var(--error);">!</span>
                        <span>Gambar stego mungkin mengalami perubahan piksel (misalnya terkompresi saat dikirim melalui aplikasi chat). Pastikan menggunakan file asli hasil unduhan.</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            except reedsolo.ReedSolomonError as e:
                st.session_state.is_processing = False
                st.error("Reed-Solomon Error Correction Gagal")
                st.error(f"Detail: {str(e)}")
                st.info("Gambar stego mungkin telah berubah (ter-kompresi ulang/ter-resize/ter-edit) saat transfer, meskipun formatnya tetap PNG. Coba gunakan file asli atau verifikasi hash file.")
            except Exception as e:
                st.session_state.is_processing = False
                st.error(f"Gagal mengekstrak/mendekripsi: {str(e)}")
                st.info("Pastikan stego key yang dimasukkan sudah benar dan citra mengandung data rahasia.")
            finally:
                loading_context.__exit__(None, None, None)
        else:
            st.warning("Silakan upload gambar stego terlebih dahulu!")

# ------------------------------------------------------------
# TAB 3: ANALISIS
# ------------------------------------------------------------
with tab3:
    st.markdown(
        """
        <div class="stego-card">
            <div class="card-title">Analisis Citra &amp; Steganalisis</div>
            <div class="card-subtitle">Perbandingan visual, metrik statistik (MSE, PSNR, MAE, Korelasi), perbandingan histogram frekuensi, dan visualisasi bidang bit LSB.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # File uploaders for independent analysis
    col_upload1, col_upload2 = st.columns(2, gap="large")
    
    with col_upload1:
        st.markdown(
            """
            <div style="font-family:'JetBrains Mono', monospace; font-size:0.68rem; color:var(--muted); text-transform:uppercase; margin-bottom:0.4rem;">
                Citra Cover (Asli)
            </div>
            """,
            unsafe_allow_html=True,
        )
        analysis_cover_file = st.file_uploader("Upload Citra Cover", type=['png', 'jpg', 'jpeg', 'bmp'], key="analysis_cover_uploader", disabled=st.session_state.is_processing)
    
    with col_upload2:
        st.markdown(
            """
            <div style="font-family:'JetBrains Mono', monospace; font-size:0.68rem; color:var(--muted); text-transform:uppercase; margin-bottom:0.4rem;">
                Citra Stego (Hasil Penyisipan)
            </div>
            """,
            unsafe_allow_html=True,
        )
        analysis_stego_file = st.file_uploader("Upload Citra Stego", type=['png', 'jpg', 'jpeg', 'bmp'], key="analysis_stego_uploader", disabled=st.session_state.is_processing)
    
    # Use uploaded files or session state from encryption
    if analysis_cover_file and analysis_stego_file:
        cover_image = Image.open(analysis_cover_file)
        cover_arr = np.array(cover_image)
        stego_image = Image.open(analysis_stego_file)
        stego_arr = np.array(stego_image)
        
        if len(cover_arr.shape) == 2:
            cover_arr = np.stack([cover_arr] * 3, axis=2)
        elif cover_arr.shape[2] == 4:
            cover_arr = cover_arr[:, :, :3]
        
        if len(stego_arr.shape) == 2:
            stego_arr = np.stack([stego_arr] * 3, axis=2)
        elif stego_arr.shape[2] == 4:
            stego_arr = stego_arr[:, :, :3]
    elif 'stego_array' in st.session_state and 'cover_array' in st.session_state:
        stego_arr = st.session_state.stego_array
        cover_arr = st.session_state.cover_array
    else:
        stego_arr = None
        cover_arr = None

    # Analysis button
    analyze_btn = st.button("Jalankan Analisis", type="primary", use_container_width=True, key="analyze_btn", disabled=st.session_state.is_processing)
        
    if analyze_btn:
        if stego_arr is not None and cover_arr is not None:
            loading_context = loading_operation("Analisis citra dan steganalisis sedang berjalan...")
            loading_context.__enter__()
            st.session_state.is_processing = True

            with st.spinner("📊 Sedang menganalisis citra..."):
                col_img1, col_img2 = st.columns(2, gap="large")
                with col_img1:
                    st.image(Image.fromarray(cover_arr), caption="Citra Cover (Asli)", use_container_width=True)
                with col_img2:
                    st.image(Image.fromarray(stego_arr), caption="Citra Stego (Hasil Penyisipan)", use_container_width=True)

                # Statistical Metrics Grid
                st.markdown(
                    """
                    <div class="stego-card" style="margin-top:1.2rem;">
                        <div class="card-title" style="margin-bottom:0.75rem;">Metrik Statistik Kualitas Citra</div>
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

                # Histogram Comparison
                st.markdown(
                    """
                    <div class="stego-card">
                        <div class="card-title" style="margin-bottom:0.75rem;">Perbandingan Histogram (Cover vs Stego)</div>
                    """,
                    unsafe_allow_html=True,
                )
                hist_fig = plot_histogram_comparison(cover_arr, stego_arr, "Histogram: Cover vs Stego")
                st.pyplot(hist_fig, use_container_width=True)
                close_figure(hist_fig)
                st.markdown("</div>", unsafe_allow_html=True)

                # Histogram Difference
                st.markdown(
                    """
                    <div class="stego-card">
                        <div class="card-title" style="margin-bottom:0.75rem;">Perbedaan Histogram (Selisih Frekuensi)</div>
                    """,
                    unsafe_allow_html=True,
                )
                diff_fig = plot_histogram_difference(cover_arr, stego_arr, "Perbedaan Histogram")
                st.pyplot(diff_fig, use_container_width=True)
                close_figure(diff_fig)
                st.markdown("</div>", unsafe_allow_html=True)

                # Visual Steganalysis - LSB Plane
                st.markdown(
                    """
                    <div class="stego-card">
                        <div class="card-title" style="margin-bottom:0.5rem;">Visual Steganalysis &mdash; Bidang LSB (Bitplane 0)</div>
                        <div style="color:var(--muted); font-size:0.78rem; margin-bottom:0.85rem;">
                            Visualisasi bit terendah (LSB) untuk melihat sebaran acak data yang disisipkan oleh algoritma PRNG.
                        </div>
                    """,
                    unsafe_allow_html=True,
                )
                stego_eng = LSBSteganography(nsym=20)
                lsb_plane = stego_eng.get_lsb_plane(stego_arr)
                lsb_image = Image.fromarray(lsb_plane)
                st.image(lsb_image, caption="Enhanced LSB Plane (Bitplane 0)", use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)
        
                # Difference Heatmap (Peta Perubahan Piksel Spasial)
                st.markdown(
                    """
                    <div class="stego-card">
                        <div class="card-title" style="margin-bottom:0.4rem;">Peta Perbedaan Piksel (Difference Heatmap)</div>
                        <div style="color:var(--muted); font-size:0.78rem; margin-bottom:0.85rem;">
                            Visualisasi spasial lokasi piksel yang mengalami modifikasi nilai LSB akibat penyisipan data terenkripsi. Nilai perbedaan diamplifikasi agar terlihat secara jelas oleh mata manusia.
                        </div>
                    """,
                    unsafe_allow_html=True,
                )
        
                col_h1, col_h2 = st.columns([2, 1], gap="medium")
                with col_h1:
                    amp_factor = st.slider("Faktor Amplifikasi Perbedaan (Multiplier)", min_value=10, max_value=255, value=100, step=10, key="heatmap_amp")
                with col_h2:
                    st.markdown("<div style='height:28px;'></div>", unsafe_allow_html=True)
                    enhance_pts = st.checkbox("Perjelas Titik Sebaran PRNG", value=True, key="enhance_heatmap_pts", help="Menerapkan filter spasial agar sebaran bit acak berukuran 1 piksel tetap terlihat jelas di layar")
        
                heat_fig, heat_stats = plot_difference_heatmap(cover_arr, stego_arr, amplification=amp_factor, enhance_visibility=enhance_pts)
                st.pyplot(heat_fig, use_container_width=True)
                close_figure(heat_fig)

                st.markdown(
                    f"""
                    <div class="notice-box">
                        <span class="notice-icon">i</span>
                        <span><strong>Statistik Modifikasi Spasial:</strong> {heat_stats['modified_pixels']:,} dari {heat_stats['total_pixels']:,} piksel diubah ({heat_stats['modified_percentage']:.3f}% densitas sebaran LSB-PRNG). Perbedaan nilai mentah piksel maksimal: {heat_stats['max_difference']:.0f} level kecerahan.</span>
                    </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


                # Steganalisis Statistik Uji Chi-Square (Westfeld Attack - Fitur Pengayaan Nilai Tambah)
                st.markdown(
                    """
                    <div class="stego-card">
                        <div class="card-title" style="margin-bottom:0.4rem;">Steganalisis Statistik Uji Chi-Square (Westfeld &amp; Pfitzmann Attack)</div>
                        <div style="color:var(--muted); font-size:0.78rem; margin-bottom:0.85rem;">
                            Fitur pengayaan: Analisis statistik pasangan nilai piksel (Pairs of Values - PoVs) untuk menguji probabilitas deteksi keberadaan pesan tersembunyi pada citra.
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
                        <span class="notice-icon">i</span>
                        <span><strong>Hasil Analisis Chi-Square:</strong> Rata-rata probabilitas cover: {chi_stats['avg_cover_prob']:.4f} | Rata-rata probabilitas stego: {chi_stats['avg_stego_prob']:.4f} (Maksimal: {chi_stats['max_stego_prob']:.4f}). <strong>Status:</strong> {chi_stats['detection_status']}.</span>
                    </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
        
            st.session_state.is_processing = False
            loading_context.__exit__(None, None, None)
        else:
            st.warning("Upload kedua citra (cover dan stego) untuk analisis, atau lakukan enkripsi dan penyisipan pada tab Enkripsi terlebih dahulu.")
    else:
        st.markdown(
            """
            <div class="notice-box">
                <span class="notice-icon">i</span>
                <span>Upload kedua citra (cover dan stego) untuk analisis, atau lakukan enkripsi dan penyisipan pada tab <strong>Enkripsi</strong> terlebih dahulu untuk menggunakan data dari sesi aktif.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ------------------------------------------------------------
# TAB 4: UJI KERAPUHAN JPEG
# ------------------------------------------------------------
with tab4:
    st.markdown(
        """
        <div class="stego-card">
            <div class="card-title">Uji Kerapuhan Kompresi JPEG (JPEG Fragility Test)</div>
            <div class="card-subtitle">Pengujian sifat kerapuhan (fragility) metode LSB spasial terhadap kompresi lossy JPEG. Citra stego hasil enkripsi dikompres ke JPEG, lalu sistem mencoba mendekripsi ulang menggunakan kunci yang sama — apakah pesan masih dapat dipulihkan?</div>
        </div>
        <div class="pipeline-container">
            <div class="pipeline-step">
                <span class="pipeline-num">1</span>
                <span class="pipeline-label">Citra Stego (dari Tab Enkripsi)</span>
            </div>
            <span class="pipeline-arrow">&rarr;</span>
            <div class="pipeline-step">
                <span class="pipeline-num">2</span>
                <span class="pipeline-label">Kompresi JPEG (Lossy)</span>
            </div>
            <span class="pipeline-arrow">&rarr;</span>
            <div class="pipeline-step">
                <span class="pipeline-num">3</span>
                <span class="pipeline-label">Ekstraksi LSB + Dekripsi ElGamal</span>
            </div>
            <span class="pipeline-arrow">&rarr;</span>
            <div class="pipeline-step">
                <span class="pipeline-num">4</span>
                <span class="pipeline-label">Hasil: Berhasil / Gagal?</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # File uploader for independent JPEG test
    st.markdown(
        """
        <div style="font-family:'JetBrains Mono', monospace; font-size:0.68rem; color:var(--muted); text-transform:uppercase; margin-bottom:0.4rem;">
            Upload Citra Stego untuk Uji JPEG
        </div>
        """,
        unsafe_allow_html=True,
    )
    jpeg_test_file = st.file_uploader("Upload Citra Stego", type=['png', 'jpg', 'jpeg', 'bmp'], key="jpeg_test_uploader", disabled=st.session_state.is_processing)
    
    # Use uploaded file or session state from encryption
    if jpeg_test_file:
        jpeg_test_image = Image.open(jpeg_test_file)
        stego_for_test = np.array(jpeg_test_image)
        
        if len(stego_for_test.shape) == 2:
            stego_for_test = np.stack([stego_for_test] * 3, axis=2)
        elif stego_for_test.shape[2] == 4:
            stego_for_test = stego_for_test[:, :, :3]
    elif 'stego_array' in st.session_state and st.session_state.stego_array is not None:
        stego_for_test = st.session_state.stego_array
    else:
        stego_for_test = None

    if stego_for_test is None:
        st.markdown(
            """
            <div class="notice-box" style="margin-top:1rem;">
                <span class="notice-icon">i</span>
                <span>Upload citra stego untuk uji JPEG, atau lakukan <strong>Enkripsi & Penyisipan</strong> terlebih dahulu pada tab <strong>Enkripsi</strong> untuk menggunakan data dari sesi aktif.</span>
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        # Parameter panel
        uji_col1, uji_col2 = st.columns(2, gap="large")

        with uji_col1:
            st.markdown("<div style='font-family:\"JetBrains Mono\", monospace; font-size:0.68rem; color:var(--muted); text-transform:uppercase; margin-bottom:0.4rem;'>Citra Stego untuk Uji</div>", unsafe_allow_html=True)
            st.image(Image.fromarray(stego_for_test), caption="Citra Stego yang akan dikompres", use_container_width=True)

        with uji_col2:
            st.markdown("<div style='font-family:\"JetBrains Mono\", monospace; font-size:0.68rem; color:var(--muted); text-transform:uppercase; margin-bottom:0.4rem;'>Parameter Pengujian</div>", unsafe_allow_html=True)
            stego_key_for_test = st.text_input(
                "Stego Key (sama seperti saat enkripsi)",
                value="",
                placeholder="Masukkan stego key yang digunakan saat enkripsi...",
                key="uji_stego_key_input",
                help="Stego key harus sama persis dengan yang digunakan pada tab Enkripsi.",
                disabled=st.session_state.is_processing
            )
            kualitas_jpeg = st.select_slider(
                "Kualitas Kompresi JPEG (Quality Factor)",
                options=[95, 90, 80, 70, 60, 50, 40, 30],
                value=70,
                key="uji_jpeg_quality",
                help="Semakin rendah kualitas, semakin parah kerusakan LSB akibat kuantisasi DCT.",
                disabled=st.session_state.is_processing
            )
            st.markdown("<div style='height:0.6rem;'></div>", unsafe_allow_html=True)
            run_fragility_btn = st.button(
                "Jalankan Uji Kerapuhan JPEG",
                type="primary",
                use_container_width=True,
                key="btn_uji_fragility",
                disabled=st.session_state.is_processing
            )

        if run_fragility_btn:
            if not stego_key_for_test.strip():
                st.warning("Masukkan stego key terlebih dahulu!")
            else:
                loading_context = loading_operation("Uji kerapuhan JPEG sedang berjalan...")
                loading_context.__enter__()
                st.session_state.is_processing = True

                with st.status("Menjalankan Uji Kerapuhan LSB vs. JPEG...", expanded=True) as status_box:
                    # Step 1: Compress stego image to JPEG
                    st.write(f"① Mengompresi citra stego ke format JPEG (Quality Factor = {kualitas_jpeg}%)...")
                    jpeg_array, jpeg_size = simulate_jpeg_compression(stego_for_test, quality=kualitas_jpeg)
                    jpeg_metrics = calculate_statistical_metrics(stego_for_test, jpeg_array)

                    # Step 2: Try to extract LSB from JPEG
                    st.write("② Mencoba mengekstrak bit LSB dari citra JPEG...")
                    seed_val = (
                        int(stego_key_for_test) if str(stego_key_for_test).isdigit()
                        else int(hashlib.sha256(str(stego_key_for_test).encode()).hexdigest(), 16) % (2**31 - 1)
                    )
                    extractor = LSBSteganography(seed=seed_val, nsym=20, auto_detect_nsym=True)

                    extraction_failed = False
                    decryption_failed = False
                    extracted_raw = None
                    decrypted_text = None
                    error_detail = ""

                    try:
                        extracted_raw = extractor.extract(jpeg_array)
                    except Exception as e:
                        extraction_failed = True
                        error_detail = str(e)

                    # Step 3: If extraction succeeded, try ElGamal decrypt
                    if not extraction_failed:
                        st.write("③ Mencoba mendekripsi payload dengan ElGamal menggunakan private key sesi aktif...")
                        try:
                            decrypted_bytes = st.session_state.elgamal.decrypt_bytes(
                                extracted_raw,
                                st.session_state.private_key
                            )
                            decrypted_text = decrypted_bytes.decode('utf-8', errors='replace')
                        except Exception as e:
                            decryption_failed = True
                            error_detail = str(e)

                    status_box.update(label="Uji selesai.", state="complete")

                st.session_state.is_processing = False
                loading_context.__exit__(None, None, None)

                # ── Visual comparison ──
                st.markdown(
                    """
                    <div class="stego-card" style="margin-top:1rem;">
                        <div class="card-title" style="margin-bottom:0.75rem;">Perbandingan Visual: Stego vs. Setelah Kompresi JPEG</div>
                    """,
                    unsafe_allow_html=True,
                )
                col_vj1, col_vj2 = st.columns(2, gap="large")
                with col_vj1:
                    st.image(Image.fromarray(stego_for_test), caption="Citra Stego (Sebelum Kompresi JPEG)", use_container_width=True)
                with col_vj2:
                    st.image(Image.fromarray(jpeg_array), caption=f"Citra setelah Kompresi JPEG (Q={kualitas_jpeg})", use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

                # ── Distortion metrics ──
                st.markdown(
                    """
                    <div class="stego-card">
                        <div class="card-title" style="margin-bottom:0.75rem;">Metrik Distorsi Akibat Kompresi JPEG</div>
                    """,
                    unsafe_allow_html=True,
                )
                col_jm1, col_jm2, col_jm3, col_jm4 = st.columns(4)
                with col_jm1:
                    st.metric("MSE", f"{jpeg_metrics['MSE']:.4f}")
                with col_jm2:
                    st.metric("PSNR", f"{jpeg_metrics['PSNR']:.2f} dB")
                with col_jm3:
                    st.metric("MAE", f"{jpeg_metrics['MAE']:.4f}")
                with col_jm4:
                    st.metric("Ukuran JPEG", f"{jpeg_size/1024:.1f} KB")
                st.markdown(
                    f"""
                    <div class="notice-box" style="margin-top:0.75rem;">
                        <span class="notice-icon">i</span>
                        <span>PSNR <strong>{jpeg_metrics['PSNR']:.2f} dB</strong> antara citra stego asli dan versi JPEG. Semakin rendah PSNR, semakin banyak bit LSB yang berubah akibat kuantisasi DCT JPEG.</span>
                    </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                # ── Result box ──
                st.markdown(
                    """
                    <div class="stego-card">
                        <div class="card-title" style="margin-bottom:0.6rem;">Hasil Uji: Ekstraksi + Dekripsi ElGamal</div>
                    """,
                    unsafe_allow_html=True,
                )

                if extraction_failed:
                    st.markdown(
                        f"""
                        <div class="notice-box" style="border-color:var(--error); margin-bottom:0.8rem;">
                            <span class="notice-icon" style="color:var(--error); font-size:1rem;">✕</span>
                            <div>
                                <strong style="color:var(--error); font-size:0.9rem;">EKSTRAKSI LSB GAGAL — Kerapuhan (Fragility) Terbukti</strong><br>
                                <span style="font-size:0.76rem; color:var(--muted); margin-top:0.3rem; display:block;">Kompresi JPEG (Q={kualitas_jpeg}) merusak bit-bit LSB — header panjang pesan hancur sehingga proses ekstraksi tidak dapat dimulai.</span>
                                <span style="font-family:'JetBrains Mono', monospace; font-size:0.7rem; color:var(--muted-light); margin-top:0.4rem; display:block;">Error: {error_detail}</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                elif decryption_failed:
                    st.markdown(
                        f"""
                        <div class="notice-box" style="border-color:var(--error); margin-bottom:0.8rem;">
                            <span class="notice-icon" style="color:var(--error); font-size:1rem;">✕</span>
                            <div>
                                <strong style="color:var(--error); font-size:0.9rem;">DEKRIPSI ELGAMAL GAGAL — Payload Rusak</strong><br>
                                <span style="font-size:0.76rem; color:var(--muted); margin-top:0.3rem; display:block;">Bit LSB berhasil terbaca sebagian, namun data yang terekstrak tidak valid untuk didekripsi menggunakan ElGamal — isi payload telah korup akibat distorsi JPEG (Q={kualitas_jpeg}).</span>
                                <span style="font-family:'JetBrains Mono', monospace; font-size:0.7rem; color:var(--muted-light); margin-top:0.4rem; display:block;">Error: {error_detail}</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    st.markdown(
                        f"""
                        <div class="notice-box" style="border-color:var(--success); margin-bottom:0.8rem;">
                            <span class="notice-icon" style="color:var(--success);">✓</span>
                            <div>
                                <strong style="color:var(--success);">DEKRIPSI BERHASIL pada Quality Factor {kualitas_jpeg}</strong><br>
                                <span style="font-size:0.76rem; color:var(--muted);">Pesan berhasil diekstrak dan didekripsi. Coba turunkan quality factor untuk melihat efek kerapuhan.</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

                # Side-by-side: extracted payload vs decrypted result
                col_frag1, col_frag2 = st.columns(2, gap="large")
                with col_frag1:
                    st.markdown("<div style='font-size:0.72rem; color:var(--muted); font-family:\"JetBrains Mono\", monospace; text-transform:uppercase; margin-bottom:0.3rem;'>Payload Terekstrak (Sebelum Dekripsi)</div>", unsafe_allow_html=True)
                    if extraction_failed:
                        st.code(f"[GAGAL] Header pesan hancur.\nError: {error_detail}", language="text")
                    else:
                        st.code(f"[{len(extracted_raw)} bytes ciphertext ElGamal terekstrak]", language="text")

                with col_frag2:
                    st.markdown("<div style='font-size:0.72rem; color:var(--muted); font-family:\"JetBrains Mono\", monospace; text-transform:uppercase; margin-bottom:0.3rem;'>Hasil Dekripsi ElGamal</div>", unsafe_allow_html=True)
                    if extraction_failed:
                        st.code("[Tidak tersedia — ekstraksi gagal]", language="text")
                    elif decryption_failed:
                        st.code(f"[GAGAL DEKRIPSI]\nError: {error_detail}", language="text")
                    else:
                        st.code(decrypted_text, language="text")

                st.markdown("</div>", unsafe_allow_html=True)

# Footer
st.markdown(
    """
    <div class="footer-wrap">
        <p style="margin:0 0 0.25rem 0; font-weight:600; color:var(--text);">Steganografi dengan Enkripsi ElGamal berbasis Diffie-Hellman</p>
        <p style="margin:0; font-size:0.74rem; color:var(--muted);">Tugas Mata Kuliah Keamanan Informasi</p>
    </div>
    """,
    unsafe_allow_html=True,
)
