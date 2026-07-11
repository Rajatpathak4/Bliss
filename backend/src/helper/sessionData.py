sessionuserData={}
from fastapi import Request


def getSessionUserId(request):
    return request.session.get('userData')['id']


def getSessionUserName(request):
    return request.session.get('userData')['name']


def getSessionUserEmail(request):
    return request.session.get('userData')['email']


def getSessionUserOrgName(request):
    return request.session.get('userData')['orgname']


def getSessionUserType(request):
    return request.session.get('userData')['user_type']


def getSessionUserCategoryId(request):
    return request.session.get('userData')['user_category_id']

def getSessionUserToken(request):
     return request.session.get('userData')['token'] if request.session.get('userData')['token'] else ''