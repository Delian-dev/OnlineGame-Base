import signal
import socket
import sys
import threading
import random
import string

#Configurare server pt matchmaking
MATCHMAKING_SERVER_IP='0.0.0.0'
MATCHMAKING_SERVER_PORT=5555

#Dictionar care retine codurile jocurile si adresele pe server corespunzatoare
game_sessions={}

def generate_unique_code(length=6):
    #generare cod alfanumeric
    return ''.join(random.choices(string.ascii_uppercase+string.digits, k=length))

def handle_client(client_socket):
    #Handles matchmaking request from clients
    while True:
        try:
            request=client_socket.recv(1024).decode('utf-8')
            if request.startswith('CREATE'):
                #Generare cod unic pt joc
                game_code=generate_unique_code()
                server_address=request.split()[1]
                game_sessions[game_code]=server_address
                print(f"Sending response...")  # Debug statement
                client_socket.send(f'CODE {game_code}'.encode('utf-8'))

            elif request.startswith('JOIN'):
                game_code=request.split()[1]
                if game_code in game_sessions:
                    server_address=game_sessions[game_code]
                    client_socket.send(f'ADDRESS {server_address}'.encode('utf-8'))
                else:
                    client_socket.send('INVALID_CODE'.encode('utf-8'))

        except Exception as e:
            print(f'Error: {e}')
            client_socket.close()
            break

def handle_exit(signal, frame):
    print("Shutting down matchmaking server...")
    sys.exit(0)

signal.signal(signal.SIGINT, handle_exit)

def main():
    matchmaking_server=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    matchmaking_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    matchmaking_server.bind((MATCHMAKING_SERVER_IP,MATCHMAKING_SERVER_PORT))
    matchmaking_server.listen()
    print(f'Matchmaking server is listening on {MATCHMAKING_SERVER_IP}:{MATCHMAKING_SERVER_PORT}')

    while True:
        client_socket,client_address = matchmaking_server.accept()
        print(f'Mathcmaking connection from {client_address}')
        thread=threading.Thread(target=handle_client, args=(client_socket,))
        thread.start()


if __name__=="__main__":
    main()

