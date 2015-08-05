import functools

from PySide import QtCore, QtGui


class MenuView(QtGui.QMenu):
    """A view that creates submenues based on a model
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
        self._menuindexmap = {self, QtCore.QModelIndex()}
        self._actionindexmap = {}
        self.recursive = False
        """If True, create submenues for treemodels."""

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
        self._model = model
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

    def _create_menues(self, ):
        """Create all menues according to the model

        :returns: None
        :rtype: None
        :raises: None
        """
        pass

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
