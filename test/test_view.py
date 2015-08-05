from PySide import QtGui

import qmenuview


def test_title(qtbot):
    title = 'Test title'
    mv = qmenuview.MenuView(title)
    assert mv.title() == title


def test_parent(qtbot):
    p = QtGui.QWidget()
    mv = qmenuview.MenuView(parent=p)
    assert mv.parent() is p
