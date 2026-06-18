import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QListWidget, QComboBox, QLabel,
    QTabWidget, QSplitter
)
from PyQt5.QtCore import Qt


class MplCanvas(FigureCanvas):
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        super().__init__(self.fig)
        self.fig.tight_layout()


class GraphTab(QWidget):
    def __init__(self, filename, parent=None):
        super().__init__(parent)
        self.filename = filename
        self.data = None
        self.selected_line = None

        # Layout split into left (graph) and right (controls)
        splitter = QSplitter(Qt.Horizontal)

        # Left side: graph
        self.canvas = MplCanvas()
        splitter.addWidget(self.canvas)

        # Right side: controls
        control_widget = QWidget()
        control_layout = QVBoxLayout()

        self.load_btn = QPushButton("Load File")
        self.load_btn.clicked.connect(self.load_file)
        control_layout.addWidget(self.load_btn)

        control_layout.addWidget(QLabel("Double-click Y-axis variable:"))
        self.list_widget = QListWidget()
        self.list_widget.itemDoubleClicked.connect(self.plot_data)
        control_layout.addWidget(self.list_widget)

        # Styling controls
        control_layout.addWidget(QLabel("Line Color:"))
        self.color_combo = QComboBox()
        self.color_combo.addItems(["blue", "red", "green", "black", "orange"])
        control_layout.addWidget(self.color_combo)

        control_layout.addWidget(QLabel("Line Style:"))
        self.style_combo = QComboBox()
        self.style_combo.addItems(["-", "--", "-.", ":"])
        control_layout.addWidget(self.style_combo)

        control_layout.addWidget(QLabel("Line Width:"))
        self.width_combo = QComboBox()
        self.width_combo.addItems([str(i) for i in range(1, 6)])
        control_layout.addWidget(self.width_combo)

        control_layout.addWidget(QLabel("Marker:"))
        self.marker_combo = QComboBox()
        self.marker_combo.addItems(["None", "o", "s", "x", "d", "^"])
        control_layout.addWidget(self.marker_combo)

        control_layout.addWidget(QLabel("Marker Size:"))
        self.marker_size_combo = QComboBox()
        self.marker_size_combo.addItems([str(i) for i in range(4, 13)])
        control_layout.addWidget(self.marker_size_combo)

        # Apply changes
        self.apply_btn = QPushButton("Apply Style")
        self.apply_btn.clicked.connect(self.update_line_style)
        control_layout.addWidget(self.apply_btn)

        control_layout.addStretch()
        control_widget.setLayout(control_layout)
        splitter.addWidget(control_widget)

        layout = QHBoxLayout()
        layout.addWidget(splitter)
        self.setLayout(layout)

        # Enable line picking
        self.canvas.mpl_connect("pick_event", self.on_pick)

        # If filename given, load directly
        if filename:
            self.load_file(filename)

    def load_file(self, fname=None):
        if not fname:
            fname, _ = QFileDialog.getOpenFileName(self, "Open CSV/Excel", "", "Data Files (*.csv *.xlsx)")
        if not fname:
            return
        self.filename = fname

        # Load CSV or Excel
        if fname.endswith(".csv"):
            self.data = pd.read_csv(fname)
        else:
            self.data = pd.read_excel(fname)

        # Update list widget
        self.list_widget.clear()
        for col in self.data.columns:
            self.list_widget.addItem(col)

    def plot_data(self, item):
        if self.data is None:
            return

        y_col = item.text()
        x_col = self.data.columns[0]  # first column as X
        x = self.data[x_col]
        y = self.data[y_col]

        line, = self.canvas.ax.plot(x, y, label=y_col, picker=5)
        self.canvas.ax.set_xlabel(x_col)
        self.canvas.ax.set_ylabel("Values")
        self.canvas.ax.set_title(self.filename)
        self.canvas.ax.grid(True)  # ✅ Enable grid
        self.canvas.ax.legend()
        self.canvas.draw()

    def on_pick(self, event):
        if isinstance(event.artist, plt.Line2D):
            # Reset old selection
            if self.selected_line:
                orig_width = getattr(self.selected_line, "_orig_width", 1)
                self.selected_line.set_linewidth(orig_width)

            # Highlight new selection
            self.selected_line = event.artist
            self.selected_line._orig_width = self.selected_line.get_linewidth()
            self.selected_line.set_linewidth(self.selected_line._orig_width + 2)
            self.canvas.draw()

    def update_line_style(self):
        if not self.selected_line:
            return

        color = self.color_combo.currentText()
        style = self.style_combo.currentText()
        width = int(self.width_combo.currentText())
        marker = self.marker_combo.currentText()
        msize = int(self.marker_size_combo.currentText())

        if marker == "None":
            marker = ""

        self.selected_line.set_color(color)
        self.selected_line.set_linestyle(style)
        self.selected_line.set_linewidth(width)
        self.selected_line.set_marker(marker)
        self.selected_line.set_markersize(msize)

        # Update stored width
        self.selected_line._orig_width = width
        self.canvas.draw()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Multi-Tab Graph Viewer")
        self.resize(1200, 700)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Start with an empty tab
        self.add_new_tab()

    def add_new_tab(self, filename=None):
        tab = GraphTab(filename)
        name = filename if filename else "New Tab"
        self.tabs.addTab(tab, name.split("/")[-1])
        self.tabs.setCurrentWidget(tab)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())




