from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.db.models import Exists
from rest_framework import serializers, generics

from warroom.map.models import Map, Hex, Terrain, Improvement
from warroom.models import Platoon

# Create your views here.

def warroom(request):
    if(request.user.is_authenticated and request.user.is_active):

        mapid = request.GET.get('mapid', "")
        if(mapid):
            map_query = Map.objects.filter(name=mapid)
            if(len(map_query)!=1):
                #either no matches or multiple matches
                return(redirect('/warroom', mapid=""))
        context = {'mapid':mapid}
        template = loader.get_template('warroom.html')
        return HttpResponse(template.render(context, request))
    else:
        response = redirect('/menu')
        response['Location'] += '?not_logedin=1'
        return(response)
    

def mapeditor(request):
    if(request.user.is_authenticated and request.user.is_active):
        if(not request.user.is_staff):
            # only acessible to admins
            raise PermissionDenied
        mapid = request.GET.get('mapid', "Tutorial")
        if(mapid):
            map_query = Map.objects.filter(name=mapid)
            if(len(map_query)!=1):
                #either no matches or multiple matches
                return(HttpResponse("Map "+mapid+" does not exist. Create it via admin first."))
        context = {'mapid':mapid}
        template = loader.get_template('mapeditor.html')
        return HttpResponse(template.render(context, request))
    else:
        return(redirect('/menu'))
    



class TerrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Terrain
        fields = ('name','color')

class HexSerializer(serializers.ModelSerializer):
    terrain = TerrainSerializer(read_only=True, many=False)
    class Meta:
        model = Hex
        fields = ('x','y','terrain','improvements')

class MapSerializer(serializers.ModelSerializer):
    hexes = HexSerializer(read_only=True, source="hex_set", many=True)
    class Meta:
        model = Map
        fields = ('name','hexes')

class MapListView(generics.ListAPIView):
    serializer_class = MapSerializer

    def get_queryset(self):
        """
        This view should return a list containing the desired map.
        and prefetch the relevant hexes.
        """
        mapid = self.request.GET.get('mapid', "")
        return Map.objects.filter(name=mapid).prefetch_related("hex_set")
    

class PlatoonSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    def get_name(self, obj):
        return obj.__str__()
    
    class Meta:
        model = Platoon
        fields = ( 'name','type','x','y','faction',
                   'supplies_in_use', 'supplies_missing',
                   'camo', 'spotting', 'moveSpeed'
                 )


class PlatoonsListView(generics.ListAPIView):
    serializer_class = PlatoonSerializer

    def get_queryset(self):
        """
        This view should return a list of platoons on the desired map.
        """
        user = User.objects.get(pk=self.request.user.id)
        user_faction=user.profile.faction
        mapid = self.request.GET.get('mapid', "")
        map_platoons = Platoon.objects.filter(Exists(Map.objects.filter(name=mapid)))
        faction_platoons = map_platoons.filter(faction=user_faction)

        #TODO: also collect platoons of other factions that are 
        # in the zone of controll of player faction
        return faction_platoons