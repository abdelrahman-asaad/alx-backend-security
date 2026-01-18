from django.core.management.base import BaseCommand
from ip_tracking.models import BlockedIP

class Command(BaseCommand):
    """
    Command مخصص لإضافة IP إلى قائمة الحظر
    """

    help = "Block an IP address from accessing the system" #وصف الأمر الذي يظهر في المساعدة help is a documentation string for the command line

    def add_arguments(self, parser):
        """
        تعريف الباراميترات التي يمكن تمريرها مع الأمر
        """
        parser.add_argument(
            "ip_address",                 #ip address parameter in the command line like : python manage.py block_ip , django converts it to dictionary of :options={"ip_address": "8.8.8.8"}
            type=str,
            help="The IP address that should be blocked"
        )

    def handle(self, *args, **options):
        """
        المنفذ الأساسي للأمر
        """
        ip = options["ip_address"]  # قراءة الـ IP من التيرمينال , options is a dictionary in terminal of the command line , like : python manage.py block_ip 8.8.8.8 , Django converts options to dictionary: options = {"ip_address": "8.8.8.8"}

        # إضافة الـ IP لو مش موجود
        obj, created = BlockedIP.objects.get_or_create(ip_address=ip)

        if created:
            self.stdout.write(
                self.style.SUCCESS(f"IP {ip} has been blocked successfully.")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"IP {ip} is already blocked.")
            )
