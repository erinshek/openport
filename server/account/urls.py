from django.urls import path

from account import views


urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('get-me/', views.get_me, name='get_me'),
    path('regenerate-api-key/', views.regenerate_api_key, name='regenerate_api_key'),
]
