import numpy as np
from PIL import Image
import random
from typing import Tuple

class LSBSteganography:
    """
    LSB Steganography with PRNG-based randomization.
    """
    
    def __init__(self, seed: int = None):
        """
        Initialize with seed for PRNG.
        """
        self.seed = seed
    
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
        Calculate maximum capacity in bytes (accounting for 4-byte length header).
        Each pixel can store 1 bit (LSB).
        """
        if len(image.shape) == 2:
            height, width = image.shape
            channels = 1
        else:
            height, width, channels = image.shape
        
        total_bits = height * width * channels
        # Reserve 32 bits (4 bytes) for message length header
        usable_bits = total_bits - 32
        return max(0, usable_bits // 8)  # Convert to bytes
    
    def embed(self, image: np.ndarray, message: bytes) -> np.ndarray:
        """
        Embed message into image using randomized LSB.
        Returns modified image array.
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
        
        # Calculate capacity
        capacity = self.calculate_capacity(image)
        
        if len(message) > capacity:
            raise ValueError(f"Message too large. Capacity: {capacity} bytes, Message: {len(message)} bytes")
        
        # Add message length (4 bytes) at the beginning
        length_bytes = len(message).to_bytes(4, byteorder='big')
        data_to_embed = length_bytes + message
        
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
        Extract message from stego image using randomized LSB.
        Returns extracted message.
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
        message_length = int.from_bytes(length_bytes, byteorder='big')
        
        # Validate message length
        max_capacity = (total_pixels - 32) // 8
        if message_length < 0 or message_length > max_capacity:
            raise ValueError(f"Invalid message length: {message_length}. Possible corrupted data or wrong stego key. Max capacity: {max_capacity}")
        
        # Extract message bits
        total_message_bits = message_length * 8
        message_bits = []
        start_idx = 32
        end_idx = min(32 + total_message_bits, len(indices))
        
        for i in range(start_idx, end_idx):
            if i >= len(indices):
                break
            row, col, channel = self._index_to_position(indices[i], height, width, channels)
            message_bits.append(stego_image_temp[row, col, channel] & 1)
        
        # Convert bits to bytes (little-endian bit order within each byte)
        message = bytearray()
        for i in range(0, len(message_bits), 8):
            byte = 0
            for j in range(8):
                if i + j < len(message_bits):
                    byte |= (message_bits[i + j] << j)
            message.append(byte)
        
        return bytes(message)
    
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
