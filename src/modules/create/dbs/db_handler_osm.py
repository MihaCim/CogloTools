import psycopg2


class db_handler_osm:

    def __init__(self, string, logging):
        self.con_string_osm = string
        self.logging = logging
        self.logging.info("Connecting to database\n	->%s" % (self.con_string_osm))
        self.logging.info(self.con_string_osm)
        self.connection_osm = psycopg2.connect(self.con_string_osm)



    def create_database(self):
        cur = self.connection_osm.cursor()
        select = '''
            DROP TABLE IF EXISTS public.post_offices;
            CREATE TABLE public.post_offices
           (pe character varying(2),
            postna_stevilka bigint,
            gemoetry public.geometry,
            vrsta_posta character varying(30),
            vrsta_poste2 character varying(30) )'''
        cur.execute(select,)
        self.connection_osm.commit()
        """
    def create_table(self):
        cur = self.connection_osm.cursor()
        select = " create table updated_table( " \
                 "iso varchar(2)," \
                 "country_name varchar(35) PRIMARY KEY," \
                 "created timestamp with time zone," \
                 "updated timestamp with time zone," \
                 "updated_id bigint)  "
        cur.execute(select,)
        self.connection_osm.commit()

    def insert_country(self,country_name,created):
        cur = self.connection_osm.cursor()
        select = ''' insert into updated_table(country_name,iso,created)
                    VALUES (%s,%s,%s) 
                    ON CONFLICT (country_name) DO
                    UPDATE SET created=%s
                    WHERE updated_table.country_name LIKE %s'''
        cur.execute(select,(country_name,self.country[country_name],created,created,country_name,))
        self.connection_osm.commit()
    
    def select_country(self, item):
        cur = self.connection_osm.cursor()
        # select = "SELECT name, country,way FROM public.countries; "
        select = "SELECT country,name FROM countries WHERE ST_COntains(way," \
                 "ST_SetSRID(ST_AsText(\'" + str(item) + "\'),4326));"
        cur.execute(select, )
        records = cur.fetchone()
        return records

    
    def contain_polygon(self,country_polygon,item):
        cur = self.connection_osm.cursor()
        select = "SELECT ST_Contains(ST_SetSRID(ST_AsText(\'"+str(country_polygon)+"\'),4326),ST_SetSRID(ST_AsText(\'"+str(item)+"\'),4326))";
        cur.execute(select,)
        record = cur.fetchone()
        return record[0]

    def retrieve_town(self, iso, way, distance):
        select = "SELECT osm_id, tags, ST_DistanceSphere(ST_Transform(way, 4326), ST_SetSRID(ST_AsText(%s), 4326)) FROM public." + iso + "_point WHERE(tags->'place' = 'city' or tags->'place' = 'town') and ST_DistanceSphere(ST_Transform(way, 4326), ST_SetSRID(ST_AsText(%s), 4326)) <=%s ORDER BY ST_DistanceSphere(ST_Transform(way, 4326), ST_SetSRID(ST_AsText(%s), 4326));"
        cur = self.connection_osm.cursor()
        cur.execute(select, ((way), (way), (str(distance)), (way),))
        records = cur.fetchall()
        return records
    """
