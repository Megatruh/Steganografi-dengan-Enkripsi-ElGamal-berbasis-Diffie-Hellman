# Software Requirements Specification (SRS)
# Steganografi dengan Enkripsi ElGamal berbasis Diffie-Hellman

---

## 1. Pendahuluan

### 1.1 Tujuan Dokumen
Dokumen ini mendefinisikan persyaratan fungsional dan non-fungsional untuk aplikasi Steganografi dengan Enkripsi ElGamal berbasis Diffie-Hellman. Dokumen ini berfungsi sebagai panduan untuk pengembangan, pengujian, dan implementasi sistem.

### 1.2 Ruang Lingkup Proyek
Aplikasi ini adalah sistem web berbasis Streamlit yang memungkinkan pengguna untuk:
- Mengenkripsi pesan menggunakan algoritma ElGamal berbasis Diffie-Hellman
- Menyembunyikan pesan terenkripsi dalam gambar menggunakan metode LSB (Least Significant Bit)
- Mengekstrak dan mendekripsi pesan dari gambar stego
- Menganalisis perbedaan antara gambar cover dan stego menggunakan histogram dan metrik statistik
- Melakukan steganalisis visual dengan menampilkan bidang LSB
- Menggunakan Reed-Solomon Error Correction Code (ECC) untuk ketahanan terhadap error
- Memverifikasi integritas file stego menggunakan SHA-256 hash

### 1.3 Definisi, Akronim, dan Singkatan
- **LSB**: Least Significant Bit - bit paling signifikan dari nilai piksel
- **PRNG**: Pseudo-Random Number Generator - generator angka acak semu
- **ElGamal**: Algoritma enkripsi asimetris berbasis Diffie-Hellman
- **Cover Image**: Gambar asli sebelum steganografi
- **Stego Image**: Gambar setelah steganografi (mengandung pesan tersembunyi)
- **PSNR**: Peak Signal-to-Noise Ratio - rasio sinyal maksimum terhadap noise
- **MSE**: Mean Squared Error - rata-rata kuadrat error
- **MAE**: Mean Absolute Error - rata-rata error absolut
- **ECC**: Error Correction Code - kode koreksi error
- **Reed-Solomon**: Algoritma error correction code untuk koreksi burst error
- **nsym**: Number of parity symbols - jumlah simbol parity dalam Reed-Solomon

### 1.4 Referensi
- RFC 4880: OpenPGP Message Format
- IEEE Standard for Steganography
- Matplotlib Documentation
- Streamlit Documentation
- Pillow Documentation
- Reed-Solomon Documentation

### 1.5 Tinjauan Dokumen
Bagian 2 menjelaskan deskripsi umum sistem. Bagian 3 mendefinisikan persyaratan fungsional. Bagian 4 mendefinisikan persyaratan non-fungsional. Bagian 5 menjelaskan persyaratan antarmuka. Bagian 6 berisi analisis dan model sistem.

---

## 2. Deskripsi Umum

### 2.1 Perspektif Produk
Aplikasi ini adalah sistem web interaktif yang berjalan sebagai aplikasi Streamlit. Sistem ini beroperasi sebagai aplikasi lokal yang dapat diakses melalui browser web. Sistem tidak memerlukan backend server terpisah karena semua pemrosesan dilakukan di sisi klien.

### 2.2 Fungsi Produk
Sistem menyediakan tiga fungsi utama:
1. **Enkripsi dan Embedding**: Mengenkripsi pesan dan menyembunyikannya dalam gambar
2. **Ekstraksi dan Dekripsi**: Mengekstrak pesan dari gambar dan mendekripsinya
3. **Analisis**: Menganalisis perbedaan antara gambar cover dan stego

### 2.3 Karakteristik Pengguna
**Pengguna Utama**:
- Mahasiswa atau peneliti di bidang keamanan informasi
- Pengguna yang memiliki pengetahuan dasar tentang kriptografi dan steganografi
- Pengguna yang membutuhkan alat untuk demonstrasi atau penelitian

**Kemampuan Pengguna**:
- Memahami konsep enkripsi dan steganografi
- Dapat menggunakan antarmuka web dasar
- Memahami pentingnya kunci dalam sistem kriptografi

### 2.4 Kendala
- **Keamanan**: Private key disimpan di session state dan tidak dipersistenkan
- **Kapasitas**: Kapasitas steganografi terbatas oleh ukuran gambar dan overhead Reed-Solomon
- **Format Gambar**: Mendukung format PNG, JPG, JPEG, dan BMP
- **Platform**: Berjalan pada sistem operasi yang mendukung Python 3.7+
- **Bahasa**: Antarmuka dalam Bahasa Indonesia

### 2.5 Asumsi dan Ketergantungan
- Pengguna memiliki Python 3.7 atau lebih tinggi terinstal
- Koneksi internet tidak diperlukan untuk operasi dasar
- Streamlit dan semua dependencies terinstal dengan benar
- Sistem memiliki memori yang cukup untuk memproses gambar

---

## 3. Persyaratan Fungsional

### 3.1 Manajemen Kunci ElGamal

#### FR-1.1 Generate Key Pair
**Deskripsi**: Sistem harus dapat menghasilkan pasangan kunci ElGamal (private dan public key) secara otomatis.

