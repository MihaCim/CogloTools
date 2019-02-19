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
           (pe character varying(6),
            postna_stevilka bigint,
            gemoetry public.geometry,
            vrsta_posta character varying(30),
            vrsta_poste2 character varying(30) )'''
        cur.execute(select,)
        self.connection_osm.commit()
        cur.close()

    def insert(self,pe, postna_stevilka, lat, lon, vrsta_poste, vrsta_poste2):
        cur = self.connection_osm.cursor()
        select = '''
            INSERT INTO public.post_offices(
            pe, postna_stevilka, gemoetry, vrsta_posta, vrsta_poste2)  VALUES (%s, %s, ST_GeomFromText('POINT( %s %s)', 4326), %s, %s);'''
        cur.execute(select, (pe, postna_stevilka, lat, lon, vrsta_poste, vrsta_poste2))
        self.connection_osm.commit()
        cur.close()