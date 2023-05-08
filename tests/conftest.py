import pytest
from datetime import datetime
from models import Base, User, Advertising
from config import PG_DB, PG_PORT, PG_HOST, PG_USER, PG_PASSWORD
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from auth import hash_password


engine = create_engine(f'postgresql://{PG_USER}:{PG_PASSWORD}@'
                       f'{PG_HOST}:{PG_PORT}/{PG_DB}')
Session = sessionmaker(bind=engine)


@pytest.fixture(scope='session', autouse=True)
def cleanup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield


@pytest.fixture(scope='session')
def root_user():
    with Session() as session:
        new_user = User(
            name='root',
            admin=True,
            psw=hash_password('toor'),
            mail='root@mail.ru'
            )
        session.add(new_user)
        session.commit()
        return {
            'id': new_user.id,
            'name': new_user.name,
            'admin': new_user.admin,
            'psw': 'toor',
            'mail': new_user.mail
        }


@pytest.fixture(scope='session', autouse=True)
def new_user():
    with Session() as session:
        new_user = User(name=f'user777_{datetime.now().time()}',
                        admin=True,
                        psw=hash_password('toor2'),
                        mail='root2@mail.ru'
                        )
        session.add(new_user)
        session.commit()
        return {
            'id': new_user.id,
            'name': new_user.name,
            'admin': new_user.admin,
            'psw': 'toor2',
            'mail': new_user.mail
        }


@pytest.fixture(scope='session', autouse=True)
def new_adv(new_user):
    with Session() as session:
        new_adv = Advertising(owner_id=new_user['id'],
                              title=f'Titlyatina_{datetime.now().time()}',
                              description='About_text'
                              )
        session.add(new_adv)
        session.commit()
        return {
            'id': new_adv.id,
            'owner_id': new_user['id'],
            'title': new_adv.title,
            'description': new_adv.description,
        }
