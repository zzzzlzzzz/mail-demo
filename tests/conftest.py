from os import environ
import pytest

from skltech import create_app, db


@pytest.fixture('session', autouse=True)
def client():
    environ['SKLTECH_CONFIG'] = 'config.TestConfig'
    flask_app = create_app()
    with flask_app.app_context():
        with flask_app.test_client() as client:
            yield client


@pytest.fixture('module', autouse=True)
def create_database(client):
    db.Model.metadata.create_all(bind=db.get_engine())
    yield
    db.Model.metadata.drop_all(bind=db.get_engine())


@pytest.fixture('function', autouse=True)
def prepare_database(create_database):
    for _ in reversed(db.Model.metadata.sorted_tables):
        db.session.execute(_.delete())
    db.session.commit()
    yield
    db.session.rollback()


@pytest.fixture('module', autouse=True)
def database():
    return db