**Input**: Tidak ada (dipicu oleh tombol "Generate New Keys")

**Output**: 
- Private key (bilangan bulat)
- Public key (bilangan bulat)
- Parameter ElGamal (prime p dan generator g)

**Proses**:
1. Inisialisasi ElGamal dengan safe prime 1024-bit
2. Generate private key secara acak dalam rentang [2, p-2]
3. Hitung public key sebagai g^private_key mod p
4. Tampilkan kunci di sidebar

**Prioritas**: Tinggi

#### FR-1.2 Display ElGamal Parameters
**Deskripsi**: Sistem harus menampilkan parameter ElGamal (prime p dan generator g) di sidebar.

**Input**: Tidak ada

**Output**: Tampilan parameter di sidebar

**Prioritas**: Sedang

### 3.2 Enkripsi dan Steganografi

#### FR-2.1 Upload Cover Image
**Deskripsi**: Pengguna dapat mengupload gambar cover yang akan digunakan untuk menyembunyikan pesan.

**Input**: File gambar (PNG, JPG, JPEG, BMP)

**Output**: 
- Tampilan gambar cover
- Informasi kapasitas maksimum (dalam bytes)

**Validasi**:
- File harus berupa gambar yang valid
- Mendukung format PNG, JPG, JPEG, BMP
- Gambar dikonversi ke RGB jika grayscale atau RGBA

**Prioritas**: Tinggi

#### FR-2.2 Input Message
**Deskripsi**: Pengguna dapat memasukkan pesan teks yang ingin disembunyikan.

**Input**: String teks

**Output**: Pesan tersimpan di memori

**Validasi**:
- Pesan tidak boleh kosong
- Pesan harus dalam format UTF-8

**Prioritas**: Tinggi

#### FR-2.3 Input Stego Key
**Deskripsi**: Pengguna dapat memasukkan stego key (seed untuk PRNG) yang digunakan untuk mengacak posisi LSB.

**Input**: Bilangan bulat (default: 12345)

**Output**: Stego key tersimpan di memori

**Validasi**:
- Stego key harus berupa bilangan bulat yang valid

**Prioritas**: Tinggi

#### FR-2.4 Encrypt Message
**Deskripsi**: Sistem mengenkripsi pesan menggunakan algoritma ElGamal dengan public key.

**Input**: 
- Pesan (bytes)
- Public key

**Output**: Pesan terenkripsi (bytes)

**Proses**:
1. Konversi pesan ke bytes
2. Tambahkan length prefix (4 bytes)
3. Split data menjadi blok
4. Enkripsi setiap blok dengan ElGamal
5. Gabungkan blok terenkripsi

**Prioritas**: Tinggi

#### FR-2.5 Apply Reed-Solomon ECC
**Deskripsi**: Sistem menerapkan Reed-Solomon Error Correction Code pada pesan terenkripsi untuk ketahanan terhadap error.

**Input**: 
- Pesan terenkripsi (bytes)
- nsym (number of parity symbols, default: 20)

**Output**: Pesan terenkripsi dengan Reed-Solomon parity bytes

**Proses**:
1. Inisialisasi Reed-Solomon codec dengan nsym parity symbols
2. Encode pesan terenkripsi untuk menambahkan parity bytes
3. Return pesan yang sudah di-encode

**Prioritas**: Tinggi

#### FR-2.6 Check Capacity
**Deskripsi**: Sistem memeriksa apakah pesan terenkripsi (dengan Reed-Solomon overhead) muat dalam kapasitas gambar.

**Input**: 
- Ukuran pesan terenkripsi (dengan Reed-Solomon)
- Kapasitas gambar

**Output**: True jika muat, False jika tidak

**Validasi**:
- Kapasitas harus memperhitungkan overhead Reed-Solomon (nsym bytes)
- Kapasitas harus memperhitungkan 4-byte length header

**Prioritas**: Tinggi

#### FR-2.7 Embed Message
**Deskripsi**: Sistem menyembunyikan pesan terenkripsi (dengan Reed-Solomon) dalam gambar menggunakan LSB yang diacak.

**Input**: 
- Cover image (numpy array)
- Pesan terenkripsi dengan Reed-Solomon (bytes)
- Stego key (seed untuk PRNG)

**Output**: Stego image (numpy array)

**Proses**:
1. Tambahkan message length header (4 bytes)
2. Generate urutan pixel yang diacak menggunakan PRNG dengan stego key
3. Embed bit ke LSB sesuai urutan yang diacak
4. Return stego image

**Prioritas**: Tinggi

#### FR-2.8 Calculate PSNR
**Deskripsi**: Sistem menghitung PSNR antara cover image dan stego image.

**Input**: 
- Cover image
- Stego image

**Output**: Nilai PSNR (dB)

**Prioritas**: Sedang

#### FR-2.9 Download Stego Image
**Deskripsi**: Pengguna dapat mengunduh stego image dalam format PNG.

**Input**: Stego image

**Output**: File PNG

**Prioritas**: Tinggi

### 3.3 Ekstraksi dan Dekripsi

#### FR-3.1 Upload Stego Image
**Deskripsi**: Pengguna dapat mengupload gambar stego yang akan diekstrak.

