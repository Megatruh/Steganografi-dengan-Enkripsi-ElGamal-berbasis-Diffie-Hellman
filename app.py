import streamlit as st
import numpy as np
from PIL import Image
import io
import matplotlib.pyplot as plt
import hashlib

from elgamal import ElGamalDH
from steganography import LSBSteganography
from analysis import (plot_histogram_comparison, plot_histogram_difference, 
                      calculate_statistical_metrics, close_figure)
import reedsolo

# Page configuration
st.set_page_config(
    page_title="Steganografi dengan Enkripsi ElGamal",
    page_icon="🔐",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2c3e50;
        margin-top: 2rem;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">🔐 Steganografi dengan Enkripsi ElGamal berbasis Diffie-Hellman</h1>', 
            unsafe_allow_html=True)

st.markdown("""
Aplikasi ini melakukan steganografi pada gambar dengan alur kerja:
1. Pesan dienkripsi menggunakan algoritma ElGamal berbasis Diffie-Hellman
2. Pesan terenkripsi dilindungi dengan Reed-Solomon Error Correction Code (ECC)
3. Pesan terenkripsi disembunyikan menggunakan metode LSB yang diacak dengan PRNG
4. Analisis perbandingan histogram cover dan stego
5. Steganalisis visual dengan menampilkan bidang LSB (enhanced LSB)
""")

# Cache ElGamal instance to avoid regenerating safe prime on each rerun
@st.cache_resource
def get_elgamal_instance():
    """Get or create cached ElGamal instance."""
    return ElGamalDH()

# Initialize session state
if 'elgamal' not in st.session_state:
    st.session_state.elgamal = get_elgamal_instance()
if 'private_key' not in st.session_state:
    st.session_state.private_key, st.session_state.public_key = st.session_state.elgamal.generate_keypair()

# Sidebar for key management
st.sidebar.title("🔑 Manajemen Kunci")

st.sidebar.subheader("ElGamal Parameters")
st.sidebar.write(f"Prime (p): {st.session_state.elgamal.p}")
st.sidebar.write(f"Generator (g): {st.session_state.elgamal.g}")

st.sidebar.subheader("Key Pair")
st.sidebar.write(f"Private Key: {st.session_state.private_key}")
st.sidebar.write(f"Public Key: {st.session_state.public_key}")

if st.sidebar.button("Generate New Keys"):
    # Clear cache and regenerate
    st.cache_resource.clear()
    st.session_state.elgamal = get_elgamal_instance()
    st.session_state.private_key, st.session_state.public_key = st.session_state.elgamal.generate_keypair()
    st.sidebar.success("New keys generated!")
    st.rerun()

# Main content
tab1, tab2, tab3 = st.tabs(["🔒 Enkripsi", "🔓 Dekripsi", "📊 Analisis"])

