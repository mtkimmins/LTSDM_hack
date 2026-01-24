
class Window:
    def __init__(self, position:list)->None:
        self.children:list = []
        self.components:list = []
        self.position:list = position
    
    def addChildWindow(self, child:Window)->None:
        self.children.append(child)

    def removeChildWindow(self, child:Window)->None:
        self.children.remove(child)

    def addComponent(self, component)->None:
        self.components.append(component)

    def setPosition(self, position:list)->None:
        self.position = position

    def getPosition(self)->list:
        return self.position
    



class GUI(Window):
    def __init__(self):
        super().__init__([0,0])
        self.children:list = [] #1D list that acts as a container of all child nodes

        # open window

        # close (top) window

        # quit

    def openMainWindow(self):
        # Set up window
        # Add
        # Draw
        pass

    def update(self):
        pass

    def draw(self):
        pass

    def mainloop(self):
        pass