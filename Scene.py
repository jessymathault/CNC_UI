import tkinter as tk

import matplotlib as mpl
mpl.use("TkAgg")
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import axes3d, Axes3D
import matplotlib.pyplot as plt
import numpy as np

from CNCController import CNCController


class Scene(tk.Frame):
    CNC_TABLE_LENGTH = 630
    CNC_TABLE_WIDTH = 380
    CNC_TABLE_HEIGHT = 180

    def __init__(self, parent, root, ctrl, *args, **kwargs):
        tk.Frame.__init__(self, parent)

        self.root = root
        self.ctrl = ctrl
        self.drawCNCPath = True
        self.draw3D = True

        self.fig = plt.figure(figsize=(8, 10), dpi=50, facecolor='#636363', edgecolor='r')

        self.actualAxis = self.fig.gca(projection='3d')
        self.xActual = [0]
        self.yActual = [0]
        self.zActual = [0]

        self.expectedAxis = self.fig.gca(projection='3d')
        self.xExpected = [0]
        self.yExpected = [0]
        self.zExpected = [0]

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.canvas._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.root.after(500, self.updateActualPath)
        self.root.after(1000, self.updateScene)

    def clearExpectedPath(self):
        self.xExpected = [0]
        self.yExpected = [0]
        self.zExpected = [0]

    def updateExpectedPath(self, newX, newY, newZ):
        self.xExpected.append(newX) if newX is not None else self.xExpected.append(self.xExpected[-1])
        self.yExpected.append(newY) if newY is not None else self.yExpected.append(self.yExpected[-1])
        self.zExpected.append(newZ) if newZ is not None else self.zExpected.append(self.zExpected[-1])

    def clearActualdPath(self):
        self.xActual = [0]
        self.yActual = [0]
        self.zActual = [0]

    def updateActualPath(self):
        if self.drawCNCPath:
            self.xActual.append(self.ctrl.xPosition/CNCController.MILLIMETERS_TO_TICKS)
            self.yActual.append(self.ctrl.yPosition/CNCController.MILLIMETERS_TO_TICKS)
            self.zActual.append(self.ctrl.zPosition/CNCController.MILLIMETERS_TO_TICKS)
        self.root.after(1000, self.updateActualPath)

    def setBoundaries(self):
        if self.draw3D:
            self.expectedAxis.set_xticks(np.arange(-Scene.CNC_TABLE_LENGTH/2, (Scene.CNC_TABLE_LENGTH+1)/2, Scene.CNC_TABLE_LENGTH/5))
            self.expectedAxis.set_yticks(np.arange(-Scene.CNC_TABLE_WIDTH/2, (Scene.CNC_TABLE_WIDTH+1)/2, Scene.CNC_TABLE_WIDTH/5))
            self.expectedAxis.set_zticks(np.arange(-Scene.CNC_TABLE_HEIGHT/2, (Scene.CNC_TABLE_HEIGHT+1)/2, Scene.CNC_TABLE_HEIGHT/5))
        else:
            self.expectedAxis.set_xticks(np.arange(-Scene.CNC_TABLE_LENGTH/2, (Scene.CNC_TABLE_LENGTH+1)/2, Scene.CNC_TABLE_LENGTH/5))
            self.expectedAxis.set_yticks(np.arange(-Scene.CNC_TABLE_WIDTH/2, (Scene.CNC_TABLE_WIDTH+1)/2, Scene.CNC_TABLE_WIDTH/5))

        if self.draw3D:
            self.expectedAxis.set_xlim(-Scene.CNC_TABLE_LENGTH/2, (Scene.CNC_TABLE_LENGTH+1)/2)
            self.expectedAxis.set_ylim(-Scene.CNC_TABLE_WIDTH/2, (Scene.CNC_TABLE_WIDTH+1)/2)
            self.expectedAxis.set_zlim(-Scene.CNC_TABLE_HEIGHT/2, (Scene.CNC_TABLE_HEIGHT+1)/2)
        else:
            self.expectedAxis.set_xlim(-Scene.CNC_TABLE_LENGTH/2, (Scene.CNC_TABLE_LENGTH+1)/2)
            self.expectedAxis.set_ylim(-Scene.CNC_TABLE_WIDTH/2, (Scene.CNC_TABLE_WIDTH+1)/2)

    def updateScene(self):
        if self.draw3D:
            self.actualAxis.clear()
            self.actualAxis.plot(self.xActual, self.yActual, self.zActual)
            self.expectedAxis.clear()
            self.expectedAxis.plot(self.xExpected, self.yExpected, self.zExpected)
        else:
            self.actualAxis.clear()
            self.actualAxis.plot(self.xActual, self.yActual)
            self.expectedAxis.clear()
            self.expectedAxis.plot(self.xExpected, self.yExpected)

        self.setBoundaries()
        self.canvas.draw()

        self.root.after(1000, self.updateScene)

    def set3D(self):
        self.draw3D = True
        plt.clf()
        self.expectedAxis = self.fig.gca(projection='3d')
        self.actualAxis = self.fig.gca(projection='3d')

    def set2D(self):
        self.draw3D = False
        plt.clf()
        self.expectedAxis = self.fig.gca()
        self.actualAxis = self.fig.gca()
