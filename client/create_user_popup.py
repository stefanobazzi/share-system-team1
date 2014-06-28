from PyQt4 import QtGui
import requests
import time
import json
import sys

def try_request(callback, retry_delay = 2, *args, **kwargs):
    while True:
        try:
            return callback(*args, **kwargs)
        except requests.exceptions.RequestException:
            print "fail"
            time.sleep(retry_delay)

def create_user(username, password):
    request = {
        "url": "http://127.0.0.1:5000/API/v1/create_user",
        "data": {
            "user": username,
            "psw": password
        }
    }
    response = try_request(requests.post, **request).status_code
    if response == 201:
        return True
    elif response == 409:
        return False
    else:
        sys.exit('bad request of create user')

class Login(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.textName = QtGui.QLineEdit(self)
        self.textPass = QtGui.QLineEdit(self)
        self.label_username =  QtGui.QLabel(self)
        self.label_password =  QtGui.QLabel(self)
        self.textPass.setEchoMode(QtGui.QLineEdit.Password)
        self.buttonLogin = QtGui.QPushButton('Sign in', self)
        self.buttonLogin.clicked.connect(self.handleLogin)
        self.label_username.setText('Username')
        self.label_password.setText('Password')
        self.setWindowTitle('RawBox')
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.label_username)
        layout.addWidget(self.textName)
        layout.addWidget(self.label_password)
        layout.addWidget(self.textPass)
        layout.addWidget(self.buttonLogin)

    def handleLogin(self):
        username, password = str(self.textName.text()), str(self.textPass.text())
        
        if create_user(username, password):
            with open('temp_conf.conf','wb') as f:
                json.dump({'username': username, 'password': password}, f)
            
            QtGui.QMessageBox.information(
                self, 
                'Success', 
                'User Created, we have create a RawBox folder under your home, enjoy! :)'
            )
            self.accept()
        else:
            QtGui.QMessageBox.warning(
                self, 
                'Error', 
                'User already exists'
            )

class Window(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

app = QtGui.QApplication(sys.argv)