**Input**: File gambar (PNG, JPG, JPEG, BMP)

**Output**: 
- Tampilan gambar stego
- SHA-256 hash untuk verifikasi integritas

**Validasi**:
- File harus berupa gambar yang valid
- Mendukung format PNG, JPG, JPEG, BMP
- Gambar dikonversi ke RGB jika grayscale atau RGBA

**Prioritas**: Tinggi

#### FR-3.2 Input Stego Key
**Deskripsi**: Pengguna dapat memasukkan stego key yang sama dengan saat embedding.

**Input**: Bilangan bulat (default: 12345)

**Output**: Stego key tersimpan di memori

**Validasi**:
- Stego key harus berupa bilangan bulat yang valid

**Prioritas**: Tinggi

#### FR-3.3 Extract Message
**Deskripsi**: Sistem mengekstrak pesan terenkripsi dari stego image menggunakan LSB yang diacak.

**Input**: 
- Stego image (numpy array)
- Stego key (seed untuk PRNG)

**Output**: Pesan terenkripsi dengan Reed-Solomon (bytes)

**Proses**:
1. Generate urutan pixel yang diacak menggunakan PRNG dengan stego key
2. Extract bit dari LSB sesuai urutan yang diacak
3. Convert bit ke bytes
4. Extract message length dari 4 byte pertama
5. Extract pesan terenkripsi dengan Reed-Solomon
6. Return pesan terenkripsi

**Prioritas**: Tinggi

#### FR-3.4 Apply Reed-Solomon Decoding
**Deskripsi**: Sistem menerapkan Reed-Solomon decoding untuk koreksi error pada pesan terenkripsi.

**Input**: 
- Pesan terenkripsi dengan Reed-Solomon (bytes)
- nsym (number of parity symbols, default: 20)
- auto_detect_nsym (boolean, default: True)

**Output**: Pesan terenkripsi yang sudah dikoreksi (bytes)

**Proses**:
1. Decode menggunakan Reed-Solomon codec dengan nsym yang ditentukan
2. Jika gagal dan auto_detect_nsym=True, coba dengan nsym alternatif (10, 15, 25, 30)
3. Return pesan yang sudah dikoreksi

**Error Handling**:
- Jika Reed-Solomon decoding gagal, tampilkan error message yang jelas
- Jika auto_detect_nsym gagal untuk semua nsym, tampilkan error dengan solusi

**Prioritas**: Tinggi

#### FR-3.5 Decrypt Message
**Deskripsi**: Sistem mendekripsi pesan terenkripsi menggunakan private key ElGamal.

**Input**: 
- Pesan terenkripsi (bytes)
- Private key

**Output**: Pesan asli (bytes)

**Proses**:
1. Split data menjadi blok
2. Dekripsi setiap blok dengan ElGamal
3. Gabungkan blok terdekripsi
4. Extract length dari 4 byte pertama
5. Extract pesan asli

**Prioritas**: Tinggi

#### FR-3.6 Display Decrypted Message
**Deskripsi**: Sistem menampilkan pesan asli yang sudah didekripsi.

**Input**: Pesan asli (bytes)

**Output**: Tampilan pesan asli sebagai string

**Prioritas**: Tinggi

### 3.4 Analisis

#### FR-4.1 Display Cover and Stego Image
**Deskripsi**: Sistem menampilkan cover image dan stego image secara berdampingan.

**Input**: Cover image dan stego image dari session state

**Output**: Tampilan kedua gambar

**Prioritas**: Sedang

#### FR-4.2 Plot Histogram Comparison
**Deskripsi**: Sistem menampilkan perbandingan histogram antara cover dan stego image.

**Input**: Cover image dan stego image

**Output**: Grafik histogram comparison

**Proses**:
1. Hitung histogram untuk setiap channel
2. Plot histogram cover dan stego secara berdampingan
3. Handle grayscale dan RGB image

**Prioritas**: Sedang

#### FR-4.3 Plot Histogram Difference
**Deskripsi**: Sistem menampilkan perbedaan histogram antara cover dan stego image.

**Input**: Cover image dan stego image

**Output**: Grafik histogram difference

**Prioritas**: Sedang

#### FR-4.4 Calculate Statistical Metrics
**Deskripsi**: Sistem menghitung metrik statistik antara cover dan stego image.

**Input**: Cover image dan stego image

**Output**: 
- MSE (Mean Squared Error)
- PSNR (Peak Signal-to-Noise Ratio)
- MAE (Mean Absolute Error)
- Correlation

**Prioritas**: Sedang

#### FR-4.5 Display LSB Plane
**Deskripsi**: Sistem menampilkan bidang LSB untuk steganalisis visual.

**Input**: Stego image

**Output**: Gambar LSB plane (enhanced)

**Proses**:
1. Extract LSB dari setiap piksel
2. Convert ke grayscale
3. Enhance dengan mengalikan dengan 255
4. Return gambar LSB

**Prioritas**: Sedang

---

## 4. Persyaratan Non-Fungsional

### 4.1 Persyaratan Performa

#### NFR-4.1.1 Encryption Time
**Deskripsi**: Waktu enkripsi pesan harus ≤ 1 detik untuk pesan pendek (< 100 bytes).

