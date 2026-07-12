from typing import Optional

from fastapi import APIRouter,Depends, File, UploadFile, status
from config import get_setting
from database.database import get_db
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, Request
from helper import customhelper
from dependencies import tokenvalidation,is_readable
from helper import customhelper
from modules.Upload_Excel import crud
from modules.Upload_Excel.schemas import UserExcelSchema

is_valid = [Depends(tokenvalidation),Depends(is_readable)]
routes = APIRouter(
    tags=["Reports"],
    dependencies=is_valid
)
configObj = get_setting()

@routes.post('/upload_user_excel')
def upload_user_excel(files: UploadFile = File(...), db:Session= Depends(get_db), serviceRequest: Request = None):
   try:
      response = crud.upload_excel(files, db, serviceRequest)
      return response
   except Exception as err:
      customhelper.print_error_with_linenumebr(err)
      return customhelper.printCustmMsg(500,'FALSE',f"Exception {type(err).__name__} occurs.")  
   
@routes.get('/delete_user_excel')
def delete_user_excel(policy_number:Optional[str], db:Session= Depends(get_db), serviceRequest: Request = None):
   try:
      response = crud.delete_user(policy_number, db, serviceRequest)
      return response
   except Exception as err:
      customhelper.print_error_with_linenumebr(err)
      return customhelper.printCustmMsg(500,'FALSE',f"Exception {type(err).__name__} occurs.")
   
@routes.get("/get_user_table_data")
def get_user_table_data(
    page_no: int = 1,
    limit: int = 10,
    search: str = None,
    db: Session = Depends(get_db),
    serviceRequest: Request = None
):
    try:
        response = crud.get_user_table_data(
            page_no=page_no, limit=limit, db=db,
            serviceRequest=serviceRequest, search=search
        )
        return response

    except Exception as err:
        customhelper.print_error_with_linenumebr(err)
        return customhelper.printCustmMsg(500, "FALSE", f"Exception {type(err).__name__} occurs.")

@routes.get('/user_modal_data')
def user_modal_data(user_id:Optional[int], db:Session= Depends(get_db), serviceRequest: Request = None):
   try:
      response = crud.user_modal_data(user_id, db, serviceRequest)
      return response
   except Exception as err:
      customhelper.print_error_with_linenumebr(err)
      return customhelper.printCustmMsg(500,'FALSE',f"Exception {type(err).__name__} occurs.")
   
@routes.post('/add_user_data')
def add_user_data(userData: UserExcelSchema, db:Session= Depends(get_db), serviceRequest: Request = None):
   try:
      response = crud.add_user_data(userData, db, serviceRequest)
      print(userData)
      print(userData.model_dump())
      print(userData.agent_code)
      return response
   except Exception as err:
      customhelper.print_error_with_linenumebr(err)
      return customhelper.printCustmMsg(500,'FALSE',f"Exception {type(err).__name__} occurs.")
   
@routes.post('/update_user_data')
def update_user_data(userData: UserExcelSchema, db:Session= Depends(get_db), serviceRequest: Request = None):
   try:
      response = crud.update_user_data(userData, db, serviceRequest)
      return response
   except Exception as err:
      customhelper.print_error_with_linenumebr(err)
      return customhelper.printCustmMsg(500,'FALSE',f"Exception {type(err).__name__} occurs.")
   
@routes.get('/get_active_client')
def get_active_client(db:Session= Depends(get_db), serviceRequest: Request = None):
   try:
      response = crud.get_active_client(db, serviceRequest)
      return response
   except Exception as err:
      customhelper.print_error_with_linenumebr(err)
      return customhelper.printCustmMsg(500,'FALSE',f"Exception {type(err).__name__} occurs.")
   
@routes.get('/get_premium_stats')
def get_premium_stats(db:Session= Depends(get_db), serviceRequest: Request = None):
   try:
      response = crud.get_premium_stats(db, serviceRequest)
      return response
   except Exception as err:
      customhelper.print_error_with_linenumebr(err)
      return customhelper.printCustmMsg(500,'FALSE',f"Exception {type(err).__name__} occurs.")
   
@routes.get('/chart_data')
def get_dashboard_chart_data(db: Session = Depends(get_db), serviceRequest: Request = None):
   try:
      response = crud.get_dashboard_chart_data(db, serviceRequest)
      return response
   except Exception as err:
      customhelper.print_error_with_linenumebr(err)
      return customhelper.printCustmMsg(500,'FALSE',f"Exception {type(err).__name__} occurs.")