from django.urls import path, include
from rest_framework.routers import DefaultRouter
from chats.views import *

router = DefaultRouter()
router.register('', MessageViewSet, basename="message")

app_name = "chats"
urlpatterns = [
    # path('messages/', include(router.urls)),
    path('', ChatRenderView.as_view(), name="chat_render"),
    path('messages/<int:user_id>/', MessageListView.as_view(), name='messages'),
    path('messages/<int:message_id>/read/', MarkMessageAsReadView.as_view(), name='mark_as_read'),
]
