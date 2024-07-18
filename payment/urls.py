from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('checkout/', views.checkout, name='checkout'),
    path('success/', views.success, name='success'),
    path('cancel/', views.cancel, name='cancel'),
    path('thanks-you/', views.thank_you, name='thank_you'),
    path('apply_coupon/', views.apply_coupon, name='apply_coupon'),

]