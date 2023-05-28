from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.core.exceptions import PermissionDenied
from rest_framework import serializers, generics

from warroom.map.models import Map, Hex, Terrain, Improvement

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
        return(redirect('/menu'))
    

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


# def get_map(request):
    
#     if(request.user.is_authenticated and request.user.is_active):
#         mapid = request.GET.get('mapid', "")
#         if(mapid):
#             map_query = Map.objects.filter(name=mapid)
#             if(len(map_query)!=1):
#                 return JsonResponse(dict) # empty dictionary
            
#             # resp=dict;
#             # resp['name'] = map_query[0]['name']
#             # resp['id'] = map_query[0]['id']
            
#             hex_query = Hex.objects.filter(map_id=resp['id'])
#     else:
#         return JsonResponse(dict) # empty dictionary
    