# Tab 1: Enkripsi
with tab1:
    st.markdown('<h2 class="section-header">Enkripsi</h2>', unsafe_allow_html=True)
    
    st.markdown("Upload gambar, masukkan pesan, dan stego key untuk melakukan enkripsi dan steganografi.")
    
    # Upload cover image
    cover_file = st.file_uploader("Upload Gambar Cover", type=['png', 'jpg', 'jpeg', 'bmp'])
    
    if cover_file:
        cover_image = Image.open(cover_file)
        cover_array = np.array(cover_image)
        
        # Convert to RGB if necessary
        if len(cover_array.shape) == 2:
            cover_array = np.stack([cover_array] * 3, axis=2)
        elif cover_array.shape[2] == 4:
            cover_array = cover_array[:, :, :3]
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(cover_image, caption="Cover Image", width='stretch')
        
        with col2:
            # Calculate capacity
            stego = LSBSteganography()
            capacity = stego.calculate_capacity(cover_array)
            st.info(f"Kapasitas maksimum: {capacity} bytes")
    
    # Input message
    message = st.text_area("Input Pesan", height=100, placeholder="Masukkan pesan yang ingin disembunyikan...")
    
    # Input stego key
    stego_key = st.text_input("Input Stego Key", value="12345", help="Seed untuk PRNG dalam acak posisi LSB")
    
    # Encrypt button
    if st.button("🔒 Enkrip", type="primary"):
        if cover_file and message:
            try:
                # Encrypt message using ElGamal
                message_bytes = message.encode('utf-8')
                encrypted_message = st.session_state.elgamal.encrypt_bytes(
                    message_bytes, 
                    st.session_state.public_key
                )
                
                st.success(f"✓ Pesan terenkripsi: {len(encrypted_message)} bytes")
                
                # Check capacity
                if len(encrypted_message) > capacity:
                    st.error(f"✗ Pesan terlalu besar! Kapasitas: {capacity} bytes, Pesan: {len(encrypted_message)} bytes")
                else:
                    # Embed using LSB with PRNG
                    stego = LSBSteganography(seed=int(stego_key))
                    stego_array = stego.embed(cover_array, encrypted_message)
                    
                    # Calculate PSNR
                    psnr = stego.calculate_psnr(cover_array, stego_array)
                    st.info(f"PSNR: {psnr:.2f} dB")
                    
                    # Display stego image
                    stego_image = Image.fromarray(stego_array)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(stego_image, caption="Stego Image", width='stretch')
                    
                    with col2:
                        # Download button
                        buf = io.BytesIO()
                        stego_image.save(buf, format='PNG')
                        buf.seek(0)
                        st.download_button(
                            label="⬇️ Download Stego Image",
                            data=buf,
                            file_name="stego_image.png",
                            mime="image/png"
                        )
                    
                    # Save to session state for analysis
                    # Ensure both arrays have the same shape for histogram comparison
                    if len(cover_array.shape) == 2:
                        # If original was grayscale, convert stego back to grayscale
                        if len(stego_array.shape) == 3:
                            stego_array = stego_array[:, :, 0]
                    st.session_state.stego_array = stego_array
                    st.session_state.cover_array = cover_array
                    st.session_state.stego_key = stego_key
                    
                    st.success("✓ Enkripsi dan steganografi berhasil!")
                    
            except Exception as e:
                st.error(f"✗ Error: {str(e)}")
        else:
            st.warning("⚠️ Silakan upload gambar dan masukkan pesan!")

# Tab 2: Dekripsi
with tab2:
    st.markdown('<h2 class="section-header">Dekripsi</h2>', unsafe_allow_html=True)
    
    st.markdown("Upload gambar stego dan masukkan stego key untuk mengekstrak dan mendekripsi pesan.")
    
    # Upload stego image
    stego_file = st.file_uploader("Upload Gambar Stego", type=['png', 'jpg', 'jpeg', 'bmp'], key='stego_upload')
    
    if stego_file:
        stego_image = Image.open(stego_file)
        stego_array = np.array(stego_image)
        
        # Convert to RGB if necessary
        if len(stego_array.shape) == 2:
            stego_array = np.stack([stego_array] * 3, axis=2)
        elif stego_array.shape[2] == 4:
            stego_array = stego_array[:, :, :3]
        
        st.image(stego_image, caption="Stego Image", width='stretch')
        
        # Calculate and display SHA-256 hash for integrity verification
        stego_file.seek(0)
        file_hash = hashlib.sha256(stego_file.read()).hexdigest()
        st.info(f"🔒 SHA-256 Hash: {file_hash}")
        st.caption("Gunakan hash ini untuk verifikasi integritas file stego")
    
    # Input stego key
    extract_stego_key = st.text_input("Input Stego Key", value="12345", key='extract_key', help="Gunakan stego key yang sama saat enkripsi")
    
    # Decrypt button
    if st.button("🔓 Dekrip", type="primary"):
        if stego_file:
            try:
                # Extract using LSB with PRNG and Reed-Solomon error correction
                # auto_detect_nsym=True (default) enables backward compatibility with old stego images
                stego = LSBSteganography(seed=int(extract_stego_key))
                encrypted_message = stego.extract(stego_array)
                
                st.success(f"✓ Pesan terenkripsi diekstrak: {len(encrypted_message)} bytes")
                
                # Decrypt using ElGamal
                decrypted_bytes = st.session_state.elgamal.decrypt_bytes(
                    encrypted_message,
                    st.session_state.private_key
                )
                
                decrypted_message = decrypted_bytes.decode('utf-8')
                
                st.subheader("Pesan yang Diekstrak dan Didekripsi:")
                st.text_area("", decrypted_message, height=150, key='decrypted_output')
                
                st.success("✓ Dekripsi berhasil!")
                
            except reedsolo.ReedSolomonError as e:
                # Specific error handling for Reed-Solomon decoding failure
                st.error("✗ Reed-Solomon Error Correction Gagal")
                st.error(f"Detail: {str(e)}")
                st.warning("💡 Solusi: Gambar stego mungkin telah berubah (ter-kompresi ulang/ter-resize/ter-edit) saat transfer, meskipun formatnya tetap PNG. Coba gunakan file asli atau verifikasi hash file.")
            except Exception as e:
                st.error(f"✗ Error: {str(e)}")
                st.error("Pastikan stego key benar dan gambar mengandung pesan terenkripsi!")
        else:
            st.warning("⚠️ Silakan upload gambar stego!")

