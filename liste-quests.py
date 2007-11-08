#!/usr/bin/python
from django.core.management import setup_environ
import settings
setup_environ(settings)

from lg.testing.models import Enonce

for e in Enonce.objects.all():
    print e
    for q in e.question_set.all():
        print q
        for r in q.reponse_set.all():
            print r
