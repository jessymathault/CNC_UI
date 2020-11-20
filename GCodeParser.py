import re

supportedCommands = [-1, 0, 1, 2, 3, 4, 20, 21, 28, 90, 91, 92]

lastCommand = 20

def verifyCommand(command):
    #Check if the command is empty
    color = "#ffffff"
    arguments = {}

    if not command:
        color = "#ffffff"

    if command == '\n':
        color = "#ffffff"
        return color, arguments

    #Check if its a comment
    if command[0] == "(":
        color = "#3398db"
        return color, arguments

    if command[0] == ";":
        color = "#3398db"
        return color, arguments

    if command[0] == "%":
        color = "#3398db"
        return color, arguments

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
        if "S" in arguments:
            color = "yellow"
            return color, arguments
        if "M" in arguments:
            color = "yellow"
            return color, arguments

        global lastCommand
        arguments.update({"G": lastCommand})

    #Check if the command is supported
    if int(arguments["G"]) not in supportedCommands:
        color = "yellow"

    #Check if the arguments are valid
    try:
        if int(arguments["G"]) == 0 or int(arguments["G"]) == 1 or int(arguments["G"]) == 28 or int(arguments["G"]) == 92:
            for key, value in enumerate(arguments):
                if key != "X" and key != "Y" and key != "Z" and key != "F" and key != "G":
                    color = "#e7463b"

        elif int(arguments["G"]) == 2 or int(arguments["G"]) == 3:
            for key, value in enumerate(arguments):
                if key != "X" and key != "Y" and key != "I" and key != "J" and key != "F" and key != "G":
                    color = "#e7463b"

        elif int(arguments["G"]) == 4:
            for key, value in enumerate(arguments):
                if key != "S" and key != "P" and key != "G":
                    color = "#e7463b"

        elif int(arguments["G"]) == 20 or int(arguments["G"]) == 21 or int(arguments["G"]) == 90 or int(arguments["G"]) == 91:
            if len(arguments) != 1:
                color = "#e7463b"

    except KeyError as e:
       return "#e7463b"

    lastCommand = int(arguments["G"])
    return "#2dcc71", arguments
