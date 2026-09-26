import numpy as np
from PIL import Image
import time
import io

from elgamal import ElGamalDH
from steganography import LSBSteganography
from analysis import calculate_statistical_metrics

def create_test_image(size=(512, 512), color_mode='RGB'):
    """Create test image for testing."""
    if color_mode == 'RGB':
        img_array = np.random.randint(0, 256, (*size, 3), dtype=np.uint8)
    elif color_mode == 'RGBA':
        img_array = np.random.randint(0, 256, (*size, 4), dtype=np.uint8)
    else:  # Grayscale
        img_array = np.random.randint(0, 256, size, dtype=np.uint8)
    return img_array

def test_elgamal_initialization():
    """Test ElGamal initialization performance."""
    print("Testing ElGamal initialization...")
    start = time.time()
    elgamal = ElGamalDH()
    init_time = time.time() - start
    print(f"✓ ElGamal initialization time: {init_time:.4f}s")
    
    # Test key generation
    start = time.time()
    private_key, public_key = elgamal.generate_keypair()
    keygen_time = time.time() - start
    print(f"✓ Key generation time: {keygen_time:.4f}s")
    
    return elgamal, private_key, public_key

def test_encryption_decryption(elgamal, public_key, private_key):
    """Test encryption and decryption."""
    print("\nTesting encryption/decryption...")
    test_message = b"Hello, World! This is a test message for steganography."
    
    start = time.time()
    encrypted = elgamal.encrypt_bytes(test_message, public_key)
    encrypt_time = time.time() - start
    print(f"✓ Encryption time: {encrypt_time:.4f}s (message: {len(test_message)} bytes, encrypted: {len(encrypted)} bytes)")
    
    start = time.time()
    decrypted = elgamal.decrypt_bytes(encrypted, private_key)
    decrypt_time = time.time() - start
    print(f"✓ Decryption time: {decrypt_time:.4f}s")
    
    if decrypted == test_message:
        print("✓ Encryption/decryption successful!")
    else:
        print("✗ Encryption/decryption failed!")
    
    return encrypted

def test_lsb_steganography_performance(image_array, encrypted_message):
    """Test LSB steganography performance."""
    print("\nTesting LSB steganography...")
    stego = LSBSteganography(seed=12345)
    
    # Test capacity calculation
    start = time.time()
    capacity = stego.calculate_capacity(image_array)
    capacity_time = time.time() - start
    print(f"✓ Capacity calculation time: {capacity_time:.4f}s (capacity: {capacity} bytes)")
    
    if len(encrypted_message) > capacity:
        print(f"⚠ Message too large for capacity test. Using smaller message.")
        encrypted_message = encrypted_message[:capacity // 2]
    
    # Test embedding
    start = time.time()
    stego_array = stego.embed(image_array, encrypted_message)
    embed_time = time.time() - start
    print(f"✓ Embedding time: {embed_time:.4f}s")
    
    # Test extraction
    start = time.time()
    extracted = stego.extract(stego_array)
    extract_time = time.time() - start
    print(f"✓ Extraction time: {extract_time:.4f}s")
    
    if extracted == encrypted_message:
        print("✓ Embedding/extraction successful!")
    else:
        print("✗ Embedding/extraction failed!")
    
    # Test PSNR
    start = time.time()
    psnr = stego.calculate_psnr(image_array, stego_array)
    psnr_time = time.time() - start
    print(f"✓ PSNR calculation time: {psnr_time:.4f}s (PSNR: {psnr:.2f} dB)")
    
    return stego_array

def test_wrong_stego_key(image_array, encrypted_message):
    """Test extraction with wrong stego key."""
    print("\nTesting wrong stego key...")
    stego_wrong = LSBSteganography(seed=99999)
    stego_array = LSBSteganography(seed=12345).embed(image_array, encrypted_message)
    
    try:
        extracted = stego_wrong.extract(stego_array)
        print(f"⚠ Wrong key extraction returned data (should fail): {len(extracted)} bytes")
    except Exception as e:
        print(f"✓ Wrong key extraction failed as expected: {type(e).__name__}")

def test_different_image_modes():
    """Test with different image modes."""
    print("\nTesting different image modes...")
    modes = ['RGB', 'RGBA', 'grayscale']
    
    for mode in modes:
        print(f"\nTesting {mode} mode...")
        image = create_test_image((256, 256), mode)
        stego = LSBSteganography(seed=12345)
        test_msg = b"Test message"
        
        try:
            stego_array = stego.embed(image, test_msg)
            extracted = stego.extract(stego_array)
            if extracted == test_msg:
                print(f"✓ {mode} mode successful!")
            else:
                print(f"✗ {mode} mode failed!")
        except Exception as e:
            print(f"✗ {mode} mode error: {e}")

def test_capacity_validation():
    """Test capacity validation."""
    print("\nTesting capacity validation...")
    image = create_test_image((100, 100), 'RGB')
    stego = LSBSteganography(seed=12345)
    
    capacity = stego.calculate_capacity(image)
    print(f"Image capacity: {capacity} bytes")
    
    # Test with message that exceeds capacity
    large_message = b"X" * (capacity + 100)
    try:
        stego.embed(image, large_message)
        print("✗ Capacity validation failed (should reject large message)")
    except ValueError as e:
        print(f"✓ Capacity validation works: {e}")

def main():
    print("=" * 60)
    print("Optimization Testing Script")
    print("=" * 60)
    
    # Test ElGamal
    elgamal, private_key, public_key = test_elgamal_initialization()
    encrypted = test_encryption_decryption(elgamal, public_key, private_key)
    
    # Test LSB steganography with RGB image
    print("\n" + "=" * 60)
    print("Testing with RGB image (512x512)")
    print("=" * 60)
    rgb_image = create_test_image((512, 512), 'RGB')
    test_lsb_steganography_performance(rgb_image, encrypted)
    
    # Test wrong stego key
    test_wrong_stego_key(rgb_image, encrypted)
    
    # Test different image modes
    test_different_image_modes()
    
    # Test capacity validation
    test_capacity_validation()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()
