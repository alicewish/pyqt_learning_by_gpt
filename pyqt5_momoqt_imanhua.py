import codecs
import os
import os.path
import re
import sys
import webbrowser
from copy import deepcopy
from csv import reader, writer
from functools import wraps
from getpass import getuser
from hashlib import md5
from locale import getdefaultlocale
from os.path import abspath, dirname, exists, expanduser, getsize, isfile
from pathlib import Path
from platform import system, uname
from re import findall
from shutil import copy2
from subprocess import Popen, call
from time import time
from traceback import print_exc
from uuid import getnode

import xmltodict
from PyQt6.QtCore import QPointF, QSettings, QSize, Qt, QTranslator
from PyQt6.QtGui import QAction, QBrush, QDoubleValidator, QFont, QImage, QKeySequence, QPainter, QPixmap, \
    QTextCursor, QTransform, QIcon, QActionGroup, QGuiApplication
from PyQt6.QtWidgets import QApplication, QColorDialog, QDockWidget, QFileDialog, QFontComboBox, \
    QGraphicsPixmapItem, QGraphicsScene, QGraphicsTextItem, QGraphicsView, QHBoxLayout, QLabel, QLineEdit, QListWidget, \
    QListWidgetItem, QMainWindow, QMenu, QMessageBox, QPushButton, QSlider, QSpinBox, QToolBar, \
    QVBoxLayout, QWidget, QToolButton, QListView, QTabWidget, QAbstractItemView, QStatusBar, QDialog
from loguru import logger
from natsort import natsorted
from qtawesome import icon
from ruamel.yaml import YAML


# ================================参数区================================
# @logger.catch
def a1_const():
    return


# Platforms
SYSTEM = ''
platform_system = system()
platform_uname = uname()
os_kernal = platform_uname.machine
if os_kernal in ['x86_64', 'AMD64']:
    if platform_system == 'Windows':
        SYSTEM = 'WINDOWS'
    elif platform_system == 'Linux':
        SYSTEM = 'LINUX'
    else:  # 'Darwin'
        SYSTEM = 'MAC'
else:  # os_kernal = 'arm64'
    if platform_system == 'Windows':
        SYSTEM = 'WINDOWS'
    elif platform_system == 'Darwin':
        SYSTEM = 'M1'
    else:
        SYSTEM = 'PI'

locale_tup = getdefaultlocale()
lang_code = locale_tup[0]

username = getuser()
homedir = expanduser("~")
DOWNLOADS = Path(homedir) / 'Downloads'
DOCUMENTS = Path(homedir) / 'Documents'

mac_address = ':'.join(findall('..', '%012x' % getnode()))
node_name = platform_uname.node

current_dir = dirname(abspath(__file__))
current_dir = Path(current_dir)

dirpath = os.getcwd()
ProgramFolder = Path(dirpath)
UserDataFolder = ProgramFolder / 'MomoHanhuaUserData'

if SYSTEM == 'WINDOWS':
    encoding = 'gbk'
    line_feed = '\n'
    cmct = 'ctrl'
else:
    encoding = 'utf-8'
    line_feed = '\n'
    cmct = 'command'

line_feeds = line_feed * 2

lf = line_feed
lfs = line_feeds

ignores = ('~$', '._')

type_dic = {
    'xlsx': '.xlsx',
    'csv': '.csv',
    'pr': '.prproj',
    'psd': '.psd',
    'tor': '.torrent',
    'xml': '.xml',
    'audio': ('.aif', '.mp3', '.wav', '.flac', '.m4a', '.ogg'),
    'video': ('.mp4', '.mkv', '.avi', '.flv', '.mov', '.wmv'),
    'compressed': ('.zip', '.rar', '.7z', '.tar', '.gz', '.bz2'),
    'font': ('.ttc', '.ttf', '.otf'),
    'comic': ('.cbr', '.cbz', '.rar', '.zip', '.pdf', '.txt'),
    'pic': ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'),
    'log': '.log',
    'json': '.json',
    'pickle': '.pkl',
    'python': '.py',
    'txt': '.txt',
    'doc': ('.doc', '.docx'),
    'ppt': ('.ppt', '.pptx'),
    'pdf': '.pdf',
    'html': ('.html', '.htm'),
    'css': '.css',
    'js': '.js',
    'markdown': ('.md', '.markdown'),
}

APP_NAME = 'iManhua'
MAJOR_VERSION = 1
MINOR_VERSION = 0
APP_VERSION = f'v{MAJOR_VERSION}.{MINOR_VERSION}'
APP_AUTHOR = '墨问非名'

video_width = 1920
video_height = 1080
video_size = (video_width, video_height)

pos_0 = (0, 0)
pos_c = ('center', 'center')
pylupdate = "pylupdate6"
lrelease = "lrelease"

py_path = Path(__file__).resolve()
py_dev_path = py_path.parent / f'{py_path.stem}_dev.py'

special_keywords = [
    'setIcon', 'icon',
    'setShortcut', 'QKeySequence',
    'QSettings', 'value', 'setValue',
    'triggered',
    'setWindowTitle', 'windowTitle',
]

language_tuples = [
    # ================支持的语言================
    ('zh_CN', 'Simplified Chinese', '简体中文', '简体中文'),
    ('zh_TW', 'Traditional Chinese', '繁体中文', '繁體中文'),
    ('en_US', 'English', '英语', 'English'),
    ('ja_JP', 'Japanese', '日语', '日本語'),
    ('ko_KR', 'Korean', '韩语', '한국어'),
    # ================未来支持的语言================
    # ('es_ES', 'Spanish', '西班牙语', 'Español'),
    # ('fr_FR', 'French', '法语', 'Français'),
    # ('de_DE', 'German', '德语', 'Deutsch'),
    # ('it_IT', 'Italian', '意大利语', 'Italiano'),
    # ('pt_PT', 'Portuguese', '葡萄牙语', 'Português'),
    # ('ru_RU', 'Russian', '俄语', 'Русский'),
    # ('ar_AR', 'Arabic', '阿拉伯语', 'العربية'),
    # ('nl_NL', 'Dutch', '荷兰语', 'Nederlands'),
    # ('sv_SE', 'Swedish', '瑞典语', 'Svenska'),
    # ('tr_TR', 'Turkish', '土耳其语', 'Türkçe'),
    # ('pl_PL', 'Polish', '波兰语', 'Polski'),
    # ('he_IL', 'Hebrew', '希伯来语', 'עברית'),
    # ('da_DK', 'Danish', '丹麦语', 'Dansk'),
    # ('fi_FI', 'Finnish', '芬兰语', 'Suomi'),
    # ('no_NO', 'Norwegian', '挪威语', 'Norsk'),
    # ('hu_HU', 'Hungarian', '匈牙利语', 'Magyar'),
    # ('cs_CZ', 'Czech', '捷克语', 'Čeština'),
    # ('ro_RO', 'Romanian', '罗马尼亚语', 'Română'),
    # ('el_GR', 'Greek', '希腊语', 'Ελληνικά'),
    # ('id_ID', 'Indonesian', '印度尼西亚语', 'Bahasa Indonesia'),
    # ('th_TH', 'Thai', '泰语', 'ภาษาไทย'),
]


