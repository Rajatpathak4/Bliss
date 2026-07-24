from fastapi import Depends, status
from datetime import timedelta, datetime
from sqlalchemy import or_, and_
from helper.customhelper import print_error_with_linenumebr, bcrypt_context, create_access_token, printCustmMsg
from helper import customhelper
from modules.login.models import LoginTokens, UserProfile, Users


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
                Users.is_deleted == False,  # noqa: E712
            )
            .first()
        )

        # Invalid email/password
        if user is None or not bcrypt_context.verify(
            user_schema.password, user.password
        ):
            return printCustmMsg(
                status.HTTP_200_OK,
                "FALSE",
                "Incorrect Email or Password"
            )

        now = datetime.now()

        # Delete expired tokens
        db.query(LoginTokens).filter(
            LoginTokens.user_id == user.id,
            LoginTokens.expires_at < now,
        ).delete(synchronize_session=False)

        # Check if user is already logged in
        existing_token = (
            db.query(LoginTokens)
            .filter(
                LoginTokens.user_id == user.id,
                LoginTokens.expires_at >= now,
            )
            .first()
        )

        if existing_token:
            return printCustmMsg(
                status.HTTP_200_OK,
                "FALSE",
                "You've already logged in.",
                {
                    "relogin_required": True
                }
            )

        expiry_minutes = 180

        access_token = create_access_token(
            user.email,
            user.id,
            timedelta(minutes=expiry_minutes)
        )

        user.last_login = now

        db.add(
            LoginTokens(
                token=access_token,
                user_id=user.id,
                created_at=now,
                expires_at=now + timedelta(minutes=expiry_minutes),
            )
        )

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
            status.HTTP_200_OK,
            "TRUE",
            "Login successfully",
            user_dict,
        )

    except Exception as e:
        db.rollback()
        print_error_with_linenumebr(e)

        return printCustmMsg(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "FALSE",
            "Something went wrong. Please try after some time",
        )

def update_auth_token(user_schema, db):
    try:
        schema_status = check_user_schema(user_schema)
        if schema_status:
            return schema_status

        user = (
            db.query(Users)
            .filter(
                Users.email == user_schema.email.lower(),
                Users.is_deleted == False
            )
            .first()
        )

        if user is None or not bcrypt_context.verify(
            user_schema.password,
            user.password
        ):
            return printCustmMsg(
                status.HTTP_400_BAD_REQUEST,
                "FALSE",
                "Invalid credentials"
            )

        now = datetime.now()

        # Remove all existing login sessions
        db.query(LoginTokens).filter(
            LoginTokens.user_id == user.id
        ).delete(synchronize_session=False)

        expiry_minutes = 180

        access_token = create_access_token(
            user.email,
            user.id,
            timedelta(minutes=expiry_minutes)
        )

        user.last_login = now

        db.add(
            LoginTokens(
                token=access_token,
                user_id=user.id,
                created_at=now,
                expires_at=now + timedelta(minutes=expiry_minutes),
            )
        )

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
            status.HTTP_200_OK,
            "TRUE",
            "Re-Login successfully",
            user_dict,
        )

    except Exception as e:
        db.rollback()
        print_error_with_linenumebr(e)

        return printCustmMsg(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "FALSE",
            "Something went wrong. Please try after some time",
        )

def get_user_profile(db, user_id):
    user = db.query(Users).filter(Users.id == user_id).first()
    if not user:
        return customhelper.printCustmMsg(200, 'FALSE', "User not found")

    profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()

    profile_data = {
        "id": user.id,
        "fullName": user.name,
        "email": user.email,
        "phone_number": profile.phone_number if profile else None,
        "role": profile.role if profile else None,
        "company": profile.company if profile else None,
        "location": profile.location if profile else None,
        "avatarUrl": profile.avatar_url if profile else None,
        "avatarInitials": "".join(w[0] for w in user.name.split()[:2]).upper() if user.name else "",
    }
    return customhelper.printCustmMsg(200, 'TRUE', "Profile fetched", profile_data)


def update_user_profile(db, user_id, payload):
    try:
        user = db.query(Users).filter(Users.id == user_id).first()
        if not user:
            return customhelper.printCustmMsg(200, 'FALSE', "User not found")

        update_data = payload.dict(exclude_unset=True)

        # naam/email Users table mein rehta hai
        if 'name' in update_data:
            user.name = update_data.pop('name')
        if 'email' in update_data:
            user.email = update_data.pop('email')

        # baaki fields UserProfile mein — row exist na kare to bana do (upsert)
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            profile = UserProfile(user_id=user_id)
            db.add(profile)

        for field_name, field_value in update_data.items():
            setattr(profile, field_name, field_value)

        db.commit()
        return customhelper.printCustmMsg(200, 'TRUE', "Profile updated successfully")
    except Exception:
        db.rollback()
        return customhelper.printCustmMsg(500, 'FALSE', "Something went wrong. Please try again.")


def update_user_avatar(db, user_id, avatar_url):
    try:
        profile = db.query(UserProfile).filter(UserProfile.user_id == user_id).first()
        if not profile:
            profile = UserProfile(user_id=user_id)
            db.add(profile)

        profile.avatar_url = avatar_url
        db.commit()
        return customhelper.printCustmMsg(200, 'TRUE', "Profile image updated", {"avatarUrl": avatar_url})
    except Exception:
        db.rollback()
        return customhelper.printCustmMsg(500, 'FALSE', "Something went wrong. Please try again.")