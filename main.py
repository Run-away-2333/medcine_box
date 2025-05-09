from PyQt6.QtWidgets import QApplication, QWidget
import sys


import smart_pill_box
import qrc_resources

if __name__ == '__main__':
    medicine_manage_app = QApplication(sys.argv)

    object_widget = QWidget()
    smart_pill_box_widget = smart_pill_box.MedicineBox()
    smart_pill_box_widget.setupUi(object_widget)
    object_widget.show()
    # object_widget.setWindowOpacity(0.9)

    sys.exit(medicine_manage_app.exec())
