from qtpy.QtCore import *
from qtpy.QtGui import *
from qtpy.QtWidgets import *
import qtmodern.styles
import qtmodern.windows
from collections import namedtuple
import uuid
import re

# houdini module import
import hou as hou

node = namedtuple("node", "file path cache_type frame_range progress")
no_parsers = node(None, None, None, None, None)

# This is a helper class which will be used to hold the data of the nodes
class Node:
    node = None
    context = ""
    node_path = ""
    frame_start = 0
    frame_end = 0
    frame_increment = 1
    f_range = 0
    file_path = ""
    cache_type = "Geometry"


# Custom widget class for the node parameter interface
class NodeParameter(QWidget):

    cache_node = Node()

    def __init__(self):
        super(NodeParameter, self).__init__()

        # initialize Widgets
        self.addNode = QPushButton("Start Caching")
        self.addNode.setFixedHeight(30)

        form_parameters = QFormLayout()
        empty_widget = QWidget()

        # Widgets for the form Layout
        self.nodePath = QLabel("")
        self.cache_type = QComboBox()
        self.cache_type.insertItem(0, "Geometry")
        self.cache_type.insertItem(1, "Simulation")

        # Frame Range parameters
        self.frame_cache = QComboBox()
        self.frame_cache.insertItem(0, "Render Static Frame")
        self.frame_cache.insertItem(1, "Render Frame Range")
        horizontal_frame_range_layout = QHBoxLayout()
        self.frame_start = QLineEdit()
        self.frame_end = QLineEdit()
        self.frame_increment = QLineEdit()
        horizontal_frame_range_layout.addWidget(self.frame_start)
        horizontal_frame_range_layout.addWidget(self.frame_end)
        horizontal_frame_range_layout.addWidget(self.frame_increment)
        self.timeWidgets = []
        for i in range(0, horizontal_frame_range_layout.count()):
            self.timeWidgets.append(horizontal_frame_range_layout.itemAt(i).widget())

        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)

        self.file_path = QLineEdit()

        # Add Widgets to the form Layout
        form_parameters.addRow("Node Path: ", self.nodePath)
        form_parameters.addRow("Cache type: ", self.cache_type)
        form_parameters.addRow("Frame Range: ", self.frame_cache)
        form_parameters.addRow("Start/End/Inc: ", horizontal_frame_range_layout)
        form_parameters.addRow(separator)
        form_parameters.addRow("File path: ", self.file_path)

        # Create main layout
        layout = QGridLayout(self)
        layout.setContentsMargins(2, 0, 2, 0)
        layout.addLayout(form_parameters, 1, 1)
        layout.addWidget(empty_widget, 1, 2)
        layout.addWidget(self.addNode, 2, 1, 1, 2)
        layout.setColumnStretch(1, 4)
        layout.setColumnStretch(2, 6)

        self.frame_cache.activated.connect(lambda: self.change_param("trange"))
        self.frame_start.editingFinished.connect(lambda: self.change_param("f1"))
        self.frame_end.editingFinished.connect(lambda: self.change_param("f2"))
        self.frame_increment.editingFinished.connect(lambda: self.change_param("f3"))
        self.file_path.editingFinished.connect(lambda: self.change_param("file"))

    def update_node(self, context, node_data):
        if node_data:
            self.update_object(node_data, context)
            self.frame_cache.setCurrentIndex(self.cache_node.f_range)
            if not self.cache_node.f_range:
                for widget in self.timeWidgets:
                    widget.blockSignals(True)
                    widget.setDisabled(True)
                    widget.blockSignals(False)
            else:
                for widget in self.timeWidgets:
                    widget.blockSignals(True)
                    widget.setDisabled(False)
                    widget.blockSignals(False)
            # Update node name
            if context == "SOP":
                path = node_data.path()[:-7]
                self.cache_node.node_path = path
                self.nodePath.setText(path)
            else:
                self.nodePath.setText(node_data.path())
                self.cache_node.node_path = node_data.path()
            # Update global parameters
            self.frame_start.setText(str(self.cache_node.frame_start))
            self.frame_end.setText(str(self.cache_node.frame_end))
            self.frame_increment.setText(str(self.cache_node.frame_increment))
            self.file_path.setText(self.cache_node.file_path)
        else:
            # Reset cache_node
            self.cache_node = Node()
            # Reset all widgets
            self.nodePath.setText("")
            self.frame_start.setText("")
            self.frame_end.setText("")
            self.frame_increment.setText("")
            self.file_path.setText("")

    def update_object(self, node_object, node_context):
        self.cache_node.node = node_object
        self.cache_node.context = node_context
        self.cache_node.f_range = node_object.parm("trange").eval()
        self.cache_node.frame_increment = node_object.parm("f3").eval()
        self.cache_node.file_path = node_object.parm("sopoutput").rawValue()
        if node_context == "SOP":
            self.cache_node.file_path = node_object.parent().parm("file").rawValue()
        if self.cache_node.f_range:
            self.cache_node.frame_start = int(node_object.parm("f1").eval())
            self.cache_node.frame_end = int(node_object.parm("f2").eval())
        else:
            self.cache_node.frame_start = int(hou.frame())
            self.cache_node.frame_end = int(hou.frame())

    def change_param(self, param):
        sop_parameters = {
            "trange": self.frame_cache.currentIndex(),
            "f1": self.frame_start.text(),
            "f2": self.frame_end.text(),
            "f3": self.frame_increment.text(),
            "file": self.file_path.text()
        }
        rop_parameters = {
            "trange": self.frame_cache.currentIndex(),
            "f1": self.frame_start.text(),
            "f2": self.frame_end.text(),
            "f3": self.frame_increment.text(),
            "sopoutput": self.file_path.text()
        }

        if param == "trange":
            for widget in self.timeWidgets:
                widget.setDisabled(1 - sop_parameters[param])

        # Update node Parameters
        node = self.cache_node.node
        node_type = node.type().name()
        if node_type == 'rop_geometry':
            parent_node = node.parent()
            parent_node.parm(param).set(sop_parameters[param])
        else:
            node.parm(param).set(rop_parameters[param])

        self.cache_node.frame_start = sop_parameters["f1"]
        self.cache_node.frame_end = sop_parameters["f2"]


