import os
import string
import random
import datetime

from django.db.models import Q
from django.http import JsonResponse
from app1.models import *
from django.template.context_processors import csrf
from django.core.mail import send_mail

import time

from djangoProject import settings


# Create your views here.

def get_csrf(request):
    if request.method == 'GET':
        x = csrf(request)
        csrf_token = x.get('csrf_token')
        return JsonResponse({
            "code": 20000,
            "csrf_token": str(csrf_token)
        })


def post_csrf(request):
    if request.method == 'POST':
        csrf_token = request.POST.get('csrf_token')
        return JsonResponse({
            "code": 20000
        })


def checkVerifyCode(email, verifyCode, sendType):
    try:
        emailVerify = EmailVerify.objects.get(email=email)
        sendTime = emailVerify.sendTime
        if sendTime + datetime.timedelta(minutes=settings.EMAIL_EXPIRE) < datetime.datetime.now():
            emailVerify.delete()
            return False, "验证码过期"
        else:
            if verifyCode == emailVerify.code and sendType == emailVerify.sendType:
                emailVerify.delete()
                return True, "验证成功"
            else:
                return False, "验证码错误"
    except EmailVerify.DoesNotExist:
        return False, "请先发送验证码"


def register(request):
    name = request.POST.get('username')
    password = request.POST.get('password')
    email = request.POST.get('email')
    phone = request.POST.get('phone')
    verifyCode = request.POST.get('verifyCode')

    # 判断name是否已存在
    users = User.objects.filter(name=name)
    if users.exists():
        return JsonResponse(
            {
                "code": 100,
                "msg": "用户名已存在",
            }
        )
    verified, msg = checkVerifyCode(email, verifyCode, 'register')
    if verified:
        user = User()
        user.name = name
        user.password = password  # TODO：md5加密
        user.email = email
        if phone:
            user.phone = phone
        user.save()
        return JsonResponse(
            {
                "code": 20000,
                "msg": "注册成功",
            }
        )
    else:
        return JsonResponse({
            "code": 100,
            "msg": msg
        })


def login(request):
    uid = request.POST.get('uid')  # TODO: 分辨手机号和邮箱
    password = request.POST.get('password')

    real_password = password  # TODO: md5加密

    pass  # TODO: 手机号
    if '@' in uid:
        users = User.objects.filter(email=uid, password=real_password)
    else:
        users = User.objects.filter(name=uid, password=real_password)
    if users.exists():
        user = users.first()

        request.session['userid'] = user.id
        request.session.set_expiry(24 * 3600)

        return JsonResponse(
            {
                "code": 20000,
                "msg": "登录成功",
                "data": user.isAdmin
            }
        )
    else:
        return JsonResponse(
            {
                "code": 100,
                "msg": "用户名或密码错误",
                "data": False
            }
        )


def logout(request):
    session_key = request.session.session_key
    request.session.delete(session_key)
    return JsonResponse(
        {
            "code": 20000,
            "msg": "登出成功"
        }
    )


def change_password(request):
    if request.method == "POST":
        old_password = request.POST.get('oldPassword')
        new_password = request.POST.get('newPassword')
        try:
            user = User.objects.get(id=request.session['userid'])
        except Exception:
            return JsonResponse({
                "code": 100,
                "msg": "未登录"
            })
        if user.password == old_password:
            user.password = new_password
            user.save(update_fields=["password"])
            return JsonResponse(
                {
                    "code": 20000,
                    "msg": "修改密码成功"
                }
            )
        else:
            return JsonResponse(
                {
                    "code": 100,
                    "msg": "原密码错误"
                }
            )


def forget_password(request):
    if request.method == "POST":
        try:
            email = request.POST.get('email')
            verifyCode = request.POST.get('verifyCode')
            password = request.POST.get('password')
            try:
                user = User.objects.get(email=email)
            except Exception:
                return JsonResponse({
                    "code": 100,
                    "msg": "请输入正确的邮箱"
                })
            verified, msg = checkVerifyCode(email, verifyCode, 'forget')
            if verified:
                user.password = password
                user.save()
                return JsonResponse({
                    "code": 20000,
                    "msg": "密码修改成功"
                })
            else:
                return JsonResponse({
                    "code": 100,
                    "msg": msg
                })

        except Exception:
            return JsonResponse({
                "code": 100,
                "msg": "邮箱不存在"
            })


