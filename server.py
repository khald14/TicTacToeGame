import socket
import subprocess
import sys
import threading
import tkinter as tk
from time import sleep
from tkinter import ttk

window = tk.Tk()
window.title("Tic-Tac-Toe Server")
window.attributes('-topmost', 1)
# Top frame consisting of two buttons widgets (i.e. btnStart, btnStop)
topFrame = tk.Frame(window)
topFrame.pack(side=tk.TOP, pady=(5, 0))

# Middle frame consisting of two labels for displaying the host and port info
middleFrame = tk.Frame(window)
lblHost = tk.Label(middleFrame, text="Address: X.X.X.X")
lblHost.pack(side=tk.LEFT)
lblPort = tk.Label(middleFrame, text="Port:XXXX")
lblPort.pack(side=tk.LEFT)
middleFrame.pack(side=tk.TOP, pady=(5, 0))

# The client frame shows the client area
clientFrame = tk.Frame(window)
btnAddClient = tk.Button(clientFrame, text="Add Client", command=lambda: add_client())
btnAddClient.pack(side=tk.TOP)
lbl_name_invalid = tk.Label(clientFrame, text="Name Used, Try Another Name", foreground="red")

reportsFrame = tk.Frame(clientFrame)

frame = tk.Frame(window)
lblFirst = tk.Label(frame, text="Which Player Will Start: ")
lblFirst.pack(side=tk.LEFT)

radio = tk.IntVar()
radio.set(1)
client2_turn = 0
client1_turn = 0

R1 = tk.Radiobutton(frame, text="Player 1", variable=radio, value=1)
R1.pack(side=tk.LEFT)
R2 = tk.Radiobutton(frame, text="player 2", variable=radio, value=2)
R2.pack(side=tk.LEFT)
frame.pack(side=tk.TOP, pady=(5, 0))

lbl_info = tk.Label(clientFrame, text="**********Client List**********")

radio2 = tk.IntVar()
radio2.set(1)


def update_display():
    """ Update The Display According To The Radio Buttons

        Parameters
        ----------
        No Parameters

        Returns
        -------
        No Return.
        """
    global my_game

    if radio2.get() == 1:
        lbl_info.configure(text="**********Client List**********")
    elif radio2.get() == 2:
        lbl_info.configure(text="**********Players Report**********")
    elif radio2.get() == 3:
        lbl_info.configure(text="**********Games Report**********")

    update_client_names_display(clients_names)


clients_radio = tk.Radiobutton(reportsFrame, text="Client List", variable=radio2, value=1, command=update_display)
clients_radio.pack(side=tk.LEFT)
players_radio = tk.Radiobutton(reportsFrame, text="Players Report", variable=radio2, value=2, command=update_display)
players_radio.pack(side=tk.LEFT)
games_radio = tk.Radiobutton(reportsFrame, text="Games Report", variable=radio2, value=3, command=update_display)
reportsFrame.pack(side=tk.TOP, pady=(5, 0))

lbl_info.pack()

games_radio.pack(side=tk.LEFT)

clientFrame.pack(side=tk.BOTTOM, pady=(5, 10))

game_frame = tk.Frame(clientFrame)
game_frame.pack(side=tk.BOTTOM)

# scrollbar

game_scroll = tk.Scrollbar(game_frame, orient='vertical')
game_scroll.pack(side=tk.RIGHT, fill=tk.Y)
my_game = ttk.Treeview(game_frame, yscrollcommand=game_scroll.set, xscrollcommand=game_scroll.set)
my_game.pack()
game_scroll.config(command=my_game.yview)

server = None
HOST_ADDR = "localhost"
HOST_PORT = 8080
TEST_HOST_ADDR = "localhost"
TEST_HOST_PORT = 8081
client_name = " "
client_color = []
clients = []
clients_names = []
player_data = []
processes = []
games_list = []
players_list = []
close_just_one = 0


def load_games_from_file():
    """ Load The Games List From the File

        Parameters
        ----------
        No Parameters

        Returns
        -------
        No Return.
        """
    global games_list
    games_list.clear()
    f = open('games.txt', 'r')

    while True:
        res = f.readline()
        if res == '':
            break
        str_list = res.split("#")

        games_list.append([str_list[0], str_list[1], str_list[2], str_list[3]])

    f.close()


def load_players_from_file():
    """ Load The Players List From the File

        Parameters
        ----------
        No Parameters

        Returns
        -------
        No Return.
        """
    global players_list
    players_list.clear()

    f = open('players.txt', 'r')

    while True:
        res = f.readline()
        if res == '':
            break
        str_list = res.split("#")

        players_list.append([str_list[0], str_list[1], str_list[2], str_list[3]])

    f.close()


