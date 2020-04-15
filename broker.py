import paho.mqtt.publish as publish

while True:
    message = input("Enter your command: ")
    publish.single("record/employee", message, hostname="test.mosquitto.org")