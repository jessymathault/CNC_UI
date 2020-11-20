
import tkinter as tk
import logging

from GCodeParser import verifyCommand


class SemiAutomaticControlsFrame(tk.LabelFrame):
    def __init__(self, parent, controller, *args, **kwargs):
        self.supportedCommandsList = [["G00 - Direct linear movement", "G00 Xnn.n Ynn.n Znn. Fnn.n"],
                                      ["G01 - Controlled linear movement", "G01 Xnn.n Ynn.n Znn. Fnn.n"],
                                      ["G02 - Clockwise circular movement", "G02 Xnn.n Ynn.n Inn. Jnn.n Fnn.n"],
                                      ["G03 - Counterclockwise circular movement", "G03 Xnn.n Ynn.n Inn. Jnn.n Fnn.n"],
                                      ["G04 - Dwell", "G04 Snn.n Pnn.n"],
                                      ["G20 - Set unit to inches", "G20"],
                                      ["G21 - Set unit to millimeters", "G21"],
                                      ["G28 - Go home", "G28 X Y Z"],
                                      ["G90 - Set to absolute positioning", "G90"],
                                      ["G91 - Set to relative positioning", "G91"],
                                      ["G92 - Set position", "G92 Xnn.n Ynn.n Znn.n"]]

        tk.LabelFrame.__init__(self, parent)

        self.ctrl = controller

        self.fileLabel = tk.Label(self, text="Manual commands : ", font=("Helvetica", 12))
        self.fileLabel.grid(row=0, column=0)

        self.commandTextField = tk.Entry(self, width=80, fg="black", bg="white")
        self.commandTextField.grid(row=1, column=0, columnspan=3)

        self.browseBtn = tk.Button(self, text="Pick command", width=22, fg="#e74b3b", command=self.selectCommand)
        self.browseBtn.grid(row=2, column=0)

        self.verifyBtn = tk.Button(self, text="Verify command", width=22, fg="#2dcc71", command=self.verify)
        self.verifyBtn.grid(row=2, column=1)

        self.runBtn = tk.Button(self, text="Execute command", width=22, fg="#3398db", command=self.run)
        self.runBtn.grid(row=2, column=2)

        self.commandQuickSelectList = tk.Listbox(self, background='white', foreground='black', width=80, height=11)
        self.commandQuickSelectList.grid(row=3, column=0, columnspan=3)
        self.fillCommandQuickSelect()
        self.commandQuickSelectList.bind('<Double-1>', lambda e: self.selectCommand())

    def fillCommandQuickSelect(self):
        for i, item in enumerate(self.supportedCommandsList):
            self.commandQuickSelectList.insert(tk.END, self.supportedCommandsList[i][0])

    def selectCommand(self):
        commandIndex = self.commandQuickSelectList.curselection()
        if not commandIndex:
            return
        self.commandTextField.configure(bg="white")
        self.commandTextField.delete(0, tk.END)
        self.commandTextField.insert(0, self.supportedCommandsList[commandIndex[0]][1])

    def verify(self):
        color, args = verifyCommand(self.commandTextField.get())
        self.commandTextField.configure(bg=color)

    def run(self):
        color, args = verifyCommand(self.commandTextField.get())
        if color == "#2dcc71":
            self.ctrl.sendCommand(self.commandTextField.get())
