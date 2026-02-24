from ConnectionHandler import *
from MessageHandler import *
from cli import *
import threading

try:
    connection = ConnectionHandler()
except Exception as e:
    print(f"Error : {e}")

parser = cli_parser(connection)


receive_msg = threading.Thread(target=connection.receive_message)
receive_msg.start()

print("Connection established. Type /help for a list of commands.")

while True:
    msg = input('>')
    
    cmd, args = parser.parse_args(msg)
    
    parser.execute_command(cmd, args)