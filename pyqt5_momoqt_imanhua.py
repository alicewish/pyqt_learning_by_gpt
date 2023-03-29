import os
import re
import sys
from subprocess import Popen

from PyQt6.QtCore import QPointF, QSettings, QSize, Qt
from PyQt6.QtGui import QAction, QBrush, QDoubleValidator, QFont, QImage, QKeySequence, QPainter, QPixmap, \
    QTextCursor, QTransform, QIcon
from PyQt6.QtWidgets import QApplication, QColorDialog, QDockWidget, QFileDialog, QFontComboBox, \
    QGraphicsPixmapItem, QGraphicsScene, QGraphicsTextItem, QGraphicsView, QHBoxLayout, QLabel, QLineEdit, QListWidget, \
    QListWidgetItem, QMainWindow, QMenu, QMessageBox, QPushButton, QSlider, QSpinBox, QToolBar, \
    QVBoxLayout, QWidget, QToolButton, QListView, QTabWidget, QAbstractItemView, QStatusBar
from loguru import logger
from natsort import natsorted
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

        self.selected_text_item = None
        self.current_text_item = None
        self.scene.selectionChanged.connect(self.set_current_text_item)

        # 文件夹变量
        self.image_folder = None
        self.image_list = []
        self.current_image_index = -1
        self.screen_scaling_factor = 1 / self.get_screen_scaling_factor()
        self.recent_folders = []

        self.settings = QSettings("YourOrganization", "Momohanhua")  # 根据需要修改组织和应用名

        self.image = QImage()
        self.pixmap_item = QGraphicsPixmapItem()

        # 创建工具箱
        self.create_docks()
        # 创建动作
        self.create_actions()
        # 创建工具栏
        self.create_tool_bar()
        # 创建状态栏
        self.create_status_bar()

        # 将 QGraphicsView 设置为中心窗口部件
        self.setCentralWidget(self.view)

        self.read_config()
        # self.restoreGeometry(self.settings.value("window_geometry"))
        # self.restoreState(self.settings.value("window_state"))

        self.show()

    def create_text_tool(self):
        # 创建字体选择器
        self.font_name_label = QLabel("字体:")
        self.font_combo = QFontComboBox(self)
        self.font_combo.setFontFilters(QFontComboBox.FontFilter.AllFonts)
        self.font_combo.currentFontChanged.connect(self.update_text_item_font)

        # 创建字体大小选择器
        self.font_size_label = QLabel("字号:")
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

        # 在 create_text_tool 方法中添加透明度滑块
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.opacity_slider.setRange(0, 255)
        self.opacity_slider.setValue(255)
        self.opacity_slider.valueChanged.connect(self.update_text_item_opacity)

        # 创建文本项的 X 和 Y 坐标选择器
        position_label = QLabel("位置:")
        self.x_spinbox = QSpinBox(self)
        self.x_spinbox.setRange(0, int(self.scene.width()))
        self.y_spinbox = QSpinBox(self)
        self.y_spinbox.setRange(0, int(self.scene.height()))
        self.x_spinbox.valueChanged.connect(self.update_text_item_position)
        self.y_spinbox.valueChanged.connect(self.update_text_item_position)

        self.text_items_list = QListWidget(self)
        self.text_items_list.itemClicked.connect(self.text_item_selected)

        hb_font_name_size = QHBoxLayout()
        hb_font_name_size.addWidget(self.font_name_label)
        hb_font_name_size.addWidget(self.font_combo)
        hb_font_name_size.addWidget(self.font_size_label)
        hb_font_name_size.addWidget(self.font_size_spinbox)

        self.hb_font_color_alpha = QHBoxLayout()
        self.hb_font_color_alpha.addWidget(color_label)
        self.hb_font_color_alpha.addWidget(self.color_button)
        self.hb_font_color_alpha.addWidget(QLabel("透明度:"))
        self.hb_font_color_alpha.addWidget(self.opacity_slider)

        hb_text_position = QHBoxLayout()
        hb_text_position.addWidget(position_label)
        hb_text_position.addWidget(self.x_spinbox)
        hb_text_position.addWidget(self.y_spinbox)

        # 将部件添加到布局中
        self.vb_text_tool = QVBoxLayout()
        self.vb_text_tool.addLayout(hb_font_name_size)
        self.vb_text_tool.addLayout(self.hb_font_color_alpha)
        self.vb_text_tool.addLayout(hb_text_position)
        self.vb_text_tool.addWidget(QLabel("文本项:"))
        self.vb_text_tool.addWidget(self.text_items_list)

        self.text_tool = QWidget()
        self.text_tool.setLayout(self.vb_text_tool)

    def create_docks(self):
        self.create_text_tool()

        self.layer_tool = QWidget()
        self.layer_tool.setMinimumWidth(200)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("搜索图片 (支持正则表达式)")
        self.search_bar.textChanged.connect(self.filter_image_list)

        self.image_list_widget = QListWidget(self)
        self.image_list_model = self.image_list_widget.model()
        self.image_list_selection_model = self.image_list_widget.selectionModel()
        self.image_list_widget.itemSelectionChanged.connect(self.select_image_from_list)
        self.image_list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.image_list_widget.customContextMenuRequested.connect(self.show_image_list_context_menu)

        self.tab_widget = QTabWidget()
        self.thumbnail_list_widget = QListWidget(self)
        self.thumbnail_list_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.thumbnail_list_widget.setViewMode(QListView.ViewMode.IconMode)
        self.thumbnail_list_widget.setFlow(QListView.Flow.TopToBottom)
        self.thumbnail_list_widget.setWrapping(False)
        self.thumbnail_list_widget.setResizeMode(QListView.ResizeMode.Adjust)
        self.thumbnail_list_widget.setWordWrap(True)
        self.thumbnail_list_widget.setIconSize(QSize(100, 100))
        self.thumbnail_list_widget.setSpacing(10)
        self.thumbnail_list_widget.itemClicked.connect(self.select_image_from_list)

        self.tab_widget.addTab(self.image_list_widget, "图片名列表")
        self.tab_widget.addTab(self.thumbnail_list_widget, "图片缩略图列表")

        # 添加按钮
        self.case_sensitive_button = QToolButton()
        self.case_sensitive_button.setIcon(icon('msc.case-sensitive'))
        self.case_sensitive_button.setCheckable(True)
        self.case_sensitive_button.setText("Case Sensitive")
        self.case_sensitive_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)

        self.whole_word_button = QToolButton()
        self.whole_word_button.setIcon(icon('msc.whole-word'))
        self.whole_word_button.setCheckable(True)
        self.whole_word_button.setText("Whole Word")
        self.whole_word_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)

        self.regex_button = QToolButton()
        self.regex_button.setIcon(icon('mdi.regex'))
        self.regex_button.setCheckable(True)
        self.regex_button.setText("Use Regex")
        self.regex_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)

        # 连接按钮信号
        self.case_sensitive_button.clicked.connect(self.refresh_search_results)
        self.whole_word_button.clicked.connect(self.refresh_search_results)
        self.regex_button.clicked.connect(self.refresh_search_results)

        # 将按钮放在 QLineEdit 的右侧
        self.hb_search_bar = QHBoxLayout()
        self.hb_search_bar.setContentsMargins(0, 0, 0, 0)
        self.hb_search_bar.addStretch()
        self.hb_search_bar.addWidget(self.case_sensitive_button)
        self.hb_search_bar.addWidget(self.whole_word_button)
        self.hb_search_bar.addWidget(self.regex_button)
        self.search_bar.setLayout(self.hb_search_bar)

        self.vb_image_list = QVBoxLayout()
        self.vb_image_list.addWidget(self.search_bar)
        self.vb_image_list.addWidget(self.tab_widget)

        self.pics_widget = QWidget()
        self.pics_widget.setLayout(self.vb_image_list)

        self.text_dock = QDockWidget("文本", self)
        self.text_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.text_dock.setWidget(self.text_tool)
        self.text_dock.setMinimumWidth(200)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.text_dock)

        self.layer_dock = QDockWidget("图层", self)
        self.layer_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.layer_dock.setWidget(self.layer_tool)
        self.layer_dock.setMinimumWidth(200)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.layer_dock)

        self.pics_dock = QDockWidget("图片列表", self)
        self.pics_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.pics_dock.setWidget(self.pics_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.pics_dock)

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
        self.view_menu.addAction(self.layer_dock.toggleViewAction())
        self.view_menu.addAction(self.pics_dock.toggleViewAction())
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
        self.fit_to_screen_action.setCheckable(True)  # 添加这一行
        self.fit_to_screen_action.toggled.connect(self.fit_to_screen_toggled)  # 修改这一行
        self.view_menu.addAction(self.fit_to_screen_action)

        self.fit_to_width_action = QAction("Fit to Width", self)
        self.fit_to_width_action.setIcon(icon('ei.resize-horizontal'))
        self.fit_to_width_action.setShortcut(QKeySequence("Ctrl+W"))
        self.fit_to_width_action.setCheckable(True)  # 添加这一行
        self.fit_to_width_action.toggled.connect(self.fit_to_width_toggled)  # 修改这一行
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

        self.clear_all_text_action = QAction("Clear All Text", self)
        self.clear_all_text_action.setIcon(icon('mdi6.delete-sweep-outline'))
        self.clear_all_text_action.setShortcut(QKeySequence("Ctrl+Shift+D"))
        self.clear_all_text_action.triggered.connect(self.clear_all_text)
        self.edit_menu.addAction(self.clear_all_text_action)

        # 导航菜单
        self.nav_menu = self.menuBar().addMenu("Navigate")

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

        # 添加最近打开文件夹菜单项
        self.recent_folders_menu = self.file_menu.addMenu("Recent Folders")
        self.update_recent_folders_menu()

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

    def create_status_bar(self):
        # ================状态栏================
        self.status_bar = QStatusBar()
        # 设置状态栏，类似布局设置
        self.setStatusBar(self.status_bar)

    def update_image_list(self):
        # 初始化 image_list 为空列表
        self.image_list = []

        # 遍历 self.image_folder 文件夹下的所有文件
        for f in os.listdir(self.image_folder):
            # 检查文件是否是图片格式
            if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                # 检查文件是否不是目录（即只识别文件夹内的图片，不识别子文件夹内的图片）
                if not os.path.isdir(os.path.join(self.image_folder, f)):
                    # 将图片文件路径添加到 image_list 中
                    self.image_list.append(os.path.join(self.image_folder, f))

    def open_folder(self):
        self.image_folder = QFileDialog.getExistingDirectory(self, "Open Folder")
        if self.image_folder:
            self.update_image_list()

            if not self.image_list:
                QMessageBox.warning(self, "Warning", "No image files found in the selected folder.")
                return

            self.update_image_list_widget()
            self.current_image_index = 0
            self.open_image_from_list()
            pixmap = QPixmap(self.image_list[self.current_image_index])
            self.setWindowTitle(f"漫画翻译工具 - {self.image_folder}")
            self.add_recent_folder(self.image_folder)  # 在 open_folder 方法中

    def select_image_by_path(self, image_file):
        self.current_image_index = self.image_list.index(image_file)
        pixmap = QPixmap(image_file)
        self.open_image_basic(pixmap)
        self.image_list_widget.setCurrentRow(self.current_image_index)

    def open_image_basic(self, pixmap):
        if self.image_item:
            self.scene.removeItem(self.image_item)  # 移除之前的图片项

            # 清除之前的所有文本框
            for i in range(self.text_items_list.count()):
                item = self.text_items_list.item(i)
                text_item = item.data(Qt.ItemDataRole.UserRole)
                self.scene.removeItem(text_item)

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
        self.view.setBackgroundBrush(QBrush(Qt.GlobalColor.lightGray))
        # 在设置 QGraphicsView 属性之后添加以下行
        self.view.setTransform(QTransform().scale(self.screen_scaling_factor, self.screen_scaling_factor))
        self.update_scale_percentage()
        self.thumbnail_list_widget.setCurrentRow(self.current_image_index)
        self.update_status_bar_info()

        if self.fit_to_screen_action.isChecked():
            self.fit_to_screen()
        elif self.fit_to_width_action.isChecked():
            self.fit_to_width()

    def open_image(self):
        options = QFileDialog.Option(0)
        options |= QFileDialog.Option.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, "Open Image", "",
                                                   "Images (*.png *.xpm *.jpg *.bmp);;All Files (*)", options=options)
        if file_name:
            pixmap = QPixmap(file_name)
            self.open_image_basic(pixmap)
            self.image_list = [file_name]
            self.current_image_index = 0

            # 清空文本项列表
            self.text_items_list.clear()

            self.image_folder = os.path.dirname(file_name)
            self.image_list = [file_name]

            self.current_image_index = self.image_list.index(file_name)
            self.update_image_list_widget()

            self.setWindowTitle(f"漫画翻译工具 - {file_name}")
            self.add_recent_folder(self.image_folder)  # 在 open_image 方法中

    def open_image_from_list(self):
        while self.image_list and 0 <= self.current_image_index < len(self.image_list):
            if not os.path.exists(self.image_list[self.current_image_index]):
                self.image_list.pop(self.current_image_index)
                self.update_image_list_widget()
                continue
            break

        if self.image_list and 0 <= self.current_image_index < len(self.image_list):
            pixmap = QPixmap(self.image_list[self.current_image_index])
            self.open_image_basic(pixmap)

    def update_image_list_widget(self):
        self.image_list_widget.clear()

        # 对 image_list 进行自然排序
        self.image_list = natsorted(self.image_list)

        for image in self.image_list:
            item = QListWidgetItem(os.path.basename(image))
            item.setData(Qt.ItemDataRole.UserRole, image)

            thumbnail_item = QListWidgetItem(os.path.basename(image))
            thumbnail_item.setIcon(QIcon(image))
            thumbnail_item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
            thumbnail_item.setData(Qt.ItemDataRole.UserRole, image)

            if os.path.exists(image):
                self.image_list_widget.addItem(item)
                self.thumbnail_list_widget.addItem(thumbnail_item)

        self.update_status_bar_info()

    def update_status_bar_info(self):
        total_images = len(self.image_list)
        if total_images > 0:
            current_image_index = self.current_image_index + 1
            image_path = self.image_list[self.current_image_index]
            image_size = QPixmap(image_path).size()
            image_file_size = os.path.getsize(image_path)
            status_text = f"{current_image_index}/{total_images} | 地址: {image_path} | 长度: {image_size.width()} 宽度: {image_size.height()} | 文件大小: {image_file_size} bytes"
        else:
            status_text = "No images found in the selected folder."

        self.status_bar.showMessage(status_text)

    def select_image_from_list(self):
        active_list_widget = self.tab_widget.currentWidget()
        selected_items = active_list_widget.selectedItems()
        if not selected_items:
            return
        current_item = selected_items[0]
        index = active_list_widget.row(current_item)

        if index != self.current_image_index:
            self.current_image_index = index
            image_file = current_item.data(Qt.ItemDataRole.UserRole)  # 从当前项目的 UserRole 数据中获取路径
            pixmap = QPixmap(image_file)  # 使用正确的路径创建 QPixmap 对象
            self.open_image_basic(pixmap)  # 打开图片

        self.image_list_widget.setCurrentRow(self.current_image_index)
        self.thumbnail_list_widget.setCurrentRow(self.current_image_index)

    def open_image_in_viewer(self, file_path):
        if sys.platform == 'win32':
            os.startfile(os.path.normpath(file_path))
        elif sys.platform == 'darwin':
            Popen(['open', file_path])
        else:
            Popen(['xdg-open', file_path])

    def open_file_in_explorer(self, file_path):
        folder_path = os.path.dirname(file_path)

        if sys.platform == 'win32':
            Popen(f'explorer /select,"{os.path.normpath(file_path)}"')
        elif sys.platform == 'darwin':
            Popen(['open', '-R', file_path])
        else:
            Popen(['xdg-open', folder_path])

    def open_image_in_photoshop(self, file_path):
        if sys.platform == 'win32':
            photoshop_executable_path = "C:/Program Files/Adobe/Adobe Photoshop CC 2019/Photoshop.exe"  # 请根据您的Photoshop安装路径进行修改
            Popen([photoshop_executable_path, file_path])
        elif sys.platform == 'darwin':
            photoshop_executable_path = "/Applications/Adobe Photoshop 2021/Adobe Photoshop 2021.app"  # 修改此行
            Popen(['open', '-a', photoshop_executable_path, file_path])
        else:
            QMessageBox.warning(self, "Warning", "This feature is not supported on this platform.")

    def copy_to_clipboard(self, text):
        clipboard = QApplication.clipboard()
        clipboard.setText(text)

    def show_image_list_context_menu(self, point):
        item = self.image_list_widget.itemAt(point)
        if item:
            context_menu = QMenu(self)
            open_file_action = QAction("在文件浏览器中打开", self)
            open_file_action.triggered.connect(lambda: self.open_file_in_explorer(item.data(Qt.ItemDataRole.UserRole)))
            open_image_action = QAction("在图像浏览器中打开", self)
            open_image_action.triggered.connect(lambda: self.open_image_in_viewer(item.data(Qt.ItemDataRole.UserRole)))
            context_menu.addAction(open_file_action)
            context_menu.addAction(open_image_action)

            # 添加一个打开方式子菜单
            open_with_menu = context_menu.addMenu("Open with")
            open_with_photoshop = QAction("Photoshop", self)
            open_with_menu.addAction(open_with_photoshop)

            # 添加拷贝图片路径、拷贝图片名的选项
            copy_image_path = QAction("Copy Image Path", self)
            copy_image_name = QAction("Copy Image Name", self)

            context_menu.addAction(copy_image_path)
            context_menu.addAction(copy_image_name)

            # 连接触发器
            open_with_photoshop.triggered.connect(
                lambda: self.open_image_in_photoshop(item.data(Qt.ItemDataRole.UserRole)))
            copy_image_path.triggered.connect(lambda: self.copy_to_clipboard(item.data(Qt.ItemDataRole.UserRole)))
            copy_image_name.triggered.connect(lambda: self.copy_to_clipboard(item.text()))
            context_menu.exec(self.image_list_widget.mapToGlobal(point))

    def refresh_search_results(self):
        search_text = self.search_bar.text()
        self.filter_image_list(search_text)

    def filter_image_list(self, search_text):
        case_sensitive = self.case_sensitive_button.isChecked()
        whole_word = self.whole_word_button.isChecked()
        use_regex = self.regex_button.isChecked()

        flags = re.IGNORECASE if not case_sensitive else 0

        if use_regex:
            if whole_word:
                search_text = fr"\b{search_text}\b"

            try:
                regex = re.compile(search_text, flags)
            except re.error:
                return
        else:
            if whole_word:
                search_text = fr"\b{re.escape(search_text)}\b"
            else:
                search_text = re.escape(search_text)

            regex = re.compile(search_text, flags)

        for index in range(self.image_list_widget.count()):
            item = self.image_list_widget.item(index)
            item_text = item.text()
            match = regex.search(item_text)
            if match:
                item.setHidden(False)
            else:
                item.setHidden(True)

        for index in range(self.thumbnail_list_widget.count()):
            item = self.thumbnail_list_widget.item(index)
            item_text = item.text()
            match = regex.search(item_text)
            if match:
                item.setHidden(False)
            else:
                item.setHidden(True)

    def get_filtered_image_list(self):
        search_text = self.search_bar.text()
        try:
            regex = re.compile(search_text)
        except re.error:
            return self.image_list

        filtered_image_list = [image for image in self.image_list if regex.search(os.path.basename(image))]
        return filtered_image_list

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
        filtered_image_list = self.get_filtered_image_list()
        current_image_path = self.image_list[self.current_image_index]
        current_filtered_image_index = filtered_image_list.index(current_image_path)

        if current_filtered_image_index > 0:
            prev_image_path = filtered_image_list[current_filtered_image_index - 1]
            self.current_image_index = self.image_list.index(prev_image_path)
            pixmap = QPixmap(prev_image_path)
            self.open_image_basic(pixmap)
            self.image_list_widget.setCurrentRow(self.current_image_index)

    def next_image(self):
        filtered_image_list = self.get_filtered_image_list()
        current_image_path = self.image_list[self.current_image_index]
        current_filtered_image_index = filtered_image_list.index(current_image_path)

        if current_filtered_image_index < len(filtered_image_list) - 1:
            next_image_path = filtered_image_list[current_filtered_image_index + 1]
            self.current_image_index = self.image_list.index(next_image_path)
            pixmap = QPixmap(next_image_path)
            self.open_image_basic(pixmap)
            self.image_list_widget.setCurrentRow(self.current_image_index)

    def update_recent_folders_menu(self):
        self.recent_folders_menu.clear()
        recent_folders = self.settings.value("recent_folders", [])

        for folder in recent_folders:
            action = QAction(folder, self)
            action.triggered.connect(lambda checked, p=folder: self.open_folder_by_path(p))
            self.recent_folders_menu.addAction(action)

    def add_recent_folder(self, folder_path):
        recent_folders = self.settings.value("recent_folders", [])
        if folder_path in recent_folders:
            recent_folders.remove(folder_path)
        recent_folders.insert(0, folder_path)
        recent_folders = recent_folders[:10]  # 保留最多10个最近文件夹

        self.settings.setValue("recent_folders", recent_folders)
        self.update_recent_folders_menu()

    def open_folder_by_path(self, folder_path):
        if os.path.exists(folder_path):
            self.image_folder = folder_path
            self.update_image_list()
            self.update_image_list_widget()
            self.setWindowTitle(f"漫画翻译工具 - {folder_path}")

            if not self.image_list:
                QMessageBox.warning(self, "Warning", "No image files found in the selected folder.")
            else:
                self.current_image_index = 0
                self.open_image_from_list()
                self.image_list_widget.setCurrentRow(self.current_image_index)

    def get_screen_scaling_factor(self):
        screen = QApplication.primaryScreen()
        if sys.platform == 'darwin':  # 如果是 MacOS 系统
            return screen.devicePixelRatio()
        else:
            return 1

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

    def fit_to_screen_toggled(self, checked):
        if checked:
            self.fit_to_width_action.setChecked(False)
        self.fit_to_screen()

    def fit_to_width_toggled(self, checked):
        if checked:
            self.fit_to_screen_action.setChecked(False)
        self.fit_to_width()

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
        scaling_factor = self.get_screen_scaling_factor()
        # 使用 setTransform 代替 resetMatrix 并应用缩放因子
        self.view.setTransform(QTransform().scale(1 / scaling_factor, 1 / scaling_factor))
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

        center_pos = self.view.mapToScene(self.view.viewport().rect().center())
        text_item.setPos(center_pos)
        self.scene.addItem(text_item)

        list_item = QListWidgetItem(f"文本框 {self.text_items_list.count() + 1}")
        self.text_items_list.addItem(list_item)
        list_item.setData(Qt.ItemDataRole.UserRole, text_item)

    def delete_text(self):
        if self.current_text_item:
            # 从场景删除文本
            self.scene.removeItem(self.current_text_item)

            # 找到对应的 QListWidgetItem 并从列表中删除
            for index in range(self.text_items_list.count()):
                list_item = self.text_items_list.item(index)
                if list_item.data(Qt.ItemDataRole.UserRole) == self.current_text_item:
                    self.text_items_list.takeItem(index)
                    break

            # 清除当前文本项并更新工具箱
            self.current_text_item = None
            self.update_tool_box(None)

    def update_text_item_position(self):
        if self.current_text_item:
            pos = QPointF(self.x_spinbox.value(), self.y_spinbox.value())
            self.current_text_item.setPos(pos)
            if self.text_items_list.currentItem():  # 新增判断条件
                current_item = self.text_items_list.currentItem()
                if current_item:
                    current_item.setText(self.current_text_item.toPlainText())

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

    def text_item_selected(self, list_item):
        if list_item:
            text_item = list_item.data(Qt.ItemDataRole.UserRole)
            text_item.setSelected(True)
            self.set_current_text_item()
            self.text_items_list.setCurrentItem(list_item)
        else:
            self.current_text_item.setSelected(False)
            self.set_current_text_item()

    def update_list_item(self, text_item):
        if text_item:
            # Find the corresponding QListWidgetItem in the list
            for index in range(self.text_items_list.count()):
                list_item = self.text_items_list.item(index)
                if list_item.data(Qt.ItemDataRole.UserRole) == text_item:
                    # Update the text of the QListWidgetItem
                    list_item.setText(text_item.toPlainText())
                    break

    # 添加槽方法 update_text_item_opacity
    def update_text_item_opacity(self, opacity):
        if self.current_text_item:
            color = self.current_text_item.defaultTextColor()
            color.setAlpha(opacity)
            self.current_text_item.setDefaultTextColor(color)

    def read_config(self):
        last_opened_folder = self.settings.value("last_opened_folder", "")
        if last_opened_folder and os.path.exists(last_opened_folder) and os.path.isdir(last_opened_folder):
            self.open_folder_by_path(last_opened_folder)

    def closeEvent(self, event):
        if self.image_folder:
            self.settings.setValue("last_opened_folder", self.image_folder)
        else:
            self.settings.setValue("last_opened_folder", "")
        self.settings.setValue("window_geometry", self.saveGeometry())
        self.settings.setValue("window_state", self.saveState())
        event.accept()


@logger.catch
def main_qt():
    window = MainWindow()
    sys.exit(appgui.exec())


if __name__ == "__main__":
    appgui = QApplication(sys.argv)
    main_qt()
