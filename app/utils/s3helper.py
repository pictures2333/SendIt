from typing import Tuple
import os
import io
import time
import secrets
import hashlib

from minio import Minio
from minio.lifecycleconfig import LifecycleConfig, Rule, Expiration

from config import BUCKET, OBJ_EXPIRE

# client object
client = Minio(os.getenv("MINIO_HOST"),
    access_key=os.getenv("MINIO_ACCESS_KEY"),
    secret_key=os.getenv("MINIO_SECRET_KEY"),
    secure=False # no https
)


# if not found, new bucket
def build():
    if not client.bucket_exists(BUCKET):
        # create
        client.make_bucket(BUCKET)
    
        # expire rule
        rule = Rule(
            rule_id="auto-delete",
            status="Enabled",
            expiration=Expiration(days=(OBJ_EXPIRE/24))
        )
        lifecycle_config = LifecycleConfig([rule])
        client.set_bucket_lifecycle(BUCKET, lifecycle_config)


# upload
def upload(filename:str, user:dict, binary:bytes) -> Tuple[str, int]:
    seed = (str(time.time()) + secrets.token_urlsafe(nbytes=16)).encode()
    code = hashlib.sha1(seed).hexdigest()[:10]
    
    try:
        with io.BytesIO(binary) as fp:
            client.put_object(bucket_name=BUCKET,
                              object_name=code,
                              data=fp,
                              length=len(binary),
                              metadata={"filename":filename,"username":user["username"]})
    except:
        return "", 1
    
    return code, 0


# download
def download(code:str) -> Tuple[dict, int]:
    try:
        # filename
        obinfo = client.stat_object(BUCKET, code)
        filename = obinfo.metadata.get("x-amz-meta-filename")
        author = obinfo.metadata.get("x-amz-meta-username")
        
        # file object
        file = client.get_object(BUCKET, code)
        fdata = file.data
        
        # release
        file.close()
        file.release_conn()
        
        # delete after download
        client.remove_object(BUCKET, code)
        
        return {"filename":filename, "username":author, "data":fdata}, 0
    except:
        return b"", 1
