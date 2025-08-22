import json # For handling JSON data
import urllib.parse # For URL encoding
from collections import defaultdict # For counting occurrences of names
from main import BackgroundColors, Style, verbose_output # Importing necessary functions and constants from main.py

SHOW_IN_TERMINAL = False # Flag to control whether to show URIs in the terminal
CAPITALIZE_NAME = True # Flag to control whether to capitalize names in the URIs

URI_FORMATS = { # Dictionary of URI formats for different authenticator apps
   "2FA": "otpauth://totp/{name}?secret={secret}&digits={digits}&algorithm=SHA1&period=30&issuer={issuer}",
   "Aegis": "otpauth://totp/{name}?secret={secret}&digits={digits}&algorithm=SHA1&period=30&issuer={issuer}",
   "Google Authenticator": "otpauth://totp/{issuer}:{name}?secret={secret}&digits={digits}&algorithm=SHA1&period=30",
   "Microsoft Authenticator": "otpauth://totp/{issuer}:{name}?secret={secret}&digits={digits}&algorithm=SHA1&period=30",
}

def get_app_choice():
   """
   Displays available authenticator app choices and gets a valid user selection.

   :return: Selected authenticator app as a string
   """

   app_choices = ["2FA", "Aegis", "Google Authenticator", "Microsoft Authenticator"] # List of available authenticator apps
   app_choices.sort() # Sort the list alphabetically

   print(f"{BackgroundColors.GREEN}Select an authenticator app to generate URIs for:{Style.RESET_ALL}")

   for i, app in enumerate(app_choices): # Enumerate through the app choices
      print(f"{BackgroundColors.CYAN}{i + 1}. {app}.{Style.RESET_ALL}")
   
   valid_options = ", ".join(str(i + 1) for i in range(len(app_choices))) # Create a string of valid options for user input

   while True: # Loop until a valid choice is made
      try: # Attempt to get user input
         choice = int(input(f"{BackgroundColors.GREEN}Enter your choice {BackgroundColors.CYAN}({valid_options}): {Style.RESET_ALL}")) - 1 # Get user input and adjust for zero-based index
         if 0 <= choice < len(app_choices): # If the choice is within the valid range
            return app_choices[choice] # Return the selected app choice
         else: # If the choice is out of range
            print(f"{BackgroundColors.RED}Invalid choice. Please enter a number between 1 and {len(app_choices)}.{Style.RESET_ALL}")
      except ValueError:
         print(f"{BackgroundColors.RED}Invalid input. Please enter a number.{Style.RESET_ALL}")


def read_decrypted_tokens(input_file):
   """
   Reads the decrypted tokens JSON file.

   :param input_file: Path to the input JSON file
   :return: JSON data as a string
   :raises FileNotFoundError: If the file is not found
   :raises Exception: For any other read errors
   """

   with open(input_file, "r") as f: # Open the input file in read mode
      return f.read() # Read the file content and return it as a string


def convert_to_uris(json_data, app_choice):
   """
   Converts Authy-like JSON to otpauth:// URIs based on app choice.

   :param json_data: JSON data containing authenticator tokens
   :param app_choice: The choice of authenticator app
   :return: List of URIs and their corresponding names
   """

   verbose_output(f"{BackgroundColors.GREEN}Converting JSON data to URIs for app choice: {BackgroundColors.CYAN}{app_choice}{Style.RESET_ALL}") # Output the conversion message

   try: # Attempt to parse the JSON data
      data = json.loads(json_data) # Load the JSON data
      tokens = data.get("decrypted_authenticator_tokens", []) # Get the decrypted tokens from the JSON data
      uris = [] # List to store the generated URIs
      names = [] # List to store the names corresponding to the URIs

      uri_format = URI_FORMATS.get(app_choice) # Get the URI format based on the app choice

      for token in tokens: # Iterate through each token in the decrypted tokens
         name = token.get("name").replace(":", " ").replace("_", " ").strip() if token.get("name") else "" # Get the name from the token, replacing ":" and "_" with spaces and stripping whitespace
         name = " ".join(word.capitalize() for word in name.split(" ")) if CAPITALIZE_NAME else name # Capitalize each word in the name if CAPITALIZE_NAME is True
         issuer = token.get("issuer").replace("_", " ") if token.get("issuer") else "" # Replace underscores in the issuer with spaces, if issuer exists
         secret = token.get("decrypted_seed") # Get the decrypted seed from the token
         digits = token.get("digits", 6) # Get the number of digits, defaulting to 6 if not specified

         encoded_name = urllib.parse.quote(name, safe="") # URL encode the name. For example, spaces become %20
         encoded_issuer = urllib.parse.quote(issuer, safe="") # URL encode the issuer
         encoded_secret = urllib.parse.quote(secret, safe="") if secret else "" # URL encode the secret if it exists
         encoded_digits = urllib.parse.quote(str(digits), safe="") # URL encode the digits

         if name and secret and uri_format: # If name, secret, and uri_format are available
            uri = uri_format.format(name=encoded_name, issuer=encoded_issuer, secret=encoded_secret, digits=encoded_digits)
            uris.append(uri) # Append the generated URI to the list
            names.append(token.get("name")) # Append the name to the names list

      return uris, names # Return the list of URIs and names

   except json.JSONDecodeError: # If JSON decoding fails
      return ["Error: Invalid JSON input."], [] # Return an error message and an empty list
   except Exception as e: # Catch any other exceptions
      return [f"An unexpected error occurred: {e}"], [] # Return an error message and an empty list


