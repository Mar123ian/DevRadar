from django.urls import path, include

from categories.views import CreateType, DeleteType, CreateTechnology, AllTypes, TypeDetails, UpdateType

urlpatterns = [
    path('type/', include([
        path('all/', AllTypes.as_view(), name='all_types'),
        path('create/', CreateType.as_view(), name='create_type'),
        path('delete/<int:pk>/', DeleteType.as_view(), name='delete_type'),
        path('update/<int:pk>/', UpdateType.as_view(), name='update_type'),
        path('<slug:type_slug>/', TypeDetails.as_view(), name='type_details'),

    ])),
    path('technology/', include([
        path('create/', CreateTechnology.as_view(), name='create_technology'),
    ])),
]