from django.core.management.base import BaseCommand, CommandError

from djcdn.models import CDNVersion

class Command(BaseCommand):
    args = ''
    help = ''

    def handle(self, *args, **options):
        ver = CDNVersion.objects.get_latest(is_done=False)

        if not ver:
            print('ERROR: Nothing deployed yet.')
            return 

        if ver.is_done:
            print('ERROR: Version %s already marked as done.' % ver.version_str)
            return 

        ver.is_done = True 
        ver.save(update_fields=('is_done',))

        print('Version %s marked as done.' % ver.version_str)
    
