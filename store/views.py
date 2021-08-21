from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth import authenticate, login as auth_login, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib import messages
from store import models, forms
import json
import datetime
from store import filters

from .utils import cookieCart, cartData, guestOrder

# Create your views here.
def registerUser(request):
	form = forms.CreateUserForm()

	if request.method == 'POST':
		form = forms.CreateUserForm(request.POST)
		if form.is_valid():
			messages.success(request, 'Account is created')
			
			user = form.save()
			models.Customer.objects.create(
				user = user,
				name = user.username,
				email = user.email,
			)
			
			return redirect('login')

	context = {
		'form': form
	}
	return render(request, 'store/register.html', context)

def login(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(request, username=username, password=password)

		if user is not None:
			auth_login(request, user)
			return redirect('store')
		else:
			messages.info(request, 'Username OR password is incorrect')

	context = {}
	return render(request, 'store/login.html', context)

def logoutUser(request):
	logout(request)
	return redirect('store')

def profile(request):
	customer = request.user.customer

	context = {
		'customer': customer,
	}
	return render(request, 'store/profile.html', context)

def change_password(request):
	customer = request.user.customer
	user = request.user
	form = PasswordChangeForm(user)

	if request.method == 'POST':
		form = PasswordChangeForm(user, request.POST)
		if form.is_valid():
			user = form.save()
			update_session_auth_hash(request, user)
			messages.success(request, 'Your password is successfully updated!')
			return redirect('profile')
			
	context = {
		'customer': customer,
		'form': form,
	}
	return render(request, 'store/change_password.html', context)

def editProfile(request, pk):
	customer = models.Customer.objects.get(id=pk)

	form = forms.EditProfileForm(instance=customer);
	
	if request.method == 'POST':
		form = forms.EditProfileForm(request.POST, instance=customer);
		if form.is_valid():
			form.save();
			messages.success(request, 'Your profile is successfully updated!')
			return redirect('profile')

	context = {
		'customer': customer,
		'form': form,
	}
	return render(request, 'store/edit_profile.html', context)

def orders(request):
	customer = request.user.customer

	orders = customer.order_set.all()

	context = {
		'customer': customer,
		'orders': orders,
	}
	return render(request, 'store/orders.html', context)

def store(request):
	data = cartData(request)
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']
	
	products = models.Product.objects.all()

	myFilter = filters.ProductFilter(request.GET, queryset=products)
	products = myFilter.qs

	context = {
		'products': products,
		'cartItems': cartItems,
		'myFilter': myFilter,
	}
	return render(request,'store/store.html',context)

def cart(request):
	data = cartData(request)
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context={
		'items': items,
		'order': order,
		'cartItems': cartItems,
	}
	return render(request,'store/cart.html',context)

def checkout(request):
	data = cartData(request)
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	context={
		'items': items,
		'order': order,
		'cartItems': cartItems,
	}
	return render(request,'store/checkout.html',context)

def updateItem(request):
	data=json.loads(request.body)
	productId=data['productId']
	action=data['action']
	print('Product ID: ', productId)
	print('Action: ', action)

	customer=request.user.customer
	product=models.Product.objects.get(id=productId)

	order, created=models.Order.objects.get_or_create(customer=customer, complete=False)
	orderItem, created=models.OrderItem.objects.get_or_create(product=product, order=order)

	if action=='add':
		orderItem.quantity=(orderItem.quantity+1)
	elif action=='remove':
		orderItem.quantity=(orderItem.quantity-1)

	orderItem.save()

	if orderItem.quantity<=0:
		orderItem.delete()

def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	print(transaction_id)

	data=json.loads(request.body)
	print(data)

	if request.user.is_authenticated:
		customer=request.user.customer
		order, created=models.Order.objects.get_or_create(customer=customer, complete=False)

		if order.shipping == True:
			models.ShippingAddress.objects.create(
				customer=customer,
				order=order,
				address=data['shipping']['address'],
				city=data['shipping']['city'],
				state=data['shipping']['state'],
				zipcode=data['shipping']['zipcode'],
			)
	else:
		customer, order = guestOrder(request, data)


	total=float(data['form']['total'])
	order.transaction_id=transaction_id

	if total == order.get_cart_total:
		order.complete = True
	order.save()

	if order.shipping == True:
		models.ShippingAddress.objects.create(
			customer=customer,
			order=order,
			address=data['shipping']['address'],
			city=data['shipping']['city'],
			state=data['shipping']['state'],
			zipcode=data['shipping']['zipcode'],
		)


	return JsonResponse('Payment submitted', safe=False)

def viewProduct(request, pk):
	data = cartData(request)
	cartItems = data['cartItems']
	order = data['order']
	items = data['items']

	product = models.Product.objects.get(id=pk)

	quantity = 0
	for item in items:
		if request.user.is_authenticated:
			if item.product.id == product.id:
				quantity = item.quantity
				break;			
		else:
			if item['id'] == product.id:
				quantity = item['quantity']
				break

	context = {
		'product': product,
		'items': items,
		'order': order,
		'cartItems': cartItems,
		'quantity': quantity,
	}
	return render(request, 'store/product.html', context)