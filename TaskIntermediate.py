import sys
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QFileDialog, QLabel, QComboBox, QListWidget, QSizePolicy,
    QTabWidget, QGridLayout, QCheckBox
)

class MplCanvas(FigureCanvas):
    def __init__(self):
        self.fig, self.ax = plt.subplots()
        super().__init__(self.fig)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Excel Plotter")

        self.data = None
        self.lines = []
        self.selected_line = None

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # --- Tab 1 (Plot)
        plot_tab = QWidget()
        plot_layout = QHBoxLayout(plot_tab)

        # Left: Matplotlib canvas
        self.canvas = MplCanvas()
        plot_layout.addWidget(self.canvas, 3)

        # Right: Controls
        controls = QVBoxLayout()

        load_btn = QPushButton("Load Excel/CSV")
        load_btn.clicked.connect(self.load_file)
        controls.addWidget(load_btn)

        self.x_combo = QComboBox()
        self.y_list = QListWidget()
        self.y_list.setSelectionMode(self.y_list.MultiSelection)
        controls.addWidget(QLabel("X Axis:"))
        controls.addWidget(self.x_combo)
        controls.addWidget(QLabel("Y Axis (multi):"))
        controls.addWidget(self.y_list)

        self.hold_check = QCheckBox("Hold On (Overlay)")
        self.grid_check = QCheckBox("Show Grid")
        controls.addWidget(self.hold_check)
        controls.addWidget(self.grid_check)

        self.plot_btn = QPushButton("Plot Selected")
        self.plot_btn.clicked.connect(self.plot_data)
        controls.addWidget(self.plot_btn)

        # Styling controls
        controls.addWidget(QLabel("Line Color:"))
        self.color_combo = QComboBox()
        self.color_combo.addItems(["blue", "red", "green", "black", "magenta"])
        self.color_combo.currentTextChanged.connect(self.update_line_style)
        controls.addWidget(self.color_combo)

        controls.addWidget(QLabel("Line Style:"))
        self.style_combo = QComboBox()
        self.style_combo.addItems(["-", "--", "-.", ":"])
        self.style_combo.currentTextChanged.connect(self.update_line_style)
        controls.addWidget(self.style_combo)

        controls.addWidget(QLabel("Line Width:"))
        self.width_combo = QComboBox()
        self.width_combo.addItems(["1", "2", "3", "4"])
        self.width_combo.currentTextChanged.connect(self.update_line_style)
        controls.addWidget(self.width_combo)

        controls.addWidget(QLabel("Marker:"))
        self.marker_combo = QComboBox()
        self.marker_combo.addItems(["o", "s", "^", "*", "x", "None"])
        self.marker_combo.currentTextChanged.connect(self.update_line_style)
        controls.addWidget(self.marker_combo)

        controls.addWidget(QLabel("Marker Size:"))
        self.marker_size_combo = QComboBox()
        self.marker_size_combo.addItems(["4", "6", "8", "10"])
        self.marker_size_combo.currentTextChanged.connect(self.update_line_style)
        controls.addWidget(self.marker_size_combo)

        controls.addStretch()
        plot_layout.addLayout(controls, 1)

        self.tabs.addTab(plot_tab, "Plot")

        # --- Tab 2 (Data Preview)
        data_tab = QWidget()
        self.data_label = QLabel("No data loaded")
        dlayout = QVBoxLayout(data_tab)
        dlayout.addWidget(self.data_label)
        self.tabs.addTab(data_tab, "Data Preview")

        # Connect pick events for line selection
        self.canvas.mpl_connect("pick_event", self.on_pick)

    def load_file(self):
        file, _ = QFileDialog.getOpenFileName(self, "Open Excel/CSV", "", "Data Files (*.csv *.xlsx *.xls)")
        if file:
            if file.endswith(".csv"):
                self.data = pd.read_csv(file)
            else:
                self.data = pd.read_excel(file)

            self.x_combo.clear()
            self.x_combo.addItems(self.data.columns)

            self.y_list.clear()
            self.y_list.addItems(self.data.columns)

            self.data_label.setText(str(self.data.head()))

    def plot_data(self):
        if self.data is None:
            return

        xcol = self.x_combo.currentText()
        ycols = [item.text() for item in self.y_list.selectedItems()]
        if not xcol or not ycols:
            return

        if not self.hold_check.isChecked():
            self.canvas.ax.clear()
            self.lines = []

        for ycol in ycols:
            line, = self.canvas.ax.plot(
                self.data[xcol], self.data[ycol],
                label=ycol, picker=5
            )
            self.lines.append(line)

        if self.grid_check.isChecked():
            self.canvas.ax.grid(True)

        self.canvas.ax.legend()
        self.canvas.draw()

    def on_pick(self, event):
        if isinstance(event.artist, plt.Line2D):
            if self.selected_line:
                # Reset previous selection
                self.selected_line.set_linewidth(1)
            self.selected_line = event.artist
            self.selected_line.set_linewidth(3)  # Highlight
            self.canvas.draw()

    def update_line_style(self):
        if not self.selected_line:
            return  # do nothing if no line selected

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

        self.canvas.draw()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec_())
