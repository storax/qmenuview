from PySide import QtGui
import qmenuview

app = QtGui.QApplication([])

view = qmenuview.MenuView('RootMenuTitle')

# create a model
m = QtGui.QStandardItemModel()
for i in range(10):
    m.appendRow(QtGui.QStandardItem("Delicious dish no. %s" % i))

view.model = m  # now the submenus are created

# insert new menus
m.appendRow(QtGui.QStandardItem("New fancy dish"))
# the view will also handle trees
rootitem = QtGui.QStandardItem("root")
lvl1item = QtGui.QStandardItem("Level 1")
lvl2item = QtGui.QStandardItem("Level 2")
rootitem.appendRow(lvl1item)
lvl1item.appendRow(lvl2item)
m.appendRow(rootitem)

# remove menus
m.removeRow(0)

# Menus are automatically updated
rootitem.setText("Newroot")

view.show()

app.exec_()
