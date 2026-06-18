import sys
import os
from typing import Optional

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFileDialog, QMessageBox,
    QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QComboBox, QCheckBox, QDoubleSpinBox, QSpinBox, QListWidget,
    QListWidgetItem, QAbstractItemView, QSplitter, QTabWidget, QTableWidget,
    QTableWidgetItem, QSizePolicy
)
from PyQt5.QtCore import Qt

import pandas as pd
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class MplCanvas(FigureCanvas):
    def __init__(self):
        self.fig = Figure(figsize=(6, 4), tight_layout=True)
        self.ax = self.fig.add_subplot(111)
        super().__init__(self.fig)

    def clear(self):
        self.ax.clear()
        self.ax.grid(True, linestyle=":", alpha=0.4)
        self.draw_idle()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Excel Plotter – PyQt5 + Matplotlib + Pandas")
        self.resize(1200, 720)

        # Data holders
        self.df: Optional[pd.DataFrame] = None
        self.current_path: Optional[str] = None

        # Root splitter: [left spacer] | [center tabs (canvas)] | [right controls]
        root = QSplitter(Qt.Horizontal)
        root.setChildrenCollapsible(False)
        self.setCentralWidget(root)

        # Left spacer (kept minimal to resemble your layout)
        left_spacer = QWidget()
        left_spacer.setMinimumWidth(80)
        root.addWidget(left_spacer)

        # Center: Tabs with matplotlib canvas in Tab 1 and data preview in Tab 2
        center_container = QWidget()
        center_layout = QVBoxLayout(center_container)
        self.tabs = QTabWidget()
        center_layout.addWidget(self.tabs)

        # Tab 1: Plot area
        tab1 = QWidget()
        tab1_layout = QVBoxLayout(tab1)
        self.canvas = MplCanvas()
        self.toolbar = NavigationToolbar(self.canvas, self)
        tab1_layout.addWidget(self.toolbar)
        tab1_layout.addWidget(self.canvas)
        self.tabs.addTab(tab1, "Tab 1 – Plot")

        # Tab 2: Data preview
        tab2 = QWidget()
        tab2_layout = QVBoxLayout(tab2)
        self.table = QTableWidget()
        tab2_layout.addWidget(self.table)
        self.tabs.addTab(tab2, "Tab 2 – Data Preview")

        root.addWidget(center_container)

        # Right controls panel
        right = QWidget()
        right_layout = QVBoxLayout(right)
        right_layout.setAlignment(Qt.AlignTop)

        # File info row
        file_row = QHBoxLayout()
        self.lblFile = QLabel("No file loaded")
        self.lblFile.setWordWrap(True)
        file_row.addWidget(self.lblFile, 1)
        right_layout.addLayout(file_row)

        # Buttons
        btn_row = QHBoxLayout()
        self.btnLoad = QPushButton("Load Excel/CSV")
        self.btnPlot = QPushButton("Plot Selected")
        btn_row.addWidget(self.btnLoad)
        btn_row.addWidget(self.btnPlot)
        right_layout.addLayout(btn_row)

        # Column selectors (Enter Quantities)
        col_group = QWidget()
        col_grid = QGridLayout(col_group)
        col_grid.setHorizontalSpacing(8)
        col_grid.setVerticalSpacing(6)
        col_grid.addWidget(QLabel("X (single)"), 0, 0)
        col_grid.addWidget(QLabel("Y (multi)"), 0, 1)

        self.listX = QListWidget()
        self.listX.setSelectionMode(QAbstractItemView.SingleSelection)
        self.listY = QListWidget()
        self.listY.setSelectionMode(QAbstractItemView.MultiSelection)
        self.listX.setMinimumWidth(160)
        self.listY.setMinimumWidth(160)
        self.listX.setMaximumHeight(180)
        self.listY.setMaximumHeight(180)
        col_grid.addWidget(self.listX, 1, 0)
        col_grid.addWidget(self.listY, 1, 1)
        right_layout.addWidget(col_group)

        # Style controls (Line, Linecolor, Linestyle, etc.)
        style_group = QWidget()
        style_grid = QGridLayout(style_group)
        r = 0
        style_grid.addWidget(QLabel("Line color"), r, 0)
        self.cmbLineColor = QComboBox()
        self.cmbLineColor.addItems([
            "auto", "black", "red", "green", "blue", "orange", "purple", "brown", "gray"
        ])
        style_grid.addWidget(self.cmbLineColor, r, 1)

        r += 1
        style_grid.addWidget(QLabel("Line style"), r, 0)
        self.cmbLineStyle = QComboBox()
        self.cmbLineStyle.addItems(["-", "--", "-.", ":", "None"])  # Matplotlib linestyles
        style_grid.addWidget(self.cmbLineStyle, r, 1)

        r += 1
        style_grid.addWidget(QLabel("Line width"), r, 0)
        self.spnLineWidth = QDoubleSpinBox()
        self.spnLineWidth.setRange(0.1, 10.0)
        self.spnLineWidth.setSingleStep(0.1)
        self.spnLineWidth.setValue(2.0)
        style_grid.addWidget(self.spnLineWidth, r, 1)

        r += 1
        style_grid.addWidget(QLabel("Marker"), r, 0)
        self.cmbMarker = QComboBox()
        self.cmbMarker.addItems([
            "None", "o", "s", "^", "v", "D", "x", "+", "*", "."
        ])
        style_grid.addWidget(self.cmbMarker, r, 1)

        r += 1
        style_grid.addWidget(QLabel("Marker size"), r, 0)
        self.spnMarkerSize = QSpinBox()
        self.spnMarkerSize.setRange(1, 30)
        self.spnMarkerSize.setValue(6)
        style_grid.addWidget(self.spnMarkerSize, r, 1)

        r += 1
        style_grid.addWidget(QLabel("Marker face color"), r, 0)
        self.cmbMarkerFace = QComboBox()
        self.cmbMarkerFace.addItems([
            "auto", "black", "red", "green", "blue", "orange", "purple", "brown", "gray", "white"
        ])
        style_grid.addWidget(self.cmbMarkerFace, r, 1)

        r += 1
        style_grid.addWidget(QLabel("Legend"), r, 0)
        self.cmbLegend = QComboBox()
        self.cmbLegend.addItems(["on", "off"])
        style_grid.addWidget(self.cmbLegend, r, 1)

        r += 1
        self.chkHoldOn = QCheckBox("Hold On (overlay)")
        self.chkGrid = QCheckBox("Grid")
        self.chkGrid.setChecked(True)
        style_grid.addWidget(self.chkHoldOn, r, 0)
        style_grid.addWidget(self.chkGrid, r, 1)

        right_layout.addWidget(style_group)

        # Stretch so controls stay top-aligned
        right_layout.addStretch(1)
        root.addWidget(right)

        # Signals
        self.btnLoad.clicked.connect(self.load_file_dialog)
        self.btnPlot.clicked.connect(self.plot_selected)

        # Set initial canvas grid
        self.canvas.ax.grid(True, linestyle=":", alpha=0.4)
        self.canvas.draw_idle()

    # ========= File Loading =========
    def load_file_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Excel/CSV",
            "",
            "Data Files (*.xlsx *.xls *.csv);;All Files (*)",
        )
        if not path:
            return
        try:
            self.load_dataframe(path)
            self.current_path = path
            self.lblFile.setText(os.path.basename(path))
            self.populate_columns()
            self.populate_table_preview()
            QMessageBox.information(self, "Loaded", f"Loaded file:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file:\n{e}")

    def load_dataframe(self, path: str):
        ext = os.path.splitext(path)[1].lower()
        if ext in [".xlsx", ".xls"]:
            self.df = pd.read_excel(path)
        elif ext == ".csv":
            self.df = pd.read_csv(path)
        else:
            raise ValueError("Unsupported file type. Use .xlsx, .xls, or .csv")
        # Clean column names a bit
        self.df.rename(columns=lambda c: str(c).strip(), inplace=True)

    def populate_columns(self):
        self.listX.clear()
        self.listY.clear()
        if self.df is None:
            return
        for col in self.df.columns:
            item_x = QListWidgetItem(col)
            item_y = QListWidgetItem(col)
            self.listX.addItem(item_x)
            self.listY.addItem(item_y)

    def populate_table_preview(self, max_rows: int = 300):
        if self.df is None:
            self.table.clear()
            self.table.setRowCount(0)
            self.table.setColumnCount(0)
            return
        df_show = self.df.head(max_rows)
        self.table.setRowCount(len(df_show))
        self.table.setColumnCount(len(df_show.columns))
        self.table.setHorizontalHeaderLabels([str(c) for c in df_show.columns])
        for r in range(len(df_show)):
            for c in range(len(df_show.columns)):
                val = df_show.iat[r, c]
                self.table.setItem(r, c, QTableWidgetItem(str(val)))
        self.table.resizeColumnsToContents()

    # ========= Plotting =========
    def _mpl_color(self, choice: str):
        return None if choice == "auto" else choice

    def _mpl_linestyle(self, choice: str):
        return None if choice == "None" else choice

    def _mpl_marker(self, choice: str):
        return None if choice == "None" else choice

    def plot_selected(self):
        if self.df is None:
            QMessageBox.warning(self, "No data", "Please load an Excel/CSV file first.")
            return

        # Get selected X
        x_items = self.listX.selectedItems()
        if not x_items:
            QMessageBox.warning(self, "Missing X", "Please select one X column.")
            return
        x_col = x_items[0].text()

        # Get selected Y(s)
        y_items = self.listY.selectedItems()
        if not y_items:
            QMessageBox.warning(self, "Missing Y", "Please select at least one Y column.")
            return
        y_cols = [it.text() for it in y_items]

        # Prepare X data
        try:
            x = pd.to_numeric(self.df[x_col], errors="coerce")
        except Exception:
            x = self.df[x_col]

        if not self.chkHoldOn.isChecked():
            self.canvas.ax.clear()

        # Grid
        if self.chkGrid.isChecked():
            self.canvas.ax.grid(True, linestyle=":", alpha=0.4)
        else:
            self.canvas.ax.grid(False)

        # Style selections
        color = self._mpl_color(self.cmbLineColor.currentText())
        linestyle = self._mpl_linestyle(self.cmbLineStyle.currentText())
        linewidth = float(self.spnLineWidth.value())
        marker = self._mpl_marker(self.cmbMarker.currentText())
        markersize = int(self.spnMarkerSize.value())
        markerfacecolor = self._mpl_color(self.cmbMarkerFace.currentText())

        # Plot each Y
        for y_col in y_cols:
            try:
                y = pd.to_numeric(self.df[y_col], errors="coerce")
            except Exception:
                y = self.df[y_col]

            label = y_col if y_col != x_col else f"{y_col} vs {x_col}"
            self.canvas.ax.plot(
                x,
                y,
                label=label,
                color=color,
                linestyle=linestyle,
                linewidth=linewidth,
                marker=marker,
                markersize=markersize,
                markerfacecolor=markerfacecolor,
            )

        # Labels + legend
        self.canvas.ax.set_xlabel(x_col)
        self.canvas.ax.set_ylabel(", ".join(y_cols) if len(y_cols) > 1 else y_cols[0])
        if self.cmbLegend.currentText() == "on":
            self.canvas.ax.legend(loc="best")

        self.canvas.draw_idle()


def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
