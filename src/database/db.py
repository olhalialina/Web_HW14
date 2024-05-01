from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException, status

from src.config.config import settings

url = settings.sqlalchemy_database_url
engine = create_engine(url, echo=True, pool_size=5)

DBSession = sessionmaker(bind=engine, autocommit=False, autoflush=False)


# Dependency
def get_db():
    """
    The get_db function is a context manager that creates a database session and yields it.
    The yield statement suspends the execution of get_db() and returns control to the caller.
    When the with block ends, execution resumes in get_db(), where any exceptions are caught,
    the session is rolled back (if necessary), and then closed.

    :return: A database session
    """
    db = DBSession()
    try:
        yield db
    except SQLAlchemyError as err:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(err))
    finally:
        db.close()