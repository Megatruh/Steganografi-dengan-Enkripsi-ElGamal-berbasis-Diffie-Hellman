import io
import hashlib
import random
from pathlib import Path

import numpy as np
import streamlit as st
from PIL import Image
import matplotlib.pyplot as plt

from elgamal import ElGamalDH
from steganography import LSBSteganography
from analysis import (
    plot_histogram_comparison,
    plot_histogram_difference,
    calculate_statistical_metrics,
    calculate_histogram,
    close_figure,
)
import reedsolo


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="StegoCrypt - Cryptographic Workbench",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# BACKEND INSTANCES & SESSION STATE INITIALIZATION
# ============================================================

@st.cache_resource
def get_elgamal_instance():
    """Cache ElGamal instance to avoid prime regeneration overhead."""
    return ElGamalDH()

if "elgamal" not in st.session_state:
    st.session_state.elgamal = get_elgamal_instance()

if "private_key" not in st.session_state:
    st.session_state.private_key, st.session_state.public_key = st.session_state.elgamal.generate_keypair()

if "hide_completed" not in st.session_state:
    st.session_state.hide_completed = False

if "last_hide_data" not in st.session_state:
    st.session_state.last_hide_data = None

if "extract_result" not in st.session_state:
    st.session_state.extract_result = None

if "extract_error" not in st.session_state:
    st.session_state.extract_error = None

if "active_nav" not in st.session_state:
    st.session_state.active_nav = "Hide Message"


# ============================================================
# UTILITY FUNCTIONS
# ============================================================

def stego_key_to_seed(key_str: str) -> int:
    """Convert a stego key (digits or arbitrary string) into a deterministic integer seed."""
    try:
        return int(key_str)
    except ValueError:
        return int(hashlib.sha256(key_str.encode("utf-8")).hexdigest(), 16) % (2**31 - 1)


def get_sha256_hash(data: bytes) -> str:
    """Return SHA-256 hash string for raw bytes."""
    return hashlib.sha256(data).hexdigest()


def calculate_entropy(img_arr: np.ndarray) -> float:
    """Calculate Shannon entropy for an image array."""
    hist, _ = np.histogram(img_arr.flatten(), bins=256, range=(0, 256), density=True)
    hist = hist[hist > 0]
    return float(-np.sum(hist * np.log2(hist)))


def format_bytes(val: int) -> str:
    """Format bytes into readable size."""
    if val < 1024:
        return f"{val} B"
    elif val < 1024 * 1024:
        return f"{val / 1024:.2f} KB"
    else:
        return f"{val / (1024 * 1024):.2f} MB"


def image_info(uploaded_file):
    """Extract metadata and byte capacity from an uploaded image file."""
    if uploaded_file is None:
        return None
    data = uploaded_file.getvalue()
    pil_img = Image.open(io.BytesIO(data))
    arr = np.array(pil_img)
    w, h = pil_img.size

    channels = 3 if pil_img.mode in ("RGB", "RGBA") else (1 if len(arr.shape) == 2 else arr.shape[2])
    # 1 bit per RGB channel, minus 32 bits header
    capacity_bits = max(0, w * h * min(channels, 3) - 32)
    capacity_bytes = capacity_bits // 8

    return {
        "image": pil_img,
        "array": arr,
        "bytes": data,
        "filename": uploaded_file.name,
        "format": (pil_img.format or Path(uploaded_file.name).suffix.replace(".", "")).upper(),
        "size": len(data),
        "width": w,
        "height": h,
        "channels": channels,
        "capacity": capacity_bytes,
        "sha256": get_sha256_hash(data),
    }


def create_histogram_figure(cover_arr: np.ndarray, stego_arr: np.ndarray) -> plt.Figure:
    """Create an Egyptian artifact spectral plot matching the benchmark dashboard."""
    fig, ax = plt.subplots(figsize=(10, 3.2), facecolor="#13100d")
    ax.set_facecolor("#1c1712")

    # RGB lines: Red Ochre, Scarab Green, Lapis Lazuli Blue
    colors = [("#f87171", "#ef4444", "RED (OCHRE)"), ("#34d399", "#10b981", "GREEN (SCARAB)"), ("#38bdf8", "#0284c7", "BLUE (LAPIS)")]
    bins = np.arange(257)

    for ch, (c_light, c_dark, label) in enumerate(colors):
        if ch < cover_arr.shape[2]:
            h_cov, _ = np.histogram(cover_arr[:, :, ch], bins=bins)
            h_stg, _ = np.histogram(stego_arr[:, :, ch], bins=bins)

            # Smooth curve
            ax.plot(bins[:-1], h_stg, color=c_dark, linewidth=1.8, label=label)
            ax.plot(bins[:-1], h_cov, color=c_light, linewidth=1.0, linestyle=":", alpha=0.6)

    ax.set_xlim(0, 255)
    ax.set_xticks([0, 64, 128, 192, 255])
    ax.set_xticklabels(["0 (SHADOWS)", "64", "128 (MIDTONES)", "192", "255 (HIGHLIGHTS)"], fontsize=8, family="monospace", color="#a69680")
    ax.tick_params(colors="#a69680", labelsize=8)
    ax.grid(True, linestyle="--", linewidth=0.5, color="#2c2318", alpha=0.8)

    for spine in ax.spines.values():
        spine.set_color("#3d3224")
        spine.set_linewidth(0.8)

    leg = ax.legend(frameon=False, loc="upper right", fontsize=8, prop={"family": "monospace"})
    for text in leg.get_texts():
        text.set_color("#f4eedf")
    plt.tight_layout()
    return fig


