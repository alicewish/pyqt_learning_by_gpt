import sys

from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QPen, QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QLabel, QMainWindow, \
    QPushButton, QVBoxLayout, QWidget, QToolBar, QToolButton, QComboBox, QColorDialog, QSlider, \
    QFileDialog, QCheckBox, QScrollArea, QDockWidget, QGraphicsBlurEffect


class LayerPreviewWidget(QWidget):
    def __init__(self, layer_index, drawing_app, parent=None):
        super().__init__(parent)
        self.drawing_app = drawing_app
        self.layer_index = layer_index

        layout = QVBoxLayout()

        top_layout = QHBoxLayout()
        self.checkbox = QCheckBox(f'图层 {self.layer_index + 1}', self)
        self.checkbox.setChecked(self.drawing_app.layer_visibility[self.layer_index])
        self.checkbox.stateChanged.connect(self.toggle_visibility)
        top_layout.addWidget(self.checkbox)

        self.delete_button = QPushButton('删除', self)
        self.delete_button.clicked.connect(self.delete_layer)
        top_layout.addWidget(self.delete_button)

        layout.addLayout(top_layout)

        self.preview_label = QLabel(self)
        self.preview_label.setFixedSize(100, 100)
        self.update_preview()
        layout.addWidget(self.preview_label)

        self.opacity_slider = QSlider(Qt.Horizontal, self)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(self.drawing_app.layer_opacity[self.layer_index])
        self.opacity_slider.valueChanged.connect(self.update_opacity)
        layout.addWidget(self.opacity_slider)

        self.setLayout(layout)

    def update_preview(self):
        layer_image = self.drawing_app.layers[self.layer_index].scaled(100, 100, Qt.KeepAspectRatio,
                                                                       Qt.SmoothTransformation)
        layer_pixmap = QPixmap.fromImage(layer_image)

        if not self.drawing_app.layer_visibility[self.layer_index]:
            blur_effect = QGraphicsBlurEffect()
            blur_effect.setBlurRadius(5)
            self.preview_label.setGraphicsEffect(blur_effect)
        else:
            self.preview_label.setGraphicsEffect(None)

        self.preview_label.setPixmap(layer_pixmap)

    def update_opacity(self, value):
        self.drawing_app.layer_opacity[self.layer_index] = value
        self.drawing_app.update()

    def toggle_visibility(self, state):
        self.drawing_app.layer_visibility[self.layer_index] = state == Qt.Checked
        self.update_preview()
        self.drawing_app.update()

    def delete_layer(self):
        self.drawing_app.delete_layer(self, self.layer_index)


class DrawingApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.image = QImage(800, 600, QImage.Format_RGB32)
        self.image.fill(Qt.white)

        self.layers = [self.image]
        self.current_layer = 0

        self.path = []
        self.undo_stacks = {0: []}
        self.redo_stacks = {0: []}

        self.drawing = False
        self.last_point = QPoint()

        self.pen_color = Qt.black
        self.pen_width = 4
        self.eraser = False

        self.layer_visibility = {0: True}
        self.layer_opacity = {0: 100}

        self.setGeometry(300, 300, 800, 600)
        self.setWindowTitle('绘画程序')
        self.create_toolbar()
        self.show()

        # ... 其他代码保持不变
        self.create_toolbar()
        self.create_dock_widget()
        self.show()

    def create_toolbar(self):
        toolbar = QToolBar(self)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        undo_btn = QToolButton(self)
        undo_btn.setText('撤销')
        undo_btn.clicked.connect(self.undo)
        toolbar.addWidget(undo_btn)

        redo_btn = QToolButton(self)
        redo_btn.setText('重做')
        redo_btn.clicked.connect(self.redo)
        toolbar.addWidget(redo_btn)

        toolbar.addSeparator()

        save_btn = QToolButton(self)
        save_btn.setText('保存')
        save_btn.clicked.connect(self.save_image)
        toolbar.addWidget(save_btn)

        toolbar.addSeparator()

        add_layer_btn = QToolButton(self)
        add_layer_btn.setText('添加图层')
        add_layer_btn.clicked.connect(self.add_layer)
        toolbar.addWidget(add_layer_btn)

        delete_layer_btn = QToolButton(self)
        delete_layer_btn.setText('删除图层')
        delete_layer_btn.clicked.connect(self.delete_layer)
        toolbar.addWidget(delete_layer_btn)

        self.layer_combobox = QComboBox(self)
        self.layer_combobox.addItem("图层 1")
        self.layer_combobox.currentIndexChanged.connect(self.change_layer)
        toolbar.addWidget(self.layer_combobox)

        toolbar.addSeparator()

        color_btn = QToolButton(self)
        color_btn.setText('颜色')
        color_btn.clicked.connect(self.choose_color)
        toolbar.addWidget(color_btn)

        pen_width_label = QLabel('画笔粗细', self)
        toolbar.addWidget(pen_width_label)

        self.pen_width_slider = QSlider(Qt.Horizontal, self)
        self.pen_width_slider.setRange(1, 20)
        self.pen_width_slider.setValue(self.pen_width)
        self.pen_width_slider.valueChanged.connect(self.update_pen_width)
        toolbar.addWidget(self.pen_width_slider)

        toolbar.addSeparator()

        eraser_btn = QToolButton(self)
        eraser_btn.setText('橡皮擦')
        eraser_btn.setCheckable(True)
        eraser_btn.clicked.connect(self.toggle_eraser)
        toolbar.addWidget(eraser_btn)

        toolbar.addSeparator()

        opacity_label = QLabel('透明度', self)
        toolbar.addWidget(opacity_label)

        self.opacity_slider = QSlider(Qt.Horizontal, self)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setValue(100)
        self.opacity_slider.valueChanged.connect(self.update_opacity)
        toolbar.addWidget(self.opacity_slider)

        visibility_checkbox = QCheckBox('可见', self)
        visibility_checkbox.setChecked(True)
        visibility_checkbox.stateChanged.connect(self.toggle_visibility)
        toolbar.addWidget(visibility_checkbox)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drawing = True
            self.last_point = event.pos()

    def mouseMoveEvent(self, event):
        if self.drawing and event.buttons() & Qt.LeftButton:
            painter = QPainter(self.layers[self.current_layer])
            if self.eraser:
                painter.setCompositionMode(QPainter.CompositionMode_Clear)
                painter.setPen(QPen(Qt.transparent, self.pen_width * 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
            else:
                painter.setPen(QPen(self.pen_color, self.pen_width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

            painter.drawLine(self.last_point, event.pos())

            self.path.append((self.last_point, event.pos(), self.pen_color, self.pen_width, self.eraser))
            self.last_point = event.pos()

            self.update()

    def mouseReleaseEvent(self, event):
        if self.current_layer in self.undo_stacks:
            self.undo_stacks[self.current_layer].append(self.path)
        else:
            # 如果当前图层不存在，则创建一个新的图层
            self.undo_stacks[self.current_layer] = [self.path]
        if event.button() == Qt.LeftButton:
            self.drawing = False
            self.undo_stacks[self.current_layer].append(self.path)
            self.path = []
            self.redo_stacks[self.current_layer].clear()

    def paintEvent(self, event):
        painter = QPainter(self)
        for index, layer in enumerate(self.layers):
            if self.layer_visibility[index]:
                opacity = self.layer_opacity[index] / 100.0
                painter.setOpacity(opacity)
                painter.drawImage(0, 0, layer)
        painter.setOpacity(1.0)
        # ... 其他代码保持不变
        for layer_preview in self.findChildren(LayerPreviewWidget):
            layer_preview.update_preview()

    def choose_color(self):
        color = QColorDialog.getColor(self.pen_color, self, '选择画笔颜色')

        if color.isValid():
            self.pen_color = color

    def update_pen_width(self, value):
        self.pen_width = value

    def toggle_eraser(self, checked):
        self.eraser = checked

    def undo(self):
        if self.undo_stacks[self.current_layer]:
            self.redo_stacks[self.current_layer].append(self.undo_stacks[self.current_layer].pop())
            self.repaint_image()

    def redo(self):
        if self.redo_stacks[self.current_layer]:
            self.undo_stacks[self.current_layer].append(self.redo_stacks[self.current_layer].pop())
            self.repaint_image()

    def repaint_image(self):
        self.layers[self.current_layer].fill(Qt.transparent)
        painter = QPainter(self.layers[self.current_layer])

        for path in self.undo_stacks[self.current_layer]:
            for i in range(len(path)):
                p1, p2, color, width, eraser = path[i]

                if eraser:
                    painter.setCompositionMode(QPainter.CompositionMode_Clear)
                    painter.setPen(QPen(Qt.transparent, width * 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
                else:
                    painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
                    painter.setPen(QPen(color, width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

                painter.drawLine(p1, p2)

        self.update()

    def save_image(self):
        file_path, _ = QFileDialog.getSaveFileName(self, '保存图片', '',
                                                   'Images (*.png *.xpm *.jpg *.bmp);;All Files (*)')

        if file_path:
            merged_image = QImage(self.image.size(), QImage.Format_ARGB32_Premultiplied)
            merged_image.fill(Qt.transparent)
            painter = QPainter(merged_image)
            for index, layer in enumerate(self.layers):
                if self.layer_visibility[index]:
                    opacity = self.layer_opacity[index] / 100.0
                    painter.setOpacity(opacity)
                    painter.drawImage(0, 0, layer)
                painter.setOpacity(1.0)
                painter.end()

                merged_image.save(file_path)

    def add_layer(self):
        new_layer = QImage(self.image.size(), QImage.Format_ARGB32_Premultiplied)
        new_layer.fill(Qt.transparent)
        self.layers.append(new_layer)

        new_layer_index = len(self.layers) - 1
        self.layer_combobox.addItem(f'图层 {new_layer_index + 1}')
        self.layer_combobox.setCurrentIndex(new_layer_index)

        self.undo_stacks[new_layer_index] = []
        self.redo_stacks[new_layer_index] = []

        self.layer_visibility[new_layer_index] = True
        self.layer_opacity[new_layer_index] = 100

        # ... 其他代码保持不变
        self.add_layer_preview(new_layer_index)

    # 修改 DrawingApp 类中的 delete_layer 方法
    def delete_layer(self, layer_preview_widget, layer_index):
        if len(self.layers) > 1:
            self.layers.pop(layer_index)

            self.layer_combobox.removeItem(layer_index)

            self.undo_stacks.pop(layer_index)
            self.redo_stacks.pop(layer_index)

            self.layer_visibility.pop(layer_index)
            self.layer_opacity.pop(layer_index)

            self.remove_layer_preview(layer_index)

            for i in range(layer_index, len(self.layers)):
                self.undo_stacks[i] = self.undo_stacks.pop(i + 1)
                self.redo_stacks[i] = self.redo_stacks.pop(i + 1)
                self.layer_visibility[i] = self.layer_visibility.pop(i + 1)
                self.layer_opacity[i] = self.layer_opacity.pop(i + 1)
                self.layer_combobox.setItemText(i, f'图层 {i + 1}')

                preview_widget = self.layers_layout.itemAt(i).widget()
                preview_widget.layer_index = i

            self.layer_combobox.setCurrentIndex(layer_index - 1)

    def change_layer(self, index):
        self.current_layer = index

    def update_opacity(self, value):
        self.layer_opacity[self.current_layer] = value
        self.update()

    def toggle_visibility(self, state):
        self.layer_visibility[self.current_layer] = state == Qt.Checked
        self.update()

    # 在 DrawingApp 类中修改 create_dock_widget() 方法
    def create_dock_widget(self):
        self.dock_widget = QDockWidget("图层", self)
        self.dock_widget.setAllowedAreas(Qt.RightDockWidgetArea)
        self.dock_widget.setFeatures(QDockWidget.DockWidgetMovable)

        self.layers_scroll_area = QScrollArea(self)
        self.layers_container = QWidget(self.layers_scroll_area)
        self.layers_layout = QVBoxLayout(self.layers_container)

        self.layers_scroll_area.setWidget(self.layers_container)
        self.layers_scroll_area.setWidgetResizable(True)

        self.dock_widget.setWidget(self.layers_scroll_area)
        self.addDockWidget(Qt.RightDockWidgetArea, self.dock_widget)

        self.dock_widget.setFloating(False)
        self.setCorner(Qt.TopRightCorner, Qt.RightDockWidgetArea)

        self.add_layer_preview(0)

    def add_layer_preview(self, layer_index):
        layer_preview = LayerPreviewWidget(layer_index, self)
        self.layers_layout.addWidget(layer_preview)

    def remove_layer_preview(self, layer_index):
        preview_widget = self.layers_layout.itemAt(layer_index).widget()
        self.layers_layout.removeWidget(preview_widget)
        preview_widget.deleteLater()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DrawingApp()
    sys.exit(app.exec_())
