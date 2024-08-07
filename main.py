import tkinter as tk
from client_gui import ClientApp
import subprocess
import threading
import atexit

matchmaking_server_process=None
game_server_process=None

def start_matchmaking_server():
    global matchmaking_server_process
    matchmaking_server_process=subprocess.Popen(['python', 'matchmaking_server.py'])

def start_game_server():
    global game_server_process
    game_server_process=subprocess.Popen(['python', 'game_server.py'])

def start_servers():
    threading.Thread(target=start_matchmaking_server).start()
    threading.Thread(target=start_game_server).start()

def terminate_servers():
    global matchmaking_server_process, game_server_process
    if matchmaking_server_process:
        matchmaking_server_process.terminate()
    if game_server_process:
        game_server_process.terminate()

atexit.register(terminate_servers)

def main():
    root = tk.Tk()
    app = ClientApp(root, start_servers)
    root.mainloop()

if __name__ == "__main__":
    main()
