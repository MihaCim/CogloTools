from sqlalchemy import create_engine, Table, select
from sqlalchemy import Column, String, BigInteger, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import logging

base = declarative_base()


class XBorISEvent(base):
    __tablename__ = 'ps_events'

    event_id = Column(String, primary_key=True)
    timestamp = Column(BigInteger)
    data = Column(JSON)


class PostgresConnector():

    def __init__(self, username="postgres", password="", host="127.0.0.1", port=5432, db_name="postgres"):
        user = username
        if password != "":
            user = user + ":" + password
        self._logger = logging.getLogger(self.__class__.__name__ + "_logger")
        self.conn_string = "postgres://{}@{}:{}/{}".format(user, host, port, db_name)

        self._logger.debug(self.conn_string)

        self.db = create_engine(self.conn_string)

        Session = sessionmaker(self.db)
        self.session = Session()

        base.metadata.create_all(self.db)

    def store(self, dat):
        for d in dat:
            self.session.add(d)
        self.session.commit()

    def retrieve_ids(self, age=0):
        query = select([XBorISEvent.event_id]).select_from(XBorISEvent).where(XBorISEvent.timestamp > age)
        data = self.db.execute(query)

        return [x[0] for x in data]
