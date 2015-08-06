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
def treemodel():
    m = QtGui.QStandardItemModel()
    for i in range(10):
        item = QtGui.QStandardItem("testrow%s:0" % i)
        m.appendRow(item)
        for j in range(10):
            item.appendRow(QtGui.QStandardItem("testrow%s:%s" % (i, j)))
    return m


@pytest.fixture(scope='function')
def loadedview(treemodel):
    mv = qmenuview.MenuView()
    mv.model = treemodel
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
    assert loadedview.model is m
    assert loadedview.isEmpty()


def test_set_model_none(loadedview):
    loadedview.model = None
    assert loadedview.model is None
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


def test_flatten_hierarchy(treemodel):
    flatted = qmenuview.MenuView._flatten_hierarchy(treemodel)
    i = 0
    parent = QtCore.QModelIndex()
    for index in flatted[:10]:
        assert index.parent() == parent
        assert index.row() == i
        assert index.column() == 0
        i += 1
    for j in range(10):
        parent = treemodel.index(j, 0, QtCore.QModelIndex())
        for i, index in enumerate(flatted[10 * (j + 1):10 * (j + 2)]):
            assert index.parent() == parent
            assert index.row() == i
            assert index.column() == 0


def test_menus_created(loadedview):
    for i, a in enumerate(loadedview.actions()):
        assert a.text() == 'testrow%s:0' % i
        for j, ca in enumerate(a.menu().actions()):
            assert ca.text() == 'testrow%s:%s' % (i, j)


def test_menus_created_not_recursive(treemodel):
    mv = qmenuview.MenuView()
    mv.recursive = False
    mv.model = treemodel
    for i, a in enumerate(mv.actions()):
        assert a.text() == 'testrow%s:0' % i
        assert a.menu() is None


def test_menu_action_triggered(qtbot, loadedview):
    with qtbot.waitSignal(loadedview.triggered, raising=True):
        action = loadedview.actions()[0]
        action.triggered.emit()


def test_menu_action_hovered(qtbot, loadedview):
    with qtbot.waitSignal(loadedview.hovered, raising=True):
        action = loadedview.actions()[0]
        action.hovered.emit()


def test_action_triggered(qtbot, loadedview):
    with qtbot.waitSignal(loadedview.triggered, raising=True):
        action = loadedview.actions()[0].menu().actions()[0]
        action.triggered.emit()


def test_action_hovered(qtbot, loadedview):
    with qtbot.waitSignal(loadedview.hovered, raising=True):
        action = loadedview.actions()[0].menu().actions()[0]
        action.hovered.emit()


def test_insert_menus(treemodel):
    mv = qmenuview.MenuView()
    mv.model = treemodel
    item = QtGui.QStandardItem("newitem1")
    item.appendRow(QtGui.QStandardItem("newitem2"))
    parentindex = treemodel.index(2, 0, treemodel.index(2, 0))
    parent = treemodel.itemFromIndex(parentindex)
    parent.appendRow(item)
    parentmenu = mv.actions()[2].menu().actions()[2].menu()
    assert parentmenu,\
        "The parent action was not converted to a menu"
    newaction = parentmenu.actions()[0]
    assert newaction.text() == 'newitem1'
    assert newaction.menu().actions()[0].text() == 'newitem2',\
        "Did not create submenus of inserted rows."
