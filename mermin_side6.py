from PySide6.QtWidgets import (QApplication, QWidget, QMainWindow, QLabel, QRadioButton,
                               QVBoxLayout, QHBoxLayout, QGroupBox, QPushButton, QGraphicsScene,
                               QGraphicsView, QTableWidget, QTableWidgetItem, QFileDialog, QAbstractItemView,
                               QDialog)
from PySide6.QtGui import QPalette, QColor, QBrush, QAction, QPixmap
import cirq, json


class Detector(QGroupBox):
    def __init__(self, name):
        super().__init__()
        self.setTitle(name)
        self.indicator=QLabel(text='')
        self.indicator.setAutoFillBackground(True)

        palette=self.indicator.palette()
        palette.setColor(QPalette.Window, QColor('grey'))
        self.indicator.setPalette(palette)

        self.indicator.setFixedSize(60,60)

        layout = QVBoxLayout()
        layout.addWidget(self.indicator)
        self.radio_buttons = [QRadioButton(text=f'{i}') for i in range(3)]
        self.radio_buttons[0].setChecked(True)
        for rb in self.radio_buttons:
            layout.addWidget(rb)

        self.setLayout(layout)

        self.colors = ('red', 'green')

    def get_state(self):
        for i in range(len(self.radio_buttons)):
            if self.radio_buttons[i].isChecked():
                return i

    def set_color(self, c):
        palette=self.indicator.palette()
        palette.setColor(QPalette.Window, QColor(self.colors[c]))
        self.indicator.setPalette(palette)


