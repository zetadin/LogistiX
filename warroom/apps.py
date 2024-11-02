# Copyright (c) 2024, Yuriy Khalak.
# Server-side part of LogisticX.

from django.apps import AppConfig
from glob import glob
import os
import pathlib
import json
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)



class WarroomConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'warroom'
    def ready(self):
        print("\nLoading RuleSets:")
        
        # read in the rulesets
        rs_path = os.path.join(pathlib.Path(__file__).parent.absolute(), "rules", "RuleSetConfigs")
        rs_query = os.path.join(rs_path, "*", "v*.*")

        rulesets = glob(rs_query)

        # import the RuleSet model here to avoid "Apps aren't loaded yet" error
        from warroom.rules.RuleSet_model import RuleSet

        # put all rulesets into the DB and update the ones already in it
        for rs_f in rulesets:
            rs_f_end = rs_f[len(rs_path)+1:]

            # find RuleSet name and version
            rs_name, rs_version = os.path.split(rs_f_end)
            print(f"\t{rs_name}: {rs_version}")

            if(rs_version[0]=='v'): # drop the v prefix
                rs_version = rs_version[1:]
            
            
            # load the component json files
            with open(os.path.join(rs_f, 'terrains.json')) as f:
                terrains = json.load(f)
            with open(os.path.join(rs_f, 'equipment.json')) as f:
                equipment = json.load(f)
            with open(os.path.join(rs_f, 'facilities.json')) as f:
                facilities = json.load(f)
            with open(os.path.join(rs_f, 'recipes.json')) as f:
                recipes = json.load(f)
            with open(os.path.join(rs_f, 'units.json')) as f:
                units = json.load(f)
            with open(os.path.join(rs_f, 'missions.json')) as f:
                missions = json.load(f)


            # ovewrite old copy of it from the DB, if it exists
            found = RuleSet.objects.filter(name=rs_name, version=rs_version)
            if len(found) > 0:
                rs = found.get()
                rs.terrains = terrains
                rs.equipment = equipment
                rs.facilities = facilities
                rs.recipes = recipes
                rs.units = units    
                rs.missions = missions

            # create a new instance of this RuleSet if missing
            else:
                rs = RuleSet.objects.create(name=rs_name, version=rs_version,
                                            terrains=terrains, equipment=equipment,
                                            facilities=facilities, recipes=recipes,
                                            units=units, missions=missions
                                            )
                
            rs.save() # validate and save to DB

        print()

        # also start the background tasks