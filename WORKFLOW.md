# Alur Kerja Aplikasi Steganografi Citra

## Gambaran Umum Sistem

Aplikasi ini mengimplementasikan steganografi citra digital dengan enkripsi asimetris ElGamal berbasis Diffie-Hellman, proteksi integritas Reed-Solomon Error Correction, dan penyisipan bit LSB yang diacak menggunakan PRNG (Pseudo-Random Number Generator).

---

## 1. Inisialisasi Sistem

### 1.1 Konfigurasi Parameter Kriptografi
- **ElGamal-DH**: Generate safe prime modulus (p) dan generator (g)
- **Key Generation**: Generate pasangan kunci (private key x, public key y)
- **Caching**: Instance ElGamal dicache untuk efisiensi performa

### 1.2 Komponen Utama
- `ElGamalDH`: Implementasi enkripsi/dekripsi asimetris
- `LSBSteganography`: Implementasi steganografi dengan Reed-Solomon ECC
- `PRNG`: Pengacakan posisi piksel untuk penyisipan data

---

## 2. Alur Enkripsi & Penyisipan

### 2.1 Input Data
```
Gambar Cover (Citra Asli)
    ↓
Pesan Rahasia (Plaintext)
    ↓
Stego Key (Seed PRNG)
```

### 2.2 Proses Enkripsi ElGamal
```
Plaintext → Encode UTF-8 → Bytes
    ↓
ElGamal Encryption (Public Key y)
    ↓
Ciphertext (c1, c2) = [Encrypted Bytes]
```

### 2.3 Proteksi Reed-Solomon ECC
```
Encrypted Bytes
    ↓
Reed-Solomon Encoding (RS(255, 223))
    ↓
Parity Bytes Added (32 bytes/chunk)
    ↓
Protected Data Ready for Embedding
```

### 2.4 Penyisipan LSB dengan PRNG
```
Protected Data
    ↓
LSB Embedding with PRNG (Seed from Stego Key)
    ↓
Random Pixel Selection via SHA-256 Hash
    ↓
LSB Modification at Selected Positions
    ↓
Citra Stego (Hasil)
```

### 2.5 Kualitas Output
- **PSNR Calculation**: Mengukur kualitas citra stego vs cover
- **Visual Inspection**: Citra stego harus identik secara visual dengan cover

---

## 3. Alur Ekstraksi & Dekripsi

### 3.1 Input Data
```
Citra Stego (File PNG)
    ↓
Stego Key (Sama dengan saat enkripsi)
    ↓
Private Key (x) untuk Dekripsi
```

### 3.2 Ekstraksi LSB dengan PRNG
```
Citra Stego
    ↓
LSB Extraction with PRNG (Seed from Stego Key)
    ↓
Pixel Position Reconstruction via SHA-256
    ↓
Extracted Bits from LSB Plane
    ↓
Raw Data (with potential errors)
```

### 3.3 Koreksi Reed-Solomon
```
Raw Data
    ↓
Reed-Solomon Decoding (RS(255, 223))
    ↓
Error Detection & Correction (up to 16 errors/chunk)
    ↓
Corrected Encrypted Data
```

### 3.4 Dekripsi ElGamal
```
Corrected Encrypted Data
    ↓
ElGamal Decryption (Private Key x)
    ↓
Plaintext Bytes
    ↓
Decode UTF-8
    ↓
Original Message (Hasil)
```

---

## 4. Alur Analisis & Steganalisis

### 4.1 Perbandingan Visual
```
Citra Cover vs Citra Stego
    ↓
Side-by-side Display
    ↓
Visual Inspection (Human Eye)
```

### 4.2 Metrik Statistik
```
Calculate Metrics:
- MSE (Mean Squared Error)
- PSNR (Peak Signal-to-Noise Ratio)
- MAE (Mean Absolute Error)
- Correlation Coefficient
```

### 4.3 Analisis Histogram
```
Histogram Cover vs Histogram Stego
    ↓
Frequency Distribution Comparison
    ↓
Difference Histogram (Selisih Frekuensi)
```

### 4.4 Visual Steganalysis
```
LSB Plane Extraction (Bitplane 0)
    ↓
Enhanced LSB Visualization
    ↓
Difference Heatmap (Spatial Distribution)
    ↓
Chi-Square Statistical Test (Westfeld Attack)
```

---

## 5. Alur Uji Kerapuhan JPEG

### 5.1 Setup Pengujian
```
Gambar Cover
    ↓
Pesan Rahasia (Plaintext)
    ↓
Quality Factor JPEG (30-95)
```

### 5.2 Penyisipan & Kompresi
```
Embed Message to LSB (without ECC for testing)
    ↓
JPEG Compression (Lossy)
    ↓
DCT Quantization
    ↓
LSB Distortion
```

### 5.3 Ekstraksi & Verifikasi
```
Extract from JPEG Compressed Image
    ↓
Compare with Original Message
    ↓
Fragility Assessment:
  - Total Failure (Header corrupted)
  - Partial Corruption (Message damaged)
  - No Damage (Quality too high)
```

