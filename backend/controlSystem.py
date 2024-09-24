import pygame
import asyncio
import websockets
import json

# Initialize Pygame and the joystick module
pygame.init()
pygame.joystick.init()

# Get the list of connected joysticks
joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

# Initialize each joystick
for joystick in joysticks:
    joystick.init()

async def wheelMovement(left_wheels_speed, right_wheels_speed):
    rightWheelSpeed1, rightWheelSpeed2, rightWheelSpeed3 = - round(right_wheels_speed) + 128, - round(right_wheels_speed) + 128, - round(right_wheels_speed) + 128
    leftWheelSpeed1, leftWheelSpeed2, leftWheelSpeed3 = - round(left_wheels_speed) + 128, - round(left_wheels_speed) + 128, - round(left_wheels_speed) + 128
    
    # Add your code to control the wheels here
    print(f"D_{rightWheelSpeed1}_{rightWheelSpeed2}_{rightWheelSpeed3}_{leftWheelSpeed1}_{leftWheelSpeed2}_{leftWheelSpeed3}")

    # Prepare data to send to frontend
    data = {
        "left_wheels": [leftWheelSpeed1],
        "right_wheels": [rightWheelSpeed1]
    }
    return data

DEAD_ZONE = 0.05

async def send_wheel_data(websocket):
    prev_left_wheels_speed = 0
    prev_right_wheels_speed = 0
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        try:
            # Get the joystick input and apply dead zone
            left_wheels_speed = pygame.joystick.Joystick(0).get_axis(1) * 128
            right_wheels_speed = pygame.joystick.Joystick(0).get_axis(3) * 128
            
            if abs(left_wheels_speed) < DEAD_ZONE * 128:
                left_wheels_speed = 0
            if abs(right_wheels_speed) < DEAD_ZONE * 128:
                right_wheels_speed = 0

            # Check if the joystick input has changed
            if left_wheels_speed != prev_left_wheels_speed or right_wheels_speed != prev_right_wheels_speed:
                wheelSpeed_data = await wheelMovement(left_wheels_speed, right_wheels_speed)
                # Send data to the frontend
                await websocket.send(json.dumps(wheelSpeed_data))

                prev_left_wheels_speed = left_wheels_speed
                prev_right_wheels_speed = right_wheels_speed
                                
            await asyncio.sleep(0.1)  # Limit the rate of data transmission

        except pygame.error:
            print("Joystick error")
            await websocket.send(json.dumps({
                "left_wheels": [20],
                "right_wheels": [20]
            }))
            break

# Start WebSocket server
async def main():
    async with websockets.serve(send_wheel_data, "0.0.0.0", 5000):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())

pygame.quit()
