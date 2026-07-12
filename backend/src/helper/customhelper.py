from operator import and_
import shutil
from fastapi import Path
import pandas as pd
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Query
import math
import os
import sys
from helper import customhelper
from datetime import datetime, timedelta
from config import get_setting
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from jose import jwt


configObj = get_setting()

SECRET_KEY = configObj.SECRET_KEY
ALGORITHM = configObj.ALGORITHM

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(name: str, user_id: int, expiry_time: timedelta):
    encode = {"sub": name, "id": user_id}
    expires = datetime.utcnow() + expiry_time
    encode.update({"exp": expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

def print_error_with_linenumebr(e):   
    exc_type, exc_obj, exc_tb = sys.exc_info()        
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]        
    print(exc_type, fname, exc_tb.tb_lineno)
    print(str(e))

def pagination(query:Query,page_no=1,limit=10):
    '''
    parameters:
    query:data_base query object
    page_no:int = 1
    limit:int = 10
    return:dict{}
    '''
    db_records = query.all()
    total_pages = math.ceil(len(db_records)/limit)
    limited_records =  query.offset((page_no - 1) * limit).limit(limit).all()
    return {
        'db_data': limited_records,
        'pagination': {
            'total_records':len(db_records),
            'total_pages':total_pages,
            'current_page':page_no,
            'items_per_page':limit
        }
    }

def create_upload_file(file, destination_folder, new_filename):
    upload_folder = Path(destination_folder)
    upload_folder.mkdir(parents=True, exist_ok=True)

    file_path = upload_folder / new_filename

    try:
        with file_path.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return True
    
    except Exception as e:
        customhelper.print_error_with_linenumber(e)
        print(f"Error uploading file: {e}")

    return {"filename": file.filename}

def get_color():
    """
    Returns the next color code in the list.
    After cycling through the list, returns the colors in reverse order.
    """
    color_codes = [
        "#48cae4", "#4361ee", "#598392", "#bd632f", "#f7ebec",
        "#ff74d4", "#ffefa9", "#f15bb5", "#709775", "#ab81cd",
        "#ab947e", "#99e2b4", "#fc9e4f", "#bcabae", "#73d2de",
        "#f4f1bb", "#e5b3fe", "#cfdbd5", "#ffc4d6", "#C0C0C0",
        "#FFA500", "#A52A2A", "#F0E68C", "#ADD8E6", "#80ed99"
    ]
    
    if not hasattr(get_color, "index"):
        get_color.index = 0
        get_color.direction = 1

    color_index = get_color.index
    color = color_codes[color_index]

    get_color.index += get_color.direction

    if get_color.index == len(color_codes) or get_color.index == -1:
        get_color.direction *= -1
        get_color.index += get_color.direction * 2

    return color

def printCustmMsg(statusCode = 200, type = 'TRUE', msg = '', value = None, db = None, request = None, payload = None, subject_type = None, event = None, log_name = None):
    if statusCode in [200,201] and value is not None:
        resp = {"status": type,"message": msg, "value": value}
        #  if request:
        return resp
    else: 
         resp = JSONResponse(status_code=statusCode,content={"status": type, "message": msg})
         return resp

def do_nothing(*_, **__):
    return None

def safe_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def parse_date(value):
    if value is None:
        return None
    ts = pd.to_datetime(value, dayfirst=True, errors='coerce')
    if pd.isna(ts):
        return None
    return ts.date() if ts.time() == pd.Timestamp(0).time() else ts.to_pydatetime()