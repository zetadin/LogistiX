from django.test import TestCase
from django.db.models import Exists
from warroom.rules.RuleSet_model import RuleSet
import json

# Create your tests here.

class RuleSetTestCase(TestCase):
    def setUp(self):
        pass;
        
        
    def test_save_correct(self):
        """Does saving of correctly formatted data work?"""

        name = "test_RuleSet"
        version = "0.0.0a"
        terrains = {"sand":{
                        "desc": "It gets in everywhere.",
                        "speed_factor": 0.3,      # slows
                        "mitigation_factor": 1.0, # no change
                        "camo_bonus": 0.5,        # easy to spot things in
                        "color": "#CBB093",
                        "iconURL": "graphics/absent.svg"
            }
        }

        rule_set = RuleSet(name=name, version=version, terrains=terrains)
        rule_set.save()
        
        # check that it got written to the DB
        assert Exists(RuleSet.objects.filter(name=name, version=version))