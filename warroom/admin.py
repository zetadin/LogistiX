# Copyright (c) 2024, Yuriy Khalak.
# Server-side part of LogisticX.

from django.contrib import admin
# from .models import Recipe, SupplyType, SupplyItem, CombatantType, PlatoonType, Platoon
# from .map.models import Map, Terrain, Improvement, Chunk
from .map.models import Map, Improvement, Chunk
from .map.facilities import Facility
from .units.models import Company
from .rules.RuleSet_model import RuleSet

class IconedModelAdmin(admin.ModelAdmin):
     readonly_fields = ['icon_preview']
    #  def get_form(self, request, obj=None, change=False, **kwargs):
    #     form = super().get_form(request, obj, change, **kwargs)
    #     form.base_fields['icon_preview'].label = 'Icon'
    #     return form

# class TerrainAdmin(IconedModelAdmin):
#     list_display = ('name', 'looks_like')

# Register your models here.
# admin.site.register(Recipe)
# admin.site.register(SupplyType)
# admin.site.register(SupplyItem)
# admin.site.register(CombatantType, IconedModelAdmin)
# admin.site.register(PlatoonType, IconedModelAdmin)
# admin.site.register(Platoon)
# admin.site.register(Terrain, TerrainAdmin)
admin.site.register(Company, IconedModelAdmin)
admin.site.register(Improvement)
admin.site.register(Chunk)
admin.site.register(RuleSet)

class FacilityAdmin(admin.ModelAdmin):
    list_display = ["name", "type", "map", "chunk"]
    list_filter = ["type", "chunk__map"]
    @admin.display(ordering="map")
    def map(self, obj):
        return obj.chunk.map
admin.site.register(Facility, FacilityAdmin)


class ChunkInline(admin.TabularInline):
    model = Chunk

class MapAdmin(admin.ModelAdmin):
    inlines = [
        ChunkInline,
    ]
admin.site.register(Map, MapAdmin)
