from markdown.extensions.codehilite import CodeHiliteExtension
from pygments.formatters import HtmlFormatter
import re
import sys

from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QFont, QTextCharFormat, QTextCursor,QDesktopServices
from PyQt6.QtWebEngineCore import QWebEnginePage
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWidgets import QApplication, QMainWindow, QPlainTextEdit, QSplitter, \
    QTextEdit, QToolBar, QVBoxLayout, QWidget, QDockWidget, QInputDialog, QTreeWidget, QMenu, QTreeWidgetItem,QComboBox
from loguru import logger
from markdown import markdown
from mdx_gfm import GithubFlavoredMarkdownExtension


class SyncScrollBar(QPlainTextEdit):
    def __init__(self, *args, **kwargs):
        super(SyncScrollBar, self).__init__(*args, **kwargs)
        self._scrollbar = self.verticalScrollBar()

    def set_sync_scrollbar(self, scrollbar):
        self._scrollbar.valueChanged.connect(scrollbar.setValue)
        scrollbar.rangeChanged.connect(self._sync_range)

    def _sync_range(self, min_val, max_val):
        self._scrollbar.setRange(min_val, max_val)


class MarkdownEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Markdown Editor")
        self.setGeometry(100, 100, 1200, 800)

        self.init_ui()
        self.show()

    def init_ui(self):
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)
        self.toolbar.addAction("Bold", self.apply_bold)
        self.toolbar.addAction("Italic", self.apply_italic)
        self.toolbar.addAction("Underline", self.apply_underline)
        self.toolbar.addAction("Strikethrough", self.apply_strikethrough)
        self.toolbar.addAction("Blockquote", self.apply_blockquote)
        self.toolbar.addAction("Insert Link", self.insert_link)
        self.toolbar.addAction("Insert Image", self.insert_image)
        self.toolbar.addAction("Insert Code", self.insert_code)
        self.toolbar.addAction("Heading 1", lambda: self.apply_heading(1))
        self.toolbar.addAction("Heading 2", lambda: self.apply_heading(2))
        self.toolbar.addAction("Heading 3", lambda: self.apply_heading(3))
        self.toolbar.addAction("Heading 4", lambda: self.apply_heading(4))
        self.toolbar.addAction("Heading 5", lambda: self.apply_heading(5))
        self.toolbar.addAction("Heading 6", lambda: self.apply_heading(6))

        self.toc_tree = QTreeWidget()
        self.toc_tree.setHeaderHidden(True)

        # 添加折叠和展开的上下文菜单
        self.toc_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.toc_tree.customContextMenuRequested.connect(self.show_toc_context_menu)

        self.toc_dock = QDockWidget("Table of Contents")
        self.toc_dock.setWidget(self.toc_tree)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.toc_dock)

        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        self.layout.addWidget(self.splitter)

        self.editor = SyncScrollBar()
        self.editor.textChanged.connect(self.update_preview)
        self.splitter.addWidget(self.editor)

        self.preview = QWebEngineView()
        self.preview.setPage(QWebEnginePage(self.preview))
        self.splitter.addWidget(self.preview)

        self.sync_scrollbar = QTextEdit()
        self.sync_scrollbar.verticalScrollBar().setValue(0)
        self.sync_scrollbar.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.editor.set_sync_scrollbar(self.sync_scrollbar.verticalScrollBar())

        self.splitter.setSizes([self.width() // 2, self.width() // 2])

        self.view_mode_combo = QComboBox()
        self.view_mode_combo.addItem("编辑框+预览框")
        self.view_mode_combo.addItem("仅编辑框")
        self.view_mode_combo.addItem("仅预览框")
        self.view_mode_combo.currentIndexChanged.connect(self.change_view_mode)
        self.toolbar.addWidget(self.view_mode_combo)

    def change_view_mode(self, index):
        if index == 0:
            self.editor.show()
            self.preview.show()
        elif index == 1:
            self.editor.show()
            self.preview.hide()
        elif index == 2:
            self.editor.hide()
            self.preview.show()

    def show_toc_context_menu(self, pos):
        menu = QMenu()
        menu.addAction("Expand All", self.toc_tree.expandAll)
        menu.addAction("Collapse All", self.toc_tree.collapseAll)
        menu.exec(self.toc_tree.mapToGlobal(pos))

    def generate_toc(self, md_text):
        lines = md_text.split("\n")
        toc = []
        headers = []

        for line in lines:
            match = re.match(r"^(#{1,6})\s+(.+)$", line)
            if match:
                level, title = len(match.group(1)), match.group(2)
                toc.append((level, title))
                headers.append(title)

        self.toc_tree.clear()
        current_parent = self.toc_tree.invisibleRootItem()


        for level, title in toc:
            item = QTreeWidgetItem([title])
            item.setData(0, Qt.ItemDataRole.UserRole, level)

            while current_parent is not None and current_parent.data(0,
                                                                     Qt.ItemDataRole.UserRole) is not None and level <= current_parent.data(
                    0, Qt.ItemDataRole.UserRole):
                current_parent = current_parent.parent()

            if current_parent is None:
                current_parent = self.toc_tree.invisibleRootItem()

            current_parent.addChild(item)
            current_parent = item

            md_text = md_text.replace(f"{'#' * level} {title}", f"<h{level} id='{title}'>{title}</h{level}>")

        return headers

    def update_preview(self):
        md_text = self.editor.toPlainText()
        headers = self.generate_toc(md_text)

        html = markdown(md_text, extensions=[GithubFlavoredMarkdownExtension(), CodeHiliteExtension()])
        preview_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    display: flex;
                    flex-direction: row;
                }}
                .toc {{
                    flex-basis: 20%;
                    max-width: 20%;
                    border-right: 1px solid #ccc;
                    padding-right: 10px;
                    margin-right: 10px;
                }}
                .content {{
                    flex-basis: 80%;
                }}
            </style>
        </head>
        <body>
            <div class="content">
                {html}
            </div>
        </body>
        </html>
        """

        self.preview.setHtml(preview_html)

        # Connect anchor link click event
        self.preview.page().urlChanged.connect(self.handle_link_clicked)

    def highlight_header(self, header):
        cursor = self.editor.textCursor()
        cursor.movePosition(QTextCursor.Start)
        format = QTextCharFormat()
        format.setFontWeight(QFont.Bold)
        format.setBackground(Qt.yellow)
        cursor.setCharFormat(format)
        self.editor.setTextCursor(cursor)
        self.editor.centerCursor()
        self.editor.setExtraSelections(
            [QTextEdit.ExtraSelection(cursor, format)])

    def handle_link_clicked(self, url: QUrl):
        if not url.fragment() and url.scheme() in ["http", "https"]:
            QDesktopServices.openUrl(url)
            return
        if not url.fragment():
            return
        fragment = url.fragment()
        self.find_and_scroll_to_header(self.editor, fragment)
        self.highlight_header(fragment)
        self.preview.page().runJavaScript(f"window.location.hash='{fragment}';")

    @staticmethod
    def find_and_scroll_to_header(editor: QPlainTextEdit, header: str):
        block = editor.document().findBlockByNumber(0)
        while block.isValid():
            if block.text().strip().endswith(header):
                cursor = editor.textCursor()
                cursor.setPosition(block.position())
                editor.setTextCursor(cursor)
                editor.centerCursor()
                break
            block = block.next()

    def apply_bold(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.insertText(f"**{text}**")

    def apply_italic(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.insertText(f"*{text}*")

    def apply_underline(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.insertText(f"<u>{text}</u>")

    def apply_strikethrough(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.insertText(f"~~{text}~~")

    def apply_blockquote(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.insertText(f"> {text}")

    def insert_link(self):
        link, ok = QInputDialog.getText(self, "Insert Link", "Enter URL:")
        if ok:
            cursor = self.editor.textCursor()
            if cursor.hasSelection():
                text = cursor.selectedText()
                cursor.insertText(f"[{text}]({link})")

    def insert_image(self):
        image, ok = QInputDialog.getText(self, "Insert Image", "Enter Image URL:")
        if ok:
            cursor = self.editor.textCursor()
            cursor.insertText(f"![Image Description]({image})")

    def insert_code(self):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.insertText(f"`{text}`")

    def apply_heading(self, level):
        cursor = self.editor.textCursor()
        if cursor.hasSelection():
            text = cursor.selectedText()
            cursor.insertText(f"{'#' * level} {text}")


@logger.catch
def main_qt():
    window = MarkdownEditor()
    sys.exit(appgui.exec())


if __name__ == "__main__":
    appgui = QApplication(sys.argv)
    main_qt()
