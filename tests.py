import unittest
from vm import StackMachine


class TestVM(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_vm(self):
        code = 'test 34 7 + 17 % 7 * 1 + 5 / 5 - 5 =='
        sm = StackMachine(code)
        sm.run()

        self.assertTrue(sm.top())


if __name__ == '__main__':
    unittest.main()
