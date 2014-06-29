from PyQt4 import QtGui
import requests
import time
import json
import sys
import re

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

def warning(self, warning_message):
    QtGui.QMessageBox.warning(
        self, 
        'Error', 
        warning_message
    )

class Login(QtGui.QDialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.textEmail = QtGui.QLineEdit(self)
        self.textPass = QtGui.QLineEdit(self)
        self.textPass2 = QtGui.QLineEdit(self)
        self.buttonLogin = QtGui.QPushButton('Sign in', self)

        self.label_username =  QtGui.QLabel(self)
        self.label_password =  QtGui.QLabel(self)
        self.label_password2 =  QtGui.QLabel(self)

        self.textPass.setEchoMode(QtGui.QLineEdit.Password)
        self.textPass2.setEchoMode(QtGui.QLineEdit.Password)
        self.buttonLogin.clicked.connect(self.handleLogin)

        self.label_username.setText('Email')
        self.label_password.setText('Password')
        self.label_password2.setText('Repeat password')
        self.setWindowTitle('RawBox')
        
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(self.label_username)
        layout.addWidget(self.textEmail)
        layout.addWidget(self.label_password)
        layout.addWidget(self.textPass)
        layout.addWidget(self.label_password2)
        layout.addWidget(self.textPass2)
        layout.addWidget(self.buttonLogin)

    def handleLogin(self):
        email, password, psw2 = str(self.textEmail.text()), str(self.textPass.text()), str(self.textPass2.text())
        email_regex = re.compile('[^@]+@[^@]+\.[^@]+')
        if not email_regex.match(email):
            warning(self, 'Email not valid')
            return
        if len(password) < 7 or len(password) > 19:
            warning(self, 'password to short or to long (min 8 max 20)')
            return
        if password != psw2:
            warning(self, 'password mismatch')
            return

        if create_user(email, password):
            with open('temp_conf.conf','wb') as f:
                json.dump({'username': email, 'password': password}, f)

            QtGui.QMessageBox.information(
                self,
                'Success',
                'User Created, we have create a RawBox folder under your home, enjoy! :)'
            )
            self.accept()
        else:
             warning(self, 'User already exists')


class Window(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)

app = QtGui.QApplication(sys.argv)