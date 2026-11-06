import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_sources import public_url,probe

class SourcesTests(unittest.TestCase):
    def test_unsafe_source_urls(self):
        for url in ['file:///etc/passwd','http://example.com','https://user:password@example.com','https://example.com:8443']:
            with self.subTest(url=url),self.assertRaises(ValueError): public_url(url)
        with patch('socket.getaddrinfo',return_value=[(2,1,6,'',('127.0.0.1',443))]):
            with self.assertRaises(ValueError): public_url('https://example.com')
    def test_network_failure_is_unknown(self):
        with patch('socket.getaddrinfo',side_effect=OSError('network failure')):
            self.assertEqual(probe('https://example.com')['status'],'unknown')
