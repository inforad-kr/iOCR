from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('login/', views.LoginUser.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('start_training/', views.start_training, name='start_training'),
    path('img/', views.img_recognition, name='recognition'),
    path('recognition/', views.recognition, name='recognition'),
    path('fst_rec/', views.fst_rec, name='fst_rec'),
    path('api/upload/', views.upload_image_api, name='upload_image_api'),
    path('api/recognition/', views.recognition_image_api, name='recognition_image_api'),
]