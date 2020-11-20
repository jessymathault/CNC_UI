import tkinter as tk
import tkinter.filedialog
from PIL import Image, ImageTk

from GCodeParser import verifyCommand


class AutomaticControlsFrame(tk.LabelFrame):
    def __init__(self, parent, controller, scene, *args, **kwargs):
        self.playImage = ImageTk.PhotoImage(Image.open("resources/play.png"))
        self.pauseImage = ImageTk.PhotoImage(Image.open("resources/pause.png"))
        self.stopImage = ImageTk.PhotoImage(Image.open("resources/stop.png"))

        tk.LabelFrame.__init__(self, parent)

        self.ctrl = controller
        self.scene = scene

        self.fileLabel = tk.Label(self, text="Automatic script : ", font=("Helvetica", 12))
        self.fileLabel.grid(row=0, column=0)

        self.fileTextField = tk.Entry(self, width=80, fg="white")
        self.fileTextField.grid(row=1, column=0, columnspan=5)

        self.browseBtn = tk.Button(self, text="Chose script", width=22, fg="#e74b3b", command=self.openScript)
        self.browseBtn.grid(row=2, column=0)

        self.verifyBtn = tk.Button(self, text="Verify script", width=22, fg="#2dcc71", command=self.verifyScript)
        self.verifyBtn.grid(row=2, column=1)

        self.runBtn = tk.Button(self, image=self.playImage, fg="#3398db", command=self.runScript)
        self.runBtn.grid(row=2, column=2)
        self.pauseBtn = tk.Button(self, image=self.pauseImage, fg="#3398db", command=self.pauseScript)
        self.pauseBtn.grid(row=2, column=3)
        self.stopBtn = tk.Button(self, image=self.stopImage, fg="#3398db", command=self.stopScript)
        self.stopBtn.grid(row=2, column=4)

        self.fileEditor = tk.Text(self, background='white', foreground='black')

        self.fileEditor = tk.Listbox(self, background='white', foreground='black', width=80, height=19)
        self.fileEditor.grid(row=3, column=0, columnspan=5)

        self.fileName = ""

    def openScript(self):
        self.fileName = tkinter.filedialog.askopenfile(mode='r')
        if not self.fileName:
            return

        self.fileTextField.delete(0, tk.END)
        self.fileTextField.insert(0, self.fileName.name)
        self.fileEditor.delete(0, tk.END)
        with open(self.fileName.name) as f:
            [self.fileEditor.insert(tk.END, line) for _, line in enumerate(f)]

        self.scene.clearExpectedPath()
        self.scene.clearActualdPath()

    def saveScript(self):
        with open(self.fileName.name, 'w') as f:
            f.truncate()
            for line in self.fileEditor.get('1.0', 'end-1c').splitlines():
                if line:
                    f.write(line)
                    f.write("\n")

    def verifyScript(self):
        with open(self.fileName.name) as f:
            for i, line in enumerate(f):
                x = None
                y = None
                z = None
                color, arguments = verifyCommand(line)
                try:
                    if int(arguments["G"]) == 0 or int(arguments["G"]) == 1 or int(arguments["G"]) == 2 or int(arguments["G"]) == 3:
                        if "X" in arguments:
                            x = float(arguments["X"])
                        if "Y" in arguments:
                            y = float(arguments["Y"])
                        if "Z" in arguments:
                            z = float(arguments["Z"])
                except KeyError as e:
                    pass
                self.scene.updateExpectedPath(x, y, z)
                self.fileEditor.itemconfig(i, bg=color)

    def runScript(self):
        with open(self.fileName.name) as f:
            self.ctrl.commandQueue[:] = []
            for i, line in enumerate(f):
                color, args = verifyCommand(line)
                if color == "#2dcc71":
                    self.ctrl.commandQueue.append(line)
            self.ctrl.autoPlay = True
            self.ctrl.autoPlayRoutine()

    def pauseScript(self):
        self.ctrl.autoPlay = not self.ctrl.autoPlay
        self.scene.drawCNCPath = not self.scene.drawCNCPath

    def stopScript(self):
        self.ctrl.sendCommand("G-1")

        self.ctrl.autoPlay = False
        self.ctrl.commandQueue[:] = []
        
        self.scene.drawCNCPath = False
        self.scene.xActual[:] = []
        self.scene.yActual[:] = []
        self.scene.zActual[:] = []
