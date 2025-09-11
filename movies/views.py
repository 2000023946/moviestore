from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, WishList, WishListItem
from django.contrib.auth.decorators import login_required
# Create your views here.

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()
    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    template_data['recently_viewed'] = [Movie.objects.get(id=id) for id in request.session.get('recently_viewed', [])]
    template_data['reviews'] = Review.objects.order_by('-votes')[:5]

    return render(request, 'movies/index.html',
                  {'template_data': template_data})


def vote_review(request, review_id):
    review = Review.objects.get(id=review_id)
    review.votes += 1
    review.save()
    return redirect('movies.index')

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie).order_by('-votes')[:5]
    print('show', id)
    exists = WishListItem.objects.filter(movie=movie, wishList=getWishList(request.user)).exists()
    template_data = {}
    print('viewing', id)
    addToRecent(request, id)
    print('added', id)
    template_data['title'] = movie.name
    template_data['reviews'] = reviews
    template_data['movie'] = movie
    template_data['inCart'] = str(id) in request.session.get('cart', {})
    template_data['wishList'] = 'Remove' if exists else 'Add'

    return render(request, 'movies/show.html',
                  {'template_data': template_data})

def addToRecent(request, id):
    # Get the list from session or create empty list
    recents = request.session.get('recently_viewed', [])

    if id in recents:
        recents.remove(id)

    recents.insert(0, id)

    recents = recents[:5]

    request.session['recently_viewed'] = recents


@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
    
@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)
    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html',
            {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)
    
@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)



@login_required
def addWishList(request, movie_id):
    print('adding item to wishList ...')
    #search for the movie
    movie = Movie.objects.get(id=movie_id)
    #search for the wishList
    wishList = getWishList(request.user)

    #make new item in the wishList
    item = WishListItem(movie=movie, wishList=wishList)
    item.save()

    return redirect('movies.show', movie_id)

@login_required
def removeWishList(request, movie_id):
    #search for the movie
    movie = Movie.objects.get(id=movie_id)
    #search for the wishList
    wishList = getWishList(request.user)

    itemToRemove = WishListItem.objects.filter(movie=movie, wishList=wishList).first()
    if itemToRemove:
        itemToRemove.delete()

    return redirect('movies.show', movie_id)


def getWishList(user):
    wishList = WishList.objects.filter(user=user)
    print('fetched wishList ', wishList)
    if not wishList:
        wishList = WishList.objects.create(user=user)
        wishList.save()
    else:
        wishList = wishList[0]
    return wishList

    

    