def timer_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time()
        result = func(*args, **kwargs)
        elapsed_time = time() - start_time

        hours, rem = divmod(elapsed_time, 3600)
        minutes, seconds = divmod(rem, 60)
        show_run_time = f"{int(hours)}时{int(minutes)}分{seconds:.2f}秒" if hours > 0 else f"{int(minutes)}分{seconds:.2f}秒"

        print(f"{func.__name__} took: {show_run_time}")
        return result

    return wrapper


def is_decimal_or_comma(s):
    pattern = r'^\d*\.?\d*$|^\d*[,]?\d*$'
    return bool(re.match(pattern, s))


def is_valid_file(file_path, suffixes):
    if not file_path.is_file():
        return False
    if not file_path.stem.startswith(ignores):
        if suffixes:
            return file_path.suffix.lower() in suffixes
        else:
            return True
    return False


# @logger.catch
def printe(e):
    print(e)
    logger.error(e)
    print_exc()


def get_files_custom(rootdir, file_type=None, direct=False):
    rootdir = Path(rootdir)
    file_paths = []

    # 获取文件类型的后缀
    # 默认为所有文件
    suffixes = type_dic.get(file_type, file_type)
    if isinstance(suffixes, str):
        suffixes = (suffixes,)

    # 如果根目录存在
    if rootdir and rootdir.exists():
        # 只读取当前文件夹下的文件
        if direct:
            files = os.listdir(rootdir)
            for file in files:
                file_path = Path(rootdir) / file
                if is_valid_file(file_path, suffixes):
                    file_paths.append(file_path)
        # 读取所有文件
        else:
            for root, dirs, files in os.walk(rootdir):
                for file in files:
                    file_path = Path(root) / file
                    if is_valid_file(file_path, suffixes):
                        file_paths.append(file_path)

    # 使用natsorted()进行自然排序，
    # 使列表中的字符串按照数字顺序进行排序
    file_paths = natsorted(file_paths)
    return file_paths


# ================读取文本================
# @logger.catch
def read_txt(file_path, encoding='utf-8'):
    """
    读取指定文件路径的文本内容。

    :param file_path: 文件路径
    :param encoding: 文件编码，默认为'utf-8'
    :return: 返回读取到的文件内容，如果文件不存在则返回None
    """
    file_content = None
    if file_path.exists():
        with open(file_path, mode='r', encoding=encoding) as file_object:
            file_content = file_object.read()
    return file_content


# ================写入文件================
# @logger.catch
def write_txt(file_path, text_input, encoding='utf-8', ignore_empty=True):
    """
    将文本内容写入指定的文件路径。

    :param file_path: 文件路径
    :param text_input: 要写入的文本内容，可以是字符串或字符串列表
    :param encoding: 文件编码，默认为'utf-8'
    :param ignore_empty: 是否忽略空内容，默认为True
    """
    if text_input:
        save_text = True

        if isinstance(text_input, list):
            otext = lf.join(text_input)
        else:
            otext = text_input

        file_content = read_txt(file_path, encoding)

        if file_content == otext or (ignore_empty and otext == ''):
            save_text = False

        if save_text:
            with open(file_path, mode='w', encoding=encoding, errors='ignore') as f:
                f.write(otext)


# ================对文件算MD5================
# @logger.catch
def md5_w_size(path, blksize=2 ** 20):
    if isfile(path) and exists(path):  # 判断目标是否文件,及是否存在
        file_size = getsize(path)
        if file_size <= 256 * 1024 * 1024:  # 512MB
            with open(path, 'rb') as f:
                cont = f.read()
            hash_object = md5(cont)
            t_md5 = hash_object.hexdigest()
            return t_md5, file_size
        else:
            m = md5()
            with open(path, 'rb') as f:
                while True:
                    buf = f.read(blksize)
                    if not buf:
                        break
                    m.update(buf)
            t_md5 = m.hexdigest()
            return t_md5, file_size
    else:
        return None


def write_csv(csv_path, data_input, headers=None):
    temp_csv = csv_path.parent / 'temp.csv'

    try:
        if isinstance(data_input, list):
            if len(data_input) >= 1:
                if csv_path.exists():
                    with codecs.open(temp_csv, 'w', 'utf_8_sig') as f:
                        f_csv = writer(f)
                        if headers:
                            f_csv.writerow(headers)
                        f_csv.writerows(data_input)
                    if md5_w_size(temp_csv) != md5_w_size(csv_path):
                        copy2(temp_csv, csv_path)
                    if temp_csv.exists():
                        os.remove(temp_csv)
                else:
                    with codecs.open(csv_path, 'w', 'utf_8_sig') as f:
                        f_csv = writer(f)
                        if headers:
                            f_csv.writerow(headers)
                        f_csv.writerows(data_input)
        else:  # DataFrame
            if csv_path.exists():
                data_input.to_csv(temp_csv, encoding='utf-8', index=False)
                if md5_w_size(temp_csv) != md5_w_size(csv_path):
                    copy2(temp_csv, csv_path)
                if temp_csv.exists():
                    os.remove(temp_csv)
            else:
                data_input.to_csv(csv_path, encoding='utf-8', index=False)
    except BaseException as e:
        printe(e)


