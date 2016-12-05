from django.core.management.base import BaseCommand
from SAM2017.models import *
from django.contrib.auth.hashers import make_password
 
class Command(BaseCommand):
    help = "Setup database"
     
    def handle(self, *args, **options):
        SAMUser.objects.bulk_create([
            SAMUser(username="heena@sam.com", password=make_password("holahola"), first_name="Heena", last_name="Surve",  phone_number=1234567890, address="Pune",is_superuser=False,is_admin=False),
            SAMUser(username="pratham@sam.com", password=make_password("holahola"), first_name="Pratham", last_name="Mehta",  phone_number=1234567890, address="Pune",is_superuser=False,is_admin=False),
			SAMUser(username="satyajit@sam.com", password=make_password("holahola"), first_name="Satyajit", last_name="Mohapatra",  phone_number=1234567890, address="Pune",is_superuser=False,is_admin=False),
			SAMUser(username="poornima@sam.com", password=make_password("holahola"), first_name="Poornima", last_name="Ubale",  phone_number=1234567890, address="Pune",is_superuser=False,is_admin=False),
			SAMUser(username="eman@sam.com", password=make_password("holahola"), first_name="Eman", last_name="Alomar",  phone_number=1234567890, address="Pune",is_superuser=False,is_admin=False),
            ])
        
        PCM.objects.bulk_create([
            PCM(username="a@sam.com", password=make_password("holahola"), first_name="abc", last_name="def",  phone_number=1234567890, address="Pune",is_superuser=False,is_admin=False),
            ])