from django.core.mail import send_mail
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Sum
from django.contrib.auth import authenticate, login, logout
from django.core.paginator import Paginator

from stinkomanlevels.main.models import *
from stinkomanlevels.main.forms import *

import string
import random

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
    err_msg = ''
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            # create the user
            user = User.objects.create_user(form.cleaned_data.get('username'),
                form.cleaned_data.get('email'),
                form.cleaned_data.get('password'))
            user.save()

            # create a profile
            profile = Profile()
            profile.user = user
            profile.activated = False
            profile.activate_code = create_hash(32)
            profile.logon_count = 0
            profile.save()

            # send an activation email
            subject = "Account Confirmation - Custom Stinkoman Levels"
            message = """
==========Custom Stinkoman Levels Account Confirmation==========

Please enter this link into your browser to confirm your account:
http://stinkoman.superjoesoftware.com/confirm/%s/%s

Thank you!

-Superjoe Software Admin
http://www.superjoesoftware.com
""" % (user.username, profile.activate_code)
            from_email = 'admin@superjoesoftware.com'
            to_email = user.email
            send_mail(subject, message, from_email, [to_email], fail_silently=True)

            return HttpResponseRedirect("/register/pending/")
    else:
        form = RegisterForm()
    return render_to_response('register.html', {'form': form, 'err_msg': err_msg }, context_instance=RequestContext(request))

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

def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')

def user_login(request):
    err_msg = ''
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data.get('username', ''), password=form.cleaned_data.get('password', ''))
            if user is not None:
                if user.is_active:
                    login(request, user)
                    url = '/'
                    if request.GET.has_key('next'):
                        url = request.GET['next']
                    return HttpResponseRedirect(url)
                else:
                    err_msg = 'Your account is disabled.'
            else:
                err_msg = 'Invalid login.'
    else:
        form = LoginForm()
    return render_to_response('login.html', {'form': form, 'err_msg': err_msg }, context_instance=RequestContext(request))

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

    order = request.GET.get('order', 'ASC')
    if order == 'DESC':
        sign = '-'
    else:
        sign = ''
        order = 'ASC'

    next_sort = {
        'rating': 'DESC',
        'author': 'ASC',
        'stage': 'ASC',
        'difficulty': 'ASC',
        'length': 'ASC',
        'datecreated': 'DESC',
        'title': 'ASC',
    }
    column = request.GET.get('sort', 'title')
    if not next_sort.has_key(column):
        colmun = 'title'

    if sign != '-' and next_sort[column] == 'ASC':
        next_sort[column] = 'DESC'
    elif sign == '-' and next_sort[column] == 'DESC':
        next_sort[column] = 'ASC'

    levels = Level.objects
    if column == 'rating':
        levels = levels.annotate(rating_value=Sum("ratings__value")).order_by("%srating_value" % sign)
    elif column == 'author':
        levels = levels.order_by('%sauthor' % sign, '%stitle' % sign)
    elif column == 'stage':
        levels = levels.order_by('%smajor_stage' % sign, '%sminor_stage' % sign)
    elif column == 'difficulty':
        levels = levels.order_by('%sdifficulty' % sign, '%slength' % sign)
    elif column == 'length':
        levels = levels.order_by('%slength' % sign, '%sdifficulty' % sign)
    elif column == 'datecreated':
        levels = levels.order_by('%sdate_created' % sign)
    else: # title
        levels = levels.order_by('%stitle' % sign)

    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        page = 1

    paginator = Paginator(levels, 20)
    levels = paginator.page(page)

    results = {
        'levels': levels,
        'next_sort': next_sort,
        'sort': column,
        'order': order,
    }

    return render_to_response('browse.html', results, context_instance=RequestContext(request))

def create_hash(length):
    """
    returns a string of length length with random alphanumeric characters
    """
    chars = string.letters + string.digits
    code = ""
    for i in range(length):
        code += chars[random.randint(0, len(chars)-1)]
    return code
