from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login', views.index, name='index'),
    path('dashboard/', views.ims, name='rinv'),
    path('signup/', views.signup, name='signup'),
    path('dashboard/download', views.download_inv, name='download'),
    # path('defaults', views.ins_defaults, name='defaults')
]