def getUserInfo(request):
    if request.method == "GET":
        try:
            user = User.objects.get(id=request.session['userid'])
        except Exception:
            return JsonResponse({
                "code": 100,
                "msg": "未登录"
            })
        return JsonResponse(
            {
                "code": 20000,
                "msg": "success",
                "data": {
                    "username": user.name,
                    "avatar": user.avatar,
                    "phone": user.phone,
                    "email": user.email,
                    "isAdmin": user.isAdmin
                }
            }
        )


def userCity(request):
    if request.method == "GET":
        try:
            user = User.objects.get(id=request.session['userid'])
        except Exception:
            return JsonResponse({
                "code": 100,
                "msg": "未登录"
            })
        user_cities = user.cities
        if len(user_cities) == 0:
            user_cities = []
        else:
            user_cities = user_cities.split('/')

        return JsonResponse(
            {
                "code": 20000,
                "msg": "success",
                "data": user_cities
            }
        )
    if request.method == "DELETE":
        try:
            user = User.objects.get(id=request.session['userid'])
        except Exception:
            return JsonResponse({
                "code": 100,
                "msg": "未登录"
            })
        city = request.GET.get('city')
        user_cities = user.cities
        if len(user_cities) == 0:
            user_cities = []
        else:
            user_cities = user_cities.split('/')
        try:
            index = user_cities.index(city)
        except Exception:
            index = -1

        if index == -1:
            return JsonResponse({
                "code": 100,
                "msg": "取消订阅失败！并无对此城市的订阅！"
            })
        else:
            del user_cities[index]
            user_cities = '/'.join(user_cities)
            user.cities = user_cities
            user.save(update_fields=["cities"])
            return JsonResponse(
                {
                    "code": 20000,
                    "msg": "取消订阅成功"
                }
            )
    if request.method == "POST":
        try:
            user = User.objects.get(id=request.session['userid'])
        except Exception:
            return JsonResponse({
                "code": 100,
                "msg": "未登录"
            })
        city = request.POST.get('city')
        user_cities = user.cities
        if len(user_cities) == 0:
            user_cities = []
        else:
            user_cities = user_cities.split('/')
        try:
            index = user_cities.index(city)
        except Exception:
            index = -1

        if index == -1:
            user_cities.append(city)
            user.cities = '/'.join(user_cities)
            user.save(update_fields=["cities"])
            return JsonResponse({
                "code": 20000,
                "msg": "订阅成功"
            })
        else:
            return JsonResponse({
                "code": 100,
                "msg": "订阅失败！已订阅该城市"
            })


def user_feedback(request):
    if request.method == "GET":
        try:
            user = User.objects.get(id=request.session['userid'])
        except Exception:
            return JsonResponse({
                "code": 100,
                "msg": "未登录"
            })
        feedback = user.feedback_set.all()
        return JsonResponse(
            {
                "code": 20000,
                "msg": "success",
                "data": [{
                    "title": f.title,
                    "content": f.content,
                    "reply": f.reply,
                    "status": f.status,
                    "updateTime": f.updated.strftime("%Y-%m-%d %H:%M:%S"),
                } for f in feedback]
            }
        )
    if request.method == "POST":
        try:
            user = User.objects.get(id=request.session['userid'])
        except Exception:
            return JsonResponse({
                "code": 100,
                "msg": "未登录"
            })
        feedback = Feedback()
        feedback.userId_id = user.id
        feedback.title = request.POST['title']
        feedback.content = request.POST['content']
        try:
            feedback.save()
        except Exception:
            return JsonResponse({
                "code": 100,
                "msg": "提交失败"
            })
        return JsonResponse({
            "code": 20000,
            "msg": "提交成功"
        })


def user_warning(request):
    if request.method == "GET":
        try:
            user = User.objects.get(id=request.session['userid'])
        except Exception:
            return JsonResponse({
                "code": 100,
                "msg": "未登录"
            })
        cities = user.cities.split('/')
        warnings = []
        for city in cities:
            city_warnings = Warning.objects.filter(address=city)
            if city_warnings.exists():
                for warning in city_warnings:
                    warnings.append(warning)
        return JsonResponse({
            "code": 20000,
            "msg": "success",
            "data": [{
                "title": w.title,
                "address": w.address,
                "type": w.type,
                "content": w.content,
                "warningTime": w.warningTime
            } for w in warnings]
        })


