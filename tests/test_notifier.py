import unittest
from unittest.mock import patch, MagicMock
from notifier import validate_channel_name, check_stream

class TestNotifier(unittest.TestCase):

    def test_validate_channel_name_valid(self):
        """Где валидация: корректные имена (п.1)"""
        self.assertTrue(validate_channel_name("zoinkgd"))
        self.assertTrue(validate_channel_name("xQc_123"))
        self.assertTrue(validate_channel_name("a" * 25))

    def test_validate_channel_name_invalid(self):
        """Где валидация: некорректные имена (п.1)"""
        self.assertFalse(validate_channel_name("a"))          # too short
        self.assertFalse(validate_channel_name("a" * 26))     # too long
        self.assertFalse(validate_channel_name("z@oink"))     # invalid char
        self.assertFalse(validate_channel_name(" "))          # space

    @patch('requests.get')
    def test_check_stream_network_error(self, mock_get):
        """Где обработка ошибок: исключение не падает (п.2)"""
        mock_get.side_effect = Exception("Network timeout")
        known = set()
        # Не должно вызывать исключение
        check_stream("zoinkgd", known)
        self.assertEqual(len(known), 0)

    @patch('requests.get')
    def test_check_stream_empty_response(self, mock_get):
        """Где обработка ошибок: пустой JSON (п.2)"""
        mock_get.return_value.json.return_value = {"data": []}
        mock_get.return_value.status_code = 200
        known = set()
        check_stream("zoinkgd", known)
        self.assertEqual(len(known), 0)

if __name__ == '__main__':
    unittest.main()
