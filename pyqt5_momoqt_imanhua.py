import os
import sys

from PyQt6.QtCore import QPointF, Qt, QSize
from PyQt6.QtGui import QAction, QFont, QImage, QKeySequence, QPainter, QPixmap, QImageReader, QTextCursor, \
    QTransform
from PyQt6.QtWidgets import QApplication, QDockWidget, QFontComboBox, QHBoxLayout, \
    QLabel, QListWidget, QMainWindow, QPushButton, QSpinBox, QVBoxLayout, QWidget, QFileDialog, QGraphicsScene, \
    QGraphicsView, QGraphicsTextItem, QToolBox, QColorDialog, QListWidgetItem, QToolBar


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("漫画翻译工具")
        self.resize(800, 600)

        self.image_item = None
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self.scene)

        # 创建动作
        self.create_actions()
        # 创建工具栏
        self.create_tool_bar()
        # 创建工具箱
        self.create_tool_box()
        # 将 QGraphicsView 设置为中心窗口部件
        self.setCentralWidget(self.view)
        self.selected_text_item = None
        self.current_text_item = None
        self.scene.selectionChanged.connect(self.set_current_text_item)

        # 文件夹变量
        self.image_folder = None
        self.image_list = []
        self.current_image_index = -1

    def create_actions(self):
        # 文件菜单
        self.file_menu = self.menuBar().addMenu("File")

        # 添加打开图片操作
        self.open_image_action = QAction("Open Image", self)
        self.open_image_action.setShortcut(QKeySequence.StandardKey.Open)
        self.open_image_action.triggered.connect(self.open_image)
        self.file_menu.addAction(self.open_image_action)

        # 添加打开文件夹操作
        self.open_folder_action = QAction("Open Folder", self)
        self.open_folder_action.setShortcut(QKeySequence("Ctrl+Shift+O"))
        self.open_folder_action.triggered.connect(self.open_folder)
        self.file_menu.addAction(self.open_folder_action)

        # 添加保存图片操作
        self.save_image_action = QAction("Save Image", self)
        self.save_image_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_image_action.triggered.connect(self.save_image)
        self.file_menu.addAction(self.save_image_action)

        # 显示菜单
        self.view_menu = self.menuBar().addMenu("View")

        self.zoom_in_action = QAction("Zoom In", self)
        self.zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        self.zoom_in_action.triggered.connect(self.zoom_in)
        self.view_menu.addAction(self.zoom_in_action)

        self.zoom_out_action = QAction("Zoom Out", self)
        self.zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        self.zoom_out_action.triggered.connect(self.zoom_out)
        self.view_menu.addAction(self.zoom_out_action)

        self.reset_zoom_action = QAction("Reset Zoom", self)
        self.reset_zoom_action.setShortcut(QKeySequence("Ctrl+0"))
        self.reset_zoom_action.triggered.connect(self.reset_zoom)
        self.view_menu.addAction(self.reset_zoom_action)

        # 编辑菜单
        self.edit_menu = self.menuBar().addMenu("Edit")

        self.add_text_action = QAction("Add Text", self)
        self.add_text_action.setShortcut(QKeySequence("Ctrl+T"))
        self.add_text_action.triggered.connect(self.add_text)
        self.edit_menu.addAction(self.add_text_action)

        self.delete_text_action = QAction("Delete Text", self)
        self.delete_text_action.setShortcut(QKeySequence("Ctrl+D"))
        self.delete_text_action.triggered.connect(self.delete_text)
        self.edit_menu.addAction(self.delete_text_action)

        # 导航菜单
        self.nav_menu = self.menuBar().addMenu("Edit")

        # 添加上一张图片操作
        self.prev_image_action = QAction("Previous Image", self)
        self.prev_image_action.setShortcut(QKeySequence("Ctrl+Left"))
        self.prev_image_action.triggered.connect(self.prev_image)
        self.nav_menu.addAction(self.prev_image_action)

        # 添加下一张图片操作
        self.next_image_action = QAction("Next Image", self)
        self.next_image_action.setShortcut(QKeySequence("Ctrl+Right"))
        self.next_image_action.triggered.connect(self.next_image)
        self.nav_menu.addAction(self.next_image_action)

    def create_tool_bar(self):
        # 添加顶部工具栏
        self.tool_bar = QToolBar("Toolbar", self)
        self.tool_bar.setIconSize(QSize(24, 24))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.tool_bar)
        self.tool_bar.setMovable(False)
        self.tool_bar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.tool_bar.addAction(self.open_image_action)
        self.tool_bar.addAction(self.open_folder_action)
        self.tool_bar.addAction(self.save_image_action)
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(self.zoom_in_action)
        self.tool_bar.addAction(self.zoom_out_action)
        self.tool_bar.addAction(self.reset_zoom_action)
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(self.prev_image_action)
        self.tool_bar.addAction(self.next_image_action)

    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Open Folder")
        if folder_path:
            self.image_list = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if
                               f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
            self.current_image_index = 0
            self.open_image_from_list()

    def open_image_from_list(self):
        if self.image_list and 0 <= self.current_image_index < len(self.image_list):
            pixmap = QPixmap(self.image_list[self.current_image_index])
            if self.image_item:
                self.scene.removeItem(self.image_item)
            self.image_item = self.scene.addPixmap(pixmap)
            self.view.setSceneRect(pixmap.rect().toRectF())
            self.view.setRenderHints(QPainter.RenderHint.SmoothPixmapTransform)

    def prev_image(self):
        if self.image_list:
            self.current_image_index -= 1
            if self.current_image_index < 0:
                self.current_image_index = len(self.image_list) - 1
            self.open_image_from_list()

    def next_image(self):
        if self.image_list:
            self.current_image_index += 1
            if self.current_image_index >= len(self.image_list):
                self.current_image_index = 0
            self.open_image_from_list()

    def create_tool_box(self):
        self.tool_box = QToolBox()

        # 创建字体选择器
        font_label = QLabel("字体:")
        self.font_combo = QFontComboBox(self)
        self.font_combo.setFontFilters(QFontComboBox.FontFilter.AllFonts)
        self.font_combo.currentFontChanged.connect(self.update_text_item_font)

        # 创建字体大小选择器
        font_size_label = QLabel("字号:")
        self.font_size_spinbox = QSpinBox(self)
        self.font_size_spinbox.setRange(6, 100)
        self.font_size_spinbox.setValue(18)
        self.font_size_spinbox.valueChanged.connect(self.update_text_item_font_size)

        # 创建颜色选择器
        color_label = QLabel("颜色:")
        self.color_button = QPushButton("更改颜色", self)
        self.color_button.clicked.connect(self.pick_color)
        self.color_picker = QColorDialog(self)
        self.color_picker.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel)

        # 创建文本项的 X 和 Y 坐标选择器
        position_label = QLabel("位置:")
        self.x_spinbox = QSpinBox(self)
        self.x_spinbox.setRange(0, int(self.scene.width()))
        self.y_spinbox = QSpinBox(self)
        self.y_spinbox.setRange(0, int(self.scene.height()))
        self.x_spinbox.valueChanged.connect(self.update_text_item_position)
        self.y_spinbox.valueChanged.connect(self.update_text_item_position)

        self.text_items_list = QListWidget(self)
        self.text_items_list.currentItemChanged.connect(self.text_item_selected)

        # 将部件添加到布局中
        layout = QVBoxLayout()

        hb_font_name = QHBoxLayout()
        hb_font_name.addWidget(font_label)
        hb_font_name.addWidget(self.font_combo)

        hb_font_size = QHBoxLayout()
        hb_font_size.addWidget(font_size_label)
        hb_font_size.addWidget(self.font_size_spinbox)

        hb_font_color = QHBoxLayout()
        hb_font_color.addWidget(color_label)
        hb_font_color.addWidget(self.color_button)

        hb_text_position = QHBoxLayout()
        hb_text_position.addWidget(position_label)
        hb_text_position.addWidget(self.x_spinbox)
        hb_text_position.addWidget(self.y_spinbox)

        layout.addLayout(hb_font_name)
        layout.addLayout(hb_font_size)
        layout.addLayout(hb_font_color)
        layout.addLayout(hb_text_position)

        layout.addWidget(QLabel("文本项:"))
        layout.addWidget(self.text_items_list)

        widget = QWidget()
        widget.setLayout(layout)
        self.tool_box.addItem(widget, "文本工具")

        # 创建右侧工具栏
        tool_dock = QDockWidget("工具", self)
        tool_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        tool_dock.setWidget(self.tool_box)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, tool_dock)

    def update_tool_box(self, text_item):
        self.x_spinbox.setMaximum(self.scene.width())
        self.y_spinbox.setMaximum(self.scene.height())
        if text_item:
            self.font_combo.setCurrentFont(text_item.font())
            self.font_size_spinbox.setValue(text_item.font().pointSize())  # 修改为 self.font_size_spinbox
            self.color_picker.setCurrentColor(text_item.defaultTextColor())
            self.x_spinbox.setValue(int(text_item.x()))  # 更新 X 坐标选择器的值
            self.y_spinbox.setValue(int(text_item.y()))  # 更新 Y 坐标选择器的值
        else:
            self.font_combo.setCurrentFont(QFont())
            self.font_size_spinbox.setValue(0)  # 修改为 self.font_size_spinbox
            self.color_picker.setCurrentColor(Qt.GlobalColor.black)
            self.x_spinbox.setValue(0)  # 更新 X 坐标选择器的值
            self.y_spinbox.setValue(0)  # 更新 Y 坐标选择器的值

    def set_current_text_item(self):
        selected_items = self.scene.selectedItems()
        if selected_items:
            item = selected_items[0]
            if isinstance(item, QGraphicsTextItem):
                self.current_text_item = item
                self.update_tool_box(item)
                self.update_list_item(item)
            else:
                self.current_text_item = None
                self.update_tool_box(None)
        else:
            self.current_text_item = None
            self.update_tool_box(None)

    def open_image(self):
        supported_formats = ['*.' + fmt.data().decode("utf-8") for fmt in QImageReader.supportedImageFormats()]
        file_filter = f"Images ({' '.join(supported_formats)})"
        image_path, _ = QFileDialog.getOpenFileName(self, "Open Image", filter=file_filter)

        if image_path:
            pixmap = QPixmap(image_path)

            if self.image_item:
                self.scene.removeItem(self.image_item)

            self.image_item = self.scene.addPixmap(pixmap)
            self.view.setSceneRect(pixmap.rect().toRectF())
            self.view.setRenderHints(QPainter.RenderHint.SmoothPixmapTransform)

    def save_image(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "Images (*.png *.xpm *.jpg)")

        if file_name:
            image = QImage(self.scene.sceneRect().size().toSize(), QImage.Format.Format_ARGB32)
            image.fill(Qt.GlobalColor.transparent)

            painter = QPainter(image)
            self.scene.render(painter)
            painter.end()

            image.save(file_name)

    def zoom_in(self):
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        current_transform = self.view.transform()
        current_transform.scale(1.2, 1.2)
        self.view.setTransform(current_transform)

    def zoom_out(self):
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        current_transform = self.view.transform()
        current_transform.scale(1 / 1.2, 1 / 1.2)
        self.view.setTransform(current_transform)

    def reset_zoom(self):
        self.view.setTransform(QTransform())  # 使用setTransform代替resetMatrix

    def add_text(self):
        text_item = QGraphicsTextItem()
        text_item.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable)
        text_item.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable)
        text_item.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsFocusable)
        text_item.setFont(QFont("Arial", 16))
        text_item.setDefaultTextColor(Qt.GlobalColor.black)
        text_item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditable)

        cursor = QTextCursor(text_item.document())
        cursor.insertText("翻译内容")

        text_item.setPos(self.view.mapToScene(self.view.rect().center()))
        self.scene.addItem(text_item)

        list_item = QListWidgetItem(f"文本框 {self.text_items_list.count() + 1}")
        self.text_items_list.addItem(list_item)
        list_item.setData(Qt.ItemDataRole.UserRole, text_item)

    def delete_text(self):
        if self.current_text_item:
            # 从场景删除文本
            self.scene.removeItem(self.current_text_item)

            # Find the corresponding QListWidgetItem and remove it from the list
            for index in range(self.text_items_list.count()):
                list_item = self.text_items_list.item(index)
                if list_item.data(Qt.ItemDataRole.UserRole) == self.current_text_item:
                    self.text_items_list.takeItem(index)
                    break

            # Clear the current text item and update the toolbox
            self.current_text_item = None
            self.update_tool_box(None)

    def update_text_item_position(self):
        if self.current_text_item:
            pos = QPointF(self.x_spinbox.value(), self.y_spinbox.value())
            self.current_text_item.setPos(pos)
        if self.text_items_list.currentItem():
            self.text_items_list.currentItem().setText(self.current_text_item.toPlainText())

    def update_text_item_font(self, font):
        if self.current_text_item:
            new_font = QFont(font.family(), self.current_text_item.font().pointSize())  # 修改这里
            self.current_text_item.setFont(new_font)

    def update_text_item_font_size(self, size):
        if self.current_text_item:
            font = self.current_text_item.font()
            font.setPointSize(size)
            self.current_text_item.setFont(font)

    def update_text_item_color(self, color):
        if self.current_text_item:
            self.current_text_item.setDefaultTextColor(color)

    def pick_color(self):
        color = self.color_picker.getColor()
        if color.isValid():
            self.update_text_item_color(color)
            self.color_button.setStyleSheet(f"background-color: {color.name()};")
            self.color_button.setText(color.name())

    def clear_all_text(self):
        for item in self.scene.items():
            if isinstance(item, QGraphicsTextItem):
                self.scene.removeItem(item)
        self.text_items_list.clear()

    def text_item_selected(self, current, previous):
        if current:
            text_item = current.data(Qt.ItemDataRole.UserRole)
            text_item.setSelected(True)
            self.set_current_text_item()
        if previous:
            text_item = previous.data(Qt.ItemDataRole.UserRole)
            text_item.setSelected(False)

    def update_list_item(self, text_item):
        if text_item:
            # Find the corresponding QListWidgetItem in the list
            for index in range(self.text_items_list.count()):
                list_item = self.text_items_list.item(index)
                if list_item.data(Qt.ItemDataRole.UserRole) == text_item:
                    # Update the text of the QListWidgetItem
                    list_item.setText(text_item.toPlainText())
                    break


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
