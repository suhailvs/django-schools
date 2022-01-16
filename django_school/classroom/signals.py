from django.contrib.auth.signals import (user_logged_in, 
    user_login_failed, user_logged_out)
from django.dispatch import receiver

from .models import AuditEntry

# https://stackoverflow.com/a/37620866/2351696
@receiver(user_logged_in)
def user_logged_in_callback(sender, request, user, **kwargs):
    ip = request.META.get('REMOTE_ADDR')

    from urllib.request import urlopen
    from json import load
    try:
        # https://stackoverflow.com/a/55432323/2351696
        data = load(urlopen(f'https://ipinfo.io/{ip}/json'))
        ip_loc = f"{ip}, {data['city']} {data['region']} {data['country']}"
    except:
        ip_loc = ip

    AuditEntry.objects.create(action='user_logged_in', ip=ip_loc, username=user.username)


@receiver(user_login_failed)
def user_login_failed_callback(sender, credentials, **kwargs):
    AuditEntry.objects.create(action='user_login_failed', username=credentials.get('username', None))



@receiver(user_logged_out)
def user_logged_out_callback(sender, request, user, **kwargs):  
    ip = request.META.get('REMOTE_ADDR')
    AuditEntry.objects.create(action='user_logged_out', ip=ip, username=user.username)

