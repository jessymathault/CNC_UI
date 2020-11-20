import tkinter as tk
from CNCController import CNCController

class CNCPosition(tk.Frame):
    def __init__(self, parent, root, ctrl, *args, **kwargs):
        tk.Frame.__init__(self, parent)
        self.root = root
        self.ctrl = ctrl

        self.posLabel = tk.Label(self, text="Current position: ", font=("Helvetica", 16))
        self.posLabel.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.xLabel = tk.Label(self, text="X: 23.4 cm", font=("Helvetica", 16), fg="#e74b3b")
        self.xLabel.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.yLabel = tk.Label(self, text="Y: 32.4 cm", font=("Helvetica", 16), fg="#2dcc71")
        self.yLabel.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.zLabel = tk.Label(self, text="Z: 0.8 cm", font=("Helvetica", 16), fg="#3398db")
        self.zLabel.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)

        self.root.after(100, self.updateLabels)

    def updateLabels(self):
        self.xLabel.config(text="X: " + "{0:.2f}".format(self.ctrl.xPosition/CNCController.MILLIMETERS_TO_TICKS) + "mm")
        self.yLabel.config(text="Y: " + "{0:.2f}".format(self.ctrl.yPosition/CNCController.MILLIMETERS_TO_TICKS) + "mm")
        self.zLabel.config(text="Z: " + "{0:.2f}".format(self.ctrl.zPosition/CNCController.MILLIMETERS_TO_TICKS) + "mm")
        self.root.after(100, self.updateLabels)
