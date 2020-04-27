import re
from database_helper import DatabaseHelper
import paho.mqtt.client as mqtt

database_helper = DatabaseHelper("employeerecords.db")


def start_record(args):
    return database_helper.start_record(*args)

def stop_record(args):
    return database_helper.stop_record()

def delete_employee(args):
    return database_helper.delete_employee(args)

def show_list(args):
    return database_helper.show_list(*args)

def update_employee(args):
    return database_helper.update_employee(*args)


commands = {
    "start_record": start_record,
    "stop_record"	:	stop_record,
    "update_employee": update_employee,
    "show_list"	:	show_list,
    "delete_employee":   delete_employee,
    "exit"	:	exit
}

def getCommands():
    def on_connect(client, userData, flags, rc):
        print("Connection is successful: " + str(rc))
        client.subscribe("record/employee")

    def on_message(client, userData, msg):
        print(msg.topic + ": " + str(msg.payload.decode('utf-8')))
        command_line = str(msg.payload.decode('utf-8'))
        command = re.split("[ ]+", command_line)
        chosenCommand = commands.get(command[0])
        if chosenCommand:
            print(chosenCommand(command[1:]))
        else:
            print("ERROR: unknown command")

    client = mqtt.Client()
    client.tls_set("ca.crt")
    client.username_pw_set(username="testuser", password="testuser")
    client.on_message = on_message
    client.on_connect = on_connect

    client.connect("hakangenc", 8883, 60)
    while True:
        message = input("Enter your command: ")
        client.publish("record/employee", message)
        command_line = message
        command = re.split("[ ]+", command_line)
        chosenCommand = commands.get(command[0])
        if chosenCommand:
            print(chosenCommand(command[1:]))
        else:
            print("ERROR: unknown command")

    client.loop_forever()
getCommands()