**Implementasi**: Optimasi ElGamal dengan pre-generated safe prime

#### NFR-4.1.2 Embedding Time
**Deskripsi**: Waktu embedding harus ≤ 2 detik untuk gambar 512x512.

**Implementasi**: Optimasi PRNG dan bit manipulation dengan numpy

#### NFR-4.1.3 Extraction Time
**Deskripsi**: Waktu ekstraksi harus ≤ 2 detik untuk gambar 512x512.

**Implementasi**: Optimasi PRNG dan bit manipulation dengan numpy

#### NFR-4.1.4 Reed-Solomon Encoding/Decoding Time
**Deskripsi**: Waktu encoding/decoding Reed-Solomon harus ≤ 0.5 detik untuk pesan < 1KB.

**Implementasi**: Menggunakan library reedsolo yang teroptimasi

### 4.2 Persyaratan Keamanan

#### NFR-4.2.1 Private Key Security
**Deskripsi**: Private key tidak boleh dipersistenkan ke disk.

**Implementasi**: Private key disimpan di session state Streamlit

#### NFR-4.2.2 Stego Key Required
**Deskripsi**: Stego key diperlukan untuk mengekstrak pesan.

**Implementasi**: Validasi stego key sebelum ekstraksi

#### NFR-4.2.3 Safe Prime Usage
**Deskripsi**: ElGamal harus menggunakan safe prime dan generator yang aman.

**Implementasi**: Pre-generated 1024-bit safe prime

#### NFR-4.2.4 LSB Randomization
**Deskripsi**: Posisi LSB harus diacak untuk meningkatkan keamanan.

**Implementasi**: PRNG dengan seed dari stego key

#### NFR-4.2.5 Error Correction Tolerance
**Deskripsi**: Reed-Solomon ECC harus memberikan toleransi error yang cukup.

**Implementasi**: Menggunakan nsym=20 parity symbols untuk toleransi error burst

### 4.3 Persyaratan Keandalan

#### NFR-4.3.1 Error Handling
**Deskripsi**: Sistem harus menangani error dengan pesan yang jelas.

**Implementasi**: Try-catch blocks dengan error messages yang informatif

#### NFR-4.3.2 Data Integrity
**Deskripsi**: Pesan yang diekstrak dan didekripsi harus sama dengan pesan asli.

**Implementasi**: Validasi message length dan Reed-Solomon decoding

#### NFR-4.3.3 Backward Compatibility
**Deskripsi**: Sistem harus mendukung stego image lama dengan nsym=10.

**Implementasi**: Auto-detection nsym dengan fallback ke nsym alternatif

#### NFR-4.3.4 File Integrity Verification
**Deskripsi**: Sistem harus menyediakan mekanisme verifikasi integritas file stego.

**Implementasi**: SHA-256 hash untuk file stego

### 4.4 Persyaratan Usability

#### NFR-4.4.1 User Interface
**Deskripsi**: Antarmuka harus intuitif dan mudah digunakan.

**Implementasi**: Streamlit dengan tab-based navigation

#### NFR-4.4.2 Language
**Deskripsi**: Antarmuka harus dalam Bahasa Indonesia.

**Implementasi**: Semua label dan messages dalam Bahasa Indonesia

#### NFR-4.4.3 Responsiveness
**Deskripsi**: Antarmuka harus responsif untuk berbagai ukuran layar.

**Implementasi**: Streamlit responsive layout

#### NFR-4.4.4 Error Messages
**Deskripsi**: Error messages harus jelas dan memberikan solusi.

**Implementasi**: Error messages dengan tips troubleshooting

### 4.5 Persyaratan Kompatibilitas

#### NFR-4.5.1 Image Formats
**Deskripsi**: Sistem harus mendukung format PNG, JPG, JPEG, dan BMP.

**Implementasi**: Pillow library dengan format support

#### NFR-4.5.2 Image Types
**Deskripsi**: Sistem harus mendukung gambar grayscale, RGB, dan RGBA.

**Implementasi**: Konversi otomatis ke RGB

#### NFR-4.5.3 Python Version
**Deskripsi**: Sistem harus berjalan pada Python 3.7+.

**Implementasi**: Dependencies yang kompatibel

#### NFR-4.5.4 Reed-Solomon Library
**Deskripsi**: Sistem harus menggunakan library reedsolo yang kompatibel.

**Implementasi**: reedsolo>=1.7.0

### 4.6 Persyaratan Maintainability

#### NFR-4.6.1 Code Structure
**Deskripsi**: Kode harus terstruktur dengan modularitas yang baik.

**Implementasi**: Pemisahan modul (elgamal.py, steganography.py, analysis.py, app.py)

#### NFR-4.6.2 Documentation
**Deskripsi**: Kode harus memiliki docstring yang jelas.

**Implementasi**: Docstring untuk setiap fungsi dan class

#### NFR-4.6.3 Caching
**Deskripsi**: Sistem harus menggunakan caching untuk performa.

**Implementasi**: Streamlit @st.cache_resource untuk ElGamal instance

#### NFR-4.6.4 Clean Restart Script
**Deskripsi**: Sistem harus menyediakan script untuk clean restart.

