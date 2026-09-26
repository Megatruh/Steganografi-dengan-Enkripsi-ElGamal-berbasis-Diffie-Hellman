import random
from typing import Tuple

# Pre-generated safe prime and generator for 1024-bit (for performance)
# This is a known safe prime: p = 2q + 1 where both p and q are prime
DEFAULT_SAFE_PRIME = int("FFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD129024E088A67CC74020BBEA63B139B22514A08798E3404DDEF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7EDEE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3DC2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F83655D23DCA3AD961C62F356208552BB9ED529077096966D670C354E4ABC9804F1746C08CA18217C32905E462E36CE3BE39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9DE2BCBF6955817183995497CEA956AE515D2261898FA051015728E5A8AACAA68FFFFFFFFFFFFFFFF", 16)

DEFAULT_GENERATOR = 2

class ElGamalDH:
    """
    ElGamal encryption based on Diffie-Hellman key exchange.
    """
    
    def __init__(self, p: int = None, g: int = None):
        """
        Initialize ElGamal with prime p and generator g.
        If not provided, will use pre-generated safe prime and generator for performance.
        """
        if p is None:
            self.p = DEFAULT_SAFE_PRIME
        else:
            self.p = p
        
        if g is None:
            self.g = DEFAULT_GENERATOR
        else:
            self.g = g
    
    def _is_prime(self, n: int) -> bool:
        """Check if n is prime using Miller-Rabin test."""
        if n < 2:
            return False
        if n == 2 or n == 3:
            return True
        if n % 2 == 0:
            return False
        
        # Write n-1 as 2^r * d
        r, d = 0, n - 1
        while d % 2 == 0:
            r += 1
            d //= 2
        
        # Test with multiple witnesses
        for a in [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37]:
            if a >= n:
                continue
            x = pow(a, d, n)
            if x == 1 or x == n - 1:
                continue
            for _ in range(r - 1):
                x = pow(x, 2, n)
                if x == n - 1:
                    break
            else:
                return False
        return True
    
    def _generate_safe_prime(self, bits: int = 1024) -> int:
        """Generate a safe prime (p where (p-1)/2 is also prime)."""
        while True:
            # Generate random odd number
            p = random.getrandbits(bits)
            p |= (1 << bits - 1) | 1  # Ensure bits length and odd
            
            if self._is_prime(p) and self._is_prime((p - 1) // 2):
                return p
    
    def _find_generator(self, p: int) -> int:
        """Find a generator g for the cyclic group Z_p*."""
        # For safe prime p, g=2 or g=5 are usually generators
        # Test if g is a generator
        q = (p - 1) // 2
        for g in [2, 5, 7, 11]:
            if pow(g, 2, p) != 1 and pow(g, q, p) != 1:
                return g
        
        # Fallback: find generator by testing
        for g in range(2, p):
            if pow(g, 2, p) != 1 and pow(g, q, p) != 1:
                return g
        
        return 2  # Default fallback
    
    def generate_keypair(self) -> Tuple[int, int]:
        """
        Generate public/private key pair.
        Returns: (private_key, public_key)
        """
        # Private key: random number in [2, p-2]
        private_key = random.randint(2, self.p - 2)
        
        # Public key: g^private_key mod p
        public_key = pow(self.g, private_key, self.p)
        
        return private_key, public_key
    
    def diffie_hellman_shared_secret(self, private_key: int, other_public_key: int) -> int:
        """
        Compute shared secret using Diffie-Hellman.
        shared_secret = other_public_key^private_key mod p
        """
        return pow(other_public_key, private_key, self.p)
    
    def encrypt(self, message: int, public_key: int) -> Tuple[int, int]:
        """
        Encrypt message using ElGamal.
        Returns: (c1, c2) where c1 = g^k mod p, c2 = message * public_key^k mod p
        """
        # Random ephemeral key k
        k = random.randint(2, self.p - 2)
        
        # c1 = g^k mod p
        c1 = pow(self.g, k, self.p)
        
        # s = public_key^k mod p (shared secret)
        s = pow(public_key, k, self.p)
        
        # c2 = message * s mod p
        c2 = (message * s) % self.p
        
        return c1, c2
    
    def decrypt(self, c1: int, c2: int, private_key: int) -> int:
        """
        Decrypt ciphertext using ElGamal.
        message = c2 * c1^(-private_key) mod p
        """
        # s = c1^private_key mod p
        s = pow(c1, private_key, self.p)
        
        # s_inv = modular inverse of s
        s_inv = pow(s, self.p - 2, self.p)
        
        # message = c2 * s_inv mod p
        message = (c2 * s_inv) % self.p
        
        return message
    
    def encrypt_bytes(self, data: bytes, public_key: int) -> bytes:
        """
        Encrypt bytes data by splitting into blocks.
        Each block is encrypted separately.
        """
        # Add length prefix (4 bytes) to handle padding correctly
        length_prefix = len(data).to_bytes(4, byteorder='big')
        data_with_length = length_prefix + data
        
        encrypted_blocks = []
        
        # Split data into blocks (each block < p)
        block_size = (self.p.bit_length() - 1) // 8
        
        for i in range(0, len(data_with_length), block_size):
            block = data_with_length[i:i + block_size]
            
            # Pad block to exact block_size if needed
            if len(block) < block_size:
                block = block + b'\x00' * (block_size - len(block))
            
            # Convert block to integer
            message_int = int.from_bytes(block, byteorder='big')
            
            # Encrypt
            c1, c2 = self.encrypt(message_int, public_key)
            
            # Convert to bytes
            c1_bytes = c1.to_bytes((self.p.bit_length() + 7) // 8, byteorder='big')
            c2_bytes = c2.to_bytes((self.p.bit_length() + 7) // 8, byteorder='big')
            
            encrypted_blocks.append(c1_bytes)
            encrypted_blocks.append(c2_bytes)
        
        return b''.join(encrypted_blocks)
    
    def decrypt_bytes(self, encrypted_data: bytes, private_key: int) -> bytes:
        """
        Decrypt bytes data by processing blocks.
        """
        decrypted_blocks = []
        
        block_size = (self.p.bit_length() + 7) // 8
        block_size_msg = (self.p.bit_length() - 1) // 8
        
        for i in range(0, len(encrypted_data), 2 * block_size):
            c1_bytes = encrypted_data[i:i + block_size]
            c2_bytes = encrypted_data[i + block_size:i + 2 * block_size]
            
            if len(c1_bytes) < block_size or len(c2_bytes) < block_size:
                break
            
            c1 = int.from_bytes(c1_bytes, byteorder='big')
            c2 = int.from_bytes(c2_bytes, byteorder='big')
            
            # Decrypt
            message_int = self.decrypt(c1, c2, private_key)
            
            # Convert back to bytes
            message_bytes = message_int.to_bytes(block_size_msg, byteorder='big')
            
            decrypted_blocks.append(message_bytes)
        
        result = b''.join(decrypted_blocks)
        
        # Extract length from first 4 bytes
        if len(result) >= 4:
            data_length = int.from_bytes(result[:4], byteorder='big')
            # Extract the actual data (skip length prefix)
            actual_data = result[4:4 + data_length]
            return actual_data
        else:
            return result
