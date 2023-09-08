from unittest import TestCase
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), 'build'))
import terraingen as tg

# Create your tests here.
class TestTerraingen(TestCase):
    def test_version(self):
        v=tg.version()
        v = v.split(" v")
        self.assertEqual(v[0], "LogistiX terraingen")
