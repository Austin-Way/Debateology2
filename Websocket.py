import asyncio
import websockets
import uuid

# Dictionary to store user information (user ID and username) for each WebSocket connection
connected_users = {}

async def chat_server(websocket, path):
    # Generate a unique user ID for the new connection
    user_id = str(uuid.uuid4())
    
    # Add the new connection to the connected_users dictionary
    connected_users[websocket] = {'user_id': user_id, 'username': f'User {user_id}'}

    try:
        # Send the user ID to the connected client
        await websocket.send(f"{{'type': 'userId', 'data': '{user_id}'}}")

        # Listen for messages from the client
        async for message in websocket:
            data = message.strip()

            # Check if the message is for changing the username
            if data.startswith("{'type': 'changeUsername', 'username':"):
                new_username = eval(data)['username']
                connected_users[websocket]['username'] = new_username

                # Broadcast the updated username to all connected clients
                for conn, user_info in connected_users.items():
                    await conn.send(f"{{'type': 'updateUsername', 'userId': '{user_info['user_id']}', 'username': '{new_username}'}}")
            else:
                # Broadcast the received message to all connected clients
                for conn in connected_users.keys():
                    if conn != websocket:
                        await conn.send(message)
    finally:
        # Remove the connection from the connected_users dictionary when the connection is closed
        del connected_users[websocket]

# Start the WebSocket server
start_server = websockets.serve(chat_server, "localhost", 9600)

# Run the event loop
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