def user_avatar(request):
    if request.method == "POST":
        try:
            user = User.objects.get(id=request.session['userid'])
        except Exception:
            return JsonResponse({
                "code": 100,
                "msg": "未登录"
            })
        file = request.FILES.get("avatar", None)
        if not file:
            return JsonResponse({
                "code": 101,
                "msg": "无文件上传"
            })
        file_type = file.name.split('.')[-1]
        img_name = f"{user.id}_avatar_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.{file_type}"
        file_path = os.path.join(settings.STATIC_ROOT, "avatars", img_name)

        with open(file_path, "wb") as fp:
            for part in file.chunks():
                fp.write(part)

        origin_avatar = os.path.join(settings.STATIC_ROOT, "avatars", user.avatar.split("/")[-1])
        user.avatar = "/back_static/avatars/" + img_name
        user.save(update_fields=["avatar"])
        if not origin_avatar.endswith("default.png"):
            os.remove(origin_avatar)
        return JsonResponse({
            "code": 20000,
            "msg": "头像修改成功"
        })


def userList(request):
    if request.method == "GET":
        try:
            admin = User.objects.get(id=request.session['userid'])
        except Exception:
            return JsonResponse({
                "code": 100,
                "msg": "未登录"
            })
        if admin.isAdmin:
            users = User.objects.all()
            return JsonResponse({
                "code": 20000,
                "msg": "success",
                "data": {
                    "tableData": [{
                        "username": user.name,
                        "phone": user.phone,
                        "email": user.email,
                        "isAdmin": user.isAdmin
                    } for user in users]
                }
            })
        else:
            return JsonResponse({
                "code": 100,
                "msg": "非管理员用户",
                "data": None
            })


def delete_user(request):
    if request.method == "POST":
        try:
            admin = User.objects.get(id=request.session['userid'])
        except Exception:
            return JsonResponse({
                "code": 100,
                "msg": "未登录"
            })
        if admin.isAdmin:
            uid = request.POST.get("username")
            user = User.objects.filter(name=uid).first()
            if user:
                user.delete()
                return JsonResponse({
                    "code": 20000,
                    "msg": "删除用户成功"
                })
            else:
                return JsonResponse({
                    "code": 101,
                    "msg": "没有此用户"
                })
        else:
            return JsonResponse({
                "code": 100,
                "msg": "非管理员用户",
            })


def reset_password(request):
    if request.method == "POST":
        try:
            admin = User.objects.get(id=request.session['userid'])
        except Exception:
            return JsonResponse({
                "code": 100,
                "msg": "未登录"
            })
        if admin.isAdmin:
            uid = request.POST.get("username")
            # uid = request.GET.get("username")
            user = User.objects.filter(name=uid).first()
            if user:
                user.password = "defaultPwd1"
                user.save(update_fields=["password"])
                return JsonResponse({
                    "code": 20000,
                    "msg": "密码重置成功"
                })
            else:
                return JsonResponse({
                    "code": 101,
                    "msg": "没有此用户"
                })
        else:
            return JsonResponse({
                "code": 100,
                "msg": "非管理员用户",
            })


def createWarn(request):
    if request.method == "POST":
        try:
            admin = User.objects.get(id=request.session['userid'])
        except Exception:
            return JsonResponse({
                "code": 100,
                "msg": "未登录"
            })
        if admin.isAdmin:
            title = request.POST.get("title")
            address = request.POST.get("address")
            warningTime = request.POST.get("warningTime")
            type = request.POST.get("type")
            content = request.POST.get("content")
            '''
            selectedEmail = request.POST.get("selectedEmail")
            title = request.GET.get("title")
            address = request.GET.get("address")
            warningTime = request.GET.get("warningTime")
            type = request.GET.get("type")
            content = request.GET.get("content")
            '''

            warning = Warning()
            warning.title = title
            warning.address = address
            warning.warningTime = warningTime
            warning.type = type
            warning.content = content
            try:
                warning.save()
                emails = User.objects.filter(Q(cities__contains=f'/{address}/') |
                                             Q(cities__startswith=f'{address}/') |
                                             Q(cities__endswith=f'/{address}') |
                                             Q(cities=address)).values_list('email', flat=True).distinct()
                try:
                    send_mail(title, content, settings.EMAIL_HOST_USER, emails, fail_silently=False)
                except Exception:
                    return JsonResponse({
                        "code": 100,
                        "msg": "发送邮件错误"
                    })
                return JsonResponse({
                    "code": 20000,
                    "msg": "创建成功"
                })
            except Exception:
                return JsonResponse({
                    "code": 101,
                    "msg": "创建失败"
                })
        else:
            return JsonResponse({
                "code": 100,
                "msg": "非管理员用户",
            })


