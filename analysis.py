import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple
import hashlib
from PIL import Image

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
        fig.suptitle(title, fontsize=16)
        
        cover_hist, cover_bins = calculate_histogram(cover_image)
        stego_hist, stego_bins = calculate_histogram(stego_image)
        
        axes[0, 0].bar(cover_bins[:-1], cover_hist, width=1, alpha=0.7, color='blue', label='Cover')
        axes[0, 0].set_title('Cover Image Histogram')
        axes[0, 0].set_xlabel('Pixel Value')
        axes[0, 0].set_ylabel('Frequency')
        axes[0, 0].legend()
        
        axes[0, 1].bar(stego_bins[:-1], stego_hist, width=1, alpha=0.7, color='red', label='Stego')
        axes[0, 1].set_title('Stego Image Histogram')
        axes[0, 1].set_xlabel('Pixel Value')
        axes[0, 1].set_ylabel('Frequency')
        axes[0, 1].legend()
        
        # Difference
        diff_hist = stego_hist - cover_hist
        axes[1, 0].bar(cover_bins[:-1], diff_hist, width=1, alpha=0.7, color='green')
        axes[1, 0].set_title('Histogram Difference (Stego - Cover)')
        axes[1, 0].set_xlabel('Pixel Value')
        axes[1, 0].set_ylabel('Frequency Difference')
        axes[1, 0].axhline(y=0, color='black', linestyle='--', linewidth=0.5)
        
        # Hide empty subplot
        axes[1, 1].axis('off')
        
    else:
        # Color image (RGB) - use 2x3 layout
        fig, axes = plt.subplots(2, 3, figsize=(18, 10))
        fig.suptitle(title, fontsize=16)
        
        colors = ['Red', 'Green', 'Blue']
        cover_histograms, cover_bins = calculate_histogram(cover_image)
        stego_histograms, stego_bins = calculate_histogram(stego_image)
        
        for i, color in enumerate(colors):
            axes[0, i].bar(cover_bins[:-1], cover_histograms[i], width=1, 
                         alpha=0.7, color=color.lower(), label='Cover')
            axes[0, i].bar(stego_bins[:-1], stego_histograms[i], width=1, 
                         alpha=0.3, color=color.lower(), label='Stego')
            axes[0, i].set_title(f'{color} Channel Histogram')
            axes[0, i].set_xlabel('Pixel Value')
            axes[0, i].set_ylabel('Frequency')
            axes[0, i].legend()
        
        # Overall difference
        diff_histograms = stego_histograms - cover_histograms
        for i, color in enumerate(colors):
            axes[1, i].plot(cover_bins[:-1], diff_histograms[i], 
                          color=color.lower(), linewidth=2)
            axes[1, i].set_title(f'{color} Channel Difference')
            axes[1, i].set_xlabel('Pixel Value')
            axes[1, i].set_ylabel('Frequency Difference')
            axes[1, i].axhline(y=0, color='black', linestyle='--', linewidth=0.5)
            axes[1, i].grid(True, alpha=0.3)
    
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
    fig.suptitle(title, fontsize=16)
    
    if len(cover_image.shape) == 2:
        # Grayscale
        cover_hist, cover_bins = calculate_histogram(cover_image)
        stego_hist, stego_bins = calculate_histogram(stego_image)
        diff_hist = stego_hist - cover_hist
        
        axes.bar(cover_bins[:-1], diff_hist, width=1, alpha=0.7, color='purple')
        axes.set_title('Histogram Difference (Stego - Cover)')
        axes.set_xlabel('Pixel Value')
        axes.set_ylabel('Frequency Difference')
        axes.axhline(y=0, color='black', linestyle='--', linewidth=0.5)
        
        # Add statistics
        max_diff = np.max(np.abs(diff_hist))
        mean_diff = np.mean(diff_hist)
        std_diff = np.std(diff_hist)
        
        stats_text = f'Max |Difference|: {max_diff:.2f}\nMean Difference: {mean_diff:.2f}\nStd Dev: {std_diff:.2f}'
        axes.text(0.02, 0.98, stats_text, transform=axes.transAxes, 
                 verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
    else:
        # Color image
        colors = ['Red', 'Green', 'Blue']
        cover_histograms, cover_bins = calculate_histogram(cover_image)
        stego_histograms, stego_bins = calculate_histogram(stego_image)
        diff_histograms = stego_histograms - cover_histograms
        
        for i, color in enumerate(colors):
            axes.plot(cover_bins[:-1], diff_histograms[i], 
                    color=color.lower(), label=f'{color} Channel', linewidth=2)
        
        axes.set_title('Histogram Difference by Channel (Stego - Cover)')
        axes.set_xlabel('Pixel Value')
        axes.set_ylabel('Frequency Difference')
        axes.axhline(y=0, color='black', linestyle='--', linewidth=0.5)
        axes.legend()
        axes.grid(True, alpha=0.3)
    
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

    fig, ax = plt.subplots(figsize=(10, 6), facecolor='#1c1917')
    ax.set_facecolor('#1c1917')
    
    im = ax.imshow(display_map, cmap='hot', vmin=0, vmax=255)
    ax.set_title(f"{title} (Amplifikasi {amplification}x)", fontsize=13, fontweight='bold', pad=10, color='#f3eee6')
    ax.axis('off')
    
    cbar = fig.colorbar(im, ax=ax, fraction=0.035, pad=0.04)
    cbar.set_label(f"Magnitudo Perbedaan Teramplifikasi (0 - 255)", fontsize=9, color='#f3eee6')
    cbar.ax.yaxis.set_tick_params(color='#f3eee6')
    plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color='#f3eee6')
    
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
    ax.plot(pct_cover, prob_cover, label="Citra Cover (Asli)", color='#3b82f6', linewidth=2, linestyle='--')
    ax.plot(pct_stego, prob_stego, label="Citra Stego (Tersisip Pesan)", color='#e05353', linewidth=2.5)
    
    ax.axhline(y=0.5, color='#c59b27', linestyle=':', label='Threshold Deteksi (P=0.5)')
    
    ax.set_title(title, fontsize=13, fontweight='bold', pad=10)
    ax.set_xlabel("Persentase Sampel Citra Terbaca (%)", fontsize=10)
    ax.set_ylabel("Probabilitas Penyisipan Pesan P(Chi^2)", fontsize=10)
    ax.set_ylim(-0.05, 1.05)
    ax.grid(True, alpha=0.3)
    ax.legend(loc="upper right", framealpha=0.8)
    
    plt.tight_layout()
    return fig, stats

