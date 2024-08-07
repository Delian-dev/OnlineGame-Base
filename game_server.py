import socket
import threading
import sys
import signal

player_positions=[(0.5,0.9),
                  (0.5,0.1),
                  (0.1,0.5),
                  (0.9, 0.5)
                 ]

current_players={}
player_sockets={}
player_screens={}
player_usernames={}

def generate_player_name():
    return 'Player'+str(len(current_players)+1)



#Configurare server
SERVER_IP='0.0.0.0'
SERVER_PORT=5050

#lista care retine clientii (jucatorii)
clients=[]

def broadcast(message, sender_socket):
    #Sends message to all connected clients - not the sender
    for client in clients:
        if client!=sender_socket:
            try:
                client.send(message)
            except:
                client.close()
                clients.remove(client)

def handle_client(client_socket):
    if len(clients) >= 4:
        client_socket.send("FULL".encode('utf-8'))
        client_socket.close()
        return

    player_id = generate_player_name()
    clients.append(client_socket)
    player_sockets[player_id] = client_socket

    username = 'Unknown'

    try:
        username_message = client_socket.recv(1024).decode('utf-8')
        if username_message.startswith("USERNAME"):
            _, username = username_message.split()
            player_usernames[player_id] = username

        screen_size_message = client_socket.recv(1024).decode('utf-8')
        if screen_size_message.startswith("SCREEN_SIZE"):
            _, width, height = screen_size_message.split()
            player_screens[player_id] = (int(width), int(height))
            position = player_positions[len(current_players) % len(player_positions)]
            x, y = int(position[0] * int(width)), int(position[1] * int(height))
            current_players[player_id] = (x, y)
            client_socket.send(f"INIT {player_id} {x} {y} {username}".encode('utf-8'))

            for pid, (px, py) in current_players.items():
                if pid != player_id:
                    client_socket.send(f'NEW_PLAYER {pid} {px} {py} {player_usernames[pid]}'.encode('utf-8'))

            broadcast(f"NEW_PLAYER {player_id} {x} {y} {username}".encode('utf-8'), client_socket)

        while True:
            message = client_socket.recv(1024)
            if not message:
                break
            broadcast(message, client_socket)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        clients.remove(client_socket)
        client_socket.close()
        if player_id in current_players:
            del current_players[player_id]
        if player_id in player_sockets:
            del player_sockets[player_id]
        if player_id in player_screens:
            del player_screens[player_id]
        if player_id in player_usernames:
            broadcast(f'DISCONNECT {player_id} {username}'.encode('utf-8'), client_socket)

def broadcast_position(player_id):
    x, y = current_players[player_id]
    message = f"UPDATE {player_id} {x} {y}"
    for pid, sock in player_sockets.items():
        if pid != player_id:
            sock.send(message.encode('utf-8'))

def handle_exit(signal, frame):
    print("Shutting down game server...")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)

def main():
    server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((SERVER_IP,SERVER_PORT))
    server.listen()
    print(f'Server is listening on {SERVER_IP}:{SERVER_PORT}')

    while True:
        client_socket, client_address = server.accept()
        print(f'Connection from {client_address}')
        thread = threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()


if __name__=='__main__':
    main()