def extract_uri_name(uri: str) -> str:
   """
   Extracts the part after "totp/" and before "?secret", and decodes URL encoding.
   removes "/", capitalizes words, and removes extra spaces.

   :param uri: The URI string to extract the name from
   :return: Decoded and cleaned name string
   """

   verbose_output(f"{BackgroundColors.GREEN}Extracting name from URI: {BackgroundColors.CYAN}{uri}{Style.RESET_ALL}") # Output the extraction message

   start = uri.find("totp/") # Find the start index of "totp/"
   if start == -1: # If "totp/" is not found in the URI
      return "Unknown" # Return "Unknown" if "totp/" is not found
   start += len("totp/") # Move the start index to the end of "totp/"

   end = uri.find("?secret", start) # Find the end index of "?secret" after the start index
   if end == -1: # If "?secret" is not found
      return "Unknown" # Return "Unknown" if "?secret" is not found

   raw_name = uri[start:end] # Extract raw name
   decoded_name = urllib.parse.unquote(raw_name) # Decode URL encoding
   cleaned_decoded = decoded_name.replace("_", " ").replace("/", " ") # Replace "_" with spaces and remove "/"
   cleaned_decoded = " ".join(cleaned_decoded.split()) # Remove extra spaces

   return cleaned_decoded # Return the cleaned and decoded name


def normalize_name(name: str) -> str:
   """
   Lowercase and remove trailing "." for comparison.

   :param name: The name string to normalize
   :return: Normalized name string
   """
   
   return name.rstrip(".").lower() # Normalize the name by removing trailing "." and converting to lowercase


def custom_sort(items):
   """
   Sorts items based on name, ensuring shorter prefixes come first.

   :param items: List of items to sort, each item should have a "name" key
   :return: None, sorts the list in place
   """

   verbose_output(f"{BackgroundColors.GREEN}Custom sorting items based on name and length...{Style.RESET_ALL}") # Output the sorting message

   items.sort(key=lambda x: normalize_name(x["name"])) # First sort alphabetically ignoring case

   for i in range(1, len(items)): # Iterate through the sorted list starting from the second item
      j = i # Initialize j to the current index
      while j > 0: # While j is greater than 0
         prev_name = normalize_name(items[j-1]["name"]) # Normalize the previous name
         curr_name = normalize_name(items[j]["name"]) # Normalize the current name

         if prev_name.startswith(curr_name) and len(prev_name) > len(curr_name): # If the previous name starts with the current name and is longer
            items[j], items[j-1] = items[j-1], items[j] # Swap the items
         else: # If the previous name does not start with the current name or is not longer
            break # Break the loop
         j -= 1 # Decrement j to continue checking previous items


def save_uris_to_json(app_choice, uri_data, output_filename):
   """
   Saves the generated URIs to a JSON file.

   :param app_choice: Selected authenticator app
   :param uri_data: Dictionary containing URIs and their names
   :param output_filename: Output file name without extension
   """

   with open(f"{output_filename}.json", "w") as uri_file: # Open the output file in write mode
      json.dump(uri_data, uri_file, indent=4) # Write the URIs data to the file with indentation for readability
      print(f"\n{BackgroundColors.GREEN}URIs in the format for {BackgroundColors.CYAN}{app_choice} App{BackgroundColors.GREEN} saved to {BackgroundColors.CYAN}{output_filename}.json{Style.RESET_ALL}") # Output success message


