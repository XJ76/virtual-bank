from django.urls import path
from . import views

urlpatterns = [
    path('', views.signup, name='index'),
    path('wallet/', views.wallet, name='wallet'),  # URL for the user's wallet view
    path('mine/', views.mine, name='mine_view'),  # URL for mining new blocks
    path('chain/', views.chain_view, name='chain_view'),  # URL for viewing the blockchain
    path('signup/', views.signup, name='signup'),  # URL for user registration
    path('login/', views.Login, name='login'),  # URL for user login
    path('transfer/', views.fund_transfer, name='fund_transfer'),  # URL for fund transfer
    path('fetch_notifications/', views.fetch_notifications, name='fetch_notifications'),  # URL for fetching notification
    
    #test urls
    path('password_recovery', views.password_recovery, name='password_recovery'),
    
]
