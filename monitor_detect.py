#!/usr/bin/env python3
""" 
Names: Bwalya Maele(bgmloop), Ananias Mayes(amayes24)
Monitoring/Detection and Mitigation Scripts
This script monitors file system activity to detect and prevent ransomware attacks.
It employs countermeasures and uses entropy analysis to identify dubious encryption activity.

NOTE: This is only for security research education. 
"""


# Import required libraries
import os                               # Operating system interface
import sqlite3                          # Database interface
import datetime                         # Date and time manipulation
import math                             # Mathematical functions
import subprocess                       # Subprocess management
import signal                           # Signal handling
import smtplib                          # SMTP client for email
import shutil                           # High-level file operations
import threading                        # Thread-based parallelism
import time                             # Time access and conversions
import logging                          # Logging facility for Python
from email.message import EmailMessage # Email message handling
from watchdog.observers import Observer # File system monitoring
from watchdog.events import FileSystemEventHandler # File system event handling

# === Configuration Section ===
# These variables configure the monitoring behavior

# Directory path to monitor for suspicious activity
WATCH_PATH = "/home/kali/personal_1000"

# Administrator email address for security alerts
ADMIN_EMAIL = "admin@localhost"

# Use local SMTP server for email notifications
USE_LOCAL_SMTP = True

# SMTP server configuration (if not using local)
SMTP_SERVER = "smtp.example.com"
SMTP_PORT = 587
SMTP_USER = ""
SMTP_PASS = ""

# Whitelist of command substrings to ignore (prevent false positives)
# Add legitimate system processes here to avoid suspension
WHITELIST_CMDS = []  # Example: ["sshd", "systemd", "cron"]

# Action to take when suspicious activity detected
# "stop" sends SIGSTOP to pause process, "kill" sends SIGKILL to terminate
SUSPEND_ACTION = "stop"

# Maximum file size to read for entropy calculation (1MB)
# Prevents performance issues with large files
ENTROPY_READ_LIMIT = 1024 * 1024

# === Logging Configuration ===
# Setup both file logging and database logging for security events

# Configure file-based logging with timestamps
logging.basicConfig(
    filename="monitor_detect.log",           # Log file name
    level=logging.INFO,                      # Log level
    format="%(asctime)s %(levelname)s %(message)s"  # Log format
)

# === SQLite Database Setup ===
# Create database connection for persistent event logging
conn = sqlite3.connect('access_log.db', check_same_thread=False)
cursor = conn.cursor()

# Create table for storing security events
cursor.execute('''
CREATE TABLE IF NOT EXISTS access_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT,
    event_type TEXT,
    file_path TEXT,
    alert TEXT
)
''')
conn.commit()

# === Entropy Calculation Functions ===
# These functions analyze file randomness to detect encryption

def calculate_entropy(data: bytes) -> float:
    """
    Calculate the Shannon entropy of a byte sequence.
    High entropy indicates random data typical of encrypted files.
    
    Args:
        data (bytes): Byte data to analyze
        
    Returns:
        float: Entropy value between 0.0 and 8.0
    """
    # Handle empty data case
    if not data:
        return 0.0
    
    # Get length of data for probability calculations
    length = len(data)
    
    # Count frequency of each byte value
    counts = {}
    for b in data:
        counts[b] = counts.get(b, 0) + 1
    
    # Calculate Shannon entropy
    entropy = 0.0
    for count in counts.values():
        # Calculate probability of byte value
        p_x = count / length
        
        # Add to entropy (negative because log2 of probability is negative)
        entropy -= p_x * math.log2(p_x)
    
    return entropy

def is_encrypted(file_path: str) -> bool:
    """
    Determine if a file appears to be encrypted based on entropy analysis.
    Encrypted files typically have entropy > 7.5 due to high randomness.
    
    Args:
        file_path (str): Path to file to analyze
        
    Returns:
        bool: True if file appears encrypted, False otherwise
    """
    try:
        # Open file in binary mode for reading
        with open(file_path, 'rb') as f:
            # Read limited amount of data to prevent performance issues
            data = f.read(ENTROPY_READ_LIMIT)
            
            # Calculate entropy of file content
            entropy = calculate_entropy(data)
            
            # Log entropy for debugging purposes
            logging.debug(f"Entropy for {file_path}: {entropy:.3f}")
            
            # Return True if entropy indicates encryption (threshold: 7.5)
            return entropy > 7.5
    except Exception as e:
        # Log any errors during file reading
        logging.debug(f"Could not read {file_path} for entropy: {e}")
        return False

