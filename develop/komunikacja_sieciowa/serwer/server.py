import socket
import json
import logging
from typing import Dict, Any, Optional
from threading import Thread
logging.basicConfig(level=logging.INFO)

class NetworkServer:
    def __init__(self, port: int, logger: Optional[logging.Logger] = None):
        self.port = port
        self.logger = logger or logging.getLogger(__name__)
        self.socket: Optional[socket.socket] = None
        self.running = False
        self.handlers = []

    def start(self) -> None:
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(('0.0.0.0', self.port))
        self.socket.listen(5)
        self.running = True

        self.logger.info(f"Server started on port {self.port}")

        try:
            while self.running:
                try:
                    client_socket, addr = self.socket.accept()
                    self.logger.info(f"New connection from {addr}")
                    handler = Thread(target=self._handle_client, args=(client_socket,))
                    handler.start()
                    self.handlers.append(handler)
                except socket.timeout:
                    continue
        except KeyboardInterrupt:
            self.logger.info("Server shutting down...")
        finally:
            self.stop()

    def stop(self) -> None:
        self.running = False
        if self.socket:
            self.socket.close()
        for handler in self.handlers:
            handler.join()
        self.logger.info("Server stopped")

    def _handle_client(self, client_socket: socket.socket) -> None:
        with client_socket:
            self.logger.info("Started handling client")
            buffer = b''
            while True:
                try:
                    data = client_socket.recv(1024)
                    if not data:
                        self.logger.info("Client disconnected")
                        break
                    buffer += data
                    while b'\n' in buffer:
                        message, _, buffer = buffer.partition(b'\n')
                        try:
                            decoded = json.loads(message.decode('utf-8'))
                            self._process_data(decoded)
                            client_socket.sendall(b"ACK\n")
                        except json.JSONDecodeError:
                            client_socket.sendall(b"ERROR: Invalid JSON\n")
                except (ConnectionResetError, BrokenPipeError) as e:
                    self.logger.warning(f"Connection error: {e}")
                    break
                except Exception as e:
                    self.logger.error(f"Error handling client: {e}")
                    break

    def _process_data(self, data: Dict[str, Any]) -> None:
        try:
            formatted = json.dumps(data, indent=2)
            self.logger.info(f"Received data:\n{formatted}")


        except Exception as e:
            self.logger.error(f"Data processing error: {str(e)}")

if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO)
    server = NetworkServer(port=5000)
    server.start()