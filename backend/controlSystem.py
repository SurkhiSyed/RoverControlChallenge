import pygame
import asyncio
import time
import json
import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((socket.gethostname(), 1234))
s.listen(5)  # Set the socket to listen for incoming connections

# Initialize Pygame and the joystick module
pygame.init()
pygame.joystick.init()

# Check if any joystick is connected
if pygame.joystick.get_count() == 0:
    print("No joystick detected. Please connect a controller.")
else:
    joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
    # Initialize each joystick
    for joystick in joysticks:
        joystick.init()
        print(f"Initialized joystick: {joystick.get_name()}")

# Wheel Movement Function
def wheelMovement(left_wheels_speed, right_wheels_speed):
    rightWheelSpeed1, rightWheelSpeed2, rightWheelSpeed3 = - round(right_wheels_speed) + 128, - round(right_wheels_speed) + 128, - round(right_wheels_speed) + 128
    leftWheelSpeed1, leftWheelSpeed2, leftWheelSpeed3 = - round(left_wheels_speed) + 128, - round(left_wheels_speed) + 128, - round(left_wheels_speed) + 128
    
    print(f"Left Wheels: {left_wheels_speed}, Right Wheels: {right_wheels_speed}")
    print(f"D_{rightWheelSpeed1}_{rightWheelSpeed2}_{rightWheelSpeed3}_{leftWheelSpeed1}_{leftWheelSpeed2}_{leftWheelSpeed3}")

    data = {
        "left_wheels": [leftWheelSpeed1],
        "right_wheels": [rightWheelSpeed1],
    }
    return data

# Arm Movement Function
def armMovement(gantry, elbow, left_x, left_y, right_x, right_y):
    print(f"Gantry: {gantry}, Elbow: {elbow}, Left Stick: ({left_x}, {left_y}), Right Stick: ({right_x}, {right_y})")
    print(f"A_{elbow}_N_N_N_{gantry}_N)")

    data = {
        "gantry": gantry,
        "elbow": elbow,
        "left_stick": [left_x, left_y],
        "right_stick": [right_x, right_y],
        "left_wheels": [128],
        "right_wheels": [128]
    }
    return data

DEAD_ZONE = 0.05

def send_wheel_data():
    prev_left_wheels_speed = 0
    prev_right_wheels_speed = 0
    gantry = 0
    elbow = 0
    in_wheel_mode = True  # Start in wheel mode

    running = True

    while running:
        clientSocket, address = s.accept()
        print(f"Connection from {address} has been established!")
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        try:
            if pygame.joystick.get_count() > 0:  # If joystick is connected
                joystick = pygame.joystick.Joystick(0)

                # Check button input to switch between wheel and arm mode (example: button 0)
                if joystick.get_button(0):
                    in_wheel_mode = not in_wheel_mode  # Toggle between wheel and arm mode
                    print(f"Mode switched to: {'Wheel Mode' if in_wheel_mode else 'Arm Mode'}")

                if in_wheel_mode:
                    # Get joystick input for wheel mode
                    left_wheels_speed = joystick.get_axis(1) * 128
                    right_wheels_speed = joystick.get_axis(3) * 128

                    if abs(left_wheels_speed) < DEAD_ZONE * 128:
                        left_wheels_speed = 0
                    if abs(right_wheels_speed) < DEAD_ZONE * 128:
                        right_wheels_speed = 0

                    # Only send wheel data if the joystick input has changed
                    if left_wheels_speed != prev_left_wheels_speed or right_wheels_speed != prev_right_wheels_speed:
                        wheelSpeed_data = wheelMovement(left_wheels_speed, right_wheels_speed)

                        prev_left_wheels_speed = left_wheels_speed
                        prev_right_wheels_speed = right_wheels_speed
                    
                    clientSocket.send(bytes(json.dumps(wheelSpeed_data), "utf-8"))

                else:
                    # Arm Mode
                    left_x = joystick.get_axis(0) * 128
                    left_y = joystick.get_axis(1) * 128
                    right_x = joystick.get_axis(2) * 128
                    right_y = joystick.get_axis(3) * 128

                    # Button inputs to toggle gantry and elbow values
                    if joystick.get_button(1):  # Button 1 to toggle gantry between 0 and 255
                        gantry = 0 if gantry == 255 else 255
                        print(f"Gantry toggled to: {gantry}")
                        time.sleep(0.3)  # Small delay to prevent multiple toggles

                    if joystick.get_button(2):  # Button 2 to toggle elbow between 0 and 255
                        elbow = 0 if elbow == 255 else 255
                        print(f"Elbow toggled to: {elbow}")
                        time.sleep(0.3)  # Small delay to prevent multiple toggles

                    arm_data = armMovement(gantry, elbow, left_x, left_y, right_x, right_y)
                    clientSocket.send(bytes(json.dumps(arm_data), "utf-8"))

            else:
                print("No joystick connected.")
                                

        except pygame.error as e:
            print(f"Joystick error: {e}")
            clientSocket.send(bytes(json.dumps({
                "left_wheels": [20],
                "right_wheels": [20]
            }), "utf-8"))
            break

    clientSocket.close()

if __name__ == "__main__":
    send_wheel_data()
    pygame.quit()