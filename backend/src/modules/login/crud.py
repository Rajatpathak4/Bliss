from fastapi import Depends, status
from datetime import timedelta, datetime
from sqlalchemy import or_, and_
from helper.customhelper import print_error_with_linenumebr, bcrypt_context, create_access_token, printCustmMsg
from helper import customhelper
from modules.login.models import LoginTokens, Users


DASHBOARD_REDIRECT_URL = "/dashboard"

def check_user_schema(user_schema):
    if not user_schema.email or not user_schema.password:
        return printCustmMsg(
            200, 'FALSE', "Either email or password is missing"
        )
    return None


def user_login(user_schema, db):
    try:
        schema_status = check_user_schema(user_schema)
        if schema_status:
            return schema_status

        user = (
            db.query(Users)
            .filter(
                Users.email == user_schema.email.lower(),
                Users.is_deleted == False,   # noqa: E712  soft-delete guard
            )
            .first()
        )

        # 3. Same generic message for "no user" and "wrong password"
        #    (don't leak which emails exist)
        if user is None or not bcrypt_context.verify(
            user_schema.password, user.password
        ):
            return printCustmMsg(200, 'FALSE', "Incorrect Email or Password")

        # 4. Clean up any expired tokens, then check for a live one
        now = datetime.now()
        db.query(LoginTokens).filter(
            LoginTokens.user_id == user.id,
            LoginTokens.expires_at < now,
        ).delete(synchronize_session=False)

        existing_token = (
            db.query(LoginTokens)
            .filter(
                LoginTokens.user_id == user.id,
                LoginTokens.expires_at >= now,
            )
            .first()
        )
        if existing_token:
            return printCustmMsg(200, 'FALSE', "You've already logged in")

        expiry_minutes = 180
        access_token = create_access_token(
            user.email, user.id, timedelta(minutes=expiry_minutes)
        )

        user.last_login = now
        db.add(LoginTokens(
            token=access_token,
            user_id=user.id,
            created_at=now,
            expires_at=now + timedelta(minutes=expiry_minutes),
        ))

        user_dict = {
            "uid": user.id,
            "first_name": user.name.upper() if user.name else None,
            "last_name": None,
            "name": user.name,
            "email": user.email,
            "token": access_token,
            "first_redirection": DASHBOARD_REDIRECT_URL,
            "last_login": user.last_login,
            "redirectUrl": DASHBOARD_REDIRECT_URL,
            "is_active": user.is_active,
            "current_time": now,
        }

        db.commit()
        return printCustmMsg(
            status.HTTP_200_OK, 'TRUE', "Login successfully", user_dict
        )

    except Exception as e:
        db.rollback()
        print_error_with_linenumebr(e)
        return printCustmMsg(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            'FALSE',
            "Something went wrong. Please try after some time",
        )

def update_auth_token(user_schema, db):
    try:
        schema_status = check_user_schema(user_schema)
        if schema_status:
            return schema_status

        user = db.query(Users).filter(Users.email == user_schema.email.lower(),Users.is_deleted == False).first()

        if user is None or not bcrypt_context.verify(user_schema.password, user.password):
            return printCustmMsg(status.HTTP_400_BAD_REQUEST,'FALSE',"Invalid credentials")
        now = datetime.now()

        db.query(LoginTokens).filter(LoginTokens.user_id == user.id,).delete(synchronize_session=False)

        access_token = create_access_token(user.email, user.id, timedelta(minutes=180))
        user.last_login = now

        db.add(LoginTokens(
            token=access_token,
            user_id=user.id,
            created_at=now,
            expires_at=now + timedelta(minutes=180),
        ))
        db.flush()

        user_dict = {
            "uid": user.id,
            "first_name": user.name.upper() if user.name else None,
            "last_name": None,
            "name": user.name,
            "email": user.email,
            "token": access_token,
            "first_redirection": DASHBOARD_REDIRECT_URL,
            "last_login": user.last_login,
            "redirectUrl": DASHBOARD_REDIRECT_URL,
            "is_active": user.is_active,
            "current_time": now,
        }

        response = printCustmMsg(status.HTTP_200_OK,'TRUE',"Re-Login successfully",user_dict,)
        db.commit()
        return response

    except Exception as e:
        db.rollback()
        print_error_with_linenumebr(e)
        return printCustmMsg(status.HTTP_500_INTERNAL_SERVER_ERROR,'FALSE',"Something went wrong. Please try after some time",)

