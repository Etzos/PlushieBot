import unittest

from ..message import Message


class TestMessageFile(unittest.TestCase):

    def test_plain_raw(self):
        msg = Message("This is a plain message")
        self.assertEqual(msg.raw, "This is a plain message")
