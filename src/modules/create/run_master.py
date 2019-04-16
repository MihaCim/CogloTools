import logging

from src.modules.create.utils import parms_parser

from src.modules.create.dbs import db_handler_osm as osm_handler

from src.modules.create import script_0_psql_to_database
from src.modules.create import script_1_csv_importer
from src.modules.create import script_2_search


def process_data(params, logger=None):
    if logger is None:
        logger = logging.getLogger('dummy')
        logger.addHandler(logging.NullHandler())

    db_handler_osm = osm_handler.db_handler_osm(params.osm['conn_string'], logger)
    psql_to_database = script_0_psql_to_database.psql_to_database(db_handler_osm, params.osm, logger)
    import_postaloffices = script_1_csv_importer.csv_importer(db_handler_osm, params.osm, logger)
    search_shortast_path = script_2_search.search_shortest_path(db_handler_osm, params.osm, logger)

    if params.args.export_osm2postgres:
        psql_to_database.transform_pbf_to_psql()

    if params.args.import_postalOfices:
        import_postaloffices.import_postal()

    if params.args.search_shortest_path:
        search_shortast_path.search()



def main():
    #TODO ali je treba nastaviti pot ?
    #https://docs.python.org/2/library/logging.html#logrecord-attributes
    FORMAT = '%(asctime)-15s %(filename)s %(levelname)s %(message)s'
    logging.basicConfig(format=FORMAT)

    logger = logging.getLogger('osm transforming')
    logger.setLevel('INFO')
    params = parms_parser.ParmsParser()
    params.read_config(params.args.config_file)
    process_data(params, logger)



if __name__ == '__main__':
    main()