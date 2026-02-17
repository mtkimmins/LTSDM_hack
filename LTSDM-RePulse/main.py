import tkinter as tk
from tkinter import ttk
import a1800_codec

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
        self.root.title("LTSDM RePulse")
        self.root.geometry("800x600")
        
        
        
        
        
        #Setup first window
        #Trigger main loop
        self.mainloop()

    def mainloop(self):
        while True:
            self.get_input()
            self.update()
            self.draw()
    
    def quit(self):
        self.root.destroy()

    ###################################
    #   INPUT
    ###################################
    def get_input(self):
        pass
        self.root.bind('<Key>', self.on_key_press)
        self.root.bind('<Button-1>', self.on_mouse_click)
        self.root.bind('<Motion>', self.on_mouse_motion)

    def on_key_press(self, event):
        match event.keysym:
            case 'Escape':
                self.quit()
            case _:
                pass

    def on_mouse_click(self, event):
        pass

    def on_mouse_motion(self, event):
        pass

    ###################################
    #   UPDATE
    ###################################
    def update(self):
        pass

    ###################################
    #   DRAW
    ###################################
    def draw(self):
        pass

#######################################
#   RUNTIME
#######################################
if  __name__ == "__main__":
    root = tk.Tk()
    main = Repulse(root)
