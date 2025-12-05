from django.urls import path, include
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('home')),  
    path('accounts/', include('accounts.urls')),
    

]


