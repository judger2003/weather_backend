from django.contrib import admin
from django.urls import path
from app1.views import *

urlpatterns = [
    path('get_csrf', get_csrf),
    path('post_csrf', post_csrf),

    path('user/login', login),
    path('user/logout', logout),
    path('user/changePassword', change_password),
    path('user/register', register),
    path('user/info', getUserInfo),
    path('user/citySubscribe', userCity),
    path('user/feedback', user_feedback),
    path('user/warnings', user_warning),
    path('user/avatar', user_avatar),

    path('admin/user-digests', userList),
    path('admin/delete-user', delete_user),
    path('admin/reset-password', reset_password),
    path('admin/launch-warn', createWarn),
    path('admin/fetch-feedback', getFeedback),
    path('admin/launch-notice', createNotice),
    path('admin/reply-feedback', reply_feedback),

    path('notice/digests', notice_digest),
    path('notice/content', notice_content),
    path('notice/change-state', notice_state),
    path('notice/delete-notice', delete_notice),

    path('getCityData', getCityData),

    path('verifyCode', sendVerifyCode),

    path("admin/", admin.site.urls),
]
