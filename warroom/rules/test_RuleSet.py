from django.test import TestCase
from django.db.models import Exists
from django.core.exceptions import ValidationError
from warroom.rules.RuleSet_model import RuleSet
from copy import deepcopy


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
        # print(rule_set._meta.fields)
        print([x.name for x in rule_set._meta.fields])
        rule_set.save()
        
        # check that it got written to the DB
        assert Exists(RuleSet.objects.filter(name=name, version=version))

    def test_save_incorrect(self):
        """Does saving of incorrectly formatted data raise a validation error?"""

        name = "test_RuleSet"
        version = "0.0.0a"
        terrains_correct = {"sand":{
                        "desc": "It gets in everywhere.",
                        "speed_factor": 0.3,      # slows
                        "mitigation_factor": 1.0, # no change
                        "camo_bonus": 0.5,        # easy to spot things in
                        "color": "#CBB093",
                        "iconURL": "graphics/absent.svg"
            }
        }
        terrains_wrong = {"sand":{
                        "desc": 1,
                        "speed_factor": None,
                        "mitigation_factor": -1,
                        "camo_bonus": list(),
                        "color": "#GGGGGG",
                        "iconURL": "README.me"
            }
        }

        # test each element of the sand terrain
        for key in terrains_correct["sand"].keys():
            with self.assertRaises(ValidationError):
                test_terrains = deepcopy(terrains_correct)
                test_terrains["sand"][key] = terrains_wrong["sand"][key]

                rule_set = RuleSet(name=name, version=version, terrains=test_terrains)
                rule_set.save()

        