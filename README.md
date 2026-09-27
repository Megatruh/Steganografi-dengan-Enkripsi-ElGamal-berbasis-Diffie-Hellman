# Steganografi dengan Enkripsi ElGamal berbasis Diffie-Hellman

Aplikasi web berbasis Streamlit untuk melakukan steganografi pada gambar dengan enkripsi ElGamal berbasis Diffie-Hellman.

## Fitur

1. **Enkripsi ElGamal berbasis Diffie-Hellman**
   - Menggunakan algoritma ElGamal untuk enkripsi pesan
   - Berbasis Diffie-Hellman untuk pertukaran kunci
   - Generate key pair (private dan public key) secara otomatis

2. **Reed-Solomon Error Correction Code (ECC)**
   - Menambahkan parity bytes untuk koreksi error burst
   - Meningkatkan ketahanan terhadap kompresi lossy (JPEG)
   - Dapat memperbaiki error yang disebabkan oleh konversi PNG ke JPEG

3. **Steganografi LSB dengan PRNG**
   - Menyembunyikan pesan terenkripsi menggunakan metode LSB (Least Significant Bit)
   - Posisi bit diacak menggunakan PRNG (Pseudo-Random Number Generator)
   - Seed untuk PRNG diinput melalui stego key

4. **Analisis Histogram**
   - Perbandingan histogram antara cover image dan stego image
   - Visualisasi perbedaan histogram
   - Metrik statistik (MSE, PSNR, MAE, Correlation)

5. **Steganalisis Visual**
   - Menampilkan bidang LSB (enhanced LSB)
   - Analisis visual untuk mendeteksi keberadaan pesan tersembunyi

## Instalasi

1. Install dependencies:

```bash
pip install -r requirements.txt
```

## Menjalankan Aplikasi

```bash
streamlit run app.py
```

Aplikasi akan berjalan di `http://localhost:8501`

## Cara Penggunaan

### Embed & Encrypt

1. Upload cover image (gambar yang akan menyembunyikan pesan)
2. Masukkan pesan yang ingin disembunyikan
3. Masukkan stego key (seed untuk PRNG)
4. Klik tombol "Encrypt & Embed"
5. Aplikasi akan:
   - Mengenkripsi pesan dengan ElGamal
   - Menyembunyikan pesan terenkripsi dengan LSB yang diacak
   - Menampilkan stego image
   - Menampilkan histogram comparison
   - Menampilkan LSB plane untuk steganalisis
6. Download stego image

### Extract & Decrypt

1. Upload stego image
2. Masukkan stego key yang sama dengan saat embed
3. Klik tombol "Extract & Decrypt"
4. Aplikasi akan:
   - Mengekstrak pesan terenkripsi dari LSB
   - Mendekripsi pesan dengan ElGamal
   - Menampilkan pesan asli
   - Menampilkan LSB plane untuk steganalisis

## Struktur Proyek

```
.
├── app.py              # Streamlit web interface
├── elgamal.py          # Implementasi ElGamal encryption
├── steganography.py    # Implementasi LSB steganography dengan PRNG
├── analysis.py         # Implementasi analisis histogram dan metrik
├── requirements.txt    # Dependencies
└── README.md          # Dokumentasi
```

## Teknologi

- **Streamlit**: Web framework
- **Pillow**: Image processing
- **NumPy**: Numerical computing
- **Matplotlib**: Plotting dan visualisasi
- **Reed-Solo**: Reed-Solomon error correction code untuk ketahanan terhadap kompresi lossy

## Catatan Keamanan

- Private key disimpan di session state dan tidak dipersistenkan
- Stego key diperlukan untuk mengekstrak pesan dari stego image
- ElGamal menggunakan safe prime dan generator yang aman
- LSB randomization meningkatkan keamanan steganografi
