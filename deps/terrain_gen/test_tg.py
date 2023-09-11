from unittest import TestCase
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), 'build'))
import terraingen as tg
import numpy as np

# Create your tests here.
class TestTerraingen(TestCase):
    def test_version(self):
        v=tg.version()
        v = v.split(" v")
        self.assertEqual(v[0], "LogistiX terraingen")

    def test_gen(self):
        gen=tg.Generator()
        gen.setSeed(444)
        
        N=10
        x=np.linspace(0,2,N).astype(np.float32)
        y=np.full((N,), 0.5).astype(np.float32)
        v=gen.getTerrain(x,y)
        self.assertTrue(np.all(v == 3))
        
