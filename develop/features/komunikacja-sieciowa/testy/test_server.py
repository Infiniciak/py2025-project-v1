import unittest
import socket
import threading
import json
import time
import sys
import os

from server.server import NetworkServer

class TestNetworkServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.port = 50007
        cls.server = NetworkServer(port=cls.port)
        cls.server_thread = threading.Thread(target=cls.server.start, daemon=True)
        cls.server_thread.start()
        time.sleep(1)  

    @classmethod
    def tearDownClass(cls):
        cls.server.stop()
        cls.server_thread.join()

    def test_receive_valid_json(self):
        with socket.create_connection(('127.0.0.1', self.port), timeout=5) as sock:
            data = {'sensor': 'light', 'value': 300}
            message = json.dumps(data) + '\n'
            sock.sendall(message.encode('utf-8'))
            response = sock.recv(1024).decode('utf-8').strip()

            self.assertEqual(response, 'ACK')

    def test_receive_invalid_json(self):
        with socket.create_connection(('127.0.0.1', self.port), timeout=5) as sock:
            message = "{'sensor': 'light', 'value': 300"  
            sock.sendall((message + '\n').encode('utf-8'))
            response = sock.recv(1024).decode('utf-8').strip()


            self.assertTrue(response.startswith('ERROR'))

    def test_receive_empty_message(self):
        with socket.create_connection(('127.0.0.1', self.port), timeout=5) as sock:
            sock.sendall(b'\n')
            response = sock.recv(1024).decode('utf-8').strip()
            self.assertIn(response, ['ACK', 'ERROR'])

if __name__ == '__main__':
    unittest.main()