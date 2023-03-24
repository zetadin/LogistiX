from django.contrib import admin
from .models import Recipe, SupplyType, SupplyItem, CombatantType, PlatoonType, Platoon
from .map.models import Map, Hex, Terrain, Improvement
from .map.facilities import Facility

# Register your models here.
admin.site.register(Recipe)
admin.site.register(SupplyType)
admin.site.register(SupplyItem)
admin.site.register(CombatantType)
admin.site.register(PlatoonType)
admin.site.register(Platoon)
admin.site.register(Map)
admin.site.register(Hex)
admin.site.register(Terrain)
admin.site.register(Improvement)
admin.site.register(Facility)