---

## 6. Arsitektur Teknis

### 6.1 Stack Teknologi
- **Frontend**: Streamlit (Python Web Framework)
- **Image Processing**: NumPy, PIL (Pillow)
- **Visualization**: Matplotlib
- **Cryptography**: Custom ElGamal-DH Implementation
- **Error Correction**: Reed-Solomon (reedsolo library)
- **Hashing**: hashlib (SHA-256)

### 6.2 Komponen Utama
```
app.py (Main Application)
├── ElGamalDH (elgamal.py)
├── LSBSteganography (steganography.py)
├── Analysis Functions (analysis.py)
└── Reed-Solomon (reedsolo library)
```

### 6.3 Session State Management
- `elgamal`: Instance ElGamal (cached)
- `private_key`, `public_key`: Pasangan kunci
- `stego_array`, `cover_array`: Citra untuk analisis
- `stego_key`: Kunci stego untuk ekstraksi

---

## 7. Fitur Utama

### 7.1 Tab Enkripsi
- Upload gambar cover
- Input pesan rahasia
- Input stego key (seed PRNG)
- Real-time capacity gauge
- Enkripsi & penyisipan otomatis
- Download citra stego (PNG lossless)
- Inspeksi matematis parameter kriptografi

### 7.2 Tab Dekripsi
- Upload citra stego
- Input stego key
- Ekstraksi & dekripsi otomatis
- Verifikasi integritas Reed-Solomon
- Inspeksi status rekonstruksi data

### 7.3 Tab Analisis
- Perbandingan visual cover vs stego
- Metrik statistik (MSE, PSNR, MAE, Korelasi)
- Histogram comparison & difference
- Visualisasi LSB plane
- Difference heatmap dengan amplifikasi
- Uji Chi-Square (Westfeld Attack)

### 7.4 Tab Uji JPEG
- Uji kerapuhan kompresi JPEG
- Variasi quality factor
- Perbandingan stego vs JPEG
- Metrik distorsi akibat kompresi
- Verifikasi fragility LSB method

---

## 8. Keamanan & Perlindungan

### 8.1 Enkripsi Asimetris
- ElGamal berbasis Diffie-Hellman
- Safe prime modulus untuk keamanan
- Private key tidak pernah diekspos

### 8.2 Error Correction
- Reed-Solomon RS(255, 223)
- 32 parity bytes per chunk
- Koreksi hingga 16 error per chunk
- Proteksi integritas data

### 8.3 Pengacakan Posisi
- PRNG dengan seed dari stego key
- SHA-256 hash untuk deterministik
- Posisi piksel tidak berurutan
- Meningkatkan keamanan steganografi

### 8.4 Fragility by Design
- LSB spatial rentan terhadap kompresi JPEG
- Kerapuhan mencegah manipulasi unauthorized
- Reed-Solomon membantu toleransi error minor
- PNG lossless required for transfer

---

## 9. Flowchart Diagram

