"""
Test 4: Wrong Stego Key Test
Testing gagal dekripsi jika stego key berbeda
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

def test_wrong_stego_key():
    """Test that decryption fails with wrong stego key"""
    print("=" * 60)
    print("TEST 4: Wrong Stego Key Test")
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
    
    # Use WRONG stego key
    correct_stego_key = 30092026
    wrong_stego_key = 12345678  # Different key
    print(f"\n[+] Testing with WRONG stego key:")
    print(f"    Correct key: {correct_stego_key}")
    print(f"    Wrong key: {wrong_stego_key}")
    
    # Initialize steganography with wrong stego key
    print(f"\n[+] Initializing LSB Steganography with WRONG seed: {wrong_stego_key}")
    stego = LSBSteganography(seed=wrong_stego_key, nsym=20)
    
    # Try to extract encrypted message with wrong key
    print(f"\n[+] Attempting to extract message with WRONG stego key...")
    print(f"    This should FAIL or produce garbage data.")
    
    try:
        encrypted_bytes = stego.extract(stego_array)
        print(f"    Extracted length: {len(encrypted_bytes)} bytes")
        
        # Try to decrypt
        print(f"\n[+] Attempting to decrypt extracted data...")
        try:
            decrypted_bytes = elgamal.decrypt_bytes(encrypted_bytes, x)
            decrypted_message = decrypted_bytes.decode('utf-8', errors='replace')
            print(f"    Decrypted message: '{decrypted_message}'")
            
            # Check if message is correct (it shouldn't be)
            expected_message = "uji enkripsi"
            if decrypted_message == expected_message:
                print(f"\n[!] ERROR: Decryption succeeded with wrong stego key!")
                print(f"    This is a security issue - wrong key should not work.")
                return False
            else:
                print(f"\n[+] Decryption with wrong key produced incorrect message (expected)")
                print(f"    Expected: '{expected_message}'")
                print(f"    Got: '{decrypted_message}'")
                
        except Exception as e:
            print(f"\n[+] Decryption failed with error (expected):")
            print(f"    {e}")
            
    except Exception as e:
        print(f"\n[+] Extraction failed with error (expected):")
        print(f"    {e}")
        if "Invalid encoded message length" in str(e) or "wrong stego key" in str(e).lower():
            print(f"\n[+] Wrong stego key correctly detected!")
        else:
            print(f"\n[!] ERROR: Unexpected error during extraction")
            return False
    
    print("\n" + "=" * 60)
    print("TEST 4: PASSED - Wrong stego key correctly rejected!")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = test_wrong_stego_key()
    sys.exit(0 if success else 1)
