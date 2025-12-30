# """
# mockapp/server.py

# Implements a basic WSGI server using Python's built-in modules.
# """
# import socket
# from io import BytesIO


# def run_simple(app, host='0.0.0.0', port=5000):
#     """
#     Run a simple HTTP server serving the given WSGI app.

#     Args:
#         app: WSGI application callable.
#         host: Listening address.
#         port: Listening port.
#     """
#     with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
#         sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#         sock.bind((host, port))
#         sock.listen(1)
#         print(f"* Running on http://{host}:{port}/")

#         while True:
#             client, _ = sock.accept()
#             data = client.recv(1024).decode('utf-8')
#             if not data:
#                 client.close()
#                 continue

#             # Parse request line
#             request_line, *rest = data.splitlines()
#             method, path, _ = request_line.split()

#             # Build WSGI environment
#             env = {'REQUEST_METHOD': method, 'PATH_INFO': path}
#             # Simple JSON body parsing
#             if 'Content-Length:' in data:
#                 body = data.split('\r\n\r\n')[1]
#                 import json
#                 env['json'] = json.loads(body)

#             # Capture response
#             response_body = []
#             def start_response(status, headers):
#                 nonlocal response_status, response_headers
#                 response_status = status
#                 response_headers = headers

#             result = app(env, start_response)

#             # Construct HTTP response
#             response = f"HTTP/1.1 {response_status}\r\n"
#             for name, value in response_headers:
#                 response += f"{name}: {value}\r\n"
#             response += '\r\n'
#             client.sendall(response.encode('utf-8'))
#             for chunk in result:
#                 client.sendall(chunk)
#             client.close()