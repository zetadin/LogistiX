from django.apps import AppConfig
#from .map.models import populate_db_Terrains

class WarroomConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'warroom'
    def ready(self):
        #populate_db_Terrains();
        pass # startup code here