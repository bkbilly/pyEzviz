from hashlib import md5
from Crypto.Cipher import AES

from .exceptions import (
    PyEzvizError
)

def decrypt_image(input_data, password):
    """Decrypts image data with provided password

    Args:
        input_data (bytes): Encrypted image data
        password (string): Verification code

    Raises:
        PyEzvizError

    Returns:
        bytes: Decrypted image data
    """

    if len(input_data) < 48:
        raise PyEzvizError("Invalid image data")

    # check header
    if input_data[:16] != b'hikencodepicture':
        raise PyEzvizError("Image header doesn't contain 'hikencodepicture'")
    
    file_hash = input_data[16:48]
    passwd_hash = md5(str.encode(md5(str.encode(password)).digest().hex())).digest().hex()
    if file_hash != str.encode(passwd_hash):
        raise PyEzvizError("Invalid password")

    key = str.encode(password.ljust(16, '\u0000')[:16])
    iv = bytes([48, 49, 50, 51, 52, 53, 54, 55, 0, 0, 0, 0, 0, 0, 0, 0])
    cipher = AES.new(key, AES.MODE_CBC, iv)
    
    next_chunk = b''
    output_data = b''
    finished = False
    i = 48 #offset hikencodepicture + hash
    chunk_size = 1024 * AES.block_size
    while not finished:
        chunk, next_chunk = next_chunk, cipher.decrypt(input_data[i:i+chunk_size])
        if len(next_chunk) == 0:
            padding_length = chunk[-1]
            chunk = chunk[:-padding_length]
            finished = True
        output_data += chunk
        i += chunk_size
    return output_data
