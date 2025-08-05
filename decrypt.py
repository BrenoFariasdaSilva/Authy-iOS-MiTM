import base64 # For base64 encoding/decoding
import json # For handling JSON data
import os # For file and path operations
import re # For regular expression matching
from cryptography.hazmat.backends import default_backend # For cryptographic backend
from cryptography.hazmat.primitives import hashes # For hashing algorithms
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes # For AES encryption/decryption
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC # For key derivation
from dotenv import load_dotenv # For loading environment variables from a .env file
from getpass import getpass # For securely getting the backup password input
from main import BackgroundColors, Style, verbose_output # Importing necessary functions and constants from main.py

def load_authenticator_data(input_file: str) -> dict:
   """
   Loads the JSON data from the input file and verifies the presence of 'authenticator_tokens'.

   :param input_file: Path to the input JSON file
   :return: Parsed JSON data as a dictionary
   :raises FileNotFoundError, json.JSONDecodeError, KeyError: If file issues or key missing
   """

   verbose_output(f"{BackgroundColors.GREEN}DEBUG: Input file: {BackgroundColors.CYAN}{input_file}{Style.RESET_ALL}")

   with open(input_file, "r") as json_file: # Open the input JSON file
      data = json.load(json_file) # Load the JSON data

   if "authenticator_tokens" not in data: # Check if 'authenticator_tokens' key exists in the data
      raise KeyError('Key "authenticator_tokens" not found in the input file.') # Raise error if key is missing

   return data # Return the parsed JSON data as a dictionary


def decode_base64_seed(encrypted_seed_b64: str) -> bytes:
   """
   Decodes the Base64-encoded encrypted seed into raw bytes.

   :param encrypted_seed_b64: Base64 encoded encrypted seed string
   :return: Decoded bytes of the encrypted seed
   """

   verbose_output(f"{BackgroundColors.GREEN}DEBUG: Encrypted seed (base64): {BackgroundColors.CYAN}{encrypted_seed_b64}{Style.RESET_ALL}")

   encrypted_seed = base64.b64decode(encrypted_seed_b64) # Decode the base64 string to bytes

   verbose_output(f"{BackgroundColors.GREEN}DEBUG: Encrypted seed size after base64 decode: {BackgroundColors.CYAN}{len(encrypted_seed)} bytes{Style.RESET_ALL}")
   verbose_output(f"{BackgroundColors.GREEN}DEBUG: Encrypted seed (hex): {BackgroundColors.CYAN}{encrypted_seed.hex()}{Style.RESET_ALL}")

   return encrypted_seed # Return the decoded bytes of the encrypted seed


def get_iv(unique_iv: str) -> bytes:
   """
   Converts the initialization vector (IV) from hex string to bytes and validates its length.

   :param unique_iv: Hexadecimal string representation of IV
   :return: IV as bytes
   :raises ValueError: If IV length is not 16 bytes
   """

   iv = bytes.fromhex(unique_iv) # Convert hex string IV to bytes

   verbose_output(f"{BackgroundColors.GREEN}DEBUG: IV size: {BackgroundColors.CYAN}{len(iv)} bytes{Style.RESET_ALL}")
   verbose_output(f"{BackgroundColors.GREEN}DEBUG: IV (hex): {BackgroundColors.CYAN}{iv.hex()}{Style.RESET_ALL}")

   if len(iv) != 16: # Validate IV length for AES (must be 16 bytes)
      raise ValueError(f"Invalid IV length: {len(iv)}")

   return iv # Return the IV as bytes


def derive_key(kdf_rounds: int, salt: str, passphrase: str) -> bytes:
   """
   Derives a cryptographic key from the passphrase using PBKDF2 HMAC-SHA1.

   :param kdf_rounds: Number of iterations for the key derivation function
   :param salt: Salt value to add randomness, as string
   :param passphrase: Passphrase string used to derive the key
   :return: Derived key bytes
   """

   kdf = PBKDF2HMAC( # Setup the KDF with given parameters
      algorithm=hashes.SHA1(), # Use SHA1 as the hashing algorithm
      length=32, # Key length of 32 bytes (256 bits)
      salt=salt.encode(), # Encode the salt string to bytes
      iterations=kdf_rounds, # Use the specified number of iterations
      backend=default_backend() # Use the default cryptographic backend
   )

   key = kdf.derive(passphrase.encode()) # Derive the key bytes from passphrase

   verbose_output(f"{BackgroundColors.GREEN}DEBUG: Derived key (hex): {BackgroundColors.CYAN}{key.hex()}{Style.RESET_ALL}")
   verbose_output(f"{BackgroundColors.GREEN}DEBUG: Key length: {BackgroundColors.CYAN}{len(key)} bytes{Style.RESET_ALL}")

   return key # Return the derived key bytes


