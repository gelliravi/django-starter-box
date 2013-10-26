import random 

from django.db import models
from django.utils import timezone 

from djbase.models import BaseModel 

class CDNVersionManager(models.Manager):
    def get_latest(self, is_done=True):
        qs = self.filter(is_done=is_done).order_by('-id')[0:1]
        rows = list(qs)

        if rows:
            return rows[0]

        return None

    def create_new(self):
        now = timezone.now()
        date_str = now.strftime('%Y%m%d')

        while True:
            rand = random.randint(0, 2**31 - 1)
            version_str = '%s-%08X' % (date_str, rand)
                
            try:
                return self.create(version_str=version_str)
            except IntegrityError:
                pass 

class CDNVersion(BaseModel):
    id              = models.AutoField(primary_key=True)
    version_str     = models.CharField(max_length=30, unique=True)
    is_done         = models.BooleanField(default=False,)
    created         = models.DateTimeField(auto_now_add=True)

    objects = CDNVersionManager()

    class Meta:
        index_together = [
            ['is_done', 'id'],
        ]