# Tab 3: Analisis
with tab3:
    st.markdown('<h2 class="section-header">Analisis Steganografi</h2>', unsafe_allow_html=True)
    
    st.markdown("Analisis histogram, metrik statistik, dan visual steganalysis LSB plane.")
    
    if 'stego_array' in st.session_state and 'cover_array' in st.session_state:
        stego_array = st.session_state.stego_array
        cover_array = st.session_state.cover_array
        
        col1, col2 = st.columns(2)
        with col1:
            st.image(Image.fromarray(cover_array), caption="Cover Image", width='stretch')
        with col2:
            st.image(Image.fromarray(stego_array), caption="Stego Image", width='stretch')
        
        # Show histogram comparison
        st.subheader("Perbandingan Histogram")
        hist_fig = plot_histogram_comparison(cover_array, stego_array, 
                                            "Histogram: Cover vs Stego")
        st.pyplot(hist_fig)
        close_figure(hist_fig)  # Free memory
        
        # Show histogram difference
        st.subheader("Perbedaan Histogram")
        diff_fig = plot_histogram_difference(cover_array, stego_array,
                                           "Histogram Difference")
        st.pyplot(diff_fig)
        close_figure(diff_fig)  # Free memory
        
        # Show statistical metrics
        st.subheader("Metrik Statistik")
        metrics = calculate_statistical_metrics(cover_array, stego_array)
        col_metrics1, col_metrics2, col_metrics3, col_metrics4 = st.columns(4)
        with col_metrics1:
            st.metric("MSE", f"{metrics['MSE']:.4f}")
        with col_metrics2:
            st.metric("PSNR", f"{metrics['PSNR']:.2f} dB")
        with col_metrics3:
            st.metric("MAE", f"{metrics['MAE']:.4f}")
        with col_metrics4:
            st.metric("Correlation", f"{metrics['Correlation']:.4f}")
        
        # Show LSB plane
        st.subheader("Visual Steganalysis - LSB Plane")
        stego = LSBSteganography()
        lsb_plane = stego.get_lsb_plane(stego_array)
        lsb_image = Image.fromarray(lsb_plane)
        st.image(lsb_image, caption="Enhanced LSB Plane", width='stretch')
        
    else:
        st.info("ℹ️ Silakan lakukan enkripsi terlebih dahulu untuk melihat analisis.")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666;'>
    <p>Steganografi dengan Enkripsi ElGamal berbasis Diffie-Hellman</p>
    <p>Dibuat untuk Tugas Keamanan Informasi</p>
</div>
""", unsafe_allow_html=True)
