from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from stinkomanlevels.main.models import *

def home(request):
    request.user.get_profile().save() # set active date
    return render_to_response('home.html', locals(), context_instance=RequestContext(request))

def user(request):
    return render_to_response('user.html', locals(), context_instance=RequestContext(request))

def upload(request):
    return render_to_response('upload.html', locals(), context_instance=RequestContext(request))

def submit(request):
    return render_to_response('submit.html', locals(), context_instance=RequestContext(request))

def register(request):
    return render_to_response('register.html', locals(), context_instance=RequestContext(request))

def rate(request):
    return render_to_response('rate.html', locals(), context_instance=RequestContext(request))

def post(request):
    return render_to_response('post.html', locals(), context_instance=RequestContext(request))

def play(request):
    return render_to_response('play.html', locals(), context_instance=RequestContext(request))

def namecheck(request):
    return render_to_response('namecheck.html', locals(), context_instance=RequestContext(request))

def logout(request):
    return render_to_response('logout.html', locals(), context_instance=RequestContext(request))

def login(request):
    return render_to_response('login.html', locals(), context_instance=RequestContext(request))

def edit(request):
    return render_to_response('edit.html', locals(), context_instance=RequestContext(request))

def dashboard(request):
    return render_to_response('dashboard.html', locals(), context_instance=RequestContext(request))

def confirm(request):
    return render_to_response('confirm.html', locals(), context_instance=RequestContext(request))

def browse(request):
    return render_to_response('browse.html', locals(), context_instance=RequestContext(request))

