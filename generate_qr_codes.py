import json # For reading and writing JSON files
import os # For file and directory operations
import qrcode # For generating QR codes
from main import BackgroundColors, Style, verbose_output, verify_filepath_exists # Importing necessary functions and constants from main.py
from tqdm import tqdm # For displaying a progress bar

def read_uris_file(input_file: str) -> dict:
   """
   Reads and loads the URIs JSON file.

   :param input_file: Path to the JSON file containing URIs
   :return: Dictionary with URIs data
   :raises FileNotFoundError: If the file does not exist
   :raises json.JSONDecodeError: If the JSON file is invalid
   """

   with open(input_file, "r", encoding="utf-8") as f: # Open the input file in read mode
      return json.load(f) # Load the JSON data from the file


def validate_uris_data(uris_data: dict, input_file: str) -> bool:
   """
   Validates that the URIs data is not empty and contains the key "URIs".

   :param uris_data: Dictionary with URIs data
   :param input_file: Path to the input file (for error messages)
   :return: True if valid, False otherwise
   """

   if not uris_data or "URIs" not in uris_data: # Check if the data is empty or does not contain "URIs"
      print(f"{BackgroundColors.RED}ERROR: No 'URIs' key found in {BackgroundColors.CYAN}{input_file}{BackgroundColors.RED}. Please check the file format.{Style.RESET_ALL}")
      return False # Output error message if validation fails
   return True # Return True if the data is valid


def create_output_folder(folder_name: str):
   """
   Creates the output folder if it does not already exist.

   :param folder_name: Name of the folder to create
   """

   if not verify_filepath_exists(folder_name): # Check if the folder does not exist
      os.makedirs(folder_name) # Create the folder if it does not exist


def generate_qr_code(uri, filename):
   """
   Generates a QR code from a URI and saves it to a file.

   :param uri: The URI to encode in the QR code
   :param filename: The name of the file to save the QR code image
   :return: None
   """

   verbose_output(f"{BackgroundColors.GREEN}Generating QR code for URI: {BackgroundColors.CYAN}{uri}{Style.RESET_ALL}") # Output the verbose message
   
   img = qrcode.make(uri) # Generate QR code
   img.save(filename) # Save the QR code image to the specified file


def generate_qr_codes_for_uris(uris_data: dict, folder_name: str):
   """
   Iterates through URIs and generates QR codes for each one.

   :param uris_data: Dictionary containing the URIs
   :param folder_name: Name of the folder to save QR codes
   """

   for item in tqdm(uris_data["URIs"], desc=f"{BackgroundColors.CYAN}Generating QR Codes{BackgroundColors.GREEN}", unit="QR"): # Loop through each URI in the data
      name = item["name"].rstrip(".") # Get the name for the QR code and remove trailing dot
      uri = item["uri"] # Get the URI to encode in the QR code
      filename = os.path.join(folder_name, f"{name}.png") # Construct filename
      generate_qr_code(uri, filename) # Generate and save the QR code


def main():
   """
   Main function to generate QR codes from URIs.

   :return: None
   """

   print(f"{BackgroundColors.BOLD}{BackgroundColors.GREEN}Welcome to the {BackgroundColors.CYAN}QR Code Generator{BackgroundColors.GREEN} Program!{Style.RESET_ALL}", end="\n\n") # Output the Welcome message

   input_file = "URIs.json" # Input file containing URIs
   folder_name = "Generated QR Codes" # Folder to save the generated QR codes

   try: # Attempt to read the URIs from the input file
      uris_data = read_uris_file(input_file) # Read the URIs from the input file

      if not validate_uris_data(uris_data, input_file): # If the URIs data is invalid
         return # Exit if the JSON structure is invalid

      create_output_folder(folder_name) # Create the output folder if it does not exist
      generate_qr_codes_for_uris(uris_data, folder_name) # Generate QR codes for the URIs

   except FileNotFoundError: # If the input file does not exist
      print(f"{BackgroundColors.RED}ERROR: {BackgroundColors.CYAN}{input_file}{BackgroundColors.RED} not found. Please ensure the file exists.{Style.RESET_ALL}")
   except Exception as e: # Catch any other exceptions
      print(f"{BackgroundColors.RED}ERROR: An unexpected error occurred: {str(e)}{Style.RESET_ALL}")

   print(f"\n{BackgroundColors.BOLD}{BackgroundColors.CYAN}QR Code Generation{BackgroundColors.GREEN} program completed!{Style.RESET_ALL}", end="\n\n") # Output completion message


if __name__ == "__main__":
   """
   This is the standard boilerplate that calls the main() function.

   :return: None
   """

   main() # Call the main function
