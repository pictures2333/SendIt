from typing import Tuple

import jwt

from utils import dbhelper

def auth(session, secret_key) -> Tuple[dict, int]:
    # decode
    try:
        user = jwt.decode(jwt=session, key=secret_key, algorithms=["HS256"])
    except jwt.exceptions.ExpiredSignatureError:
        return {"result":"expired"}, 1
    except jwt.exceptions.DecodeError:
        return {"result":"decode error"}, 1
    except:
        return {"result":"unknown error"}, 1
    
    # find user
    dbu = dbhelper.solo_user_get(key=user["id"], type="id")
    if not dbu:
        return {"result":"user not found"}, 1
    
    # return
    return dbu, 0
