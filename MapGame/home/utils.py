import socket
from accounts.models import UserToken
import json
from uuid import UUID
from PIL import Image
from io import BytesIO
import base64

def send_command_to_server(command, auth_token=None, host='localhost', port=50505):
    """
    Sends a command to the Phase 2 server and waits for the response.

    :param command: The command to send.
    :param host: The host address of the Phase 2 server.
    :param port: The port of the Phase 2 server.
    :return: The response from the server.
    """
    response = ''
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            
            command, *args = command.split(' ')
            token = UserToken.objects.get(token=auth_token)
            if token.player_uuid is not None:
                auth_token = token.player_uuid
            # send the command
            if args:
                command = f"{command},{auth_token},{",".join(args)}"
            else: 
                command = f"{command},{auth_token}"
            print("Sending command:", command)
            s.sendall(command.encode())
            # Wait for the response
            print("Waiting for response...")
            response = s.recv(1024*1024*10).decode()

            return response
            
    except socket.error as e:
        print(f"Socket error: {e}")
        response = 'Error: Could not connect to server.'
    finally:
        # Close the connection to the server
        s.close()


    return response

class ResponseHandler:
    color_mapping = {
        "Player": "blue",
        "Mine": "red",
        "Health": "green",
        "Freezer": "yellow"
    }
    @classmethod
    def handle_response(self,response, auth_token=None):
        """
        Handles the response from the server.
        """
        # Split only after the first ,
        # Message is json encoded
        # Convert to dict
        try:
            response = json.loads(response)
            f = response["f"]
            player_uuid = response["id"]
            objs = response["query_result"]
            image = response["image"]
            vision_x = response["vision_x"]
            vision_y = response["vision_y"]
            print(image)
            if hasattr(self,f):

                print(f"Calling {f}()")
                qr = getattr(self,f)(player_uuid=player_uuid, objs=objs, auth_token=auth_token)

                return qr,image, vision_x, vision_y
            else:
                print("No such function")

        except Exception as e:
            print("Error:", e)
            return [],None,None,None
        
    @classmethod
    def query(*args, **kwargs):
        """
        Handles the query response from the server.
        """
        # Construct a query result from the *args
        objs = kwargs.get('objs')
        query_results = []
        objlist = eval(str(objs))
        for obj in objlist:
            query_results.append((obj[0], obj[1], ResponseHandler.color_mapping[obj[2]], obj[3], obj[4]))

        # Convert query results to a format suitable for the template
        # query_results = [
        #     ('9ed2c4e8-d8b6-4a91-bc7c-dec8406dc3dc', 'Mine', 'red', 100, 150),
        #     ('07220990-6d50-4199-951f-38a676d5f94d', 'Health', 'green',150, 100)
        # ]

        # Convert query results to a format suitable for the template
        objects = [
            {"id": uuid, "name": name, "color": color, "x": x, "y": y}
            for uuid, name, color, x, y in query_results
        ]
        print("Query results:", objects)
        # Convert to json
        
        return objects

    @classmethod
    def setId(*args, **kwargs):
        """
        Sets the id of the user.
        """
        auth_token = kwargs.get('auth_token')
        player_uuid = kwargs.get('player_uuid')
        print("Setting id:",player_uuid)
        # Save the id to the database
        token = UserToken.objects.get(token=auth_token)
        token.player_uuid = player_uuid
        token.save()
        return []
