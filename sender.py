# import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt

client = mqtt.Client()
while True:
    message = input("Enter your command: ")
    # publish.single("record/employee", message, hostname="hakangenc")
    client.publish("record/employee", message)