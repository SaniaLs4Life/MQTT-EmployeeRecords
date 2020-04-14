import sys
import re
from activity_service import Service
import paho.mqtt.client as mqtt

service = Service("activities.db")


def start(args):
    return service.start(*args)

def stop(args):
    return service.stop()

def remover(args):
    return service.deleteAct(args)

def listactivities(args):
    return service.activities(*args)

def upd(args):
    return service.editID(*args)

def helpf(args):
    return '''HELP:\n
	\t- start [ACTIVITY]: start activity, if argument is missing then
	\t\tlast activity starts (if any). If a different activity is running
	\t\tthen this one will be stopped and the new one starts

	\t- stop: stop the current activity (if any)

	\t- list [group-by]: shows last activities grouped by \'gropu-by\'
	\t\tthat can be \'day\', \'week\' \'month\' or \'year\'

	\t- help: shows this output

	\t- exit: exits from this application. If an activity is running then
	\t\tit asks if you want to stop the current activity. You can exit from
	\t\tthe application while an activity is running and stop it at next usage.\n
				'''


def askstopifneeds():
    if service.current_activity:
        # ask to stop the current activity
        while (True):
            print('Q: do you want to stop the current activity named "' + service.current_activity + '"? [Y/N]')
            # read command
            command_line = sys.stdin.readline()

            if (command_line == "y\n" or command_line == "Y\n" or command_line == "y" or command_line == "Y"):
                print(service.stop())
                break
            elif (command_line == "n\n" or command_line == "N\n" or command_line == "n" or command_line == "N"):
                break



def exit(args):
    askstopifneeds()
    service.dispose()
    sys.exit()


def exit_immediately(args):
    service.dispose()
    sys.exit()


actions = {
    "start": start,
    "stop"	:	stop,
    "update": upd,
    "list"	:	listactivities,
    "deleteAct":   remover,
    "help"	:	helpf,
    "exit"	:	exit,
    "exit!"	:	exit_immediately
}
def on_connect(client, userData, flags, rc):
    print("Connected. Code: " + str(rc))

    client.subscribe("work/records")
def on_message(client, userData, msg):
    print(msg.topic + ": " + str(msg.payload.decode('utf-8')))
    print("Q: Commands: start [EmployeeID], stop, help, exit")

    command_line = str(msg.payload.decode('utf-8'))

    command = re.split("[ ]+", command_line)
        # print(command[0], command[1])
        # search the command
    action = actions.get(command[0])

    if action:
        print(action(command[1:]))
    else:
        print("ERROR: unknown command")




client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.connect("test.mosquitto.org", 1883, 60)

client.loop_forever()