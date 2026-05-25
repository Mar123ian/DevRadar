import os
from django.core.asgi import get_asgi_application

# 1. Първо казваме кои са настройките на проекта
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project_name.settings')

# 2. Инициализираме основното Django ASGI приложение. 
# Това подготвя регистъра (App Registry) и моделите.
django_asgi_app = get_asgi_application()

# 3. ЧАК СЕГА импортираме нещата от Channels и твоя routing.
# Тъй като се импортират след get_asgi_application(), Django вече е готово и моделите ще се заредят без проблем.
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import chat.routing

application = ProtocolTypeRouter({
    # Стандартни HTTP заявки
    "http": django_asgi_app,

    # WebSocket заявки
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    ),
})
