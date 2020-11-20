#!/usr/bin/python
# -*- coding: utf-8 -*-

import serial
import time
import logging
import re
from math import sqrt, atan2


class CNCController(object):
    BAUD_RATE = 115200
    COM_PORT = '/dev/ttyACM0'

    MILLIMETERS_TO_TICKS = 8/1.2*0.96
    INCHES_TO_TICKS = MILLIMETERS_TO_TICKS * 25.4
    MM_PER_MIN_TO_TICKS_PER_SEC = 1/60/156

    STATE_IDLE = 0
    STATE_BUSY = 1
    STATE_ERROR = 2

    COMMANDSENT = 0

    def __init__(self, root):
        self.root = root

        self.xPosition = 0
        self.yPosition = 0
        self.zPosition = 0
        self.speed = 0.05
        self.state = CNCController.STATE_IDLE

        self.useAbsolutePositioning = True
        self.useMillimeters = True

        self.lastCommand = 0
        self.commandQueue = []
        self.autoPlay = False

        try:
            self.ser = serial.Serial(CNCController.COM_PORT, CNCController.BAUD_RATE, timeout=1)
        except serial.serialutil.SerialException as e:
            print(e)

        self.root.after(100, self.updateInfo)

    def configurePorts(self):
            try:
                self.ser.close()
                self.ser.open()
                time.sleep(1) #Arduino soft-reboot when opening a port, giving it a bit of time
                self.ser.baudrate = 115200
                logging.info("Establishing connection with the controller... [OK]")
            except AttributeError as e:
                logging.info("Establishing connection with the controller... [FAILED]")

    def sendCommand(self, command):
        arguments = self.buildCommandFromGCode(command)

        #Test pour savoir si l'on envoi la commande
        xTooSmall = 0
        yTooSmall = 0
        zTooSmall = 0
        filteredAction = 0
        minStep = 2

        if not arguments:
            return 2#It was a configuration command no need to send data
        gCodeCommand = command
        command = []

        #Add header
        command.append(255)

        #Add arguments
        if not "action" in arguments:
            logging.error("Invalid command passed the parser, should never happen")
        command.append(arguments["action"])

        if arguments["action"] == 0 or arguments["action"] == 1 :
            filteredAction = 1

        xPos = arguments["xTarget"] if "xTarget" in arguments else self.xPosition
        command.append(int(xPos))
        if abs(xPos-self.xPosition)<minStep:
            xTooSmall = 1


        yPos = arguments["yTarget"] if "yTarget" in arguments else self.yPosition
        command.append(int(yPos))
        if abs(yPos-self.yPosition)<minStep:
            yTooSmall = 1

        zPos = arguments["zTarget"] if "zTarget" in arguments else self.zPosition
        command.append(int(zPos))
        if abs(zPos-self.zPosition)<minStep:
            zTooSmall = 1

        speed = arguments["speed"] if "speed" in arguments else self.speed
        self.speed = speed
        command.append(round(speed,4))

        radius = arguments["radius"] if "radius" in arguments else float(0)
        command.append(radius)

        startAngle = arguments["startAngle"] if "startAngle" in arguments else float(0)
        command.append(startAngle)

        finishAngle = arguments["finishAngle"] if "finishAngle" in arguments else float(0)
        command.append(finishAngle)

        milliseconds = arguments["milliseconds"] if "milliseconds" in arguments else 0
        command.append(milliseconds)

        #Add footer
        command.append(254)

        #Send the command to the Arduino
        if xTooSmall and yTooSmall and zTooSmall and filteredAction:
            logging.info("Sending command: " + str(command))
            logging.info("NOT SENT : "+gCodeCommand[:-1]+" - Command too small")
            return 1
        else:
            logging.info("Sending command: " + str(command))
            logging.info("Sent : "+gCodeCommand)
            u = ""
            for x in command:
                u += str(x) + " "

            self.ser.write(u[:-1].encode())
            return 0


    def buildCommandFromGCode(self, command):
        parsedArguments = {}

        if not command:
            return parsedArguments

        #Remove end of line comments
        command = command.split("(", 1)[0]
        command = command.split(";", 1)[0]
        command = command.split("%", 1)[0]

        #Parce the command to create a dict with the arguments
        splitted = re.split('([A-Z]+)', command)
        splitted.pop(0)
        letters, values = splitted[::2], splitted[1::2]

        arguments = dict(zip(letters, values))

        #Remove line number
        if "N" in arguments:
            arguments.pop("N")

        #If there is no G its new arguments for the same previous command
        if not "G" in arguments:
            arguments.update({"G": self.lastCommand})
        self.lastCommand = int(arguments["G"])

        parsedArguments.update({"action": int(arguments["G"])})

        #Check if its a configuration command with no CNC movement
        if int(arguments["G"]) == 20:
            self.useMillimeters = False
            return {}
        elif int(arguments["G"]) == 21:
            self.useMillimeters = True
            return {}
        elif int(arguments["G"]) == 90:
            self.useAbsolutePositioning = True
            return {}
        elif int(arguments["G"]) == 91:
            self.useAbsolutePositioning = False
            return {}

        if int(arguments["G"]) == 0 or int(arguments["G"]) == 1:
            if "X" in arguments:
                x = float(arguments["X"])
                x *= CNCController.MILLIMETERS_TO_TICKS if self.useMillimeters else CNCController.INCHES_TO_TICKS
                x += self.xPosition if not self.useAbsolutePositioning else 0
                parsedArguments.update({"xTarget": int(x)})

            if "Y" in arguments:
                y = float(arguments["Y"])
                y *= CNCController.MILLIMETERS_TO_TICKS if self.useMillimeters else CNCController.INCHES_TO_TICKS
                y += self.yPosition if not self.useAbsolutePositioning else 0
                parsedArguments.update({"yTarget": int(y)})

            if "Z" in arguments:
                z = float(arguments["Z"])
                z *= CNCController.MILLIMETERS_TO_TICKS if self.useMillimeters else CNCController.INCHES_TO_TICKS
                z += self.zPosition if not self.useAbsolutePositioning else 0
                parsedArguments.update({"zTarget": int(z)})

            if "F" in arguments:
                f = float(arguments["F"])
                f *= CNCController.MM_PER_MIN_TO_TICKS_PER_SEC
                parsedArguments.update({"speed": f})

        elif int(arguments["G"]) == 2 or int(arguments["G"]) == 3:
            if "F" in arguments:
                f = float(arguments["F"])
                f *= CNCController.MM_PER_MIN_TO_TICKS_PER_SEC
                parsedArguments.update({"speed": f})

            xi = self.xPosition
            yi = self.yPosition

            xf = float(arguments["X"])
            xf *= CNCController.MILLIMETERS_TO_TICKS if self.useMillimeters else CNCController.INCHES_TO_TICKS
            xf += self.xPosition if not self.useAbsolutePositioning else 0

            yf = float(arguments["Y"])
            yf *= CNCController.MILLIMETERS_TO_TICKS if self.useMillimeters else CNCController.INCHES_TO_TICKS
            yf += self.yPosition if not self.useAbsolutePositioning else 0

            i = float(arguments["I"])
            i *= CNCController.MILLIMETERS_TO_TICKS if self.useMillimeters else CNCController.INCHES_TO_TICKS
            i += self.xPosition #if not self.useAbsolutePositioning else 0

            j = float(arguments["J"])
            j *= CNCController.MILLIMETERS_TO_TICKS if self.useMillimeters else CNCController.INCHES_TO_TICKS
            j += self.yPosition #if not self.useAbsolutePositioning else 0

            xip = xi - i
            xfp = xf - i
            yip = yi - j
            yfp = yf - j

            radius = sqrt(xfp**2 + yfp**2)
            radius = round(radius, 1)
            parsedArguments.update({"radius": float(radius)})

            thetai = atan2(yip, xip)
            if thetai < 0:
                thetai += 2*3.14159

            thetaf = atan2(yfp, xfp)
            if thetaf < 0:
                thetaf += 2*3.14159

            if abs(round(xi) - round(xf)) <= 2 and abs(round(yi) - round(yf)) <= 2:
                if int(arguments["G"]) == 2:
                    thetaf = thetai - 2*3.14159 + 0.01
                if int(arguments["G"]) == 3:
                    thetaf = thetai + 2*3.14159 - 0.01
            else:
                if int(arguments["G"]) == 2:
                    if thetaf > thetai:
                        thetaf -= (2*3.14159)
                if int(arguments["G"]) == 3:
                    if thetaf < thetai:
                        thetaf += (2*3.14159)

            thetai = thetai / 3.14159 * 180
            thetaf = thetaf / 3.14159 * 180

            thetai = round(thetai, 2)
            thetaf = round(thetaf, 2)

            parsedArguments.update({"finishAngle": float(thetaf)})
            parsedArguments.update({"startAngle": float(thetai)})

        elif int(arguments["G"]) == 4:
            if "S" in arguments:
                parsedArguments.update({"milliseconds": int(arguments["S"])*1000})
            elif "P" in arguments:
                parsedArguments.update({"milliseconds": int(arguments["P"])})

        elif int(arguments["G"]) == 28:
            if "X" not in arguments and "Y" not in arguments and "Z" not in arguments:
                parsedArguments.update({"xTarget": 0})
                parsedArguments.update({"yTarget": 0})
                parsedArguments.update({"zTarget": 0})
            else:
                if "X" in arguments:
                    parsedArguments.update({"xTarget": 0})
                if "Y" in arguments:
                    parsedArguments.update({"yTarget": 0})
                if "Z" in arguments:
                    parsedArguments.update({"zTarget": 0})

        elif int(arguments["G"]) == 92:
            
            if "X" not in arguments and "Y" not in arguments and "Z" not in arguments:
                parsedArguments.update({"xTarget": 0})
                parsedArguments.update({"yTarget": 0})
                parsedArguments.update({"zTarget": 0})
            else:
                if "X" in arguments:
                    x = float(arguments["X"])
                    x *= CNCController.MILLIMETERS_TO_TICKS if self.useMillimeters else CNCController.INCHES_TO_TICKS
                    x += self.xPosition if not self.useAbsolutePositioning else 0
                    parsedArguments.update({"xTarget": int(x)})
                if "Y" in arguments:
                    y = float(arguments["Y"])
                    y *= CNCController.MILLIMETERS_TO_TICKS if self.useMillimeters else CNCController.INCHES_TO_TICKS
                    y += self.yPosition if not self.useAbsolutePositioning else 0
                    parsedArguments.update({"yTarget": int(y)})
                if "Z" in arguments:
                    z = float(arguments["Z"])
                    z *= CNCController.MILLIMETERS_TO_TICKS if self.useMillimeters else CNCController.INCHES_TO_TICKS
                    z += self.zPosition if not self.useAbsolutePositioning else 0
                    parsedArguments.update({"zTarget": int(z)})

        return parsedArguments

    def updateInfo(self):
        try:
            bytesToRead = self.ser.inWaiting()
            if bytesToRead > 0:
                try:
                    data = self.ser.read(bytesToRead)
                    data = data.decode("utf-8")
                    arguments = data.split(' ')
                    self.xPosition = int(arguments[0])
                    self.yPosition = int(arguments[1])
                    self.zPosition = int(arguments[2])
                    self.state = int(arguments[3])
                except Exception as e:
                    pass

        except AttributeError as e:
            pass
        self.root.after(100, self.updateInfo)

    def autoPlayRoutine(self):
        #logging.info([CNCController.COMMANDSENT, ' ', self.state])
        if self.autoPlay and self.state == CNCController.STATE_IDLE and CNCController.COMMANDSENT == 0:
            if self.commandQueue:
                if self.commandQueue[0][1:3] == '00' or self.commandQueue[0][1:3] == '01' or self.commandQueue[0][1:3] == '02' or self.commandQueue[0][1:3] == '03':
                    CNCController.COMMANDSENT = 1
                else :
                    logging.info('DebounceIgnored')
                    logging.info(self.commandQueue[0][1:3])
                    CNCController.COMMANDSENT = 0

                sent = self.sendCommand(self.commandQueue[0])
                self.commandQueue.pop(0)

                if sent :
                    CNCController.COMMANDSENT = 0

                
                
            else:
                self.autoPlay = False
                return
        elif self.autoPlay and self.state == CNCController.STATE_BUSY and CNCController.COMMANDSENT == 1:
            CNCController.COMMANDSENT = 0 
        if self.autoPlay :
            self.root.after(500, self.autoPlayRoutine)








