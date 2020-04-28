import paho.mqtt.client as mqtt #import the client1
from database_helper import DatabaseHelper
import paho.mqtt.client as mqtt
import re

database_helper = DatabaseHelper("employeerecords.db")

def show_list(args):
    return database_helper.show_list(*args)
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
client.username_pw_set(username="client", password="client")
client.connect(broker_address, port=8883) #connect to broker
print("Connected to Broker")
client.loop_start() #start the loop
print("Subscribing to topic","server/name")
client.subscribe("server/name")
commands = {
    "show_list"	:	show_list,
    "exit"	:	exit
}
while True:
    message = input("Enter a command: ")
    command_line = message
    command = re.split("[ ]+", command_line)
    chosenCommand = commands.get(command[0])
    if chosenCommand:
        print(chosenCommand(command[1:]))
        print("Publishing message to topic", "server/name")
    else:
        print("You are not authorized for this action")
    # client.publish("server/name", command)
    client.loop_stop() #stop the loop