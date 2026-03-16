
from cli import *
from PySide6.QtWidgets import QApplication
from MainWindow import MainWindow



#parser = cli_parser(connection)




print("Connection established. Type /help for a list of commands.")
'''
while True:
    msg = input('>')
    
    cmd, args = parser.parse_args(msg)
    
    parser.execute_command(cmd, args)

'''
app = QApplication()
window = MainWindow()
window.show()

app.exec()
