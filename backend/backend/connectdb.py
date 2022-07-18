import bcrypt
import psycopg2
import redis
from numpy.core.defchararray import lower

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
        self.cur.execute("create table if not exists urls_data(url_id serial primary key, user_id integer references users(user_id) on delete cascade , title text, redis_key text);")
        self.cur.execute("create table if not exists user_tags(tag_id serial primary key, user_id integer references users(user_id) on delete cascade, tag_name text)")
        self.cur.execute("create table if not exists url_tags(tag_id integer references user_tags(tag_id) on delete cascade , url_id integer references urls_data(url_id) on delete cascade);")
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
        query = "select u.password from users u where u.email = '{0}'".format(user.email)
        self.cur.execute(query)
        result: bytes = self.cur.fetchall()
        if len(result) == 0:
            return -1
        pwd = user.password.encode('utf-8')
        stored_hashed = (result[0][0]).encode('utf-8')

        if not bcrypt.checkpw(pwd,stored_hashed):
            return -2

        query = "select u.user_id from users u where u.email = '{0}'".format(user.email)
        self.cur.execute(query)
        user.id_user = self.cur.fetchone()[0]

        return 1

    def get_username(self, user_id):
        query = "select name from users where user_id='{0}'".format(user_id)
        self.cur.execute(query)
        username = self.cur.fetchone()[0]
        return username



    def get_user_links(self, id_user):
        query = "select * from urls_data where user_id = '{0}'".format(id_user)
        self.cur.execute(query)
        result = self.cur.fetchall()
        results = []

        urls_ids = []
        for i in range(len(result)):
            url_data = []
            for j in result[i]:
                url_data.append(j)
            results.append(url_data)
            urls_ids.append(results[i][0])

            long_value = self.redisConn.get(f"{results[i][3]}").decode('utf-8')
            results[i].append(long_value)

            tags_query = "select tag_id from url_tags where url_id = '{0}'".format(results[i][0])
            self.cur.execute(tags_query)
            tags_result = self.cur.fetchall()
            tags = []
            for t in tags_result:
                tag = []
                tag.append(t[0])
                tags_name = "select tag_name from user_tags where tag_id = '{0}'".format(t[0])
                self.cur.execute(tags_name)
                tag_name_result = self.cur.fetchone()
                tag.append(tag_name_result[0])
                tags.append(tag)
            results[i].append(tags)
        print(results)
        return results


    def create_link(self, long_link, short_link, id_user, title):
        aux = lower(short_link)
        if aux == 'home' or aux == 'register' or aux == 'login':
            return -1
        if self.create_link_redis(short_link,long_link) == -1:
            return -1
        self.create_link_psql(id_user, title, short_link)

    def create_link_redis(self,short_link,long_link):
        if self.redisConn.exists(f"{short_link}"):
            return -1
        self.redisConn.set(f"{short_link}", f"{long_link}")


    def create_link_psql(self,id_user, title, short_link):
        query = "insert into urls_data(user_id,title,redis_key) values(%s,%s,%s)"
        self.cur.execute(query,(id_user, title, short_link))
        self.conn.commit()

    def delete_link(self,short_link):
        if self.redisConn.exists(f"{short_link}"):
            self.redisConn.delete(f"{short_link}")
            query = "delete from urls_data where redis_key = '{0}'".format(short_link)
            self.cur.execute(query)
            self.conn.commit()
        else:
            return -1


    def change_link(self,old_link, short_link):
        if self.redisConn.exists(f"{old_link}"):
            long_link = self.redisConn.get(f"{old_link}")
            self.redisConn.delete(f"{old_link}")
            self.redisConn.set(f"{short_link}", long_link)
        else:
            return -1
        #add psql

    def create_tag(self, short_link, tag, id_user):
        tag = lower(tag)
        if self.redisConn.exists(f"{short_link}"):
            query_url_id = "select url_id from urls_data where redis_key = '{0}'".format(short_link)
            self.cur.execute(query_url_id)
            url_id = self.cur.fetchone()[0]

            total_tags_query = "select count(distinct tag_id) from url_tags where url_id = '{0}'".format(url_id)
            self.cur.execute(total_tags_query)
            total_tags = self.cur.fetchone()[0]
            if total_tags <= 4:
                # primero chequeo si existe la tag para el usuario
                fetch_tag = "select tag_id from user_tags where user_id = '{0}' and tag_name = '{1}'".format(id_user, tag)
                self.cur.execute(fetch_tag)
                tag_id = self.cur.fetchone()
                if tag_id == None:
                    create_tag = "insert into user_tags(user_id, tag_name) values ('{0}','{1}')".format(id_user, tag)
                    self.cur.execute(create_tag)
                    self.conn.commit()
                    self.cur.execute(fetch_tag)
                    tag_id = self.cur.fetchone()[0]
                else:
                    tag_id = tag_id[0]

                # asociar tag a url
                url_query = "insert into url_tags(tag_id, url_id) values ('{0}','{1}')".format(tag_id, url_id)
                self.cur.execute(url_query)
                self.conn.commit()
            else:
                return -2
        else:
            return -1