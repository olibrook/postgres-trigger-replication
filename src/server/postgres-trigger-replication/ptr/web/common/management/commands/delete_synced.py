import django.core.management.base as base
import pyelasticsearch

import ptr.web.common.models as models


class Command(base.BaseCommand):

    help = "Delete all synced model instances"

    def handle(self, *args, **options):
        models.SyncedThing.objects.all().delete()

        es = pyelasticsearch.ElasticSearch('http://localhost:9200/')
        es.delete_all_indexes()
