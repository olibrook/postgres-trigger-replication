import random
import string

import django.core.management.base as base

import ptr.web.common.models as models


class Command(base.BaseCommand):

    help = "Randomly write/update/delete synced model instances"

    @staticmethod
    def random_str():
        i = 0
        letters = []
        while i < 25:
            letters.append(random.choice(string.letters))
            i += 1
        return ''.join(letters)

    def handle(self, *args, **options):
        while True:
            op = random.choice(['CREATE', 'UPDATE', 'DELETE'])

            try:
                if op == 'CREATE':
                    models.SyncedThing.objects.create(title=self.random_str())
                elif op == 'UPDATE':
                    items = models.SyncedThing.objects.order_by('pk')[:1]
                    if len(items) == 1:
                        st = items[0]
                        st.title = self.random_str()
                        st.save()
                    pass
                elif op == 'DELETE':
                    items = models.SyncedThing.objects.order_by('pk')[:1]
                    if len(items) == 1:
                        items[0].delete()

                    pass

            except models.SyncedThing.DoesNotExist as e:
                print(e)

