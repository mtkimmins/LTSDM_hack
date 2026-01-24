import tkinter as tk
from tkinter import ttk
import gui

#######################################
#   CONSTANTS/VARS
#######################################


#######################################
#   CLASSES/FUNC
#######################################
class Repulse:
    def __init__(self, tk_root:tk.Tk):
        self.root:tk.Tk = tk_root
        self.main_window = None
        
        #Setup first window
        #Trigger main loop

    def mainloop(self):
        while True:
            self.get_input()
            self.update()
            self.draw()
    
    def quit(self):
        pass

    def get_input(self):
        pass

    def update(self):
        pass

    def draw(self):
        pass

#######################################
#   RUNTIME
#######################################
if  __name__ == "__main__":
    root = tk.Tk()
    main = Repulse(root)
