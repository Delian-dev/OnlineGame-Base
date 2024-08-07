import tkinter as tk
import tkinter.messagebox as messagebox
import socket
from game_screen import GameScreen

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # Connect to a known address to determine the local IP
        local_ip = s.getsockname()[0]
        s.close()
        return local_ip
    except Exception as e:
        messagebox.showerror("Error", f"Failed to retrieve local IP address: {e}")
        return None

MATCHMAKING_SERVER_IP = get_local_ip()
#MATCHMAKING_SERVER_IP = '127.0.0.1'
# if not MATCHMAKING_SERVER_IP:
#     messagebox.showerror("Error", "Failed to retrieve local IP address.")
#     MATCHMAKING_SERVER_IP = '127.0.0.1'  # Default to localhost if local IP retrieval fails
MATCHMAKING_SERVER_PORT = 5555
GAME_SERVER_PORT=5050

class ClientApp:
    def __init__(self, root, start_servers_callback):
        self.root = root
        self.root.title("Multiplayer Game")
        self.start_servers_callback=start_servers_callback

        self.frame = tk.Frame(root)
        self.frame.pack(pady=20)

        self.create_button = tk.Button(self.frame, text="Create Game", command=self.create_game)
        self.create_button.grid(row=0, column=0, padx=20)

        self.join_button = tk.Button(self.frame, text="Join Game", command=self.show_join_menu)
        self.join_button.grid(row=0, column=1, padx=20)

        # self.server_ip_label = tk.Label(self.frame, text="Server IP")
        # self.server_ip_label.grid(row=2, column=0, padx=20)
        #
        # self.server_ip_entry = tk.Entry(self.frame)
        # self.server_ip_entry.grid(row=2, column=1, padx=20)
        # self.server_ip_entry.insert(tk.END, MATCHMAKING_SERVER_IP)
        #
        # self.server_port_label = tk.Label(self.frame, text="Server Port")
        # self.server_port_label.grid(row=3, column=0, padx=20)
        #
        # self.server_port_entry = tk.Entry(self.frame)
        # self.server_port_entry.grid(row=3, column=1, padx=20)
        # self.server_port_entry.insert(tk.END, str(MATCHMAKING_SERVER_PORT))
        #
        # self.game_code_label = tk.Label(self.frame, text="Game Code")
        # self.game_code_label.grid(row=4, column=0, padx=20)
        #
        # self.game_code_entry = tk.Entry(self.frame)
        # self.game_code_entry.grid(row=4, column=1, padx=20)
        #
        # self.message_area = tk.Text(root, state='disabled', width=50, height=15)
        # self.message_area.pack(pady=20)
        #
        # self.input_area = tk.Entry(root, width=50)
        # self.input_area.pack(pady=10)
        # self.input_area.bind("<Return>", self.send_message)

    def create_game(self):
        self.start_servers_callback()
        self.prompt_username("create")

    def complete_create_game(self):
        username = self.username_entry.get()
        if not username:
            messagebox.showwarning("Input Error", "Please enter a username.")
            return
        self.username = username
        self.perform_create_game()

    def perform_create_game(self):
        print("Creating game...")  # Debug statement
        server_ip = get_local_ip()
        server_port = GAME_SERVER_PORT
        # if not server_ip or not server_port:
        #     messagebox.showwarning("Input Error", "Please enter the server IP and port.")
        #     return

        server_address = f"{server_ip}:{server_port}"
        try:
            print(f"Creating socket...")  # Debug statement
            matchmaking_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            print(
                f"Connecting to matchmaking server at {MATCHMAKING_SERVER_IP}:{MATCHMAKING_SERVER_PORT}")  # Debug statement
            matchmaking_socket.connect((MATCHMAKING_SERVER_IP, MATCHMAKING_SERVER_PORT))
            print("Connected to matchmaking server")  # Debug statement

            print(f"Sending CREATE command with address {server_address}")  # Debug statement
            matchmaking_socket.send(f"CREATE {server_address}".encode('utf-8'))

            print("Waiting for response from matchmaking server...")  # Debug statement
            response = matchmaking_socket.recv(1024).decode('utf-8')
            print(f"Create response: {response}")  # Debug statement

            matchmaking_socket.close()
            print("Closed matchmaking socket")  # Debug statement

            if response.startswith("CODE"):
                _, game_code = response.split()
                local_ip = get_local_ip()
                messagebox.showinfo("Game Created", f"Game created! Share this code to join: {game_code}\n For the players that join the game, "
                                                    f"they need to assign the variable 'MATCHMAKING_SERVER_IP' in the file 'client_gui.py' the ip: {local_ip} ")
                #self.connect_to_game_server(server_address)
                self.show_game_screen(server_address)
            else:
                messagebox.showerror("Error", "Failed to create game.")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def show_join_menu(self):
        self.clear_frame()
        # self.join_frame = tk.Frame(self.root)
        # self.join_frame.pack(pady=20)

        self.game_code_label=tk.Label(self.frame, text="Game Code")
        self.game_code_label.grid(row=0, column=0, padx=20)

        self.game_code_entry=tk.Entry(self.frame)
        self.game_code_entry.grid(row=0, column=1, padx=20)

        self.join_game_button=tk.Button(self.frame, text='Join', command=self.perform_join_game)
        self.join_game_button.grid(row=1, columnspan=2, pady=20)

    def complete_join_game(self, server_address):
        username = self.username_entry.get()
        if not username:
            messagebox.showwarning("Input Error", "Please enter a username.")
            return
        self.username = username
        print("Joining game...")  # Debug statement
        self.show_game_screen(server_address)

    def perform_join_game(self):
        game_code = self.game_code_entry.get()
        print(game_code)
        if not game_code:
            messagebox.showwarning("Input Error", "Please enter a game code.")
            return

        try:
            matchmaking_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print(f"Connecting to matchmaking server at {MATCHMAKING_SERVER_IP}:{MATCHMAKING_SERVER_PORT}")  # Debug statement
            matchmaking_socket.connect((MATCHMAKING_SERVER_IP, MATCHMAKING_SERVER_PORT))
            matchmaking_socket.send(f"JOIN {game_code}".encode('utf-8'))
            response = matchmaking_socket.recv(1024).decode('utf-8')
            print(f"Join response: {response}")  # Debug statement
            matchmaking_socket.close()

            if response.startswith("ADDRESS"):
                _, server_address = response.split()
                self.prompt_username('join', server_address)
            else:
                messagebox.showerror("Error", "Invalid game code.")
        except Exception as e:
            messagebox.showerror("Connection Error", str(e))

    def prompt_username(self, action, address=''):
        self.clear_frame()
        self.username_label=tk.Label(self.frame, text="Username ")
        self.username_label.grid(row=2, column=0, padx=20)

        self.username_entry=tk.Entry(self.frame)
        self.username_entry.grid(row=2, column=1, padx=20)

        if action=='create':
            self.enter_game_button=tk.Button(self.frame, text='Enter Game', command=self.complete_create_game)
            self.enter_game_button.grid(row=3, columnspan=2, pady=20)
        elif action == 'join':
            self.enter_game_button = tk.Button(self.frame, text='Enter Game', command=lambda: self.complete_join_game(address))
            self.enter_game_button.grid(row=3, columnspan=2, pady=20)

    def show_game_screen(self, server_address):
        self.frame.destroy()
        GameScreen(self.root, server_address, self.username)

    def clear_frame(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
