from sqlalchemy import MetaData
from sqlalchemy.orm import sessionmaker

from cv_db.database.tables import *

class Database:
    def __init__(self, engine, create=False):
        """
        constructor for Database class
        :param engine: sqlalchemy engine
        :param create: whether or not to create tables, if you are connecting to an existing database do not create it
        """
        self.engine=engine
        if create:
            Base.metadata.create_all(self.engine)
        self.meta = MetaData(bind=self.engine)
        self.meta.reflect(bind=self.engine)
        sess=sessionmaker(bind=self.engine)
        self.session = sess()
        self.db_tables = self.meta.tables

    # This is the same as chirpp query just paste it in
    def query(self, query):
        """
        query the database
        :param query: query dictionary specifying what to look for. TBD
        :return:
        """
        pass




