import functools

from PySide import QtCore, QtGui

__all__ = ['MenuView']


class MenuView(QtGui.QMenu):
    """A view that creates submenus based on a model
    """

    hovered = QtCore.Signal(QtCore.QModelIndex)
    """Signal for when an action gets hovered"""
    triggered = QtCore.Signal(QtCore.QModelIndex)
    """Signal for when an action gets triggered"""

    def __init__(self, title='', parent=None):
        """Initialize a new menu view with the given title

        :param title: title of the top menu
        :type title: :class:`str`
        :param parent: the parent widget
        :type parent: :class:`QtGui.QWidget`
        :raises: None
        """
        super(MenuView, self).__init__(title, parent)
        self._model = None
        self._menuindexmap = {self: QtCore.QModelIndex(),
                              QtCore.QModelIndex(): self}
        self._actionindexmap = {}
        self.recursive = True
        """If True, create submenus for treemodels."""

    @property
    def model(self, ):
        """Get the model

        :returns: the current model
        :rtype: :class:`QtCore.QAbstractItemModel`
        :raises: None
        """
        return self._model

    @model.setter
    def model(self, model):
        """Set the model

        :param model: the model to set
        :type model: :class:`QtCore.QAbstractItemModel`
        :returns: None
        :rtype: None
        :raises: None
        """
        if self._model:
            self._model.modelReset.disconnect(self.reset)
            self._model.rowsInserted.disconnect(self.insert_menus)
            self._model.rowsMoved.disconnect(self.move_menus)
            self._model.rowsRemoved.disconnect(self.remove_menus)
            self._model.dataChanged.disconnect(self.update_menus)
        self._model = model
        if model:
            model.modelReset.connect(self.reset)
            model.rowsInserted.connect(self.insert_menus)
            model.rowsMoved.connect(self.move_menus)
            model.rowsRemoved.connect(self.remove_menus)
            model.dataChanged.connect(self.update_menus)
        self.reset()

    def reset(self, ):
        """Delete and recreate all menus

        :returns: None
        :rtype: None
        :raises: None
        """
        self.clear()
        self._create_all_menus()

    def _create_all_menus(self, ):
        """Create all menus according to the model

        :returns: None
        :rtype: None
        :raises: None
        """
        m = self._model
        if not m:
            return
        if self.recursive:
            indizes = self._flatten_hierarchy(m)
        else:
            indizes = [m.index(i, 0) for i in range(m.rowCount())]
        for i in indizes:
            self._create_menu(i)

    @staticmethod
    def _flatten_hierarchy(model):
        """Return a level-order list of indizes

        :param model: the model to traverse
        :type model: :class:`QtCore.QAbstractItemModel`
        :returns: a level-order list of indizes
        :rtype: :class:`list` of :class:`QtCore.QModelIndex`
        :raises: None
        """
        indizes = []
        parent = QtCore.QModelIndex()
        parents = [parent]
        children = []
        while parents:
            for parent in parents:
                for i in range(model.rowCount(parent)):
                    index = model.index(i, 0, parent)
                    indizes.append(index)
                    children.append(index)
            parents = children
            children = []
        return indizes

    def _create_menu(self, index):
        m = self._model
        data = index.data(QtCore.Qt.DisplayRole)
        if self.recursive and m.canFetchMore(index):
            m.fetchMore(index)
        if self.recursive and m.hasChildren(index):
            parent = self._menuindexmap[index.parent()]
            newmenu = parent.addMenu(str(data))
            action = newmenu.menuAction()
            self._menuindexmap[newmenu] = index
            self._menuindexmap[index] = newmenu
            newmenu.destroyed.connect(functools.partial(self.menu_destroyed, newmenu))
        else:
            parent = self._menuindexmap[index.parent()]
            action = parent.addAction(str(data))
            self._actionindexmap[action] = index
            self._actionindexmap[index] = action
            action.destroyed.connect(functools.partial(self.action_destroyed, action))

    def menu_destroyed(self, menu):
        """Remove the menu from the indexmap

        :param menu: The menu that got destroyed
        :type menu: :class:`QtGui.QMenu`
        :returns: None
        :rtype: None
        :raises: None
        """
        index = self._menuindexmap[menu]
        del self._menuindexmap[menu]
        del self._menuindexmap[index]

    def action_destroyed(self, action):
        """Remove the action from the indexmap

        :param action: The action that got destroyed
        :type action: :class:`QtGui.QMenu`
        :returns: None
        :rtype: None
        :raises: None
        """
        index = self._actionindexmap[action]
        del self._actionindexmap[action]
        del self._actionindexmap[index]

    def action_hovered(self, action):
        """Emit the hovered signal

        :param action: The action which emitted a hovered signal
        :type action: :class:`QtGui.QAction`
        :returns: None
        :rtype: None
        :raises: None
        """
        self._emit_signal_for_action(self.hovered, action)

    def action_triggered(self, action):
        """Emit the triggered signal

        :param action: The action which emitted a hovered signal
        :type action: :class:`QtGui.QAction`
        :returns: None
        :rtype: None
        :raises: None
        """
        self._emit_signal_for_action(self.triggered, action)

    def _emit_signal_for_action(self, signal, action):
        """Emit the given signal for the index of the given action

        :param signal: The signal to emit
        :type signal: :class:`QtCore.Signal`
        :param action: The action for which to emit the signal
        :type action: :class:`QtGui.QAction`
        :returns: None
        :rtype: None
        :raises: None
        """
        index = self._actionindexmap.get(action)
        if index and index.isValid():
            signal.emit(index)

    def insert_menus(self, parent, first, last):
        """Create menus for rows first til last under the given parent

        :param parent: The parent index
        :type parent: :class:`QtCore.QModelIndex`
        :param first: the first row
        :type first: :class:`int`
        :param last: the last row
        :type last: :class:`int`
        :returns: None
        :rtype: None
        :raises: None
        """
        raise NotImplementedError

    def move_menus(self, parent, start, end, destination, row):
        """Move menus between start and end under the given parent,
        to destination starting at the given row

        :param parent: The parent of the moved rows
        :type parent: :class:`QtCore.QModelIndex`
        :param start: the start row
        :type start: :class:`int`
        :param end: the last row
        :type end: :class:`int`
        :param destination: the parent of the destinaton
        :type destination: :class:`QtCore.QModelIndex`
        :param row: the row where the menus are moved to
        :type row: :class:`int`
        :returns: None
        :rtype: None
        :raises: None
        """
        raise NotImplementedError

    def remove_menus(self, parent, first, last):
        """Remove the menus under the given parent

        :param parent: the parent of the menus
        :type parent: :class:`QtCore.QModelIndex`
        :param first: the first row
        :type first: :class:`int`
        :param last: the last row
        :type last: :class:`int`
        :returns: None
        :rtype: None
        :raises: None
        """
        raise NotImplementedError

    def update_menus(self, topLeft, bottomRight):
        """Update the menus from topleft index to bottomright index

        :param topLeft: The top left index to update
        :type topLeft: :class:`QtCore.QModelIndex`
        :param bottomRight: the bottom right index to update
        :type bottomRight: :class:`QtCore.QModelIndex`
        :returns: None
        :rtype: None
        :raises: None
        """
        raise NotImplementedError
