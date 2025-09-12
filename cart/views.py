from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404, redirect
from movies.models import Movie, WishList, WishListItem
from .utils import calculate_cart_total

from movies.views import getWishList

def add(request, id):
    print('adding multi')
    get_object_or_404(Movie, id=id)
    cart = request.session.get('cart', {})
    print(cart)
    if 'quantity' in request.POST:
        cart[str(id)] = request.POST['quantity']
    else :
        cart[str(id)] = cart.get(str(id), 0) + 1
    request.session['cart'] = cart
    return redirect('home.index')		

def remove(request, id):
    print('deleting movie', id)
    get_object_or_404(Movie, id=id)
    cart = request.session.get('cart', {})
    print('cart', cart)
    del cart[str(id)]
    request.session['cart'] = cart
    return redirect('home.index')	

def index(request):
    print('accessing cart')
    cart_total = 0
    movies_in_cart = []
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    if (movie_ids != []):
        movies_in_cart = Movie.objects.filter(id__in=movie_ids)
        cart_total = calculate_cart_total(cart,
            movies_in_cart)
        
    template_data = {}
    template_data['title'] = 'Cart'
    template_data['movies_in_cart'] = movies_in_cart
    template_data['cart_total'] = cart_total

    if request.user.is_authenticated: 
        print('getting auth user iwshList', [item.movie for item in getWishList(request).wishList.all()])
        template_data['wishList_items'] = [item.movie for item in getWishList(request).wishList.all()]

    else:
        print('session wishLIst', request.session.get('wishList', []))
        template_data['wishList_items'] = [Movie.objects.get(id=id) for id in request.session.get('wishList', [])]
        print('wishList objects sql', template_data['wishList_items'])
        
    return render(request, 'cart/index.html',
        {'template_data': template_data})

def add_to_cart(request, id):
    get_object_or_404(Movie, id=id)
    cart = request.session.get('cart', {})
    cart[id] = request.POST['quantity']
    request.session['cart'] = cart
    return redirect('cart.index')



def clear(request):
    request.session['cart'] = {}
    return redirect('cart.index')

from .models import Order, Item
from django.contrib.auth.decorators import login_required

@login_required
def purchase(request):
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    if (movie_ids == []):
        return redirect('cart.index')
    movies_in_cart = Movie.objects.filter(id__in=movie_ids)
    cart_total = calculate_cart_total(cart, movies_in_cart)
    order = Order()
    order.user = request.user
    order.total = cart_total
    order.save()
    for movie in movies_in_cart:
        item = Item()
        item.movie = movie
        item.price = movie.price
        item.order = order
        item.quantity = cart[str(movie.id)]
    item.save()
    request.session['cart'] = {}
    template_data = {}
    template_data['title'] = 'Purchase confirmation'
    template_data['order_id'] = order.id
    return render(request, 'cart/purchase.html',
        {'template_data': template_data})