import bcrypt
import psycopg2
import redis

from config import configPSQL, configREDIS


class Connection:
    def __init__(self):
        self.cur = None
        self.conn = None
        self.redisConn = None
        self.redisCur = None

    def connect(self):
        """ Connect to the PostgreSQL database server """
        try:
            # read connection parameters
            params = configPSQL()

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

            # ---------------------------------------
            print("testing redis")
            params = configREDIS()
            self.redisConn = redis.Redis(**params)
            if self.redisConn.ping():
                print("PONG")
            else:
                print("Connection failed!")


            # close the communication with the PostgreSQL
            # cur.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        # finally:
        #     if conn is not None:
        #         conn.close()
        #         print('Database connection closed.')

    def create_tables(self):
        self.cur.execute("create table if not exists users( user_id serial primary key, email varchar(255) unique not null, password text not null, name varchar(50) not null);")
        self.cur.execute("create table if not exists urls_data(url_id serial primary key, user_id integer references users(user_id), title text, redis_key text);")
        self.cur.execute("create table if not exists url_tags(tag_id serial primary key, url_id integer references urls_data(url_id));")
        self.cur.execute("create table if not exists user_tags(tag_id integer references url_tags(tag_id), user_id integer references users(user_id), tag_name text)")
        self.conn.commit()

    def close(self):
        self.cur.close()
        self.conn.close()
        print('Database connection closed.')

    def register(self, user):
        query = "select u from users u where u.email = '{0}'".format(user.email)
        self.cur.execute(query)
        result = self.cur.fetchall()
        if len(result) == 0:
            bytePwd = user.password.encode('utf-8')
            mySalt = bcrypt.gensalt()
            hash = bcrypt.hashpw(bytePwd, mySalt)
            query = "insert into users(email,password,name) values(%s,%s,%s)"
            self.cur.execute(query,(user.email, hash.decode('utf-8'), user.username))
            self.conn.commit()
        else:
            return -1

    def login(self, user):
        print(user.password)
        query = "select u.password from users u where u.email = '{0}'".format(user.email)
        self.cur.execute(query)
        result: bytes = self.cur.fetchall()
        if len(result) == 0:
            return -1
        pwd = user.password.encode('utf-8')
        stored_hashed = (result[0][0]).encode('utf-8')

        if not bcrypt.checkpw(pwd,stored_hashed):
            return -2

        return 1




    def create_link(self, long_link, short_link, user, title):
        self.create_link_redis(short_link,long_link)
        # self.create_link_psql(user, title, short_link)

    def create_link_redis(self,short_link,long_link):
        if self.redisConn.exists(f"{short_link}"):
            return -1
        self.redisConn.set(f"{short_link}", f"{long_link}")


    def create_link_psql(self,user, title, short_link):
        pass

    def delete_link(self,short_link):
        if self.redisConn.exists(f"{short_link}"):
            self.redisConn.delete(f"{short_link}")
        else:
            return -1
        # add psql

    def change_link(self,old_link, short_link):
        if self.redisConn.exists(f"{old_link}"):
            print("entre")
            long_link = self.redisConn.get(f"{old_link}")
            self.redisConn.delete(f"{old_link}")
            self.redisConn.set(f"{short_link}", long_link)
        else:
            return -1
        #add psql