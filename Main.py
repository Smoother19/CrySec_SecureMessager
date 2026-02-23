from ConnectionHandler import *
from MessageHandler import *
import threading

try:
    connection = ConnectionHandler()
except Exception as e:
    print(f"Error : {e}")

receive_msg = threading.Thread(target=connection.receive_message)
receive_msg.start()

while True:
    msg = input('Enter your message: ')
    connection.send_message(msg)