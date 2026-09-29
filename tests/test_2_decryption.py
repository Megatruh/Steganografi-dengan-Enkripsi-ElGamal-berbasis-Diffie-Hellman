"""
Test 2: Decryption Test
Testing dekripsi dari hasil enkripsi test 1
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image
import numpy as np
from elgamal import ElGamalDH
from steganography import LSBSteganography

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

def test_decryption():
    """Test decryption process"""
    print("=" * 60)
    print("TEST 2: Decryption Test")
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
    
    # Initialize steganography with same stego key
    stego_key = 30092026
    print(f"\n[+] Initializing LSB Steganography with seed: {stego_key}")
    stego = LSBSteganography(seed=stego_key, nsym=20)
    
    # Extract encrypted message
    print(f"\n[+] Extracting encrypted message from stego image...")
    try:
        encrypted_bytes = stego.extract(stego_array)
        print(f"    Extracted length: {len(encrypted_bytes)} bytes")
    except Exception as e:
        print(f"\n[!] ERROR: Failed to extract message: {e}")
        return False
    
    # Decrypt message with ElGamal
    print(f"\n[+] Decrypting message with ElGamal...")
    try:
        decrypted_bytes = elgamal.decrypt_bytes(encrypted_bytes, x)
        decrypted_message = decrypted_bytes.decode('utf-8')
        print(f"    Decrypted message: '{decrypted_message}'")
    except Exception as e:
        print(f"\n[!] ERROR: Failed to decrypt message: {e}")
        return False
    
    # Verify the decrypted message
    expected_message = "uji enkripsi"
    if decrypted_message == expected_message:
        print(f"\n[+] Message verification: SUCCESS")
        print(f"    Expected: '{expected_message}'")
        print(f"    Got: '{decrypted_message}'")
    else:
        print(f"\n[!] ERROR: Message verification failed!")
        print(f"    Expected: '{expected_message}'")
        print(f"    Got: '{decrypted_message}'")
        return False
    
    print("\n" + "=" * 60)
    print("TEST 2: PASSED - Decryption successful!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = test_decryption()
    sys.exit(0 if success else 1)
