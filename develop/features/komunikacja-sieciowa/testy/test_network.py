import unittest
from unittest.mock import patch, MagicMock
import socket
import json
import time

from network.client import NetworkClient

class TestNetworkClient(unittest.TestCase):

    @patch('socket.socket')
    def test_connection_success(self, mock_socket_class):
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        client = NetworkClient(host='127.0.0.1', port=12345, retries=1)
        connected = client.connect()

        self.assertTrue(connected)
        mock_socket.connect.assert_called_with(('127.0.0.1', 12345))

    @patch('socket.socket')
    def test_connection_failure(self, mock_socket_class):
        mock_socket = MagicMock()
        mock_socket.connect.side_effect = socket.error("Connection refused")
        mock_socket_class.return_value = mock_socket

        client = NetworkClient(host='127.0.0.1', port=12345, retries=2)
        connected = client.connect()
        self.assertFalse(connected)

    @patch('socket.socket')
    def test_send_successful_ack(self, mock_socket_class):
        mock_socket = MagicMock()
        mock_socket.recv.return_value = b'ACK
'
        mock_socket.sendall = MagicMock()
        mock_socket_class.return_value = mock_socket

        client = NetworkClient(host='127.0.0.1', port=12345)
        client._connected = True
        client.socket = mock_socket

        data = {'sensor': 'temp', 'value': 23}
        result = client.send(data)

        self.assertTrue(result)
        mock_socket.sendall.assert_called()
        mock_socket.recv.assert_called()

    @patch('socket.socket')
    def test_send_no_ack(self, mock_socket_class):
        mock_socket = MagicMock()
        mock_socket.recv.return_value = b'NACK
'
        mock_socket.sendall = MagicMock()
        mock_socket_class.return_value = mock_socket

        client = NetworkClient(host='127.0.0.1', port=12345)
        client._connected = True
        client.socket = mock_socket

        data = {'sensor': 'humidity', 'value': 55}
        result = client.send(data)

        self.assertFalse(result)

    @patch('socket.socket')
    def test_serialization_error(self, mock_socket_class):
        mock_socket = MagicMock()
        mock_socket_class.return_value = mock_socket

        client = NetworkClient(host='127.0.0.1', port=12345)
        client._connected = True
        client.socket = mock_socket

        data = {'sensor': 'temp', 'value': float('nan')} 
        result = client.send(data)
        self.assertFalse(result)

    def test_close(self):
        client = NetworkClient(host='127.0.0.1', port=12345)
        mock_socket = MagicMock()
        client.socket = mock_socket
        client._connected = True

        client.close()
        mock_socket.close.assert_called()
        self.assertFalse(client._connected)

if __name__ == '__main__':
    unittest.main()