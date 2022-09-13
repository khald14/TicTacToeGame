import os
import time

import winsound
import tkinter as tk
from tkinter import colorchooser
import socket
from time import sleep
import threading
from datetime import datetime

# MAIN GAME WINDOW
first_time = True

window_main = tk.Tk()
window_main.title("Tic-Tac-Toe Client")
window_main.attributes('-topmost', 1)
top_welcome_frame = tk.Frame(window_main)
lbl_name = tk.Label(top_welcome_frame, text="Name:")
lbl_name.pack(side=tk.LEFT)
ent_name = tk.Entry(top_welcome_frame)
ent_name.pack(side=tk.LEFT)
btn_connect = tk.Button(top_welcome_frame, text="Connect", command=lambda: connect())
btn_connect.pack(side=tk.LEFT)

lbl_error = tk.Label(top_welcome_frame, text="")
lbl_error.pack(side=tk.LEFT)

top_welcome_frame.pack(side=tk.TOP)

top_frame = tk.Frame(window_main)

# network client
client = None
HOST_ADDR = "localhost"
HOST_PORT = 8080
TEST_HOST_ADDR = "localhost"
TEST_HOST_PORT = 8081

list_labels = []
num_cols = 3
your_turn = False
you_started = False

radio_value = ""

your_details = {
    "name": "Charles",
    "symbol": "X",
    "color": "",
    "score": 0
}

opponent_details = {
    "name": " ",
    "symbol": "O",
    "color": "",
    "score": 0
}
color = ""
game_list = []
players_list = []
flag = False
terminated = False


def count_down():
    """ Count Down Function

        We Used This Function To Display A Timer To Both Clients, And Warn Them That They
        Have 10 seconds To Play Again Or The Session Will Shut Down.

        Parameters
        ----------
        No Parameters

        Returns
        -------
        No Return.
        """
    global flag, terminated
    # if terminated is False:
    #     terminated = True
    # else:
    #     return

    lbl_play_again["text"] = "10"
    window_main.update()
    sleep(1)
    for i in range(10, 0, -1):
        window_main.update()
        if terminated is False:
            try:
                lbl_play_again["text"] = str(i)
            except Exception:
                return
        else:
            return
        sleep(1)
    window_main.update()
    sleep(1)
    if flag is False:
        terminated = True
        window_main.destroy()
    else:
        flag = False


def play_again_show():
    """ Display Play Again Button To Clients

        Parameters
        ----------
        No Parameters

        Returns
        -------
        No Return.
        """
    global flag
    flag = True
    play_again.grid_forget()
    lbl_play_again.grid_forget()
    threading._start_new_thread(init, ("", ""))


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
    f = open('players.txt', 'r')

    while True:
        res = f.readline()
        if res == '':
            break
        str_list = res.split("#")

        players_list.append(Player(str_list[0], int(str_list[1]), int(str_list[2]), int(str_list[3])))

    f.close()


def save_players_to_file():
    """ Save The Players List To the File

        Parameters
        ----------
        No Parameters

        Returns
        -------
        No Return.
        """
    global players_list

    # players_list.sort(key=lambda plyr: plyr.num_of_games)

    # To return a new list, use the sorted() built-in function...
    new_list = sorted(players_list, key=lambda plyr: plyr.num_of_wins, reverse=True)
    f = open('players.txt', 'w')

    for p in new_list:
        f.writelines([p.name, "#", str(p.num_of_games), "#", str(p.num_of_wins), "#", str(p.num_of_looses), "\n"])

    f.close()


def load_games_from_file():
    """ Load The Games List From the File

        Parameters
        ----------
        No Parameters

        Returns
        -------
        No Return.
        """
    global game_list
    f = open('games.txt', 'r')

    while True:
        res = f.readline()
        if res == '':
            break
        str_list = res.split("#")

        game_list.append(Game(str_list[0], str_list[1], str_list[2], str_list[3][0:-1]))

    f.close()


