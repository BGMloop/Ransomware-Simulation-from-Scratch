#!/usr/bin/env python3
""" 
 Component for File Decryption
 This script shows how to decrypt files that have been encrypted by the ransomware simulation.
 
 NOTICE: Only in controlled settings for educational purposes. 
 """

from cryptography.fernet import Fernet  # Symmetric encryption library
import os                               # Operating system interface
import sys                              # System-specific parameters and functions

def load_key():
    """
    Load the encryption key from the secret.key file.
    This key is required to decrypt the encrypted files.
    
    Returns:
        bytes: The encryption key
    """
    try:
        # Attempt to open and read the encryption key file
        return open("secret.key", "rb").read()
    except FileNotFoundError:
        # If key file doesn't exist, inform user and exit
        print("[-] secret.key not found! Make sure it's in the same folder.")
        sys.exit(1)

def decrypt_file(file_path, fernet):
    """
    Decrypt a single encrypted file using the Fernet decryption object.
    
    Args:
        file_path (str): Path to the file to be decrypted
        fernet (Fernet): Initialized Fernet decryption object
    
    Returns:
        None
    """
    # Only process files with .encrypted extension
    if not file_path.endswith(".encrypted"):
        return
         
    try:
        # Read the encrypted file content
        with open(file_path, "rb") as enc_file:
            encrypted_data = enc_file.read()
         
        # Decrypt the data using the Fernet key
        decrypted = fernet.decrypt(encrypted_data)
        
        # Create original filename by removing .encrypted extension
        decrypted_path = file_path.replace(".encrypted", "")
         
        # Write the decrypted data to the original filename
        with open(decrypted_path, "wb") as dec_file:
            dec_file.write(decrypted)
             
        # Remove the encrypted file
        os.remove(file_path)
        print(f"[+] Decrypted: {file_path} → {decrypted_path}")
    except Exception as e:
        # Handle any decryption errors
        print(f"[-] Failed to decrypt {file_path}: {e}")

def decrypt_directory(directory):
    """
    Recursively decrypt all encrypted files in a directory.
    
    Args:
        directory (str): Path to the directory to decrypt
    
    Returns:
        None
    """
    # Load the decryption key
    key = load_key()
    
    # Initialize the Fernet decryption object with the key
    f = Fernet(key)
     
    # Walk through the directory tree
    for root, dirs, files in os.walk(directory):
        # Process each file in the current directory
        for name in files:
            file_path = os.path.join(root, name)
            decrypt_file(file_path, f)

def main():
    """
    Main function to handle command-line arguments and execute decryption.
    """
    # Check if user provided any arguments
    if len(sys.argv) < 2:
        # Display usage instructions if no arguments provided
        print("Usage:")
        print("  python3 decrypt.py <file_or_folder>")
        sys.exit(1)
         
    # Get the target for decryption
    target = sys.argv[1]
    
    # Verify that the target exists
    if not os.path.exists(target):
        print("[-] Target not found!")
        sys.exit(1)
         
    # Determine if target is directory or file and decrypt accordingly
    if os.path.isdir(target):
        print(f"[+] Decrypting directory: {target}")
        decrypt_directory(target)
    else:
        # Decrypt single file
        key = load_key()
        f = Fernet(key)
        decrypt_file(target, f)

# Execute main function when script is run directly
if __name__ == "__main__":
    main()
