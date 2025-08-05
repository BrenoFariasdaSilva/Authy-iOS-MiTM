import atexit # For playing a sound when the program finishes
import os # For running a command in the terminal
import platform # For getting the operating system name
import subprocess # For running a command in the terminal
import sys # For getting the current Python interpreter
from colorama import Style # For coloring the terminal

# Macros:
class BackgroundColors: # Colors for the terminal
   CYAN = "\033[96m" # Cyan
   GREEN = "\033[92m" # Green
   YELLOW = "\033[93m" # Yellow
   RED = "\033[91m" # Red
   BOLD = "\033[1m" # Bold
   UNDERLINE = "\033[4m" # Underline
   CLEAR_TERMINAL = "\033[H\033[J" # Clear the terminal

# Execution Constants:
VERBOSE = False # Set to True to output verbose messages

# Sound Constants:
SOUND_COMMANDS = {"Darwin": "afplay", "Linux": "aplay", "Windows": "start"} # The commands to play a sound for each operating system
SOUND_FILE = "./.assets/Sounds/NotificationSound.wav" # The path to the sound file

# RUN_FUNCTIONS:
RUN_FUNCTIONS = {
   "Play Sound": True, # Set to True to play a sound when the program finishes
}

def verbose_output(true_string="", false_string=""):
   """
   Outputs a message if the VERBOSE constant is set to True.

   :param true_string: The string to be outputted if the VERBOSE constant is set to True.
   :param false_string: The string to be outputted if the VERBOSE constant is set to False.
   :return: None
   """

   if VERBOSE and true_string != "": # If the VERBOSE constant is set to True and the true_string is set
      print(true_string) # Output the true statement string
   elif false_string != "": # If the false_string is set
      print(false_string) # Output the false statement string


def verify_filepath_exists(filepath):
   """
   Verify if a file or folder exists at the specified path.

   :param filepath: Path to the file or folder
   :return: True if the file or folder exists, False otherwise
   """

   verbose_output(f"{BackgroundColors.GREEN}Verifying if the file or folder exists at the path: {BackgroundColors.CYAN}{filepath}{Style.RESET_ALL}") # Output the verbose message

   return os.path.exists(filepath) # Return True if the file or folder exists, False otherwise


def run_script(script_name):
   """
   Runs a Python script using the current venv Python interpreter.

   :param script_name: Name of the script to run
   :return: None
   """

   verbose_output(f"{BackgroundColors.GREEN}Running script: {BackgroundColors.CYAN}{script_name}{Style.RESET_ALL}")

   try:
      result = subprocess.run([sys.executable, script_name], check=True) # Run the script using the current venv Python interpreter

   except subprocess.CalledProcessError: # If the script failed to run
      print(f"{BackgroundColors.RED}Script {BackgroundColors.CYAN}{script_name}{BackgroundColors.RED} failed to run.{Style.RESET_ALL}")
      exit(1)


def play_sound():
   """
   Plays a sound when the program finishes.

   :return: None
   """

   if verify_filepath_exists(SOUND_FILE): # If the sound file exists
      if platform.system() in SOUND_COMMANDS: # If the platform.system() is in the SOUND_COMMANDS dictionary
         os.system(f"{SOUND_COMMANDS[platform.system()]} {SOUND_FILE}") # Play the sound
      else: # If the platform.system() is not in the SOUND_COMMANDS dictionary
         print(f"{BackgroundColors.RED}The {BackgroundColors.CYAN}platform.system(){BackgroundColors.RED} is not in the {BackgroundColors.CYAN}SOUND_COMMANDS dictionary{BackgroundColors.RED}. Please add it!{Style.RESET_ALL}")
   else: # If the sound file does not exist
      print(f"{BackgroundColors.RED}Sound file {BackgroundColors.CYAN}{SOUND_FILE}{BackgroundColors.RED} not found. Make sure the file exists.{Style.RESET_ALL}")


def main():
   """
   Main function.

   :return: None
   """

   print(f"{BackgroundColors.CLEAR_TERMINAL}{BackgroundColors.BOLD}{BackgroundColors.GREEN}Welcome to the {BackgroundColors.CYAN}Authy Tokens Decryptor{BackgroundColors.GREEN} Program!{Style.RESET_ALL}", end="\n\n") # Output the Welcome message

   scripts = {"decrypt.py": False, "generate_uris.py": False, "generate_qr_codes.py": True} # Dictionary of scripts to run in order

   for script, requires_confirmation in scripts.items(): # Loop through the scripts dictionary
      if requires_confirmation: # If the script requires user confirmation
         while True: # Keep asking until the user enters a valid response
            user_input = input(f"{BackgroundColors.GREEN}Run {BackgroundColors.CYAN}{script}{BackgroundColors.GREEN}? (Y/n): ").strip().lower()
            if user_input in ["y", "yes", ""]: # Valid response for "yes"
               run_script(script) # Run the script
               break # Exit the loop after running the script
            elif user_input in ["n", "no"]: # Valid response for "no"
               print(f"{BackgroundColors.YELLOW}Skipping {script}.{Style.RESET_ALL}")
               break # Exit the loop after skipping
            else:
               print(f"{BackgroundColors.RED}Invalid input. Please enter Y, N, yes, or no.{Style.RESET_ALL}")
      else: # If the script does not require user confirmation
         run_script(script) # Run the script without user confirmation


   print(f"{BackgroundColors.BOLD}{BackgroundColors.GREEN}Authy Tokens Decryptor Program finished!{Style.RESET_ALL}") # Output the success message

   atexit.register(play_sound) if RUN_FUNCTIONS["Play Sound"] else None # Register the play_sound function to be called when the program finishes

if __name__ == "__main__":
   """
   This is the standard boilerplate that calls the main() function.

   :return: None
   """

   main() # Call the main function
