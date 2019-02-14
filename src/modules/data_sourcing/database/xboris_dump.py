from sqlalchemy import create_engine
from sqlalchemy import Column, String, BigInteger, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

db_string = "postgres://admin:donotusethispassword@aws-us-east-1-portal.19.dblayer.com:15813/compose"

db = create_engine(db_string)
base = declarative_base()

class XBorISEvent(base):
    __tablename__ = 'ps_events'

    event_id = Column(String, primary_key=True)
    timestamp = Column(BigInteger)
    data = Column(JSON)

Session = sessionmaker(db)
session = Session()

base.metadata.create_all(db)

# Create
doctor_strange = XBorISEvent(title="Doctor Strange", director="Scott Derrickson", year="2016")
session.add(doctor_strange)
session.commit()

# Read
films = session.query(XBorISEvent)
for film in films:
    print(film.title)

# Update
doctor_strange.title = "Some2016Film"
session.commit()

# Delete
session.delete(doctor_strange)
session.commit()