class Settings:
    def __init__(self, file_path):
        self.file_path = file_path
        self.yaml = YAML()
        self.settings = None

        if os.path.exists(self.file_path):
            self.read_settings()
        else:
            self.settings = {}
            self.save_settings()

    def read_settings(self):
        with open(self.file_path, 'r') as yaml_file:
            self.settings = self.yaml.load(yaml_file)

    def save_settings(self):
        with open(self.file_path, 'w') as yaml_file:
            self.yaml.dump(self.settings, yaml_file)

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()

    def reload(self):
        self.read_settings()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.a0_para()
        self.a1_initialize()
        self.a2_status_bar()
        self.a3_docks()
        self.a4_menubar()
        self.a5_toolbar()
        self.a9_setting()

    def b1_window(self):
        return

    def a0_para(self):
        # ================初始化变量================
        self.screen_icon = icon('ei.screen')
        self.setWindowIcon(self.screen_icon)
        self.default_palette = QGuiApplication.palette()
        self.setAcceptDrops(True)

        self.setWindowTitle("漫画翻译工具")
        self.resize(1200, 800)

        # 创建 QGraphicsScene 和 QGraphicsView 对象
        self.graphics_scene = QGraphicsScene(self)  # 图形场景对象
        self.graphics_scene.selectionChanged.connect(self.set_current_text_item)
        self.graphics_view = QGraphicsView(self)  # 图形视图对象
        # 设置渲染、优化和视口更新模式
        # 设置渲染抗锯齿
        self.graphics_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        # 设置优化标志以便不为抗锯齿调整
        self.graphics_view.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing, True)
        # 设置优化标志以便不保存画家状态
        self.graphics_view.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontSavePainterState, True)
        # 设置视口更新模式为完整视口更新
        self.graphics_view.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        # 设置渲染提示为平滑图像变换，以提高图像的显示质量
        self.graphics_view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

    def a1_initialize(self):
        # ================文本项================
        self.selected_text_item = None
        self.current_text_item = None
        # ================图片列表================
        self.image_folder = None
        self.image_list = []
        self.image_file = None
        self.image_item = None
        self.image = QImage()
        self.pixmap_item = QGraphicsPixmapItem()
        self.image_index = -1
        self.filtered_image_index = -1
        self.view_mode = 0
        self.screen_scaling_factor = self.get_screen_scaling_factor()
        self.screen_scaling_factor_reciprocal = 1 / self.screen_scaling_factor
        # ================最近文件夹================
        self.recent_folders = []
        # ================设置================
        self.program_settings = QSettings("YourOrganization", "iManhua")  # 根据需要修改组织和应用名

    def a2_status_bar(self):
        # ================状态栏================
        self.status_bar = QStatusBar()
        # 设置状态栏，类似布局设置
        self.setStatusBar(self.status_bar)

    def a3_docks(self):
        # ================缩略图列表================
        self.thumbnails_widget = QListWidget(self)
        self.thumbnails_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)  # 设置自定义右键菜单
        self.thumbnails_widget.customContextMenuRequested.connect(self.show_image_list_context_menu)  # 连接自定义右键菜单信号与函数
        self.thumbnails_widget.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)  # 设置单选模式
        self.thumbnails_widget.setViewMode(QListView.ViewMode.IconMode)  # 设置图标模式
        self.thumbnails_widget.setFlow(QListView.Flow.TopToBottom)  # 设置从上到下排列
        self.thumbnails_widget.setResizeMode(QListView.ResizeMode.Adjust)  # 设置自动调整大小
        self.thumbnails_widget.setWrapping(False)  # 关闭自动换行
        self.thumbnails_widget.setWordWrap(True)  # 开启单词换行
        self.thumbnails_widget.setIconSize(QSize(240, 240))  # 设置图标大小
        self.thumbnails_widget.setSpacing(5)  # 设置间距
        self.thumbnails_widget.itemSelectionChanged.connect(self.select_image_from_list)  # 连接图标选择信号与函数

        self.nav_tab = QTabWidget()  # 创建选项卡控件
        self.nav_tab.addTab(self.thumbnails_widget, self.tr('Thumbnails'))  # 添加缩略图列表到选项卡

        self.case_sensitive_button = QToolButton()  # 创建区分大小写按钮
        self.case_sensitive_button.setIcon(icon('msc.case-sensitive'))  # 设置图标
        self.case_sensitive_button.setCheckable(True)  # 设置可选中
        self.case_sensitive_button.setText(self.tr('Case Sensitive'))  # 设置文本
        self.case_sensitive_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)  # 设置仅显示图标

        self.whole_word_button = QToolButton()  # 创建全词匹配按钮
        self.whole_word_button.setIcon(icon('msc.whole-word'))  # 设置图标
        self.whole_word_button.setCheckable(True)  # 设置可选中
        self.whole_word_button.setText(self.tr('Whole Word'))  # 设置文本
        self.whole_word_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)  # 设置仅显示图标

        self.regex_button = QToolButton()  # 创建正则表达式按钮
        self.regex_button.setIcon(icon('mdi.regex'))  # 设置图标
        self.regex_button.setCheckable(True)  # 设置可选中
        self.regex_button.setText(self.tr('Use Regex'))  # 设置文本
        self.regex_button.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)  # 设置仅显示图标

        # 连接按钮的点击事件与搜索结果的刷新
        self.case_sensitive_button.clicked.connect(self.refresh_search_results)
        self.whole_word_button.clicked.connect(self.refresh_search_results)
        self.regex_button.clicked.connect(self.refresh_search_results)

        self.hb_search_bar = QHBoxLayout()  # 创建水平布局，用于将三个按钮放在一行
        self.hb_search_bar.setContentsMargins(0, 0, 0, 0)
        self.hb_search_bar.addStretch()
        self.hb_search_bar.addWidget(self.case_sensitive_button)
        self.hb_search_bar.addWidget(self.whole_word_button)
        self.hb_search_bar.addWidget(self.regex_button)

        self.search_bar = QLineEdit()  # 创建搜索栏
        self.search_bar.setPlaceholderText(self.tr('Search'))  # 设置占位符文本
        self.search_bar.textChanged.connect(self.filter_image_list)  # 连接文本改变信号与函数
        self.search_bar.setLayout(self.hb_search_bar)  # 将按钮添加到 QLineEdit 的右侧

        self.vb_search_nav = QVBoxLayout()  # 创建垂直布局，用于将搜索框和图片列表放在一列
        self.vb_search_nav.addWidget(self.search_bar)
        self.vb_search_nav.addWidget(self.nav_tab)

        self.pics_widget = QWidget()  # 创建 QWidget，用于容纳搜索框和图片列表
        self.pics_widget.setLayout(self.vb_search_nav)

        self.pics_dock = QDockWidget(self.tr('Image List'), self)  # 创建 QDockWidget，用于显示图片列表
        self.pics_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.pics_dock.setWidget(self.pics_widget)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.pics_dock)

        # 创建字体选择器
        self.font_name_label = QLabel(self.tr('Font'))
        self.font_combo = QFontComboBox(self)
        self.font_combo.setFontFilters(QFontComboBox.FontFilter.AllFonts)
        self.font_combo.currentFontChanged.connect(self.update_text_item_font)

        # 创建字体大小选择器
        self.font_size_label = QLabel(self.tr('Font Size'))
        self.font_size_spinbox = QSpinBox(self)
        self.font_size_spinbox.setRange(6, 100)
        self.font_size_spinbox.setValue(18)
        self.font_size_spinbox.valueChanged.connect(self.update_text_item_font_size)

        # 创建颜色选择器
        color_label = QLabel(self.tr('Color'))
        self.color_button = QPushButton(self.tr('Change Color'), self)
        self.color_button.clicked.connect(self.pick_color)
        self.color_picker = QColorDialog(self)
        self.color_picker.setOption(QColorDialog.ColorDialogOption.ShowAlphaChannel)

        # 在 create_text_tool 方法中添加透明度滑块
        self.opacity_slider = QSlider(Qt.Orientation.Horizontal, self)
        self.opacity_slider.setRange(0, 255)
        self.opacity_slider.setValue(255)
        self.opacity_slider.valueChanged.connect(self.update_text_item_opacity)

        # 创建文本项的 X 和 Y 坐标选择器
        position_label = QLabel(self.tr('Position'))
        self.x_spinbox = QSpinBox(self)
        self.x_spinbox.setRange(0, int(self.graphics_scene.width()))
        self.y_spinbox = QSpinBox(self)
        self.y_spinbox.setRange(0, int(self.graphics_scene.height()))
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
        self.hb_font_color_alpha.addWidget(QLabel(self.tr('Transparency')))
        self.hb_font_color_alpha.addWidget(self.opacity_slider)

        hb_text_position = QHBoxLayout()
        hb_text_position.addWidget(position_label)
        hb_text_position.addWidget(self.x_spinbox)
        hb_text_position.addWidget(self.y_spinbox)

        self.vb_text_tool = QVBoxLayout()
        self.vb_text_tool.addLayout(hb_font_name_size)
        self.vb_text_tool.addLayout(self.hb_font_color_alpha)
        self.vb_text_tool.addLayout(hb_text_position)
        self.vb_text_tool.addWidget(QLabel(self.tr('Text Items')))
        self.vb_text_tool.addWidget(self.text_items_list)

        self.text_tool = QWidget()
        self.text_tool.setLayout(self.vb_text_tool)

        self.layer_tool = QWidget()  # 创建图层工具
        self.layer_tool.setMinimumWidth(200)  # 设置最小宽度

        self.step_tool = QWidget()  # 创建步骤工具

        self.text_dock = QDockWidget(self.tr('Text'), self)  # 创建 QDockWidget，用于显示文本工具
        self.text_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.text_dock.setWidget(self.text_tool)
        self.text_dock.setMinimumWidth(200)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.text_dock)

        self.layer_dock = QDockWidget(self.tr('Layer'), self)  # 创建 QDockWidget，用于显示图层工具
        self.layer_dock.setAllowedAreas(Qt.DockWidgetArea.LeftDockWidgetArea | Qt.DockWidgetArea.RightDockWidgetArea)
        self.layer_dock.setWidget(self.layer_tool)
        self.layer_dock.setMinimumWidth(200)
        self.addDockWidget(Qt.DockWidgetArea.RightDockWidgetArea, self.layer_dock)

        self.step_dock = QDockWidget(self.tr('Step'), self)
        self.step_dock.setAllowedAreas(Qt.DockWidgetArea.BottomDockWidgetArea | Qt.DockWidgetArea.TopDockWidgetArea)
        self.step_dock.setWidget(self.step_tool)
        self.step_dock.setMinimumWidth(200)
        self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea, self.step_dock)

    def a4_menubar(self):
        # 文件菜单
        self.file_menu = self.menuBar().addMenu(self.tr('File'))

        # 添加打开文件夹操作
        self.open_folder_action = QAction(self.tr('Open Folder'), self)
        self.open_folder_action.setIcon(icon('ei.folder'))
        self.open_folder_action.setShortcut(QKeySequence("Ctrl+O"))
        self.open_folder_action.triggered.connect(self.open_folder_by_dialog)
        self.file_menu.addAction(self.open_folder_action)

        # 添加保存图片操作
        self.save_image_action = QAction(self.tr('Save Image'), self)
        self.save_image_action.setIcon(icon('ri.image-edit-fill'))
        self.save_image_action.setShortcut(QKeySequence.StandardKey.Save)
        self.save_image_action.triggered.connect(self.save_image)
        self.file_menu.addAction(self.save_image_action)

        self.file_menu.addSeparator()

        # 添加最近打开文件夹菜单项
        self.recent_folders_menu = self.file_menu.addMenu(self.tr('Recent Folders'))
        self.update_recent_folders_menu()

        # 显示菜单
        self.view_menu = self.menuBar().addMenu(self.tr('View'))

        # 添加视图菜单选项
        self.view_menu.addAction(self.text_dock.toggleViewAction())
        self.view_menu.addAction(self.layer_dock.toggleViewAction())
        self.view_menu.addAction(self.pics_dock.toggleViewAction())
        self.view_menu.addSeparator()

        # 添加缩放选项
        self.zoom_in_action = QAction(self.tr('Zoom In'), self)
        self.zoom_in_action.setIcon(icon('ei.zoom-in'))
        self.zoom_in_action.setShortcut(QKeySequence.StandardKey.ZoomIn)
        self.zoom_in_action.triggered.connect(self.zoom_in)
        self.view_menu.addAction(self.zoom_in_action)

        self.zoom_out_action = QAction(self.tr('Zoom Out'), self)
        self.zoom_out_action.setIcon(icon('ei.zoom-out'))
        self.zoom_out_action.setShortcut(QKeySequence.StandardKey.ZoomOut)
        self.zoom_out_action.triggered.connect(self.zoom_out)
        self.view_menu.addAction(self.zoom_out_action)

        self.view_menu.addSeparator()

        # 添加自适应屏幕选项
        self.fit_to_screen_action = QAction(self.tr('Fit to Screen'), self)
        self.fit_to_screen_action.setIcon(icon('mdi6.fit-to-screen-outline'))
        self.fit_to_screen_action.setShortcut(QKeySequence("Ctrl+F"))
        self.fit_to_screen_action.setCheckable(True)  # 将选项设置为可选
        self.fit_to_screen_action.toggled.connect(self.fit_to_view_toggled)
        self.view_menu.addAction(self.fit_to_screen_action)

        # 添加自适应宽度选项
        self.fit_to_width_action = QAction(self.tr('Fit to Width'), self)
        self.fit_to_width_action.setIcon(icon('ei.resize-horizontal'))
        self.fit_to_width_action.setShortcut(QKeySequence("Ctrl+W"))
        self.fit_to_width_action.setCheckable(True)  # 将选项设置为可选
        self.fit_to_width_action.toggled.connect(self.fit_to_view_toggled)
        self.view_menu.addAction(self.fit_to_width_action)

        # 添加自适应高度选项
        self.fit_to_height_action = QAction(self.tr('Fit to Height'), self)
        self.fit_to_height_action.setIcon(icon('ei.resize-vertical'))
        self.fit_to_height_action.setShortcut(QKeySequence("Ctrl+H"))
        self.fit_to_height_action.setCheckable(True)  # 设置选项为可选
        self.fit_to_height_action.toggled.connect(self.fit_to_view_toggled)
        self.view_menu.addAction(self.fit_to_height_action)

        # 添加重置缩放选项
        self.reset_zoom_action = QAction(self.tr('Reset Zoom'), self)
        self.reset_zoom_action.setIcon(icon('mdi6.backup-restore'))
        self.reset_zoom_action.setShortcut(QKeySequence("Ctrl+0"))
        self.reset_zoom_action.triggered.connect(self.reset_zoom)
        self.view_menu.addAction(self.reset_zoom_action)

        self.view_menu.addSeparator()

        # 添加显示选项
        self.display_modes = [(self.tr('Show Thumbnails'), 0),
                              (self.tr('Show Filenames'), 1),
                              (self.tr('Show Both'), 2)]
        self.display_mode_group = QActionGroup(self)
        for display_mode in self.display_modes:
            action = QAction(display_mode[0], self, checkable=True)
            action.triggered.connect(lambda _, mode=display_mode[1]: self.set_display_mode(mode))
            self.view_menu.addAction(action)
            self.display_mode_group.addAction(action)

        self.display_mode_group.actions()[2].setChecked(True)  # 默认选中 Show Both 选项

        # 编辑菜单
        self.edit_menu = self.menuBar().addMenu(self.tr('Edit'))

        self.add_text_action = QAction(self.tr('Add Text'), self)  # 添加“添加文本”动作
        self.add_text_action.setIcon(icon('ri.chat-new-line'))  # 设置图标
        self.add_text_action.setShortcut(QKeySequence("Ctrl+T"))  # 设置快捷键
        self.add_text_action.triggered.connect(self.add_text)  # 设置响应事件
        self.edit_menu.addAction(self.add_text_action)  # 将动作添加到“编辑”菜单

        self.delete_text_action = QAction(self.tr('Delete Text'), self)  # 添加“删除文本”动作
        self.delete_text_action.setIcon(icon('mdi6.delete-forever-outline'))  # 设置图标
        self.delete_text_action.setShortcut(QKeySequence("Ctrl+D"))  # 设置快捷键
        self.delete_text_action.triggered.connect(self.delete_text)  # 设置响应事件
        self.edit_menu.addAction(self.delete_text_action)  # 将动作添加到“编辑”菜单

        self.clear_all_text_action = QAction(self.tr('Clear All Text'), self)  # 添加“清空所有文本”动作
        self.clear_all_text_action.setIcon(icon('mdi6.delete-sweep-outline'))  # 设置图标
        self.clear_all_text_action.setShortcut(QKeySequence("Ctrl+Shift+D"))  # 设置快捷键
        self.clear_all_text_action.triggered.connect(self.clear_all_text)  # 设置响应事件
        self.edit_menu.addAction(self.clear_all_text_action)  # 将动作添加到“编辑”菜单

        # 导航菜单
        self.nav_menu = self.menuBar().addMenu(self.tr('Navigate'))

        # 添加上一张图片操作
        self.prev_image_action = QAction(self.tr('Previous Image'), self)
        self.prev_image_action.setIcon(icon('ei.arrow-left'))
        self.prev_image_action.setShortcut(QKeySequence("Ctrl+Left"))
        self.prev_image_action.triggered.connect(lambda: self.change_image(-1))
        self.nav_menu.addAction(self.prev_image_action)

        # 添加下一张图片操作
        self.next_image_action = QAction(self.tr('Next Image'), self)
        self.next_image_action.setIcon(icon('ei.arrow-right'))
        self.next_image_action.setShortcut(QKeySequence("Ctrl+Right"))
        self.next_image_action.triggered.connect(lambda: self.change_image(1))
        self.nav_menu.addAction(self.next_image_action)

        # 添加第一张图片操作
        self.first_image_action = QAction(self.tr('First Image'), self)
        self.first_image_action.setIcon(icon('ei.step-backward'))
        self.first_image_action.setShortcut(QKeySequence("Ctrl+Home"))
        self.first_image_action.triggered.connect(lambda: self.change_image("first"))
        self.nav_menu.addAction(self.first_image_action)

        # 添加最后一张图片操作
        self.last_image_action = QAction(self.tr('Last Image'), self)
        self.last_image_action.setIcon(icon('ei.step-forward'))
        self.last_image_action.setShortcut(QKeySequence("Ctrl+End"))
        self.last_image_action.triggered.connect(lambda: self.change_image("last"))
        self.nav_menu.addAction(self.last_image_action)

        # 帮助菜单
        self.help_menu = self.menuBar().addMenu(self.tr('Help'))

        self.about_action = QAction(self.tr('About iManhua'), self)
        self.about_action.triggered.connect(self.show_about_dialog)
        self.help_menu.addAction(self.about_action)

        self.about_qt_action = QAction(self.tr('About Qt'), self)
        self.about_qt_action.triggered.connect(QApplication.instance().aboutQt)
        self.help_menu.addAction(self.about_qt_action)

        self.help_document_action = QAction(self.tr('iManhua Help'), self)
        self.help_document_action.triggered.connect(self.show_help_document)
        self.help_menu.addAction(self.help_document_action)

        self.feedback_action = QAction(self.tr('Bug Report'), self)
        self.feedback_action.triggered.connect(self.show_feedback_dialog)
        self.help_menu.addAction(self.feedback_action)

        self.update_action = QAction(self.tr('Update Online'), self)
        self.update_action.triggered.connect(self.check_for_updates)
        self.help_menu.addAction(self.update_action)

    def a5_toolbar(self):

        # 添加顶部工具栏
        self.tool_bar = QToolBar(self.tr('Toolbar'), self)
        self.tool_bar.setIconSize(QSize(24, 24))
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.tool_bar)
        self.tool_bar.setMovable(False)
        self.tool_bar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.tool_bar.addAction(self.open_folder_action)
        self.tool_bar.addAction(self.save_image_action)
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(self.zoom_in_action)
        self.tool_bar.addAction(self.zoom_out_action)
        self.tool_bar.addAction(self.fit_to_screen_action)
        self.tool_bar.addAction(self.fit_to_width_action)
        self.tool_bar.addAction(self.fit_to_height_action)
        self.tool_bar.addAction(self.reset_zoom_action)
        self.tool_bar.addSeparator()
        self.tool_bar.addAction(self.first_image_action)
        self.tool_bar.addAction(self.prev_image_action)
        self.tool_bar.addAction(self.next_image_action)
        self.tool_bar.addAction(self.last_image_action)

        # 添加缩放百分比输入框
        self.scale_percentage_edit = QLineEdit(self)
        self.scale_percentage_edit.setFixedWidth(60)
        self.scale_percentage_edit.setValidator(QDoubleValidator(1, 1000, 2))
        self.scale_percentage_edit.setText('100.00')
        self.scale_percentage_edit.editingFinished.connect(self.scale_by_percentage)
        self.tool_bar.addWidget(self.scale_percentage_edit)
        self.tool_bar.addWidget(QLabel('%'))

    def a9_setting(self):
        # 读取上一次打开的文件夹、窗口位置和状态
        last_opened_folder = self.program_settings.value("last_opened_folder", "")
        geometry = self.program_settings.value("window_geometry")
        state = self.program_settings.value("window_state")
        # 如果上一次打开的文件夹存在，则打开它
        if last_opened_folder and os.path.exists(last_opened_folder) and os.path.isdir(last_opened_folder):
            self.open_folder_by_path(last_opened_folder)
        # 如果上一次有记录窗口位置，则恢复窗口位置
        if geometry is not None:
            self.restoreGeometry(geometry)
        # 如果上一次有记录窗口状态，则恢复窗口状态
        if state is not None:
            self.restoreState(self.program_settings.value("window_state"))

        # 将 QGraphicsView 设置为中心窗口部件
        self.setCentralWidget(self.graphics_view)

        # 显示窗口
        self.show()

    def open_image_by_path(self, image_file):
        # 需要路径存在
        image_file = Path(image_file)
        if image_file.exists():
            self.image_file = image_file
            self.image_file_size = os.path.getsize(self.image_file)
            self.image_index = self.image_list.index(self.image_file)

            # ================清除之前的图像和所有文本框================
            if self.image_item:
                self.graphics_scene.removeItem(self.image_item)  # 移除之前的图片项

                # 清除之前的所有文本框
                for i in range(self.text_items_list.count()):
                    item = self.text_items_list.item(i)
                    text_item = item.data(Qt.ItemDataRole.UserRole)
                    self.graphics_scene.removeItem(text_item)

            # ================显示新图片================
            self.pixmap = QPixmap(self.image_file.as_posix())
            self.image_size = self.pixmap.size()
            self.image_item = self.graphics_scene.addPixmap(self.pixmap)
            # 将视图大小设置为 pixmap 的大小，并将图像放入视图中
            self.graphics_view.setSceneRect(self.pixmap.rect().toRectF())
            self.graphics_view.setScene(self.graphics_scene)

            # 设置视图渲染选项
            self.graphics_view.setRenderHint(QPainter.RenderHint.Antialiasing)
            self.graphics_view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            self.graphics_view.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontAdjustForAntialiasing, True)
            self.graphics_view.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
            self.graphics_view.setOptimizationFlag(QGraphicsView.OptimizationFlag.DontSavePainterState, True)
            self.graphics_view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
            self.graphics_view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)

            # 设置视图转换和缩放选项
            self.graphics_view.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
            self.graphics_view.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
            self.graphics_view.setBackgroundBrush(QBrush(Qt.GlobalColor.lightGray))
            self.graphics_view.setTransform(
                QTransform().scale(self.screen_scaling_factor_reciprocal, self.screen_scaling_factor_reciprocal))

            # 更新缩放比例
            self.update_scale_percentage()

            # 如果自适应屏幕选项已经选中，则按照自适应屏幕缩放图片
            if self.fit_to_screen_action.isChecked():
                self.fit_to_view("screen")
            # 如果自适应宽度选项已经选中，则按照自适应宽度缩放图片
            elif self.fit_to_width_action.isChecked():
                self.fit_to_view("width")
            # 如果自适应高度选项已经选中，则按照自适应宽度缩放图片
            elif self.fit_to_height_action.isChecked():
                self.fit_to_view("height")

            # 将当前图片项设为选中状态，更新状态栏信息
            self.thumbnails_widget.setCurrentRow(self.image_index)
            index_str = f'{self.image_index + 1}/{len(self.image_list)}'
            meta_str = f'宽度: {self.image_size.width()} 高度: {self.image_size.height()} | 文件大小: {self.image_file_size} bytes'
            status_text = f'{index_str} | 图片名: {self.image_file.name} | {meta_str}'
            self.status_bar.showMessage(status_text)

    def open_folder_by_path(self, folder_path):
        # 打开上次关闭程序时用到的文件夹
        # 打开最近的文件夹
        # 打开文件夹

        # 判断文件夹路径是否存在
        if os.path.exists(folder_path):
            # 获取所有图片文件的路径
            image_list = get_files_custom(folder_path, 'pic', True)
            if image_list:
                self.image_folder = folder_path
                self.image_list = image_list
                self.filtered_image_list = self.image_list
                self.image_index = 0
                self.filtered_image_index = 0
                self.image_file = self.image_list[self.image_index]

                # ================更新导航栏中的图片列表================
                self.thumbnails_widget.clear()
                for image_file in self.image_list:
                    # 将image的basename作为文本添加到thumbnail_item中
                    thumbnail_item = QListWidgetItem(image_file.name)
                    # 将image的图标设置为缩略图
                    thumbnail_item.setIcon(QIcon(image_file.as_posix()))
                    # 文本居中显示
                    thumbnail_item.setTextAlignment(Qt.AlignmentFlag.AlignHCenter)
                    thumbnail_item.setData(Qt.ItemDataRole.UserRole, image_file)
                    # 如果image文件存在，则将thumbnail_item添加到thumbnails_widget中
                    if image_file.exists():
                        self.thumbnails_widget.addItem(thumbnail_item)

                self.open_image_by_path(self.image_file)

                # 设置主窗口标题为 "漫画翻译工具 - 文件夹路径"
                self.setWindowTitle(f"漫画翻译工具 - {self.image_folder}")
                # 将该文件夹添加到最近使用文件夹列表
                self.add_recent_folder(self.image_folder)

    def open_folder_by_dialog(self):
        image_folder = QFileDialog.getExistingDirectory(self, self.tr('Open Folder'))
        if image_folder:
            self.image_folder = image_folder
            self.open_folder_by_path(self.image_folder)

    def update_recent_folders_menu(self):
        self.recent_folders_menu.clear()
        recent_folders = self.program_settings.value("recent_folders", [])
        for folder in recent_folders:
            action = QAction(folder, self)
            action.triggered.connect(lambda checked, p=folder: self.open_folder_by_path(p))
            self.recent_folders_menu.addAction(action)

    def add_recent_folder(self, folder_path):
        recent_folders = self.program_settings.value("recent_folders", [])
        if folder_path in recent_folders:
            recent_folders.remove(folder_path)
        recent_folders.insert(0, folder_path)
        recent_folders = recent_folders[:10]  # 保留最多10个最近文件夹

        self.program_settings.setValue("recent_folders", recent_folders)
        self.update_recent_folders_menu()

    def set_display_mode(self, mode):
        self.view_mode = mode
        self.thumbnails_widget.setUpdatesEnabled(False)
        for index in range(self.thumbnails_widget.count()):
            item = self.thumbnails_widget.item(index)
            data = item.data(Qt.ItemDataRole.UserRole)
            if self.view_mode == 0:  # Show thumbnails only
                item.setIcon(QIcon(data.as_posix()))
                item.setText('')
                self.thumbnails_widget.setWordWrap(False)
            elif self.view_mode == 1:  # Show filenames only
                item.setIcon(QIcon())  # Clear the icon
                item.setText(data.name)
                self.thumbnails_widget.setWordWrap(False)  # Make sure filenames don't wrap
            elif self.view_mode == 2:  # Show both thumbnails and filenames
                item.setIcon(QIcon(data.as_posix()))
                item.setText(data.name)
                self.thumbnails_widget.setWordWrap(True)

        thumbnail_size = QSize(240, 240)  # Set the thumbnail size to 240x240
        self.thumbnails_widget.setIconSize(thumbnail_size)  # Set the icon size

        if self.view_mode == 1:  # Show filenames only
            self.thumbnails_widget.setGridSize(QSize(-1, -1))  # Use default size for grid
        else:
            # Set grid size for thumbnails and both modes
            self.thumbnails_widget.setGridSize(
                QSize(thumbnail_size.width() + 30, -1))  # Add extra width for file names and spacing

        self.thumbnails_widget.setUpdatesEnabled(True)

    def select_image_from_list(self):
        # 通过键鼠点击获取的数据是真实序数image_index
        active_list_widget = self.nav_tab.currentWidget()
        selected_items = active_list_widget.selectedItems()
        if not selected_items:
            return
        current_item = selected_items[0]
        image_index = active_list_widget.row(current_item)
        if image_index != self.image_index:
            self.image_index = image_index
            image_file = current_item.data(Qt.ItemDataRole.UserRole)
            self.open_image_by_path(image_file)

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

    def open_image_in_ps(self, file_path):
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
        item = self.thumbnails_widget.itemAt(point)
        if item:
            context_menu = QMenu(self)
            open_file_action = QAction(self.tr('Open in Explorer'), self)
            open_file_action.triggered.connect(
                lambda: self.open_file_in_explorer(item.data(Qt.ItemDataRole.UserRole)))
            open_image_action = QAction(self.tr('Open in Preview'), self)
            open_image_action.triggered.connect(
                lambda: self.open_image_in_viewer(item.data(Qt.ItemDataRole.UserRole)))
            context_menu.addAction(open_file_action)
            context_menu.addAction(open_image_action)

            # 添加一个打开方式子菜单
            open_with_menu = context_menu.addMenu(self.tr('Open with'))
            open_with_ps = QAction(self.tr('Photoshop'), self)
            open_with_menu.addAction(open_with_ps)

            # 添加拷贝图片路径、拷贝图片名的选项
            copy_image_path = QAction(self.tr('Copy Image Path'), self)
            copy_image_name = QAction(self.tr('Copy Image Name'), self)

            context_menu.addAction(copy_image_path)
            context_menu.addAction(copy_image_name)

            # 连接触发器
            open_with_ps.triggered.connect(lambda: self.open_image_in_ps(item.data(Qt.ItemDataRole.UserRole)))
            copy_image_path.triggered.connect(lambda: self.copy_to_clipboard(item.data(Qt.ItemDataRole.UserRole)))
            copy_image_name.triggered.connect(lambda: self.copy_to_clipboard(item.text()))
            context_menu.exec(self.thumbnails_widget.mapToGlobal(point))

    def refresh_search_results(self):
        # 用于三个筛选按钮
        search_text = self.search_bar.text()
        self.filter_image_list(search_text)

    def filter_image_list(self, search_text):
        # 用于搜索框内容更新
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

        # ================筛选列表更新================
        self.filtered_image_list = []
        for image_file in self.image_list:
            match = regex.search(image_file.name)
            if match:
                self.filtered_image_list.append(image_file)

        # ================缩略图列表更新================
        for index in range(self.thumbnails_widget.count()):
            item = self.thumbnails_widget.item(index)
            item_text = item.text()
            match = regex.search(item_text)
            if match:
                item.setHidden(False)
            else:
                item.setHidden(True)

    def save_image(self):
        file_name, _ = QFileDialog.getSaveFileName(self, self.tr('Save Image'), "", "Images (*.png *.xpm *.jpg)")

        if file_name:
            image = QImage(self.graphics_scene.sceneRect().size().toSize(), QImage.Format.Format_ARGB32)
            image.fill(Qt.GlobalColor.transparent)

            painter = QPainter(image)
            self.graphics_scene.render(painter)
            painter.end()

            image.save(file_name)

    def change_image(self, step):
        current_image_path = self.image_list[self.image_index]
        # 检查当前图片路径是否在过滤后的图片列表中
        if current_image_path not in self.filtered_image_list:
            return
        current_filtered_index = self.filtered_image_list.index(current_image_path)

        if step == "first":
            new_filtered_index = 0
        elif step == "last":
            new_filtered_index = len(self.filtered_image_list) - 1
        else:
            new_filtered_index = current_filtered_index + step

        if 0 <= new_filtered_index < len(self.filtered_image_list):
            new_image_path = self.filtered_image_list[new_filtered_index]
            self.open_image_by_path(new_image_path)

    def get_screen_scaling_factor(self):
        screen = QApplication.primaryScreen()
        if sys.platform == 'darwin':  # 如果是 MacOS 系统
            return screen.devicePixelRatio()
        else:
            return 1

    def zoom(self, scale_factor):
        self.graphics_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        current_transform = self.graphics_view.transform()
        current_scale = current_transform.m11()
        new_scale = current_scale * scale_factor

        if 0.01 <= new_scale <= 10:
            current_transform.scale(scale_factor, scale_factor)
            self.graphics_view.setTransform(current_transform)
            self.update_scale_percentage()

    def zoom_in(self):
        self.zoom(1.2)

    def zoom_out(self):
        self.zoom(1 / 1.2)

    def fit_to_view(self, mode):
        if self.image_item:
            if mode == "screen":
                self.graphics_view.fitInView(self.image_item, Qt.AspectRatioMode.KeepAspectRatio)
            elif mode == "width":
                view_width = self.graphics_view.viewport().width()
                pixmap_width = self.image_item.pixmap().width()
                scale_factor = view_width / pixmap_width
                self.graphics_view.setTransform(QTransform().scale(scale_factor, scale_factor))
            elif mode == "height":
                view_height = self.graphics_view.viewport().height()
                pixmap_height = self.image_item.pixmap().height()
                scale_factor = view_height / pixmap_height
                self.graphics_view.setTransform(QTransform().scale(scale_factor, scale_factor))
            self.graphics_view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            self.update_scale_percentage()

    def fit_to_view_toggled(self, checked):
        sender = self.sender()
        if sender == self.fit_to_screen_action:
            mode = 'screen'
            if checked:
                self.fit_to_width_action.setChecked(False)
                self.fit_to_height_action.setChecked(False)
        elif sender == self.fit_to_width_action:
            mode = 'width'
            if checked:
                self.fit_to_screen_action.setChecked(False)
                self.fit_to_height_action.setChecked(False)
        else:  # if sender == self.fit_to_height_action
            mode = 'height'
            if checked:
                self.fit_to_screen_action.setChecked(False)
                self.fit_to_width_action.setChecked(False)
        self.fit_to_view(mode)

    def reset_zoom(self):
        self.fit_to_screen_action.setChecked(False)
        self.fit_to_width_action.setChecked(False)
        self.fit_to_height_action.setChecked(False)
        # 使用 setTransform 代替 resetMatrix 并应用缩放因子
        self.graphics_view.setTransform(
            QTransform().scale(self.screen_scaling_factor_reciprocal, self.screen_scaling_factor_reciprocal))
        self.update_scale_percentage()

    def update_scale_percentage(self):
        current_scale = round(self.graphics_view.transform().m11() * 100, 2)
        self.scale_percentage_edit.setText(str(current_scale))

    def scale_by_percentage(self):
        scale_percentage = float(self.scale_percentage_edit.text())
        target_scale = scale_percentage / 100
        current_scale = self.graphics_view.transform().m11()

        scale_factor = target_scale / current_scale
        self.graphics_view.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.graphics_view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.graphics_view.scale(scale_factor, scale_factor)

    def update_tool_box(self, text_item):
        self.x_spinbox.setMaximum(int(self.graphics_scene.width()))
        self.y_spinbox.setMaximum(int(self.graphics_scene.height()))
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
        selected_items = self.graphics_scene.selectedItems()
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
        text_item.setFont(QFont("Arial", 30))
        text_item.setDefaultTextColor(Qt.GlobalColor.black)
        text_item.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)

        cursor = QTextCursor(text_item.document())
        cursor.insertText(f"{self.tr('Translation Text')}")

        center_pos = self.graphics_view.mapToScene(self.graphics_view.viewport().rect().center())
        text_item.setPos(center_pos)
        self.graphics_scene.addItem(text_item)

        list_item = QListWidgetItem(f"{self.tr('Text Item')} {self.text_items_list.count() + 1}")
        self.text_items_list.addItem(list_item)
        list_item.setData(Qt.ItemDataRole.UserRole, text_item)

    def delete_text(self):
        if self.current_text_item:
            # 从场景删除文本
            self.graphics_scene.removeItem(self.current_text_item)

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
        for item in self.graphics_scene.items():
            if isinstance(item, QGraphicsTextItem):
                self.graphics_scene.removeItem(item)
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

    def show_about_dialog(self):
        about_dialog = QDialog(self)
        about_dialog.setWindowTitle("关于漫画翻译工具")

        app_name_label = QLabel("漫画翻译工具")
        app_name_label.setFont(QFont("Arial", 20, QFont.Bold))

        version_label = QLabel("版本: 1.0.0")
        libraries_label = QLabel("使用的库：PyQt, QImage, QSettings")
        license_label = QLabel("许可证: MIT License")

        main_layout = QVBoxLayout()
        main_layout.addWidget(app_name_label)
        main_layout.addWidget(version_label)
        main_layout.addWidget(libraries_label)
        main_layout.addWidget(license_label)
        about_dialog.setLayout(main_layout)
        about_dialog.exec_()

    def show_help_document(self):
        # 在此处显示帮助文档
        pass

    def show_feedback_dialog(self):
        recipient_email = "your_email@example.com"  # 替换为您的电子邮件地址
        subject = "Bug Report - 漫画翻译工具"
        body = "请在此处详细描述您遇到的问题：\n\n\n\n软件版本：1.0.0"
        mailto_url = f"mailto:{recipient_email}?subject={subject}&body={body}"

        try:
            webbrowser.open(mailto_url)
        except webbrowser.Error as e:
            QMessageBox.warning(self, "错误", f"无法打开邮件客户端：{e}")

    def check_for_updates(self):
        # 在此处实现在线更新软件的功能
        pass

    def closeEvent(self, event):
        # 如果有打开图片的文件夹，将其保存到程序设置中
        if self.image_folder:
            self.program_settings.setValue("last_opened_folder", self.image_folder)
        else:
            self.program_settings.setValue("last_opened_folder", "")
        # 保存窗口的几何和状态信息到程序设置中
        self.program_settings.setValue("window_geometry", self.saveGeometry())
        self.program_settings.setValue("window_state", self.saveState())
        event.accept()


