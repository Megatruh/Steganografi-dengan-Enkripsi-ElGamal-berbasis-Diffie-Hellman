"""
Test 1: Full Encryption Test
Testing fitur enkripsi secara full dengan:
- Foto: Jonathan_Pollard.png
- Stego Key: 30092026
- Pesan: "uji enkripsi"
- Stego Parameter: dari dummy_steego_parameter.txt
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

def test_full_encryption():
    """Test full encryption process"""
    print("=" * 60)
    print("TEST 1: Full Encryption Test")
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
    print(f"    Image size: {cover_image.size}")
    
    # Initialize steganography with stego key
    stego_key = 30092026
    print(f"\n[+] Initializing LSB Steganography with seed: {stego_key}")
    stego = LSBSteganography(seed=stego_key, nsym=20)
    
    # Calculate capacity
    capacity = stego.calculate_capacity(cover_array)
    print(f"    Maximum capacity: {capacity} bytes")
    
    # Message to encrypt
    message = "uji enkripsi"
    message_bytes = message.encode('utf-8')
    print(f"\n[+] Message to encrypt: '{message}'")
    print(f"    Message length: {len(message_bytes)} bytes")
    
    # Check if message fits
    if len(message_bytes) > capacity:
        print(f"\n[!] ERROR: Message too large for capacity!")
        return False
    
    # Encrypt message with ElGamal
    print(f"\n[+] Encrypting message with ElGamal...")
    encrypted_bytes = elgamal.encrypt_bytes(message_bytes, y)
    print(f"    Encrypted length: {len(encrypted_bytes)} bytes")
    
    # Check if encrypted message fits
    if len(encrypted_bytes) > capacity:
        print(f"\n[!] ERROR: Encrypted message too large for capacity!")
        return False
    
    # Embed encrypted message into image
    print(f"\n[+] Embedding encrypted message into image...")
    stego_array = stego.embed(cover_array, encrypted_bytes)
    print(f"    Stego image shape: {stego_array.shape}")
    
    # Calculate PSNR
    psnr = stego.calculate_psnr(cover_array, stego_array)
    print(f"    PSNR: {psnr:.2f} dB")
    
    # Save stego image
    output_path = os.path.join(os.path.dirname(__file__), 'test1_stego_image.png')
    stego_image = Image.fromarray(stego_array)
    stego_image.save(output_path)
    print(f"\n[+] Stego image saved to: {output_path}")
    
    print("\n" + "=" * 60)
    print("TEST 1: PASSED - Full encryption successful!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = test_full_encryption()
    sys.exit(0 if success else 1)
