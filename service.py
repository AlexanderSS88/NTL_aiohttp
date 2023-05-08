import datetime
import json
from sqlalchemy.future import select
from aiohttp import web
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from config import PG_DSN, TOKEN_TTL
from typing import Callable, Awaitable
from models import Base, User, Token, Advertising
from auth import hash_password, check_password


engine = create_async_engine(PG_DSN)
Session = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
    )


@web.middleware
async def session_middleware(
        request: web.Request,
        handler: Callable[[web.Request], Awaitable[web.Response]]
        ):
    async with Session() as session:
        request['session'] = session
        return await handler(request)


async def app_context(app: web.Application):
    async with engine.begin() as conn:
        async with Session() as session:
            await session.execute(
                'CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'
                )
            await session.commit()
        await conn.run_sync(Base.metadata.create_all)
    print('START')
    yield
    print('FINISH')
    await engine.dispose()


def raise_error(exception_class, message):
    raise exception_class(
        text=json.dumps({'status': 'error', 'message': message}),
        content_type='application/json'
        )


async def check_auth(request: web.Request):
    token_id = request.headers.get('token')
    if not token_id:
        raise_error(web.HTTPForbidden, message='incorrect token')
    try:
        token = await get_orm_item(Token, token_id, request['session'])
    except web.HTTPNotFound:
        raise_error(web.HTTPForbidden, message='incorrect token')
    if token.created + datetime.timedelta(seconds=TOKEN_TTL)\
            < datetime.datetime.utcnow():
        raise_error(web.HTTPForbidden, message='incorrect token')
    request['token'] = token


async def check_owner(request: web.Request, owner_id: int):
    if request['token'].user.id != owner_id:
        raise_error(web.HTTPForbidden, message='token incorrect')


async def get_orm_item(orm_class, object_id, session):
    item = await session.get(orm_class, object_id)
    if item is None:
        raise raise_error(
            web.HTTPNotFound,
            f'{orm_class.__name__} not found'
            )
    return item


async def login(request: web.Request):
    user_data = await request.json()
    query = select(User).where(User.name == user_data['name'])
    result = await request['session'].execute(query)
    user = result.scalar()
    if not user or not check_password(user_data['psw'],
                                      user.psw
                                      ):
        raise raise_error(web.HTTPUnauthorized,
                          message='user or password is incorrect'
                          )
    token = Token(user=user)
    request['session'].add(token)
    await request['session'].commit()
    return web.json_response({'status': 'success', 'token': token.id})


class UserView(web.View):

    async def get(self):
        user_id = int(self.request.match_info['user_id'])
        user = await get_orm_item(User,
                                  user_id,
                                  self.request['session']
                                  )
        return web.json_response({'id': user.id, 'name': user.name})

    async def post(self):
        user_data = await self.request.json()
        user_data['psw'] = hash_password(user_data['psw'])
        new_user = User(**user_data)
        self.request['session'].add(new_user)
        await self.request['session'].commit()
        return web.json_response({
            'status': 'success',
            'id': new_user.id
        })

    async def patch(self):
        user_id = int(self.request.match_info['user_id'])
        user = await get_orm_item(User,
                                  user_id,
                                  self.request['session']
                                  )
        user_data = await self.request.json()
        if 'psw' in user_data:
            user_data['psw'] = hash_password(user_data['psw'])
        for field, value in user_data.items():
            setattr(user, field, value)
        self.request['session'].add(user)
        await self.request['session'].commit()
        return web.json_response({'status': 'success'})

    async def delete(self):
        await check_auth(self.request)
        user_id = int(self.request.match_info['user_id'])
        await check_owner(self.request, user_id)
        user = await get_orm_item(User,
                                  user_id,
                                  self.request['session']
                                  )
        await self.request['session'].delete(user)
        await self.request['session'].commit()
        return web.json_response({'status': 'delete'})


class AdvertisingView(web.View):

    async def get(self):
        adv_id = int(self.request.match_info['adv_id'])
        adv = await get_orm_item(Advertising,
                                 adv_id,
                                 self.request['session']
                                 )
        return web.json_response({'id': adv.id, 'title': adv.title})

    async def post(self):
        adv_data = await self.request.json()
        new_adv = Advertising(**adv_data)
        self.request['session'].add(new_adv)
        await self.request['session'].commit()
        return web.json_response({
            'status': 'created',
            'adv_id': new_adv.id
            })

    async def patch(self):
        await check_auth(self.request)
        adv_id = int(self.request.match_info['adv_id'])
        adv = await get_orm_item(Advertising,
                                 adv_id,
                                 self.request['session']
                                 )
        adv_data = await self.request.json()
        for field, value in adv_data.items():
            setattr(adv, field, value)
        self.request['session'].add(adv)
        await self.request['session'].commit()
        return web.json_response({'status': 'success'})

    async def delete(self):
        await check_auth(self.request)
        adv_id = int(self.request.match_info['adv_id'])
        adv = await get_orm_item(Advertising,
                                 adv_id,
                                 self.request['session']
                                 )
        await self.request['session'].delete(adv)
        await self.request['session'].commit()
        return web.json_response({'status': 'delete'})



application = web.Application(middlewares=[session_middleware])
application.cleanup_ctx.append(app_context)

application.add_routes(
    [web.post('/login', login),
     web.post('/user/', UserView),
     web.get('/user/{user_id:\d+}', UserView),
     web.patch('/user/{user_id:\d+}', UserView),
     web.delete('/user/{user_id:\d+}', UserView),
     web.post('/user/adv/', AdvertisingView),
     web.patch('/user/adv/{adv_id:\d+}', AdvertisingView),
     web.delete('/user/adv/{adv_id:\d+}', AdvertisingView),
     web.get('/user/adv/{adv_id:\d+}', AdvertisingView)
     ]
)


if __name__ == '__main__':
    web.run_app(application, host='127.0.0.1', port=8080)