# === Event Logging Function ===
# Store security events in both file log and database

def log_event(event_type: str, file_path: str, alert: str = None):
    """
    Log security events to both file and database.
    
    Args:
        event_type (str): Type of event (MODIFIED, CREATED, DELETED)
        file_path (str): Path of affected file
        alert (str): Alert message if security event detected
        
    Returns:
        None
    """
    # Get current timestamp in ISO format
    timestamp = datetime.datetime.now().isoformat()
    
    # Insert event into database
    cursor.execute('''
        INSERT INTO access_events (timestamp, event_type, file_path, alert)
        VALUES (?, ?, ?, ?)
    ''', (timestamp, event_type, file_path, alert))
    conn.commit()
    
    # Also log to file for immediate monitoring
    logging.info(f"{event_type} {file_path} {alert or ''}")

# === Process Management Functions ===
# Handle identification and control of suspicious processes

def get_cmdline(pid: int) -> str:
    """
    Get the command line of a process from /proc filesystem.
    
    Args:
        pid (int): Process ID
        
    Returns:
        str: Command line of process or empty string if error
    """
    try:
        # Read command line from /proc filesystem
        with open(f"/proc/{pid}/cmdline", "rb") as f:
            # Replace null bytes with spaces and strip whitespace
            raw = f.read().replace(b'\x00', b' ').strip()
            return raw.decode(errors="ignore")
    except Exception:
        # Return empty string if unable to read
        return ""

def kill_process_using_file(file_path: str, action: str = "stop") -> list:
    """
    Identify and suspend processes that are accessing a specific file.
    This is a mitigation technique to stop encryption in progress.
    
    Args:
        file_path (str): Path to file being accessed
        action (str): Action to take ("stop" or "kill")
        
    Returns:
        list: List of suspended process IDs
    """
    # List to store suspended process IDs
    suspended = []
    
    try:
        # Use lsof to find processes using the file (get PIDs only)
        output = subprocess.check_output(
            ['lsof', '-t', file_path], 
            stderr=subprocess.DEVNULL
        ).decode().strip()
        
        # Handle case where no processes are found
        if not output:
            return suspended
        
        # Process each PID found by lsof
        for line in output.splitlines():
            try:
                # Convert line to integer PID
                pid = int(line.strip())
            except ValueError:
                # Skip invalid PIDs
                continue
            
            # Skip our own process to avoid self-termination
            if pid == os.getpid():
                continue
            
            # Get process command line for whitelist checking
            cmd = get_cmdline(pid)
            
            # Check if process is in whitelist (should not be suspended)
            if any(w in cmd for w in WHITELIST_CMDS):
                logging.info(f"Skipping whitelisted process {pid} ({cmd})")
                continue
            
            # Determine signal based on action parameter
            sig = signal.SIGSTOP if action == "stop" else signal.SIGKILL
            
            try:
                # Send signal to process
                os.kill(pid, sig)
                suspended.append(pid)
                logging.info(f"Signaled {pid} ({cmd}) with {sig}")
            except PermissionError:
                # Handle insufficient privileges
                logging.error(f"Permission denied signaling pid {pid}")
            except ProcessLookupError:
                # Handle case where process disappeared
                logging.warning(f"Process {pid} disappeared before signaling")
    except subprocess.CalledProcessError:
        # Handle case where lsof returns no processes
        logging.debug("lsof returned no processes for file")
    except FileNotFoundError:
        # Handle missing lsof command
        logging.error("lsof not installed; install lsof to enable process lookup")
    except Exception as e:
        # Handle any other unexpected errors
        logging.exception(f"Unexpected error in kill_process_using_file: {e}")
    
    return suspended

# === Notification Functions ===
# Alert administrators about security events

