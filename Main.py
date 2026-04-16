
from cli import *
from PySide6.QtWidgets import QApplication
from MainWindow import MainWindow


import threading
from MessageTransferer import *
from ConnectionHandler import *
from MessageHandler import *
'''
try:
    connection = ConnectionHandler()
except Exception as e:
    print(f"Error : {e}")

receive_msg = threading.Thread(target=connection.receive_message)
receive_msg.start()  

parser = cli_parser(connection)




print("Connection established. Type /help for a list of commands.")

while True:
    msg = input('>')
    
    cmd, args = parser.parse_args(msg)
    
    parser.execute_command(cmd, args)

'''
app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())
