import unittest
from unittest.mock import patch, MagicMock
from data_processing import DataProcessing
import pandas as pd
import os

class TestDataProcessing(unittest.TestCase):
    
    @patch('configparser.ConfigParser.read')
    @patch('os.path.exists', return_value=True)
    def test_init_success(self, mock_exists, mock_read):
        """Test, že se třída správně inicializuje, pokud INI existuje."""
        # Simulace dat v configu
        with patch('configparser.ConfigParser.__getitem__') as mock_item:
            mock_item.return_value = {
                'server': 'smtp.seznam.cz',
                'port': '465',
                'username': 'test@seznam.cz',
                'password': 'testpassword',
                'sender': 'test@seznam.cz',
                'recipient': 'target@test.cz'
            }
            
            processor = DataProcessing("fake_config.ini")
            self.assertEqual(processor.smtp_server, "smtp.seznam.cz")
            self.assertEqual(processor.smtp_port, 465)

if __name__ == '__main__':
    unittest.main()