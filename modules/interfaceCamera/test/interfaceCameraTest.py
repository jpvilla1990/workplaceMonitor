import unittest
from unittest.mock import patch
from modules.interfaceCamera.interfaceCamera import InterfaceCamera

class mockGet(object):
    raw = "mockRaw"

class InterfaceCameraTest(unittest.TestCase):
    """
    Interface Camera Unit Tests
    """
    @patch("PIL.Image.open")
    @patch("requests.get", return_value=mockGet)
    def test_getConfig(self, get_call, open_call):
        """
        Test getConfig Method
        """
        interfaceCamera : InterfaceCamera = InterfaceCamera()
        images : dict = interfaceCamera.getImages()

        self.assertEqual(open_call.assert_called_with("mockRaw"), None)
        self.assertGreaterEqual(len(images), 0)

if __name__ == '__main__':
    unittest.main()