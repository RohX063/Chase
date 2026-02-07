import sys
from PyQt5.QtWidgets import QApplication
from core_gui import ChaseCore3D

def main():
    app = QApplication(sys.argv)   
    window = ChaseCore3D()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()