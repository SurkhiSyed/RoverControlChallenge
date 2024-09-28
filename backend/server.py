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

async def wheelMovement(left_wheels_speed, right_wheels_speed):
    rightWheelSpeed1, rightWheelSpeed2, rightWheelSpeed3 = - round(right_wheels_speed) + 128, - round(right_wheels_speed) + 128, - round(right_wheels_speed) + 128
    leftWheelSpeed1, leftWheelSpeed2, leftWheelSpeed3 = - round(left_wheels_speed) + 128, - round(left_wheels_speed) + 128, - round(left_wheels_speed) + 128
    
    # Print wheel speeds for debugging
    print(f"Left Wheels: {left_wheels_speed}, Right Wheels: {right_wheels_speed}")
    print(f"D_{rightWheelSpeed1}_{rightWheelSpeed2}_{rightWheelSpeed3}_{leftWheelSpeed1}_{leftWheelSpeed2}_{leftWheelSpeed3}")

    # Prepare data to send to frontend
    data = {
        "left_wheels": [leftWheelSpeed1],
        "right_wheels": [rightWheelSpeed1]
    }
    return data

async def armMovement():
    # Placeholder for arm movement
    pass

DEAD_ZONE = 0.05

async def send_wheel_data(websocket):
    #Define wheel speeds initially before input
    prev_left_wheels_speed = 0
    prev_right_wheels_speed = 0
    running = True #Activate the while loop

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        try:
            print()
            if pygame.joystick.get_count() > 0: #If joystick is connected
                # Get the joystick input and apply dead zone
                left_wheels_speed = pygame.joystick.Joystick(0).get_axis(1) * 128 #Get left joystick input
                right_wheels_speed = pygame.joystick.Joystick(0).get_axis(3) * 128 #Get right joystick input
                
                if abs(left_wheels_speed) < DEAD_ZONE * 128: #If joystick input is within dead zone
                    left_wheels_speed = 0
                if abs(right_wheels_speed) < DEAD_ZONE * 128: #If joystick input is within dead zone
                    right_wheels_speed = 0

                # Check if the joystick input has changed
                if left_wheels_speed != prev_left_wheels_speed or right_wheels_speed != prev_right_wheels_speed:
                    wheelSpeed_data = await wheelMovement(left_wheels_speed, right_wheels_speed)
                    # Send data to the frontend
                    await websocket.send(json.dumps(wheelSpeed_data))

                    # Update the previous wheel speeds
                    prev_left_wheels_speed = left_wheels_speed
                    prev_right_wheels_speed = right_wheels_speed
            else:
                print("No joystick connected.") #If no joystick is connected
                                
            await asyncio.sleep(0.1)  # Limit the rate of data transmission

            if pygame.

        except pygame.error as e:
            print(f"Joystick error: {e}") #If there is an error with the joystick connection
            await websocket.send(json.dumps({ #Test data to send to frontend
                "left_wheels": [20],
                "right_wheels": [20]
            }))
            break

# Start WebSocket server
async def main():
    print("WebSocket server started on ws://0.0.0.0:5000") #Print the server address
    async with websockets.serve(send_wheel_data, "0.0.0.0", 5000): #Start the server
        await asyncio.Future()  # Run forever

if __name__ == "__main__": #Run the main function
    asyncio.run(main()) #Run the main function

pygame.quit() #Quit Pygame
