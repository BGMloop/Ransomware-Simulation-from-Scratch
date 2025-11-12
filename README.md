# CSCE 5550 Final Project: Detection and Simulation of Ransomware

## Notice of Academic Project** This project is solely intended for educational purposes.  
Every component is made to be tested and studied in a controlled environment.  
Unauthorized use is forbidden.

## Overview of the Project
The ransomware component and detection mechanism simulation tools created for the CSCE 5550 Cybersecurity course are available in this repository.
The project illustrates:
The use of Keyloggers to prevent the spread of infections
Simulations of Ransomware Infection Component, Encrypt/Decrypt, Monitoring/Detection, Miitigation scripts.

 ## Important Information
 For testing, all scripts need express authorization.  
 Use only on authorized systems.

## Instructions for Setup

 ### 1. Configuring the Environment

 # Establish and turn on a virtual environment
 cd ~/csce5550_env 
 source ~/csce5550_env/bin/activate

## Install the necessary packages
 pip install -r requirements.txt

## Create an Encryption Key  
 Python 3 encrypt.py --genkey

## Get Test Files Ready
 mkdir -p ~/personal_1000
 echo "This is a confidential document" > ~/personal_1000/document1.txt
 echo "Secret financial information" > ~/personal_1000/financial_data.txt
 echo "Personal photos list" > ~/personal_1000/photos_list.txt

 ### Usage Guidelines

## Keylogger Testing 
sudo python3 keylogger.py
# To stop logging, press ESC. 

# Look for keystrokes that were recorded in 
infection_keylog.txt.

## Building Infection Components 
ransomware_infect.py 
# In Python 3 choose option 3 for the malicious file

## Performing a Document-Based Attack
./malicious_document.sh

## Encryption/Decryption
# Encrypt files
python3 encrypt.py ~/personal_1000

## Decrypt files
python3 decrypt.py ~/personal_1000

## Monitoring System
python3 monitor_detect.py

## Requirements
Python 3.7+
cryptography library and cryptography==3.4.8
keyboard library and keyboard==0.13.5
watchdog library and watchdog==2.1.6
sudo privileges for keylogger
