import os  # To work with the file system
import time  # To handle wait times
import socket
import threading
from watchdog.observers import Observer  # Observer to monitor changes in directories
from watchdog.events import FileSystemEventHandler  # Event handler for file changes

# Configuration
SYNC_FOLDER = "./sync_folder"  
peer_addr = "XX:XX:XX:XX:XX:XX"
local_addr = "YY:YY:YY:YY:YY:YY"
port = 30
os.makedirs(SYNC_FOLDER, exist_ok=True)  
class SyncHandler(FileSystemEventHandler):
    
    def __init__(self, send_change):
        self.send_change = send_change 

    def on_any_event(self, event):
        if event.is_directory:  
            return
        self.send_change(event)  

def send_change(event):
    try:
        with socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM) as sock:
            sock.connect((peer_addr, port))
            change_info = {
                "event": event.event_type,
                "src_path": os.path.relpath(event.src_path, SYNC_FOLDER),
                "is_directory": event.is_directory,
            }
            if event.event_type == "modified" or event.event_type == "created":
                with open(event.src_path, "rb") as f:
                    file_data = f.read()
                change_info["data"] = file_data.decode(errors="ignore")
            sock.send(str(change_info).encode())
    except Exception as e:
        print(f"Error al enviar cambio: {e}")

def apply_change(change_info):
    """Aplicar cambios recibidos desde el dispositivo remoto."""
    try:
        path = os.path.join(SYNC_FOLDER, change_info["src_path"])
        if change_info["event"] == "deleted":
            if os.path.exists(path):
                os.remove(path)
        elif change_info["event"] in ["created", "modified"]:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "wb") as f:
                f.write(change_info.get("data", "").encode())
    except Exception as e:
        print(f"Error al aplicar cambio: {e}")

def start_server():
    """Iniciar servidor para recibir cambios desde el dispositivo remoto."""
    sock = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
    sock.bind((local_addr, port))
    sock.listen(1)

    while True:
        client_sock, _ = sock.accept()
        try:
            data = client_sock.recv(1024).decode()
            change_info = eval(data)  # Convertir de string a dict
            apply_change(change_info)
        except Exception as e:
            print(f"Error al recibir cambio: {e}")
        finally:
            client_sock.close()

server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()

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