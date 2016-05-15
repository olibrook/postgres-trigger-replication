"""Listen for change notifications on a Postgres database and write them
to Elastic Search"""

import json
import optparse

import psycopg2
import psycopg2.extensions as exts
import eventlet.hubs as hubs
import pyelasticsearch


def parse_args():
    parser = optparse.OptionParser()
    parser.description = __doc__
    parser.add_option("--database", default='docker')
    parser.add_option("--user", default='docker')
    parser.add_option("--host", default='localhost')
    parser.add_option("--port", default='5432')
    parser.add_option("--elastic-search-url", dest='es_url', default='http://localhost:9200/')
    return parser.parse_args()


def main():
    opts, args = parse_args()

    cnn = psycopg2.connect(
        database=opts.database,
        user=opts.user,
        host=opts.host,
        port=opts.port
    )

    cnn.set_isolation_level(exts.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = cnn.cursor()
    cur.execute("LISTEN sync;")
    es = pyelasticsearch.ElasticSearch(opts.es_url)
    refresh = True
    index = 'synced-docs'
    try:
        es.create_index(index)
    except pyelasticsearch.exceptions.IndexAlreadyExistsError:
        pass

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
