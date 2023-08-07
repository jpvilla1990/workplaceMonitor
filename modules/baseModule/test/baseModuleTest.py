import unittest
from modules.baseModule.baseModule import BaseModule

class BaseModuleTest(unittest.TestCase):
    """
    Base Module Unit Tests
    """
    def test_getConfig(self):
        """
        Test getConfig Method
        """
        baseModule : BaseModule = BaseModule()
        config : dict = baseModule.getConfig()
        lenConfig : int = len(config)

        self.assertGreater(lenConfig, 0)

if __name__ == '__main__':
    unittest.main()