from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os

db_url = os.environ.get('DATABASE_URL', 'sqlite:////tmp/test.db')
engine = create_engine(db_url, convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))

Base = declarative_base()
Base.query = db_session.query_property()

def init_db():
    import model
    Base.metadata.create_all(bind=engine)

if __name__ == '__main__':
    init_db()
