import numpy as np
from PIL import Image
import random
from typing import Tuple
import reedsolo

class LSBSteganography:
    """
    LSB Steganography with PRNG-based randomization.
    """
    
    def __init__(self, seed: int = None, nsym=20, **kwargs):
        """
        Initialize with seed for PRNG and Reed-Solomon parity symbols.
        
        Args:
            seed: Seed for PRNG (Pseudo-Random Number Generator)
            nsym: Number of parity symbols for Reed-Solomon ECC (default: 20)
                  Higher values provide more error correction but reduce capacity
                  Increased from 10 to 20 for better tolerance against file transfer errors
            **kwargs: Additional keyword arguments (for backward compatibility)
                      auto_detect_nsym: If True, will attempt to auto-detect nsym during extraction
                                       for backward compatibility with old stego images (nsym=10)
        """
        self.seed = seed
        self.nsym = nsym
        # Extract auto_detect_nsym from kwargs with default True
        self.auto_detect_nsym = kwargs.get('auto_detect_nsym', True)
        # Initialize Reed-Solomon codec with specified parity symbols
        self.rs = reedsolo.RSCodec(nsym)
    
    def _generate_pixel_indices(self, total_pixels: int) -> list:
        """
        Generate randomized pixel indices using Python random for determinism.
        Returns list of shuffled indices.
        """
        indices = list(range(total_pixels))
        if self.seed is not None:
            # Use local random state to avoid affecting global state
            rng = random.Random(self.seed)
            rng.shuffle(indices)
        return indices
    
    def _index_to_position(self, index: int, height: int, width: int, channels: int) -> Tuple[int, int, int]:
        """
        Convert flat index to (row, col, channel) position.
        """
        channel = index % channels
        remaining = index // channels
        row = remaining // width
        col = remaining % width
        return (int(row), int(col), int(channel))
    
    def calculate_capacity(self, image: np.ndarray) -> int:
        """
        Calculate maximum capacity in bytes (accounting for 4-byte length header and Reed-Solomon parity).
        Each pixel can store 1 bit (LSB).
        
        Note: Capacity is reduced by Reed-Solomon parity bytes overhead.
        """
        if len(image.shape) == 2:
            height, width = image.shape
            channels = 1
        else:
            height, width, channels = image.shape
        
        total_bits = height * width * channels
        # Reserve 32 bits (4 bytes) for message length header
        usable_bits = total_bits - 32
        raw_capacity = max(0, usable_bits // 8)  # Convert to bytes
        
        # Calculate effective capacity accounting for Reed-Solomon overhead
        # RSCodec adds nsym parity bytes, so effective data capacity is:
        # effective_capacity = raw_capacity - nsym - 4 (for length header)
        effective_capacity = max(0, raw_capacity - self.nsym - 4)
        
        return effective_capacity
    
    def embed(self, image: np.ndarray, message: bytes) -> np.ndarray:
        """
        Embed message into image using randomized LSB with Reed-Solomon error correction.
        
        Args:
            image: Cover image as numpy array
            message: Encrypted message bytes (typically from ElGamal)
            
        Returns:
            Stego image as numpy array
            
        Process:
        1. Apply Reed-Solomon encoding to add parity bytes for error correction
        2. Add message length header
        3. Embed encoded data using randomized LSB
        """
        # Convert to mutable array
        stego_image = image.copy()
        
        # Handle grayscale images
        if len(image.shape) == 2:
            height, width = image.shape
            channels = 1
            # Add channel dimension for consistency
            stego_image = stego_image[:, :, np.newaxis]
        else:
            height, width, channels = image.shape
        
        total_pixels = height * width * channels
        
        # Calculate capacity (already accounts for Reed-Solomon overhead)
        capacity = self.calculate_capacity(image)
        
        if len(message) > capacity:
            raise ValueError(f"Message too large. Capacity: {capacity} bytes, Message: {len(message)} bytes")
        
        # Apply Reed-Solomon encoding to add parity bytes for error correction
        # This adds nsym parity bytes to the message for burst error recovery
        encoded_message = self.rs.encode(message)
        
        # Add message length (4 bytes) at the beginning
        # Note: We store the ENCODED message length (original + parity bytes)
        length_bytes = len(encoded_message).to_bytes(4, byteorder='big')
        data_to_embed = length_bytes + encoded_message
        
        # Convert data to bit stream
        total_bits = len(data_to_embed) * 8
        bit_stream = []
        for byte in data_to_embed:
            for i in range(8):
                bit_stream.append((byte >> i) & 1)
        
        # Generate randomized pixel indices
        indices = self._generate_pixel_indices(total_pixels)
        
        # Embed bits
        for idx, pixel_idx in enumerate(indices):
            if idx >= len(bit_stream):
                break
            
            row, col, channel = self._index_to_position(pixel_idx, height, width, channels)
            
            # Clear LSB and set to message bit
            stego_image[row, col, channel] = (stego_image[row, col, channel] & 0xFE) | bit_stream[idx]
        
        # Keep the same shape as original image
        if len(image.shape) == 2:
            stego_image = stego_image[:, :, 0]
        
        return stego_image
    
    def extract(self, stego_image: np.ndarray) -> bytes:
        """
        Extract message from stego image using randomized LSB with Reed-Solomon error correction.
        
        Args:
            stego_image: Stego image as numpy array
            
        Returns:
            Decoded (error-corrected) message bytes
            
        Process:
        1. Extract raw encoded data from LSB
        2. Apply Reed-Solomon decoding to correct burst errors
        3. Return corrected message bytes
            
        Raises:
            reedsolo.ReedSolomonError: If JPEG compression damage exceeds ECC tolerance
            ValueError: If message length is invalid or data is corrupted
        """
        # Handle grayscale images
        if len(stego_image.shape) == 2:
            height, width = stego_image.shape
            channels = 1
            # Add channel dimension for consistency
            stego_image_temp = stego_image[:, :, np.newaxis]
        else:
            height, width, channels = stego_image.shape
            stego_image_temp = stego_image
        
        total_pixels = height * width * channels
        
        # Generate randomized pixel indices
        indices = self._generate_pixel_indices(total_pixels)
        
        # Extract first 32 bits for message length
        length_bits = []
        for i in range(32):
            row, col, channel = self._index_to_position(indices[i], height, width, channels)
            length_bits.append(stego_image_temp[row, col, channel] & 1)
        
        # Convert length bits to bytes (little-endian bit order within each byte)
        length_bytes = bytearray()
        for byte_num in range(4):
            byte_val = 0
            for bit_num in range(8):
                bit_idx = byte_num * 8 + bit_num
                if bit_idx < len(length_bits):
                    byte_val |= (length_bits[bit_idx] << bit_num)
            length_bytes.append(byte_val)
        
        # Convert bytes to integer (big-endian byte order)
        # This is the ENCODED message length (original + parity bytes)
        encoded_length = int.from_bytes(length_bytes, byteorder='big')
        
        # Validate encoded message length
        max_capacity = (total_pixels - 32) // 8
        if encoded_length < 0 or encoded_length > max_capacity:
            raise ValueError(f"Invalid encoded message length: {encoded_length}. Possible corrupted data or wrong stego key. Max capacity: {max_capacity}")
        
        # Extract encoded message bits (including Reed-Solomon parity bytes)
        total_encoded_bits = encoded_length * 8
        encoded_bits = []
        start_idx = 32
        end_idx = min(32 + total_encoded_bits, len(indices))
        
        for i in range(start_idx, end_idx):
            if i >= len(indices):
                break
            row, col, channel = self._index_to_position(indices[i], height, width, channels)
            encoded_bits.append(stego_image_temp[row, col, channel] & 1)
        
        # Convert bits to bytes (little-endian bit order within each byte)
        encoded_message = bytearray()
        for i in range(0, len(encoded_bits), 8):
            byte = 0
            for j in range(8):
                if i + j < len(encoded_bits):
                    byte |= (encoded_bits[i + j] << j)
            encoded_message.append(byte)
        
        def decode_with_nsym(nsym: int) -> bytes:
            codec = self.rs if nsym == self.nsym else reedsolo.RSCodec(nsym)
            result = codec.decode(bytes(encoded_message))
            decoded = bytes(result[0] if isinstance(result, tuple) else result)

            if isinstance(result, tuple) and len(result) > 1:
                corrected_codeword = bytes(result[1])
                if corrected_codeword != bytes(codec.encode(decoded)):
                    raise reedsolo.ReedSolomonError(
                        f"Decoded payload validation failed for nsym={nsym}"
                    )

            return decoded

        try:
            return decode_with_nsym(self.nsym)
        except reedsolo.ReedSolomonError as error:
            if not self.auto_detect_nsym:
                raise reedsolo.ReedSolomonError(
                    f"Reed-Solomon error correction failed for nsym={self.nsym}. "
                    f"The stego key may be wrong, or the image was changed after embedding. "
                    f"Error details: {str(error)}"
                ) from error

            fallback_nsymbols = [10, 15, 25, 30]
            for fallback_nsym in fallback_nsymbols:
                if fallback_nsym == self.nsym:
                    continue
                try:
                    return decode_with_nsym(fallback_nsym)
                except (reedsolo.ReedSolomonError, ValueError, IndexError):
                    continue

            raise reedsolo.ReedSolomonError(
                f"Reed-Solomon decoding failed for nsym values "
                f"[{self.nsym}, {', '.join(map(str, fallback_nsymbols))}]. "
                f"The stego key may be wrong, or the image was changed after embedding. "
                f"Original error: {str(error)}"
            ) from error
    
    def get_lsb_plane(self, image: np.ndarray) -> np.ndarray:
        """
        Extract LSB plane from image for visual steganalysis.
        Returns grayscale image showing LSB values.
        """
        # Extract LSB from each channel
        lsb_plane = (image & 1).astype(np.uint8)
        
        # Convert to grayscale by averaging channels
        if len(lsb_plane.shape) == 3:
            lsb_gray = np.mean(lsb_plane, axis=2).astype(np.uint8)
        else:
            lsb_gray = lsb_plane
        
        # Enhance LSB (multiply by 255 for visibility)
        lsb_enhanced = (lsb_gray * 255).astype(np.uint8)
        
        return lsb_enhanced
    
    def calculate_psnr(self, original: np.ndarray, stego: np.ndarray) -> float:
        """
        Calculate PSNR (Peak Signal-to-Noise Ratio) between original and stego images.
        """
        mse = np.mean((original.astype(float) - stego.astype(float)) ** 2)
        
        if mse == 0:
            return float('inf')
        
        max_pixel = 255.0
        psnr = 20 * np.log10(max_pixel / np.sqrt(mse))
        
        return psnr