class HistoryWidget(QGroupBox):
    def __init__(self):
        super().__init__()
        self.setTitle("History")
        self.history=[]
        self.table=QTableWidget(0,4)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers);
        self.table.setHorizontalHeaderLabels(['Det1', 'Det2', 'col1', 'col2'])
        for i in range(4):
            self.table.setColumnWidth(i, 50)
        self.is_visible = True

        save_button=QPushButton('Save history')
        save_button.clicked.connect(self.save_history)

        layout=QVBoxLayout()
        layout.addWidget(self.table)
        layout.addWidget(save_button)
        self.setLayout(layout)

    def add_row(self, det1, det2, col1, col2):
        i = self.table.rowCount()
        c1 = window.detector1.colors[col1]
        c2 = window.detector2.colors[col2]
        self.history.append((det1, det2, c1, c2))
        self.table.insertRow(i)
        self.table.setItem(i, 0, QTableWidgetItem(f'{det1}'))
        self.table.setItem(i, 1, QTableWidgetItem(f'{det2}'))
        self.table.setItem(i, 2, QTableWidgetItem(''))
        self.table.setItem(i, 3, QTableWidgetItem(''))
        self.table.item(i, 2).setBackground(QBrush(c1))
        self.table.item(i, 3).setBackground(QBrush(c2))

    def save_history(self):
        filename=QFileDialog.getSaveFileName(self, 'Save file', '.',
                                             'Text file (*.txt);; JSON file (*.json)')
        if filename[1] == 'Text file (*.txt)':
            with open(filename[0], 'w') as f:
                for line in self.history:
                    f.write(f'{line}\n')
        elif filename[1] == 'JSON file (*.json)':
            with open(filename[0], 'w') as f:
                json.dump(self.history, f)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Mermin device')

        self.root_layout = QHBoxLayout() # Contains main_layout + on/off history
        main_layout = QVBoxLayout() # Contains top_layout and button_layout
        top_layout = QHBoxLayout() #Detector - Canvas - Detector
        button_layout = QHBoxLayout() #label - "Run" - label - "History>>"
        history_layout = QHBoxLayout() #Title - Table - save button

        self.detector1=Detector('Detector1')
        top_layout.addWidget(self.detector1)

        self.graphic_scene=QGraphicsScene()
        min_size = 100
        self.graphic_scene.setSceneRect(-min_size, -min_size, 2*min_size, 2*min_size)
        self.graphic_view=QGraphicsView(self.graphic_scene)
        self.draw_scene()
        self.graphic_view = QGraphicsView(self.graphic_scene)
        top_layout.addWidget(self.graphic_view)
        self.graphic_view.setMinimumSize(2.2*min_size, 2.2*min_size)

        self.detector2=Detector('Detector1')
        top_layout.addWidget(self.detector2)

        button_layout.addWidget(QLabel(text='    '))
        run_button = QPushButton(text='Run')
        button_layout.addWidget(run_button)
        run_button.clicked.connect(self.run_function)
        button_layout.addWidget(QLabel(text='    '))
        self.history_button = QPushButton(text='History >>')
        button_layout.addWidget(self.history_button)
        self.history_button.clicked.connect(self.history_function)

        main_layout.addLayout(top_layout)
        main_layout.addLayout(button_layout)

        self.history_widget = HistoryWidget()
        history_layout.addWidget(self.history_widget)

        self.root_layout.addLayout(main_layout)
        self.root_layout.addLayout(history_layout)

        self.widget=QWidget()
        self.widget.setLayout(self.root_layout)
        self.setCentralWidget(self.widget)

        save_file_action=QAction('&Save', self)
        save_file_action.triggered.connect(self.history_widget.save_history)

        history_action=QAction('History', self)
        history_action.setCheckable(True)
        history_action.setChecked(True)
        history_action.triggered.connect(self.history_function)

        exit_action=QAction('&Exit', self)
        exit_action.triggered.connect(exit)

        about_action=QAction('&About', self)
        about_action.triggered.connect(self.about_dialog)

        help_action=QAction('&Help', self)
        help_action.triggered.connect(self.help_dialog)

        menu=self.menuBar()
        file_menu = menu.addMenu('&File')
        help_menu = menu.addMenu('Help')

        file_menu.addAction(save_file_action)
        file_menu.addAction(history_action)
        file_menu.addSeparator()
        file_menu.addAction(exit_action)

        help_menu.addAction(help_action)
        help_menu.addAction(about_action)

    def draw_scene(self):
        h_size=self.graphic_scene.width()
        r_size=h_size/20
        self.graphic_scene.addRect(-r_size,-r_size, 2*r_size, 2*r_size)
        self.graphic_scene.addLine(-r_size, -r_size, r_size, r_size)
        self.graphic_scene.addLine(-r_size, r_size, r_size, -r_size)

        self.graphic_scene.addLine(-4*h_size, 0, -r_size, 0)
        self.graphic_scene.addLine(r_size, 0, 4*h_size, 0)

    def run_function(self):
        a = self.detector1.get_state() / 3
        b = self.detector2.get_state() / 3

        q_A = cirq.NamedQubit('A')
        q_B = cirq.NamedQubit('B')

        crt = cirq.Circuit()
        crt.append(cirq.X(q_A))
        crt.append(cirq.H(q_A))
        crt.append(cirq.CNOT(q_A, q_B))
        crt.append(cirq.X(q_A) ** a)
        crt.append(cirq.X(q_B) ** b)
        crt.append(cirq.measure(q_A, key='A'))
        crt.append(cirq.measure(q_B, key='B'))

        # print(f"Circuit:\n{crt}")

        sim = cirq.Simulator()
        result = sim.run(crt)

        A = result.measurements['A'][0][0]
        B = result.measurements['B'][0][0]

        self.detector1.set_color(A)
        self.detector2.set_color(B)

        self.history_widget.add_row(self.detector1.get_state(), self.detector2.get_state(), A,B)

    def history_function(self):
        if not self.history_widget.is_visible:
            self.history_button.setText('History <<')
            self.history_widget.setVisible(True)

        else:
            self.history_button.setText('History >>')
            self.history_widget.setVisible(False)
        self.history_widget.is_visible = not self.history_widget.is_visible

    def about_dialog(self):
        about_dlg=QDialog(self)
        about_dlg.setWindowTitle('About')
        dlg_layout=QHBoxLayout()
        dlg_pic_label=QLabel('')
        dlg_pic_label.setPixmap(QPixmap('logo.tif'))
        right_widget=QWidget()
        right_layout=QVBoxLayout()
        dlg_text_label=QLabel('Mermin device\n (c) 2024 QMode lab IKBFU\n Licensed under LGPL 3.0')
        dlg_button=QPushButton('Ok')
        dlg_button.clicked.connect(about_dlg.destroy)
        right_layout.addWidget(dlg_text_label)
        right_layout.addWidget(dlg_button)
        right_widget.setLayout(right_layout)
        dlg_layout.addWidget(dlg_pic_label)
        dlg_layout.addWidget(right_widget)
        about_dlg.setLayout(dlg_layout)
        about_dlg.exec()

    def help_dialog(self):
        help_dialog=QDialog()
        help_dialog.setWindowTitle('Help')
        help_text1=QLabel("""This program illustrate Mermin device.
Mermin's device is an quantum-mechanical demonstration
which show statistics that could not be explained
by classical physics.
It was first proposed in the paper by N.D. Mermin
"Bringing home the atomic world: Quantum mysteries for anybody"
Am. J. Phys. 49, 940–943 (1981)
        """)
        help_text2 = QLabel("<a href=https://doi.org/10.1119/1.12594>https://doi.org/10.1119/1.12594</a>")
        help_text2.openExternalLinks()

        help_layout=QVBoxLayout()

        help_OK_button=QPushButton('Ok')
        help_OK_button.clicked.connect(help_dialog.destroy)

        help_layout.addWidget(help_text1)
        help_layout.addWidget(help_text2)
        help_layout.addWidget(help_OK_button)
        help_dialog.setLayout(help_layout)
        help_dialog.exec()


if __name__=='__main__':
    app = QApplication([])

    window=MainWindow()
    window.show()

    app.exec()