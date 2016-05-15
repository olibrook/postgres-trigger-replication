import json

import psycopg2
import psycopg2.extensions as exts
import eventlet.hubs as hubs
import pyelasticsearch


DB = dict(
    database='docker',
    user='docker',
    host='localhost',
    port='5432',
)


_es = None


def get_es_client():
    global _es
    if _es is None:
        _es = pyelasticsearch.ElasticSearch('http://localhost:9200/')
    return _es


def main():
    cnn = psycopg2.connect(**DB)
    cnn.set_isolation_level(exts.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = cnn.cursor()
    cur.execute("LISTEN sync;")
    es = get_es_client()
    refresh = True
    index = 'synced-docs'
    es.create_index(index)

    while True:
        hubs.trampoline(cnn, read=True)
        cnn.poll()
        while cnn.notifies:
            message = cnn.notifies.pop()
            message = json.loads(message.payload)

            print(message)

            action = message['action']
            doc_type = message['table']

            try:
                doc = message['data'].copy()
                _id = doc.pop('id')

                if action == 'INSERT':
                    es.index(
                        index,
                        doc_type,
                        doc,
                        id=_id,
                        refresh=refresh
                    )
                elif action == 'UPDATE':
                    es.update(
                        index,
                        doc_type,
                        doc=doc,
                        id=_id,
                        refresh=refresh
                    )
                elif action == 'DELETE':
                    es.delete(
                        index,
                        doc_type,
                        _id,
                        refresh=refresh
                    )
            except Exception as e:
                print(e)


if __name__ == '__main__':
    main()