def getFeedback(request):
    if request.method == "GET":
        try:
            user = User.objects.get(id=request.session['userid'])
        except Exception:
            return JsonResponse({
                "code": 100,
                "msg": "未登录"
            })
        feedback = Feedback.objects.all()
        if user.isAdmin:
            return JsonResponse({
                "code": 20000,
                "msg": "success",
                "data": {
                    "tableData": [{
                        "id": f.id,
                        "title": f.title,
                        "content": f.content,
                        "reply": f.reply,
                        "status": f.status,
                        "updateTime": f.updated.strftime("%Y-%m-%d %H:%M:%S"),
                        "username": User.objects.get(id=f.userId_id).name
                    } for f in feedback]
                }
            })
        else:
            return JsonResponse({
                "code": 100,
                "msg": "非管理员用户",
                "data": None
            })


def createNotice(request):
    if request.method == "POST":
        try:
            admin = User.objects.get(id=request.session['userid'])
        except Exception:
            return JsonResponse({
                "code": 100,
                "msg": "未登录"
            })
        if admin.isAdmin:
            title = request.POST.get("title")
            content = request.POST.get("content")
            tag = request.POST.get("tag")
            '''
            title = request.GET.get("title")
            content = request.GET.get("content")
            tag = request.GET.get("tag")
            '''

            notice = Notice()
            notice.title = title
            notice.content = content
            notice.tag = tag
            try:
                notice.save()
            except Exception:
                return JsonResponse({
                    "code": 101,
                    "msg": "创建失败"
                })
            return JsonResponse({
                "code": 20000,
                "msg": "创建成功"
            })
        else:
            return JsonResponse({
                "code": 100,
                "msg": "非管理员用户",
            })


def reply_feedback(request):
    if request.method == "POST":
        try:
            admin = User.objects.get(id=request.session['userid'])
        except Exception:
            return JsonResponse({
                "code": 100,
                "msg": "未登录"
            })
        if admin.isAdmin:
            id = request.POST.get("id")
            reply = request.POST.get("reply")
            # id = request.GET.get("id")
            # reply = request.GET.get("reply")
            try:
                id = int(id)
                feedback = Feedback.objects.get(id=id)
            except Exception:
                return JsonResponse({
                    "code": 101,
                    "msg": "id错误",
                })
            feedback.reply = reply
            feedback.status = "已处理"
            feedback.save()
            return JsonResponse({
                "code": 20000,
                "msg": "回复成功"
            })
        else:
            return JsonResponse({
                "code": 100,
                "msg": "非管理员用户",
            })


def notice_digest(request):
    if request.method == "GET":
        try:
            user = User.objects.get(id=request.session['userid'])
        except Exception:
            return JsonResponse({
                "code": 100,
                "msg": "未登录"
            })

        notices = Notice.objects.all()
        return JsonResponse({
            "code": 20000,
            "msg": "success",
            "data": [{
                "date": n.created.strftime("%Y-%m-%d %H:%M:%S"),
                "title": n.title,
                "tag": n.tag,
                "state": n.read,
                "id": str(n.id)
            } for n in notices]
        })


def notice_content(request):
    if request.method == "GET":
        try:
            user = User.objects.get(id=request.session['userid'])
        except Exception:
            return JsonResponse({
                "code": 100,
                "msg": "未登录"
            })

        # id = request.POST.get("id")
        id = request.GET.get("id")
        try:
            id = int(id)
            notice = Notice.objects.get(id=id)
        except Exception:
            return JsonResponse({
                "code": 101,
                "msg": "id错误",
                "data": None
            })
        return JsonResponse({
            "code": 20000,
            "msg": "success",
            "data": {
                "content": notice.content
            }
        })


