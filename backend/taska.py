import pygame
import asyncio
import websockets
import json

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
async def wheelMovement(left_wheels_speed, right_wheels_speed):
    rightWheelSpeed1, rightWheelSpeed2, rightWheelSpeed3 = - round(right_wheels_speed) + 128, - round(right_wheels_speed) + 128, - round(right_wheels_speed) + 128
    leftWheelSpeed1, leftWheelSpeed2, leftWheelSpeed3 = - round(left_wheels_speed) + 128, - round(left_wheels_speed) + 128, - round(left_wheels_speed) + 128
    
    print(f"Left Wheels: {left_wheels_speed}, Right Wheels: {right_wheels_speed}")
    print(f"D_{rightWheelSpeed1}_{rightWheelSpeed2}_{rightWheelSpeed3}_{leftWheelSpeed1}_{leftWheelSpeed2}_{leftWheelSpeed3}")

    '''data = {
        "left_wheels": [leftWheelSpeed1],
        "right_wheels": [rightWheelSpeed1],
        "wheel_Data": [f"D_{rightWheelSpeed1}_{rightWheelSpeed2}_{rightWheelSpeed3}_{leftWheelSpeed1}_{leftWheelSpeed2}_{leftWheelSpeed3}"]
    }'''
    
    data = f"D_{rightWheelSpeed1}_{rightWheelSpeed2}_{rightWheelSpeed3}_{leftWheelSpeed1}_{leftWheelSpeed2}_{leftWheelSpeed3}"
    
    return data

# Arm Movement Function
async def armMovement(gantry, elbow, clawRotation, clawInOrOut, claw, shoulderRotation):
    if(clawRotation != 0):
        # To make the claw go up or down
        wristleft = clawInOrOut * 128 + 128
        wristright = - (clawInOrOut * 128) + 128
    else: #If claw is moving in or out
        # To make the claw rotate left or right
        wristright = clawRotation * 128 + 128
        wristleft = clawRotation * 128 + 128
    
    #For Shoulder Rotation clockwise or counterclockwise
    shoulderRotation = shoulderRotation * 128 + 128
    #For elbow up or down
    elbow = elbow * 128 + 128
    
    print(f"Gantry: {gantry}, Elbow: {elbow}, Left Stick: ({clawInOrOut}, {clawRotation}))")
    print(f"A_{elbow}_{wristright}_{wristleft}_{claw}_{gantry}_{shoulderRotation})")

    data = (f"A_{elbow}_{wristright}_{wristleft}_{claw}_{gantry}_{shoulderRotation})")
    '''data = {
        "gantry": gantry,
        "elbow": elbow,
        "clawRotation": clawRotation, 
        "clawInOrOut": clawInOrOut,
        "claw": claw,
        "shoulder": shoulderRotation,
        "left_wheels": [128],
        "right_wheels": [128]
    }'''
    return data

DEAD_ZONE = 0.05

async def send_wheel_data(websocket):
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
    gantry_speed = 5  # Speed of elbow adjustment per loop iteration
    in_wheel_mode = True  # Start in wheel mode
    wheelSpeed_data = "D_128_128_128_128_128_128"  # Default wheel data
    arm_data = "A_128_128_128_128_128_128"  # Default arm data
    running = True
    armMovementSpeed = 5

    while running:
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
                    await asyncio.sleep(0.3)  # Small delay to prevent multiple toggles

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
                        wheelSpeed_data = await wheelMovement(left_wheels_speed, right_wheels_speed)
                        #await websocket.send(json.dumps(wheelSpeed_data))

                        prev_left_wheels_speed = left_wheels_speed
                        prev_right_wheels_speed = right_wheels_speed
                
                ###############################################################################################################
                else:
                    # Arm Mode
                    clawRotation = joystick.get_axis(0)  #For rotating the claw clockwise or counterclockwise
                    clawMovement = joystick.get_axis(1)   #For moving the claw up or down
                    shoulderRotation = joystick.get_axis(2)  #For rotating the shoulder clockwise or counterclockwise with right joystick x
                    elbowMovement = joystick.get_axis(3)  #For moving the elbow up or down with right joystick y

                    # Button inputs to toggle wrist to open or close
                    if joystick.get_button(1):  # Button 1 to toggle wrist between 0 and 255
                        claw = 0 if claw == 255 else 255
                        await asyncio.sleep(0.3)  # Small delay to prevent multiple toggles

                    # Button 2: Increase gantry towards 255 while holding
                    if joystick.get_button(2):
                        gantry = min(gantry + gantry_speed, 255)  # Increase gantry value

                    # Button 3: Decrease gantry towards 0 while holding
                    if joystick.get_button(3):
                        gantry = max(gantry - gantry_speed, 0)  # Decrease gantry value

                    # Send arm movement data if there was change in values
                    if prev_claw != claw or prev_gantry != gantry or prev_leftJoystick_x != clawRotation or prev_leftJoystick_y != clawMovement or prev_elbowMovement != elbowMovement or prev_shoulderRotation != shoulderRotation:
                        arm_data = await armMovement(gantry, elbowMovement, clawRotation, clawMovement, claw, shoulderRotation)
                        #await websocket.send(json.dumps(arm_data))
                        
                        #Update the previous values with the current values
                        prev_claw = claw
                        prev_gantry = gantry
                        prev_leftJoystick_x = clawRotation
                        prev_leftJoystick_y = clawMovement
                        prev_elbowMovement = elbowMovement
                        prev_shoulderRotation = shoulderRotation
                    
                data = {
                    #"wheel_Data": [f"0"],
                    "left_wheels": [left_wheels_speed*2],
                    "right_wheels": [right_wheels_speed*2],
                    "wheel_Data": [wheelSpeed_data],
                    "arm_data": [arm_data]
                }
                await websocket.send(json.dumps(data))


            else:
                data = {
                "wheel_Data": [f"0"],
                "left_wheels": [128*2],
                "right_wheels": [128*2]
                }
                await websocket.send(json.dumps(data))
                print("No joystick connected.")
                                
            await asyncio.sleep(0.1)  # Limit the rate of data transmission to 10 times per second

        except pygame.error as e:
            print(f"Joystick error: {e}")
            await websocket.send(json.dumps({
                "left_wheels": [20],
                "right_wheels": [20]
            }))
            break

# Start WebSocket server
async def main():
    print("WebSocket server started on ws://0.0.0.0:5000")
    async with websockets.serve(send_wheel_data, "0.0.0.0", 5000):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())

pygame.quit()
