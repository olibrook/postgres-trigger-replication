import psycopg2
import psycopg2.extensions as exts
import eventlet.hubs as hubs

DB = dict(
    database='docker',
    user='docker',
    host='localhost',
    port='5432',
)


def main():
    cnn = psycopg2.connect(**DB)
    cnn.set_isolation_level(exts.ISOLATION_LEVEL_AUTOCOMMIT)
    cur = cnn.cursor()
    cur.execute("LISTEN sync;")
    while True:
        hubs.trampoline(cnn, read=True)
        cnn.poll()
        while cnn.notifies:
            n = cnn.notifies.pop()
            print(n)

if __name__ == '__main__':
    main()
