import tkinter as tk
import tkinter.messagebox

import sys
import glob
import serial

class CNCMenu(tk.Menu):
    def __init__(self, parent, scene, *args, **kwargs):
        tk.Menu.__init__(self, parent)
        self.scene = scene

        self.add_command(label="Quit", command=parent.quit)

        portsMenu = tk.Menu(self, tearoff=0, bg="white")
        self.ports = self.serialPorts()
        for i, port in enumerate(self.ports):
            portsMenu.add_command(label=port)
        self.add_cascade(label="Ports", menu=portsMenu)

        graphic = tk.Menu(self, tearoff=0, bg="white")
        graphic.add_command(label="2D View", command=self.scene.set2D)
        graphic.add_command(label="3D View", command=self.scene.set3D)
        self.add_cascade(label="Graphic", menu=graphic)

        self.add_command(label="About", command=self.showAboutDialog)

    def showAboutDialog(self):
        tkinter.messagebox.showinfo(
            "About",
            "Program de contrôle de la CNC v1.0 beta"
        )

    def serialPorts(self):
        if sys.platform.startswith('win'):
            ports = ['COM%s' % (i + 1) for i in range(256)]
        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this excludes your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')
        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')
        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass
        return result