import tkinter as tk
import threading
import socket
import tkinter.messagebox as messagebox

class GameScreen:
    def __init__(self, root, server_address, username):
        self.root=root
        self.server_address=server_address
        self.username=username

        # self.dimension=root.geometry("1240x1080")
        # self.background=root.configure(background="green")
        self.players={}
        self.player_labels={}
        self.player_id=None
        self.player_initial_positions = {}
        self.screen_size = (0, 0)

        # Standardized player positions relative to the local player
        self.relative_positions = [(0.5, 0.9), (0.5, 0.1), (0.1, 0.5), (0.9, 0.5)]

        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Creating and packing the canvas
        self.canvas = tk.Canvas(self.main_frame, width=700, height=550, bg='green')
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        # Creating the chat frame
        self.chat_frame = tk.Frame(self.main_frame)
        self.chat_frame.pack(side=tk.BOTTOM, fill=tk.X)


        # Creating and packing the message area
        self.message_area = tk.Text(self.chat_frame, state='disabled', height=10)
        self.message_area.pack(side=tk.TOP, fill=tk.X, padx=20, pady=(10, 10))

        # Creating and packing the input area
        self.input_area = tk.Entry(self.chat_frame)
        self.input_area.pack(side=tk.TOP, fill=tk.X, padx=20, pady=(10, 50))
        self.input_area.bind("<Return>", self.send_message)

        self.connect_to_game_server(server_address)
        #self.root.bind("<Configure>", self.on_resize)

    def connect_to_game_server(self, server_address):
        print(f"Connecting to game server at {server_address}")
        ip, port = server_address.split(':')
        port = int(port)
        try:
            self.game_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.game_socket.connect((ip, port))
            print("Connected to game server")
            self.message_area.config(state='normal')
            self.message_area.insert(tk.END, "Connected to game server\n")
            self.message_area.config(state='disabled')

            # Send the username to the server
            self.game_socket.send(f"USERNAME {self.username}".encode('utf-8'))

            self.root.after(100, self.send_screen_size) #delay pt ca fereastra sa fie in totalitate incarcata intai

            thread = threading.Thread(target=self.receive_messages)
            thread.daemon = True
            thread.start()
        except Exception as e:
            messagebox.showerror("Connection Error", f"Failed to connect to game server: {e}")

    def send_screen_size(self):
        width, height = self.canvas.winfo_width(), self.canvas.winfo_height()
        self.screen_size=(width, height)
        screen_size_message = f"SCREEN_SIZE {width} {height}"
        self.game_socket.send(screen_size_message.encode('utf-8'))

    def send_message(self, event):
        message =self.username+': '+ self.input_area.get()
        if message.lower() == 'exit':
            self.root.quit()
        else:
            print(f"Sending message: {message}")
            try:
                self.game_socket.send(message.encode('utf-8'))
                self.message_area.config(state='normal')
                self.message_area.insert(tk.END, f"{message}\n")
                self.message_area.config(state='disabled')
                self.input_area.delete(0, tk.END)
                self.message_area.see(tk.END)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to send message: {e}")

    def receive_messages(self):
        while True:
            try:
                message = self.game_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                self.process_message(message)
            except:
                break

    def process_message(self, message):
        parts = message.split()
        command = parts[0]

        if command=="FULL":
            tk.messagebox.showerror("Server Full", "The game is full. Please try again later.")
            self.root.quit()

        elif command == "INIT":
            self.player_id = parts[1]
            player_name = parts[4]  # Assume player_name is included in the message
            self.initialize_player(self.player_id, player_name, 'blue')
            self.update_message_area(f"Connected as {player_name}")

        elif command == "NEW_PLAYER":
            player_id = parts[1]
            x, y = float(parts[2]), float(parts[3])
            player_name = parts[4]  # Assume player_name is included in the message
            self.add_player(player_id, x, y, player_name, 'red')
            self.update_message_area(f"New player {player_name} joined")

        elif command == "UPDATE":
            player_id = parts[1]
            x, y = float(parts[2]), float(parts[3])
            self.update_player_position(player_id, x, y)

        elif command == "DISCONNECT":
            player_id = parts[1]
            player_name=parts[2]
            self.update_message_area(f"Player {player_name} disconnected")
            self.remove_player(player_id)

        else:
            self.update_message_area(message)

    def initialize_player(self, player_id, player_name, color):
        self.players[player_id] = {"name": player_name, "color": color}
        self.update_player_positions()

    def add_player(self, player_id, x, y, player_name, color):
        self.players[player_id] = {"name": player_name, "x": x, "y": y, "color": color}
        self.update_player_positions()

    def remove_player(self, player_id):
        player = self.players.pop(player_id, None)
        if player:
            self.canvas.delete(player["oval"])
            self.canvas.delete(player["label"])
            self.update_player_positions()

    def update_player_positions(self):
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        found_player=0
        for i, player_id in enumerate(self.players):
            player = self.players[player_id]

            if player_id == self.player_id:
                x, y = self.relative_positions[0]
                found_player=1
            else:
                x, y = self.relative_positions[(i + 1-found_player) % len(self.relative_positions)]

            canvas_x = x * canvas_width
            canvas_y = y * canvas_height

            if "oval" in player:
                self.canvas.coords(player["oval"], canvas_x - 10, canvas_y - 10, canvas_x + 10, canvas_y + 10)
                self.canvas.coords(player["label"], canvas_x, canvas_y + 25)
            else:
                player["oval"] = self.canvas.create_oval(canvas_x - 10, canvas_y - 10, canvas_x + 10, canvas_y + 10,
                                                         fill=player["color"])
                player["label"] = self.canvas.create_text(canvas_x, canvas_y + 25, text=player["name"], font=("Helvetica", 12, "bold"), fill="white")

    def update_player_position(self, player_id, x, y):
        player = self.players.get(player_id)
        if player:
            player["x"] = x
            player["y"] = y
            self.update_player_positions()
    def update_message_area(self, message):
        self.message_area.config(state='normal')
        self.message_area.insert(tk.END, f"{message}\n")
        self.message_area.config(state='disabled')


    # def on_resize(self, event):
    #     self.resize_players()
    #
    # def resize_players(self):
    #     canvas_width = self.canvas.winfo_width()
    #     canvas_height = self.canvas.winfo_height()
    #     #print(self.player_initial_positions)
    #     for player_id, original_pos in self.player_initial_positions.items():
    #         original_x, original_y = original_pos
    #         new_x = int(original_x * canvas_width / self.screen_size[0])
    #         new_y = int(original_y * canvas_height / self.screen_size[1])
    #         self.canvas.coords(self.players[player_id], new_x + 10, new_y + 10, new_x + 30, new_y + 30)
    #         self.canvas.coords(self.player_labels[player_id], new_x + 20, new_y + 40)
    #
    def on_canvas_resize(self, event):
        self.update_player_positions()