from typing import Tuple
import bcrypt

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from utils import SQLclass
from config import DBPATH

engine = create_engine(DBPATH)
SQLclass.Base.metadata.create_all(engine)

# utils
def get_session():
    Session = sessionmaker(bind=engine)
    return Session()

# users
def solo_user_create(username:str, password:str) -> Tuple[str, int]:
    # check args
    if (not username) or (not password):
        return "arguments error", 1
    
    # check repeat
    if solo_user_get(username):
        return "user exists", 1
    
    # execute
    with get_session() as session:
        try:
            user = SQLclass.SQLuser(
                username=username,
                password=bcrypt.hashpw(password=password.encode(),
                                   salt=bcrypt.gensalt()).decode()
            )
            session.add(user)
            session.commit()
        except:
            session.rollback()
            return "error", 1
    return "", 0


def solo_user_delete(username:str) -> int:
    # execute
    user = SQLclass.SQLuser
    with get_session() as session:
        try:
            target = session.query(user).filter(user.username==username).first()
            if not target:
                return 1
            session.delete(target)
            session.commit()
        except:
            session.rollback()
            return 1
    return 0

        
def solo_user_get(key, type:str="username", password:str=None) -> dict:
    # fetch
    user = SQLclass.SQLuser
    with get_session() as session:
        res = session.query(user)
        if type == "username" or type == "auth":
            res = res.filter(user.username==str(key))
        elif type == "id":
            res = res.filter(user.id==int(key))
        res = res.first()
    
    # return
    if res:
        if type == "auth": # auth:check password
            if not bcrypt.checkpw(password=password.encode(),
                                  hashed_password=res.password.encode()):
                return None
        return {"id":res.id, "username":res.username}
    else:
        return None