**Implementasi**: clean_restart.sh untuk menghapus cache

---

## 5. Persyaratan Antarmuka

### 5.1 Antarmuka Pengguna

#### UI-5.1.1 Main Header
**Deskripsi**: Header utama dengan judul aplikasi dan ikon.

**Lokasi**: Bagian atas halaman

**Konten**: "🔐 Steganografi dengan Enkripsi ElGamal berbasis Diffie-Hellman"

#### UI-5.1.2 Sidebar - Key Management
**Deskripsi**: Sidebar untuk manajemen kunci ElGamal.

**Lokasi**: Sidebar kiri

**Konten**:
- Judul: "🔑 Manajemen Kunci"
- Subheader: "ElGamal Parameters"
- Prime (p)
- Generator (g)
- Subheader: "Key Pair"
- Private Key
- Public Key
- Tombol: "Generate New Keys"

#### UI-5.1.3 Tab Navigation
**Deskripsi**: Navigasi tab untuk tiga fungsi utama.

**Lokasi**: Di bawah header

**Tab**:
- "🔒 Enkripsi"
- "🔓 Dekripsi"
- "📊 Analisis"

#### UI-5.1.4 Tab 1 - Enkripsi
**Deskripsi**: Tab untuk enkripsi dan steganografi.

**Komponen**:
- Section header: "Enkripsi"
- Deskripsi: "Upload gambar, masukkan pesan, dan stego key untuk melakukan enkripsi dan steganografi."
- File uploader: "Upload Gambar Cover"
- Tampilan cover image
- Informasi kapasitas
- Text area: "Input Pesan"
- Text input: "Input Stego Key" (default: 12345)
- Tombol: "🔒 Enkrip" (primary)
- Tampilan stego image
- Tombol download: "⬇️ Download Stego Image"

#### UI-5.1.5 Tab 2 - Dekripsi
**Deskripsi**: Tab untuk ekstraksi dan dekripsi.

**Komponen**:
- Section header: "Dekripsi"
- Deskripsi: "Upload gambar stego dan masukkan stego key untuk mengekstrak dan mendekripsi pesan."
- File uploader: "Upload Gambar Stego"
- Tampilan stego image
- SHA-256 hash untuk verifikasi integritas
- Text input: "Input Stego Key" (default: 12345)
- Tombol: "🔓 Dekrip" (primary)
- Subheader: "Pesan yang Diekstrak dan Didekripsi:"
- Text area untuk output pesan

#### UI-5.1.6 Tab 3 - Analisis
**Deskripsi**: Tab untuk analisis steganografi.

**Komponen**:
- Section header: "Analisis Steganografi"
- Deskripsi: "Analisis histogram, metrik statistik, dan visual steganalysis LSB plane."
- Tampilan cover dan stego image (berdampingan)
- Subheader: "Perbandingan Histogram"
- Grafik histogram comparison
- Subheader: "Perbedaan Histogram"
- Grafik histogram difference
- Subheader: "Metrik Statistik"
- Metrics: MSE, PSNR, MAE, Correlation
- Subheader: "Visual Steganalysis - LSB Plane"
- Tampilan LSB plane image

#### UI-5.1.7 Footer
**Deskripsi**: Footer dengan informasi aplikasi.

**Lokasi**: Bagian bawah halaman

**Konten**:
- "Steganografi dengan Enkripsi ElGamal berbasis Diffie-Hellman"
- "Dibuat untuk Tugas Keamanan Informasi"

### 5.2 Antarmuka Eksternal

#### EI-5.2.1 File System
**Deskripsi**: Akses ke file system untuk upload dan download gambar.

**Format**: File gambar (PNG, JPG, JPEG, BMP)

#### EI-5.2.2 Browser
**Deskripsi**: Aplikasi berjalan di browser web.

**Platform**: Browser modern (Chrome, Firefox, Safari, Edge)

---

## 6. Analisis dan Model Sistem

### 6.1 Use Case Diagram

#### UC-6.1.1 Enkripsi dan Embedding
**Aktor**: Pengguna

**Deskripsi**: Pengguna mengenkripsi pesan dan menyembunyikannya dalam gambar.

**Prekondisi**: 
- Aplikasi berjalan
- ElGamal key pair tersedia

**Alur Utama**:
1. Pengguna mengupload cover image
2. Sistem menampilkan cover image dan kapasitas
3. Pengguna memasukkan pesan
4. Pengguna memasukkan stego key
5. Pengguna menekan tombol "Enkrip"
6. Sistem mengenkripsi pesan dengan ElGamal
7. Sistem menerapkan Reed-Solomon ECC pada pesan terenkripsi
8. Sistem mengecek kapasitas
9. Sistem menyembunyikan pesan dengan LSB yang diacak
10. Sistem menghitung PSNR
11. Sistem menampilkan stego image
12. Pengguna mengunduh stego image

**Postkondisi**: Stego image tersedia untuk diunduh

#### UC-6.1.2 Ekstraksi dan Dekripsi
**Aktor**: Pengguna

**Deskripsi**: Pengguna mengekstrak pesan dari gambar stego dan mendekripsinya.

**Prekondisi**: 
- Aplikasi berjalan
- ElGamal key pair tersedia
- Stego image tersedia

