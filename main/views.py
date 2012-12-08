from django.core.mail import send_mail
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, Context, Template
from django.template.loader import get_template
from django.http import HttpResponseRedirect, HttpResponse
from django.db.models import Sum
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator

from stinkomanlevels.main.models import *
from stinkomanlevels.main.forms import *

from stinkomanlevels.settings import MEDIA_ROOT

import string
import random
import datetime
import os

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
    top_levels = Level.objects.annotate(rating_value=Sum("rating__value")).order_by('-rating_value')[:10]

    return render_to_response('home.html', locals(), context_instance=RequestContext(request))

def user(request, username):
    activeUser(request)

    selected_user = get_object_or_404(User, username=username)
    profile = selected_user.get_profile()

    user_levels = Level.objects.filter(author=profile)
    comments = ProfileComment.objects.filter(profile=profile)

    return render_to_response('user.html', locals(), context_instance=RequestContext(request))

def upload(request):
    activeUser(request)
    return render_to_response('upload.html', locals(), context_instance=RequestContext(request))

def submit(request):
    activeUser(request)
    err_msg = ""
    if request.method == 'POST':
        form = UploadLevelForm(request.POST, request.FILES)
        if form.is_valid() and request.user.is_authenticated():
            if len(form.cleaned_data.get('title')) == 0:
                err_msg = "You must supply a title."
            else:
                # create the new level
                level = Level()
                level.title = form.cleaned_data.get('title')
                level.major_stage, level.minor_stage = form.cleaned_data.get('stage').split('.')
                level.difficulty = form.cleaned_data.get('difficulty')
                level.length = form.cleaned_data.get('length')
                level.author = request.user.get_profile()
                level.description = form.cleaned_data.get('description')
                level.file = unique_level_path(level.title)

                out_path = os.path.join(MEDIA_ROOT, "levels", level.file)
                if form.cleaned_data.get('xml_file') is not None:
                    # upload the file to that file
                    handle_uploaded_file(request.FILES['xml_file'], out_path)
                elif form.cleaned_data.get('xml_code') is not None:
                    # write the xml code to that file
                    open(out_path, "w").write(form.cleaned_data.get('xml_code'))

                level.save()

                return HttpResponseRedirect("/play/%s/" % level.title)
    else:
        form = UploadLevelForm()
    return render_to_response('submit.html', locals(), context_instance=RequestContext(request))

def handle_uploaded_file(f, new_name):
	dest = open(new_name, 'wb+')
	for chunk in f.chunks():
		dest.write(chunk)
	dest.close()
    

def unique_level_path(title):
    """
    returns a unique file title for the level to have guaranteeing that
    it won't collide with another file in the levels media folder
    """
    allowed = string.letters + string.digits + "_-."
    clean = ""
    for c in title:
        if c in allowed:
            clean += c
        else:
            clean += "_"

    ext = ".xml"
    if os.path.exists(os.path.join(MEDIA_ROOT, "levels", clean + ext)):
        # use digits
        suffix = 2
        while os.path.exists(os.path.join(MEDIA_ROOT, "levels", clean + str(suffix) + ext)):
            suffix += 1
        unique = clean + str(suffix) + ext
    else:
        unique = clean + ext

    return unique

def register(request):
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
            message = get_template('activation_email.txt').render(Context({ 'username': user.username, 'code': profile.activate_code}))
            from_email = 'admin@superjoesoftware.com'
            to_email = user.email
            send_mail(subject, message, from_email, [to_email], fail_silently=True)

            return HttpResponseRedirect("/register/pending/")
    else:
        form = RegisterForm()
    return render_to_response('register.html', {'form': form}, context_instance=RequestContext(request))

@login_required
def rate(request, level_title, value):
    activeUser(request)
    value = int(value)
    
    level = get_object_or_404(Level, title=level_title)
    profile = request.user.get_profile()
    user_ratings = level.rating_set.filter(owner=profile)

    if user_ratings.count() > 0:
        # user has already rated - change their vote
        rating = user_ratings[0]
        rating.value = value
        rating.save()
    else: 
        # create a new rating
        rating = Rating()
        rating.owner = profile
        rating.value = value
        rating.level = level
        rating.save()

    results = {
        'user': request.user,
        'user_rating': rating.value,
    }

    return render_to_response('rate_response.html', results, context_instance=RequestContext(request))

def post(request):
    activeUser(request)
    return render_to_response('post.html', locals(), context_instance=RequestContext(request))

