from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QSize, QMargins

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        self.win = QWidget()

        # window settings
        self.win.setWindowTitle("CRYSEC - Secure Messager")
        self.win.setFixedSize(QSize(700, 700))

        mainBox = QHBoxLayout(self.win)
        mainBox.setContentsMargins(QMargins(10, 10, 10, 10))

        chatBox = QVBoxLayout() #Layout for chat
        settingsBox = QVBoxLayout() # Layout for settings

        # ScrollArea settings
        scrollChat = QScrollArea(alignment=Qt.AlignmentFlag.AlignCenter)
        scrollChat.setWidgetResizable(False)

        # Set scroll to vertical not horizontal
        scrollChat.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scrollChat.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # ScrollArea Content
        scrollContainer = QWidget()
        scrollContainer.setFixedWidth(scrollChat.width())
        self.scrollLayout = QVBoxLayout(scrollContainer)

        # Send message to server textbox
        sendChat = QHBoxLayout()
        self.chatText = QTextEdit(placeholderText="Send a message")
        self.chatText.setMaximumHeight(30)
        self.btnSend = QPushButton("Send")    

        sendChat.addWidget(self.chatText)
        sendChat.addWidget(self.btnSend)

        #Example to add chat field to scrollArea
        for i in range(1, 200):
            self.addChatField("wads")

        # Checkbox for Serv only (Task)
        self.servOnly = QCheckBox("Send to serv ONLY")

        # CHoosing encoding method
        encodeLayout = QHBoxLayout()

        self.encoding = QComboBox()
        self.encoding.setMaximumWidth(120)


        self.encoding.addItem("Shift")
        self.encoding.addItem("Vegenere")
        self.encoding.addItem("RSA")
        self.encoding.addItem("DiffieHellman")
        self.encoding.addItem("Hashing")

        
        encodeLayout.addWidget(self.servOnly)
        encodeLayout.addWidget(self.encoding)

        # Key textfield
        
        keyLayout = QHBoxLayout()

        keyLabel = QLabel("Key: ")
        keyLabel.setMaximumWidth(50)

        
        self.keyText = QTextEdit(placeholderText="Encoding Key")
        self.keyText.setMaximumHeight(30)

        keyLayout.addWidget(keyLabel)
        keyLayout.addWidget(self.keyText)

        # Adding layouts and Widgets to parents

        scrollChat.setWidget(scrollContainer)
        chatBox.addWidget(scrollChat)
        chatBox.addLayout(sendChat)
        
        settingsBox.addWidget(scrollChat)
        settingsBox.addLayout(encodeLayout)
        settingsBox.addLayout(keyLayout)

        mainBox.addLayout(chatBox)
        mainBox.addLayout(settingsBox)

        self.setLayout(mainBox)
    

    # Adds a text/chat display to the UI
    def addChatField(self, chatText: str, isSend: bool=False):
        label = QLabel(chatText)  
        label.setFixedWidth(300)
        label.setMargin(10)
        label.setWordWrap(True)

        if isSend:
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            label.setStyleSheet("background-color: #CDFFC2; border-radius: 10px; color: black")  
        else:
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            label.setStyleSheet("background-color: #C9C9C9; border-radius: 10px; color: black")   
        self.scrollLayout.addWidget(label) 
    