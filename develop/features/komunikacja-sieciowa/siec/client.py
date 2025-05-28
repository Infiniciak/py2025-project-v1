import socket
import json
import time
from typing import Optional, Dict, Any
import logging
from datetime import datetime


class NetworkClient:
    def __init__(
            self,
            host: str,
            port: int,
            timeout: float = 5.0,
            retries: int = 3,
            logger: Optional[logging.Logger] = None
    ):
        self.host = host
        self.port = port
        self.timeout = timeout
        self.retries = retries
        self.socket: Optional[socket.socket] = None
        self.logger = logger or logging.getLogger(__name__)
        self._connected = False

    def connect(self) -> bool:
        if self._connected:
            return True

        for attempt in range(1, self.retries + 1):
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(self.timeout)
                self.socket.connect((self.host, self.port))
                self._connected = True
                self.logger.info(f"Connected to {self.host}:{self.port}")
                return True
            except (socket.timeout, ConnectionRefusedError) as e:
                self.logger.warning(f"Connection attempt {attempt} failed: {str(e)}")
                if attempt < self.retries:
                    time.sleep(1)

        self.logger.error(f"Failed to connect after {self.retries} attempts")
        return False

    def send(self, data: Dict[str, Any]) -> bool:
        if not self._connected and not self.connect():
            return False

        serialized = self._serialize(data)
        if not serialized:
            return False

        for attempt in range(1, self.retries + 1):
            try:
                self.socket.sendall(serialized + b'\n')

                ack = self.socket.recv(1024).decode().strip()
                if ack == "ACK":
                    self.logger.info(f"Data sent and acknowledged: {data}")
                    return True
                else:
                    self.logger.warning(f"Invalid ACK received: {ack}")
            except (socket.timeout, ConnectionError) as e:
                self.logger.warning(f"Send attempt {attempt} failed: {str(e)}")
                if attempt < self.retries:
                    time.sleep(1)
                continue

        self.logger.error(f"Failed to send data after {self.retries} attempts")
        self._connected = False
        return False

    def close(self) -> None:
        if self.socket:
            try:
                self.socket.close()
                self.logger.info("Connection closed")
            except Exception as e:
                self.logger.error(f"Error closing connection: {str(e)}")
            finally:
                self.socket = None
                self._connected = False

    def _serialize(self, data: Dict[str, Any]) -> Optional[bytes]:
        try:
            if 'timestamp' not in data:
                data['timestamp'] = datetime.now().isoformat()
            return json.dumps(data).encode('utf-8')
        except (TypeError, ValueError) as e:
            self.logger.error(f"Serialization error: {str(e)}")
            return None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()