**Alur Utama**:
1. Pengguna mengupload stego image
2. Sistem menampilkan stego image dan SHA-256 hash
3. Pengguna memasukkan stego key
4. Pengguna menekan tombol "Dekrip"
5. Sistem mengekstrak pesan terenkripsi dengan LSB yang diacak
6. Sistem menerapkan Reed-Solomon decoding untuk koreksi error
7. Sistem mendekripsi pesan dengan ElGamal
8. Sistem menampilkan pesan asli

**Postkondisi**: Pesan asli ditampilkan

**Alur Alternatif**:
- Jika Reed-Solomon decoding gagal dengan nsym=20, sistem mencoba nsym alternatif (10, 15, 25, 30)
- Jika semua nsym gagal, sistem menampilkan error message dengan solusi

#### UC-6.1.3 Analisis
**Aktor**: Pengguna

**Deskripsi**: Pengguna menganalisis perbedaan antara cover dan stego image.

**Prekondisi**: 
- Aplikasi berjalan
- Cover dan stego image tersedia di session state

**Alur Utama**:
1. Pengguna membuka tab "Analisis"
2. Sistem menampilkan cover dan stego image
3. Sistem menampilkan histogram comparison
4. Sistem menampilkan histogram difference
5. Sistem menampilkan metrik statistik
6. Sistem menampilkan LSB plane

**Postkondisi**: Analisis ditampilkan

#### UC-6.1.4 Generate New Keys
**Aktor**: Pengguna

**Deskripsi**: Pengguna menghasilkan pasangan kunci baru.

**Prekondisi**: Aplikasi berjalan

**Alur Utama**:
1. Pengguna menekan tombol "Generate New Keys"
2. Sistem menghapus cache
3. Sistem menginisialisasi ElGamal baru
4. Sistem menghasilkan key pair baru
5. Sistem menampilkan kunci baru

**Postkondisi**: Key pair baru tersedia

### 6.2 Flowchart

#### FC-6.2.1 Alur Enkripsi dan Embedding
```
Mulai
  ↓
Upload Cover Image
  ↓
Input Pesan
  ↓
Input Stego Key
  ↓
Encrypt Pesan dengan ElGamal
  ↓
Apply Reed-Solomon ECC (nsym=20)
  ↓
Check Kapasitas
  ↓ (cukup)
Embed dengan LSB + PRNG
  ↓
Hitung PSNR
  ↓
Tampilkan Stego Image
  ↓
Download Stego Image
  ↓
Selesai
```

#### FC-6.2.2 Alur Ekstraksi dan Dekripsi
```
Mulai
  ↓
Upload Stego Image
  ↓
Display SHA-256 Hash
  ↓
Input Stego Key
  ↓
Extract dengan LSB + PRNG
  ↓
Validate Message Length
  ↓ (valid)
Apply Reed-Solomon Decoding (nsym=20)
  ↓ (gagal?)
Try Auto-detect nsym (10, 15, 25, 30)
  ↓ (berhasil/gagal)
Decrypt dengan ElGamal
  ↓
Tampilkan Pesan Asli
  ↓
Selesai
```

### 6.3 Sequence Diagram

#### SD-6.3.1 Enkripsi dan Embedding
```
Pengguna → App: Upload Cover Image
App → LSBSteganography: Calculate Capacity
LSBSteganography → App: Return Capacity
Pengguna → App: Input Pesan
Pengguna → App: Input Stego Key
Pengguna → App: Klik "Enkrip"
App → ElGamal: Encrypt Bytes
ElGamal → App: Return Encrypted Message
App → LSBSteganography: Apply Reed-Solomon ECC
LSBSteganography → App: Return Encoded Message
App → LSBSteganography: Embed
LSBSteganography → LSBSteganography: Generate PRNG Sequence
LSBSteganography → LSBSteganography: Embed Bits to LSB
LSBSteganography → App: Return Stego Image
App → LSBSteganography: Calculate PSNR
LSBSteganography → App: Return PSNR
App → Pengguna: Tampilkan Stego Image dan PSNR
```

#### SD-6.3.2 Ekstraksi dan Dekripsi
```
Pengguna → App: Upload Stego Image
App → App: Calculate SHA-256 Hash
App → Pengguna: Tampilkan Stego Image dan Hash
Pengguna → App: Input Stego Key
Pengguna → App: Klik "Dekrip"
App → LSBSteganography: Extract
LSBSteganography → LSBSteganography: Generate PRNG Sequence
LSBSteganography → LSBSteganography: Extract Bits from LSB
LSBSteganography → LSBSteganography: Validate Length
LSBSteganography → LSBSteganography: Apply Reed-Solomon Decoding
LSBSteganography → App: Return Encrypted Message
App → ElGamal: Decrypt Bytes
ElGamal → App: Return Decrypted Message
App → Pengguna: Tampilkan Pesan Asli
```

### 6.4 Data Flow Diagram

#### DFD-6.4.1 Level 0
```
Pengguna → [Sistem Steganografi] → Pengguna
```