@logger.catch
def main_qt():
    window = MainWindow()
    sys.exit(appgui.exec())


def wrap_strings_with_tr():
    content = read_txt(py_path)

    # 匹配从 QWidget 或 QMainWindow 继承的类
    class_pattern = r'class\s+\w+\s*\((?:\s*\w+\s*,\s*)*(QWidget|QMainWindow)(?:\s*,\s*\w+)*\s*\)\s*:'
    class_matches = re.finditer(class_pattern, content)

    # 在这些类中查找没有包裹在 self.tr() 中的字符串
    string_pattern = r'(?<!self\.tr\()\s*(".*?"|\'.*?\')(?!\s*\.(?:format|replace)|\s*\%|settings\.value)(?!\s*(?:setIcon|icon|setShortcut|QKeySequence|QSettings)\s*\()'

    for class_match in class_matches:
        class_start = class_match.start()
        next_match = re.search(r'class\s+\w+\s*\(', content[class_start + 1:])
        if next_match:
            class_end = next_match.start()
        else:
            class_end = len(content)

        class_content = content[class_start:class_end]

        matches = re.finditer(string_pattern, class_content)
        new_class_content = class_content
        for match in reversed(list(matches)):
            # 检查是否需要替换文本
            str_value = match.group(1)[1:-1]

            # 获取字符串所在的整行
            line_start = class_content.rfind('\n', 0, match.start()) + 1
            line_end = class_content.find('\n', match.end())
            line = class_content[line_start:line_end]

            if is_decimal_or_comma(str_value) or str_value.endswith('%'):
                continue

            # 检查行中是否包含我们不需要替换的关键字
            if any(keyword in line for keyword in special_keywords):
                continue

            start = match.start(1)
            end = match.end(1)
            logger.info(f'正在修改: {match.group(1)}')
            # 使用单引号包裹字符串
            new_class_content = new_class_content[
                                :start] + f'self.tr(\'{match.group(1)[1:-1]}\')' + new_class_content[end:]
        content = content[:class_start] + new_class_content + content[class_start + class_end:]
    updated_content = content

    print(updated_content)
    write_txt(py_dev_path, updated_content)


