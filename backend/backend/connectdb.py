import psycopg2
from config import config

class ConnectionPSQL:
    def __init__(self):
        self.cur = None
        self.conn = None

    def connect(self):
        """ Connect to the PostgreSQL database server """
        try:
            # read connection parameters
            params = config()

            # connect to the PostgreSQL server
            print('Connecting to the PostgreSQL database...')
            self.conn = psycopg2.connect(**params)

            # create a cursor
            self.cur = self.conn.cursor()

            # execute a statement
            print('PostgreSQL database version:')
            self.cur.execute('SELECT version()')

            # display the PostgreSQL database server version
            db_version = self.cur.fetchone()
            print(db_version)


            # close the communication with the PostgreSQL
            # cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        # finally:
        #     if conn is not None:
        #         conn.close()
        #         print('Database connection closed.')

    def create_tables(self):
        self.cur.execute("create table if not exists users( user_id serial primary key, email varchar(255) not null, password varchar(50) not null, name varchar(50) not null);")
        self.cur.execute("create table if not exists urls_data(url_id serial primary key, user_id integer references users(user_id), title text, redis_key text);")
        self.cur.execute("create table if not exists url_tags(tag_id serial primary key, url_id integer references urls_data(url_id));")
        self.cur.execute("create table if not exists user_tags(tag_id integer references url_tags(tag_id), user_id integer references users(user_id), tag_name text)")
        self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()
        print('Database connection closed.')
