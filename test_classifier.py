import time
import random
import threading
# import keyboard
from pynput.keyboard import Key,Controller
# from paho.mqtt import client as mqtt_client

# broker = 'test.mosquitto.org'
# port = 1883
# topic = "2025_09_09_07_19"
# client_id = f'python-mqtt-{random.randint(0, 1000)}'
# print("client_id: "+ str(client_id ))
# client = mqtt_client.Client(client_id)
# client.connect(broker, port)

# Function for classification and sending results
def classification_worker():
    keyboard = Controller()
    while True:
        # Read sensor data and perform classification
        sensor_data = read_sensor_data()
        classification_result = classify_data(sensor_data)
        # send the result
        # Publish the result to an MQTT topic
        # lock = threading.Lock()
        # with lock:
        #         with open("commands.txt","w") as file:
        #             file.write(f"{classification_result}\n")
        #             print("Written: ", classification_result)
        if classification_result == "LEFT":
            # keyboard.release("right")
            # keyboard.press("left")
            keyboard.release(Key.left)
            keyboard.press(Key.right)
            print("left")
        elif classification_result == "RIGHT":
            keyboard.release(Key.right)
            keyboard.press(Key.left)
            print("right")
        time.sleep(0.5)  # Adjust the delay as needed

def read_sensor_data():
    # Generate a random integer (0 or 1)
    return random.randint(0,1)

def classify_data(sensor_data):
    # Implement the classification logic
    if sensor_data == 0:
        return "LEFT"
    else:
        return "RIGHT"

if __name__ == "__main__":
    # writer_thread = threading.Thread(target=classification_worker)
    # writer_thread.start()
    classification_worker()