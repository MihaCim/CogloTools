import os
import pexpect


class psql_to_database:
    def __init__(self,db_handler_osm, config_osm, logging):
        self.logging = logging
        self.folder = config_osm['folder']
        self.log_file = self.folder + "/log.txt"
        self.last_update_file = self.folder + "/last_update.txt"

        self.db_name = config_osm['dbname']
        self.db_host = config_osm['host']
        self.db_port = config_osm['port']
        self.db_user = config_osm['user']
        self.db_password = config_osm['password']
        self.osm_file = config_osm['osm_file']
        self.db_handler_osm = db_handler_osm

        self.cache_size = config_osm['cache_size']
        self.osm2pgsql_number_processes = config_osm['number_processes']

        self.style_file = config_osm['style_file']

        self.fout = open(self.log_file, 'ab')



    def transform_pbf_to_psql(self):
        self.thread_transform()


    def thread_transform(self):
        args = []
        for file in sorted(os.listdir(self.osm_file)):
            if file.endswith(".pbf"):
                path = os.path.join(self.osm_file, file)
                arg = {'path': path}
                self.thread_transform_worker(arg)
                args.append(arg)



    def thread_transform_worker(self, args):
        from random import randint
        from time import sleep

        sleep(randint(0, 10))

        self.osm_postgis_transform(self.db_name, self.cache_size, self.osm2pgsql_number_processes, self.db_host,
                                   self.db_port, self.db_user,
                                   self.style_file, args['path'], 'create')
        #self.check_if_update(args['check'])
        self.logging.info('Finished')



    def file_read(self):
        f = open(self.last_update_file, "r")
        return f.read().split(',')



    def osm_postgis_transform(self, db_name, cache_size, osm2pgsql_number_processes, db_host, db_port, db_user,
                              style_file, osm_files, mode, prefix = 'test'):

        osm2pgsql_proc = pexpect.spawn(
            ' '.join(["osm2pgsql", "--" + mode,
                      "--database", db_name,
                      "--cache", str(cache_size),
                      "--number-processes", str(osm2pgsql_number_processes),
                      "--prefix", prefix,
                      "--slim",
                      "--port", str(db_port),
                      "--host", db_host,
                      "--username", db_user,
                      # "--latlong",
                      "--password", "--keep-coastlines",
                      "--extra-attributes", "--hstore-all",
                      # "--style",style_file,
                      osm_files]))


        osm2pgsql_proc.logfile = self.fout
        osm2pgsql_proc.expect('Password:')
        osm2pgsql_proc.sendline(self.db_password)
        osm2pgsql_proc.timeout = 100000000
        osm2pgsql_proc.expect(pexpect.EOF)
