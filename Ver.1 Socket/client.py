import os
import time
import socket
import win32ui
import win32gui
import win32con
import win32api
import tempfile
from PIL import Image

IP = socket.gethostname()
PORT = 13337
DISCONNECT_MESSAGE = b"!BEGONE"
FORMAT = "utf-8"
HEADER = 7
Shotted_WIDTH = win32api.GetSystemMetrics(0)
Shotted_HEIGHT = win32api.GetSystemMetrics(1)
IMAGE_NAME = os.path.join(tempfile.gettempdir(), "x")
global RECONNECT_DELAY, MAX_RECONNECT_DELAY
RECONNECT_DELAY = 5
MAX_RECONNECT_DELAY = 60

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

def click(x, y):
    win32api.SetCursorPos((x, y))
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
    time.sleep(0.01)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)


def screenshot(name):
    hwnd = win32gui.FindWindow(None, 'explorer.exe')
    wDC = win32gui.GetWindowDC(hwnd)
    dcObj=win32ui.CreateDCFromHandle(wDC)
    cDC=dcObj.CreateCompatibleDC()
    dataBitMap = win32ui.CreateBitmap()
    dataBitMap.CreateCompatibleBitmap(dcObj, Shotted_WIDTH, Shotted_HEIGHT)
    cDC.SelectObject(dataBitMap)
    cDC.BitBlt((0,0), (Shotted_WIDTH, Shotted_HEIGHT), dcObj, (0,0), win32con.SRCCOPY)
    dataBitMap.SaveBitmapFile(cDC, f"{name}.bmp")
    im = Image.open(f"{name}.bmp")
    im = im.convert("RGB")
    im.save(f"{name}.jpg")
    os.remove(f"{name}.bmp")

    # Free Resources
    dcObj.DeleteDC()
    cDC.DeleteDC()
    win32gui.ReleaseDC(hwnd, wDC)
    win32gui.DeleteObject(dataBitMap.GetHandle())


def connect(IP, PORT):
    global RECONNECT_DELAY, MAX_RECONNECT_DELAY
    while RECONNECT_DELAY != MAX_RECONNECT_DELAY:
        try:
            client.connect((IP, PORT))
            break
        except (ConnectionRefusedError, OSError):
            time.sleep(RECONNECT_DELAY)
            RECONNECT_DELAY = min(RECONNECT_DELAY * 2, MAX_RECONNECT_DELAY)
            print("Trying again...")
            continue

connect(IP, PORT)

while True:
    try:
        command = client.recv(HEADER)
        if command == b"<START>":
            while True:
                status = client.recv(HEADER)
                if status == b"<GET>":
                    screenshot(IMAGE_NAME)
                    with open(f"{IMAGE_NAME}.jpg", "rb") as file:
                        file_size = os.path.getsize(f"{IMAGE_NAME}.jpg")
                        file_size = str(file_size).encode(FORMAT)
                        file_content = file.read()

                    client.send(file_size)
                    client.sendall(file_content)
                    client.send("<END>".encode(FORMAT))
                elif status == b"<CLICK>": # Need better synchronize
                    try:
                        x = int(client.recv(HEADER).decode())
                        time.sleep(0.3)
                        y = int(client.recv(HEADER).decode())
                        click(x, y)
                    except ValueError: # Better ways of handling this
                        continue
                elif status == b"<STOP>":
                    print("Stopped signal received")
                    os.remove(f"{IMAGE_NAME}.jpg")
                    break
        elif command == b"<SCRL>":
            client.send(str(Shotted_WIDTH).encode(FORMAT))
            client.send(str(Shotted_HEIGHT).encode(FORMAT)) 
        elif command == DISCONNECT_MESSAGE:
            exit()
    except (ConnectionResetError, ConnectionAbortedError, socket.error) as e:
        print(f"Connection error: {e}")
        print("Server crashed or connection lost, reconnecting...")
        client.close()
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connect(IP, PORT)