#### DFD-6.4.2 Level 1
```
Pengguna → [Modul Enkripsi] → Pesan Terenkripsi
Pesan Terenkripsi → [Modul Reed-Solomon ECC] → Pesan Terenkripsi + Parity
Pesan Terenkripsi + Parity → [Modul Steganografi] → Stego Image
Stego Image → [Modul Ekstraksi] → Pesan Terenkripsi + Parity
Pesan Terenkripsi + Parity → [Modul Reed-Solomon Decoding] → Pesan Terenkripsi
Pesan Terenkripsi → [Modul Dekripsi] → Pesan Asli
Cover Image, Stego Image → [Modul Analisis] → Metrik & Visualisasi
```

### 6.5 Entity Relationship Diagram

Tidak ada database yang digunakan dalam sistem ini. Semua data disimpan di session state Streamlit (in-memory).

### 6.6 State Diagram

#### SD-6.6.1 State ElGamal
```
[Uninitialized] → Initialize → [Ready]
[Ready] → Generate Keys → [Keys Generated]
[Keys Generated] → Generate Keys → [Keys Generated]
[Keys Generated] → Encrypt → [Ready]
[Keys Generated] → Decrypt → [Ready]
```

#### SD-6.6.2 State Steganografi
```
[No Image] → Upload Cover → [Cover Loaded]
[Cover Loaded] → Embed → [Stego Ready]
[Cover Loaded] → Upload New Cover → [Cover Loaded]
[Stego Ready] → Download → [Stego Ready]
[No Image] → Upload Stego → [Stego Loaded]
[Stego Loaded] → Extract → [Message Extracted]
[Stego Loaded] → Upload New Stego → [Stego Loaded]
```

#### SD-6.6.3 State Reed-Solomon
```
[Ready] → Encode (nsym=20) → [Encoded]
[Encoded] → Decode (nsym=20) → [Decoded]
[Decoded] → Validate → [Success]
[Decoded] → Validate → [Failed]
[Failed] → Try Auto-detect nsym → [Decoded (Alternative nsym)]
[Decoded (Alternative nsym)] → Validate → [Success]
[Decoded (Alternative nsym)] → Validate → [Failed (All nsym)]
```

---

## 7. Persyaratan Pengujian

### 7.1 Pengujian Fungsional

#### TC-7.1.1 Generate Key Pair
**Tujuan**: Memastikan key pair ElGamal dapat dihasilkan dengan benar.

**Langkah**:
1. Buka aplikasi
2. Periksa sidebar untuk melihat kunci default
3. Klik tombol "Generate New Keys"
4. Verifikasi kunci baru ditampilkan
5. Verifikasi kunci berbeda dari sebelumnya

**Expected Result**: Kunci baru berhasil dihasilkan dan ditampilkan

#### TC-7.1.2 Encrypt and Embed Valid Message
**Tujuan**: Memastikan pesan dapat dienkripsi dan disematkan dengan benar.

**Langkah**:
1. Upload cover image
2. Input pesan pendek (< kapasitas)
3. Input stego key
4. Klik "Enkrip"
5. Verifikasi pesan terenkripsi ditampilkan
6. Verifikasi stego image ditampilkan
7. Verifikasi PSNR ditampilkan
8. Download stego image

**Expected Result**: Enkripsi dan embedding berhasil, stego image tersedia

#### TC-7.1.3 Extract and Decrypt Valid Message
**Tujuan**: Memastikan pesan dapat diekstrak dan didekripsi dengan benar.

**Langkah**:
1. Upload stego image (dari TC-7.1.2)
2. Input stego key yang sama
3. Klik "Dekrip"
4. Verifikasi pesan asli ditampilkan
5. Verifikasi pesan sama dengan pesan asli

**Expected Result**: Ekstraksi dan dekripsi berhasil, pesan asli ditampilkan

#### TC-7.1.4 Extract with Wrong Stego Key
**Tujuan**: Memastikan stego key yang salah menghasilkan error.

**Langkah**:
1. Upload stego image
2. Input stego key yang berbeda
3. Klik "Dekrip"

**Expected Result**: Error message ditampilkan, pesan tidak berhasil diekstrak

#### TC-7.1.5 Embed Message Exceeding Capacity
**Tujuan**: Memastikan pesan yang terlalu besar ditolak.

**Langkah**:
1. Upload cover image kecil
2. Input pesan panjang (> kapasitas)
3. Input stego key
4. Klik "Enkrip"

**Expected Result**: Error message ditampilkan, pesan tidak disematkan

#### TC-7.1.6 Analysis Display
**Tujuan**: Memastikan analisis ditampilkan dengan benar.

**Langkah**:
1. Lakukan enkripsi dan embedding (TC-7.1.2)
2. Buka tab "Analisis"
3. Verifikasi cover dan stego image ditampilkan
4. Verifikasi histogram comparison ditampilkan
5. Verifikasi histogram difference ditampilkan
6. Verifikasi metrik statistik ditampilkan
7. Verifikasi LSB plane ditampilkan

**Expected Result**: Semua analisis ditampilkan dengan benar

#### TC-7.1.7 Reed-Solomon Encoding and Decoding
**Tujuan**: Memastikan Reed-Solomon ECC berfungsi dengan benar.

