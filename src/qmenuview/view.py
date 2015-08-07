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
        self.recursive = True
        """If True, create submenus for treemodels."""

    def get_index(self, action, column=0):
        """Return the index for the given action

        :param action: the action to query
        :type action: :class:`QtGui.QAction`
        :param column: The column of the index
        :type column: :class:`int`
        :returns: the index of the action
        :rtype: :class:`QtCore.QModelIndex`
        :rasies: None
        """
        if action == self.menuAction():
            return QtCore.QModelIndex()
        # find all parents to get their index
        parents = self._get_parents(action)
        index = QtCore.QModelIndex()
        # Move through indexes down the chain
        for a in reversed(parents):
            parent = a.parent()
            # if parent of action is its own menu, get parent of that menu.
            # We want to know which row the action is in. For that we need
            # The real parent menu.
            if parent is a.menu():
                parent = parent.parent()
            row = parent.actions().index(a)
            index = self._model.index(row, 0, index)
        parent = action.parent()
        if parent is None:
            return index
        if parent is action.menu():
            parent = parent.parent()
        row = parent.actions().index(action)
        index = self._model.index(row, column, index)
        return index

    def get_action(self, index):
        """Return the action for the given index

        :param index: the index to query
        :type index: :class:`QtCore.QModelIndex`
        :returns: the action for the given index
        :rtype: :class:`QtGui.QAction`
        :raises: None
        """
        if not index.isValid():
            return self.menuAction()
        parents = self._get_parent_indizes(index)
        menu = self
        for i in reversed(parents):
            action = menu.actions()[i.row()]
            menu = action.menu()
        if not menu:
            return None
        try:
            return menu.actions()[index.row()]
        except IndexError:
            return None

    def _get_parents(self, action):
        parents = []
        a = action
        while True:
            parent = a.parent()
            # If parent is self, then the action is the views menuAction
            # So there are no parents
            if parent is self:
                return []
            if parent and parent is a.menu():
                parent = parent.parent()
            if not isinstance(parent, QtGui.QMenu):
                # Is not part of the tree. Parent is not a menu but
                # might be None or another Widget
                return []
            # break if parent is root because we got all parents we need
            if parent is self:
                break
            # a new parent was found and we are still not at root
            # search further until we get to root
            parent = parent.menuAction()
            a = parent
            parents.append(parent)
        return parents

    def _get_parent_indizes(self, index):
        if not index.isValid() or index.model() != self._model:
            return []
        parents = []
        i = index
        while True:
            p = i.parent()
            if not p.isValid():
                break
            parents.append(p)
            i = p
        return parents

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
    def _flatten_hierarchy(model, parent=None):
        """Return a level-order list of indizes

        :param model: the model to traverse
        :type model: :class:`QtCore.QAbstractItemModel`
        :param parent: the parent index. Default is the root.
        :type parent: :class:`QtCore.QModelIndex`
        :returns: a level-order list of indizes
        :rtype: :class:`list` of :class:`QtCore.QModelIndex`
        :raises: None
        """
        indizes = []
        if parent is None:
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
        parentaction = self.get_action(index.parent())
        # Action has no menu yet. In order to create a sub action,
        # we have to convert it.
        if parentaction.menu() is None:
            self._convert_action_to_menu(parentaction)
        parent = parentaction.menu()
        beforeindex = index.sibling(index.row(), 0)
        before = self.get_action(beforeindex)
        if self.recursive and m.hasChildren(index):
            action = parent.insertMenu(before, QtGui.QMenu(str(data), parent=parent))
        else:
            action = QtGui.QAction(parent)
            action.setText(str(data))
            parent.insertAction(before, action)
        action.triggered.connect(functools.partial(self.action_triggered, action))
        action.hovered.connect(functools.partial(self.action_hovered, action))

    def _convert_action_to_menu(self, action):
        parent = action.parentWidget()
        menu = QtGui.QMenu(parent)
        action.setMenu(menu)

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
        :param checked: True if the action was in a checked state
        :type checked: :class:`bool`
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
        index = self.get_index(action)
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
        for i in range(first, last + 1):
            index = self._model.index(i, 0, parent)
            flattened = [index]
            flattened.extend(self._flatten_hierarchy(self._model, index))
            for newi in flattened:
                self._create_menu(newi)

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