def send_notification(file_path: str, pids: list):
    """
    Send security alert notification via desktop notification and email.
    
    Args:
        file_path (str): Path to affected file
        pids (list): List of suspended process IDs
        
    Returns:
        None
    """
    # Create notification content
    title = "Security Alert"
    body = f"Suspicious encryption detected on {file_path}\nSuspended PIDs: {pids or 'none'}"
    
    # Try desktop notification first (Linux only)
    if shutil.which("notify-send"):
        try:
            # Send desktop notification
            subprocess.run(
                ["notify-send", title, body], 
                check=False
            )
            logging.info("Desktop notification sent")
            return
        except Exception as e:
            # Log desktop notification errors
            logging.error(f"notify-send failed: {e}")
    
    # Fallback to email notification
    try:
        # Create email message
        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = 'Security Alert: Possible Keylogger Activity'
        msg['From'] = f"monitor@{os.uname().nodename}"  # Use system hostname
        msg['To'] = ADMIN_EMAIL
        
        # Send email via appropriate SMTP server
        if USE_LOCAL_SMTP:
            # Use local SMTP server
            with smtplib.SMTP('localhost') as server:
                server.send_message(msg)
        else:
            # Use external SMTP server with authentication
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()  # Enable encryption
                if SMTP_USER and SMTP_PASS:
                    server.login(SMTP_USER, SMTP_PASS)  # Authenticate
                server.send_message(msg)
        
        logging.info("Email notification sent")
    except Exception as e:
        # Log any email sending errors
        logging.exception(f"Failed to send email notification: {e}")

# === File System Event Handler ===
# This class handles file system events detected by watchdog

class MonitorHandler(FileSystemEventHandler):
    """
    Custom event handler for monitoring file system changes.
    Detects suspicious encryption activity and triggers mitigation.
    """
    
    def on_modified(self, event):
        """
        Handle file modification events.
        This is where the main detection logic resides.
        
        Args:
            event: File system event object from watchdog
            
        Returns:
            None
        """
        # Skip directory events (only monitor files)
        if event.is_directory:
            return
        
        # Get the path of the modified file
        file_path = event.src_path
        
        # Analyze file for encryption signatures
        if is_encrypted(file_path):
            # Construct alert message
            alert_text = "ALERT: Possible encryption attempt"
            
            # Log the security event
            log_event('MODIFIED', file_path, alert_text)
            
            # Display alert in console
            print(f"[ALERT] Suspicious encryption detected: {file_path}")
            logging.warning(f"Suspicious encryption detected: {file_path}")
            
            # Define alert handling function for separate thread
            def handle_alert(fp):
                # Warn if not running as root (process suspension requires privileges)
                if os.geteuid() != 0:
                    logging.warning(
                        "Not running as root; cannot suspend processes. " +
                        "Notification will still be sent."
                    )
                
                # Attempt to suspend processes accessing the file
                pids = kill_process_using_file(fp, action=SUSPEND_ACTION)
                
                # Send notification to administrator
                send_notification(fp, pids)
            
            # Run alert handling in separate thread to avoid blocking
            threading.Thread(
                target=handle_alert, 
                args=(file_path,), 
                daemon=True
            ).start()
        else:
            # Log normal file modifications
            log_event('MODIFIED', file_path)

# === Monitoring Control Functions ===
# Start and control the file system monitoring process

def start_monitoring(path_to_watch: str):
    """
    Start monitoring a directory for suspicious file activity.
    
    Args:
        path_to_watch (str): Directory path to monitor
        
    Returns:
        None
    """
    # Create watch directory if it doesn't exist
    if not os.path.exists(path_to_watch):
        os.makedirs(path_to_watch, exist_ok=True)
        logging.info(f"Created missing watch directory: {path_to_watch}")
    
    # Create event handler and observer
    event_handler = MonitorHandler()
    observer = Observer()
    
    # Schedule observer to watch directory recursively
    observer.schedule(
        event_handler, 
        path=path_to_watch, 
        recursive=True
    )
    
    # Start the observer
    observer.start()
    print(f"Monitoring started on: {path_to_watch}")
    logging.info(f"Monitoring started on: {path_to_watch}")
    
    # Keep monitoring until interrupted
    try:
        while True:
            time.sleep(1)  # Sleep to prevent high CPU usage
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        observer.stop()
    
    # Wait for observer to finish
    observer.join()

# === Main Execution ===
# Start the monitoring system when script is run directly

if __name__ == "__main__":
    # Start monitoring the configured directory
    start_monitoring(WATCH_PATH)
