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
        self.recursive = False
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
        self._delete_menus()
        self._create_menus()

    def _delete_menus(self, ):
        """Delete all menus

        :returns: None
        :rtype: None
        :raises: None
        """
        for action in self.actions():
            action.deleteLater()

    def _create_menus(self, ):
        """Create all menus according to the model

        :returns: None
        :rtype: None
        :raises: None
        """
        raise NotImplementedError

    def menu_destroyed(self, menu):
        """Remove the menu from the indexmap

        :param menu: The menu that got destroyed
        :type menu: :class:`QtGui.QMenu`
        :returns: None
        :rtype: None
        :raises: None
        """
        del self._menuindexmap[menu]

    def action_destroyed(self, action):
        """Remove the action from the indexmap

        :param action: The action that got destroyed
        :type action: :class:`QtGui.QMenu`
        :returns: None
        :rtype: None
        :raises: None
        """
        del self._actionindexmap[action]

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
