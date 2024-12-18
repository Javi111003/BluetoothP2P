import os  # To work with the file system
import time  # To handle wait times
from watchdog.observers import Observer  # Observer to monitor changes in directories
from watchdog.events import FileSystemEventHandler  # Event handler for file changes

# Configuration of the synchronization folder
SYNC_FOLDER = "./sync_folder"  # Path to the local folder for synchronization
os.makedirs(SYNC_FOLDER, exist_ok=True)  # Creates the folder if it does not exist
class SyncHandler(FileSystemEventHandler):
    
    def __init__(self, send_change):
        self.send_change = send_change 

    def on_any_event(self, event):
        if event.is_directory:  
            return
        self.send_change(event)  

def send_change(event):
    print(f"Cambio detectado: {event.event_type} en {event.src_path}")

observer = Observer() 
observer.schedule(SyncHandler(send_change), SYNC_FOLDER, recursive=True)
observer.start() 

try:
    print(f"Sincronizando carpeta: {SYNC_FOLDER}")
    while True:
        time.sleep(1)  
except KeyboardInterrupt:
    print("Finalizando sincronización...")
    observer.stop() 
    observer.join() 