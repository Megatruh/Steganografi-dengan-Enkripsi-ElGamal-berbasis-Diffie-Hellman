"""
Test 3: Capacity Limit Test
Testing enkripsi gagal jika pesan melebihi kapasitas
Menggunakan paragraf_dummy.txt yang berisi 100 paragraf dummy
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

def test_capacity_limit():
    """Test that encryption fails when message exceeds capacity"""
    print("=" * 60)
    print("TEST 3: Capacity Limit Test")
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
    
    # Load image
    image_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Jonathan_Pollard.png')
    print(f"\n[+] Loading image: {image_path}")
    cover_image = Image.open(image_path)
    cover_array = np.array(cover_image)
    print(f"    Image shape: {cover_array.shape}")
    
    # Initialize steganography with stego key
    stego_key = 30092026
    print(f"\n[+] Initializing LSB Steganography with seed: {stego_key}")
    stego = LSBSteganography(seed=stego_key, nsym=20)
    
    # Calculate capacity
    capacity = stego.calculate_capacity(cover_array)
    print(f"    Maximum capacity: {capacity} bytes")
    
    # Load dummy paragraphs
    dummy_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'paragraf_dummy.txt')
    print(f"\n[+] Loading dummy paragraphs from: {dummy_file}")
    
    if not os.path.exists(dummy_file):
        print(f"\n[!] ERROR: Dummy file not found at {dummy_file}")
        return False
    
    with open(dummy_file, 'r', encoding='utf-8') as f:
        message = f.read()
    
    message_bytes = message.encode('utf-8')
    print(f"    Message length: {len(message_bytes)} bytes")
    print(f"    Number of characters: {len(message)}")
    
    # Check if message exceeds capacity
    if len(message_bytes) <= capacity:
        print(f"\n[!] WARNING: Message does not exceed capacity!")
        print(f"    This test expects message to exceed capacity.")
        print(f"    Capacity: {capacity} bytes, Message: {len(message_bytes)} bytes")
        # Continue anyway to test the behavior
    
    # Try to encrypt message with ElGamal
    print(f"\n[+] Attempting to encrypt message with ElGamal...")
    try:
        encrypted_bytes = elgamal.encrypt_bytes(message_bytes, y)
        print(f"    Encrypted length: {len(encrypted_bytes)} bytes")
    except Exception as e:
        print(f"\n[!] ERROR during encryption: {e}")
        return False
    
    # Try to embed encrypted message into image (should fail)
    print(f"\n[+] Attempting to embed encrypted message into image...")
    print(f"    This should FAIL because message exceeds capacity.")
    
    try:
        stego_array = stego.embed(cover_array, encrypted_bytes)
        print(f"\n[!] ERROR: Embedding succeeded when it should have failed!")
        print(f"    This indicates the capacity check is not working properly.")
        return False
    except ValueError as e:
        if "too large" in str(e).lower() or "capacity" in str(e).lower():
            print(f"\n[+] Embedding correctly failed with error:")
            print(f"    {e}")
            print(f"\n[+] Capacity limit enforcement: WORKING")
        else:
            print(f"\n[!] ERROR: Embedding failed with unexpected error:")
            print(f"    {e}")
            return False
    except Exception as e:
        print(f"\n[!] ERROR: Embedding failed with unexpected error:")
        print(f"    {e}")
        return False
    
    print("\n" + "=" * 60)
    print("TEST 3: PASSED - Capacity limit correctly enforced!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = test_capacity_limit()
    sys.exit(0 if success else 1)
