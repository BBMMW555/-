from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent

class MouseEvents:
    def __init__(self, window):
        self.window = window
        self.drag_pos = None

    # تغيير أسماء الدوال لتتطابق مع ما يتم استدعاؤه
    def on_press(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPos()
            event.accept()

    def on_move(self, event: QMouseEvent):
        if event.buttons() & Qt.LeftButton and self.drag_pos:
            delta = event.globalPos() - self.drag_pos
            self.window.move(self.window.pos() + delta)
            self.drag_pos = event.globalPos()
            event.accept()

    def on_release(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            if hasattr(self.window, 'chat_frame'):
                self.window.chat_frame.hide()
            self._adjust_positions()
            self.drag_pos = None
            event.accept()

    def _adjust_positions(self):
        """ضبط المواقع بعد الإخفاء"""
        if hasattr(self.window, 'icon'):
            self.window.resize(self.window.icon.width() + 20, 
                             self.window.icon.height() + 20)
            self.window.icon.move(
                (self.window.width() - self.window.icon.width()) // 2,
                (self.window.height() - self.window.icon.height()) // 2
            )
            self.window.update()
                              