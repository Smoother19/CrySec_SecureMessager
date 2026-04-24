from PySide6.QtWidgets import *
from PySide6.QtCore import Qt, QSize, QMargins
from PySide6.QtGui import QFont


import threading
import time

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
        self.chatText.setEnabled(False)
        self.chatText.setMaximumHeight(30)
        self.btnSend = QPushButton("Send")
        self.btnSend.clicked.connect(self.btnSendMsg)
        self.btnSend.setEnabled(False)

        sendChat.addWidget(self.chatText)
        sendChat.addWidget(self.btnSend)

        # Checkbox for Serv only (Task)
        self.servOnly = QCheckBox("Send to serv ONLY")
        self.servOnly.stateChanged.connect(self.checkOnlyServ)
        self.servOnly.setChecked(True)

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
            self.connection.send_message(text)
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
            key_len = int(self.vgnrkeyText.toPlainText())
            if (key_len > 0):
                #Commande: 
                print(key_len)
                self.parser._cmd_send(["-s", "task", "vigenere", "encode", f"{key_len}"]) # Pass cli cmd args
                self.btnSendVgnr.setEnabled(False)
                self.vgnrkeyText.setEnabled(False)                
                self.btnSendVgnred.setEnabled(True)
                self.vgnredKey.setEnabled(True)

            else:
                raise ValueError
        except ValueError:
            self.addChatField("Error: Wrong Vegenere msg length !")
        self.vgnrkeyText.setPlainText("")

    
    def btnSendVegeneredMsg(self):
        key = ""
        try:
            key = self.vgnredKey.toPlainText()
            msg = self.vgnredMsgText.toPlainText()
            if (key is not None and msg is not None):
                #Commande: 
                self.parser._cmd_encode(["vigenere", f"{key}"])
                self.parser._cmd_send(["-s", "encoded"])
                self.btnSendVgnr.setEnabled(False)
                self.btnSend.setEnabled(True)
                self.vgnrkeyText.setEnabled(False)

            else:
                raise ValueError
        except ValueError:
            self.addChatField("Error: Wrong Shift key length !")
        except:
            self.addChatField("Error: Something went wrong ! (Maybe it's the server ?)")
        self.vgnredKey.setPlainText("")
    
    # Button to generate RSA keys event
    def btnSendTaskRSA(self):
        key_len = 0
        try:
            key_len = int(self.rsaMsgLen.toPlainText())
            if (key_len > 0):
                #Commande: 
                self.parser._cmd_send(["-s", "task", "RSA", "encode", f"{key_len}"]) # Pass cli cmd args
                self.rsaMsgLen.setEnabled(False)
                self.btnRSATask.setEnabled(False)                
                self.btnRSAEncoding.setEnabled(True)

            else:
                raise ValueError
        except ValueError:
            self.addChatField("Error: Wrong RSA msg length value !")
        self.rsaMsgLen.setPlainText("")
    
    def btnSendRSAEncoding(self):
        try:
            #Commande: 
            self.parser._cmd_encode(["rsa"]) # Pass cli cmd args
            self.parser._cmd_send(["-s", "encoded"]) # Pass cli cmd args
            self.btnRSAEncoding.setEnabled(False)
            self.rsaMsgLen.setEnabled(True)
            self.btnRSATask.setEnabled(True)
        except:
            self.addChatField("Error: Something went wrong ! (Maybe it's the server ?)")

    def btnSendDifHelTask(self):
        self.parser._cmd_send(["-s", "task", "DifHel"])  
        self.parser._cmd_dh_gen([])      
        self.parser._cmd_send(["-s", f"{self.parser.dh_p},{self.parser.dh_g}"])         
        self.btnDifHelTask.setEnabled(False)  
        self.btnDifHelGenerate.setEnabled(True)              
        self.difHelPubKeyText.setEnabled(True)
        

    def btnSendDifHelGenModulo(self):     
        key = 0
        try:
            key = int(self.difHelPubKeyText.toPlainText())
            if (key > 0):
                #Commande: 
                self.parser._cmd_send(["-s", f"{self.parser.dh_A}"])
                self.parser._cmd_dh_sec([key])
                self.parser._cmd_send(["-s", f"{self.parser.dh_secret}"])
            
                self.btnDifHelTask.setEnabled(True)  
                self.btnDifHelGenerate.setEnabled(False)              
                self.difHelPubKeyText.setEnabled(False)
            else:
                raise ValueError
        except ValueError:
            self.addChatField("Error: Wrong Shift key length !")
        self.difHelPubKeyText.setPlainText("")

    def btnSendHashEncoding(self):
        self.parser._cmd_send(["-s", "task", "hash", "hash"])
        self.btnHashTask.setEnabled(False)
        self.btnHashVerify.setEnabled(True)

    def btnSendHashVerify(self):
        self.parser._cmd_hash([])
        self.parser._cmd_send(["-s", "encoded"])
        self.btnHashTask.setEnabled(True)
        self.btnHashVerify.setEnabled(False)

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
                keyLabel = QLabel("Msg length : ")
                keyLabel.setMaximumWidth(60)
                
                self.shiftkeyText = QTextEdit(placeholderText="Msg length")
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
                keyLabel = QLabel("Msg length : ")
                keyLabel.setMaximumWidth(60)
                
                self.vgnrkeyText = QTextEdit(placeholderText="Msg length")
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
                self.btnSendVgnred.clicked.connect(self.btnSendVegeneredMsg)
                self.btnSendVgnred.setEnabled(False)
               

                # Button to generate RSA keys
                self.btnSendVgnr = QPushButton("Send Task")
                self.btnSendVgnr.clicked.connect(self.btnSendTaskVegenere)

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
                privateLabel = QLabel("Msg Length : ")
                privateLabel.setFixedWidth(70)
                
                self.rsaMsgLen = QTextEdit(placeholderText="Msg length")
                self.rsaMsgLen.setMaximumHeight(30)

                privateLayout.addWidget(privateLabel)
                privateLayout.addWidget(self.rsaMsgLen)
               

                # Button to generate RSA keys
                self.btnRSATask = QPushButton("Send Task")
                self.btnRSATask.clicked.connect(self.btnSendTaskRSA)

                
                self.btnRSAEncoding = QPushButton("Encode and Send")
                self.btnRSAEncoding.clicked.connect(self.btnSendRSAEncoding)
                self.btnRSAEncoding.setEnabled(False)

                self.rsaLayout.addLayout(privateLayout)
                self.rsaLayout.addWidget(self.btnRSATask)
                self.rsaLayout.addWidget(self.btnRSAEncoding)
                self.settingsDynamicLayout.addLayout(self.rsaLayout)
            case "DiffieHellman": 
                self.difHelLayout = QVBoxLayout() 
                difHelPubKeyLayout = QHBoxLayout()              

                # Button to send Hash task 
                self.btnDifHelTask = QPushButton("Send Task")
                self.btnDifHelTask.clicked.connect(self.btnSendDifHelTask)                
                self.btnDifHelTask.setEnabled(True)  
                
                # Button to verify Hash  
                self.btnDifHelGenerate = QPushButton("Send Half-Key and Verify")
                self.btnDifHelGenerate.clicked.connect(self.btnSendDifHelGenModulo)
                self.btnDifHelGenerate.setEnabled(False)              

                # Field for the private key
                keyLabel = QLabel("Half-Key : ")
                keyLabel.setMaximumWidth(60)
                
                self.difHelPubKeyText = QTextEdit(placeholderText="Half-Key")
                self.difHelPubKeyText.setMaximumHeight(30)                
                self.difHelPubKeyText.setEnabled(False)

                difHelPubKeyLayout.addWidget(keyLabel)
                difHelPubKeyLayout.addWidget(self.difHelPubKeyText)

                self.difHelLayout.addWidget(self.btnDifHelTask)
                self.difHelLayout.addLayout(difHelPubKeyLayout)
                self.difHelLayout.addWidget(self.btnDifHelGenerate)
                self.settingsDynamicLayout.addLayout(self.difHelLayout)
            case "Hashing": 
                # Create layout for hash encoding
                self.hashLayout = QVBoxLayout()               

                # Button to send Hash task 
                self.btnHashTask = QPushButton("Send Task")
                self.btnHashTask.clicked.connect(self.btnSendHashEncoding)
                
                # Button to verify Hash  
                self.btnHashVerify = QPushButton("Verify Hash")
                self.btnHashVerify.clicked.connect(self.btnSendHashVerify)
                self.btnHashVerify.setEnabled(False)

                self.hashLayout.addWidget(self.btnHashTask)
                self.hashLayout.addWidget(self.btnHashVerify)
                self.settingsDynamicLayout.addLayout(self.hashLayout)
        
        self.btnSend.setEnabled(False)


    def checkOnlyServ(self):
        self.chatText.setEnabled(not self.servOnly.isChecked())
        self.btnSend.setEnabled(not self.servOnly.isChecked())
        self.encoding.setEnabled(self.servOnly.isChecked())
        if not self.servOnly.isChecked():
            self.clearLayout(self.settingsDynamicLayout)
        else:
            self.cmbChangedSelected()
        
        
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
        label.setFont(QFont("Arial", 10))
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
        # print("Wasd: ", self.parser.plain_buffer)
        if self.servOnly.isChecked():
            match self.encoding.currentText():
                case "Shift": 
                    if self.parser.plain_buffer is not None or self.parser.plain_buffer != "":
                        self.shiftedMsgText.setPlainText(self.parser.plain_buffer)
                case "Vegenere": 
                    if self.parser.plain_buffer is not None or self.parser.plain_buffer != "":
                        self.vgnredMsgText.setPlainText(self.parser.plain_buffer)
                case "DiffieHellman": 
                    if self.parser.plain_buffer is not None or self.parser.plain_buffer != "":
                        self.difHelPubKeyText.setPlainText(self.parser.plain_buffer)
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
