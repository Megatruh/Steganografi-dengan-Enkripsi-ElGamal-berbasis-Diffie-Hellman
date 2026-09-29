"""
Test 6: JPEG Compression Test
Testing menjalankan fitur uji JPEG compression
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image
import numpy as np
from elgamal import ElGamalDH
from steganography import LSBSteganography
import analysis

def parse_stego_parameters(file_path):
    """Parse stego parameters from dummy_steego_parameter.txt"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Extract p (Prime Modulus)
    p_start = content.find("Prime Modulus (p)")
    p_end = content.find("\n\n", p_start)
    p_text = content[p_start:p_end].split('\n')[1].strip()
    p = int(p_text)
    
    # Extract g (Generator)
    g_start = content.find("Generator Kuil (g)")
    g_end = content.find("\n\n", g_start)
    g_text = content[g_start:g_end].split('\n')[1].strip()
    g = int(g_text)
    
    # Extract x (Private Key)
    x_start = content.find("Private Key (x)")
    x_end = content.find("\n\n", x_start)
    x_text = content[x_start:x_end].split('\n')[1].strip()
    x = int(x_text)
    
    # Extract y (Public Key)
    y_start = content.find("Public Key (y)")
    y_text = content[y_start:].split('\n')[1].strip()
    y = int(y_text)
    
    return p, g, x, y

def test_jpeg_compression():
    """Test JPEG compression and its effect on steganography"""
    print("=" * 60)
    print("TEST 6: JPEG Compression Test")
    print("=" * 60)
    
    # Load stego parameters
    param_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'dummy_steego_parameter.txt')
    p, g, x, y = parse_stego_parameters(param_file)
    
    print(f"\n[+] Stego Parameters loaded:")
    print(f"    Prime Modulus (p): {p.bit_length()} bits")
    print(f"    Generator (g): {g}")
    print(f"    Private Key (x): {x.bit_length()} bits")
    print(f"    Public Key (y): {y.bit_length()} bits")
    
    # Initialize ElGamal with custom parameters
    elgamal = ElGamalDH(p=p, g=g)
    
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
    
    # Test different JPEG quality levels
    quality_levels = [95, 85, 75, 65, 55]
    
    print(f"\n[+] Testing JPEG compression at different quality levels:")
    
    for quality in quality_levels:
        print(f"\n--- Quality: {quality} ---")
        
        # Simulate JPEG compression
        try:
            jpeg_array, file_size = analysis.simulate_jpeg_compression(stego_array, quality=quality)
            print(f"    JPEG compression successful")
            print(f"    File size: {file_size} bytes ({file_size / 1024:.2f} KB)")
            print(f"    Shape: {jpeg_array.shape}")
            
            # Save compressed image
            output_path = os.path.join(os.path.dirname(__file__), f'test6_jpeg_q{quality}.jpg')
            jpeg_image = Image.fromarray(jpeg_array)
            jpeg_image.save(output_path, quality=quality)
            print(f"    Saved to: {output_path}")
            
            # Try to extract message from JPEG compressed image
            stego_key = 30092026
            stego = LSBSteganography(seed=stego_key, nsym=20)
            
            print(f"    Attempting to extract message from JPEG compressed image...")
            try:
                encrypted_bytes = stego.extract(jpeg_array)
                print(f"    Extraction successful - length: {len(encrypted_bytes)} bytes")
                
                # Try to decrypt
                try:
                    decrypted_bytes = elgamal.decrypt_bytes(encrypted_bytes, x)
                    decrypted_message = decrypted_bytes.decode('utf-8')
                    print(f"    Decryption successful - message: '{decrypted_message}'")
                    
                    expected_message = "uji enkripsi"
                    if decrypted_message == expected_message:
                        print(f"    Message integrity: VERIFIED")
                    else:
                        print(f"    Message integrity: CORRUPTED")
                        print(f"    Expected: '{expected_message}'")
                        print(f"    Got: '{decrypted_message}'")
                        
                except Exception as e:
                    print(f"    Decryption failed (JPEG compression damaged data):")
                    print(f"    {e}")
                    
            except Exception as e:
                print(f"    Extraction failed (JPEG compression damaged data):")
                print(f"    {e}")
                
        except Exception as e:
            print(f"    JPEG compression failed: {e}")
    
    # Test with very low quality to demonstrate failure
    print(f"\n--- Quality: 30 (Low Quality Test) ---")
    try:
        jpeg_array, file_size = analysis.simulate_jpeg_compression(stego_array, quality=30)
        print(f"    JPEG compression successful")
        print(f"    File size: {file_size} bytes ({file_size / 1024:.2f} KB)")
        
        output_path = os.path.join(os.path.dirname(__file__), 'test6_jpeg_q30.jpg')
        jpeg_image = Image.fromarray(jpeg_array)
        jpeg_image.save(output_path, quality=30)
        print(f"    Saved to: {output_path}")
        
        # Try to extract message
        stego_key = 30092026
        stego = LSBSteganography(seed=stego_key, nsym=20)
        
        print(f"    Attempting to extract message from heavily compressed image...")
        try:
            encrypted_bytes = stego.extract(jpeg_array)
            print(f"    Extraction successful - length: {len(encrypted_bytes)} bytes")
            
            try:
                decrypted_bytes = elgamal.decrypt_bytes(encrypted_bytes, x)
                decrypted_message = decrypted_bytes.decode('utf-8')
                print(f"    Decryption successful - message: '{decrypted_message}'")
            except Exception as e:
                print(f"    Decryption failed (expected with heavy compression):")
                print(f"    {e}")
                
        except Exception as e:
            print(f"    Extraction failed (expected with heavy compression):")
            print(f"    {e}")
            
    except Exception as e:
        print(f"    JPEG compression failed: {e}")
    
    print("\n" + "=" * 60)
    print("TEST 6: PASSED - JPEG compression test completed!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = test_jpeg_compression()
    sys.exit(0 if success else 1)
