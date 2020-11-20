
#Graphical libraries
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

#Custom widgets
from CNCMenu import CNCMenu
from CNCPosition import CNCPosition
from AutomaticControlsFrame import AutomaticControlsFrame
from LoggingConsole import LoggingConsole
from Scene import Scene
from SemiAutomaticControlsFrame import SemiAutomaticControlsFrame

#Controller
from CNCController import CNCController

#Util
import logging


def onClosing():
    if messagebox.askokcancel("Quit", "Do you want to quit?"):
        root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    root.wm_title("Factoriel Pixel - CNC")
    root.geometry("%dx%d+0+0" % (root.winfo_screenwidth(), root.winfo_screenheight()))
    root.tk_setPalette(background='#303030', foreground='#636363', activeBackground='#636363', activeForeground='#636363')
    root.protocol("WM_DELETE_WINDOW", root.quit)

    controller = CNCController(root)

    photo = ImageTk.PhotoImage(Image.open("resources/FP_Banner.png"))
    banner = tk.Label(image=photo, bg="white", width=root.winfo_screenwidth())
    banner.pack()
    banner.pack()

    m1 = tk.PanedWindow(bg="#303030")
    m1.pack(fill=tk.BOTH, expand=1)

    m2 = tk.PanedWindow(m1, orient=tk.VERTICAL, bg="#303030")

    top = tk.LabelFrame(m2, text="CNC Position", font=("Helvetica", 16))

    scene = Scene(top, root, controller)
    scene.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    cncPosition = CNCPosition(top, root, controller)
    cncPosition.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

    left = tk.LabelFrame(m1, text="Controls", padx=5, pady=5, font=("Helvetica", 16))

    automaticControlFrame = AutomaticControlsFrame(left, controller, scene, padx=5, pady=5)
    automaticControlFrame.pack(fill=tk.BOTH, expand=1)

    semiAutomaticControlFrame = SemiAutomaticControlsFrame(left, controller, padx=5, pady=5)
    semiAutomaticControlFrame.pack(fill=tk.BOTH, expand=1)

    bottom = tk.LabelFrame(m2, text="Log", font=("Helvetica", 16))

    handle = LoggingConsole(tk.Text(bottom, background='black', foreground='white'))
    handle.widget.pack(fill=tk.BOTH)
    logger = logging.getLogger()
    logger.addHandler(handle)
    logger.setLevel(logging.INFO)

    menubar = CNCMenu(root, scene)
    root.config(menu=menubar)

    m2.add(top)
    m2.add(bottom)
    m1.add(left)
    m1.add(m2)

    controller.configurePorts()

    root.mainloop()