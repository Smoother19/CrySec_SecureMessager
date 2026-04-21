from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QSize, QMargins
from PySide6.QtGui import QFont


import threading
from MessageTransferer import *
from ConnectionHandler import *
from MessageHandler import *
from cli import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        
        self.win = QWidget()

        self.fontNew = QFont("Consolas", 10)

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
        self.servOnly.stateChanged.connect(self.checkOnlyServ)

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

        # Set cmb box to first item and doesnt generate any error 
        self.encoding.setCurrentIndex(1) 
        self.encoding.setCurrentIndex(0)


    
    # Button to send event
    def btnSendMsg(self):
        text = self.chatText.toPlainText()        
        if text:                      
            msgEncr = ""
            match self.encoding.currentText():
                case "Shift": 
                    ...
                case "Vegenere": 
                    vgnrKey = self.shiftkeyText.toPlainText()
                    if vgnrKey is not None:
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
        key_len = 0
        try:
            key_len = int(self.shiftkeyText.toPlainText())
            if (key_len > 0):
                #Commande: 
                self.parser._cmd_send(["-s", "task", "shift", "encode", f"{key_len}"]) # Pass cli cmd args
                self.btnSendShift.setEnabled(False)
                self.shiftkeyText.setEnabled(False)                
                self.btnSendShifted.setEnabled(True)
                self.shiftedKey.setEnabled(True)
                self.shiftedMsgText.setEnabled(True)

            else:
                raise ValueError
        except ValueError:
            self.addChatField("Error: Wrong Shift key length !")
        self.shiftkeyText.setPlainText("")
    
    def btnSendShiftedMsg(self):
        key = 0
        try:
            key = int(self.shiftedKey.toPlainText())
            msg = self.shiftedMsgText.toPlainText()
            if (key > 0 and msg is not None):
                #Commande: 
                encoded = self.connection.message_handler.encode_shift(msg, key)
                self.connection.send_message(encoded, "s")
                self.btnSendShift.setEnabled(False)
                self.btnSend.setEnabled(True)
                self.shiftkeyText.setEnabled(False)

            else:
                raise ValueError
        except ValueError:
            self.addChatField("Error: Wrong Shift key length !")
        except:
            self.addChatField("Error: Something went wrong ! (Maybe it's the server ?)")
        self.shiftkeyText.setPlainText("")
        

    def btnSendTaskVegenere(self):
        key_len = 0
        try:
            key_len = int(self.shiftkeyText.toPlainText())
            if (key_len > 0):
                #Commande: 
                self.parser._cmd_send(["-s", "task", "vegenere", "encode", f"{key_len}"]) # Pass cli cmd args
                self.btnSendVgnr.setEnabled(False)
                self.vgnrkeyText.setEnabled(False)                
                self.btnSendVgnred.setEnabled(True)
                self.vgnredKey.setEnabled(True)
                self.vgnredMsgText.setEnabled(True)

            else:
                raise ValueError
        except ValueError:
            self.addChatField("Error: Wrong Shift key length !")
        self.shiftkeyText.setPlainText("")

    
    def btnSendVegeneredMsg(self):
        key = 0
        try:
            key = int(self.vgnredKey.toPlainText())
            msg = self.vgnredMsgText.toPlainText()
            if (key > 0 and msg is not None):
                #Commande: 
                encoded = self.connection.message_handler.encode_vigenere(msg, key)
                self.connection.send_message(encoded, "s")
                self.btnSendVgnr.setEnabled(False)
                self.btnSend.setEnabled(True)
                self.vgnrkeyText.setEnabled(False)

            else:
                raise ValueError
        except ValueError:
            self.addChatField("Error: Wrong Shift key length !")
        except:
            self.addChatField("Error: Something went wrong ! (Maybe it's the server ?)")
        self.shiftkeyText.setPlainText("")

    def btnSendTaskRSA(self):
        ...

    
    # Button to generate RSA keys event
    def btnGenRSAKey(self):
        size = int(self.rsaKeyLen.toPlainText())
        
        if self.size is not None:
            if  size < 2048:
                self.addChatField("Error: RSA key length too small (< 2048)")
                raise ValueError
            else:
                self.rsaShared_key, self.rsaE, self.rsaPrivate_key = self.connection.message_handler.rsa_keygen(size)
                self.btnRSATask.setEnabled(True)
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
                msgLayout = QHBoxLayout()
                shftlayout = QHBoxLayout()

                # Field for the private key
                keyLabel = QLabel("Key length : ")
                keyLabel.setMaximumWidth(50)
                
                self.shiftkeyText = QTextEdit(placeholderText="Keys length")
                self.shiftkeyText.setMaximumHeight(30)

                # Field for the private key
                lblMsg = QLabel("Message (encoded) : ")
                lblMsg.setMaximumWidth(50)
                
                self.shiftedMsgText = QTextEdit(placeholderText="Shifted Message")
                self.shiftedMsgText.setMaximumHeight(30)
                self.shiftedMsgText.setEnabled(False)

                # Field for the private key
                lblshiftkey = QLabel("Key : ")
                lblshiftkey.setMaximumWidth(50)
                
                self.shiftedKey = QTextEdit(placeholderText="Key")
                self.shiftedKey.setMaximumHeight(30)
                self.shiftedKey.setEnabled(False)

                keyLayout.addWidget(keyLabel)
                keyLayout.addWidget(self.shiftkeyText)

                msgLayout.addWidget(lblMsg)                
                msgLayout.addWidget(self.shiftedMsgText)

                shftlayout.addWidget(lblshiftkey)                
                shftlayout.addWidget(self.shiftedKey)

                self.btnSendShifted = QPushButton("Encode and Send")
                self.btnSendShifted.clicked.connect(self.btnSendShiftedMsg)
                self.btnSendShifted.setEnabled(False)
               

                # Button to generate RSA keys
                self.btnSendShift = QPushButton("Send Task")
                self.btnSendShift.clicked.connect(self.btnSendTaskShift)

                self.shiftLayout.addLayout(keyLayout)
                self.shiftLayout.addWidget(self.btnSendShift)
                self.shiftLayout.addLayout(msgLayout)
                self.shiftLayout.addLayout(shftlayout)
                self.shiftLayout.addWidget(self.btnSendShifted)
                self.settingsDynamicLayout.addLayout(self.shiftLayout)
            case "Vegenere": 
                # Create layout for rsa encoding
                self.vegenereLayout = QVBoxLayout()
                keyLayout = QHBoxLayout()
                msgLayout = QHBoxLayout()
                vgnrlayout = QHBoxLayout()

                # Field for the private key
                keyLabel = QLabel("Key length : ")
                keyLabel.setMaximumWidth(50)
                
                self.vgnrkeyText = QTextEdit(placeholderText="Keys length")
                self.vgnrkeyText.setMaximumHeight(30)

                # Field for the private key
                lblMsg = QLabel("Message (encoded) : ")
                lblMsg.setMaximumWidth(50)
                
                self.vgnredMsgText = QTextEdit(placeholderText="Vegenere Encoded Message")
                self.vgnredMsgText.setMaximumHeight(30)
                self.vgnredMsgText.setEnabled(False)

                # Field for the private key
                lblshiftkey = QLabel("Key : ")
                lblshiftkey.setMaximumWidth(50)
                
                self.vgnredKey = QTextEdit(placeholderText="Key")
                self.vgnredKey.setMaximumHeight(30)
                self.vgnredKey.setEnabled(False)

                keyLayout.addWidget(keyLabel)
                keyLayout.addWidget(self.vgnrkeyText)

                msgLayout.addWidget(lblMsg)                
                msgLayout.addWidget(self.vgnredMsgText)

                vgnrlayout.addWidget(lblshiftkey)                
                vgnrlayout.addWidget(self.vgnredKey)

                self.btnSendVgnred = QPushButton("Encode and Send")
                self.btnSendVgnred.clicked.connect(self.btnSendShiftedMsg)
                self.btnSendVgnred.setEnabled(False)
               

                # Button to generate RSA keys
                self.btnSendVgnr = QPushButton("Send Task")
                self.btnSendVgnr.clicked.connect(self.btnSendTaskShift)

                self.vegenereLayout.addLayout(keyLayout)
                self.vegenereLayout.addWidget(self.btnSendVgnr)
                self.vegenereLayout.addLayout(msgLayout)
                self.vegenereLayout.addLayout(vgnrlayout)
                self.vegenereLayout.addWidget(self.btnSendVgnred)
                self.settingsDynamicLayout.addLayout(self.vegenereLayout)
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
                self.btnGenerateRSA = QPushButton("Send Task")
                self.btnGenerateRSA.clicked.connect(self.btnGenRSAKey)

                
                # Button to send RSA task
                self.btnRSATask = QPushButton("Generate")
                self.btnRSATask.clicked.connect(self.btnSendTaskRSA)
                self.btnRSATask.setEnabled(False)

                self.rsaLayout.addLayout(privateLayout)
                self.rsaLayout.addWidget(self.btnGenerateRSA)
                self.rsaLayout.addWidget(self.btnRSATask)
                self.settingsDynamicLayout.addLayout(self.rsaLayout)
            case "DiffieHellman": 
                print("DiffieHellman")
            case "Hashing": 
                print("Hashing")
        
        self.btnSend.setEnabled(False)


    def checkOnlyServ(self):
        self.chatText.setEnabled(not self.servOnly.isChecked())
        self.btnSend.setEnabled(not self.servOnly.isChecked())
        
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
        label.setMinimumHeight(30)
        label.setMargin(10)
        label.setFont(self.fontNew)
        label.setWordWrap(True)   
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)     

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
