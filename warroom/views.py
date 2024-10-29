# Copyright (c) 2024, Yuriy Khalak.
# Server-side part of LogisticX.

import time
import json

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from django.db.models import Exists
from rest_framework import serializers, generics
from django.templatetags.static import static
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from functools import reduce
from django.shortcuts import get_object_or_404

from LogistiX_backend.user_utils import user_hash
from warroom.map.models import Map, Chunk, Improvement, MapType
from warroom.map.mapgen import mapgen_ter
from warroom.models import Platoon, PlatoonType
from warroom.rules.RuleSet_model import RuleSet



# helper function to add error messages
def add_to_err(msg, context):
    if("err" not in context.keys()):
        context["err"]=""
    else:
        context["err"]+="\n"
    context["err"]+=msg


# Create your views here.

def warroom(request):
    if(request.user.is_authenticated and request.user.is_active):

        mapid = request.GET.get('mapid', "")
        if(mapid):
            map_query = Map.objects.filter(name=mapid)
            if(map_query.count()!=1):
                # either no matches or multiple matches
                response = redirect('/warroom/map_setup')
                response['Location'] += f"?mapid={mapid}&err=Invalid map requested from warroom."
                return(response)
            
            # find the map's RuleSet
            map = map_query.first()
            if(map.ruleset):
                ruleset = map.ruleset
            else:
                ruleset = RuleSet.objects.get(name="default")
            context = {'mapid':mapid, 'ruleset_name':ruleset.name, 'ruleset_version':ruleset.version}


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
        template = loader.get_template('map_setup.html')
        context = {"allow_regen":True} # allow regenerating map by default
        context["err"] = request.GET.get('err', "") # show passed errors
        try:
            mapid = request.GET.get('mapid', "") # exact id of map
            maptype = int(request.GET.get('maptype', 0)) # MapType requested (use value), default to 0 -> Tutorial Island
            if(maptype not in MapType):
                raise TypeError("Wrong MapType")
            forbid_gen = int(request.GET.get('forbid_gen', 0)) # re-generation was forbidden
        except (TypeError, ValueError):
            add_to_err("Invalid input.", context)
            context["allow_regen"]=False
            return HttpResponse(template.render(context, request))


        # show error message for forbid_gen
        if(forbid_gen>0):
            add_to_err("Re-generation forbidden: map in use by others.", context)

        # if a particular mapid was requested
        if(mapid):
            map_query = Map.objects.prefetch_related('profiles').filter(name=mapid)
            try:
                m = map_query.get() # will throw error if no match or >1

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
                        # add_to_err("Re-generation disabled: map in use by others.", context)

                # mapid should only be set if user can join


                # send the webpage to the client now
                return HttpResponse(template.render(context, request))

            except (ObjectDoesNotExist, MultipleObjectsReturned):
                # either no matched mapids or multiple matches
                add_to_err("Invalid map requested.", context)
               
            
        

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
        maptype = int(request.GET.get('maptype', "0")) # MapType requested (use value), default to 0 -> Tutorial Island

        # if no particular mapid was requested, build one
        if(not mapid):
            mapid = f"{MapType(maptype).name}_{user_hash(request.user)}";

        # ginen a particular mapid    
        map_query = Map.objects.prefetch_related('profiles').filter(name=mapid)
        if(map_query.count()==0):   # map does not exist
            allow_regen=True # can generate a new one       
        elif(map_query.count()==1): # map exists
            # check if someone else is already using this map
            profiles = map_query[0].profiles
            if(profiles.count()==1 and profiles.first().user == request.user):   # map used only by this user
                allow_regen=True
            elif(profiles.count()==0):  # no one uses it
                allow_regen=True
            else:                       # someone else uses it
                allow_regen=False
        else: # many maps exist: send user back to map_setup with an error
            context = {"allow_regen":False,
                       "mapid":mapid,
                       "maptype":maptype,
                       "err":"Invalid map requested (hash conflict?). Please contact support."
                       }
            template = loader.get_template('map_setup.html')
            return HttpResponse(template.render(context, request))
                    
        if(not allow_regen):
            # send the client back to map_setup with an error
            response = redirect('/warroom/map_setup')
            response['Location'] += '?forbid_gen=1'
            return(response)
        
        elif(map_query.count()==1):
            # delete existing map if regenerating it
            map_query[0].delete()
                
        # generate new map
        m = Map()
        m.name = mapid
        m.seed = time.time_ns()%(2**31)
        # m. seed = 1761922281
        m.type = maptype
        m.sideLen = 40

        m.save() # needs to be saved before ManyToMany, like profiles, can be added
        m.profiles.add(request.user.profile)
        m.save()
        mapgen_ter(m, MapType(maptype), 
                   # MapShape.Square,
                   size=m.sideLen)
        


        # send the client to warroom with the new mapid
        response = redirect('/warroom')
        response['Location'] += '?mapid=' + str(mapid)
        return(response)
    
    else:
        # send the client to wback to main menu for login
        response = redirect('/menu')
        response['Location'] += '?not_logedin=1'
        return(response)



