# StegoCipher Test Suite

This directory contains 6 comprehensive test files for the StegoCipher steganography project.

## Test Files

### 1. test_1_full_encryption.py
**Purpose**: Test full encryption workflow

Tests:
- Loads stego parameters from `dummy_steego_parameter.txt`
- Loads image `Jonathan_Pollard.png`
- Uses stego key `30092026`
- Encrypts message "uji enkripsi" with ElGamal
- Embeds encrypted message into image using LSB steganography
- Saves stego image as `test1_stego_image.png`
- Calculates and displays PSNR

**Run**: `python test_1_full_encryption.py`

**Output**: `test1_stego_image.png`

---

### 2. test_2_decryption.py
**Purpose**: Test decryption of encrypted message from Test 1

Tests:
- Loads stego parameters from `dummy_steego_parameter.txt`
- Loads stego image from Test 1 (`test1_stego_image.png`)
- Uses same stego key `30092026`
- Extracts encrypted message from stego image
- Decrypts message with ElGamal
- Verifies decrypted message matches original "uji enkripsi"

**Run**: `python test_2_decryption.py`

**Prerequisite**: Test 1 must be run first

---

### 3. test_3_capacity_limit.py
**Purpose**: Test that encryption fails when message exceeds capacity

Tests:
- Loads stego parameters from `dummy_steego_parameter.txt`
- Loads image `Jonathan_Pollard.png`
- Loads large dummy text from `paragraf_dummy.txt` (100 paragraphs)
- Attempts to encrypt and embed the large message
- Verifies that the system correctly rejects messages exceeding capacity
- Confirms capacity limit enforcement is working

**Run**: `python test_3_capacity_limit.py`

---

### 4. test_4_wrong_stego_key.py
**Purpose**: Test that decryption fails with wrong stego key

Tests:
- Loads stego parameters from `dummy_steego_parameter.txt`
- Loads stego image from Test 1 (`test1_stego_image.png`)
- Uses WRONG stego key `12345678` (instead of `30092026`)
- Attempts to extract and decrypt message
- Verifies that wrong key produces incorrect results or fails
- Confirms stego key security is working

**Run**: `python test_4_wrong_stego_key.py`

**Prerequisite**: Test 1 must be run first

---

### 5. test_5_image_analysis.py
**Purpose**: Test image analysis features

Tests:
- Loads cover image `Jonathan_Pollard.png`
- Loads stego image from Test 1 (`test1_stego_image.png`)
- Runs histogram comparison and saves result
- Runs histogram difference analysis and saves result
- Runs difference heatmap visualization and saves result
- Calculates statistical metrics (MSE, PSNR, MAE, Correlation)
- Performs Chi-Square steganalysis and saves result
- Extracts LSB plane and saves result

**Run**: `python test_5_image_analysis.py`

**Prerequisite**: Test 1 must be run first

**Output Files**:
- `test5_histogram_comparison.png`
- `test5_histogram_difference.png`
- `test5_difference_heatmap.png`
- `test5_chi_square_analysis.png`
- `test5_lsb_plane.png`

---

### 6. test_6_jpeg_compression.py
**Purpose**: Test JPEG compression effects on steganography

Tests:
- Loads stego parameters from `dummy_steego_parameter.txt`
- Loads stego image from Test 1 (`test1_stego_image.png`)
- Simulates JPEG compression at different quality levels (95, 85, 75, 65, 55)
- Tests message extraction from each compressed version
- Verifies Reed-Solomon error correction tolerance
- Tests with very low quality (30) to demonstrate failure point

**Run**: `python test_6_jpeg_compression.py`

**Prerequisite**: Test 1 must be run first

**Output Files**:
- `test6_jpeg_q95.jpg`
- `test6_jpeg_q85.jpg`
- `test6_jpeg_q75.jpg`
- `test6_jpeg_q65.jpg`
- `test6_jpeg_q55.jpg`
- `test6_jpeg_q30.jpg`

---

## Running All Tests

To run all tests in sequence:

```bash
python run_all_tests.py
```

This will execute tests 1-6 in order and provide a summary of results.

## Running Individual Tests

To run a specific test:

```bash
python test_1_full_encryption.py
python test_2_decryption.py
# etc.
```

## Test Dependencies

- Test 1 must be run before Tests 2, 4, 5, and 6 (they depend on `test1_stego_image.png`)
- All tests require:
  - `dummy_steego_parameter.txt` in the parent directory
  - `Jonathan_Pollard.png` in the parent directory
  - `paragraf_dummy.txt` in the parent directory (for Test 3)

## Cleaning Test Outputs

To clean up generated test files:

```bash
rm -f tests/test1_stego_image.png
rm -f tests/test5_*.png
rm -f tests/test6_*.jpg
```

## Expected Results

All tests should pass with the following expected outcomes:

1. **Test 1**: Successful encryption, stego image saved
2. **Test 2**: Successful decryption, message verified
3. **Test 3**: Capacity limit correctly enforced (encryption fails)
4. **Test 4**: Wrong stego key correctly rejected
5. **Test 5**: All analysis features work, visualizations saved
6. **Test 6**: JPEG compression effects demonstrated, error correction tested