def save_games_to_file():
    """ Save The Games List To the File

        Parameters
        ----------
        No Parameters

        Returns
        -------
        No Return.
        """
    global game_list
    f = open('games.txt', 'w')

    for g in game_list:
        f.writelines([g.start_date, "#", str(g.player1), "#", str(g.player2), "#", str(g.winner), "\n"])

    f.close()


class Player:
    def __init__(self, name, num_of_games, num_of_wins, num_of_looses):
        self.name = name
        self.num_of_games = num_of_games
        self.num_of_wins = num_of_wins
        self.num_of_looses = num_of_looses

    def set_name(self, n):
        self.name = n

    def set_num_of_games(self, g):
        self.num_of_games = g

    def set_num_of_wins(self, wins):
        self.num_of_wins = wins

    def set_num_of_looses(self, looses):
        self.num_of_looses = looses

    def print_player(self):
        print("Player Name:", self.name, " Number Of Games:", self.num_of_games, " Number Of Wins:",
              self.num_of_wins, " Number Of Looses:", self.num_of_looses)


class Game:
    def __init__(self, start_date, player1, player2, winner):
        self.start_date = start_date
        self.player1 = player1
        self.player2 = player2
        self.winner = winner

    def set_winner(self, w):
        self.winner = w

    def set_start_date(self, d):
        self.start_date = d

    def set_player1(self, p1):
        self.player1 = p1

    def set_player2(self, p2):
        self.player2 = p2

    def print_game(self):
        print("Start Date:", self.start_date, " Player1:", self.player1, " Player2:",
              self.player2, " Winner:", self.winner)


load_players_from_file()
load_games_from_file()

for x in range(3):
    for y in range(3):
        lbl = tk.Button(top_frame, text=" ", font="Helvetica 45 bold", height=1, width=4, highlightbackground="black",
                        highlightcolor="black", highlightthickness=1, command=lambda xy=[x, y]: get_coordinate(xy))
        lbl.grid(row=x, column=y)

        dict_labels = {"xy": [x, y], "symbol": "", "label": lbl, "ticked": False}
        list_labels.append(dict_labels)

lbl_status = tk.Label(top_frame, text="Status: Not connected to server", font="Helvetica 14 bold")
lbl_status.grid(row=3, columnspan=3)
play_again = tk.Button(top_frame, text="Play Again", font="Helvetica 10 bold", command=play_again_show)
play_again.grid(row=4, columnspan=3)
lbl_play_again = tk.Label(top_frame, text="10", font="Helvetica 10 bold")
lbl_play_again.grid(row=5, columnspan=3)

play_again.grid_forget()
lbl_play_again.grid_forget()

top_frame.pack_forget()


def choose_color():
    """ Choose Color From Color's Window

        The client chooses his symbol color when the connects to the server.

        Parameters
        ----------
        No Parameters.

        Returns
        -------
        No Return.
        """
    global color
    # variable to store hexadecimal code of color
    color = colorchooser.askcolor(title="Choose color")[1]
    if color is None:
        color = "#000000"


def init(arg0, arg1):
    """ Init The Client

           Parameters
           ----------
           arg0, arg1.

           Returns
           -------
           No Return.
           """
    global list_labels, your_turn, your_details, opponent_details, you_started

    sleep(0.5)

    for i in range(len(list_labels)):
        list_labels[i]["symbol"] = ""
        list_labels[i]["ticked"] = False
        list_labels[i]["label"]["text"] = ""
        list_labels[i]["label"].config(foreground="black", highlightbackground="grey",
                                       highlightcolor="grey", highlightthickness=1)

    lbl_status.config(foreground="black")
    lbl_status["text"] = "STATUS: Game's starting."
    sleep(0.5)
    lbl_status["text"] = "STATUS: Game's starting.."
    sleep(0.5)
    lbl_status["text"] = "STATUS: Game's starting..."
    sleep(0.5)

    if you_started:
        you_started = False
        your_turn = False
        lbl_status["text"] = "STATUS: " + opponent_details["name"] + "'s turn!"
    else:
        you_started = True
        your_turn = True
        lbl_status["text"] = "STATUS: Your turn!"


