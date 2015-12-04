#!/usr/bin/env python3

import sys

#from PyQt5.QtWidgets import QApplication, QInputDialog, QLineEdit

from PyQt5.QtWidgets import QApplication, QInputDialog


def getPassword():
    text, ok = QInputDialog.getText(None, "Attention", "Password?", QLineEdit.Password)
    if ok and text:
        print("password=%s" % text)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    getPassword()
