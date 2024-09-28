#File for sending packets to server

import pygame
import json
import socket
import time

# Initialize Pygame and the joystick module
pygame.init()
pygame.joystick.init()

# Create a socket object
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(("127.0.0.1", 5000))  # Connect to the server

# Check if any joystick is connected
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
# Initialize each joystick (if any)
for joystick in joysticks:
    joystick.init()
    print(f"Initialized joystick: {joystick.get_name()}")

# Wheel Movement Function
def wheelMovement(left_wheels_speed, right_wheels_speed):
    rightWheelSpeed1, rightWheelSpeed2, rightWheelSpeed3 = - round(right_wheels_speed) + 128, - round(right_wheels_speed) + 128, - round(right_wheels_speed) + 128
    leftWheelSpeed1, leftWheelSpeed2, leftWheelSpeed3 = - round(left_wheels_speed) + 128, - round(left_wheels_speed) + 128, - round(left_wheels_speed) + 128
    
    data = f"D_{rightWheelSpeed1}_{rightWheelSpeed2}_{rightWheelSpeed3}_{leftWheelSpeed1}_{leftWheelSpeed2}_{leftWheelSpeed3}"
    return data

# Arm Movement Function
def armMovement(gantry, elbow, clawRotation, clawInOrOut, claw, shoulderRotation):
    if clawRotation != 0:
        wristleft = round(clawInOrOut * 128 + 128)
        wristright = - round((clawInOrOut * 128) + 128)
    else:
        wristright = round(clawRotation * 128 + 128)
        wristleft = round(clawRotation * 128 + 128)
    
    shoulderRotation = round(shoulderRotation * 128 + 128)
    elbow = round(elbow * 128 + 128)
    
    data = f"A_{elbow}_{wristright}_{wristleft}_{claw}_{gantry}_{shoulderRotation}"
    return data

DEAD_ZONE = 0.05

#Main file that runs all the movements
def send_wheel_data():
    prev_left_wheels_speed = 0
    prev_right_wheels_speed = 0
    gantry = 128
    claw = 0
    prev_claw = 0
    prev_gantry = 128
    prev_leftJoystick_x = 0
    prev_leftJoystick_y = 0
    prev_shoulderRotation = 0
    prev_elbowMovement = 0
    gantry_speed = 5  # Speed of gantry adjustment per loop iteration
    in_wheel_mode = True  # Start in wheel mode
    wheelSpeed_data = "D_128_128_128_128_128_128"  # Default wheel data
    arm_data = "A_128_128_128_128_128_128"  # Default arm data
    running = True
    shoulderRotation = 1
    elbowMovement = 1
    clawRotation = 1
    
    #Send data initially to the server first and then moving forward send data only when values change
    data = {
        "wheelSpeed_data": wheelSpeed_data,
        "arm_data": arm_data
    }
    client_socket.sendall(json.dumps(data).encode('utf-8')) #send data to the server via socket connection

    while running:
        data_changed = False  # Flag to track data changes
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        try:
            if pygame.joystick.get_count() > 0:  # If joystick is connected
                joystick = pygame.joystick.Joystick(0)

                # Check button input to switch between wheel and arm mode
                if joystick.get_button(0):
                    in_wheel_mode = not in_wheel_mode  # Toggle between wheel and arm mode
                    print(f"Mode switched to: {'Wheel Mode' if in_wheel_mode else 'Arm Mode'}")
                    time.sleep(0.3)  # Small delay to prevent multiple toggles

                if in_wheel_mode:
                    # Get joystick input for wheel mode
                    left_wheels_speed = joystick.get_axis(1) * 128
                    right_wheels_speed = joystick.get_axis(3) * 128

                    if abs(left_wheels_speed) < DEAD_ZONE * 128:
                        left_wheels_speed = 0
                    if abs(right_wheels_speed) < DEAD_ZONE * 128:
                        right_wheels_speed = 0

                    # Only update wheel data if the joystick input has changed
                    if left_wheels_speed != prev_left_wheels_speed or right_wheels_speed != prev_right_wheels_speed:
                        wheelSpeed_data = wheelMovement(left_wheels_speed, right_wheels_speed)
                        prev_left_wheels_speed = left_wheels_speed
                        prev_right_wheels_speed = right_wheels_speed
                        data_changed = True  # Mark that data has changed
                
                else:
                    # Arm Mode
                    clawRotation = joystick.get_axis(0)
                    clawMovement = joystick.get_axis(1)
                    shoulderRotation = joystick.get_axis(2)
                    elbowMovement = joystick.get_axis(3)

                    #To change claw open and close
                    if joystick.get_button(1):
                        claw = 0 if claw == 255 else 255
                        time.sleep(0.3)

                    #To move gantry up while button is held
                    if joystick.get_button(2):
                        gantry = min(gantry + gantry_speed, 255)

                    #To move gantry down while button is held  
                    if joystick.get_button(3):
                        gantry = max(gantry - gantry_speed, 0)

                    #To check if values changed
                    if (prev_claw != claw or prev_gantry != gantry or 
                        prev_leftJoystick_x != clawRotation or prev_leftJoystick_y != clawMovement or 
                        prev_elbowMovement != elbowMovement or prev_shoulderRotation != shoulderRotation):
                        arm_data = armMovement(gantry, elbowMovement, clawRotation, clawMovement, claw, shoulderRotation)
                        
                        prev_claw = claw
                        prev_gantry = gantry
                        prev_leftJoystick_x = clawRotation
                        prev_leftJoystick_y = clawMovement
                        prev_elbowMovement = elbowMovement
                        prev_shoulderRotation = shoulderRotation
                        data_changed = True  # Mark that data has changed

            # Send the data only if there's been a change to the terminal
            if data_changed:
                data = {
                    "wheelSpeed_data": wheelSpeed_data,
                    "arm_data": arm_data
                }
                client_socket.sendall(json.dumps(data).encode('utf-8'))
                print("Data sent to the server:", data)

            time.sleep(0.1)

        #Send default data if an error occurs
        except pygame.error as e:
            print(f"Joystick error: {e}")
            # Send default data if an error occurs
            client_socket.sendall(json.dumps({
                "wheelSpeed_data": "D_128_128_128_128_128_128",
                "arm_data": "A_128_128_128_128_128_128"
            }).encode('utf-8'))
            break

# Start the sending function
if __name__ == "__main__":
    send_wheel_data()

client_socket.close()
pygame.quit()
