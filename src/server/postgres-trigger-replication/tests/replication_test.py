import shlex
import subprocess
import random
import time
import string

import pytest
import pyelasticsearch
import django.db as db
import django.db.transaction as transaction
import django.conf as conf

import ptr.web.common.models as models

es_url = 'http://localhost:9200/'

@pytest.fixture()
def elasticsearch(request):
    es = pyelasticsearch.ElasticSearch(es_url)
    es.delete_all_indexes()

    def fin():
        es.delete_all_indexes()

    request.addfinalizer(fin)
    return es


@pytest.mark.django_db(transaction=True)
def test_replication(elasticsearch):

    def _random_str():
        i = 0
        letters = []
        while i < 25:
            letters.append(random.choice(string.letters))
            i += 1
        return ''.join(letters)

    def _random_writes(max_writes=50):
        i = 0
        while i < max_writes:
            op = random.choice(['INSERT', 'UPDATE'])

            try:
                with transaction.atomic():

                    if op == 'INSERT':
                        models.SyncedThing.objects.create(title=_random_str())

                    elif op == 'UPDATE':
                        items = models.SyncedThing.objects.order_by('pk')[:1]
                        if len(items) == 1:
                            st = items[0]
                            st.title = _random_str()
                            st.save()
                        pass

                    elif op == 'DELETE':
                        items = models.SyncedThing.objects.order_by('pk')[:1]
                        if len(items) == 1:
                            items[0].delete()

            except models.SyncedThing.DoesNotExist as e:
                print(e)

            time.sleep(0.025)
            i += 1

    kwargs = db.connection.get_connection_params()
    kwargs.update(es_url=es_url)

    cmd = (
        "./bin/receiver "
        "--database {database} "
        "--user {user} "
        "--host {host} "
        "--port {port} "
        "--elastic-search-url {es_url}"
    ).format(**kwargs)

    cmd = shlex.split(cmd)

    p = subprocess.Popen(
        cmd,
        shell=False,
        cwd=conf.settings.BASE_DIR,
    )

    time.sleep(1)

    _random_writes(max_writes=10)

    time.sleep(1)
    p.terminate()
    p.wait()

    index, doc_type = 'synced-docs', 'common_syncedthing'
    res = elasticsearch.search({}, index=index, doc_type=doc_type)

    assert models.SyncedThing.objects.count() == res['hits']['total']


