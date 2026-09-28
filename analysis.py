import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple
import hashlib
from PIL import Image

# ── Ancient Egyptian Ruins Theme Palette ──
_THEME = {
    "bg": "#13110E",              # Deep Obsidian Stone
    "surface": "#1E1A15",         # Carved Dark Sandstone Block
    "surface_low": "#171410",     # Deep Tomb Shadow
    "border": "#3D3428",          # Weathered Sandstone Bevel
    "primary": "#D0AE62",         # Muted Gold
    "primary_hover": "#E8D9B5",   # Papyrus Light
    "text": "#F1E6C8",            # Papyrus White
    "text_secondary": "#D8BC82",  # Natural Sandstone
    "muted": "#A3937F",           # Weathered Silt / Muted Stone
    "muted_light": "#736758",     # Deep Stone Shadow
    "success": "#3C9A91",         # Egyptian Turquoise
    "error": "#C25B45",           # Red Jasper / Terracotta
    "amber": "#C6A66B",           # Sandstone Gold
    # Channel palette
    "ch_red": "#C25B45",          # Red Ochre / Jasper
    "ch_green": "#3C9A91",        # Egyptian Turquoise
    "ch_blue": "#2E6388",         # Lapis Lazuli
    "ch_diff": "#D0AE62",         # Muted Gold Difference
    "grid_alpha": 0.20,
}

def _apply_dark_style(ax, fig=None):
    """Apply the unified dark theme to an axes (and optionally figure)."""
    if fig is not None:
        fig.patch.set_facecolor(_THEME["bg"])
    ax.set_facecolor(_THEME["surface"])
    ax.tick_params(colors=_THEME["muted"], which="both", labelsize=8)
    ax.xaxis.label.set_color(_THEME["muted"])
    ax.yaxis.label.set_color(_THEME["muted"])
    ax.title.set_color(_THEME["text"])
    for spine in ax.spines.values():
        spine.set_color(_THEME["border"])
    ax.grid(True, alpha=_THEME["grid_alpha"], color=_THEME["border"], linewidth=0.5)


def _get_image_hash(image: np.ndarray) -> str:
    """Generate hash for image array for caching purposes."""
    return hashlib.sha256(image.tobytes()).hexdigest()