**Langkah**:
1. Lakukan enkripsi dan embedding (TC-7.1.2)
2. Verifikasi pesan terenkripsi memiliki Reed-Solomon parity bytes
3. Lakukan ekstraksi dan dekripsi (TC-7.1.3)
4. Verifikasi pesan asli sama dengan pesan input

**Expected Result**: Reed-Solomon encoding dan decoding berhasil

#### TC-7.1.8 Reed-Solomon Auto-detection nsym
**Tujuan**: Memastikan auto-detection nsym berfungsi untuk backward compatibility.

**Langkah**:
1. Upload stego image lama (dengan nsym=10)
2. Input stego key yang benar
3. Klik "Dekrip"
4. Verifikasi sistem mencoba nsym alternatif
5. Verifikasi pesan berhasil diekstrak

**Expected Result**: Auto-detection nsym berhasil, pesan diekstrak dengan benar

#### TC-7.1.9 SHA-256 Hash Verification
**Tujuan**: Memastikan SHA-256 hash ditampilkan untuk verifikasi integritas.

**Langkah**:
1. Upload stego image
2. Verifikasi SHA-256 hash ditampilkan
3. Catat hash
4. Upload file yang sama lagi
5. Verifikasi hash sama

**Expected Result**: SHA-256 hash ditampilkan dan konsisten untuk file yang sama

### 7.2 Pengujian Non-Fungsional

#### TC-7.2.1 Performance - Encryption Time
**Tujuan**: Memastikan waktu enkripsi ≤ 1 detik.

**Langkah**:
1. Upload cover image
2. Input pesan pendek (< 100 bytes)
3. Input stego key
4. Klik "Enkrip"
5. Catat waktu enkripsi

**Expected Result**: Waktu enkripsi ≤ 1 detik

#### TC-7.2.2 Performance - Embedding Time
**Tujuan**: Memastikan waktu embedding ≤ 2 detik untuk gambar 512x512.

**Langkah**:
1. Upload cover image 512x512
2. Input pesan pendek
3. Input stego key
4. Klik "Enkrip"
5. Catat waktu embedding

**Expected Result**: Waktu embedding ≤ 2 detik

#### TC-7.2.3 Performance - Reed-Solomon Time
**Tujuan**: Memastikan waktu encoding/decoding Reed-Solomon ≤ 0.5 detik untuk pesan < 1KB.

**Langkah**:
1. Upload cover image
2. Input pesan < 1KB
3. Input stego key
4. Klik "Enkrip"
5. Catat waktu encoding Reed-Solomon
6. Klik "Dekrip"
7. Catat waktu decoding Reed-Solomon

**Expected Result**: Waktu encoding/decoding ≤ 0.5 detik

#### TC-7.2.4 Security - Private Key Not Persisted
**Tujuan**: Memastikan private key tidak disimpan di file.

**Langkah**:
1. Generate key pair
2. Tutup aplikasi
3. Buka aplikasi lagi
4. Periksa kunci

**Expected Result**: Kunci baru dihasilkan (private key tidak dipersistenkan)

#### TC-7.2.5 Compatibility - Image Formats
**Tujuan**: Memastikan berbagai format gambar didukung.

**Langkah**:
1. Upload PNG image
2. Verifikasi berhasil
3. Upload JPG image
4. Verifikasi berhasil
5. Upload JPEG image
6. Verifikasi berhasil
7. Upload BMP image
8. Verifikasi berhasil

**Expected Result**: Semua format didukung

#### TC-7.2.6 Compatibility - Image Types
**Tujuan**: Memastikan berbagai tipe gambar didukung.

**Langkah**:
1. Upload grayscale image
2. Verifikasi berhasil
3. Upload RGB image
4. Verifikasi berhasil
5. Upload RGBA image
6. Verifikasi berhasil

**Expected Result**: Semua tipe didukung

#### TC-7.2.7 Reliability - Reed-Solomon Error Correction
**Tujuan**: Memastikan Reed-Solomon dapat mengoreksi error burst.

**Langkah**:
1. Lakukan enkripsi dan embedding
2. Simulasi error dengan mengubah beberapa byte di stego image
3. Lakukan ekstraksi dan dekripsi
4. Verifikasi pesan berhasil dikoreksi

**Expected Result**: Reed-Solomon berhasil mengoreksi error hingga nsym parity symbols

#### TC-7.2.8 Usability - Error Messages
**Tujuan**: Memastikan error messages jelas dan memberikan solusi.

**Langkah**:
1. Upload stego image yang sudah dimodifikasi
2. Input stego key yang benar
3. Klik "Dekrip"
4. Verifikasi error message ditampilkan
5. Verifikasi error message memberikan solusi

**Expected Result**: Error messages jelas dan informatif

---

## 8. Revisi

|| Versi | Tanggal | Deskripsi Perubahan | Penulis |
||-------|---------|---------------------|---------|
|| 1.0 | 2026-09-27 | Dokumen SRS awal | Devin |
|| 1.1 | 2026-09-27 | Penambahan Reed-Solomon ECC (nsym=20, auto-detection, error handling), SHA-256 hash verification, update FR dan NFR terkait | Devin |

---

## 9. Persetujuan

|| Nama | Peran | Tanda Tangan | Tanggal |
||------|-------|--------------|---------|
|| | | | |
|| | | | |
|| | | | |