# Start server function
def start_server():
    """Start The Server

         Parameters
         ----------
         No Parameters.

         Returns
         -------
         No Return.
         """

    load_games_from_file()
    load_players_from_file()
    global server, HOST_ADDR, HOST_PORT  # code is fine without this

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST_ADDR, HOST_PORT))
    server.listen(5)  # server is listening for client connection

    threading._start_new_thread(accept_clients, (server, " "))

    lblHost["text"] = "Address: " + HOST_ADDR
    lblPort["text"] = "Port: " + str(HOST_PORT)

    with open('log.txt', 'a') as f:
        f.write('Starting the server.')


# Add Client
def add_client():
    """Add Client To Server

         Parameters
         ----------
         No Parameters.

         Returns
         -------
         No Return.
         """
    global processes, frame
    if len(clients) == 2:
        btnAddClient["state"] = "disabled"
    if len(clients) < 2:
        processes.append(subprocess.Popen("Python client.py", stdout=sys.stdout))


def accept_clients(the_server, y):
    """ Accept Clients To Server

        Parameters
        ----------
        the_server: the server connection.

        Returns
        -------
        No Return.
        """
    while True:
        if len(clients) < 2:
            client, addr = the_server.accept()
            clients.append(client)
            if len(clients) == 1:
                R1.configure(state=tk.DISABLED)
                R2.configure(state=tk.DISABLED)

            # use a thread so as not to clog the gui thread
            threading._start_new_thread(send_receive_client_message, (client, addr))


def start_test_server():
    """Start The Server

         Parameters
         ----------
         No Parameters.

         Returns
         -------
         No Return.
         """

    global server, HOST_ADDR, HOST_PORT  # code is fine without this

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((TEST_HOST_ADDR, TEST_HOST_PORT))
    server.listen(5)  # server is listening for client connection

    threading._start_new_thread(accept_clients_test, (server, " "))

    lblHost["text"] = "Address: " + HOST_ADDR
    lblPort["text"] = "Port: " + str(HOST_PORT)

    with open('log.txt', 'a') as f:
        f.write('Starting test server.\n')


def accept_clients_test(the_server, y):
    """ Accept Clients To Server

        Parameters
        ----------
        the_server: the server connection.

        Returns
        -------
        No Return.
        """
    while True:
        client, addr = the_server.accept()
        # use a thread so as not to clog the gui thread
        threading._start_new_thread(check_connection_with_server, (client, addr))


def check_connection_with_server(client_connection, addr):
    """ Check Connection With Server

        Parameters
        ----------
        No Parameters

        Returns
        -------
        No Return.
        """
    sync = client_connection.recv(4096).decode()
    client_connection.send('ack'.encode())


