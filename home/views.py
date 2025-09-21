from django.shortcuts import render #type: ignore
from cart.models import Order
from django.db.models import Sum


def index(request):
    template_data = {}
    template_data['title'] = 'Movies Store'

    return render(request, 'home/index.html', {
        'template_data': template_data})


def about(request):
    template_data = {}
    template_data['title'] = 'About'
    return render(request,
        'home/about.html',
        {'template_data': template_data})

def subs(request):
    template_data = {}
    template_data['title'] = 'About'
    subs = get_total_spent(request.user)
    if subs < 15:
        template_data['subscription'] = 'Basic'
    elif subs < 30:
        template_data['subscription'] = 'Medium'
    else: 
        template_data['subscription'] = 'Premium'

    return render(request,
        'home/subs.html',
        {'template_data': template_data})

def get_total_spent(user):
    return (
        Order.objects
        .filter(user=user)
        .aggregate(total_spent=Sum('total'))
    )['total_spent'] or 0
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Petition, VotePetition

def petition(request):
    template_data = {'title': 'Petition'}

    # Handle POST: create new petition + auto vote
    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            petition, created = Petition.objects.get_or_create(name=name)
            vote = VotePetition.objects.get_or_create(user=request.user, petition=petition)
            print('created new petition:', petition.name, 'created:', created, 'vote:', vote)
            # Automatically add a vote if the user is logged in
            if request.user.is_authenticated:
                VotePetition.objects.get_or_create(user=request.user, petition=petition)
            template_data['message'] = f'Thank you for voting for {petition.name}!'
        else:
            template_data['error'] = 'No petition name provided.'

    # Handle GET or after POST: list petitions
    petitions = Petition.objects.all()
    template_data['petitions'] = [{
        'id': p.id,
        'name': p.name,
        'votes': p.vote_count()
    } for p in petitions]

    return render(request, 'home/petition.html', {'template_data': template_data})


@login_required
def vote_petition(request):
    template_data = {'title': 'Petition'}

    if request.method == 'POST':
        name = request.POST.get('name')
        if name:
            petition = get_object_or_404(Petition, name=name)
            # Prevent duplicate votes
            VotePetition.objects.get_or_create(user=request.user, petition=petition)
        else:
            template_data['error'] = 'No petition ID provided.'

    # Refresh petition list
    petitions = Petition.objects.all()
    template_data['petitions'] = [{
        'id': p.id,
        'name': p.name,
        'votes': p.vote_count()
    } for p in petitions]

    return render(request, 'home/petition.html', {'template_data': template_data})

