from django.test import TestCase
from django.db.models import Exists
from django.core.exceptions import ValidationError
from warroom.rules.RuleSet_model import RuleSet
from warroom.rules.equipment_categories import EquipmentCategory
from warroom.rules.equipment_features import EquipmentFeatures
from copy import deepcopy


# Create your tests here.

class RuleSetTestCase(TestCase):
    def setUp(self):
        pass;
        
    def test_save_correct(self):
        """Does saving of correctly formatted data work?"""

        name = "test_RuleSet"
        version = "0.0.0a"
        terrains = {"Sand":{
                        "Desc": "It gets in everywhere.",
                        "Speed_factor": 0.3,      # slows
                        "Mitigation_factor": 1.0, # no change
                        "Camo_bonus": 0.5,        # easy to spot things in
                        # lower or mixed case name should still pass validation
                        "coLor": "#CBB093",       
                        "IconURL": "graphics/absent.svg"
            }
        }

        equipment = {"Basic Rifle":
                     {"Category":"INF",
                      #"Features":[],
                      "HP":1, "Speed":6,
                      "IconURL":"graphics/absent.svg",
                      "DAM_LGT":1, "DAM_EXP":0, "DAM_PEN":0,
                      "MIT_LGT":0, "MIT_EXP":0, "MIT_PEN":0,
                      "Cammo":0, "Recon":0,
                      "Volume":1, "Capacity":0},

                     "Heavy Machinegun":
                     {"Category":"INF",
                      #"Features":[],
                      "HP":2, "Speed":5,
                      "IconURL":"graphics/absent.svg",
                      "DAM_LGT":4, "DAM_EXP":0, "DAM_PEN":0,
                      "MIT_LGT":0, "MIT_EXP":0, "MIT_PEN":0,
                      "Cammo":-0.1, "Recon":0,
                      "Volume":5, "Capacity":0},

                     "Supply Truck":
                     {"Category":"VEH",
                      "Features":["Logi"],
                      "HP":0, "Speed":0,
                      "IconURL":"graphics/absent.svg",
                      "DAM_LGT":0, "DAM_EXP":0, "DAM_PEN":0,
                      "MIT_LGT":0, "MIT_EXP":0, "MIT_PEN":0,
                      "Cammo":0, "Recon":0,
                      "Volume":0, "Capacity":0}
                     }

        rule_set = RuleSet(name=name, version=version, terrains=terrains,
                           equipment=equipment
                           )
        # print(rule_set._meta.fields)
        # print([x.name for x in rule_set._meta.fields])
        rule_set.save()
        
        # check that it got written to the DB
        assert Exists(RuleSet.objects.filter(name=name, version=version))



    def test_save_incorrect_terrains(self):
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

        # Test each element of the sand Terrain.
        # Each should fail validation.
        for key in terrains_correct["sand"].keys():
            with self.assertRaises(ValidationError):
                test_terrains = deepcopy(terrains_correct)
                test_terrains["sand"][key] = terrains_wrong["sand"][key]

                rule_set = RuleSet(name=name, version=version, terrains=test_terrains)
                rule_set.save()



def test_save_incorrect_terrains(self):
        """Does saving of incorrectly formatted data raise a validation error?"""

        name = "test_RuleSet"
        version = "0.0.0a"
        equipment_correct = {     
                "Supply Truck":
                     {"Category":"VEH",
                      "Features":["Logi"],
                      "HP":0, "Speed":0,
                      "IconURL":"graphics/absent.svg",
                      "DAM_LGT":0, "DAM_EXP":0, "DAM_PEN":0,
                      "MIT_LGT":0, "MIT_EXP":0, "MIT_PEN":0,
                      "Cammo":0, "Recon":0,
                      "Volume":0, "Capacity":0
                      }
                }
        
        equipment_wrong = {
             "Supply Truck":
                    {"Category":"BLA",
                      "Features":["Random"],
                      "HP":-1000, "Speed":-1.0,
                      "IconURL":"graphics/absent.jpeg",
                      "DAM_LGT":None, "DAM_EXP":"bla", "DAM_PEN":"3d9+1",
                      "MIT_LGT":-10., "MIT_EXP":None, "MIT_PEN":"N/A",
                      "Cammo":None, "Recon":"TNK",
                      "Volume":0.1, "Capacity":1 # cap 1 is ok, but not when it is > Volume
                }
            }

        # Test each element of the Supply Truck equipment in equipment_wrong.
        # Each should fail validation.
        for key in equipment_correct["Supply Truck"].keys():
            with self.assertRaises(ValidationError):
                test_equip = deepcopy(equipment_correct)
                test_equip["Supply Truck"][key] = equipment_wrong["Supply Truck"][key]

                rule_set = RuleSet(name=name, version=version, equipment=test_equip)
                rule_set.save()

        