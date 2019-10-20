import asyncio
import aioconsole
import websockets

SLEEPTIME = 3
COLOR_URI = "ws://connect.websocket.in/QAgctMbspTnTJT4FIDLd?room_id=UQ9ce3vekLLNIG0rhGX8"
ACK_URI = "ws://connect.websocket.in/QAgctMbspTnTJT4FIDLd?room_id=UQ9ce3vekLLNIG0rhGX9"
lampTask = None


async def recv(my_color):
    # Waits for an incoming message
    # If it receives a message, send an ack and turns the lamp on 
    global lampTask
    async with websockets.connect(COLOR_URI) as color_websocket, websockets.connect(ACK_URI) as ack_websocket:
        while True:
            # For now, assume that data a string containing the color
            data = await color_websocket.recv()
            await ack_websocket.send("ack")
            if(dataIsValid(data)):
                if lampTask is not None and not lampTask.done():
                    lampTask.cancel()
                lampTask = asyncio.create_task(lampOn(data))


def dataIsValid(data):
    # Should eventually do more rigorous checks
    # Thing currently manages to recieve its own messages, so this filters them out
    if data == my_color:
        return False
    else:
        return True


async def lampOn(color):
    # Handles lamp color, fading, etc
    print(color, "on")
    await asyncio.sleep(3)
    print(color, "done")


async def sendColor(my_color):
    # Stop whatever's going on with the lamp currently
    # Send a color to the recipient's lamp
    # Flicker lamp
    # Wait for ack bit
    # If successful transmission, also turn lamp on
    global lampTask
    
    ackTimeout = 5

    async with websockets.connect(COLOR_URI) as color_websocket, websockets.connect(ACK_URI) as ack_websocket:
        await color_websocket.send(my_color)
        try:
            await asyncio.wait_for(ack_websocket.recv(), timeout = ackTimeout)
        except asyncio.TimeoutError:
            print("ack timeout")
        # In future, implement loop if failure here
        if lampTask is not None and not lampTask.done():
            lampTask.cancel()
        lampTask = asyncio.create_task(lampOn(my_color))


async def flickerLamp():
    # Call to indicate an attempted message send
    # Probably assume that whatever called it has already told the lamp to stop what it's doing?
    # Could also confirm this?
    pass


async def readSensor(my_color):
    # Will eventually read a sensor
    # For now, let it read from the command line
    while True:
        await aioconsole.ainput("Poke?")
        asyncio.create_task(sendColor(my_color))

async def main(my_color):
    await asyncio.gather(recv(my_color), readSensor(my_color))


if __name__ == '__main__':
    my_color = input("color: ")
    asyncio.run(main(my_color))
    print("loop complete")