def iread_csv(csv_file, pop_head=True, get_head=False):
    with open(csv_file, encoding='utf-8', mode='r') as f:
        f_csv = reader(f)
        if pop_head:
            head = next(f_csv, [])  # 获取首行并在需要时将其从数据中删除
        else:
            head = []
        idata = [tuple(row) for row in f_csv]  # 使用列表推导式简化数据读取
    if get_head:
        return idata, head
    else:
        return idata


def trans_self():
    src_head = ['Source', '目标语言']

    for i in range(len(language_tuples)):
        language_tuple = language_tuples[i]
        lang_code, en_name, cn_name, self_name = language_tuple

        ts_file = UserDataFolder / f'{APP_NAME}_{lang_code}.ts'
        csv_file = UserDataFolder / f'{APP_NAME}_{lang_code}.csv'

        # 提取可翻译的字符串生成ts文件
        cmd = f'{pylupdate} {py_path.as_posix()} -ts {ts_file.as_posix()}'
        call(cmd, shell=True)
        # 解析 ts 文件
        xml_text = read_txt(ts_file)
        doc = xmltodict.parse(xml_text)

        # 使用预先提供的翻译更新 ts 文件
        messages = doc['TS']['context']['message']

        en2dst, dst2en = {}, {}
        existing_sources = set()
        src = []
        if csv_file.exists():
            src = iread_csv(csv_file, True, False)
            for pind in range(len(src)):
                entry = src[pind]
                en_str = entry[0]
                dst_str = entry[-1]
                existing_sources.add(en_str)
                if en_str != '' and dst_str != '':
                    en2dst[en_str] = dst_str
                    dst2en[dst_str] = en_str

        updated_messages = deepcopy(messages)
        missing_sources = []
        for message in updated_messages:
            source = message['source']
            if source not in existing_sources:
                missing_sources.append(source)
            if source in en2dst:
                message['translation'] = en2dst[source]

        doc['TS']['context']['message'] = updated_messages
        if missing_sources:
            new_src = deepcopy(src)
            for missing_source in missing_sources:
                new_src.append([missing_source, ''])
            write_csv(csv_file, new_src, src_head)

        # 保存更新后的 ts 文件
        with ts_file.open('w', encoding='utf-8') as f:
            f.write(xmltodict.unparse(doc))

        # 生成 qm
        cmd = f'{lrelease} {ts_file.as_posix()}'
        call(cmd, shell=True)


if __name__ == "__main__":
    # wrap_strings_with_tr()
    # trans_self()

    appgui = QApplication(sys.argv)
    # lang_code = 'en_US'
    lang_code = 'zh_CN'
    # lang_code = 'zh_TW'
    # lang_code = 'ja_JP'
    qm_path = UserDataFolder / f'iManhua_{lang_code}.qm'
    translator = QTranslator()
    translator.load(str(qm_path))
    QApplication.instance().installTranslator(translator)
    appgui.installTranslator(translator)

    main_qt()