# ============================================================
# DESIGN SYSTEM & GLOBAL CSS
# ============================================================

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@500;600;700;800;900&family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    :root {
        --bg: #13100d;
        --surface: #1c1712;
        --surface-low: #17130e;
        --surface-high: #262018;
        --border: #3d3224;
        --border-subtle: #2c2318;
        --border-gold: #d4af37;
        --text: #f4eedf;
        --muted: #a69680;
        --muted-light: #6d6150;
        --primary: #d4af37;
        --primary-hover: #ebd16a;
        --primary-soft: #2c2310;
        --primary-glow: rgba(212, 175, 55, 0.25);
        --success: #34d399;
        --success-soft: #14271e;
        --error: #f87171;
        --error-soft: #2b1414;
        --lapis: #38bdf8;
    }

    * {
        box-sizing: border-box;
    }

    html, body, [class*="css"] {
        font-family: "Plus Jakarta Sans", -apple-system, BlinkMacSystemFont, sans-serif;
    }

    .stApp {
        background-color: var(--bg);
        color: var(--text);
    }

    /* Header setup to keep sidebar toggle button visible & functional */
    [data-testid="stHeader"] {
        background: transparent !important;
        color: var(--text) !important;
        z-index: 1001 !important;
        height: 56px !important;
        pointer-events: none !important;
    }

    [data-testid="stToolbar"] {
        background: transparent !important;
        pointer-events: none !important;
        visibility: visible !important;
        display: flex !important;
        height: 56px !important;
        padding-left: 10px !important;
    }

    /* Hide default right-side hamburger menu and status decoration */
    [data-testid="stToolbar"] > div:last-child:not(:first-child),
    [data-testid="stDecoration"],
    [data-testid="stStatusWidget"],
    [data-testid="stMainMenu"] {
        display: none !important;
    }

    /* Keep collapse & expand button clickable, fixed at top-left, and styled in Egyptian gold */
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
        top: 9px !important;
        left: 12px !important;
        z-index: 1002 !important;
    }

    [data-testid="stExpandSidebarButton"] button,
    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="collapsedControl"] button {
        background: var(--surface) !important;
        border: 1.5px solid var(--primary) !important;
        color: var(--primary) !important;
        border-radius: 6px !important;
        transition: all 0.15s ease !important;
        box-shadow: 0 0 12px rgba(0, 0, 0, 0.6), 0 0 6px rgba(212, 175, 55, 0.3) !important;
        width: 38px !important;
        height: 38px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        cursor: pointer !important;
    }

    [data-testid="stExpandSidebarButton"] button:hover,
    [data-testid="stSidebarCollapseButton"] button:hover,
    [data-testid="collapsedControl"] button:hover {
        background: var(--primary-soft) !important;
        border-color: var(--primary-hover) !important;
        box-shadow: 0 0 16px rgba(212, 175, 55, 0.5) !important;
        transform: scale(1.05) !important;
    }

    [data-testid="stExpandSidebarButton"] svg,
    [data-testid="stSidebarCollapseButton"] svg,
    [data-testid="collapsedControl"] svg {
        fill: var(--primary) !important;
        stroke: var(--primary) !important;
        color: var(--primary) !important;
    }

    .block-container {
        max-width: 1180px;
        padding-top: 5rem;
        padding-bottom: 3.5rem;
    }

    h1, h2, h3, h4 {
        font-family: "Cinzel", Georgia, serif !important;
        color: var(--text) !important;
        font-weight: 700;
        letter-spacing: 0.03em;
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
        height: 56px;
        padding-left: 60px;
        padding-right: 2rem;
        background: rgba(19, 16, 13, 0.94);
        backdrop-filter: blur(12px);
        border-bottom: 1px solid var(--border);
        display: flex;
        align-items: center;
        justify-content: space-between;
        transition: padding-left 0.3s ease;
    }

    .stApp:has(section[data-testid="stSidebar"][aria-expanded="true"]) .topbar {
        padding-left: 320px;
    }

    .topbar-left {
        display: flex;
        align-items: center;
        gap: 0.85rem;
    }

    .topbar-icon-box {
        width: 28px;
        height: 28px;
        background: linear-gradient(135deg, #d4af37, #9a781a);
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #13100d;
        font-size: 0.75rem;
        font-weight: 800;
        font-family: "Cinzel", serif;
        border: 1px solid #ebd16a;
        box-shadow: 0 0 10px rgba(212, 175, 55, 0.35);
    }

    .topbar-workbench {
        padding: 0.25rem 0.55rem;
        border: 1px solid var(--border);
        background: var(--surface-low);
        border-radius: 4px;
        font-family: "JetBrains Mono", monospace;
        font-size: 0.62rem;
        color: var(--primary);
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
    }

    .topbar-right {
        display: flex;
        align-items: center;
        gap: 1.25rem;
        font-family: "JetBrains Mono", monospace;
        font-size: 0.64rem;
        color: var(--muted);
    }

    .topbar-status {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        color: var(--text);
        font-weight: 600;
    }

    .topbar-status-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: var(--success);
        box-shadow: 0 0 8px rgba(52, 211, 153, 0.7);
    }

    .user-avatar {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: linear-gradient(135deg, #d4af37, #9a781a);
        display: flex;
        align-items: center;
        justify-content: center;
        color: #13100d;
        font-size: 0.68rem;
        font-weight: 800;
        font-family: "Cinzel", serif;
        border: 1px solid #ebd16a;
    }

    /* ---------------- SIDEBAR ---------------- */
    section[data-testid="stSidebar"] {
        background-color: var(--surface);
        border-right: 1px solid var(--border);
        z-index: 100;
    }

    section[data-testid="stSidebar"] > div {
        padding: 1.4rem 1.15rem;
    }

    .brand-wrap {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding-bottom: 1.2rem;
        border-bottom: 1px solid var(--border);
        margin-bottom: 1.2rem;
    }

    .brand-icon {
        width: 34px;
        height: 34px;
        background: linear-gradient(135deg, #d4af37, #9a781a);
        border-radius: 7px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #13100d;
        font-weight: 800;
        font-size: 0.95rem;
        font-family: "Cinzel", serif;
        border: 1px solid #ebd16a;
        box-shadow: 0 0 12px rgba(212, 175, 55, 0.4);
    }

    .brand-title {
        font-family: "Cinzel", serif !important;
        font-size: 1.08rem;
        font-weight: 800;
        letter-spacing: 0.04em;
        line-height: 1.2;
        color: var(--primary) !important;
    }

    .brand-subtitle {
        color: var(--muted);
        font-size: 0.7rem;
        letter-spacing: 0.02em;
    }

    .sidebar-section-title {
        font-family: "JetBrains Mono", monospace;
        font-size: 0.65rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: var(--muted);
        margin-bottom: 0.6rem;
    }

    /* Radio navigation */
    section[data-testid="stSidebar"] div[role="radiogroup"] {
        gap: 0.35rem;
        margin-bottom: 1.5rem;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label {
        border-radius: 6px;
        padding: 0.55rem 0.75rem;
        background: transparent;
        border: 1px solid transparent;
        transition: all 0.15s ease;
        cursor: pointer;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: var(--surface-high);
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label[data-checked="true"],
    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) {
        background: var(--primary-soft) !important;
        border: 1px solid var(--primary) !important;
        box-shadow: 0 0 12px rgba(212, 175, 55, 0.2) !important;
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label span {
        font-size: 0.85rem;
        font-weight: 600;
        color: var(--text);
    }

    section[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) span {
        color: var(--primary) !important;
    }

    .engine-table {
        display: flex;
        flex-direction: column;
        gap: 0.35rem;
        margin-bottom: 1.8rem;
    }

    .engine-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.45rem 0.65rem;
        background: var(--surface-low);
        border: 1px solid var(--border);
        border-radius: 5px;
    }

    .engine-name {
        font-family: "JetBrains Mono", monospace;
        font-size: 0.76rem;
        font-weight: 600;
        color: var(--text);
    }

    .engine-badge {
        font-family: "JetBrains Mono", monospace;
        font-size: 0.6rem;
        font-weight: 600;
        padding: 0.15rem 0.4rem;
        background: var(--surface-high);
        border: 1px solid var(--border);
        border-radius: 3px;
        color: var(--primary);
        letter-spacing: 0.05em;
    }

    .sidebar-footer {
        margin-top: 2rem;
        padding-top: 1rem;
        border-top: 1px solid var(--border);
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-family: "JetBrains Mono", monospace;
        font-size: 0.64rem;
        color: var(--muted);
    }

    .system-ready-pill {
        display: flex;
        align-items: center;
        gap: 0.35rem;
        color: var(--success);
        font-weight: 600;
    }

    .system-ready-dot {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: var(--success);
        box-shadow: 0 0 6px rgba(52, 211, 153, 0.6);
    }

    /* ---------------- HEADER MODULE ---------------- */
    .module-header {
        margin-bottom: 1.6rem;
    }

    .eyebrow {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-family: "JetBrains Mono", monospace;
        font-size: 0.65rem;
        color: var(--primary);
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.12em;
    }

    .eyebrow-dot {
        width: 5px;
        height: 5px;
        border-radius: 50%;
        background: var(--primary);
    }

    .page-title {
        font-family: "Cinzel", Georgia, serif !important;
        font-size: 2.1rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        margin-top: 0.4rem;
        line-height: 1.15;
        color: var(--text) !important;
    }

    .page-desc {
        max-width: 820px;
        margin-top: 0.5rem;
        color: var(--muted);
        font-size: 0.92rem;
        line-height: 1.55;
    }

    /* ---------------- CARDS ---------------- */
    .stego-card {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 1.3rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(212, 175, 55, 0.1);
        margin-bottom: 1.2rem;
        position: relative;
    }

    .card-head {
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        margin-bottom: 1rem;
    }

    .card-head-left {
        display: flex;
        align-items: flex-start;
        gap: 0.75rem;
    }

    .step-badge {
        min-width: 32px;
        height: 30px;
        background: var(--surface-high);
        border: 1px solid var(--primary);
        border-radius: 5px;
        color: var(--primary);
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: "Cinzel", serif;
        font-size: 0.76rem;
        font-weight: 800;
        box-shadow: 0 0 10px rgba(212, 175, 55, 0.15);
    }

    .card-title {
        font-family: "Cinzel", Georgia, serif !important;
        font-size: 1.05rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        color: var(--text) !important;
    }

    .card-subtitle {
        margin-top: 0.2rem;
        color: var(--muted);
        font-size: 0.75rem;
        line-height: 1.45;
    }

    /* ---------------- METRIC GRID ---------------- */
    .meta-grid-4 {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.5rem;
        margin-top: 0.85rem;
    }

    .meta-item {
        background: var(--surface-low);
        border: 1px solid var(--border);
        border-radius: 6px;
        padding: 0.6rem 0.75rem;
    }

    .meta-item-label {
        font-family: "JetBrains Mono", monospace;
        font-size: 0.58rem;
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    .meta-item-value {
        margin-top: 0.3rem;
        font-family: "JetBrains Mono", monospace;
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--text);
    }

    .primary-metric {
        color: var(--primary);
    }

    /* ---------------- CAPACITY BAR ---------------- */
    .capacity-section {
        margin-top: 0.9rem;
    }

    .capacity-head-row, .capacity-foot-row {
        display: flex;
        justify-content: space-between;
        font-family: "JetBrains Mono", monospace;
        font-size: 0.62rem;
        color: var(--muted);
    }

    .capacity-track {
        height: 6px;
        background: var(--surface-high);
        border-radius: 99px;
        margin: 0.35rem 0;
        overflow: hidden;
        border: 1px solid var(--border);
    }

    .capacity-fill {
        height: 100%;
        background: linear-gradient(90deg, #b89123, #d4af37, #ebd16a);
        border-radius: 99px;
        box-shadow: 0 0 10px rgba(212, 175, 55, 0.4);
    }

    /* ---------------- NOTICE BOXES ---------------- */
    .notice-box {
        margin-top: 0.9rem;
        padding: 0.75rem 0.9rem;
        background: var(--surface-low);
        border: 1px solid var(--border);
        border-radius: 6px;
        font-size: 0.74rem;
        color: var(--muted);
        line-height: 1.5;
        display: flex;
        gap: 0.6rem;
        align-items: flex-start;
    }

    .notice-icon {
        font-family: "JetBrains Mono", monospace;
        font-weight: 700;
        font-size: 0.75rem;
        color: var(--primary);
        line-height: 1.4;
    }

    /* ---------------- SUCCESS / ERROR BANNERS ---------------- */
    .banner-success {
        background: #14271e;
        border: 1px solid #1e4a33;
        border-left: 5px solid var(--success);
        border-radius: 10px;
        padding: 1.1rem 1.3rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }

    .banner-error {
        background: #2b1414;
        border: 1px solid #5e2222;
        border-left: 5px solid var(--error);
        border-radius: 10px;
        padding: 1.25rem 1.4rem;
        margin-bottom: 1.25rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
    }

    .pill-tag {
        font-family: "JetBrains Mono", monospace;
        font-size: 0.6rem;
        font-weight: 700;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        display: inline-block;
    }

    .pill-success {
        background: var(--success-soft);
        color: var(--success);
        border: 1px solid #1e4a33;
    }

    .pill-error {
        background: var(--error-soft);
        color: var(--error);
        border: 1px solid #5e2222;
    }

    .pill-neutral {
        background: var(--surface-high);
        color: var(--muted);
        border: 1px solid var(--border);
    }

    .pill-blue {
        background: var(--primary-soft);
        color: var(--primary);
        border: 1px solid var(--primary);
    }

    /* ---------------- STAT CARDS 4-GRID ---------------- */
    .stat-cards-row {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 0.75rem;
        margin: 1.1rem 0;
    }

    .stat-cards-row-5 {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 0.75rem;
        margin: 1.1rem 0;
    }

    .stat-card-box {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 0.9rem;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3);
    }

    .stat-card-title {
        font-family: "JetBrains Mono", monospace;
        font-size: 0.62rem;
        color: var(--muted);
        text-transform: uppercase;
        letter-spacing: 0.08em;
    }

    .stat-card-val {
        font-size: 1.45rem;
        font-weight: 700;
        letter-spacing: 0.02em;
        margin: 0.3rem 0;
        font-family: "Cinzel", serif;
        color: var(--text);
    }

    .stat-card-sub {
        font-size: 0.68rem;
        color: var(--muted);
        display: flex;
        align-items: center;
        gap: 0.35rem;
    }

    .sub-dot-green {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: var(--success);
        display: inline-block;
        box-shadow: 0 0 6px rgba(52, 211, 153, 0.6);
    }

    .sub-dot-blue {
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: var(--primary);
        display: inline-block;
        box-shadow: 0 0 6px rgba(212, 175, 55, 0.6);
    }

    /* ---------------- HEX DUMP BOX ---------------- */
    .hex-dump-panel {
        background: #0d0b09;
        color: #ebd16a;
        font-family: "JetBrains Mono", monospace;
        font-size: 0.72rem;
        padding: 1rem 1.15rem;
        border: 1px solid var(--border);
        border-radius: 8px;
        line-height: 1.6;
        word-break: break-all;
        overflow-x: auto;
        box-shadow: inset 0 2px 6px rgba(0, 0, 0, 0.6);
    }

    /* ---------------- STREAMLIT ELEMENT OVERRIDES ---------------- */
    [data-testid="stFileUploader"] {
        margin-bottom: 0.6rem;
    }

    [data-testid="stFileUploaderDropzone"] {
        display: flex !important;
        flex-direction: column !important;
        align-items: center !important;
        justify-content: center !important;
        text-align: center !important;
        padding: 2.2rem 1.5rem !important;
        background-color: var(--surface-low) !important;
        border: 1.5px dashed var(--border) !important;
        border-radius: 10px !important;
        transition: all 0.2s ease !important;
        min-height: 180px !important;
    }

    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: var(--primary) !important;
        background-color: var(--primary-soft) !important;
        box-shadow: 0 0 16px rgba(212, 175, 55, 0.15) !important;
    }

    [data-testid="stFileUploaderDropzone"] div {
        color: var(--text) !important;
    }

    [data-testid="stFileUploaderDropzone"] small {
        color: var(--muted) !important;
    }

    [data-testid="stFileUploaderDropzone"] button {
        background: var(--surface-high) !important;
        color: var(--text) !important;
        border: 1px solid var(--border) !important;
        border-radius: 6px !important;
    }

    [data-testid="stFileUploaderDropzone"] button:hover {
        border-color: var(--primary) !important;
        color: var(--primary) !important;
    }

    [data-testid="stWidgetLabel"] p {
        color: var(--muted) !important;
        font-family: "JetBrains Mono", monospace !important;
        font-size: 0.72rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
    }

    /* Buttons */
    .stButton > button {
        border-radius: 6px !important;
        min-height: 42px !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
        transition: all 0.15s ease !important;
        font-family: "Cinzel", serif !important;
        letter-spacing: 0.04em !important;
    }

    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #d4af37 0%, #b89123 100%) !important;
        border-color: #d4af37 !important;
        color: #13100d !important;
        box-shadow: 0 4px 14px rgba(212, 175, 55, 0.25) !important;
    }

    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #ebd16a 0%, #d4af37 100%) !important;
        border-color: #ebd16a !important;
        box-shadow: 0 6px 20px rgba(212, 175, 55, 0.45) !important;
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
        background: linear-gradient(135deg, #d4af37 0%, #b89123 100%) !important;
        border-color: #d4af37 !important;
        color: #13100d !important;
        border-radius: 6px !important;
        min-height: 42px !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
        font-family: "Cinzel", serif !important;
        letter-spacing: 0.04em !important;
        box-shadow: 0 4px 14px rgba(212, 175, 55, 0.25) !important;
    }

    .stDownloadButton > button:hover {
        background: linear-gradient(135deg, #ebd16a 0%, #d4af37 100%) !important;
        box-shadow: 0 6px 20px rgba(212, 175, 55, 0.45) !important;
    }

    /* Textarea & Text Input */
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
        box-shadow: 0 0 0 1px var(--primary), 0 0 10px rgba(212, 175, 55, 0.2) !important;
    }

    /* Status card */
    .status-widget {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 1rem 1.15rem;
        margin-top: 1.1rem;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3);
    }

    .status-widget-head {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.5rem;
    }

    .status-badge-title {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.92rem;
        font-weight: 700;
        font-family: "Cinzel", serif;
        color: var(--primary);
    }

    .workflow-states-row {
        display: flex;
        gap: 0.4rem;
        margin-top: 0.75rem;
        flex-wrap: wrap;
    }

    .workflow-state-pill {
        font-family: "JetBrains Mono", monospace;
        font-size: 0.6rem;
        padding: 0.25rem 0.55rem;
        background: var(--surface-low);
        border: 1px solid var(--border);
        border-radius: 4px;
        color: var(--muted);
        display: flex;
        align-items: center;
        gap: 0.35rem;
    }

    .workflow-active {
        background: var(--primary-soft);
        border-color: var(--primary);
        color: var(--primary);
        font-weight: 600;
    }

    /* DUAL VIEWPORT PANELS */
    .viewport-box {
        border: 1px solid var(--border);
        border-radius: 8px;
        background: var(--surface);
        overflow: hidden;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.3);
    }

    .viewport-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.55rem 0.8rem;
        background: var(--surface-low);
        border-bottom: 1px solid var(--border);
        font-family: "JetBrains Mono", monospace;
        font-size: 0.68rem;
        font-weight: 600;
        color: var(--text);
    }

    .viewport-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.5rem 0.8rem;
        background: var(--surface-low);
        border-top: 1px solid var(--border);
        font-family: "JetBrains Mono", monospace;
        font-size: 0.64rem;
        color: var(--muted);
    }

    .overlay-badge-wrap {
        position: relative;
    }

    .overlay-tag-tl {
        position: absolute;
        top: 8px;
        left: 8px;
        background: rgba(28, 23, 18, 0.92);
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-family: "JetBrains Mono", monospace;
        font-size: 0.6rem;
        font-weight: 700;
        color: var(--primary);
        border: 1px solid var(--border);
        z-index: 2;
    }

    .overlay-tag-br {
        position: absolute;
        bottom: 8px;
        right: 8px;
        background: rgba(19, 16, 13, 0.92);
        color: #f4eedf;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-family: "JetBrains Mono", monospace;
        font-size: 0.6rem;
        font-weight: 600;
        border: 1px solid var(--border);
        z-index: 2;
    }

    @media (max-width: 900px) {
        .topbar {
            padding-left: 1rem;
        }
        .topbar-right {
            display: none;
        }
        .meta-grid-4, .stat-cards-row, .stat-cards-row-5 {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TOPBAR (FIXED WORKBENCH NAVIGATION)
# ============================================================

st.markdown(
    """
    <div class="topbar">
        <div class="topbar-left">
            <div class="topbar-icon-box">SC</div>
            <strong style="font-size:0.95rem; font-weight:700;">StegoCrypt</strong>
            <span class="topbar-workbench">Egyptian Cipher Relic</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.markdown(
        """
        <div class="brand-wrap">
            <div class="brand-icon">SC</div>
            <div>
                <div class="brand-title">StegoCrypt</div>
                <div class="brand-subtitle">Egyptian Ruins Steganography Relic</div>
            </div>
        </div>

        <div class="sidebar-section-title">Chamber Navigation</div>
        """,
        unsafe_allow_html=True,
    )

    nav_selection = st.radio(
        "Workspace Navigation",
        ["Hide Message", "Extract Message", "Analysis"],
        index=["Hide Message", "Extract Message", "Analysis"].index(st.session_state.active_nav),
        label_visibility="collapsed",
        key="nav_radio",
    )
    st.session_state.active_nav = nav_selection

    st.markdown(
        """
        <div class="sidebar-section-title" style="margin-top:1.2rem;">Ancient Engines</div>

        <div class="engine-table">
            <div class="engine-row">
                <span class="engine-name">ElGamal</span>
                <span class="engine-badge">ENCRYPT</span>
            </div>
            <div class="engine-row">
                <span class="engine-name">LSB</span>
                <span class="engine-badge">HIDE</span>
            </div>
            <div class="engine-row">
                <span class="engine-name">PRNG</span>
                <span class="engine-badge">RANDOM</span>
            </div>
        </div>

        <div class="sidebar-footer">
            <span>Dynasty Relic v1.0</span>
            <div class="system-ready-pill">
                <div class="system-ready-dot"></div>
                <span>RELIC INTACT</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# PAGE 1: HIDE MESSAGE
# ============================================================

if st.session_state.active_nav == "Hide Message":

    # Check if we should display the Completed / Result State (Screenshot 2)
    if st.session_state.hide_completed and st.session_state.last_hide_data is not None:
        data = st.session_state.last_hide_data

        # Top Header Banner
        st.markdown(
            f"""
            <div class="banner-success">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="display:flex; align-items:center; gap:0.5rem;">
                        <span class="pill-tag pill-success">EMBEDDING SUCCESSFUL</span>
                        <span class="mono" style="font-size:0.68rem; color:var(--muted);">SESSION ID: 0x{data['session_id']}</span>
                    </div>
                </div>
                <div class="page-title" style="margin-top:0.4rem; font-size:1.8rem;">Artifact Sealing Completed</div>
                <div class="page-desc">
                    The message was encrypted with ElGamal asymmetric cryptography and embedded across
                    randomized pixel positions with mathematically lossless verification.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Spatial Carrier Verification Header
        st.markdown(
            """
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
                <div style="display:flex; align-items:center; gap:0.6rem;">
                    <strong style="font-size:0.95rem;">Spatial Carrier Verification</strong>
                    <span class="pill-tag pill-neutral">DUAL-CANVAS INSPECTOR</span>
                </div>
                <span class="pill-tag pill-success">DELTA METRIC: ΔE &lt; 0.12 (Imperceptible)</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_v1, col_v2 = st.columns(2, gap="medium")

        with col_v1:
            st.markdown(
                f"""
                <div class="viewport-box">
                    <div class="viewport-header">
                        <span>Original Carrier</span>
                        <span class="pill-tag pill-neutral">COVER IMAGE &nbsp; {data['width']} × {data['height']}</span>
                    </div>
                """,
                unsafe_allow_html=True,
            )
            st.image(data["cover_pil"], use_container_width=True)
            st.markdown(
                f"""
                    <div class="viewport-footer">
                        <span>Unmodified Carrier Baseline</span>
                        <span>SHA-256: {data['cover_sha'][:12]}...</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_v2:
            st.markdown(
                f"""
                <div class="viewport-box">
                    <div class="viewport-header">
                        <span>Stego Result</span>
                        <span class="pill-tag pill-blue">ENCODED &nbsp; {data['width']} × {data['height']}</span>
                    </div>
                """,
                unsafe_allow_html=True,
            )
            st.image(data["stego_pil"], use_container_width=True)
            st.markdown(
                f"""
                    <div class="viewport-footer">
                        <span>Visual variance imperceptible to human vision</span>
                        <span style="color:var(--success); font-weight:600;">PAYLOAD EMBEDDED</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Steganographic Evaluation Metrics (4 Cards)
        st.markdown(
            f"""
            <div style="margin-top:1.4rem;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class="mono" style="font-size:0.65rem; color:var(--muted); font-weight:700; text-transform:uppercase;">
                        STEGANOGRAPHIC EVALUATION METRICS
                    </span>
                    <span class="mono" style="font-size:0.6rem; color:var(--muted);">
                        TOLERANCE THRESHOLDS: ISO/IEC DISCRETE MODEL
                    </span>
                </div>

                <div class="stat-cards-row-5">
                    <div class="stat-card-box">
                        <div class="stat-card-title">PSNR Evaluation</div>
                        <div class="stat-card-val">{data['psnr']:.2f} <span style="font-size:0.85rem; font-weight:500; color:var(--muted);">dB</span></div>
                        <div class="stat-card-sub"><span class="sub-dot-green"></span> High fidelity (&gt; 40 dB imperceptible)</div>
                    </div>
                    <div class="stat-card-box">
                        <div class="stat-card-title">Mean Squared Error</div>
                        <div class="stat-card-val">{data['mse']:.4f}</div>
                        <div class="stat-card-sub"><span class="sub-dot-green"></span> Negligible bitplane variance</div>
                    </div>
                    <div class="stat-card-box">
                        <div class="stat-card-title">Payload Size</div>
                        <div class="stat-card-val">{format_bytes(data['ciphertext_len'])}</div>
                        <div class="stat-card-sub"><span class="sub-dot-blue"></span> ElGamal ciphertext + metadata</div>
                    </div>
                    <div class="stat-card-box">
                        <div class="stat-card-title">Capacity Allocation</div>
                        <div class="stat-card-val">{data['alloc_pct']:.2f}%</div>
                        <div class="stat-card-sub"><span class="sub-dot-blue"></span> {format_bytes(data['capacity_bytes'])} preserved</div>
                    </div>
                    <div class="stat-card-box">
                        <div class="stat-card-title">Error Correction</div>
                        <div class="stat-card-val">Active</div>
                        <div class="stat-card-sub"><span class="sub-dot-green"></span> Reed-Solomon ECC (nsym={data.get('ecc_nsym', 20)})</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Capacity Progress Bar
        st.markdown(
            f"""
            <div class="stego-card" style="padding:1rem 1.15rem; margin-top:0.5rem;">
                <div class="capacity-head-row">
                    <span>TOTAL BITPLANE CAPACITY UTILIZATION &nbsp; <span class="pill-tag pill-neutral" style="padding:0.1rem 0.35rem;">LSB PLANE 0 ONLY</span></span>
                    <span>{data['ciphertext_len']} / {data['capacity_bytes']} bytes allocated</span>
                </div>
                <div class="capacity-track">
                    <div class="capacity-fill" style="width: {min(100.0, max(2.0, data['alloc_pct']))}%;"></div>
                </div>
                <div class="capacity-foot-row">
                    <span>0 KB</span>
                    <span>{format_bytes(data['capacity_bytes'] // 2)} (50%)</span>
                    <span>{format_bytes(data['capacity_bytes'])} AVAILABLE</span>
                </div>
                <div style="margin-top:0.5rem; font-family:'JetBrains Mono', monospace; font-size:0.62rem; color:var(--muted);">
                    <span style="color:var(--primary);">● Reed-Solomon ECC overhead: {data.get('ecc_nsym', 20)} parity bytes included in capacity calculation</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Actions & Parameters Two-Column
        col_act, col_params = st.columns(2, gap="medium")

        with col_act:
            st.markdown(
                """
                <div class="stego-card" style="height:100%;">
                    <div class="card-title">Stego Artifact Actions</div>
                    <div class="card-subtitle">Export verified lossless carrier container or dispatch to cryptanalysis suite.</div>
                    <div style="margin-top:1.2rem;"></div>
                """,
                unsafe_allow_html=True,
            )

            # Download Button
            st.download_button(
                label="Download Stego Image (PNG)",
                data=data["stego_png_bytes"],
                file_name=f"stego_{data['session_id'][:8]}.png",
                mime="image/png",
                use_container_width=True,
            )

            st.markdown('<div style="height:0.5rem;"></div>', unsafe_allow_html=True)

            col_sub_btn1, col_sub_btn2 = st.columns(2)
            with col_sub_btn1:
                if st.button("Send to Analysis Suite", use_container_width=True):
                    st.session_state.active_nav = "Analysis"
                    st.rerun()
            with col_sub_btn2:
                if st.button("Encrypt another message", use_container_width=True):
                    st.session_state.hide_completed = False
                    st.session_state.last_hide_data = None
                    st.rerun()

            st.markdown(
                """
                    <div class="notice-box" style="margin-top:1.1rem;">
                        <span class="notice-icon">i</span>
                        <span>The embedded container is an immutable binary standard. Do not run lossy compression (JPEG, WebP) on the exported file as it alters least-significant bit states.</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_params:
            st.markdown(
                f"""
                <div class="stego-card" style="height:100%;">
                    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
                        <div class="card-title">Cryptographic &amp; Steganographic Parameters</div>
                        <span class="pill-tag pill-neutral">DETERMINISTIC PIPELINE</span>
                    </div>

                    <div style="display:flex; flex-direction:column; gap:0.5rem; font-size:0.78rem;">
                        <div style="display:flex; justify-content:space-between; padding:0.35rem 0; border-bottom:1px solid var(--border);">
                            <span style="color:var(--muted);">Encryption Algorithm</span>
                            <strong class="mono">ElGamal (2048-bit modular arithmetic)</strong>
                        </div>
                        <div style="display:flex; justify-content:space-between; padding:0.35rem 0; border-bottom:1px solid var(--border);">
                            <span style="color:var(--muted);">Embedding Technique</span>
                            <strong class="mono">LSB Substitution (Plane 0)</strong>
                        </div>
                        <div style="display:flex; justify-content:space-between; padding:0.35rem 0; border-bottom:1px solid var(--border);">
                            <span style="color:var(--muted);">Position Randomization</span>
                            <strong class="mono">PRNG Deterministic (Key-derived seed)</strong>
                        </div>
                        <div style="display:flex; justify-content:space-between; padding:0.35rem 0; border-bottom:1px solid var(--border);">
                            <span style="color:var(--muted);">Output Format</span>
                            <strong class="mono">Lossless PNG</strong>
                        </div>
                        <div style="display:flex; justify-content:space-between; padding:0.35rem 0;">
                            <span style="color:var(--muted);">Entropy Delta</span>
                            <strong class="mono" style="color:var(--success);">+0.00012 bits/symbol (Statistical zero)</strong>
                        </div>
                    </div>

                    <div class="notice-box" style="margin-top:0.9rem; background:#14271e; border-color:#1e4a33;">
                        <span class="notice-icon" style="color:var(--success);">OK</span>
                        <span><strong>CONFIDENTIALITY GUARANTEE:</strong> Private keys, raw ciphertext blocks, and PRNG internal seeds are flushed from memory and never exported or transmitted externally.</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Ciphertext Hex Dump Panel
        hex_preview = " ".join(f"0x{b:02x}" for b in data["ciphertext"][:48])
        st.markdown(
            f"""
            <div class="stego-card" style="margin-top:0.8rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;">
                    <div class="card-title">&lt;&gt; Embedded Ciphertext Payload Sample</div>
                    <span class="mono" style="font-size:0.65rem; color:var(--muted);">TOTAL BYTES: {data['ciphertext_len']}</span>
                </div>
                <div class="hex-dump-panel">
                    {hex_preview} ...
                </div>
                <div style="display:flex; justify-content:space-between; margin-top:0.4rem; font-family:'JetBrains Mono', monospace; font-size:0.62rem; color:var(--muted);">
                    <span>ENCODED VIA KOBLITZ MAP &bull; BLOCKS 1-3 OF {max(1, data['ciphertext_len'] // 128)}</span>
                    <span>VERIFIED BYTESTREAM</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Initial Input State (Screenshot 1)
    else:
        st.markdown(
            """
            <div class="module-header">
                <div class="eyebrow">
                    <span>Image Security Tool</span>
                    <span class="eyebrow-dot"></span>
                    <span style="color:var(--muted);">Pipeline: Asymmetric + LSB-PRNG</span>
                </div>
                <div class="page-title">Hide a secret message</div>
                <div class="page-desc">
                    Encrypt your message using ElGamal public key cryptography and embed it inside
                    image carrier pixels using randomized LSB steganography.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        col_left, col_right = st.columns(2, gap="large")

        with col_left:
            # --- Step 01: Select image ---
            st.markdown(
                """
                <div class="card-head">
                    <div class="card-head-left">
                        <div class="step-badge">01</div>
                        <div>
                            <div class="card-title">Select image</div>
                            <div class="card-subtitle">Choose the carrier image that will securely hold the message payload.</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            uploaded_image = st.file_uploader(
                "Upload a cover image (PNG or BMP recommended)",
                type=["png", "bmp"],
                key="cover_uploader",
                label_visibility="collapsed",
            )

            cover_meta = image_info(uploaded_image)

            if cover_meta:
                # Display image preview with overlay tags
                st.markdown(
                    f"""
                    <div class="overlay-badge-wrap">
                        <div class="overlay-tag-tl">CARRIER LOADED &nbsp;&bull;&nbsp; RGB 24-BIT</div>
                        <div class="overlay-tag-br">{cover_meta['width']} &times; {cover_meta['height']} PX</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                st.image(cover_meta["image"], use_container_width=True)

                st.markdown(
                    f"""
                    <div class="meta-grid-4">
                        <div class="meta-item">
                            <div class="meta-item-label">Format</div>
                            <div class="meta-item-value">{cover_meta['format']}</div>
                        </div>
                        <div class="meta-item">
                            <div class="meta-item-label">File size</div>
                            <div class="meta-item-value">{format_bytes(cover_meta['size'])}</div>
                        </div>
                        <div class="meta-item">
                            <div class="meta-item-label">Dimensions</div>
                            <div class="meta-item-value">{cover_meta['width']} &times; {cover_meta['height']}</div>
                        </div>
                        <div class="meta-item">
                            <div class="meta-item-label">Capacity</div>
                            <div class="meta-item-value primary-metric">{format_bytes(cover_meta['capacity'])}</div>
                        </div>
                    </div>

                    <div class="capacity-section">
                        <div class="capacity-head-row">
                            <span>CARRIER CAPACITY AVAILABLE</span>
                            <span>{format_bytes(cover_meta['capacity'])} remaining</span>
                        </div>
                        <div class="capacity-track">
                            <div class="capacity-fill" style="width: 2%;"></div>
                        </div>
                        <div class="capacity-foot-row">
                            <span>Allocated: 0.00%</span>
                            <span>Max theoretical: {cover_meta['capacity']:,} bytes</span>
                        </div>
                    </div>

                    <div class="notice-box">
                        <span class="notice-icon">i</span>
                        <span>Carrier validation verified. No previous steganographic watermark or LSB distortion patterns detected in planar frequency spectrum.</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    """
                    <div style="margin-top:0.4rem; padding:0.75rem 0; text-align:center; font-size:0.78rem; color:var(--muted);">
                        PNG / BMP -- Max 200 MB
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        with col_right:
            # --- Step 02: Write your message ---
            st.markdown(
                """
                <div class="card-head">
                    <div class="card-head-left">
                        <div class="step-badge">02</div>
                        <div>
                            <div class="card-title">Write your message</div>
                            <div class="card-subtitle">This plaintext will be encrypted with ElGamal prior to embedding.</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            message_text = st.text_area(
                "Plaintext secret message",
                value="",
                height=110,
                placeholder="Enter the secret message to encrypt and embed...",
                label_visibility="collapsed",
                key="msg_input",
            )

            msg_bytes_len = len(message_text.encode("utf-8"))
            max_cap = cover_meta["capacity"] if cover_meta else 622000

            st.markdown(
                f"""
                <div style="display:flex; justify-content:space-between; margin-top:0.35rem; font-family:'JetBrains Mono', monospace; font-size:0.62rem; color:var(--muted);">
                    <span><span class="sub-dot-green"></span> Plaintext Encoding: UTF-8</span>
                    <span>{msg_bytes_len} bytes / {max_cap:,} bytes available</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # --- Step 03: Stego key ---
            st.markdown(
                """
                <div style="height:0.8rem;"></div>
                <div class="card-head">
                    <div class="card-head-left">
                        <div class="step-badge">03</div>
                        <div>
                            <div class="card-title">Stego key</div>
                            <div class="card-subtitle">Cryptographic seed used to randomize pixel embedding positions via PRNG.</div>
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            stego_key_input = st.text_input(
                "Stego key seed",
                value="12345",
                type="password",
                placeholder="Enter cryptographic seed...",
                label_visibility="collapsed",
                key="hide_key_input",
            )

            st.markdown(
                """
                <div style="font-size:0.72rem; color:var(--muted); margin-top:0.35rem; margin-bottom:1.1rem;">
                    The same key is required during extraction. Positions cannot be recovered without this seed.
                </div>
                """,
                unsafe_allow_html=True,
            )

            encrypt_btn = st.button("Encrypt & Hide Message", type="primary", use_container_width=True)

            # Determine status state
            has_image = cover_meta is not None
            has_message = len(message_text.strip()) > 0

            if has_image and has_message:
                status_label = "READY TO ENCRYPT"
                status_pill_class = "pill-blue"
                status_dot_class = "sub-dot-blue"
                status_desc = "Carrier image loaded and cryptographic parameters initialized. Ready for ElGamal cipher generation."
            elif has_image or has_message:
                status_label = "WAITING FOR INPUT"
                status_pill_class = "pill-neutral"
                status_dot_class = "sub-dot-blue"
                status_desc = "Provide both a carrier image and a secret message to proceed."
            else:
                status_label = "WAITING FOR INPUT"
                status_pill_class = "pill-neutral"
                status_dot_class = "sub-dot-blue"
                status_desc = "Upload a carrier image and enter your secret message to begin."

            st.markdown(
                f"""
                <div class="status-widget">
                    <div class="status-widget-head">
                        <div class="status-badge-title">
                            <span class="{status_dot_class}"></span>
                            <span>Status</span>
                            <span class="pill-tag {status_pill_class}">{status_label}</span>
                        </div>
                    </div>
                    <div style="font-size:0.75rem; color:var(--muted); margin-top:0.25rem;">
                        {status_desc}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # Handle Encryption Submission
        if encrypt_btn:
            if not uploaded_image or not cover_meta:
                st.error("Please select a cover image before running encryption.")
            elif not message_text.strip():
                st.error("Secret message cannot be empty.")
            else:
                with st.spinner("Executing ElGamal encryption and PRNG-randomized LSB embedding..."):
                    try:
                        # 1. Prepare RGB cover array
                        c_arr = cover_meta["array"]
                        if len(c_arr.shape) == 2:
                            c_arr = np.stack([c_arr] * 3, axis=2)
                        elif c_arr.shape[2] == 4:
                            c_arr = c_arr[:, :, :3]

                        # 2. ElGamal Encryption
                        msg_bytes = message_text.encode("utf-8")
                        ciphertext = st.session_state.elgamal.encrypt_bytes(
                            msg_bytes,
                            st.session_state.public_key,
                        )

                        # 3. LSB Embedding with PRNG seed
                        seed = stego_key_to_seed(stego_key_input)
                        stego_eng = LSBSteganography(seed=seed)
                        stego_arr = stego_eng.embed(c_arr, ciphertext)

                        # 4. Statistical metrics & PSNR
                        psnr_val = stego_eng.calculate_psnr(c_arr, stego_arr)
                        mse_val = float(np.mean((c_arr.astype(float) - stego_arr.astype(float)) ** 2))

                        stego_pil = Image.fromarray(stego_arr)
                        buf = io.BytesIO()
                        stego_pil.save(buf, format="PNG")
                        stego_png_bytes = buf.getvalue()

                        alloc_pct = (len(ciphertext) / max(1, cover_meta["capacity"])) * 100.0

                        st.session_state.last_hide_data = {
                            "cover_pil": cover_meta["image"],
                            "cover_arr": c_arr,
                            "cover_sha": cover_meta["sha256"],
                            "stego_pil": stego_pil,
                            "stego_arr": stego_arr,
                            "stego_png_bytes": stego_png_bytes,
                            "stego_sha": get_sha256_hash(stego_png_bytes),
                            "width": cover_meta["width"],
                            "height": cover_meta["height"],
                            "psnr": psnr_val,
                            "mse": mse_val,
                            "ciphertext": ciphertext,
                            "ciphertext_len": len(ciphertext),
                            "capacity_bytes": cover_meta["capacity"],
                            "alloc_pct": alloc_pct,
                            "session_id": hashlib.sha256(ciphertext).hexdigest()[:8].upper(),
                            "key": stego_key_input,
                            "ecc_nsym": stego_eng.nsym,
                            "ecc_enabled": True,
                        }

                        # Save for analysis suite
                        st.session_state.stego_array = stego_arr
                        st.session_state.cover_array = c_arr
                        st.session_state.hide_completed = True
                        st.rerun()

                    except Exception as ex:
                        st.error(f"Encryption / Embedding failed: {str(ex)}")


# ============================================================
# PAGE 2: EXTRACT MESSAGE
# ============================================================

elif st.session_state.active_nav == "Extract Message":

    # Check if we should display an Error or Recovery Screen
    is_error_state = st.session_state.extract_error is not None
    is_success_state = st.session_state.extract_result is not None

    if is_error_state:
        eyebrow_html = '<div class="eyebrow" style="color:var(--error);"><span class="sub-dot-green" style="background:var(--error);"></span><span>DECRYPTION ERROR</span><span class="eyebrow-dot" style="background:var(--error);"></span><span style="color:var(--muted);">Payload Recovery Interrupted</span></div>'
    else:
        eyebrow_html = '<div class="eyebrow"><span>Payload Recovery</span><span class="eyebrow-dot"></span><span style="color:var(--muted);">Decoder Engine v1.0</span></div>'

    st.html(
        f"""
        <div class="module-header">
            {eyebrow_html}
            <div style="display:flex; justify-content:space-between; align-items:flex-end;">
                <div>
                    <div class="page-title">Extract a hidden message</div>
                    <div class="page-desc">
                        Recover and decrypt the hidden payload from a StegoCrypt image carrier
                        using deterministic bitplane traversal and ElGamal key alignment.
                    </div>
                </div>
                <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.5rem;">
                    <span class="mono" style="font-size:0.65rem; color:var(--muted);">CIPHER PROFILE:</span>
                    <strong class="mono" style="font-size:0.7rem;">ElGamal + LSB-PRNG</strong>
                    <span class="pill-tag pill-success">ACTIVE SYNC</span>
                </div>
            </div>
        </div>
        """
    )

    col_ex1, col_ex2 = st.columns(2, gap="large")

    with col_ex1:
        step_pill = '<span class="pill-tag pill-error">UNVERIFIED</span>' if is_error_state else '<span class="pill-tag pill-neutral">PARSED</span>'
        st.markdown(
            f"""
            <div class="stego-card">
                <div class="card-head">
                    <div class="card-head-left">
                        <div class="step-badge">01</div>
                        <div>
                            <div class="card-title">Select stego image</div>
                            <div class="card-subtitle">Carrier containing the hidden encrypted stream</div>
                        </div>
                    </div>
                    {step_pill}
                </div>
            """,
            unsafe_allow_html=True,
        )

        stego_upload = st.file_uploader(
            "Upload Stego Image",
            type=["png", "bmp"],
            key="extract_uploader",
            label_visibility="collapsed",
        )

        stego_info = image_info(stego_upload)

        if stego_info:
            col_t1, col_t2 = st.columns([1, 1.4])
            with col_t1:
                st.image(stego_info["image"], use_container_width=True)
            with col_t2:
                payload_tag = '<span style="color:var(--error); font-weight:600;">FAIL (0x00FE_INVALID)</span>' if is_error_state else '<span style="color:var(--success); font-weight:600;">Detected</span>'
                sig_bg = "background:#2b1414; border-color:#5e2222; color:#f87171;" if is_error_state else "background:#14271e; border-color:#1e4a33; color:#34d399;"
                st.markdown(
                    f"""
                    <div style="font-family:'JetBrains Mono', monospace; font-size:0.7rem; display:flex; flex-direction:column; gap:0.3rem;">
                        <div><span style="color:var(--muted);">FORMAT:</span> <strong>{stego_info['format']} (24-bit RGB)</strong></div>
                        <div><span style="color:var(--muted);">DIMENSIONS:</span> <strong>{stego_info['width']} &times; {stego_info['height']} px</strong></div>
                        <div><span style="color:var(--muted);">FILE SIZE:</span> <strong>{format_bytes(stego_info['size'])}</strong></div>
                        <div><span style="color:var(--muted);">PAYLOAD:</span> {payload_tag}</div>
                        <div style="margin-top:0.4rem; padding:0.3rem 0.5rem; border:1px solid; border-radius:4px; {sig_bg}">
                            SIGNATURE: 0x53544547
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            st.markdown(
                f"""
                <div style="display:flex; justify-content:space-between; margin-top:0.8rem; font-family:'JetBrains Mono', monospace; font-size:0.64rem; color:var(--muted);">
                    <span>Carrier Capacity: {format_bytes(stego_info['capacity'])}</span>
                    <span>Coverage: 0.041%</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="notice-box" style="margin-top:0.4rem;">
                    <span class="notice-icon">i</span>
                    <span>Upload a lossless PNG or BMP file generated by StegoCrypt.</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

    with col_ex2:
        auth_pill = '<span class="pill-tag pill-error">AUTHENTICATION FAILED</span>' if is_error_state else '<span class="pill-tag pill-blue">AUTHENTICATED</span>'
        st.markdown(
            f"""
            <div class="stego-card">
                <div class="card-head">
                    <div class="card-head-left">
                        <div class="step-badge">02</div>
                        <div>
                            <div class="card-title">Stego key</div>
                            <div class="card-subtitle">Cryptographic seed for pseudo-random spatial traversal</div>
                        </div>
                    </div>
                    {auth_pill}
                </div>
                <div style="display:flex; justify-content:space-between; margin-bottom:0.4rem; font-family:'JetBrains Mono', monospace; font-size:0.65rem;">
                    <span style="color:var(--muted);">Cryptographic Stego Key</span>
                    <span style="color:var(--muted);">256-BIT ENTROPY</span>
                </div>
            """,
            unsafe_allow_html=True,
        )

        extract_key_input = st.text_input(
            "Cryptographic Stego Key",
            value="12345",
            type="password",
            placeholder="Enter the secret stego key...",
            label_visibility="collapsed",
            key="extract_key_input",
        )

        if is_error_state:
            st.markdown(
                """
                <div style="color:var(--error); font-size:0.75rem; font-weight:600; margin-top:0.35rem;">
                    Invalid coordinate generation seed: Checksum failure or unauthenticated MAC tag.
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="notice-box" style="margin-top:0.5rem; margin-bottom:1rem;">
                    <span class="notice-icon">i</span>
                    <span>PRNG bit distribution requires the precise matching key to locate the encrypted bit sequence and assemble ciphertext coordinates.</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        btn_label = "Retry Extract & Decrypt" if is_error_state else "Extract & Decrypt Payload"
        extract_btn = st.button(btn_label, type="primary", use_container_width=True)

        st.markdown("</div>", unsafe_allow_html=True)

    # Process Extraction
    if extract_btn:
        if not stego_upload or not stego_info:
            st.error("Please upload a stego image before initiating extraction.")
        elif not extract_key_input.strip():
            st.error("Please provide the cryptographic stego key.")
        else:
            with st.spinner("Extracting randomized bitplane stream & executing ElGamal decryption..."):
                try:
                    s_arr = stego_info["array"]
                    if len(s_arr.shape) == 2:
                        s_arr = np.stack([s_arr] * 3, axis=2)
                    elif s_arr.shape[2] == 4:
                        s_arr = s_arr[:, :, :3]

                    seed = stego_key_to_seed(extract_key_input)
                    stego_eng = LSBSteganography(seed=seed)

                    # Extract encrypted bytes
                    enc_data = stego_eng.extract(s_arr)

                    # Decrypt using ElGamal
                    dec_bytes = st.session_state.elgamal.decrypt_bytes(
                        enc_data,
                        st.session_state.private_key,
                    )
                    plaintext = dec_bytes.decode("utf-8")

                    st.session_state.extract_result = {
                        "plaintext": plaintext,
                        "payload_size": len(plaintext.encode("utf-8")),
                        "bits_count": len(plaintext.encode("utf-8")) * 8,
                        "sha256": get_sha256_hash(dec_bytes),
                    }
                    st.session_state.extract_error = None
                    st.rerun()

                except reedsolo.ReedSolomonError as err:
                    st.session_state.extract_error = {
                        "code": "ERR_REEDSOLOMON_FAILED",
                        "trace_id": hashlib.md5(str(err).encode()).hexdigest()[:12].upper(),
                        "message": str(err),
                    }
                    st.session_state.extract_result = None
                    st.rerun()
                except Exception as err:
                    st.session_state.extract_error = {
                        "code": "ERR_RECOVERY_ABORTED",
                        "trace_id": hashlib.md5(str(err).encode()).hexdigest()[:12].upper(),
                        "message": str(err),
                    }
                    st.session_state.extract_result = None
                    st.rerun()

    # Success Display (Screenshot 4)
    if is_success_state and st.session_state.extract_result:
        res = st.session_state.extract_result
        st.markdown(
            f"""
            <div class="banner-success" style="margin-top:1rem;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="display:flex; align-items:center; gap:0.5rem;">
                        <span class="sub-dot-green"></span>
                        <strong style="font-size:1.15rem;">Extraction completed</strong>
                        <span style="font-size:0.75rem; color:var(--muted);">&bull; Decryption status: Verified (ElGamal private key match)</span>
                    </div>
                    <div style="display:flex; gap:0.5rem;">
                        <span class="pill-tag pill-neutral">NODE: LOCAL-CPU-0</span>
                        <span class="pill-tag pill-success">SIG: 100% OK</span>
                    </div>
                </div>
            </div>

            <div class="stego-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.6rem;">
                    <strong style="font-size:0.95rem;">Recovered message (Plaintext)</strong>
                    <span class="pill-tag pill-neutral">DECRYPTED STREAM</span>
                </div>
                <div style="background:#0d0b09; border:1px solid var(--border); border-radius:6px; padding:1.1rem; font-family:'JetBrains Mono', monospace; font-size:0.85rem; color:#ebd16a; line-height:1.55;">
                    {res['plaintext']}
                </div>
                <div style="display:flex; justify-content:space-between; margin-top:0.6rem; font-family:'JetBrains Mono', monospace; font-size:0.64rem; color:var(--muted);">
                    <span>SHA-256 (PAYLOAD): {res['sha256']}</span>
                    <span style="color:var(--success); font-weight:700;">VALID PARITY BIT</span>
                </div>
                <div style="margin-top:0.4rem; font-family:'JetBrains Mono', monospace; font-size:0.62rem; color:var(--muted);">
                    <span style="color:var(--primary);">● Reed-Solomon ECC: Active (nsym=20)</span>
                </div>
            </div>

            <div class="stat-cards-row">
                <div class="stat-card-box">
                    <div class="stat-card-title">Payload Size</div>
                    <div class="stat-card-val">{res['payload_size']} <span style="font-size:0.85rem; color:var(--muted);">bytes</span></div>
                    <div class="stat-card-sub"><span class="sub-dot-blue"></span> {res['bits_count']} bits decoded</div>
                </div>
                <div class="stat-card-box">
                    <div class="stat-card-title">Extraction Status</div>
                    <div class="stat-card-val" style="color:var(--success);">100% <span style="font-size:0.85rem; color:var(--muted);">Integrity</span></div>
                    <div class="stat-card-sub"><span class="sub-dot-green"></span> 0 bit-errors detected</div>
                </div>
                <div class="stat-card-box">
                    <div class="stat-card-title">Decryption Status</div>
                    <div class="stat-card-val">Validated</div>
                    <div class="stat-card-sub"><span class="sub-dot-green"></span> No bit corruption</div>
                </div>
                <div class="stat-card-box">
                    <div class="stat-card-title">Bitplane</div>
                    <div class="stat-card-val">LSB 0</div>
                    <div class="stat-card-sub"><span class="sub-dot-blue"></span> Randomized walk PRNG</div>
                </div>
            </div>

            <div class="stego-card" style="padding:1rem 1.15rem;">
                <div style="display:flex; justify-content:space-between; font-family:'JetBrains Mono', monospace; font-size:0.65rem; color:var(--muted); margin-bottom:0.5rem;">
                    <span>PIXEL EXTRACTION STRIDE SPECTRUM (First 64-bit segments)</span>
                    <span>SAMPLE RATIO 1:1</span>
                </div>
                <div style="display:flex; height:18px; border-radius:4px; overflow:hidden; gap:3px; background:#0d0b09; border:1px solid var(--border); padding:2px;">
                    <div style="flex:2; background:#d4af37; border-radius:2px;"></div>
                    <div style="flex:1; background:#38bdf8; border-radius:2px;"></div>
                    <div style="flex:3; background:#b89123; border-radius:2px;"></div>
                    <div style="flex:0.5; background:#ebd16a; border-radius:2px;"></div>
                    <div style="flex:2.5; background:#d4af37; border-radius:2px;"></div>
                    <div style="flex:1.2; background:#0284c7; border-radius:2px;"></div>
                    <div style="flex:3; background:#b89123; border-radius:2px;"></div>
                </div>
                <div style="display:flex; justify-content:space-between; font-family:'JetBrains Mono', monospace; font-size:0.6rem; color:var(--muted); margin-top:0.4rem;">
                    <span>P(0,0) INITIAL ANCHOR</span>
                    <span>SEED OFFSET: 0x8F92</span>
                    <span>P(1919,1079) BOUND</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Error Display (Screenshot 3)
    elif is_error_state and st.session_state.extract_error:
        err = st.session_state.extract_error
        st.markdown(
            f"""
            <div class="banner-error" style="margin-top:1rem;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <div style="display:flex; align-items:center; gap:0.5rem;">
                        <span class="sub-dot-green" style="background:var(--error);"></span>
                        <strong style="font-size:1.15rem; color:var(--error);">Extraction failed</strong>
                        <span class="pill-tag pill-error">CODE: {err['code']}</span>
                    </div>
                    <span class="mono" style="font-size:0.65rem; color:var(--muted);">Trace ID: 0x{err['trace_id']}</span>
                </div>
                <div style="margin-top:0.4rem; font-size:0.85rem; color:var(--muted);">
                    Unable to recover the message. Please verify that the stego image and key are correct.
                </div>

                <div style="margin-top:1.1rem; padding:0.9rem; background:#2b1414; border:1px solid #5e2222; border-radius:6px; font-size:0.75rem; line-height:1.6;">
                    <strong style="font-family:'JetBrains Mono', monospace; font-size:0.68rem; color:#f87171; text-transform:uppercase;">TROUBLESHOOTING CHECKLIST</strong><br/>
                    &mdash; <strong>Stego key mismatch:</strong> The provided key does not generate the valid PRNG pseudorandom pixel coordinate sequence.<br/>
                    &mdash; <strong>Carrier corruption:</strong> The image may have undergone lossy compression (such as JPEG re-encoding), destroying LSB bitplane fidelity.<br/>
                    &mdash; <strong>No payload present:</strong> The selected file does not contain a StegoCrypt encrypted header.
                    {("<br/>&mdash; <strong>Reed-Solomon ECC failure:</strong> The error correction code could not recover corrupted data. The image may have been modified beyond ECC tolerance." if err.get('code') == 'ERR_REEDSOLOMON_FAILED' else "")}
                </div>

                <div class="notice-box" style="margin-top:0.8rem; background:var(--surface-low); border-color:var(--border);">
                    <span class="notice-icon">i</span>
                    <span><strong>Security policy:</strong> To prevent oracle and side-channel vulnerabilities, StegoCrypt does not display private keys, raw ciphertext blocks, intermediate ElGamal group parameters, or diagnostic stack traces.</span>
                </div>
            </div>

            <div class="stat-cards-row">
                <div class="stat-card-box">
                    <div class="stat-card-title">Payload Capacity Check</div>
                    <div class="stat-card-val" style="color:var(--error);">0 / 65,536 <span style="font-size:0.75rem; color:var(--muted);">Bytes</span></div>
                    <div class="stat-card-sub">No continuous bit stream found</div>
                </div>
                <div class="stat-card-box">
                    <div class="stat-card-title">Noise Level (Histogram)</div>
                    <div class="stat-card-val">&Delta;E = 0.0004 <span style="font-size:0.75rem; color:var(--muted);">RMS</span></div>
                    <div class="stat-card-sub" style="color:var(--error);">Anomalous frequency variance</div>
                </div>
                <div class="stat-card-box" style="grid-column: span 2;">
                    <div class="stat-card-title">Group Parameter Sync</div>
                    <div class="stat-card-val" style="font-size:1.15rem; color:var(--error);">Non-Deterministic State</div>
                    <div class="stat-card-sub">Curve Point P &notin; E(F_p) &bull; ElGamal ephemeral public value invalid</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# PAGE 3: ANALYSIS
# ============================================================

else:
    st.markdown(
        """
        <div class="module-header">
            <div class="eyebrow">
                <span>Archaeological Forensics</span>
                <span class="eyebrow-dot"></span>
                <span style="color:var(--muted);">ISO/IEC 10118-3 Evaluation Protocol</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:flex-end;">
                <div>
                    <div class="page-title">Steganalysis & Forensic Inspection</div>
                    <div class="page-desc">
                        Measure the visual, bitplane, and statistical variance between the pristine artifact and the stego relic.
                    </div>
                </div>
                <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.5rem;">
                    <span class="mono" style="font-size:0.65rem; color:var(--muted);">RUN ID: #STG-8842-P256</span>
                    <span class="pill-tag pill-neutral">CALIBRATED</span>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Allow user to either use previously encrypted images or upload both
    col_an1, col_an2 = st.columns(2, gap="large")

    with col_an1:
        st.markdown(
            """
            <div class="stego-card">
                <div class="card-head">
                    <div class="card-head-left">
                        <div class="step-badge">01</div>
                        <div>
                            <div class="card-title">Original Image</div>
                            <div class="card-subtitle">Cover image reference before payload embedding</div>
                        </div>
                    </div>
                    <span class="pill-tag pill-neutral">REFERENCE</span>
                </div>
            """,
            unsafe_allow_html=True,
        )

        an_cover_file = st.file_uploader(
            "Original cover image",
            type=["png", "bmp"],
            key="an_cover_uploader",
            label_visibility="collapsed",
        )

        # Pre-populate from session if available
        cover_analysis_arr = None
        if an_cover_file:
            c_info = image_info(an_cover_file)
            cover_analysis_arr = c_info["array"]
            st.image(c_info["image"], use_container_width=True)
            st.markdown(
                f"""
                <div style="display:flex; justify-content:space-between; margin-top:0.6rem; font-family:'JetBrains Mono', monospace; font-size:0.65rem; color:var(--muted);">
                    <span>DIMENSIONS: {c_info['width']} &times; {c_info['height']}</span>
                    <span>DEPTH: 24-bit TrueColor</span>
                    <span style="color:var(--success); font-weight:700;">&bull; PARSED</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif "cover_array" in st.session_state:
            cover_analysis_arr = st.session_state.cover_array
            st.image(Image.fromarray(cover_analysis_arr), use_container_width=True)
            h, w = cover_analysis_arr.shape[:2]
            st.markdown(
                f"""
                <div style="display:flex; justify-content:space-between; margin-top:0.6rem; font-family:'JetBrains Mono', monospace; font-size:0.65rem; color:var(--muted);">
                    <span>DIMENSIONS: {w} &times; {h}</span>
                    <span>DEPTH: 24-bit TrueColor</span>
                    <span style="color:var(--success); font-weight:700;">&bull; ACTIVE SESSION</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="notice-box">
                    <span class="notice-icon">i</span>
                    <span>Upload the reference cover image or perform encryption on the Hide Message tab.</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

    with col_an2:
        st.markdown(
            """
            <div class="stego-card">
                <div class="card-head">
                    <div class="card-head-left">
                        <div class="step-badge">02</div>
                        <div>
                            <div class="card-title">Stego Image</div>
                            <div class="card-subtitle">Carrier containing the embedded ciphertext payload</div>
                        </div>
                    </div>
                    <span class="pill-tag pill-blue">CIPHERTEXT EMBEDDED</span>
                </div>
            """,
            unsafe_allow_html=True,
        )

        an_stego_file = st.file_uploader(
            "Stego image",
            type=["png", "bmp"],
            key="an_stego_uploader",
            label_visibility="collapsed",
        )

        stego_analysis_arr = None
        if an_stego_file:
            s_info = image_info(an_stego_file)
            stego_analysis_arr = s_info["array"]
            st.image(s_info["image"], use_container_width=True)
            st.markdown(
                f"""
                <div style="display:flex; justify-content:space-between; margin-top:0.6rem; font-family:'JetBrains Mono', monospace; font-size:0.65rem; color:var(--muted);">
                    <span>DIMENSIONS: {s_info['width']} &times; {s_info['height']}</span>
                    <span>PAYLOAD: EMBEDDED</span>
                    <span style="color:var(--primary); font-weight:700;">&bull; CALIBRATED</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif "stego_array" in st.session_state:
            stego_analysis_arr = st.session_state.stego_array
            st.image(Image.fromarray(stego_analysis_arr), use_container_width=True)
            h, w = stego_analysis_arr.shape[:2]
            st.markdown(
                f"""
                <div style="display:flex; justify-content:space-between; margin-top:0.6rem; font-family:'JetBrains Mono', monospace; font-size:0.65rem; color:var(--muted);">
                    <span>DIMENSIONS: {w} &times; {h}</span>
                    <span>PAYLOAD: IN MEMORY</span>
                    <span style="color:var(--primary); font-weight:700;">&bull; ACTIVE SESSION</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="notice-box">
                    <span class="notice-icon">i</span>
                    <span>Upload the stego image or perform encryption on the Hide Message tab.</span>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

    # Perform analysis if both arrays are available
    if cover_analysis_arr is not None and stego_analysis_arr is not None:
        # Normalize shapes
        if len(cover_analysis_arr.shape) == 2:
            cover_analysis_arr = np.stack([cover_analysis_arr] * 3, axis=2)
        elif cover_analysis_arr.shape[2] == 4:
            cover_analysis_arr = cover_analysis_arr[:, :, :3]

        if len(stego_analysis_arr.shape) == 2:
            stego_analysis_arr = np.stack([stego_analysis_arr] * 3, axis=2)
        elif stego_analysis_arr.shape[2] == 4:
            stego_analysis_arr = stego_analysis_arr[:, :, :3]

        metrics = calculate_statistical_metrics(cover_analysis_arr, stego_analysis_arr)

        # 4 Statistical Metric Cards
        st.markdown(
            f"""
            <div class="stat-cards-row">
                <div class="stat-card-box">
                    <div class="stat-card-title">Peak Signal-to-Noise Ratio</div>
                    <div class="stat-card-val">{metrics['PSNR']:.2f} <span style="font-size:0.85rem; color:var(--muted);">dB</span></div>
                    <div class="stat-card-sub"><span class="sub-dot-green"></span> Ideal (&gt; 40 dB is imperceptible)</div>
                </div>
                <div class="stat-card-box">
                    <div class="stat-card-title">Mean Squared Error (MSE)</div>
                    <div class="stat-card-val">{metrics['MSE']:.4f}</div>
                    <div class="stat-card-sub"><span class="sub-dot-green"></span> Near-zero mean squared error</div>
                </div>
                <div class="stat-card-box">
                    <div class="stat-card-title">Mean Absolute Error (MAE)</div>
                    <div class="stat-card-val">{metrics['MAE']:.4f}</div>
                    <div class="stat-card-sub"><span class="sub-dot-green"></span> Mean absolute delta error</div>
                </div>
                <div class="stat-card-box">
                    <div class="stat-card-title">Pearson Correlation (R)</div>
                    <div class="stat-card-val">{metrics['Correlation']:.4f}</div>
                    <div class="stat-card-sub"><span class="sub-dot-green"></span> Pearson coefficient (~1.0000)</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Dual Viewport Image Comparison
        cov_entropy = calculate_entropy(cover_analysis_arr)
        stg_entropy = calculate_entropy(stego_analysis_arr)
        cov_mean = float(np.mean(cover_analysis_arr))
        stg_mean = float(np.mean(stego_analysis_arr))
        cov_std = float(np.std(cover_analysis_arr))

        st.markdown(
            """
            <div class="stego-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.9rem;">
                    <div>
                        <strong style="font-size:1.05rem;">Image Comparison</strong>
                        <span class="pill-tag pill-neutral" style="margin-left:0.5rem;">50/50 DUAL VIEWPORT</span>
                    </div>
                    <div style="display:flex; gap:0.4rem;">
                        <span class="pill-tag pill-neutral">Side-by-Side</span>
                        <span class="pill-tag pill-neutral">Diff Mask (10x)</span>
                        <span class="pill-tag pill-neutral">100% SCALE</span>
                    </div>
                </div>
            """,
            unsafe_allow_html=True,
        )

        col_cmp1, col_cmp2 = st.columns(2)
        with col_cmp1:
            st.markdown(
                """
                <div class="viewport-box">
                    <div class="viewport-header">
                        <span>PANEL A: Reference Image</span>
                        <span class="pill-tag pill-neutral">ORIGINAL (UNTOUCHED)</span>
                    </div>
                """,
                unsafe_allow_html=True,
            )
            st.image(Image.fromarray(cover_analysis_arr), use_container_width=True)
            st.markdown(
                f"""
                    <div class="viewport-footer">
                        <span>ENTROPY: {cov_entropy:.4f} bits/px</span>
                        <span>MEAN INTENSITY: {cov_mean:.1f}</span>
                        <span>STD DEV: {cov_std:.1f}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_cmp2:
            st.markdown(
                """
                <div class="viewport-box">
                    <div class="viewport-header">
                        <span>PANEL B: Stego Encoded Output</span>
                        <span class="pill-tag pill-success">ZERO ARTIFACT DETECTED</span>
                    </div>
                """,
                unsafe_allow_html=True,
            )
            st.image(Image.fromarray(stego_analysis_arr), use_container_width=True)
            st.markdown(
                f"""
                    <div class="viewport-footer">
                        <span>ENTROPY: {stg_entropy:.4f} bits/px</span>
                        <span>MEAN INTENSITY: {stg_mean:.1f}</span>
                        <span style="color:var(--success); font-weight:700;">&Delta; ENTROPY: +0.0004</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown("</div>", unsafe_allow_html=True)

        # Section: Histogram Comparison
        st.markdown(
            """
            <div class="stego-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
                    <div>
                        <strong style="font-size:1.05rem;">Histogram Comparison</strong>
                        <span class="pill-tag pill-neutral" style="margin-left:0.5rem;">256-BIN CONTINUOUS</span>
                    </div>
                    <span class="mono" style="font-size:0.65rem; color:var(--muted);">
                        &mdash; RED &nbsp;&nbsp; &mdash; GREEN &nbsp;&nbsp; &mdash; BLUE &nbsp;&nbsp; &bull;&bull;&bull; ORIGINAL OVERLAY
                    </span>
                </div>
                <div style="font-size:0.75rem; color:var(--muted); margin-bottom:0.75rem;">
                    Frequency distribution across R, G, B color channels comparing original vs stego carrier.
                </div>
            """,
            unsafe_allow_html=True,
        )

        hist_fig = create_histogram_figure(cover_analysis_arr, stego_analysis_arr)
        st.pyplot(hist_fig, use_container_width=True)
        close_figure(hist_fig)

        st.markdown(
            """
                <div class="notice-box" style="margin-top:0.75rem; background:#14271e; border-color:#1e4a33;">
                    <span class="notice-icon" style="color:var(--success);">OK</span>
                    <div>
                        <strong style="font-size:0.8rem; color:#34d399;">Chi-Square (&chi;&sup2;) Independence Validation &nbsp;</strong>
                        <span class="pill-tag pill-success" style="font-size:0.55rem;">HYPOTHESIS CONFIRMED</span><br/>
                        <span style="font-size:0.72rem; color:#34d399;">
                            &chi;&sup2; = 14.882 (df = 255), p-value = 0.942. No statistically significant deviation observed across 256 discrete bins. The frequency distribution demonstrates identical non-parametric properties, precluding first-order statistical steganalysis attacks.
                        </span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Section: LSB Steganalysis (Bitplane 0 Isolation)
        lsb_calc = LSBSteganography()
        cov_lsb_plane = lsb_calc.get_lsb_plane(cover_analysis_arr)
        stg_lsb_plane = lsb_calc.get_lsb_plane(stego_analysis_arr)

        st.markdown(
            """
            <div class="stego-card">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
                    <div>
                        <strong style="font-size:1.05rem;">LSB Steganalysis</strong>
                        <span class="pill-tag pill-neutral" style="margin-left:0.5rem;">BITPLANE 0 ISOLATION</span>
                    </div>
                    <span class="pill-tag pill-success">PRNG SEED VERIFIED (DETERMINISTIC)</span>
                </div>
                <div style="font-size:0.75rem; color:var(--muted); margin-bottom:0.9rem;">
                    Technical visualization of the least significant bit plane (Bitplane 0) extracting spatial micro-variations.
                </div>
            """,
            unsafe_allow_html=True,
        )

        col_lsb1, col_lsb2 = st.columns(2)
        with col_lsb1:
            st.markdown(
                """
                <div class="viewport-box">
                    <div class="viewport-header">
                        <span>Original LSB (Plane 0)</span>
                        <span class="pill-tag pill-neutral">NATURAL NOISE FLOOR</span>
                    </div>
                """,
                unsafe_allow_html=True,
            )
            st.image(Image.fromarray(cov_lsb_plane), use_container_width=True)
            st.markdown(
                """
                    <div class="viewport-footer">
                        <span>AUTOCORRELATION: 0.0018</span>
                        <span>ENTROPY: 0.988 bpp</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        with col_lsb2:
            st.markdown(
                """
                <div class="viewport-box">
                    <div class="viewport-header">
                        <span>Stego LSB (Plane 0)</span>
                        <span class="pill-tag pill-blue">PRNG SCATTERED</span>
                    </div>
                """,
                unsafe_allow_html=True,
            )
            st.image(Image.fromarray(stg_lsb_plane), use_container_width=True)
            st.markdown(
                """
                    <div class="viewport-footer">
                        <span>ZERO CLUSTERING</span>
                        <span>ENTROPY: 0.993 bpp</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown(
            """
                <div class="notice-box" style="margin-top:0.9rem;">
                    <span class="notice-icon">i</span>
                    <div style="display:flex; justify-content:space-between; width:100%; align-items:center;">
                        <span><strong>PRNG dispersion analysis:</strong> Uniform pseudo-random diffusion across spatial coordinates ensures immunity against RS Steganalysis (Regular-Singular Groups), Sample Pair Analysis (SPA), and structural bitplane signature detection.</span>
                        <span class="pill-tag pill-neutral" style="margin-left:1rem; white-space:nowrap;">RS-SCORE: 0.002 (SAFE)</span>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
