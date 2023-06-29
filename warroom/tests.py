from django.test import TestCase, TransactionTestCase, Client
from django.contrib import auth
from django.contrib.auth.models import User
from django.db.models import Exists
from django.urls import reverse
from warroom.map.models import Map, Hex, Terrain, Improvement
from warroom.models import Platoon, PlatoonType
from main_menu.models import Profile
import json

# Create your tests here.

class ProfileTestCase(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create(username='testuser')
        self.user.set_password('12345@!A')
        self.user.save()
        self.client = Client()
        
    def test_login(self):
        """Can we log in?"""
        self.client.login(username=self.user.username, password='12345@!A')
        u = auth.get_user(self.client)
        assert u.is_authenticated

    def test_profile(self):
        """Profile should be created automatically and faction set to 0"""
        self.client.login(username=self.user.username, password='12345@!A')
        u = auth.get_user(self.client)
        p = Profile.objects.get(user=u.id)
        self.assertEqual(p.faction, 0)




class QuerryingTestCase(TestCase):
    def setUp(self):
        map = Map.objects.create(name="Test")
        pt = PlatoonType.objects.create(type="Militia")
        Platoon.objects.create(map=map,
                               faction=0, x=0,y=0,number=0,
                               type = pt
                              )
        Platoon.objects.create(map=map,
                               faction=1, x=1,y=1,number=1,
                               type = pt
                              )
        
        self.user = User.objects.create(username='testuser')
        self.user.set_password('12345@!A')
        self.user.save()
        self.client = Client()

    def test_Platoon_Query(self):
        """print the Tutorial platoons from side 0"""
        # map = Map.objects.get(name="Test")
        # faction_platoons = map.platoon_set.filter(faction=0)

        # map_platoons = Platoon.objects.filter(map__name="Test") # 2 querries
        map_platoons = Platoon.objects.filter(Exists(Map.objects.filter(name="Test"))) # 1 querry?
        faction_platoons = map_platoons.filter(faction=0)
        # print(faction_platoons)
        self.assertEqual(faction_platoons.count(), 1)
        self.assertEqual(faction_platoons.first().__str__(), "HQ Militia Platoon")

    def test_Platoon_Get(self):
        self.client.login(username=self.user.username, password='12345@!A')
        responce = self.client.get(reverse("getplatoons"), {"mapid":"Test"})
        self.assertEqual(responce.status_code, 200)
        data = json.loads(responce.content)
        # print(data)
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "HQ Militia Platoon")
        