def get_coordinate(xy):
    """ Get coordinate value client

        Parameters
        ----------
        xy: List of coordinates [x, y].

        Returns
        -------
        No Return.
        """

    global client, your_turn, terminated
    # convert 2D to 1D coordinate i.e. index = x * num_cols + y
    label_index = xy[0] * num_cols + xy[1]
    label = list_labels[label_index]

    if your_turn:
        if label["ticked"] is False:

            label["label"].config(foreground=your_details["color"])
            label["label"]["text"] = your_details["symbol"]
            label["ticked"] = True
            label["symbol"] = your_details["symbol"]
            # send xy coordinate to server
            coordinate = "$xy$" + str(xy[0]) + "$" + str(xy[1])
            client.send(coordinate.encode())
            your_turn = False

            # Does this play leads to a win or a draw
            result = game_logic()
            if result[0] is True and result[1] != "":  # a win
                your_details["score"] = your_details["score"] + 1
                lbl_status["text"] = "Game over, You won! You(" + str(your_details["score"]) + ") - " \
                                                                                               "" + opponent_details[
                                         "name"] + "(" + str(opponent_details["score"]) + ")"
                lbl_status.config(foreground="green")

                if your_details["symbol"] == "X":
                    player = next((pl for pl in players_list if pl.name == your_details["name"]), None)
                    player2 = next((pl for pl in players_list if pl.name == opponent_details["name"]), None)
                    if player is not None:
                        players_list.remove(player)
                        player.num_of_games += 1
                        player.num_of_wins += 1
                        players_list.append(Player(player.name, player.num_of_games, player.num_of_wins,
                                                   player.num_of_looses))
                    else:
                        players_list.append(Player(your_details["name"], 1, 1, 0))

                    if player2 is not None:
                        players_list.remove(player2)
                        player2.num_of_games += 1
                        player2.num_of_looses += 1
                        players_list.append(Player(player2.name, player2.num_of_games, player2.num_of_wins,
                                                   player2.num_of_looses))
                    else:
                        players_list.append(Player(opponent_details["name"], 1, 0, 1))

                    game_list.append(
                        Game(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), your_details["name"],
                             opponent_details["name"], your_details["name"]))

                    save_players_to_file()
                    save_games_to_file()

                winsound.PlaySound('sound.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)

                play_again.grid(row=4, columnspan=3)
                lbl_play_again.grid(row=5, columnspan=3)
                count_down()
                terminated = False

            elif result[0] is True and result[1] == "":  # a draw
                lbl_status["text"] = "Game over, Draw! You(" + str(your_details["score"]) + ") - " \
                                                                                            "" + opponent_details[
                                         "name"] + "(" + str(opponent_details["score"]) + ")"
                lbl_status.config(foreground="blue")

                play_again.grid(row=4, columnspan=3)
                lbl_play_again.grid(row=5, columnspan=3)
                count_down()
                terminated = False

            else:
                lbl_status["text"] = "STATUS: " + opponent_details["name"] + "'s turn!"
    else:
        lbl_status["text"] = "STATUS: Wait for your turn!"
        lbl_status.config(foreground="red")

        # send xy coordinate to server


# [(0,0) -> (0,1) -> (0,2)], [(1,0) -> (1,1) -> (1,2)], [(2,0), (2,1), (2,2)]
def check_row():
    """ Check Row Win Client

            Parameters
            ----------
            No Parameters.

            Returns
            -------
            list that contains both the winner which is a boolean
            True if there is a winner and the symbol of the winner.
            """
    list_symbols = []
    list_labels_temp = []
    winner = False
    win_symbol = ""
    for i in range(len(list_labels)):
        list_symbols.append(list_labels[i]["symbol"])
        list_labels_temp.append(list_labels[i])
        if (i + 1) % 3 == 0:
            if list_symbols[0] == list_symbols[1] == list_symbols[2]:
                if list_symbols[0] != "":
                    winner = True
                    win_symbol = list_symbols[0]

                    list_labels_temp[0]["label"].config(foreground="green", highlightbackground="green",
                                                        highlightcolor="green", highlightthickness=2)
                    list_labels_temp[1]["label"].config(foreground="green", highlightbackground="green",
                                                        highlightcolor="green", highlightthickness=2)
                    list_labels_temp[2]["label"].config(foreground="green", highlightbackground="green",
                                                        highlightcolor="green", highlightthickness=2)

            list_symbols = []
            list_labels_temp = []

    return [winner, win_symbol]


# [(0,0) -> (1,0) -> (2,0)], [(0,1) -> (1,1) -> (2,1)], [(0,2), (1,2), (2,2)]
def check_col():
    """ Check Column Win Client

            Parameters
            ----------
            No Parameters.

            Returns
            -------
            list that contains both the winner which is a boolean
            True if there is a winner and the symbol of the winner.
            """

    winner = False
    win_symbol = ""
    for i in range(num_cols):
        if list_labels[i]["symbol"] == list_labels[i + num_cols]["symbol"] == list_labels[i + num_cols + num_cols][
            "symbol"]:
            if list_labels[i]["symbol"] != "":
                winner = True
                win_symbol = list_labels[i]["symbol"]

                list_labels[i]["label"].config(foreground="green", highlightbackground="green",
                                               highlightcolor="green", highlightthickness=2)
                list_labels[i + num_cols]["label"].config(foreground="green", highlightbackground="green",
                                                          highlightcolor="green", highlightthickness=2)
                list_labels[i + num_cols + num_cols]["label"].config(foreground="green", highlightbackground="green",
                                                                     highlightcolor="green", highlightthickness=2)

    return [winner, win_symbol]


def check_diagonal():
    """ Check Diagonal Win Client

            Parameters
            ----------
            No Parameters.

            Returns
            -------
            list that contains both the winner which is a boolean
            True if there is a winner and the symbol of the winner.
            """

    winner = False
    win_symbol = ""
    i = 0
    j = 2

    # top-left to bottom-right diagonal (0, 0) -> (1,1) -> (2, 2)

    if list_labels[i]["symbol"] == list_labels[i + (num_cols + 1)]["symbol"] == \
            list_labels[(num_cols + num_cols) + (i + 2)]["symbol"]:
        if list_labels[i]["symbol"] != "":
            winner = True
            win_symbol = list_labels[i]["symbol"]

            list_labels[i]["label"].config(foreground="green", highlightbackground="green",
                                           highlightcolor="green", highlightthickness=2)

            list_labels[i + (num_cols + 1)]["label"].config(foreground="green", highlightbackground="green",
                                                            highlightcolor="green", highlightthickness=2)
            list_labels[(num_cols + num_cols) + (i + 2)]["label"].config(foreground="green",
                                                                         highlightbackground="green",
                                                                         highlightcolor="green", highlightthickness=2)

    # top-right to bottom-left diagonal (0, 0) -> (1,1) -> (2, 2)
    elif list_labels[j]["symbol"] == list_labels[j + (num_cols - 1)]["symbol"] == list_labels[j + (num_cols + 1)][
        "symbol"]:
        if list_labels[j]["symbol"] != "":
            winner = True
            win_symbol = list_labels[j]["symbol"]

            list_labels[j]["label"].config(foreground="green", highlightbackground="green",
                                           highlightcolor="green", highlightthickness=2)
            list_labels[j + (num_cols - 1)]["label"].config(foreground="green", highlightbackground="green",
                                                            highlightcolor="green", highlightthickness=2)
            list_labels[j + (num_cols + 1)]["label"].config(foreground="green", highlightbackground="green",
                                                            highlightcolor="green", highlightthickness=2)
    else:
        winner = False

    return [winner, win_symbol]


# it's a draw if grid is filled
def check_draw():
    """ Check If There Are Draw Client

            Parameters
            ----------
            No Parameters

            Returns
            -------
            list that contains True if there is a draw and false if not.
            """

    for i in range(len(list_labels)):
        if list_labels[i]["ticked"] is False:
            return [False, ""]
    return [True, ""]


def game_logic():
    """ Define Game Logic """
    result = check_row()
    if result[0]:
        return result

    result = check_col()
    if result[0]:
        return result

    result = check_diagonal()
    if result[0]:
        return result

    result = check_draw()
    return result


def connect():
    """ Connect To Server

        Parameters
        ----------
        No Parameters

        Returns
        -------
        No Return.
        """
    global your_details
    if len(ent_name.get()) < 1:
        pass
    else:
        # choose_color()
        your_details["name"] = ent_name.get()
        btn_connect['state'] = tk.NORMAL
        connect_to_server(ent_name.get())


def connect_to_server(name):
    """ Connect and send data To Server

        Parameters
        ----------
        name: name of the client trying to connect to the server.

        Returns
        -------
        No Return.
        """
    global client, HOST_PORT, HOST_ADDR
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST_ADDR, HOST_PORT))
        client.send(name.encode())  # Send name to server after connecting
        choose_color()
        client.send(color.encode())
        # start a thread to keep receiving message from server
        # do not block the main thread :)
        threading._start_new_thread(receive_message_from_server, (client, "m"))
        top_welcome_frame.pack_forget()
        top_frame.pack(side=tk.TOP)
        window_main.title("Tic-Tac-Toe Client - " + name)
    except Exception as e:
        client.close()
        window_main.destroy()


