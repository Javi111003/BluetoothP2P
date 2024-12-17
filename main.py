import os  # To work with the file system
import time  # To handle wait times
from watchdog.observers import Observer  # Observer to monitor changes in directories
from watchdog.events import FileSystemEventHandler  # Event handler for file changes

# Configuration of the synchronization folder
SYNC_FOLDER = "./sync_folder"  # Path to the local folder for synchronization
os.makedirs(SYNC_FOLDER, exist_ok=True)  # Creates the folder if it does not exist

print(f"Synchronization folder configured: {SYNC_FOLDER}")