# Function to receive message from current client AND
# Send that message to other clients
def send_receive_client_message(client_connection, client_ip_addr):
    """ Send And Receive Client Messages

        Function to receive message from current client AND
        Send that message to other clients.

        Parameters
        ----------
        client_connection: client connection used to send and receive data to the client.

        Returns
        -------
        No Return.
        """

    global server, client_name, client_color, clients, player_data, player0, player1, \
        client1_turn, client2_turn, my_game, close_just_one, lbl_name_invalid

    for i in range(2):
        try:
            name_and_color = client_connection.recv(4096).decode()
            if i == 0:
                client_name = name_and_color
                clients_names.append(client_name)
                if len(clients) == 2:
                    if clients_names[0] == clients_names[1]:
                        clients_names.remove(clients_names[1])
                        clients.remove(clients[1])
                        update_display()
                        processes[-1].terminate()
                        close_just_one = 1
                        lbl_name_invalid.pack(side=tk.TOP)
                    else:
                        lbl_name_invalid.pack_forget()
            else:
                client_color.append(name_and_color)
        except Exception:
            pass

    # name_and_color = client_connection.recv(4096).decode().split('#')
    # if len(name_and_color) == 3:
    #     return
    # # send welcome message to client
    # client_name = name_and_color[0]
    #
    # client_color.append('#' + name_and_color[1])
    #
    # clients_names.append(client_name)
    #
    # if len(clients) == 2:
    #     if clients_names[0] == clients_names[1]:
    #         client_color.remove(client_color[1])
    #         clients_names.remove(clients_names[1])
    #         clients.remove(clients[1])
    #         update_display()
    #         processes[-1].terminate()
    #         close_just_one = 1
    #         lbl_name_invalid.pack(side=tk.TOP)
    #     else:
    #         lbl_name_invalid.pack_forget()

    try:
        if len(clients) < 2:
            client_connection.send("welcome1".encode())
        else:
            client_connection.send("welcome2".encode())
    except Exception:
        pass

    with open('log.txt', 'a') as f:
        f.write(f'{client_name} joined the server.\n')

    update_display()  # update client names display
    if len(clients) > 1:
        sleep(1)
        symbols = ["O", "X"]
        if radio.get() == 1:
            client1_turn = 1
            client2_turn = 2
        else:
            client1_turn = 2
            client2_turn = 1

        # send opponent name and symbol

        s1 = "opponent_name$" + clients_names[1] + "#" + symbols[1] + "#" + str(client1_turn)
        clients[0].send(s1.encode())

        s2 = "opponent_name$" + clients_names[0] + "#" + symbols[0] + "#" + str(client2_turn)
        clients[1].send(s2.encode())

        c1 = "color" + clients_names[1] \
             + client_color[1]
        clients[0].send(c1.encode())

        c2 = "color" + clients_names[0] \
             + client_color[0]
        clients[1].send(c2.encode())

    while True:
        idx = get_client_index(clients, client_connection)
        try:
            # get the player choice from received data
            data = client_connection.recv(4096)
            if not data:
                break
            with open('log.txt', 'a') as f:
                position = ",".join(data.decode().split("$")[2:])
                f.write(f'{clients_names[idx]} played {position}\n')
            # player x,y coordinate data. forward to the other player
            if data.startswith("$xy$".encode()):
                # is the message from client1 or client2?

                if client_connection == clients[0]:
                    # send the data from this player (client) to the other player (client)
                    clients[1].send(data)
                else:
                    # send the data from this player (client) to the other player (client)
                    clients[0].send(data)
        except ConnectionResetError:
            break

    # find the client index then remove from both lists(client name list and connection list)
    idx = get_client_index(clients, client_connection)

    try:
        with open('log.txt', 'a') as f:
            f.write(f'{clients_names[idx]} disconnected..\n')
        del clients_names[idx]
        del clients[idx]
    except Exception:
        pass

    load_games_from_file()
    load_players_from_file()
    update_display()

    if close_just_one == 0:
        client_color.clear()

        for p in processes:
            p.terminate()
        processes.clear()

        R1.configure(state=tk.NORMAL)
        R2.configure(state=tk.NORMAL)

        btnAddClient["state"] = "normal"

        client_connection.close()

    close_just_one = 0
    update_display()  # update client names display


# Return the index of the current client in the list of clients
def get_client_index(client_list, curr_client):
    """ Get Client by Index

            Function that return the index of the current client in the list of clients.

            Parameters
            ----------
            client_list: the clients list.
            curr_client: the client we need its index in the clients list.

            Returns
            -------
            The index of the current client in the list of clients.
            """

    idx = 0
    for conn in client_list:
        if conn == curr_client:
            break
        idx = idx + 1

    return idx


# Update client name display when a new client connects OR
# When a connected client disconnects
def update_client_names_display(name_list):
    """ Update Client Names On Server Display

            Update client name display when a new client connects OR
            When a connected client disconnects.

            Parameters
            ----------
            name_list: the clients names' list .

            Returns
            -------
            No Return.
            """
    global radio2, my_game
    try:
        my_game.delete(*my_game.get_children())
    except Exception:
        pass

    try:
        if radio2.get() == 1:
            my_game['columns'] = 'Clients'

            my_game.column("#0", width=0, stretch=tk.NO)
            for c in my_game['columns']:
                my_game.column(c, anchor=tk.CENTER, width=200)
                my_game.heading(c, text=c, anchor=tk.CENTER)
            i = 1
            for p in name_list:
                my_game.insert(parent='', index='end', iid=str(i), text='',
                               values=p)
                i += 1

        else:

            if radio2.get() == 2:
                my_game['columns'] = ('Player Name', 'No. Games', 'No. Wins', 'No. Looses')

                my_game.column("#0", width=0, stretch=tk.NO)
                for c in my_game['columns']:
                    my_game.column(c, anchor=tk.CENTER, width=200)
                    my_game.heading(c, text=c, anchor=tk.CENTER)
                i = 1
                for p in players_list:
                    my_game.insert(parent='', index='end', iid=str(i), text='',
                                   values=(p[0], p[1], p[2], p[3]))
                    i += 1

            elif radio2.get() == 3:
                my_game['columns'] = ('Game Date', 'Player 1', 'Player 2', 'Winner')
                my_game.column("#0", width=0, stretch=tk.NO)
                for c in my_game['columns']:
                    my_game.column(c, anchor=tk.CENTER, width=200)
                    my_game.heading(c, text=c, anchor=tk.CENTER)
                i = 1
                for g in games_list:
                    my_game.insert(parent='', index='end', iid=str(i), text='',
                                   values=(g[0], g[1], g[2], g[3]))
                    i += 1
                my_game.pack(side=tk.BOTTOM, pady=(5, 0))
    except Exception:
        pass


start_test_server()
start_server()
window.mainloop()