def play(request, level_title):
    activeUser(request)

    level = get_object_or_404(Level, title=level_title)

    if request.method == 'POST':
        form = NewCommentForm(request.POST)
        if form.is_valid() and request.user.is_authenticated():
            comment = LevelComment()
            comment.owner = request.user.get_profile()
            comment.text = form.cleaned_data.get('content')
            comment.level = level
            comment.save()

            return HttpResponseRedirect(".")
    else:
        form = NewCommentForm()

    level.last_played = datetime.datetime.today()
    level.save()

    level_size = os.path.getsize(os.path.join(MEDIA_ROOT, "levels", level.file))

    level_reviews = LevelComment.objects.filter(level=level).order_by('date_created')

    if request.user.is_authenticated():
        user_rating = level.rating_set.filter(owner=request.user.get_profile())
        if user_rating.count() > 0:
            user_rating = user_rating[0].value
        else:
            user_rating = 0

    return render_to_response('play.html', locals(), context_instance=RequestContext(request))

def level_xml(request, level_title, major_stage, minor_stage):
    major_stage = int(major_stage)
    minor_stage = int(minor_stage)

    level = get_object_or_404(Level, title=level_title)

    if level.major_stage == major_stage and level.minor_stage == minor_stage:
        # give them the level file
        return HttpResponseRedirect("/media/levels/" + level.file)
    elif level.minor_stage == 3 and level.major_stage == major_stage and minor_stage == 2:
        # it's a boss fight, give them an instant win level so they can skip
        # to the boss
        return HttpResponseRedirect("/media/level-templates/instant_win.xml")
    else:
        # not allowed to play this level
        return HttpResponseRedirect("/media/level-templates/instant_death.xml")

def namecheck(request):
    activeUser(request)
    return render_to_response('namecheck.html', locals(), context_instance=RequestContext(request))

def user_logout(request):
    logout(request)
    return HttpResponseRedirect(request.META['HTTP_REFERER'])

def user_login(request):
    err_msg = ''
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(username=form.cleaned_data.get('username', ''), password=form.cleaned_data.get('password', ''))
            if user is not None:
                if user.is_active and user.get_profile().activated:
                    login(request, user)
                    return HttpResponseRedirect(form.cleaned_data.get('next_url'))
                else:
                    err_msg = 'Your account is not activated.'
            else:
                err_msg = 'Invalid login.'
    else:
        form = LoginForm(initial={'next_url': request.GET.get('next', '/')})
    return render_to_response('login.html', {'form': form, 'err_msg': err_msg }, context_instance=RequestContext(request))

@login_required
def edit(request, level_title):
    activeUser(request)
    level = get_object_or_404(Level, title=level_title)
    if request.method == 'POST':
        form = UploadLevelForm(request.POST, request.FILES)
        if form.is_valid() and request.user.is_authenticated():
            level.major_stage, level.minor_stage = form.cleaned_data.get('stage').split('.')
            level.difficulty = form.cleaned_data.get('difficulty')
            level.length = form.cleaned_data.get('length')
            level.description = form.cleaned_data.get('description')

            out_path = level_path(level)
            if form.cleaned_data.get('xml_file') is not None:
                # upload the file to that file
                handle_uploaded_file(request.FILES['xml_file'], out_path)
            elif form.cleaned_data.get('xml_code') is not None:
                # write the xml code to that file
                open(out_path, "w").write(form.cleaned_data.get('xml_code'))

            level.save()

            return HttpResponseRedirect("/play/%s/" % level.title)
    else:
        init = {
            'title': level.title,
            'stage': "%s.%s" % (level.major_stage, level.minor_stage),
            'difficulty': level.difficulty,
            'length': level.length,
            'description': level.description,
            'xml_code': open(level_path(level), "r").read(),
        }
        form = UploadLevelForm(initial=init)

    return render_to_response('edit.html', locals(), context_instance=RequestContext(request))

def level_path(level):
    return os.path.join(MEDIA_ROOT, "levels", level.file)

@login_required
def dashboard(request):
    activeUser(request)

    profile = request.user.get_profile()
    unrated_levels = Level.objects.exclude(rating__owner=profile).order_by('date_created')
    level_reviews = LevelComment.objects.filter(level__author=profile).order_by('-date_created')

    return render_to_response('dashboard.html', locals(), context_instance=RequestContext(request))

def confirm_legacy(request):
    username = request.GET.get('name')
    code = request.GET.get('code')
    return confirm(request, username, code)

def confirm(request, username, code):
    try:
        user = User.objects.get(username=username)
    except:
        err_msg = "Invalid username. Your account may have expired. You can try registering again."
        return render_to_response('confirm_failure.html', locals(), context_instance=RequestContext(request))

    profile = user.get_profile()
    real_code = profile.activate_code

    if real_code == code:
        # activate the account
        user.is_active = True
        user.save()
        profile.activated = True
        profile.save()
        return render_to_response('confirm_success.html', locals(), context_instance=RequestContext(request))
    else:
        err_msg = "Invalid activation code. Nice try!"
        return render_to_response('confirm_failure.html', locals(), context_instance=RequestContext(request))


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
        levels = levels.annotate(rating_value=Sum("rating__value")).order_by("%srating_value" % sign)
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