def decrypt_data(encrypted_seed: bytes, key: bytes, iv: bytes) -> bytes:
   """
   Decrypts the encrypted seed bytes using AES CBC mode with the derived key and IV.

   :param encrypted_seed: The encrypted data as bytes
   :param key: The AES key bytes
   :param iv: The AES initialization vector bytes
   :return: Decrypted data bytes (including padding)
   """

   cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend()) # Create AES cipher in CBC mode

   decryptor = cipher.decryptor() # Create decryptor from cipher

   decrypted_data = decryptor.update(encrypted_seed) + decryptor.finalize() # Decrypt data (including padding)

   verbose_output(f"{BackgroundColors.GREEN}DEBUG: Decrypted data size: {BackgroundColors.CYAN}{len(decrypted_data)} bytes{Style.RESET_ALL}")
   verbose_output(f"{BackgroundColors.GREEN}DEBUG: Decrypted data (hex): {BackgroundColors.CYAN}{decrypted_data.hex()}{Style.RESET_ALL}")

   return decrypted_data # Return the decrypted data bytes (including padding)


def remove_padding(decrypted_data: bytes) -> bytes:
   """
   Removes PKCS#7 padding from decrypted data.

   :param decrypted_data: Decrypted bytes with padding
   :return: Decrypted bytes without padding
   :raises ValueError: If padding is invalid
   """

   padding_len = decrypted_data[-1] # Last byte indicates padding length (PKCS#7 standard)
   padding_start = len(decrypted_data) - padding_len # Calculate start index of padding

   verbose_output(f"{BackgroundColors.GREEN}DEBUG: Padding length: {BackgroundColors.CYAN}{padding_len}{Style.RESET_ALL}")

   if padding_len > 16 or padding_start < 0: # Validate padding length sanity
      raise ValueError("Invalid padding length")

   padding_bytes = decrypted_data[padding_start:] # Extract padding bytes

   if not all(pad == padding_len for pad in padding_bytes): # Verify all padding bytes have the same value (PKCS#7 standard)
      raise ValueError("Invalid padding bytes")

   decrypted_seed_without_padding = decrypted_data[:padding_start] # Remove padding from decrypted data

   verbose_output(f"{BackgroundColors.GREEN}DEBUG: Data without padding: {BackgroundColors.CYAN}{decrypted_seed_without_padding.hex()}{Style.RESET_ALL}")

   return decrypted_seed_without_padding # Return decrypted data without padding


def decode_decrypted_seed(decrypted_seed_without_padding: bytes) -> str:
   """
   Attempts to decode decrypted seed bytes to a meaningful string representation.

   :param decrypted_seed_without_padding: Decrypted bytes after padding removal
   :return: Decoded string (base32 uppercase, ASCII, or hex)
   """

   try: # Attempt to decode as UTF-8
      utf8_result = decrypted_seed_without_padding.decode("utf-8") # Decode bytes to UTF-8 string

      verbose_output(f'{BackgroundColors.GREEN}DEBUG: Successfully decoded as UTF-8: {BackgroundColors.CYAN}"{utf8_result}"{Style.RESET_ALL}')

      if re.match(r"^[A-Z2-7=]+$", utf8_result.upper().replace(" ", "")): # Check if string matches base32 charset; return uppercase without spaces if yes
         return utf8_result.upper().replace(" ", "") # Remove spaces and return uppercase base32 string

      return utf8_result # Otherwise return decoded UTF-8 string as is

   except UnicodeDecodeError as e: # Warning: UTF-8 decode failed
      verbose_output(f"{BackgroundColors.YELLOW}DEBUG: UTF-8 decode failed: {BackgroundColors.CYAN}{e}{Style.RESET_ALL}")

   ascii_chars = [chr(b) for b in decrypted_seed_without_padding if 32 <= b <= 126] # Extract printable ASCII characters (32-126)
   ascii_string = "".join(ascii_chars) # Join characters to form ASCII string

   verbose_output(f'{BackgroundColors.GREEN}DEBUG: Extracted ASCII string: {BackgroundColors.CYAN}"{ascii_string}"{Style.RESET_ALL}')

   base32_match = re.search(r"[A-Z2-7=]{10,}", ascii_string.upper()) # Search for base32 pattern in uppercase ASCII string
   if base32_match: # If a valid base32 pattern is found
      return base32_match.group() # Return the matched base32 string

   if len(ascii_string) >= 8: # If ASCII string is long enough, return it as is
      return ascii_string # Otherwise, return hex uppercase representation

   return decrypted_seed_without_padding.hex().upper() # Otherwise, return hex uppercase representation