class ChunkSerializer(serializers.ModelSerializer):
    # convert hexes from the data atribute
    hexes = serializers.SerializerMethodField()
    def get_hexes(self, obj):
        return json.loads(obj.data)
    
    class Meta:
        model = Chunk
        fields = ('x','y', 'hexes')

class MapSerializer(serializers.ModelSerializer):
    chunks = ChunkSerializer(read_only=True, source="chunk_set", many=True)
    class Meta:
        model = Map
        fields = ('name','chunks')

class MapListView(generics.ListAPIView):
    serializer_class = MapSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list containing the desired map.
        and prefetch the relevant hexes.
        """
        mapid = self.request.GET.get('mapid', "")
        return Map.objects.filter(name=mapid).prefetch_related("chunk_set")
    
        
    

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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of platoons on the desired map.
        """
        user = User.objects.get(pk=self.request.user.id)
        user_faction=user.profile.faction
        mapid = self.request.GET.get('mapid', "")
        map_platoons = Platoon.objects.filter(map__name=mapid)
        faction_platoons = map_platoons.filter(faction=user_faction)

        #TODO: also collect platoons of other factions that are 
        # in the zone of controll of player faction
        return faction_platoons
    


# Rules
class RuleSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuleSet
        fields = ( 'name','version','terrains','recipes','equipment',
                   'facilities', 'missions','units'
                 )

class RuleSetView(generics.RetrieveAPIView):
    serializer_class = RuleSetSerializer
    permission_classes = [IsAuthenticated]
    lookup_fields = ('name', 'version')

    def get_queryset(self):
        """
        This view should return a single ruleset by name and version.
        """
        # name = self.request.GET.get('name', "minimal")
        # version = self.request.GET.get('version', "0.0.0")
        rs = RuleSet.objects.all()#.filter(name=name, version=version)
        return rs
    
    def get_object(self):
        """
        This view should return a single ruleset by name and version.
        Overrides the base class to support multiple lookup fields.
        """
        queryset = self.get_queryset()             # Get the base queryset
        queryset = self.filter_queryset(queryset)  # Apply any filter backends
        filter = {}
        filter["name"] = self.request.GET.get("name", "minimal")
        filter["version"] = self.request.GET.get("version", "0.0.0")

        for key in filter.keys():
            print(f"{key}: {filter[key]}")
        
        # Run the query on the DB
        obj = get_object_or_404(queryset, **filter)
        
        # May raise a permission denied
        self.check_object_permissions(self.request, obj)
        return obj
    

class RuleSetIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = RuleSet
        fields = ( 'name','version')

class RuleSetListView(generics.ListAPIView):
    serializer_class = RuleSetIDSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of ruleset names and versions.
        """
        rs = RuleSet.objects.all().only('name', 'version') # limit infor retrieved from DB
        return rs
