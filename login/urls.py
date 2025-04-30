from django.conf import settings
from django.contrib import admin
from django.urls import path
from  login  import views
from django.conf.urls.static import static  
urlpatterns = [
    path('',views.home,name='login'),
    path('signup',views.signup,name="signup"),
    path('login',views.login_view,name="login"),
    path("logout",views.logout_view,name="Log Out"),
   path("home",views.home,name="home"),
    path('index',views.home,name="index"),
    path('verify_otp',views.verify_otp,name="otp verify"),
   path('add_to_cart/<int:product_id>', views.add_to_cart, name='add_to_cart'),
   path('cart',views.cart,name="cart"),
   path('checkout',views.checkout,name="checkout"),
   path('update_quantity/<int:product_id>',views.update_quantity,name="update_quantity"),
   path('payment',views.initiate_payment,name="payment"),
    path('process_payment/<int:transaction_id>', views.process_payment, name='process_payment'),
    path('resend_otp',views.resend_otp,name="resend"),
    path('track_order/', views.track_order, name='track_order'),
    path('submit_review/', views.submit_review, name='submit_review'),
] 
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
