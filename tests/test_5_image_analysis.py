"""
Test 5: Image Analysis Test
Testing menjalankan fitur analisis gambar
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image
import numpy as np
from steganography import LSBSteganography
import analysis

def test_image_analysis():
    """Test image analysis features"""
    print("=" * 60)
    print("TEST 5: Image Analysis Test")
    print("=" * 60)
    
    # Load cover image
    image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Jonathan_Pollard.png')
    print(f"\n[+] Loading cover image: {image_path}")
    cover_image = Image.open(image_path)
    cover_array = np.array(cover_image)
    print(f"    Image shape: {cover_array.shape}")
    
    # Load stego image from test 1
    stego_image_path = os.path.join(os.path.dirname(__file__), 'test1_stego_image.png')
    
    if not os.path.exists(stego_image_path):
        print(f"\n[!] ERROR: Stego image not found at {stego_image_path}")
        print(f"    Please run test_1_full_encryption.py first!")
        return False
    
    print(f"\n[+] Loading stego image: {stego_image_path}")
    stego_image = Image.open(stego_image_path)
    stego_array = np.array(stego_image)
    print(f"    Stego image shape: {stego_array.shape}")
    
    # Test 1: Histogram Comparison
    print(f"\n[+] Test 5.1: Histogram Comparison")
    try:
        fig = analysis.plot_histogram_comparison(cover_array, stego_array, 
                                                 title="Histogram Comparison: Cover vs Stego")
        output_path = os.path.join(os.path.dirname(__file__), 'test5_histogram_comparison.png')
        fig.savefig(output_path, dpi=150, bbox_inches='tight')
        analysis.close_figure(fig)
        print(f"    Histogram comparison saved to: {output_path}")
        print(f"    Status: SUCCESS")
    except Exception as e:
        print(f"    Status: FAILED - {e}")
        return False
    
    # Test 2: Histogram Difference
    print(f"\n[+] Test 5.2: Histogram Difference")
    try:
        fig = analysis.plot_histogram_difference(cover_array, stego_array,
                                                 title="Histogram Difference: Stego - Cover")
        output_path = os.path.join(os.path.dirname(__file__), 'test5_histogram_difference.png')
        fig.savefig(output_path, dpi=150, bbox_inches='tight')
        analysis.close_figure(fig)
        print(f"    Histogram difference saved to: {output_path}")
        print(f"    Status: SUCCESS")
    except Exception as e:
        print(f"    Status: FAILED - {e}")
        return False
    
    # Test 3: Difference Heatmap
    print(f"\n[+] Test 5.3: Difference Heatmap")
    try:
        fig, stats = analysis.plot_difference_heatmap(cover_array, stego_array,
                                                      amplification=50,
                                                      title="Peta Perbedaan Piksel")
        output_path = os.path.join(os.path.dirname(__file__), 'test5_difference_heatmap.png')
        fig.savefig(output_path, dpi=150, bbox_inches='tight')
        analysis.close_figure(fig)
        print(f"    Difference heatmap saved to: {output_path}")
        print(f"    Modified pixels: {stats['modified_pixels']}")
        print(f"    Modified percentage: {stats['modified_percentage']:.2f}%")
        print(f"    Max difference: {stats['max_difference']}")
        print(f"    Status: SUCCESS")
    except Exception as e:
        print(f"    Status: FAILED - {e}")
        return False
    
    # Test 4: Statistical Metrics
    print(f"\n[+] Test 5.4: Statistical Metrics")
    try:
        metrics = analysis.calculate_statistical_metrics(cover_array, stego_array)
        print(f"    MSE: {metrics['MSE']:.4f}")
        print(f"    PSNR: {metrics['PSNR']:.2f} dB")
        print(f"    MAE: {metrics['MAE']:.4f}")
        print(f"    Correlation: {metrics['Correlation']:.4f}")
        print(f"    Status: SUCCESS")
    except Exception as e:
        print(f"    Status: FAILED - {e}")
        return False
    
    # Test 5: Chi-Square Analysis
    print(f"\n[+] Test 5.5: Chi-Square Steganalysis")
    try:
        fig, stats = analysis.plot_chi_square_analysis(cover_array, stego_array,
                                                      num_points=60,
                                                      title="Steganalisis Statistik Uji Chi-Square")
        output_path = os.path.join(os.path.dirname(__file__), 'test5_chi_square_analysis.png')
        fig.savefig(output_path, dpi=150, bbox_inches='tight')
        analysis.close_figure(fig)
        print(f"    Chi-square analysis saved to: {output_path}")
        print(f"    Avg cover probability: {stats['avg_cover_prob']:.4f}")
        print(f"    Avg stego probability: {stats['avg_stego_prob']:.4f}")
        print(f"    Max stego probability: {stats['max_stego_prob']:.4f}")
        print(f"    Detection status: {stats['detection_status']}")
        print(f"    Status: SUCCESS")
    except Exception as e:
        print(f"    Status: FAILED - {e}")
        return False
    
    # Test 6: LSB Plane Extraction
    print(f"\n[+] Test 5.6: LSB Plane Extraction")
    try:
        stego_key = 30092026
        stego = LSBSteganography(seed=stego_key, nsym=20)
        
        lsb_plane = stego.get_lsb_plane(stego_array)
        output_path = os.path.join(os.path.dirname(__file__), 'test5_lsb_plane.png')
        lsb_image = Image.fromarray(lsb_plane)
        lsb_image.save(output_path)
        print(f"    LSB plane saved to: {output_path}")
        print(f"    LSB plane shape: {lsb_plane.shape}")
        print(f"    Status: SUCCESS")
    except Exception as e:
        print(f"    Status: FAILED - {e}")
        return False
    
    print("\n" + "=" * 60)
    print("TEST 5: PASSED - All image analysis features working!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = test_image_analysis()
    sys.exit(0 if success else 1)
