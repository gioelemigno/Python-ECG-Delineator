from PyQt5.QtWidgets import *
from PyQt5.QtCore import QSize, QPoint, Qt
from PyQt5.QtGui import QIcon



class MyProxyStyle(QProxyStyle):
    pass
    def pixelMetric(self, QStyle_PixelMetric, option=None, widget=None):

        if QStyle_PixelMetric == QStyle.PM_SmallIconSize:
            return 100
        else:
            return QProxyStyle.pixelMetric(self, QStyle_PixelMetric, option, widget)



class main(QMainWindow):
    def __init__(self):
        super().__init__()

        self.central = QWidget()

        self.toolbar = toolbar()

        self.button1 = toolbutton("icon.jpg")
        self.button2 = toolbutton("icon.jpg")
        
        self.toolbar.addWidget(self.button1)          
        self.toolbar.addWidget(self.button2)

        self.button1.clicked.connect(lambda: self.open_menu(self.button1))
        self.button2.clicked.connect(lambda: self.open_menu(self.button2))
        
        self.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolbar)

        self.setCentralWidget(self.central)
        self.resize(600,400)
        self.show()

    
    def open_menu(self, obj):
        self.menu = QMenu()
        self.menu.setStyle(MyProxyStyle())

        self.menu.addAction(QIcon("icon.jpg"), "Person")
        self.menu.addMenu("Configuration")
        self.menu.addSeparator()
        self.menu.addMenu("Profile")

        pos = self.mapToGlobal(QPoint(obj.x(), obj.y()+obj.height()))

        self.menu.exec(pos)



class toolbar(QToolBar):
    def __init__(self):
        super().__init__()

        self.setIconSize(QSize(80,80))
        self.setMinimumHeight(80)
        self.setMovable(False)



class toolbutton(QToolButton):
    def __init__(self, icon):
        super().__init__()

        self.setIcon(QIcon(icon))
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonIconOnly)



app = QApplication([])
window = main()
app.exec()
