from django.urls import path
from store import views
from django.contrib.auth import views as auth_views

urlpatterns = [
	path('cart/', views.cart, name='cart'),
	path('checkout/', views.checkout, name='checkout'),
	path('update_item/', views.updateItem, name='update_item'),
	path('process_order/', views.processOrder, name='process_order'),
	path('product/<int:pk>/', views.viewProduct, name='viewProduct'),
	path('register/', views.registerUser, name='register'),
	path('login/', views.login, name='login'),
	path('logout/', views.logoutUser, name='logout'),
	path('profile/', views.profile, name='profile'),
	path('profile/edit/<int:pk>/', views.editProfile, name='edit_profile'),
	path('profile/change_password/', views.change_password, name='change_password'),
	path('orders/', views.orders, name='orders'),
	
	path('reset_password/', auth_views.PasswordResetView.as_view(template_name="store/forgot_password.html"), name="reset_password"),
	path('reset_password_sent/', auth_views.PasswordResetDoneView.as_view(template_name="store/password_reset_send.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="store/password_reset_confirm.html"), name="password_reset_confirm"),
    path('reset_password_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="store/password_reset_complete.html"), name="password_reset_complete"),
	
	path('', views.store, name='store'),
]
