from fbs_runtime.application_context.PySide2 import ApplicationContext, cached_property
from PySide2.QtWidgets import QFormLayout, QPushButton, QLabel, QLineEdit, QDialog, QGridLayout, QMessageBox

from PySide2 import QtGui, QtCore, QtWidgets
from package.main_windows import MainWindow
import sys, os, json
HOME_DIR = QtCore.QStandardPaths().standardLocations(QtCore.QStandardPaths.HomeLocation)[0]

def creds_absent():
    folder_name = '/.linkedin_booster'
    if not os.path.exists(HOME_DIR + folder_name):
        print("pass here")
        os.makedirs(HOME_DIR + folder_name)
        return True
    else:
        try:
            with open(HOME_DIR + folder_name + '/' + 'creds.json') as json_file:
                cred = json.load(json_file)
                return cred
        except:
            print("pass here3")
            True



class Form(QDialog):
    def __init__(self, parent=None):
        super(Form, self).__init__(parent)

        self.username = QLineEdit(self)
        self.QUserLabel = QLabel("USERNAME")

        self.password = QLineEdit(self)
        self.QPasswordLabel = QLabel("PASSWORD")

        self.btn_Submit = QPushButton("LOGIN")

        layout = QFormLayout()
        layout.addRow(self.QUserLabel, self.username)
        layout.addRow(self.QPasswordLabel, self.password)
        layout.addRow(self.btn_Submit)

        self.setLayout(layout)

        # self.connect(self.btn_Submit, SIGNAL("clicked()"), self.Submit_btn)
        self.btn_Submit.clicked.connect(self.Submit_btn)
    def Submit_btn(self):
        USERNAME = self.username.text()
        PASSWORD = self.password.text()


        if self.username.text() == "moi" and self.password.text() == "moi":
            print('lol')
            return True
        else:
            print("pas lol")
            return False


#https://airtable-python-wrapper.readthedocs.io/en/master/
class AppContext(ApplicationContext):
    def run(self):
        window = MainWindow(ctx=self)
        # window.resize(1920 / 4, 1200 / 2)
        window.show()

        return self.app.exec_()

    @cached_property #permet de mettre ce que retourne la fonction dans le cache
    def img_checked(self):
        return QtGui.QIcon(self.get_resource("images/checked.png"))

    @cached_property #permet de mettre ce que retourne la fonction dans le cache
    def img_unchecked(self):
        return QtGui.QIcon(self.get_resource("images/unchecked.png"))

    @cached_property  # permet de mettre ce que retourne la fonction dans le cache
    def upload_pdf_icon(self):
        return QtGui.QIcon(self.get_resource("pdf-book.png"))


if __name__ == '__main__':
    creds = creds_absent()

    appctxt = AppContext()


    sys.exit(appctxt.run())