def calculate_histogram(image: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """
    Calculate histogram for each channel of the image.
    Returns: (histograms, bin_edges)
    """
    if len(image.shape) == 2:
        # Grayscale image
        hist, bins = np.histogram(image.flatten(), bins=256, range=(0, 256))
        return hist, bins
    elif len(image.shape) == 3:
        # Color image
        histograms = []
        for channel in range(image.shape[2]):
            hist, bins = np.histogram(image[:, :, channel].flatten(), bins=256, range=(0, 256))
            histograms.append(hist)
        return np.array(histograms), bins
    else:
        raise ValueError(f"Unsupported image shape: {image.shape}")

def plot_histogram_comparison(cover_image: np.ndarray, stego_image: np.ndarray, 
                            title: str = "Histogram Comparison") -> plt.Figure:
    """
    Plot histogram comparison between cover and stego images.
    Returns matplotlib Figure.
    """
    # Ensure both images have the same shape
    if len(cover_image.shape) != len(stego_image.shape):
        # If shapes differ, convert both to match the cover image shape
        if len(cover_image.shape) == 2 and len(stego_image.shape) == 3:
            # Convert stego to grayscale by averaging channels
            stego_image = np.mean(stego_image, axis=2).astype(np.uint8)
        elif len(cover_image.shape) == 3 and len(stego_image.shape) == 2:
            # Convert stego to RGB by stacking
            stego_image = np.stack([stego_image] * 3, axis=2)
    
    if len(cover_image.shape) == 2:
        # Grayscale - use 2x2 layout
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.patch.set_facecolor(_THEME["bg"])
        fig.suptitle(title, fontsize=14, fontweight='bold', color=_THEME["text"])
        
        cover_hist, cover_bins = calculate_histogram(cover_image)
        stego_hist, stego_bins = calculate_histogram(stego_image)
        
        for ax in axes.flat:
            _apply_dark_style(ax)
        
        axes[0, 0].bar(cover_bins[:-1], cover_hist, width=1, alpha=0.8, color=_THEME["primary"], label='Cover')
        axes[0, 0].set_title('Cover Image Histogram', color=_THEME["text"], fontsize=11)
        axes[0, 0].set_xlabel('Pixel Value', fontsize=9)
        axes[0, 0].set_ylabel('Frequency', fontsize=9)
        axes[0, 0].legend(facecolor=_THEME["surface"], edgecolor=_THEME["border"], labelcolor=_THEME["muted"])
        
        axes[0, 1].bar(stego_bins[:-1], stego_hist, width=1, alpha=0.8, color=_THEME["ch_red"], label='Stego')
        axes[0, 1].set_title('Stego Image Histogram', color=_THEME["text"], fontsize=11)
        axes[0, 1].set_xlabel('Pixel Value', fontsize=9)
        axes[0, 1].set_ylabel('Frequency', fontsize=9)
        axes[0, 1].legend(facecolor=_THEME["surface"], edgecolor=_THEME["border"], labelcolor=_THEME["muted"])
        
        # Difference
        diff_hist = stego_hist - cover_hist
        axes[1, 0].bar(cover_bins[:-1], diff_hist, width=1, alpha=0.8, color=_THEME["ch_diff"])
        axes[1, 0].set_title('Histogram Difference (Stego - Cover)', color=_THEME["text"], fontsize=11)
        axes[1, 0].set_xlabel('Pixel Value', fontsize=9)
        axes[1, 0].set_ylabel('Frequency Difference', fontsize=9)
        axes[1, 0].axhline(y=0, color=_THEME["muted_light"], linestyle='--', linewidth=0.6)
        
        # Hide empty subplot
        axes[1, 1].axis('off')
        axes[1, 1].set_facecolor(_THEME["bg"])
        
    else:
        # Color image (RGB) - use 2x3 layout
        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        fig.patch.set_facecolor(_THEME["bg"])
        fig.suptitle(title, fontsize=14, fontweight='bold', color=_THEME["text"])
        
        channel_colors = [_THEME["ch_red"], _THEME["ch_green"], _THEME["ch_blue"]]
        colors = ['Red', 'Green', 'Blue']
        cover_histograms, cover_bins = calculate_histogram(cover_image)
        stego_histograms, stego_bins = calculate_histogram(stego_image)
        
        for ax in axes.flat:
            _apply_dark_style(ax)
        
        for i, color in enumerate(colors):
            axes[0, i].bar(cover_bins[:-1], cover_histograms[i], width=1, 
                         alpha=0.7, color=channel_colors[i], label='Cover')
            axes[0, i].bar(stego_bins[:-1], stego_histograms[i], width=1, 
                         alpha=0.3, color=channel_colors[i], label='Stego')
            axes[0, i].set_title(f'{color} Channel Histogram', color=_THEME["text"], fontsize=11)
            axes[0, i].set_xlabel('Pixel Value', fontsize=9)
            axes[0, i].set_ylabel('Frequency', fontsize=9)
            axes[0, i].legend(facecolor=_THEME["surface"], edgecolor=_THEME["border"], labelcolor=_THEME["muted"])
        
        # Overall difference
        diff_histograms = stego_histograms - cover_histograms
        for i, color in enumerate(colors):
            axes[1, i].plot(cover_bins[:-1], diff_histograms[i], 
                          color=channel_colors[i], linewidth=1.5)
            axes[1, i].set_title(f'{color} Channel Difference', color=_THEME["text"], fontsize=11)
            axes[1, i].set_xlabel('Pixel Value', fontsize=9)
            axes[1, i].set_ylabel('Frequency Difference', fontsize=9)
            axes[1, i].axhline(y=0, color=_THEME["muted_light"], linestyle='--', linewidth=0.6)
    
    plt.tight_layout()
    return fig

def close_figure(fig: plt.Figure) -> None:
    """Close matplotlib figure to free memory."""
    try:
        plt.close(fig)
    except:
        pass

def plot_histogram_difference(cover_image: np.ndarray, stego_image: np.ndarray,
                            title: str = "Histogram Difference") -> plt.Figure:
    """
    Plot detailed histogram difference between cover and stego images.
    Returns matplotlib Figure.
    """
    # Ensure both images have the same shape
    if len(cover_image.shape) != len(stego_image.shape):
        # If shapes differ, convert both to match the cover image shape
        if len(cover_image.shape) == 2 and len(stego_image.shape) == 3:
            # Convert stego to grayscale by averaging channels
            stego_image = np.mean(stego_image, axis=2).astype(np.uint8)
        elif len(cover_image.shape) == 3 and len(stego_image.shape) == 2:
            # Convert stego to RGB by stacking
            stego_image = np.stack([stego_image] * 3, axis=2)
    
    fig, axes = plt.subplots(1, 1, figsize=(12, 6))
    fig.patch.set_facecolor(_THEME["bg"])
    fig.suptitle(title, fontsize=14, fontweight='bold', color=_THEME["text"])
    _apply_dark_style(axes)
    
    if len(cover_image.shape) == 2:
        # Grayscale
        cover_hist, cover_bins = calculate_histogram(cover_image)
        stego_hist, stego_bins = calculate_histogram(stego_image)
        diff_hist = stego_hist - cover_hist
        
        axes.bar(cover_bins[:-1], diff_hist, width=1, alpha=0.8, color=_THEME["ch_diff"])
        axes.set_title('Histogram Difference (Stego - Cover)', color=_THEME["text"], fontsize=11)
        axes.set_xlabel('Pixel Value', fontsize=9)
        axes.set_ylabel('Frequency Difference', fontsize=9)
        axes.axhline(y=0, color=_THEME["muted_light"], linestyle='--', linewidth=0.6)
        
        # Add statistics
        max_diff = np.max(np.abs(diff_hist))
        mean_diff = np.mean(diff_hist)
        std_diff = np.std(diff_hist)
        
        stats_text = f'Max |Diff|: {max_diff:.2f}\nMean Diff: {mean_diff:.2f}\nStd Dev: {std_diff:.2f}'
        axes.text(0.02, 0.98, stats_text, transform=axes.transAxes, 
                 verticalalignment='top', fontsize=8, color=_THEME["text_secondary"],
                 bbox=dict(boxstyle='round,pad=0.5', facecolor=_THEME["surface"], 
                           edgecolor=_THEME["border"], alpha=0.9))
        
    else:
        # Color image
        channel_colors = [_THEME["ch_red"], _THEME["ch_green"], _THEME["ch_blue"]]
        colors = ['Red', 'Green', 'Blue']
        cover_histograms, cover_bins = calculate_histogram(cover_image)
        stego_histograms, stego_bins = calculate_histogram(stego_image)
        diff_histograms = stego_histograms - cover_histograms
        
        for i, color in enumerate(colors):
            axes.plot(cover_bins[:-1], diff_histograms[i], 
                    color=channel_colors[i], label=f'{color} Channel', linewidth=1.5)
        
        axes.set_title('Histogram Difference by Channel (Stego - Cover)', color=_THEME["text"], fontsize=11)
        axes.set_xlabel('Pixel Value', fontsize=9)
        axes.set_ylabel('Frequency Difference', fontsize=9)
        axes.axhline(y=0, color=_THEME["muted_light"], linestyle='--', linewidth=0.6)
        axes.legend(facecolor=_THEME["surface"], edgecolor=_THEME["border"], labelcolor=_THEME["muted"])
    
    plt.tight_layout()
    return fig

def calculate_statistical_metrics(cover_image: np.ndarray, stego_image: np.ndarray) -> dict:
    """
    Calculate statistical metrics between cover and stego images.
    Returns dictionary with metrics.
    """
    # Ensure both images have the same shape
    if len(cover_image.shape) != len(stego_image.shape):
        # If shapes differ, convert both to match the cover image shape
        if len(cover_image.shape) == 2 and len(stego_image.shape) == 3:
            # Convert stego to grayscale by averaging channels
            stego_image = np.mean(stego_image, axis=2).astype(np.uint8)
        elif len(cover_image.shape) == 3 and len(stego_image.shape) == 2:
            # Convert stego to RGB by stacking
            stego_image = np.stack([stego_image] * 3, axis=2)
    
    metrics = {}
    
    # MSE (Mean Squared Error)
    mse = np.mean((cover_image.astype(float) - stego_image.astype(float)) ** 2)
    metrics['MSE'] = mse
    
    # PSNR (Peak Signal-to-Noise Ratio)
    if mse == 0:
        metrics['PSNR'] = float('inf')
    else:
        max_pixel = 255.0
        metrics['PSNR'] = 20 * np.log10(max_pixel / np.sqrt(mse))
    
    # MAE (Mean Absolute Error)
    mae = np.mean(np.abs(cover_image.astype(float) - stego_image.astype(float)))
    metrics['MAE'] = mae
    
    # Correlation coefficient
    cover_flat = cover_image.flatten()
    stego_flat = stego_image.flatten()
    correlation = np.corrcoef(cover_flat, stego_flat)[0, 1]
    metrics['Correlation'] = correlation
    
    return metrics

def plot_difference_heatmap(cover_image: np.ndarray, stego_image: np.ndarray, 
                            amplification: int = 50,
                            enhance_visibility: bool = True,
                            title: str = "Peta Perbedaan Piksel (Difference Heatmap)") -> Tuple[plt.Figure, dict]:
    """
    Plot spatial pixel difference heatmap between cover and stego images.
    Returns: (matplotlib Figure, stats_dict)
    """
    from scipy.ndimage import maximum_filter
    
    # Ensure matching dimensions
    if len(cover_image.shape) != len(stego_image.shape):
        if len(cover_image.shape) == 2 and len(stego_image.shape) == 3:
            stego_image = np.mean(stego_image, axis=2).astype(np.uint8)
        elif len(cover_image.shape) == 3 and len(stego_image.shape) == 2:
            stego_image = np.stack([stego_image] * 3, axis=2)

    diff = np.abs(stego_image.astype(np.float32) - cover_image.astype(np.float32))
    
    if len(diff.shape) == 3:
        diff_spatial = np.max(diff, axis=2)
    else:
        diff_spatial = diff

    mod_pixels = int(np.count_nonzero(diff_spatial > 0))
    total_pixels = int(diff_spatial.size)
    mod_pct = (mod_pixels / total_pixels) * 100 if total_pixels > 0 else 0.0
    max_diff = float(np.max(diff_spatial)) if total_pixels > 0 else 0.0

    stats = {
        "modified_pixels": mod_pixels,
        "total_pixels": total_pixels,
        "modified_percentage": mod_pct,
        "max_difference": max_diff,
        "amplification": amplification
    }

    # If enhance_visibility is on, apply a 3x3 dilation filter so single pixel changes are visible on screen
    if enhance_visibility and mod_pixels > 0:
        # Scale by amplification factor with maximum filter for crisp dot visibility
        diff_scaled = np.clip(diff_spatial * amplification, 0, 255)
        # Apply 3x3 max filter to prevent downsampling interpolation from hiding single pixels
        display_map = maximum_filter(diff_scaled, size=3)
    else:
        display_map = np.clip(diff_spatial * amplification, 0, 255)

    fig, ax = plt.subplots(figsize=(10, 6), facecolor=_THEME["bg"])
    ax.set_facecolor(_THEME["bg"])
    
    # Use a custom colormap that matches the Egyptian theme (Obsidian -> Lapis -> Turquoise -> Sandstone -> Papyrus)
    from matplotlib.colors import LinearSegmentedColormap
    cmap_colors = [_THEME["bg"], _THEME["ch_blue"], _THEME["success"], _THEME["amber"], _THEME["text"]]
    custom_cmap = LinearSegmentedColormap.from_list('egyptian_heat', cmap_colors, N=256)
    
    im = ax.imshow(display_map, cmap=custom_cmap, vmin=0, vmax=255)
    ax.set_title(f"{title} (Amplifikasi {amplification}x)", fontsize=12, fontweight='bold', pad=10, color=_THEME["text"])
    ax.axis('off')
    
    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.04)
    cbar.set_label(f"Magnitudo Perbedaan Teramplifikasi (0 - 255)", fontsize=9, color=_THEME["muted"])
    cbar.ax.yaxis.set_tick_params(color=_THEME["muted"])
    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color=_THEME["muted"], fontsize=8)
    cbar.outline.set_edgecolor(_THEME["border"])
    
    plt.tight_layout()
    return fig, stats

