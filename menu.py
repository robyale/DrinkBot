# Class to handle menu items
class MenuItem(object):
    def __init__(self, type, name, attributes = None, visible = True):
        self.type = type
        self.name = name
        self.attributes = attributes
        self.visible = visible

# Class to handle back button
class Back(MenuItem):
    def __init__(self, name):
        MenuItem.__init__(self, "back", name)

# Class to handle menus
class Menu(MenuItem):
    def __init__(self, name, parent = None, selected = 0, attributes = None, visible = True):
        MenuItem.__init__(self, "menu", name, attributes, visible)
        self.parent = parent
        self.children = []
        self.selected = selected

    def addChild(self, child):
        self.children.append(child)

    def addBack(self):
        self.children.append(MenuItem.__init__(self, "back", "Back"))

    def next(self):
        self.selected = (self.selected + 1) % len(self.children)
        if(self.children[self.selected].visible == False):
            self.next()

    def before(self):
        self.selected = (self.selected - 1) % len(self.children)
        if(self.children[self.selected].visible == False):
            self.before()

    def setParent(self, parent):
        self.parent = parent

    def getSelected(self):
        return self.children[self.selected]

# Gives context to how all menus relate
class MenuContext(object):
    def __init__(self, menu, delegate):
        self.topLevelMenu = menu
        self.currentMenu = menu
        self.delegate = delegate
        self.delegate.displayMenuItem(menu)

    def setMenu(self, menu):
        if(len(menu.children) == 0):
            raise ValueError("Cannot setMenu on a menu with no options")
        self.topLevelMenu = menu
        self.currentMenu = menu
        self.delegate.displayMenuItem(menu)

    def select(self):
        selection = self.currentMenu.getSelected()
        if(not self.delegate.menuItemClicked(selection)):
            if (selection.type is "menu"):
                self.setMenu(selection)
            elif (selection.type is "back"):
                if (not self.currentMenu.parent):
                    raise ValueError("Cannot navigate back when parent is None")
                self.setMenu(self.currentMenu.parent)

# Delegates certain menu actions to main.py
class MenuDelegate(object):
	def menuItemClicked(self, menuItem):
		"""
		Called when a menu item is selected. Useful for taking action on a menu item click.
		"""
		raise NotImplementedError

	def displayMenuItem(self, menuItem):
		"""
		Called when the menu item should be displayed.
		"""
		raise NotImplementedError