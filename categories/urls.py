from django.urls import path, include

from categories.views import CreateType, DeleteType, CreateTechnology, DeleteTechnology

urlpatterns = [
    path('type/', include([
        path('create/', CreateType.as_view(), name='create_type'),
        path('delete/<slug:type_slug>/', DeleteType.as_view(), name='delete_type'),
    ])),
    path('technology/', include([
        path('create/', CreateTechnology.as_view(), name='create_technology'),
        path('delete/<slug:technology_slug>/', DeleteTechnology.as_view(), name='delete_technology'),
    ])),
]