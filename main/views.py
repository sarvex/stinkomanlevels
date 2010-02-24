from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from stinkomanlevels.main.models import *
from django.db.models import Sum

def activeUser(request):
    """
    touch the request's user if they are authenticated in order
    to update the last_activity field
    """
    if request.user.is_authenticated():
        request.user.get_profile().save() # set active date

def home(request):
    activeUser(request)

    new_levels = Level.objects.order_by("-date_created")[:10]
    top_levels = Level.objects.annotate(rating_value=Sum("ratings__value")).order_by('-rating_value')[:10]

    return render_to_response('home.html', locals(), context_instance=RequestContext(request))

def user(request):
    activeUser(request)
    return render_to_response('user.html', locals(), context_instance=RequestContext(request))

def upload(request):
    activeUser(request)
    return render_to_response('upload.html', locals(), context_instance=RequestContext(request))

def submit(request):
    activeUser(request)
    return render_to_response('submit.html', locals(), context_instance=RequestContext(request))

def register(request):
    activeUser(request)
    return render_to_response('register.html', locals(), context_instance=RequestContext(request))

def rate(request):
    activeUser(request)
    return render_to_response('rate.html', locals(), context_instance=RequestContext(request))

def post(request):
    activeUser(request)
    return render_to_response('post.html', locals(), context_instance=RequestContext(request))

def play(request):
    activeUser(request)
    return render_to_response('play.html', locals(), context_instance=RequestContext(request))

def namecheck(request):
    activeUser(request)
    return render_to_response('namecheck.html', locals(), context_instance=RequestContext(request))

def logout(request):
    activeUser(request)
    return render_to_response('logout.html', locals(), context_instance=RequestContext(request))

def login(request):
    activeUser(request)
    return render_to_response('login.html', locals(), context_instance=RequestContext(request))

def edit(request):
    activeUser(request)
    return render_to_response('edit.html', locals(), context_instance=RequestContext(request))

def dashboard(request):
    activeUser(request)
    return render_to_response('dashboard.html', locals(), context_instance=RequestContext(request))

def confirm(request):
    activeUser(request)
    return render_to_response('confirm.html', locals(), context_instance=RequestContext(request))

def browse(request):
    activeUser(request)
    return render_to_response('browse.html', locals(), context_instance=RequestContext(request))