def simulate_jpeg_compression(image: np.ndarray, quality: int = 70) -> Tuple[np.ndarray, int]:
    """
    Simulate saving and reloading an image as JPEG with specified quality.
    Returns: (jpeg_image_array, file_size_in_bytes)
    """
    import io
    pil_img = Image.fromarray(image)
    if pil_img.mode != 'RGB':
        pil_img = pil_img.convert('RGB')
    
    buffer = io.BytesIO()
    pil_img.save(buffer, format='JPEG', quality=int(quality))
    file_size = buffer.tell()
    
    buffer.seek(0)
    reloaded_img = Image.open(buffer)
    jpeg_array = np.array(reloaded_img)
    return jpeg_array, file_size

def perform_chi_square_attack(image: np.ndarray, num_points: int = 60) -> Tuple[np.ndarray, np.ndarray]:
    """
    Perform Westfeld & Pfitzmann (1999) Chi-Square Steganalysis on image.
    Calculates probability of embedding across cumulative portions of the image.
    Returns: (percentages, probabilities)
    """
    from scipy.stats import chi2
    
    if len(image.shape) == 3:
        flat_data = image[:, :, 0].flatten()
    else:
        flat_data = image.flatten()
        
    total_len = len(flat_data)
    step = max(1, total_len // num_points)
    
    percentages = []
    probabilities = []
    
    for i in range(step, total_len + 1, step):
        sample = flat_data[:i]
        counts = np.bincount(sample, minlength=256)
        
        observed_even = counts[0::2]
        observed_odd = counts[1::2]
        expected = (observed_even + observed_odd) / 2.0
        
        valid = expected > 0
        if np.count_nonzero(valid) > 1:
            chi_val = np.sum(((observed_even[valid] - expected[valid]) ** 2) / expected[valid])
            dof = np.count_nonzero(valid) - 1
            p_val = 1.0 - chi2.cdf(chi_val, dof)
            prob_embedding = 1.0 - p_val
        else:
            prob_embedding = 0.0
            
        percentages.append((i / total_len) * 100.0)
        probabilities.append(float(np.clip(prob_embedding, 0.0, 1.0)))
        
    return np.array(percentages), np.array(probabilities)

def plot_chi_square_analysis(cover_image: np.ndarray, stego_image: np.ndarray, 
                             num_points: int = 60,
                             title: str = "Steganalisis Statistik Uji Chi-Square (Westfeld Attack)") -> Tuple[plt.Figure, dict]:
    """
    Plot Chi-Square probability curves for Cover and Stego images.
    Returns: (matplotlib Figure, stats_dict)
    """
    pct_cover, prob_cover = perform_chi_square_attack(cover_image, num_points)
    pct_stego, prob_stego = perform_chi_square_attack(stego_image, num_points)
    
    avg_cover_prob = float(np.mean(prob_cover))
    avg_stego_prob = float(np.mean(prob_stego))
    max_stego_prob = float(np.max(prob_stego))
    
    stats = {
        "avg_cover_prob": avg_cover_prob,
        "avg_stego_prob": avg_stego_prob,
        "max_stego_prob": max_stego_prob,
        "detection_status": "Terdeteksi Modifikasi LSB" if avg_stego_prob > 0.5 else "Aman / Sebaran Alami"
    }
    
    fig, ax = plt.subplots(figsize=(10, 5))
    fig.patch.set_facecolor(_THEME["bg"])
    _apply_dark_style(ax)
    
    # Cover curve - dashed, subdued
    ax.plot(pct_cover, prob_cover, label="Citra Cover (Asli)", color=_THEME["primary"], 
            linewidth=1.8, linestyle='--', alpha=0.7)
    # Stego curve - solid, prominent
    ax.plot(pct_stego, prob_stego, label="Citra Stego (Tersisip Pesan)", color=_THEME["ch_red"], 
            linewidth=2.2)
    
    # Threshold line
    ax.axhline(y=0.5, color=_THEME["amber"], linestyle=':', linewidth=1.2, alpha=0.8,
               label='Threshold Deteksi (P=0.5)')
    
    # Fill area above threshold for stego
    ax.fill_between(pct_stego, prob_stego, 0.5, 
                     where=(prob_stego > 0.5), 
                     alpha=0.08, color=_THEME["ch_red"])
    
    ax.set_title(title, fontsize=12, fontweight='bold', pad=12, color=_THEME["text"])
    ax.set_xlabel("Persentase Sampel Citra Terbaca (%)", fontsize=9, color=_THEME["muted"])
    ax.set_ylabel("Probabilitas Penyisipan Pesan P(Chi²)", fontsize=9, color=_THEME["muted"])
    ax.set_ylim(-0.05, 1.05)
    ax.legend(loc="upper right", framealpha=0.9, 
              facecolor=_THEME["surface"], edgecolor=_THEME["border"], labelcolor=_THEME["muted"])
    
    plt.tight_layout()
    return fig, stats
