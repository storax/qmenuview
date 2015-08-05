from PySide import QtGui

import qmenuview


def test_title(qtbot):
    title = 'Test title'
    qmenuview.MenuView(title)
    assert qmenuview.title() == title


def test_parent(qtbot):
    p = QtGui.QWidget()
    qmenuview.MenuView(parent=p)
    assert qmenuview.parent() is p