def receive_message_from_server(sck, m):
    """ Receive Messages From Server

        Receive Messages From Server and updates the clients
        as the message received.

        Parameters
        ----------
        sck: the socket data received from the server.

        Returns
        -------
        No Return.
        """
    global your_details, opponent_details, your_turn, you_started, radio_value, terminated
    while True:
        try:
            from_server = sck.recv(4096)

            if not from_server:
                break
            if from_server.startswith("welcome".encode()):
                if from_server.startswith("welcome1".encode()):
                    your_details["color"] = color
                    lbl_status["text"] = "Server: Welcome " + your_details["name"] + "! Waiting for player 2"

                elif from_server.startswith("welcome2".encode()):
                    lbl_status["text"] = "Server: Welcome " + your_details["name"] + "! Game will start soon"
                    your_details["color"] = color
                    # opponent_details["color"] = "purple"

            elif from_server.startswith("color".encode()):
                from_server = from_server.replace("color".encode(), "".encode())
                opponent_details["color"] = '#' + from_server.decode().split('#')[1]

            elif from_server.startswith("opponent_name$".encode()):
                from_server = from_server.replace("opponent_name$".encode(), "".encode())

                opponent_details["name"] = from_server.decode().split('#')[0]
                your_details["symbol"] = from_server.decode().split('#')[1]
                # set opponent symbol
                global radio_value
                radio_value = from_server.decode().split('#')[2]
                if your_details["symbol"] == "O":
                    opponent_details["symbol"] = "X"
                else:
                    opponent_details["symbol"] = "O"

                lbl_status["text"] = "STATUS: " + opponent_details["name"] + " is connected!"
                sleep(0.5)
                # is it your turn to play? hey! 'O' comes before 'X'
                if radio_value == "1":
                    lbl_status["text"] = "STATUS: Your turn!"
                    your_turn = True
                    you_started = True
                elif radio_value == "2":
                    lbl_status["text"] = "STATUS: " + opponent_details["name"] + "'s turn!"
                    you_started = False
                    your_turn = False
            elif from_server.startswith("$xy$".encode()):
                temp = from_server.replace("$xy$".encode(), "".encode())
                _x = temp[0:temp.find("$".encode())]
                _y = temp[temp.find("$".encode()) + 1:len(temp)]

                # update board
                label_index = int(_x) * num_cols + int(_y)
                label = list_labels[label_index]
                label["symbol"] = opponent_details["symbol"]
                label["label"]["text"] = opponent_details["symbol"]
                label["label"].config(foreground=opponent_details["color"])
                label["ticked"] = True

                # Does this coordinate leads to a win or a draw
                result = game_logic()
                if result[0] is True and result[1] != "":  # opponent win
                    opponent_details["score"] = opponent_details["score"] + 1
                    if result[1] == opponent_details["symbol"]:  #
                        lbl_status["text"] = "Game over, You Lost! You(" + str(your_details["score"]) + ") - " \
                                                                                                        "" + \
                                             opponent_details["name"] + "(" + str(opponent_details["score"]) + ")"
                        lbl_status.config(foreground="red")

                        if your_details["symbol"] == "X":

                            player = next((pl for pl in players_list if pl.name == your_details["name"]), None)
                            player2 = next((pl for pl in players_list if pl.name == opponent_details["name"]), None)
                            if player is not None:
                                players_list.remove(player)
                                player.num_of_games += 1
                                player.num_of_looses += 1
                                players_list.append(Player(player.name, player.num_of_games, player.num_of_wins,
                                                           player.num_of_looses))
                            else:
                                players_list.append(Player(your_details["name"], 1, 0, 1))

                            if player2 is not None:
                                players_list.remove(player2)
                                player2.num_of_games += 1
                                player2.num_of_wins += 1
                                players_list.append(Player(player2.name, player2.num_of_games, player2.num_of_wins,
                                                           player2.num_of_looses))
                            else:
                                players_list.append(Player(opponent_details["name"], 1, 1, 0))

                            game_list.append(Game(datetime.now().strftime("%d/%m/%Y %H:%M:%S"), your_details["name"],
                                                  opponent_details["name"], opponent_details["name"]))

                            save_players_to_file()
                            save_games_to_file()

                        winsound.PlaySound('sound.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)

                        play_again.grid(row=4, columnspan=3)
                        lbl_play_again.grid(row=5, columnspan=3)
                        count_down()
                        terminated = False


                elif result[0] is True and result[1] == "":  # a draw
                    lbl_status["text"] = "Game over, Draw! You(" + str(your_details["score"]) + ") - " \
                                                                                                "" + opponent_details[
                                             "name"] + "(" + str(opponent_details["score"]) + ")"
                    lbl_status.config(foreground="blue")

                    play_again.grid(row=4, columnspan=3)
                    lbl_play_again.grid(row=5, columnspan=3)
                    count_down()
                    terminated = False


                else:
                    your_turn = True
                    lbl_status["text"] = "STATUS: Your turn!"
                    lbl_status.config(foreground="black")
        except ConnectionResetError:
            with open('log.txt', 'a') as f:
                f.write(f'server connection is closed.')

    sck.close()


def try_connect_to_server():
    """ Try To Connect To Server

        Try To Connect To server To check If The Server Is Connected Or Not

        Parameters
        ----------
        No Parameters

        Returns
        -------
        No Return.
        """
    global client, HOST_PORT, HOST_ADDR
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((TEST_HOST_ADDR, TEST_HOST_PORT))
        client.send('sync'.encode())
        # start a thread to keep receiving message from server
        # do not block the main thread :)
        threading._start_new_thread(check_connection_with_server, (client, "m"))

    except Exception as e:
        client.close()
        window_main.destroy()


def check_connection_with_server(sck, m):
    """ Check Connection With Server

        Parameters
        ----------
        No Parameters

        Returns
        -------
        No Return.
        """
    ack = sck.recv(4096).decode()
    sck.close()


try_connect_to_server()
window_main.mainloop()

# connect and send name to server
# when two player connects, server sends opponent name, symbol
# p1: $name$charles$symbol$O
# client with symbol of O starts
# when client receive opponent position, then it's their turn to play
# check if I win or draw each time I choose play or receive coordinate
