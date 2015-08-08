========
Usage
========

To use QMenuView::

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


-------
Signals
-------

To handle signals connect to the views signals::

  from PySide import QtGui
  import qmenuview

  app = QtGui.QApplication([])

  view = qmenuview.MenuView('RootMenuTitle')

  # create a model
  m = QtGui.QStandardItemModel()
  for i in range(10):
      m.appendRow(QtGui.QStandardItem("Delicious dish no. %s" % i))

  view.model = m  # now the submenus are created

  def triggered_cb(index, checked=False):
       item = index.model().itemForIndex(index)
       print('Item triggered', item)
  menuview.action_triggered.connect(triggered_cb)

See :data:`qmenuview.MenuView.action_triggered`, :data:`qmenuview.MenuView.action_toggled`, :data:`qmenuview.MenuView.action_hovered`.

-------------
Customization
-------------

There are multiple things you can customize.

+++++++
Columns
+++++++

You can specify which columns of the model you want to use for the data::

  import qmenuview
  view = qmenuview.MenuView()

  view.text_column = 2  # use third column for action text
  view.icon_column = 1  # use second column for icon
  view.icontext_column = -1  # don't set the icontext

+++++++++++++++++++++
Advanced Data Control
+++++++++++++++++++++

If you want to have more control over how the data is applied to actions,
have a look at the :data:`qmenuview.MenuView.setdataargs`.
It is a list of :class:`qmenuview.view.SetDataArgs`. Each entry defines
a column and a role for the data to query, a method to convert the data and a name
of a action method to apply the data.

So you can remove or add entries to the list. The following example
will make the view query data from column 0 with :data:`PySide.QtCore.Qt.FontRole`.
There is no need to convert the data, so the convertion function is None. ``setFont``
will specify that :meth:`PySide.QtGui.QAction.setFont` will be used to apply the data::

  from PySide import QtCore
  import qmenuview
  view = qmenuview.MenuView()
  fontargs = qmenuview.SetDataArgs('setFont', 0, QtCore.Qt.FontRole, None)
  view.setdataargs.append(fontargs)

++++++++++++++
Custom classes
++++++++++++++

If you want to use custom menu or action classes subclass the view and override
:meth:`qmenuview.MenuView.create_menu` or :meth:`qmenuview.MenuView.create_action`::


  from PySide import QtGui
  import qmenuview

  class SuperAction(QtGui.QAction): pass

  class SuperMenuView(qmenuview.MenuView):
      def create_action(self, parent):
          return SuperAction(parent)
