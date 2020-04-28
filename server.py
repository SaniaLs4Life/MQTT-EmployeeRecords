import paho.mqtt.client as mqtt #import the client1
from database_helper import DatabaseHelper
import paho.mqtt.client as mqtt
import re

username = "client"
password = "client"

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
def on_message(client, userdata, message):
    print("message received " ,str(message.payload.decode("utf-8")))
    print("message topic=",message.topic)
########################################
broker_address="hakangenc"
#broker_address="iot.eclipse.org"
print("Creating new Mosquitto Instance")
client = mqtt.Client("P1") #create new instance
client.on_message=on_message #attach function to callback
print("Connecting to Broker")
client.tls_set("ca.crt")
client.username_pw_set(username="server", password="server")
client.connect(broker_address, port=8883) #connect to broker
print("Connected to Broker")
client.loop_start() #start the loop
print("Subscribing to topic","server/name")
client.subscribe("server/name")
commands = {
    "start_record": start_record,
    "stop_record"	:	stop_record,
    "update_employee": update_employee,
    "show_list"	:	show_list,
    "delete_employee":   delete_employee,
    "exit"	:	exit
}
while True:
    message = input("Enter a command: ")
    command_line = message
    command = re.split("[ ]+", command_line)
    chosenCommand = commands.get(command[0])
    if chosenCommand:
        print(chosenCommand(command[1:]))
    else:
        print("ERROR: unknown command")
    print("Publishing message to topic", "server/name")
    # client.publish("server/name", command)
    client.loop_stop() #stop the loop