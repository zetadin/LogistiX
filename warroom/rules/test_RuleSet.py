# Copyright (c) 2024, Yuriy Khalak.
# Server-side part of LogisticX.

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

        equipment = {"Basic Rifle Kit":
                     {"Category":"INF",
                      #"Features":[],
                      "HP":1, "Speed":6,
                      "IconURL":"sprites/equipment/INF/basic_rifle.webp",
                      "DAM_LGT":1, "DAM_EXP":0, "DAM_PEN":0,
                      "MIT_LGT":1, "MIT_EXP":1, "MIT_PEN":1,
                      "Cammo":0, "Recon":0.1,
                      "Volume":1, "Capacity":0},

                     "Heavy Machinegun Kit":
                     {"Category":"INF",
                      #"Features":[],
                      "HP":2, "Speed":5,
                      "IconURL":"graphics/absent.svg",
                      "DAM_LGT":4, "DAM_EXP":0, "DAM_PEN":0,
                      "MIT_LGT":0.8, "MIT_EXP":1, "MIT_PEN":1,
                      "Cammo":-0.5, "Recon":0,
                      "Volume":5, "Capacity":0},

                     "Rocket Launcher Kit":
                     {"Category":"INF",
                      #"Features":[],
                      "HP":1, "Speed":6,
                      "IconURL":"graphics/absent.svg",
                      "DAM_LGT":0, "DAM_EXP":3, "DAM_PEN":1,
                      "MIT_LGT":0, "MIT_EXP":0, "MIT_PEN":0,
                      "Cammo":0, "Recon":0,
                      "Volume":3, "Capacity":0},

                     "Supply Truck":
                     {"Category":"VEH",
                      "Features":["Logi"],
                      "HP":5, "Speed":30,
                      "IconURL":"sprites/equipment/VEH/Supply_Truck.webp",
                      "DAM_LGT":0, "DAM_EXP":0, "DAM_PEN":0,
                      "MIT_LGT":1, "MIT_EXP":1, "MIT_PEN":1,
                      "Cammo":-2, "Recon":0,
                      "Volume":150, "Capacity":100},

                     "MG Buggy":
                     {"Category":"VEH",
                      #"Features":[],
                      "HP":5, "Speed":60,
                      "IconURL":"sprites/equipment/VEH/Buggy.webp",
                      "DAM_LGT":5, "DAM_EXP":0, "DAM_PEN":0,
                      "MIT_LGT":1, "MIT_EXP":1, "MIT_PEN":1,
                      "Cammo":0, "Recon":2,
                      "Volume":50, "Capacity":6},

                     "Half-Track":
                     {"Category":"VEH",
                      #"Features":[],
                      "HP":20, "Speed":20,
                      "IconURL":"graphics/absent.svg",
                      "DAM_LGT":4, "DAM_EXP":0, "DAM_PEN":0,
                      "MIT_LGT":0.5, "MIT_EXP":0.2, "MIT_PEN":0,
                      "Cammo":-3, "Recon":0,
                      "Volume":120, "Capacity":12},

                     "Steel":{
                         "Category":"CON",
                         "IconURL":"graphics/absent.svg",
                         "Volume":1
                     },

                     "Organics":{
                         "Category":"CON",
                         "IconURL":"graphics/absent.svg",
                         "Volume":1
                     },
        }
        
        facilities = {"Nano Fab":
                      {"Description": "Small versatile factory that uses nanites to assemble bits and bobs.",
                       "HP": 1000,
                       "IconURL": "graphics/absent.svg",
                       "Capacity": 500,
                       "Production_rate": 20,
                      }
        }

        missions = {
            "Fortify": {   
                "Description": "Shores up defensive positions of an infantry unit.",
                "IconURL": "graphics/absent.svg",
                "Requirements":{
                    "INF": 90,
                },
                "MIT_LGT_factor": 2.0,
                "MIT_EXP_factor": 1.5,
                "DAM_LGT_factor": 0.8,
                "Cammo_flat_bonus": 4,
            },

            "Infantry Assault":{
                "Description": "A massed infantry push.",
                "IconURL": "graphics/absent.svg",
                "Requirements":{
                    "INF": 150,
                },
                "MIT_EXP_factor": 0.5,
                "INF_HP_factor": 0.7, # less HP of each piece of equipment allows for more of them to be used at once
            },

            "Patrol":{
                "Description": "Go out there and be my eyes!",
                "IconURL": "graphics/absent.svg",
                "Requirements":{
                    "Unit": "Recon > 4",
                },
                "Recon_factor": 2.0,          # can find enemy units further
                "Control_radius_factor": 1.5, # far-flung patrols means you get into fights more often
            },

            "Artillery Barrage":{
                "Description": "Saturate the enemy with high-explosives.",
                "IconURL": "graphics/absent.svg",
                "Requirements":{
                    "Unit": "DAM_EXP > 20",
                },
                "Cammo_flat_bonus": -20,
                "DAM_EXP_factor": 3.0,
            }

        }


        units = {
            "Militia":{
                "Description": "Civilian volunteers hastily organised into a fighting force.",
                "IconURL": "sprites/units/INF/militia.webp",
                "Requirements":{
                    "INF": 190,
                    "Any": 200,
                },
                "Features":["Rear"],
                "Control_radius": 2,
                "Control_power": 1,
            },

            "Foot Infantry":{
                "Description": "Trained soldiers with little to no vehicle support.",
                "IconURL": "graphics/absent.svg",
                "Requirements":{
                    "INF": 150,
                    "Any": 200,
                },
                "Control_radius": 2,
                "Control_power": 2,
            },

            "Drop Troops":{
                "Description": "Infantry unit specialised in inserting from orbit without their own heavy assets.",
                "IconURL": "graphics/absent.svg",
                "Requirements":{
                    "INF": 180,
                    "Any": 200,
                },
                "Features":["Drop"],
                "Control_radius": 2,
                "Control_power": 2,
            },

            "Scouts":{
                "Description": "Reconnaissance unit specialised in finding the enemy.",
                "IconURL": "sprites/units/INF/scouts.webp",
                "Requirements":{
                    "INF": 50,
                    "Any": 100,
                },
                "Control_radius": 1, # small radius means you can slip between enemy units without fighting
                "Control_power": 0,  # does not exert control, so not exposed on the map via border changes
            },

            "Mobile Infantry":{
                "Description": "Infantry that drives themselves. Good QRF potential.",
                "IconURL": "graphics/absent.svg",
                "Requirements":{
                    "INF": 100,
                    "VEH": 80,
                    "Any": 200,
                },
                "Control_radius": 4,
                "Control_power": 2,
            },

            "Artillery Battery":{
                "Description": "Lobs shells over a large distance.",
                "IconURL": "graphics/absent.svg",
                "Requirements":{
                    "Arty": 100,
                    "Any": 200,
                },
                "Features":["Indir"],
                "Control_radius": 3,
                "Control_power": 1,
            }

        }


        recipes = {
            "Basic Kit":{
                "Product": "Basic Rifle Kit",
                "Ingredients": {
                    "Organics": 1,
                    "Steel": 1
                },
                "Production_Cost": 1,
                "Facilities": [
                    "Nano Fab"
                ],
                "IconURL": "sprites/equipment/INF/basic_rifle.webp"
            },

            "Machinegun":{
                "Product": "Heavy Machinegun Kit",
                "Ingredients": {
                    "Organics": 2,
                    "Steel": 4
                },
                "Production_Cost": 8,
                "Facilities": [
                    "Nano Fab"
                ],
                "IconURL": "graphics/absent.svg"
            }
        }


        rule_set = RuleSet(name=name, version=version, terrains=terrains,
                           equipment=equipment, facilities=facilities,
                           missions=missions, units=units, recipes=recipes
                           )
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

        