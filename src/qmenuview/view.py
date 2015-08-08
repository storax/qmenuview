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
        self.text_column = 0
        """The column for the action text"""
        self.icon_column = 0
        """The column for the action icon"""
        self.icontext_column = -1
        """The column for the action icon text"""
        self.tooltip_column = -1
        """The column for the tooltip data"""
        self.checked_column = -1
        """The column for the checked data. Has to be checkable."""
        self.whatsthis_column = -1
        """The column for the whatsThis text."""
        self.statustip_column = -1
        """The column for the statustip text."""
        self._model = None

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
            # if the parent is the actions menu, we have to get
            # the menues parent. Else we get stuck on the same level.
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
        signalmap = {"modelReset": self.reset,
                     "rowsInserted": self.insert_menus,
                     "rowsAboutToBeRemoved": self.remove_menus,
                     "dataChanged": self.update_menus}
        if self._model:
            for signal, callback in signalmap.items():
                getattr(self._model, signal).disconnect(callback)
        self._model = model
        if model:
            for signal, callback in signalmap.items():
                getattr(model, signal).connect(callback)
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
        indizes = self._flatten_hierarchy(m)
        for i in indizes:
            self.create_menu_for_index(i)

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
        # for all parents, get the children
        # during the next iteration, the children become the parents
        # and are queried for children as well. Once no new children are found
        # the loop ends
        while parents:
            for parent in parents:
                for i in range(model.rowCount(parent)):
                    index = model.index(i, 0, parent)
                    indizes.append(index)
                    children.append(index)
            parents = children
            children = []
        return indizes

    def create_menu_for_index(self, index):
        m = self._model
        parentaction = self.get_action(index.parent())
        # Action has no menu yet. In order to create a sub action,
        # we have to convert it.
        if parentaction.menu() is None:
            self._convert_action_to_menu(parentaction)
        parent = parentaction.menu()
        beforeindex = index.sibling(index.row(), 0)
        before = self.get_action(beforeindex)
        if m.hasChildren(index):
            action = self.create_menu(parent)
        else:
            action = self.create_action(parent)
        parent.insertAction(before, action)
        self.set_action_data(action, index)
        action.triggered.connect(functools.partial(self.action_triggered, action))
        action.hovered.connect(functools.partial(self.action_hovered, action))

    def create_menu(self, parent):
        """Create a menu and return the menus action.

        The parent of the menu has to be set to ``parent``

        :param parent: The parent menu
        :type parent: :class:`QtGui.QMenu`
        :returns: The menu action
        :rtype: :class:`QtGui.QAction`
        :raises: None
        """
        menu = QtGui.QMenu(parent=parent)
        return menu.menuAction()

    def create_action(self, parent):
        """Create and return a new action

        The parent of the action has to be set to ``parent``

        :param parent: The parent menu
        :type parent: :class:`QtGui.QMenu`
        :returns: The created action
        :rtype: :class:`QtGui.QAction`
        :raises: None
        """
        return QtGui.QAction(parent)

    def set_action_data(self, action, index):
        """Set the data of the action for the given index

        .. Note:: The column of the index does not matter. The columns for the data
                  are specified in :data:`MenuView.text_column` and :data:`MenuView.icon_column`.

        :param action: The action to update
        :type action: :class:`QtGui.QAction`
        :param index: The index with the data
        :type index: :class:`QtCore.QModelIndex`
        :returns: None
        :rtype: None
        :raises: None
        """
        flags = index.flags()
        textdata = self.get_data(index, QtCore.Qt.DisplayRole, self.text_column)
        icondata = self.get_data(index, QtCore.Qt.DecorationRole, self.icon_column)
        icontextdata = self.get_data(index, QtCore.Qt.DisplayRole, self.icontext_column)
        tooltipdata = self.get_data(index, QtCore.Qt.ToolTipRole, self.tooltip_column)
        checkdata = self.get_data(index, QtCore.Qt.CheckStateRole, self.checked_column)
        whatsthisdata = self.get_data(index, QtCore.Qt.WhatsThisRole, self.whatsthis_column)
        statustipdata = self.get_data(index, QtCore.Qt.StatusTipRole, self.statustip_column)
        text = str(textdata)
        icon = self._process_icondata(icondata)
        icontext = str(icontextdata)
        tooltip = str(tooltipdata)
        checked = int(checkdata) if checkdata is not None else 0
        whatsthis = str(whatsthisdata)
        statustip = str(statustipdata)

        action.setEnabled(flags & QtCore.Qt.ItemIsEnabled)
        if textdata:
            action.setText(text)
        if icon:
            action.setIcon(icon)
        if icontextdata:
            action.setIconText(icontext)
        if tooltipdata:
            action.setToolTip(tooltip)
        checkedindex = index.sibling(index.row(), self.checked_column)
        checkedflags = checkedindex.flags()
        action.setCheckable(checkedflags & QtCore.Qt.ItemIsUserCheckable)
        if checkdata:
            action.setChecked(checked == QtCore.Qt.Checked)
        if whatsthisdata:
            action.setWhatsThis(whatsthis)
        if statustipdata:
            action.setStatusTip(statustip)

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
                self.create_menu_for_index(newi)

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
        parentaction = self.get_action(parent)
        parentmenu = parentaction.menu()
        for i in reversed(range(first, last + 1)):
            index = self._model.index(i, 0, parent)
            action = self.get_action(index)
            parentmenu.removeAction(action)
        # menu has no childs, only display the action
        if not parentmenu.actions():
            parentaction.setMenu(None)

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
        columns = [self.text_column, self.icon_column, self.icontext_column,
                   self.tooltip_column, self.checked_column, self.whatsthis_column,
                   self.statustip_column]
        needupdate = any([(c >= topLeft.column() and c <= bottomRight.column()) for c in columns])
        if needupdate:
            for row in range(topLeft.row(), bottomRight.row() + 1):
                index = topLeft.sibling(row, 0)
                action = self.get_action(index)
                self.set_action_data(action, index)

    @staticmethod
    def get_data(index, role, column=None):
        """Get data of the given index

        If the column is is not None and different from
        the index column, will get the data from a sibling
        index with the same row.

        :param index: The index to query for data
        :type index: :class:`QtCore.QModelIndex`
        :param role: the data role
        :type role: :data:`QtCore.Qt.ItemDataRole`
        :param column: the column of the row to query for data.
        :type column: :class:`int` | None
        :returns: The data retrieved
        :raises: None
        """
        if column and index.column() != column:
            index = index.sibling(index.row(), column)
        if index.isValid():
            return index.data(role)

    @staticmethod
    def _process_icondata(icondata):
        """Return an icon for the data of the :data:`QtCore.Qt.DecorationRole`

        :param icondata: The data from the :data:`QtCore.Qt.DecorationRole`
        :type icondata: :class:`QtGui.QIcon` | :class:`QtGui.QPixmap`
        :returns: A Icon based on the data.
        :rtype: :class:`QtGui.QIcon`
        :raises: None
        """
        if isinstance(icondata, QtGui.QIcon):
            return icondata
        if isinstance(icondata, QtGui.QPixmap):
            return QtGui.QIcon(icondata)