def notice_state(request):
    if request.method == "POST":
        id = request.POST.get("id")
        state = request.POST.get("state")
        # id = request.GET.get("id")
        # state = request.GET.get("state")
        try:
            id = int(id)
            notice = Notice.objects.get(id=id)
        except Exception:
            return JsonResponse({
                "code": 101,
                "msg": "id错误",
            })
        notice.read = state == "已读"
        notice.save(update_fields=["read"])
        return JsonResponse({
            "code": 20000,
            "msg": "公告状态更改为%s" % state
        })


def delete_notice(request):
    if request.method == "POST":
        try:
            admin = User.objects.get(id=request.session['userid'])
        except Exception:
            return JsonResponse({
                "code": 100,
                "msg": "未登录",
            })
        if admin.isAdmin:
            id = request.POST.get("id")
            # id = request.GET.get("id")
            try:
                id = int(id)
                notice = Notice.objects.get(id=id)
            except Exception:
                return JsonResponse({
                    "code": 101,
                    "msg": "id错误",
                })
            notice.delete()
            return JsonResponse({
                "code": 20000,
                "msg": "删除成功"
            })
        else:
            return JsonResponse({
                "code": 100,
                "msg": "非管理员用户",
            })


def getCityData(request):
    if request.method == "GET":
        # try:
        #     user = User.objects.get(id=request.session['userid'])
        # except Exception:
        #     return JsonResponse({
        #         "code": 100,
        #         "msg": "未登录",
        #         "data": None
        #     })
        adcodes = request.GET.getlist('adcodes[]')
        print(adcodes)
        # type = request.POST.get("type")
        # date = request.POST.get("date").split('-')
        from . import get_api

        api_key = '3cdf5414d4c5422abfb6aa6bcf19cbce'
        # 替换为你的帐号和密码
        # user_id = "<你的帐号>"
        # password = "<你的密码>"
        '''params = {
            "userId": user_id,
            "pwd": password,
            "dataFormat": "json",
            "interfaceId": "getSurfEleByTimeRangeAndStaID",
            "dataCode": "SURF_CHN_MUL_HOR_3H",
            "timeRange": "<时间范围>",
            "staIDs": "<台站列表>",
            "elements": "Station_Id_C,Year,Mon,Day,Hour,<要素列表>"
            "weather": get_api.main(adcodes,api_key)
        }
        print(params)'''
        # 发起API请求
        # response = requests.get(url, params=params)
        result = get_api.retrieve_weather_data(adcodes)
        print(result)
        return JsonResponse(result)


def send_code(subject, email, sendType, sendTime):
    code = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    try:
        # 主题, 内容, 发送者, 接收方(多个, 错误相关
        send_mail(subject,
                  f"您好, 验证码为{code}, 请在网站上输入此验证码, 有效期为{settings.EMAIL_EXPIRE}分钟。如果本封邮件非您本人触发, 请忽略。",
                  settings.EMAIL_HOST_USER, [email], fail_silently=False)
        try:
            emailVerify = EmailVerify.objects.get(email=email)
            emailVerify.code = code
            emailVerify.sendType = sendType
        except Exception:
            emailVerify = EmailVerify()
            emailVerify.code = code
            emailVerify.email = email
            emailVerify.sendType = sendType
        emailVerify.sendTime = sendTime
        emailVerify.save()
    except Exception:
        return JsonResponse({
            "code": 100,
            "msg": "发送邮件错误"
        })
    return JsonResponse({
        "code": 20000,
        "msg": "验证码已发送，请注意查收"
    })


def sendVerifyCode(request):
    if request.method == "POST":
        email = request.POST.get("email")
        sendType = request.POST.get('sendType')
        sendTime = datetime.datetime.now()
        if sendType == 'register':
            try:
                User.objects.get(email=email)
            except Exception:
                return send_code("邮箱绑定", email, sendType, sendTime)
            return JsonResponse({
                "code": 100,
                "msg": "邮箱已被使用"
            })
        else:
            try:
                User.objects.get(email=email)
                return send_code("修改密码", email, sendType, sendTime)
            except Exception:
                return JsonResponse({
                    "code": 100,
                    "msg": "邮箱不存在"
                })