def decrypt_token(kdf_rounds: int, encrypted_seed_b64: str, salt: str, passphrase: str, unique_iv: str) -> str:
   """
   Decrypts the authenticator token using the provided parameters.

   :param kdf_rounds: Number of key derivation iterations
   :param encrypted_seed_b64: Base64 encoded encrypted seed
   :param salt: Salt used for key derivation
   :param passphrase: Passphrase for decryption
   :param unique_iv: Unique initialization vector for decryption
   :return: Decrypted seed as a string, or error message on failure
   """

   verbose_output(f"{BackgroundColors.GREEN}DEBUG: Starting decryption process of the token {BackgroundColors.CYAN}{encrypted_seed_b64}{Style.RESET_ALL}")

   try: # Attempt to decrypt the token
      verbose_output(f"{BackgroundColors.GREEN}DEBUG: Starting token decryption{Style.RESET_ALL}")
      verbose_output(f"{BackgroundColors.GREEN}DEBUG: KDF rounds: {BackgroundColors.CYAN}{kdf_rounds}{Style.RESET_ALL}")
      verbose_output(f"{BackgroundColors.GREEN}DEBUG: Salt: {BackgroundColors.CYAN}{salt}{Style.RESET_ALL}")
      verbose_output(f"{BackgroundColors.GREEN}DEBUG: Unique IV: {BackgroundColors.CYAN}{unique_iv}{Style.RESET_ALL}")
      verbose_output(f"{BackgroundColors.GREEN}DEBUG: Passphrase length: {BackgroundColors.CYAN}{len(passphrase)} characters{Style.RESET_ALL}")

      # Perform each step in the decryption process
      encrypted_seed = decode_base64_seed(encrypted_seed_b64) # Decode the Base64-encoded encrypted seed
      iv = get_iv(unique_iv) # Get the initialization vector from the unique IV string
      key = derive_key(kdf_rounds, salt, passphrase) # Derive the AES key using PBKDF2 HMAC-SHA1 with the provided parameters
      decrypted_data = decrypt_data(encrypted_seed, key, iv) # Decrypt the encrypted seed using AES CBC mode with the derived key and IV
      decrypted_seed_without_padding = remove_padding(decrypted_data) # Remove PKCS#7 padding from the decrypted data
      return decode_decrypted_seed(decrypted_seed_without_padding) # Decode the decrypted seed bytes to a meaningful string representation

   except Exception as e: # Catch any exceptions during the decryption process
      import traceback # Import traceback for detailed error information
      print(f"{BackgroundColors.RED}ERROR: Decryption failed with exception: {type(e).__name__}: {str(e)}{Style.RESET_ALL}")
      traceback.print_exc() # Print the traceback for debugging
      return f"Decryption failed: {str(e)}" # Return an error message indicating decryption failure


def decrypt_all_tokens(tokens: list, backup_password: str) -> list:
   """
   Decrypts each token in the tokens list using the provided backup password.

   :param tokens: List of token dictionaries
   :param backup_password: Password to use for decryption
   :return: List of decrypted token dictionaries
   """

   decrypted_tokens = [] # Initialize an empty list to store decrypted tokens

   for i, token in enumerate(tokens): # Iterate over each token in the list
      verbose_output(f"\n{BackgroundColors.GREEN}DEBUG: Token {i+1} data: {BackgroundColors.CYAN}{json.dumps(token, indent=4)}{Style.RESET_ALL}")

      unique_iv = token.get("unique_iv", "00000000000000000000000000000000") # Use default IV if not present

      decrypted_seed = decrypt_token( # Decrypt token seed
         kdf_rounds=token["key_derivation_iterations"], # Number of key derivation iterations
         encrypted_seed_b64=token["encrypted_seed"], # Base64 encoded encrypted seed
         salt=token["salt"], # Salt used for key derivation
         passphrase=backup_password, # Use the backup password for decryption
         unique_iv=unique_iv # Unique initialization vector for decryption
      )

      decrypted_tokens.append({ # Append decrypted token info
         "account_type": token["account_type"], # Account type of the token
         "name": token["name"], # Name of the token
         "issuer": token["issuer"], # Issuer of the token
         "decrypted_seed": decrypted_seed, # Decrypted seed value
         "digits": token["digits"], # Number of digits in the token
         "logo": token["logo"], # Logo URL of the token
         "unique_id": token["unique_id"] # Unique identifier of the token
      })

   return decrypted_tokens # Return the list of decrypted token dictionaries


