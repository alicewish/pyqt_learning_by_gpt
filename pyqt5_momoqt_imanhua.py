import os
import sys

from PyQt6.QtCore import QPointF, QSize, Qt
from PyQt6.QtGui import QAction, QImage, QKeySequence, QPainter, QDoubleValidator, QBrush, QPixmap, QTransform, QFont, \
    QTextCursor
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QGraphicsScene, \
    QGraphicsView, QGraphicsPixmapItem, QLabel, QToolBar, QLineEdit, QDockWidget, QFontComboBox, QHBoxLayout, \
    QListWidget, QPushButton, QSpinBox, QVBoxLayout, QWidget, QGraphicsTextItem, QColorDialog, QListWidgetItem
from qtawesome import icon


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("漫画翻译工具")
        self.resize(1200, 800)

        self.image_item = None
        self.scene = QGraphicsScene(self)
        self.view = QGraphicsView(self)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing, True)
        self.view.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontSavePainterState, True)
        self.view.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)

        # 添加缩放变化信号/槽连接
        self.view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # 创建工具箱
        self.create_docks()
        # 创建动作
        self.create_actions()
        # 创建工具栏
        self.create_tool_bar()

        # 将 QGraphicsView 设置为中心窗口部件
        self.setCentralWidget(self.view)
        self.selected_text_item = None
        self.current_text_item = None
        self.scene.selectionChanged.connect(self.set_current_text_item)

        # 文件夹变量
        self.image_folder = None
        self.image_list = []
        self.current_image_index = -1

        self.image = QImage()
        self.pixmap_item = QGraphicsPixmapItem()

    def create_text_tool(self):
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

        # 将部件添加到布局中
        self.vb_text_tool = QVBoxLayout()
        self.vb_text_tool.addLayout(hb_font_name)
        self.vb_text_tool.addLayout(hb_font_size)
        self.vb_text_tool.addLayout(hb_font_color)
        self.vb_text_tool.addLayout(hb_text_position)

        self.vb_text_tool.addWidget(QLabel("文本项:"))
        self.vb_text_tool.addWidget(self.text_items_list)

        self.text_tool = QWidget()
        self.text_tool.setLayout(self.vb_text_tool)

    def create_docks(self):
        self.create_text_tool()

        self.image_tool = QWidget()
        self.image_tool.setMinimumWidth(200)
        self.folder_tool = QWidget()
        self.folder_tool.setMinimumWidth(200)

        self.text_dock = QDockWidget("文本工具", self)
        self.text_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.text_dock.setWidget(self.text_tool)
        self.text_dock.setMinimumWidth(200)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.text_dock)

        self.image_dock = QDockWidget("图片工具", self)
        self.image_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.image_dock.setWidget(self.image_tool)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.image_dock)

        self.folder_dock = QDockWidget("文件夹工具", self)
        self.folder_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.folder_dock.setWidget(self.folder_tool)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.folder_dock)

    def create_actions(self):
        # 文件菜单
        self.file_menu = self.menuBar().addMenu("File")

        # 添加打开图片操作
        self.open_image_action = QAction("Open Image", self)
        self.open_image_action.setIcon(icon('ei.picture'))
        self.open_image_action.setShortcut(QKeySequence.StandardKey.Open)
        self.open_image_action.triggered.connect(self.open_image)
        self.file_menu.addAction(self.open_image_action)

        # 添加打开文件夹操作
        self.open_folder_action = QAction("Open Folder", self)
        self.open_folder_action.setIcon(icon('ei.folder'))
        self.open_folder_action.setShortcut(QKeySequence("Ctrl+Shift+O"))
        self.open_folder_action.triggered.connect(self.open_folder)
        self.file_menu.addAction(self.open_folder_action)

        # 添加保存图片操作
        self.save_image_action = QAction("Save Image", self)
        self.save_image_action.setIcon(icon('ri.image-edit-fill'))
        self.save_image_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_image_action.triggered.connect(self.save_image)
        self.file_menu.addAction(self.save_image_action)

        # 显示菜单
        self.view_menu = self.menuBar().addMenu("View")

        self.view_menu.addAction(self.text_dock.toggleViewAction())
        self.view_menu.addAction(self.image_dock.toggleViewAction())
        self.view_menu.addAction(self.folder_dock.toggleViewAction())
        self.view_menu.addSeparator()

        self.zoom_in_action = QAction("Zoom In", self)
        self.zoom_in_action.setIcon(icon('ei.zoom-in'))
        self.zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        self.zoom_in_action.triggered.connect(self.zoom_in)
        self.view_menu.addAction(self.zoom_in_action)

        self.zoom_out_action = QAction("Zoom Out", self)
        self.zoom_out_action.setIcon(icon('ei.zoom-out'))
        self.zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        self.zoom_out_action.triggered.connect(self.zoom_out)
        self.view_menu.addAction(self.zoom_out_action)

        self.view_menu.addSeparator()

        self.fit_to_screen_action = QAction("Fit to Screen", self)
        self.fit_to_screen_action.setIcon(icon('mdi6.fit-to-screen-outline'))
        self.fit_to_screen_action.setShortcut(QKeySequence("Ctrl+F"))
        self.fit_to_screen_action.triggered.connect(self.fit_to_screen)
        self.view_menu.addAction(self.fit_to_screen_action)

        self.fit_to_width_action = QAction("Fit to Width", self)
        self.fit_to_width_action.setIcon(icon('ei.text-width'))
        self.fit_to_width_action.setShortcut(QKeySequence("Ctrl+W"))
        self.fit_to_width_action.triggered.connect(self.fit_to_width)
        self.view_menu.addAction(self.fit_to_width_action)

        self.reset_zoom_action = QAction("Reset Zoom", self)
        self.reset_zoom_action.setIcon(icon('mdi6.backup-restore'))
        self.reset_zoom_action.setShortcut(QKeySequence("Ctrl+0"))
        self.reset_zoom_action.triggered.connect(self.reset_zoom)
        self.view_menu.addAction(self.reset_zoom_action)

        # 编辑菜单
        self.edit_menu = self.menuBar().addMenu("Edit")

        self.add_text_action = QAction("Add Text", self)
        self.add_text_action.setIcon(icon('ri.chat-new-line'))
        self.add_text_action.setShortcut(QKeySequence("Ctrl+T"))
        self.add_text_action.triggered.connect(self.add_text)
        self.edit_menu.addAction(self.add_text_action)

        self.delete_text_action = QAction("Delete Text", self)
        self.delete_text_action.setIcon(icon('mdi6.delete-forever-outline'))
        self.delete_text_action.setShortcut(QKeySequence("Ctrl+D"))
        self.delete_text_action.triggered.connect(self.delete_text)
        self.edit_menu.addAction(self.delete_text_action)

        # 导航菜单
        self.nav_menu = self.menuBar().addMenu("Edit")

        # 添加上一张图片操作
        self.prev_image_action = QAction("Previous Image", self)
        self.prev_image_action.setIcon(icon('ei.arrow-left'))
        self.prev_image_action.setShortcut(QKeySequence("Ctrl+Left"))
        self.prev_image_action.triggered.connect(self.prev_image)
        self.nav_menu.addAction(self.prev_image_action)

        # 添加下一张图片操作
        self.next_image_action = QAction("Next Image", self)
        self.next_image_action.setIcon(icon('ei.arrow-right'))
        self.next_image_action.setShortcut(QKeySequence("Ctrl+Right"))
        self.next_image_action.triggered.connect(self.next_image)
        self.nav_menu.addAction(self.next_image_action)

    def create_tool_bar(self):
        # 添加顶部工具栏
        self.tool_bar = QToolBar("Toolbar", self)
        self.tool_bar.setIconSize(QSize(24, 24))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.tool_bar)
        self.tool_bar.setMovable(False)
        self.tool_bar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.tool_bar.addAction(self.open_image_action)
        self.tool_bar.addAction(self.open_folder_action)
        self.tool_bar.addAction(self.save_image_action)
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(self.zoom_in_action)
        self.tool_bar.addAction(self.zoom_out_action)
        self.tool_bar.addAction(self.fit_to_screen_action)
        self.tool_bar.addAction(self.fit_to_width_action)
        self.tool_bar.addAction(self.reset_zoom_action)
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(self.prev_image_action)
        self.tool_bar.addAction(self.next_image_action)

        # 添加缩放百分比输入框
        self.scale_percentage_edit = QLineEdit(self)
        self.scale_percentage_edit.setFixedWidth(60)
        self.scale_percentage_edit.setValidator(QDoubleValidator(1, 1000, 2))
        self.scale_percentage_edit.setText("100.00")
        self.scale_percentage_edit.editingFinished.connect(self.scale_by_percentage)
        self.tool_bar.addWidget(self.scale_percentage_edit)
        self.tool_bar.addWidget(QLabel("%"))

    def open_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Open Folder")
        if folder_path:
            self.image_list = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if
                               f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]
            self.current_image_index = 0
            self.open_image_from_list()

    def open_image_basic(self, pixmap):
        if self.image_item:
            self.scene.removeItem(self.image_item)  # 移除之前的图片项

        self.image_item = self.scene.addPixmap(pixmap)
        self.view.setSceneRect(pixmap.rect().toRectF())
        self.view.setScene(self.scene)
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.view.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing, True)
        self.view.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.view.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontSavePainterState, True)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.update_scale_percentage()
        self.view.setBackgroundBrush(QBrush(Qt.GlobalColor.transparent))

    def open_image(self):
        options = QFileDialog.Option(0)
        options |= QFileDialog.Option.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "",
                                                   "Images (*.png *.xpm *.jpg *.bmp);;All Files (*)", options=options)
        if file_name:
            pixmap = QPixmap(file_name)
            self.open_image_basic(pixmap)

    def open_image_from_list(self):
        if self.image_list and 0 <= self.current_image_index < len(self.image_list):
            pixmap = QPixmap(self.image_list[self.current_image_index])
            self.open_image_basic(pixmap)

    def save_image(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Image", "", "Images (*.png *.xpm *.jpg)")

        if file_name:
            image = QImage(self.scene.sceneRect().size().toSize(), QImage.Format.Format_ARGB32)
            image.fill(Qt.GlobalColor.transparent)

            painter = QPainter(image)
            self.scene.render(painter)
            painter.end()

            image.save(file_name)

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

    def zoom_in(self):
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        current_transform = self.view.transform()
        current_scale = current_transform.m11()
        if current_scale * 1.2 <= 10:
            current_transform.scale(1.2, 1.2)
            self.view.setTransform(current_transform)
            self.update_scale_percentage()

    def zoom_out(self):
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        current_transform = self.view.transform()
        current_scale = current_transform.m11()
        if current_scale / 1.2 >= 0.01:
            current_transform.scale(1 / 1.2, 1 / 1.2)
            self.view.setTransform(current_transform)
            self.update_scale_percentage()

    def fit_to_screen(self):
        if self.image_item:
            self.view.fitInView(self.image_item, Qt.AspectRatioMode.KeepAspectRatio)
            self.view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            self.update_scale_percentage()

    def fit_to_width(self):
        if self.image_item:
            view_width = self.view.viewport().width()
            pixmap_width = self.image_item.pixmap().width()
            scale_factor = view_width / pixmap_width
            self.view.setTransform(QTransform().scale(scale_factor, scale_factor))
            self.view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            self.update_scale_percentage()

    def reset_zoom(self):
        self.view.setTransform(QTransform())  # 使用setTransform代替resetMatrix
        self.update_scale_percentage()

    def update_scale_percentage(self):
        current_scale = round(self.view.transform().m11() * 100, 2)
        self.scale_percentage_edit.setText(str(current_scale))

    def scale_by_percentage(self):
        scale_percentage = float(self.scale_percentage_edit.text())
        target_scale = scale_percentage / 100
        current_scale = self.view.transform().m11()

        scale_factor = target_scale / current_scale
        self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.view.scale(scale_factor, scale_factor)

    def update_tool_box(self, text_item):
        self.x_spinbox.setMaximum(int(self.scene.width()))
        self.y_spinbox.setMaximum(int(self.scene.height()))
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