```
┌─────────────────────────────────────────────────────────┐
│              INISIALISASI SISTEM                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ ElGamal-DH   │  │ Key Gen      │  │ PRNG Setup   │ │
│  │ (p, g)       │  │ (x, y)       │  │ (Seed)       │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              ALUR ENKRIPSI & PENYISIPAN                  │
│                                                          │
│  Input: Cover Image + Plaintext + Stego Key             │
│         │                    │           │              │
│         ▼                    ▼           ▼              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Image Upload │  │ Message Input│  │ Key Input    │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│         │                    │           │              │
│         └────────────────────┼───────────┘              │
│                              ▼                          │
│                    ┌──────────────┐                     │
│                    │ ElGamal      │                     │
│                    │ Encryption   │                     │
│                    └──────────────┘                     │
│                              │                          │
│                              ▼                          │
│                    ┌──────────────┐                     │
│                    │ Reed-Solomon │                     │
│                    │ ECC Encoding │                     │
│                    └──────────────┘                     │
│                              │                          │
│                              ▼                          │
│                    ┌──────────────┐                     │
│                    │ LSB Embed    │                     │
│                    │ with PRNG    │                     │
│                    └──────────────┘                     │
│                              │                          │
│                              ▼                          │
│                    ┌──────────────┐                     │
│                    │ Stego Image  │                     │
│                    │ Output       │                     │
│                    └──────────────┘                     │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              ALUR EKSTRAKSI & DEKRIPSI                   │
│                                                          │
│  Input: Stego Image + Stego Key + Private Key            │
│         │                    │           │              │
│         ▼                    ▼           ▼              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Stego Upload │  │ Key Verify   │  │ Private Key  │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│         │                    │           │              │
│         └────────────────────┼───────────┘              │
│                              ▼                          │
│                    ┌──────────────┐                     │
│                    │ LSB Extract  │                     │
│                    │ with PRNG    │                     │
│                    └──────────────┘                     │
│                              │                          │
│                              ▼                          │
│                    ┌──────────────┐                     │
│                    │ Reed-Solomon │                     │
│                    │ Error Corr.  │                     │
│                    └──────────────┘                     │
│                              │                          │
│                              ▼                          │
│                    ┌──────────────┐                     │
│                    │ ElGamal      │                     │
│                    │ Decryption   │                     │
│                    └──────────────┘                     │
│                              │                          │
│                              ▼                          │
│                    ┌──────────────┐                     │
│                    │ Original     │                     │
│                    │ Message      │                     │
│                    └──────────────┘                     │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              ANALISIS & STEGANALISIS                     │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Visual       │  │ Statistical  │  │ Histogram    │ │
│  │ Comparison   │  │ Metrics      │  │ Analysis     │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│         │                    │           │              │
│         └────────────────────┼───────────┘              │
│                              ▼                          │
│                    ┌──────────────┐                     │
│                    │ LSB Plane    │                     │
│                    │ Visualization│                     │
│                    └──────────────┘                     │
│                              │                          │
│                              ▼                          │
│                    ┌──────────────┐                     │
│                    │ Difference   │                     │
│                    │ Heatmap      │                     │
│                    └──────────────┘                     │
│                              │                          │
│                              ▼                          │
│                    ┌──────────────┐                     │
│                    │ Chi-Square   │                     │
│                    │ Test         │                     │
│                    └──────────────┘                     │
└─────────────────────────────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────┐
│              UJI KERAPUHAN JPEG                           │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ Cover Image  │  │ Test Message │  │ JPEG Quality │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│         │                    │           │              │
│         └────────────────────┼───────────┘              │
│                              ▼                          │
│                    ┌──────────────┐                     │
│                    │ LSB Embed    │                     │
│                    │ (no ECC)     │                     │
│                    └──────────────┘                     │
│                              │                          │
│                              ▼                          │
│                    ┌──────────────┐                     │
│                    │ JPEG         │                     │
│                    │ Compression  │                     │
│                    └──────────────┘                     │
│                              │                          │
│                              ▼                          │
│                    ┌──────────────┐                     │
│                    │ LSB Extract  │                     │
│                    │ from JPEG    │                     │
│                    └──────────────┘                     │
│                              │                          │
│                              ▼                          │
│                    ┌──────────────┐                     │
│                    │ Fragility    │                     │
│                    │ Assessment   │                     │
│                    └──────────────┘                     │
└─────────────────────────────────────────────────────────┘
```

---

## 10. Konfigurasi & Parameter

### 10.1 Parameter ElGamal
- **Safe Prime (p)**: Bilangan prima aman (safe prime)
- **Generator (g)**: Generator grup siklik
- **Private Key (x)**: Kunci privat acak
- **Public Key (y)**: y = g^x mod p

### 10.2 Parameter Reed-Solomon
- **Scheme**: RS(255, 223)
- **Data Bytes**: 223 bytes per chunk
- **Parity Bytes**: 32 bytes per chunk
- **Error Correction**: Up to 16 errors per chunk

### 10.3 Parameter Steganografi
- **Bit Depth**: 1 bit per channel (LSB)
- **Channels**: RGB (3 channels)
- **PRNG Seed**: SHA-256 hash dari stego key
- **Embedding**: Random position selection

---

## 11. Catatan Penggunaan

### 11.1 Format File
- **Cover Image**: PNG, JPG, JPEG, BMP
- **Stego Output**: PNG (lossless recommended)
- **Transfer**: Use PNG lossless for integrity

### 11.2 Kunci & Keamanan
- **Stego Key**: Simpan dengan aman, diperlukan untuk ekstraksi
- **Private Key**: Jangan bagikan, diperlukan untuk dekripsi
- **Public Key**: Dapat dibagikan untuk enkripsi

### 11.3 Batasan
- **Kapasitas**: Tergantung ukuran gambar
- **Kompresi**: JPEG akan merusak data LSB
- **Resizing**: Perubahan ukuran akan merusak data
- **Editing**: Modifikasi piksel akan merusak data

---

## 12. Troubleshooting

### 12.1 Ekstraksi Gagal
- Verifikasi stego key yang digunakan
- Pastikan menggunakan file PNG lossless asli
- Cek apakah gambar pernah dikompresi/edited

### 12.2 Reed-Solomon Error
- Gambar mungkin mengalami distorsi
- Coba gunakan file asli hasil download
- Verifikasi hash file jika tersedia

### 12.3 Kapasitas Terlampaui
- Gunakan gambar dengan resolusi lebih tinggi
- Perpendek pesan rahasia
- Pertimbangkan kompresi pesan sebelum enkripsi

---

*Dokumentasi ini dibuat untuk memahami alur kerja aplikasi Steganografi Citra dengan Enkripsi ElGamal berbasis Diffie-Hellman sebagai tugas Mata Kuliah Keamanan Informasi.*
