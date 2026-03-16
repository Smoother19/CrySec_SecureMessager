from PySide6.QtCore import QObject, Signal

class MessageTransferer(QObject):
    text = Signal(str)

    def emitText(self, text):
        self.text.emit(text)