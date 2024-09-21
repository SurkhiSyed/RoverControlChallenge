import socket
import pygame
import threading
from flask import Flask, jsonify
from flask_cors import CORS
from backend.controlSystem import roverMovement
import logging

HOST = socket.gethostbyname(socket.gethostname())
PORT = 9090
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Pygame and the joystick module
pygame.init()
pygame.joystick.init()
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
for joystick in joysticks:
    joystick.init()

server.listen(5)
DEAD_ZONE = 0.05
running = True

# Initialize previous values for joystick axes
prev_left_wheels_speed = 0
prev_right_wheels_speed = 0

# Global dictionary to hold the latest wheel speeds
wheel_speeds = {
    "left_wheels_speed": prev_left_wheels_speed,
    "right_wheels_speed": prev_right_wheels_speed
}

@app.route('/')
def index():
    return "Joystick input server is running"

@app.route('/wheel-speeds', methods=['GET'])
def get_wheel_speeds():
    # Return the current wheel speeds as JSON
    return jsonify({
        "left_wheels_speed": wheel_speeds['left_wheels_speed'],
        "right_wheels_speed": wheel_speeds['right_wheels_speed']
    })

def handle_socket_connections():
    global running
    while running:
        communication_socket, address = server.accept()
        print(f"Connected to {address}")
        message = communication_socket.recv(1024).decode('utf-8')
        print(f"Message from client is: {message}")
        communication_socket.send("Got your message! Thank you!".encode('utf-8'))
        communication_socket.close()
        print(f"Communication with {address} ended!")

def joystick_polling():
    global running
    global prev_left_wheels_speed, prev_right_wheels_speed, wheel_speeds
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update the wheel speeds by calling roverMovement
        prev_left_wheels_speed, prev_right_wheels_speed = roverMovement(
            prev_left_wheels_speed, prev_right_wheels_speed)

        # Store the updated wheel speeds in the shared dictionary
        wheel_speeds["left_wheels_speed"] = prev_left_wheels_speed
        wheel_speeds["right_wheels_speed"] = prev_right_wheels_speed

        pygame.time.delay(500)

    pygame.quit()

if __name__ == "__main__":
    # Run socket handling in a separate thread
    threading.Thread(target=handle_socket_connections).start()

    # Run joystick polling in the main thread
    joystick_polling()
