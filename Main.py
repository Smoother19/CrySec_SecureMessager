from ConnectionHandler import *
from MessageHandler import *
import threading
from PySide6.QtWidgets import QApplication
from MainWindow import MainWindow

try:
    connection = ConnectionHandler()
except Exception as e:
    print(f"Error : {e}")

app = QApplication()
window = MainWindow()
window.show()

app.exec()


# Recieve messages from server on a separate thread
receive_msg = threading.Thread(target=connection.receive_message)
receive_msg.start()


while True:
    #Send message to server
    msg = input('Enter your message: ')
    connection.send_message(msg)
