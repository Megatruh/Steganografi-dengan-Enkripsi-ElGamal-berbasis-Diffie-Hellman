import jpegio as jio
import numpy as np
import os

class DCT_LSBSteganography:
    
    def hide_data(self, cover_image_path, secret_bits_string, output_path):
        """
        Menyembunyikan string biner ke dalam koefisien DCT JPEG.
        """
        if not os.path.exists(cover_image_path):
            raise FileNotFoundError(f"File {cover_image_path} tidak ditemukan.")
            
        jpeg_struct = jio.read(cover_image_path)
        dct_coefficients = jpeg_struct.coef_arrays[0]
        flat_dct = dct_coefficients.flatten()
        
        bit_index = 0
        pesan_panjang = len(secret_bits_string)
        
        for i in range(len(flat_dct)):
            coef = flat_dct[i]
            # ATURAN DCT: Lewati 0, 1, dan -1
            if coef not in [0, 1, -1]:
                if bit_index < pesan_panjang:
                    bit_pesan = int(secret_bits_string[bit_index])
                    tanda = np.sign(coef)
                    nilai_absolut = abs(coef)
                    
                    # LOGIKA LSB UTAMA
                    nilai_baru = (nilai_absolut & ~1) | bit_pesan
                    
                    flat_dct[i] = nilai_baru * tanda
                    bit_index += 1
                else:
                    break
                    
        if bit_index < pesan_panjang:
            raise ValueError("Kapasitas gambar tidak cukup untuk menyisipkan seluruh pesan.")
            
        jpeg_struct.coef_arrays[0] = flat_dct.reshape(dct_coefficients.shape)
        jio.write(jpeg_struct, output_path)
        print(f"Berhasil menyisipkan pesan! Tersimpan di: {output_path}")

    def extract_data(self, stego_image_path, panjang_pesan):
        """
        Mengekstrak pesan biner dari koefisien DCT JPEG.
        """
        jpeg_struct = jio.read(stego_image_path)
        flat_dct = jpeg_struct.coef_arrays[0].flatten()
        
        pesan_biner = ""
        
        for coef in flat_dct:
            if coef not in [0, 1, -1]:
                # EKSTRAKSI LSB UTAMA
                bit_pesan = abs(coef) & 1
                pesan_biner += str(bit_pesan)
                
                if len(pesan_biner) == panjang_pesan:
                    break
                    
        return pesan_biner


# Blok test agar bisa langsung dieksekusi di terminal
if __name__ == "__main__":
    stego = DCT_LSBSteganography()
    
    # Siapkan nama file
    cover_image = "test_image.jpg"  # Pastikan Anda menyiapkan file ini di folder proyek
    stego_image = "test_stego_result.jpg"
    
    pesan_rahasia_biner = "101010101111000011001100" # Contoh pesan dummy
    
    print("--- Test Steganografi DCT LSB ---")
    if os.path.exists(cover_image):
        print(f"Menyisipkan pesan: {pesan_rahasia_biner}")
        stego.hide_data(cover_image, pesan_rahasia_biner, stego_image)
        
        # Coba ekstrak kembali
        pesan_ekstrak = stego.extract_data(stego_image, len(pesan_rahasia_biner))
        print(f"Pesan terekstrak : {pesan_ekstrak}")
        
        if pesan_rahasia_biner == pesan_ekstrak:
            print("STATUS: SUKSES! Pesan berhasil bertahan (utuh).")
        else:
            print("STATUS: GAGAL.")
    else:
        print(f"INFO: Silakan siapkan gambar JPEG dengan nama '{cover_image}' di folder ini terlebih dahulu untuk menjalankan tes.")
