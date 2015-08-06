import pytest
from PySide import QtGui, QtCore

import qmenuview


@pytest.fixture(scope='function', autouse=True)
def useqtbot(qtbot):
    pass


@pytest.fixture(scope='function')
def model():
    m = QtGui.QStandardItemModel()
    for i in range(10):
        m.appendRow(QtGui.QStandardItem("testrow%s" % i))
    return m


@pytest.fixture(scope='function')
def loadedview(model):
    mv = qmenuview.MenuView()
    mv.model = model
    return mv


def test_title():
    title = 'Test title'
    mv = qmenuview.MenuView(title)
    assert mv.title() == title


def test_parent():
    p = QtGui.QWidget()
    mv = qmenuview.MenuView(parent=p)
    assert mv.parent() is p


def test_set_empty_model(loadedview):
    m = QtGui.QStandardItemModel()
    loadedview.model = m
    assert loadedview.isEmpty()


def test_set_empty_model_menumap(loadedview):
    m = QtGui.QStandardItemModel()
    loadedview.model = m
    assert loadedview._menuindexmap == {loadedview: QtCore.QModelIndex(),
                                        QtCore.QModelIndex(): loadedview}


def test_set_empty_model_actionmap(loadedview):
    m = QtGui.QStandardItemModel()
    loadedview.model = m
    assert not loadedview._actionindexmap


def test_actions_created(model):
    mv = qmenuview.MenuView()
    mv.model = model
    actions = mv.actions()
    assert len(actions) == 10,\
        'There should be 10 actions for 10 items'
    for i in range(10):
        assert actions[i].text() == 'testrow%s' % i
