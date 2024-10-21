from django.test import TestCase
from django.db.models import Exists
from warroom.rules.RuleSet_model import RuleSet
import json

# Create your tests here.

class ProfileTestCase(TestCase):
    def setUp(self):
        pass;
        
    def test_save_correct(self):
        """Does saving of correctly formatted data work?"""

        name = "test_RuleSet"
        version = "0.0.0a"
        terrains = {"sand":}
        
        assert 0