def write_decrypted_tokens(output_file: str, decrypted_tokens: list) -> None:
   """
   Writes the decrypted tokens data to the specified output JSON file.

   :param output_file: Path to output JSON file
   :param decrypted_tokens: List of decrypted token dictionaries
   """

   output_data = { # Main output structure
      "message": "success",
      "decrypted_authenticator_tokens": decrypted_tokens,
      "success": True
   }

   verbose_output(f"{BackgroundColors.GREEN}DEBUG: Output file: {BackgroundColors.CYAN}{output_file}{Style.RESET_ALL}")

   with open(output_file, "w") as output_json_file: # Open the output JSON file for writing
      json.dump(output_data, output_json_file, indent=4) # Write the output data as formatted JSON

   verbose_output(f"{BackgroundColors.GREEN}DEBUG: Successfully wrote decrypted tokens to {BackgroundColors.CYAN}{output_file}{Style.RESET_ALL}")


def process_authenticator_data(input_file: str, output_file: str, backup_password: str) -> None:
   """
   Processes the input JSON file, decrypts the tokens, and writes the output to a new JSON file.

   :param input_file: Path to the input JSON file containing encrypted tokens
   :param output_file: Path to the output JSON file to save decrypted tokens
   :param backup_password: Backup password for decryption
   :return: None
   """

   verbose_output(f"{BackgroundColors.GREEN}Processing authenticator data...{Style.RESET_ALL}")

   try: # Attempt to load the input JSON data
      data = load_authenticator_data(input_file) # Load input JSON and verify 'authenticator_tokens' key
   except FileNotFoundError as e: # If input file not found
      print(f"{BackgroundColors.RED}ERROR: Input file not found: {str(e)}{Style.RESET_ALL}")
      return
   except json.JSONDecodeError as e: # If JSON decoding fails
      print(f"{BackgroundColors.RED}ERROR: Invalid JSON format: {str(e)}{Style.RESET_ALL}")
      return
   except KeyError as e: # If 'authenticator_tokens' key is missing
      print(f"{BackgroundColors.RED}ERROR: {str(e)}{Style.RESET_ALL}")
      return
   except Exception as e: # Catch any other exceptions
      print(f"{BackgroundColors.RED}ERROR: Failed to load input: {str(e)}{Style.RESET_ALL}")
      return

   try: # Attempt to decrypt all tokens using the provided backup password
      decrypted_tokens = decrypt_all_tokens(data["authenticator_tokens"], backup_password) # Decrypt all tokens using the provided backup password
   except Exception as e: # If decryption fails
      print(f"{BackgroundColors.RED}ERROR: Failed during decryption: {str(e)}{Style.RESET_ALL}")
      return

   try: # Attempt to write the decrypted tokens to the output file
      write_decrypted_tokens(output_file, decrypted_tokens) # Write decrypted tokens to output file
   except Exception as e: # If writing to output file fails
      print(f"{BackgroundColors.RED}ERROR: Failed to write output: {str(e)}{Style.RESET_ALL}")


def main():
   """
   Main function to run the authenticator token decryption process.

   :return: None
   """

   print(f"{BackgroundColors.BOLD}{BackgroundColors.GREEN}Welcome to the {BackgroundColors.CYAN}Authenticator Token Decryptor{BackgroundColors.GREEN} Program!{Style.RESET_ALL}", end="\n\n") # Output the Welcome message

   load_dotenv() # Load environment variables from .env file

   input_file = "authenticator_tokens.json" # Input file containing encrypted tokens
   output_file = "decrypted_tokens.json" # Output file to save decrypted tokens

   backup_password = os.getenv("BACKUP_PASSWORD") # Get the backup password from environment variable
   if not backup_password: # If the backup password is not set in the environment variable
      backup_password = getpass("The BACKUP_PASSWORD environment variable is not set. Please enter the backup password: ") # Prompt the user to enter the backup password

   process_authenticator_data(input_file, output_file, backup_password) # Process and decrypt tokens

   print(f"{BackgroundColors.BOLD}{BackgroundColors.CYAN}Authenticator Token Decryption{BackgroundColors.GREEN} program completed.{Style.RESET_ALL}", end="\n\n") # Output the end of the program message


if __name__ == "__main__":
   """
   This is the standard boilerplate that calls the main() function.

   :return: None
   """

   main() # Call the main function
