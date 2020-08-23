# https://www.jetbrains.com/help/pycharm/using-code-editor.html
from PySide2 import QtWidgets,QtCore, QtGui


class Worker(QtCore.QObject):
    finished = QtCore.Signal()
    def __init__(self):
        super().__init__()

    def app(self):

        print("finally !")
        self.finished.emit()

class MainWindow(QtWidgets.QWidget):
    def __init__(self, ctx):
        super().__init__()
        self.ctx = ctx
        self.setup_ui()

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.lbl_airtable = QtWidgets.QLabel("API key Airtable")
        self.spn_airtable = QtWidgets.QLineEdit()
        self.lbl_mail_link = QtWidgets.QLabel("mail linkedin")
        self.spn_mail_link = QtWidgets.QLineEdit()
        self.lbl_pwd_link = QtWidgets.QLabel("mot de passe linkedin")
        self.spn_pwd_link = QtWidgets.QLineEdit()
        self.btn_on = QtWidgets.QPushButton("Lancer l'application")
        self.btn_off = QtWidgets.QPushButton("Arrêter l'application")

    def modify_widgets(self):
        css_file = self.ctx.get_resource("style.css")
        with open(css_file, "r") as f:
            self.setStyleSheet(f.read())

    def create_layouts(self):
        self.main_layout = QtWidgets.QGridLayout(self)

    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.lbl_airtable, 0, 0, 1, 2)
        self.main_layout.addWidget(self.spn_airtable, 1, 0, 1, 2)
        self.main_layout.addWidget(self.lbl_mail_link, 2, 0, 1, 2)
        self.main_layout.addWidget(self.spn_mail_link, 3, 0, 1, 2)
        self.main_layout.addWidget(self.lbl_pwd_link, 4, 0, 1, 2)
        self.main_layout.addWidget(self.spn_pwd_link, 5, 0, 1, 2)
        self.main_layout.addWidget(self.btn_on, 6, 0, 1, 1)
        self.main_layout.addWidget(self.btn_off, 6, 1, 1, 1)


    def setup_connections(self):
        self.btn_on.clicked.connect(self.launch)


    def is_creds_ok(self):
        return True

    def launch(self):
        # check if all data are good
        if self.is_creds_ok():
            self.thread = QtCore.QThread(self)
            self.worker = Worker()
            self.worker.moveToThread(self.thread)
            self.thread.started.connect(self.worker.app)
            self.worker.finished.connect(self.thread.quit)
            self.thread.start()
        else:
            msg_box = QtWidgets.QMessageBox(QtWidgets.QMessageBox.Warning,
                                            "Erreur credentials",
                                            "Vous n'avez pas bien remplis vos crédentials")
            msg_box.exec_()
            return None

#
# from PySide2 import QtWidgets
#
# class MainWindow(QtWidgets.QWidget):
#     def __init__(self):
#         super().__init__()
#         self.setup_ui()
#
#     def setup_ui(self):
#         self.create_widgets()
#         self.modify_widgets()
#         self.create_layouts()
#         self.add_widgets_to_layouts()
#         self.setup_connections()
#
#     def create_widgets(self):
#         self.btn_clique = QtWidgets.QPushButton("Clique")
#
#     def modify_widgets(self):
#         pass
#
#     def create_layouts(self):
#         self.main_layout = QtWidgets.QVBoxLayout(self)
#
#     def add_widgets_to_layouts(self):
#         self.main_layout.addWidget(self.btn_clique)
#
#     def setup_connections(self):
#         self.btn_clique.clicked.connect(self.bouton_clicked)
#
#     def bouton_clicked(self):
#         message_box = QtWidgets.QMessageBox()
#         message_box.setWindowTitle("Cool")
#         message_box.setText("Tu a réussi frère")
#         message_box.exec_()