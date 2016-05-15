import shlex
import subprocess
import random
import time
import string

import pytest
import pyelasticsearch
import django.db as db
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
    _random_writes()
    time.sleep(5)

    p.terminate()
    p.wait()

    index, doc_type = 'synced-docs', 'common_syncedthing'
    res = elasticsearch.search({}, index=index, doc_type=doc_type)

    assert models.SyncedThing.objects.count() == res['hits']['total']

    for st in models.SyncedThing.objects.all():
        res = elasticsearch.get(index, doc_type, st.pk)
        assert st.title == res['_source']['title']


def _random_str():
    i = 0
    letters = []
    while i < 25:
        letters.append(random.choice(string.letters))
        i += 1
    return ''.join(letters)


def _random_writes(initial_inserts=5000, num_ops=5000):
    i = 0
    while i < initial_inserts:
        models.SyncedThing.objects.create(title=_random_str())
        i += 1

    i = 0
    while i < num_ops:
        count = models.SyncedThing.objects.count()
        offset = random.randint(0, count - 1)

        op = random.choice(['INSERT', 'UPDATE', 'DELETE'])

        if op == 'INSERT':
            models.SyncedThing.objects.create(title=_random_str())

        elif op == 'UPDATE':
            items = models.SyncedThing.objects.all()[offset:offset + 1]
            st = items[0]
            st.title = _random_str()
            st.save()

        elif op == 'DELETE':
            items = models.SyncedThing.objects.all()[offset:offset + 1]
            st = items[0]
            st.delete()

        time.sleep(0.025)
        i += 1
