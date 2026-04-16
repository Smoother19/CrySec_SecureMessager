from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QSize, QMargins


import threading
from MessageTransferer import *
from ConnectionHandler import *
from MessageHandler import *
from cli import *

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

        
        settingsBox.addLayout(encodeLayout)
        settingsBox.addLayout(self.settingsDynamicLayout)

        mainBox.addLayout(chatBox)
        mainBox.addLayout(settingsBox)

        self.setCentralWidget(self.win)

        self.startConnection()
        self.parser = cli_parser(self.connection)
        self.textSignal = MessageTransferer()
        # Set event for handling messages reception
        self.textSignal.text.connect(self.handleServerReceptionToWindw)
        self.connection.set_callback(self.textSignal.emitText)


    
    # Button to send event
    def btnSendMsg(self):
        text = self.chatText.toPlainText()        
        if text:                      
            msgEncr = ""
            match self.encoding.currentText():
                case "Shift": 
                    shftKey = int(self.shiftkeyText.toPlainText())
                    if shftKey is not None:
                        msgEncr = self.connection.message_handler.encode_shift(text, shftKey)
                    else:
                        self.addChatField("Error: Wrong Shift Key value")
                        raise ValueError
                case "Vegenere": 
                    vgnrKey = self.shiftkeyText.toPlainText()
                    if shftKey is not None:
                        msgEncr = self.connection.message_handler.encode_vigenere(vgnrKey)
                    else:
                        self.addChatField("Error: Wrong Vegenere Key value")
                        raise ValueError
                case "RSA": 
                    if self.rsaShared_key is not None and self.rsaE is not None and self.rsaPrivate_key is not None :
                        print("Aled je cé pa koa fèr")
                        #Faire l'encryption RSA mais je comprend pas les paramètres

                    else:
                        self.addChatField("Error: Wrong RSA data. Have you generated RSA keys?")
                        raise ValueError
                
                case "DiffieHellman": 
                    print("wasd")
                case "Hashing": 
                    print("wasd")
            if self.servOnly.isChecked():
                self.connection.send_message(msgEncr, 's')
                print("wasd")
            else:  
                self.connection.send_message(msgEncr)
                print("wasd")
            self.addChatField(text, True)
            self.chatText.clear()
        else:
            print("Text vide")

    def btnSendTaskShift(self):
        key = 0
        try:
            key = int(self.shiftkeyText.toPlainText())
            if (key > 0):
                #Commande: 
                self.parser._cmd_encode(self.parser, "shift", key) # A adapter à la commande car aled on cé pa
            else:
                raise ValueError
        except ValueError:
            self.addChatField("Error: Wrong Shift key value !")

    def btnSendTaskVegenere(self):
        key = ""
        try:
            key = self.txtVegenKey.toPlainText()
            if (key is not None):
                #Commande: 
                self.parser._cmd_encode(self.parser, "vegenere", key) # A adapter à la commande car aled on cé pa
            else:
                raise ValueError
        except ValueError:
            self.addChatField("Error: Wrong Vegenere key value !")

    
    # Button to generate RSA keys event
    def btnGenRSAKey(self):
        size = int(self.rsaKeyLen.toPlainText())
        
        if self.size is not None:
            if  size < 2048:
                self.addChatField("Error: RSA key length too small (< 2048)")
                raise ValueError
            else:
                self.rsaShared_key, self.rsaE, self.rsaPrivate_key = self.connection.message_handler.rsa_keygen(size)
        else:
            self.addChatField("Error: Wrong RSA key length value")
            raise ValueError


    # Selecting encondig method event
    def cmbChangedSelected(self):
        text = self.encoding.currentText()
        
        self.clearLayout(self.settingsDynamicLayout) # Clear the settings layout
        match text:
            case "Shift": 

                # Create layout for rsa encoding
                self.shiftLayout = QVBoxLayout()
                keyLayout = QHBoxLayout()

                # Field for the private key
                keyLabel = QLabel("Key : ")
                keyLabel.setMaximumWidth(50)
                
                self.shiftkeyText = QTextEdit(placeholderText="Keys length")
                self.shiftkeyText.setMaximumHeight(30)

                keyLayout.addWidget(keyLabel)
                keyLayout.addWidget(self.shiftkeyText)
               

                # Button to generate RSA keys
                self.btnSendShift = QPushButton("Send Task")
                self.btnSendShift.clicked.connect(self.btnSendTaskShift)

                self.shiftLayout.addWidget(self.btnSendShift)
                self.shiftLayout.addLayout(keyLayout)
                self.settingsDynamicLayout.addLayout(self.shiftLayout)
            case "Vegenere": 
                # Create layout for rsa encoding
                self.vegenLayout = QVBoxLayout()
                keyLayout = QHBoxLayout()

                # Field for the private key
                keyLabel = QLabel("Key : ")
                keyLabel.setMaximumWidth(50)
                
                self.txtVegenKey = QTextEdit(placeholderText="Key")
                self.txtVegenKey.setMaximumHeight(30)

                keyLayout.addWidget(keyLabel)
                keyLayout.addWidget(self.txtVegenKey)
               

                # Button to generate RSA keys
                self.btnSendVegen = QPushButton("Send Task")
                self.btnSendVegen.clicked.connect(self.btnSendTaskVegenere)

                self.vegenLayout.addWidget(self.btnSendVegen)
                self.vegenLayout.addLayout(keyLayout)
                self.settingsDynamicLayout.addLayout(self.vegenLayout)
            case "RSA": 
                # Create layout for rsa encoding
                self.rsaLayout = QVBoxLayout()
                privateLayout = QHBoxLayout()

                # Field for the private key
                privateLabel = QLabel("Keys Length : ")
                privateLabel.setFixedWidth(70)
                
                self.rsaKeyLen = QTextEdit(placeholderText="Keys length")
                self.rsaKeyLen.setMaximumHeight(30)

                privateLayout.addWidget(privateLabel)
                privateLayout.addWidget(self.rsaKeyLen)
               

                # Button to generate RSA keys
                self.btnGenerateRSA = QPushButton("Generate")
                self.btnGenerateRSA.clicked.connect(self.btnGenRSAKey)

                self.rsaLayout.addLayout(privateLayout)
                self.rsaLayout.addWidget(self.btnGenerateRSA)
                self.settingsDynamicLayout.addLayout(self.rsaLayout)
            case "DiffieHellman": 
                print("DiffieHellman")
            case "Hashing": 
                print("Hashing")
        # TODO Pour corriger l'align des settings je pourrai passer le parent en self mais c'est bof

        
    # CLears a layout of it's wigets AND layouts
    def clearLayout(self, layout:QLayout):
        for widget_no in range(0,layout.count()):
            if layout.itemAt(widget_no) != None:
                if "Layout" not in str(layout.itemAt(widget_no)):
                    layout.itemAt(widget_no).widget().deleteLater()
                else:
                    self.clearLayout(layout.itemAt(widget_no))


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
    
    def handleServerReceptionToWindw(self, message):
        self.parser.handle_server_message(message)
        self.addChatField(message)

    def startConnection(self):
        try:
            self.connection = ConnectionHandler()
        except Exception as e:
            print(f"Error : {e}")

        self.receive_msg = threading.Thread(target=self.connection.receive_message)
        self.receive_msg.setDaemon(True)
        self.receive_msg.start()    
        

    def closeEvent(self, event):
        self.connection.closeConnection()
        return super().closeEvent(event)
