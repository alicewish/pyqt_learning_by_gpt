import sys

import numpy as np
import simpleaudio as sa
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPainter, QColor, QFont, QAction
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QMenu, QMenuBar, QScrollArea, QLabel
from loguru import logger
from music21 import pitch


class Piano(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Piano')
        self.setGeometry(100, 100, 800, 400)

        self.recorded_notes = []

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setGeometry(400, 50, 380, 300)
        self.sheet_music_label = QLabel(self.scroll_area)
        self.scroll_area.setWidget(self.sheet_music_label)

        self.create_piano_keys()
        self.create_menu_bar()
        self.show()

    def create_piano_keys(self):
        # 添加白键
        self.white_keys = ['A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L']
        self.white_notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C', 'D']

        # 添加黑键
        self.black_keys = ['W', 'E', '', 'R', 'T', 'Y', 'U']
        self.black_notes = ['C#', 'D#', '', 'F#', 'G#', 'A#', 'B#']

        # 创建白键
        for i, key in enumerate(self.white_keys):
            button = QPushButton(f"{self.white_notes[i]}\n{key}", self)
            button.setGeometry(40 * i + 80, 100, 30, 150)
            button.setStyleSheet("QPushButton { font-size: 14px; } QPushButton::hover { background-color: lightgrey; }")
            button.clicked.connect(self.play_note)

        # 创建黑键
        black_key_positions = [0, 1, 3, 4, 5, 6, 8]
        for i, key in enumerate(self.black_keys):
            if key:  # 如果有黑键
                button = QPushButton(f"{self.black_notes[i]}\n{key}", self)
                button.setGeometry(40 * black_key_positions[i] + 100, 100, 20, 90)
                button.setStyleSheet(
                    "QPushButton { font-size: 12px; background-color: black; color: white; } QPushButton::hover { background-color: darkgrey; }")
                button.clicked.connect(self.play_note)

    def create_menu_bar(self):
        menu_bar = QMenuBar(self)

        file_menu = QMenu("File", self)
        menu_bar.addMenu(file_menu)

        open_action = QAction("Open", self)
        open_action.triggered.connect(self.open_sheet_music)
        file_menu.addAction(open_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_sheet_music)
        file_menu.addAction(save_action)

    def play_note(self):
        sender = self.sender()
        key_text = sender.text().split("\n")[1]

        if key_text in self.white_keys:
            note = self.white_notes[self.white_keys.index(key_text)]
        elif key_text in self.black_keys:
            note = self.black_notes[self.black_keys.index(key_text)]

        self.record_note(note)
        self.play_audio(note)

    def play_audio(self, note_number):
        frequency = pitch.Pitch(note_number).frequency
        sample_rate = 44100
        duration = 0.5
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = 0.5 * np.sin(frequency * 2 * np.pi * t)
        audio_data = audio_data * (2 ** 15 - 1) / np.max(np.abs(audio_data))
        audio_data = audio_data.astype(np.int16)
        play_obj = sa.play_buffer(audio_data, 1, 2, sample_rate)
        play_obj.wait_done()

    def get_note_from_key(self, key):
        # 根据键盘按键返回对应的音符
        key_map = {
            Qt.Key.Key_Q: 60, Qt.Key.Key_2: 61, Qt.Key.Key_W: 62, Qt.Key.Key_3: 63,
            Qt.Key.Key_E: 64, Qt.Key.Key_R: 65, Qt.Key.Key_5: 66, Qt.Key.Key_T: 67,
            Qt.Key.Key_6: 68, Qt.Key.Key_Y: 69, Qt.Key.Key_7: 70, Qt.Key.Key_U: 71,
            Qt.Key.Key_I: 72, Qt.Key.Key_9: 73, Qt.Key.Key_O: 74, Qt.Key.Key_0: 75,
            Qt.Key.Key_P: 76, Qt.Key.Key_BracketLeft: 77, Qt.Key.Key_Equal: 78,
            Qt.Key.Key_BracketRight: 79
        }

        note_number = key_map.get(key, None)
        return note_number

    # 修改record_note方法
    def record_note(self, note):
        self.recorded_notes.append(note)
        self.sheet_music_label.setText("<br>".join(self.recorded_notes))
        self.sheet_music_label.adjustSize()

    def open_sheet_music(self):
        options = QFileDialog.Option(0)
        options |= QFileDialog.Option.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Sheet Music", "", "Text Files (*.txt);;All Files (*)",
                                                   options=options)
        if file_name:
            with open(file_name, "r") as file:
                self.recorded_notes = file.read().split()
                self.update()

    def save_sheet_music(self):
        options = QFileDialog.Option(0)
        options |= QFileDialog.Option.ReadOnly
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Sheet Music", "", "Text Files (*.txt);;All Files (*)",
                                                   options=options)
        if file_name:
            with open(file_name, "w") as file:
                file.write(" ".join(self.recorded_notes))

    def keyPressEvent(self, event):
        # 按下键盘时触发
        note_number = self.get_note_from_key(event.key())

        if note_number:
            # 播放音符
            self.findChild(QPushButton, str(note_number)).get(note_number, None).setChecked(True)
            self.play_audio(note_number)

            # 添加音符到乐谱
            quarter_note_duration = duration.Duration(1 / 4)
            note_pitch = pitch.Pitch()
            note_pitch.midi = note_number
            note = note.Note(pitch=note_pitch, duration=quarter_note_duration)
            self.score.insert(self.score.highestTime, note)
            self.score_view.show_score(self.score)

    def keyReleaseEvent(self, event):
        # 释放键盘时触发
        note_number = self.get_note_from_key(event.key())

        if note_number:
            # 停止播放音符
            self.findChild(QPushButton, str(note_number)).get(note_number, None).setChecked(False)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QColor(0, 0, 0))
        painter.setFont(QFont('Decorative', 20))
        painter.drawText(20, 50, " ".join(self.recorded_notes))


@logger.catch
def main_qt():
    window = Piano()
    sys.exit(appgui.exec())


if __name__ == "__main__":
    appgui = QApplication(sys.argv)
    main_qt()
