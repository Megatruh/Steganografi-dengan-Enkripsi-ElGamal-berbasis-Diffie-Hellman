import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple
import hashlib

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