def save_uris_to_txt(app_choice, uri_data, output_filename):
   """
   Saves the generated URIs to a TXT file.

   :param app_choice: Selected authenticator app
   :param uri_data: Dictionary containing URIs and their names
   :param output_filename: Output file name without extension
   """

   with open(f"{output_filename}.txt", "w") as uri_txt_file: # Open the output TXT file in write mode
      for item in uri_data["URIs"]: # Loop through each URI item
         uri_txt_file.write(f"{item['uri']}\n") # Write the URI to the file
      print(f"{BackgroundColors.GREEN}URIs in the format for {BackgroundColors.CYAN}{app_choice} App{BackgroundColors.GREEN} saved to {BackgroundColors.CYAN}{output_filename}.txt{Style.RESET_ALL}", end="\n\n") # Output success message


def handle_uri_generation(json_data, app_choice, output_filename):
   """
   Generates URIs from the decrypted tokens and writes them to JSON and TXT files.

   :param json_data: JSON data containing decrypted tokens
   :param app_choice: Selected authenticator app
   :param output_filename: Output file name without extension
   """

   uris, names = convert_to_uris(json_data, app_choice) # Convert the JSON data to URIs based on the selected app choice

   if "Error" in uris[0]: # If there is an error in the URIs
      print(f"{BackgroundColors.RED}Error generating URIs:{BackgroundColors.CYAN}{uris[0]}{Style.RESET_ALL}")
      return # Exit the function if there is an error

   if SHOW_IN_TERMINAL: # If the SHOW_IN_TERMINAL flag is set to True
      for i, uri in enumerate(uris): # Loop through the URIs and print them in the terminal
         print(f"{BackgroundColors.BOLD}{i + 1}. {BackgroundColors.CYAN}{uri}{Style.RESET_ALL}")

   name_counts = defaultdict(int) # Dictionary to count occurrences of names
   unique_uri_items = [] # List to store unique URI items with names

   for uri in uris: # Loop through each URI
      name = extract_uri_name(uri) # Extract the name from the URI
      name_counts[name] += 1 # Increment the count for the name
      unique_name = f"{name} {name_counts[name]:02}" if name_counts[name] > 1 else name # If the name has duplicates, append the count to the name
      unique_uri_items.append({"name": unique_name, "uri": uri}) # Append the unique URI item to the list

   uri_data = {"URIs": unique_uri_items} # Create a dictionary to hold the URIs data
   custom_sort(uri_data["URIs"]) # Sort the URIs based on their names

   save_uris_to_json(app_choice, uri_data, output_filename) # Save the URIs to a JSON file
   save_uris_to_txt(app_choice, uri_data, output_filename) # Save the URIs to a TXT file


def main():
   """
   Main function to run generate URIs based on decrypted tokens.

   :return: None
   """

   print(f"{BackgroundColors.BOLD}{BackgroundColors.GREEN}Welcome to the {BackgroundColors.CYAN}URI Generator{BackgroundColors.GREEN} Program!{Style.RESET_ALL}", end="\n\n") # Output the Welcome message

   try: # Attempt to read the decrypted tokens from the input file
      app_choice = get_app_choice() # Get the user's choice of authenticator app
      input_file = "decrypted_tokens.json" # Input file containing decrypted tokens
      output_filename = "URIs" # Base name for output files

      json_data = read_decrypted_tokens(input_file) # Read the decrypted tokens from the input file
      handle_uri_generation(json_data, app_choice, output_filename) # Generate URIs and save them to files

   except FileNotFoundError: # If the input file is not found
      print(f"{BackgroundColors.RED}Error: {BackgroundColors.CYAN}{input_file}{BackgroundColors.RED} not found.{Style.RESET_ALL}")
   except Exception as e: # Catch any other exceptions
      print(f"{BackgroundColors.RED}An unexpected error occurred: {e}{Style.RESET_ALL}")

   print(f"{BackgroundColors.BOLD}{BackgroundColors.CYAN}Generation of URIs{BackgroundColors.GREEN} program completed.{Style.RESET_ALL}", end="\n\n")


if __name__ == "__main__":
   """
   This is the standard boilerplate that calls the main() function.

   :return: None
   """

   main() # Call the main function
