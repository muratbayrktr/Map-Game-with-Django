import socket

def login_backend(auth_token, host='127.0.0.1', port=50505):
    """
    Sends a command to the Phase 2 server and waits for the response.

    :param command: The command to send.
    :param host: The host address of the Phase 2 server.
    :param port: The port of the Phase 2 server.
    :return: The response from the server.
    """
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            # send the command
            command = f"login,{auth_token}"
            # Wait for the response
            print("Waiting for response...")
            response = s.recv(1024).decode()
            print("Received response:", response)
    except socket.error as e:
        print(f"Socket error: {e}")
        response = 'Error: Could not connect to server.'

    return response