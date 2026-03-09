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
        settingsBox.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ScrollArea settings
        scrollChat = QScrollArea(alignment=Qt.AlignmentFlag.AlignCenter)
        scrollChat.setWidgetResizable(True)
       

        # Set scroll to vertical not horizontal
        scrollChat.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        scrollChat.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # ScrollArea Content
        scrollContainer = QWidget()
        scrollContainer.setFixedWidth(scrollChat.width())
        self.scrollLayout = QVBoxLayout(scrollContainer)
    
        self.scrollLayout.setAlignment(Qt.AlignmentFlag.AlignBottom)

        scrollChat.setWidget(scrollContainer)

        # Send message to server textbox
        sendChat = QHBoxLayout()
        self.chatText = QTextEdit(placeholderText="Send a message")
        self.chatText.setMaximumHeight(30)
        self.btnSend = QPushButton("Send")
        self.btnSend.clicked.connect(self.btnSendMsg)

        sendChat.addWidget(self.chatText)
        sendChat.addWidget(self.btnSend)

        # Checkbox for Serv only (Task)
        self.servOnly = QCheckBox("Send to serv ONLY")

        # CHoosing encoding method
        encodeLayout = QHBoxLayout()

        self.encoding = QComboBox()
        self.encoding.currentIndexChanged.connect(self.cmbChangedSelected)
        self.encoding.setMaximumWidth(120)


        self.encoding.addItem("Shift")
        self.encoding.addItem("Vegenere")
        self.encoding.addItem("RSA")
        self.encoding.addItem("DiffieHellman")
        self.encoding.addItem("Hashing")

        
        encodeLayout.addWidget(self.servOnly)
        encodeLayout.addWidget(self.encoding)


        self.settingsDynamicLayout = QVBoxLayout()


        # Adding layouts and Widgets to parents

        scrollChat.setWidget(scrollContainer)
        chatBox.addWidget(scrollChat)
        chatBox.addLayout(sendChat)

        
        settingsBox.addWidget(scrollChat)
        settingsBox.addLayout(encodeLayout)
        settingsBox.addLayout(self.settingsDynamicLayout)

        mainBox.addLayout(chatBox)
        mainBox.addLayout(settingsBox)

        self.setCentralWidget(self.win)

    
    # Button to send event
    def btnSendMsg(self):
        text = self.chatText.toPlainText()
        if text:
            self.addChatField(text, True)
        else:
            print("Text vide")

    
    # Button to generate RSA keys event
    def btnGenRSAKey(self):
        print("Generating RSA")


    # Selecting encondig method event
    def cmbChangedSelected(self):
        text = self.encoding.currentText()
        
        self.clearLayout(self.settingsDynamicLayout) # Clear the settings layout
        match text:
            case "Shift": 
                # Create layout for shift encoding
                self.shiftLayout = QHBoxLayout()

                # Field for the key
                keyLabel = QLabel("Key : ")
                keyLabel.setMaximumWidth(50)
                
                self.shiftkeyText = QTextEdit(placeholderText="Encoding Key")
                self.shiftkeyText.setMaximumHeight(30)


                self.shiftLayout.addWidget(keyLabel)
                self.shiftLayout.addWidget(self.shiftkeyText)
                self.settingsDynamicLayout.addLayout(self.shiftLayout)
            case "Vegenere": 
                # Create layout for vegenere encoding
                self.vegenereLayout = QHBoxLayout()

                # Field for the key
                keyLabel = QLabel("Word : ")
                keyLabel.setMaximumWidth(50)
                
                self.vegenerekeyText = QTextEdit(placeholderText="Encoding Key")
                self.vegenerekeyText.setMaximumHeight(30)


                self.vegenereLayout.addWidget(keyLabel)
                self.vegenereLayout.addWidget(self.vegenerekeyText)
                self.settingsDynamicLayout.addLayout(self.vegenereLayout)
            case "RSA": 
                # Create layout for rsa encoding
                self.rsaLayout = QVBoxLayout()
                privateLayout = QHBoxLayout()
                publicLayout = QHBoxLayout()

                # Field for the private key
                privateLabel = QLabel("Private Key : ")
                privateLabel.setFixedWidth(70)
                
                self.rsaPrivateText = QTextEdit(placeholderText="Private Key")
                self.rsaPrivateText.setMaximumHeight(30)

                privateLayout.addWidget(privateLabel)
                privateLayout.addWidget(self.rsaPrivateText)

                # Field for the public key
                publicLabel = QLabel("Public Key : ")
                publicLabel.setFixedWidth(70)
                
                self.rsaPublicText = QTextEdit(placeholderText="Public Key")
                self.rsaPublicText.setMaximumHeight(30)

                # Button to generate RSA keys
                self.btnGenerateRSA = QPushButton("Generate")
                self.btnGenerateRSA.clicked.connect(self.btnGenRSAKey)

                publicLayout.addWidget(publicLabel)
                publicLayout.addWidget(self.rsaPublicText)

                self.rsaLayout.addLayout(privateLayout)
                self.rsaLayout.addLayout(publicLayout)
                self.rsaLayout.addWidget(self.btnGenerateRSA)
                self.settingsDynamicLayout.addLayout(self.rsaLayout)
            case "DiffieHellman": 
                print("DiffieHellman")
            case "Hashing": 
                print("Hashing")

        
    # CLears a layout of it's wigets AND layouts
    def clearLayout(self, layout: QLayout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                if item is not None:
                    while item.count():
                        subitem = item.takeAt(0)
                        widget = subitem.widget()
                        if widget is not None:
                            widget.setParent(None)
                    layout.removeItem(item)


    # Adds a text/chat display to the UI
    def addChatField(self, chatText: str, isSend: bool=False):        
        label = QLabel(chatText)  
        label.setFixedWidth(300)
        label.setFixedHeight(30)
        label.setMargin(10)
        label.setWordWrap(True)        

        if isSend:
            label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            label.setStyleSheet("background-color: #CDFFC2; border-radius: 10px; color: black")  
        else:
            label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            label.setStyleSheet("background-color: #C9C9C9; border-radius: 10px; color: black")   
            
        self.scrollLayout.addWidget(label) 
    