# Class item delegate for having the Progress bar inside the table
class ProgressItemDelegate(QStyledItemDelegate):
    def paint(self, painter, option, index):
        data = index.model().data(index, Qt.DisplayRole)
        brush = QBrush()
        brush.setColor(QColor("#33a02c"))
        brush.setStyle(Qt.SolidPattern)

        width = option.rect.width() * data / 100

        rect = QRect(option.rect)
        rect.setWidth(width)
        painter.fillRect(rect, brush)

        pen = QPen()
        pen.setColor(Qt.black)
        painter.drawText(option.rect, Qt.AlignCenter | Qt.AlignVCenter, "{}%".format(data))


class TableModelProgress(QAbstractTableModel):

    _jobs = {}
    _node = {}
    _state = {}

    def __init__(self):
        super(TableModelProgress, self).__init__()
        self._data = {}
        self._headers = ["File", "Node", "Type", "Frame Range", "Progress"]

    def update_table(self, node=no_parsers):
        job_id = uuid.uuid4().hex

        # function to add the process to the signal
        def fwd_signal(target):
            return lambda *args: target(job_id, *args)

        self._data[job_id] = node

        # Update file for display purpose
        display_path = node.file.split("/")[-1]
        self._data[job_id] = self._data[job_id]._replace(file=display_path)

        p = QProcess()
        p.readyReadStandardOutput.connect(fwd_signal(self.handle_output))
        p.readyReadStandardError.connect(fwd_signal(self.handle_output))
        p.finished.connect(fwd_signal(self.done))

        self._jobs[job_id] = p
        render_node = node.path
        if "/obj" in render_node:
            render_node += "/render"
        file_path = node.file
        p.start("cmd", ["/c", "hbatch", "-c", "render -Va {};quit".format(render_node), "{}".format(file_path)])
        self.layoutChanged.emit()

    def handle_output(self, job_id):
        p = self._jobs[job_id]
        stdout = bytes(p.readAllStandardOutput()).decode("utf8")
        progress_re = re.compile("ALF_PROGRESS (\\d+)%")
        m = progress_re.search(stdout)
        if m:
            pc_complete = int(m.group(1))
            update = self._data[job_id]._replace(progress=pc_complete)
            self._data[job_id] = update
            self.layoutChanged.emit()

    def done(self, job_id, exit_code):
        update = self._data[job_id]._replace(progress=100)
        self._data[job_id] = update
        self.layoutChanged.emit()


    def data(self, index, role):
        job_ids = list(self._data.keys())
        self.task = []
        for item in job_ids:
            self.task.append(self._data[item])
        if role == Qt.DisplayRole:
            return self.task[index.row()][index.column()]

        if role == Qt.TextAlignmentRole:
            value = self.task[index.row()][index.column()]
            if isinstance(value, str):
                return Qt.AlignCenter

        if role == Qt.BackgroundColorRole:
            if index.row() % 2 == 0:
                return QColor('#6d6d6d')
            else:
                return QColor('#353535')

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self._headers[section]
        return QAbstractTableModel.headerData(self, section, orientation, role)

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._headers)


