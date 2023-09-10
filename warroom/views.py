from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.db.models import Exists
from rest_framework import serializers, generics
from django.templatetags.static import static

from warroom.map.models import Map, Hex, Terrain, Improvement, MapType
from warroom.models import Platoon, PlatoonType

# Create your views here.

def warroom(request):
    if(request.user.is_authenticated and request.user.is_active):

        mapid = request.GET.get('mapid', "")
        if(mapid):
            map_query = Map.objects.filter(name=mapid)
            if(map_query.count()!=1):
                #either no matches or multiple matches
                return(redirect('/warroom', mapid=""))
        context = {'mapid':mapid}
        template = loader.get_template('warroom.html')
        # template = loader.get_template('warroom_fabric.html')
        return HttpResponse(template.render(context, request))
    
    else:
        # send the client to wback to main menu for login
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
        # send the client to wback to main menu for login
        response = redirect('/menu')
        response['Location'] += '?not_logedin=1'
        return(response)
    

def map_setup(request):
    if(request.user.is_authenticated and request.user.is_active):

        # helper function to add error messages
        def add_to_err(msg):
            if("err" not in context.keys()):
                context["err"]=""
            else:
                context["err"]+="\n"
            context["err"]+=msg

        template = loader.get_template('map_setup.html')
        context = {"allow_regen":True} # allow regenerating map by default
        try:
            mapid = request.GET.get('mapid', "") # exact if of map
            maptype = int(request.GET.get('maptype', 0)) # MapType requested (use value), default to 0 -> Tutorial Island
            if(maptype not in MapType):
                raise TypeError("Wrong MapType")
            forbid_gen = int(request.GET.get('forbid_gen', 0)) # re-generation was forbidden
        except (TypeError, ValueError):
            add_to_err("Invalid input.")
            context["allow_regen"]=False
            return HttpResponse(template.render(context, request))


        # show error message for forbid_gen
        if(forbid_gen>0):
            add_to_err("Re-generation forbidden: map in use by others.")

        # if a particular mapif was requested
        if(mapid):
            map_query = Map.objects.prefetch_related('profiles').filter(name=mapid)
            try:
                m = map_query.get() # will throw error if no match or then one

                # show option to join the existing map
                context["mapid"]=mapid
                maptype = map_query[0].type # read maptype of this mapid
                context["maptype"]=maptype
                context["maptype_name"]=MapType(maptype).name

                # check if someone else is already using this map
                profiles = m.profiles
                if(profiles.count()>1):
                    context["allow_regen"]=False
                elif(profiles.count()==1):
                    if(profiles.get().user != request.user): # get shoult only return the first; If there are none or more, it raises errors
                        context["allow_regen"]=False
                        # add_to_err("Re-generation disabled: map in use by others.")

                # send the webpage to the client now
                return HttpResponse(template.render(context, request))

            except (Model.DoesNotExist, Model.MultipleObjectsReturned):
                # either no matched mapids or multiple matches
                add_to_err("Invalid map requested.")
               
            
        

        # if no mapid requested or it does not exist, propose generating a new map
        context["maptype"]=maptype # there is a default set even if not requested from client
        context["maptype_name"]=MapType(maptype).name

        # send the webpage to the client
        return HttpResponse(template.render(context, request))
    
    else:
        # send the client to wback to main menu for login
        response = redirect('/menu')
        response['Location'] += '?not_logedin=1'
        return(response)
    


def generate_map(request):
    if(request.user.is_authenticated and request.user.is_active):

        mapid = request.GET.get('mapid', "") # exact if of map
        maptype = request.GET.get('maptype', "0") # MapType requested (use value), default to 0 -> Tutorial Island
        context = {"allow_regen":True} # allow regenerating map by default       

        # if a particular mapid was requested
        if(mapid):
            map_query = Map.objects.prefetch_related('profiles').filter(name=mapid)
            allow_regen=False
            if(map_query.count()==1):
                # check if someone else is already using this map
                profiles = map_query[0].profiles
                if(profiles.count()==1 and profiles[0].user == request.user):
                    allow_regen=True
                elif(profiles.count()==0):
                    allow_regen=True
                        
            if(not allow_regen):
                # send the client back to map_setup with an error
                response = redirect('/warroom/map_setup')
                response['Location'] += '?forbid_gen=1'
                return(response)
            
            else:
                # TODO: delete existing map
                pass
                
        # TODO: generate new map
        # TODO: set new mapid
        # TODO: save map

        # send the client to warroom with the new mapid
        response = redirect('/warroom')
        response['Location'] += '?mapid=' + str(mapid)
        return(response)
    
    else:
        # send the client to wback to main menu for login
        response = redirect('/menu')
        response['Location'] += '?not_logedin=1'
        return(response)


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
    

# Platoons
class PlatoonTypeSerializer(serializers.ModelSerializer):

    # prepend path to static to iconURL
    iconURL = serializers.SerializerMethodField()
    def get_iconURL(self, obj):
        url=obj.iconURL
        url=static(url)
        return url
    class Meta:
        model = PlatoonType
        fields = ('type', 'iconURL', 'composition', 'supply_requirements')

class PlatoonSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    type = PlatoonTypeSerializer(read_only=True, many=False)
    def get_name(self, obj):
        return obj.__str__()
    
    class Meta:
        model = Platoon
        fields = ( 'name','type','x','y','faction',
                   'supplies_in_use', 'supplies_missing',
                   'camo', 'spotting', 'moveSpeed', 
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