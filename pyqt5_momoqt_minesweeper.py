import random
import sys

from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QGridLayout, QPushButton, QVBoxLayout, QWidget, QLabel


class MineSweeper(QMainWindow):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('MineSweeper')
        self.setFixedSize(QSize(400, 400))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        self.grid = QGridLayout()
        layout.addLayout(self.grid)
        self.grid.setSpacing(0)

        self.rows = 10
        self.cols = 10
        self.mines = 15

        self.buttons = [[None for _ in range(self.cols)] for _ in range(self.rows)]
        self.mine_map = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

        self.create_buttons()
        self.generate_mines()
        self.calculate_mine_counts()

    def create_buttons(self):
        for row in range(self.rows):
            for col in range(self.cols):
                button = QPushButton()
                button.setFixedSize(QSize(30, 30))
                button.clicked.connect(self.on_button_click)
                button.setStyleSheet("QPushButton { font-weight: bold; font-size: 14px; }"
                                     "QPushButton { border: 1px solid gray; }"
                                     "QPushButton:pressed { background-color: white; }")
                button.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
                button.customContextMenuRequested.connect(self.on_right_click)
                self.grid.addWidget(button, row, col)
                self.buttons[row][col] = button

    def generate_mines(self):
        mine_count = 0
        while mine_count < self.mines:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)

            if self.mine_map[row][col] == 0:
                self.mine_map[row][col] = -1
                mine_count += 1

    def calculate_mine_counts(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.mine_map[row][col] == -1:
                    continue

                mine_count = 0
                for r in range(-1, 2):
                    for c in range(-1, 2):
                        if 0 <= row + r < self.rows and 0 <= col + c < self.cols and self.mine_map[row + r][
                            col + c] == -1:
                            mine_count += 1

                self.mine_map[row][col] = mine_count

    def on_button_click(self):
        sender = self.sender()
        row, col = self.get_button_position(sender)

        if self.mine_map[row][col] == -1:
            self.reveal_mines()
            self.show_message("You lost!")
            return

        self.reveal_button(row, col)

        if self.check_win():
            self.show_message("You won!")

    def on_right_click(self, pos):
        sender = self.sender()
        row, col = self.get_button_position(sender)

        if not sender.text():
            sender.setText("F")
            sender.setStyleSheet("QPushButton { font-weight: bold; font-size: 14px; color: red; }"
                                 "QPushButton { border: 1px solid gray; }"
                                 "QPushButton:pressed { background-color: white; }")
        elif sender.text() == "F":
            sender.setText("")
            sender.setStyleSheet("QPushButton { font-weight: bold; font-size: 14px; }"
                                 "QPushButton { border: 1px solid gray; }"
                                 "QPushButton:pressed { background-color: white; }")

    def get_button_position(self, button):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.buttons[row][col] == button:
                    return row, col

    def reveal_mines(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.mine_map[row][col] == -1:
                    self.buttons[row][col].setText("M")
                    self.buttons[row][col].setEnabled(False)

    def reveal_button(self, row, col):
        if not self.buttons[row][col].isEnabled():
            return

        self.buttons[row][col].setEnabled(False)
        count = self.mine_map[row][col]

        if count == 0:
            self.buttons[row][col].setText("")
            for r in range(-1, 2):
                for c in range(-1, 2):
                    if 0 <= row + r < self.rows and 0 <= col + c < self.cols:
                        self.reveal_button(row + r, col + c)
        else:
            self.buttons[row][col].setText(str(count))

    def check_win(self):
        for row in range(self.rows):
            for col in range(self.cols):
                if self.buttons[row][col].isEnabled() and self.mine_map[row][col] != -1:
                    return False
        return True

    def show_message(self, message):
        for row in range(self.rows):
            for col in range(self.cols):
                self.buttons[row][col].setEnabled(False)

        message_label = QLabel(message, self)
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.grid.addWidget(message_label, 0, 0, self.rows, self.cols)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    minesweeper = MineSweeper()
    minesweeper.show()
    sys.exit(app.exec())