class ProgressUpdate(QWidget):
    def __init__(self):
        super(ProgressUpdate, self).__init__()
        delegate = ProgressItemDelegate()
        self.table_progress = QTableView()

        self.table_model = TableModelProgress()
        self.table_progress.setModel(self.table_model)

        self.table_progress.horizontalHeader().setFixedHeight(30)
        self.table_progress.verticalHeader().hide()
        self.table_progress.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.table_progress.setItemDelegateForColumn(self.table_model.columnCount(0) - 1, delegate)
        self.table_progress.setSelectionMode(QAbstractItemView.NoSelection)

        self.btn_clear = QPushButton("Clear tasks")
        self.btn_clear.clicked.connect(self.clear_tasks)
        self.btn_clear.setFixedHeight(30)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.table_progress)
        layout.addWidget(self.btn_clear)

    def clear_tasks(self):
        self.table_model.task = []
        self.table_model._data = {}
        self.table_model.layoutChanged.emit()


class MainWidget(QWidget):
    def __init__(self):
        super(MainWidget, self).__init__()
        # Create widgets and layout
        self.create_widgets()
        self.create_layouts()
        self.create_connections()
        self.setMinimumWidth(500)


        # Adapt table column width
        self.node_Progress.table_progress.setColumnWidth(0, (1280 - 20) / 5)
        self.node_Progress.table_progress.setColumnWidth(1, (1280 - 20) / 5)
        self.node_Progress.table_progress.setColumnWidth(2, (1280 - 20) / 5)
        self.node_Progress.table_progress.setColumnWidth(3, (1280 - 20) / 5)
        self.node_Progress.table_progress.setColumnWidth(4, (1280 - 20) / 5)

        self.rendering_nodes = {}
        self.file_open = False

    def _add_dic(self, node, node_type, dict_name):
        if node:
            dict_name[node_type] = node
            return True
        else:
            return False

    def _update_list(self):
        self.listModel.clear()

        node_type = self.nodeType.currentText()
        nodes_list = []
        for node in self.rendering_nodes[node_type]:
            if node_type == "SOP":
                node_name = node.parent().name()
            else:
                node_name = node.name()
            nodes_list.append(node_name)

        for node in nodes_list:
            item = QStandardItem(node)
            self.listModel.appendRow(item)

    def create_widgets(self):
        self.edit = QLineEdit("Hip file path")
        self.start = QPushButton("Open File")
        self.start.setFixedWidth(80)
        self.nodeType = QComboBox()

        # Node List
        self.list = QListView()
        self.list.setMinimumWidth(150)
        self.list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.listModel = QStandardItemModel()
        self.list.setModel(self.listModel)

        # Node Parameters widget
        self.node_Params = NodeParameter()

        # Node caching progress widget
        self.node_Progress = ProgressUpdate()

    def create_layouts(self):
        # Create Layouts
        self.mainVerticalLayout = QVBoxLayout(self)

        # Caching main Layout
        self.openingLayout = QHBoxLayout()
        self.openingLayout.addWidget(self.edit)
        self.openingLayout.addWidget(self.start)

        # Set layout to main parameters layout
        self.cacheLayout = QGridLayout()
        self.cacheLayout.setColumnStretch(1, 3)
        self.cacheLayout.setColumnStretch(2, 7)

        # Add widgets to layout
        self.cacheLayout.addWidget(self.nodeType, 1, 1)
        self.cacheLayout.addWidget(self.list, 2, 1)
        self.cacheLayout.addWidget(self.node_Params, 2, 2)
        self.cacheLayout.addWidget(self.node_Progress, 3, 1, 1, 2)

        # Add layouts to main layout
        self.mainVerticalLayout.addLayout(self.openingLayout)
        self.mainVerticalLayout.addLayout(self.cacheLayout)

        # Ending layout
        self.startCachingLayout = QHBoxLayout()

        self.mainVerticalLayout.addLayout(self.startCachingLayout)

    def create_connections(self):
        self.start.clicked.connect(self.display_caching_nodes)
        self.nodeType.activated.connect(self.update_node)
        self.list.selectionModel().currentChanged.connect(self.send_node_object)
        self.node_Params.addNode.clicked.connect(lambda: self.add_node_to_table(self.node_Params.cache_node))

    def opening_file(self):
        # Function to open the file
        hou.hipFile.load(self.edit.text(), ignore_load_warnings=True)
        self.file_open = True

    # Function for signals
    def display_caching_nodes(self):
        self.listModel.clear()
        self.opening_file()

        # Get instances type for caching
        out_render = hou.nodeType(hou.ropNodeTypeCategory(), "geometry")
        rendering_node = out_render.instances()

        # Get SOP filecache node
        sop_render = hou.nodeType(hou.sopNodeTypeCategory(), "rop_geometry")
        geometry_node = sop_render.instances()

        # Create empty dictionnary containing the render nodes and add the nodes
        self._add_dic(rendering_node, "ROP", self.rendering_nodes)
        self._add_dic(geometry_node, "SOP", self.rendering_nodes)

        # Update QComboBox
        i = 0
        self.nodeType.clear()
        for key, value in self.rendering_nodes.items():
            self.nodeType.insertItem(i, key)
            i += 1
        self._update_list()

    def update_node(self):
        self._update_list()
        context = self.nodeType.currentText()
        node = None
        self.node_Params.update_node(context, node)

    def send_node_object(self, index):
        text = index.data()
        if text is not None:
            context = self.nodeType.currentText()
            node = self.rendering_nodes[context][index.row()]
            self.node_Params.update_node(context, node)

    def add_node_to_table(self, node_data):
        if self.file_open:
            file_path = self.edit.text()
            path = node_data.node_path
            cache_type = node_data.cache_type
            frame_range = "{}-{}".format(node_data.frame_start, node_data.frame_end)
            progress = 0
            new_node = node(file_path, path, cache_type, frame_range, progress)
            hou.hipFile.save()
            self.node_Progress.table_model.update_table(new_node)
        else:
            print("Open a file first")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Caching Manager")
        self.widget = MainWidget()
        self.setCentralWidget(self.widget)

    def resizeEvent(self, event):
        self.widget.node_Progress.table_progress.setColumnWidth(0, (self.width() - 20) / 5)
        self.widget.node_Progress.table_progress.setColumnWidth(1, (self.width() - 20) / 5)
        self.widget.node_Progress.table_progress.setColumnWidth(2, (self.width() - 20) / 5)
        self.widget.node_Progress.table_progress.setColumnWidth(3, (self.width() - 20) / 5)
        self.widget.node_Progress.table_progress.setColumnWidth(4, (self.width() - 20) / 5)


if __name__ == "__main__":
    app = QApplication([])
    qtmodern.styles.dark(app)
    
    ui = qtmodern.windows.ModernWindow(MainWindow())
    ui.setFixedWidth(1280)
    ui.setFixedHeight(720)

    # Set icons and colors
    closeIcon = QIcon("./ressources/icons/close.png")
    minIcon = QIcon("./ressources/icons/minimize.png")
    maxIcon = QIcon("./ressources/icons/maximize.png")
    ui.btnClose.setIcon(closeIcon)
    ui.btnMinimize.setIcon(minIcon)
    ui.btnMaximize.setIcon(maxIcon)
    ui.btnRestore.setIcon(maxIcon)
    buttons = {ui.btnClose, ui.btnMaximize, ui.btnMinimize, ui.btnRestore}
    for button in buttons:
        with open("./ressources/style_override.qss") as stylesheet:
            button.setStyleSheet(stylesheet.read())
    # Show the window
    ui.show()
    app.exec_()
