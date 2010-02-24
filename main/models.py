from django.db import models
from django.contrib.auth.models import User

VERY_EASY, EASY, MEDIUM, HARD, VERY_HARD = range(5)
VERY_SHORT, SHORT, MEDIUM, LONG, VERY_LONG = range(5)
THUMBS_DOWN, NO_RATING, THUMBS_UP = (-1, 0, 1)

class Profile(models.Model):
    user = models.ForeignKey(User, unique=True)
    activated = models.BooleanField()
    activate_code = models.CharField(max_length=256)
    date_activity = models.DateTimeField(auto_now=True)
    logon_count = models.IntegerField()
    comments = models.ManyToManyField('Comment')

    def __unicode__(self):
        return self.user.username

class Rating(models.Model):
    RATING_CHOICES = (
        (THUMBS_UP, 'Thumbs Up'),
        (NO_RATING, 'No Rating'),
        (THUMBS_DOWN, 'Thumbs Down'),
    )
    owner = models.ForeignKey(Profile)
    value = models.IntegerField(choices=RATING_CHOICES, default=NO_RATING)

class Comment(models.Model):
    owner = models.ForeignKey(Profile)
    text = models.TextField()
    date_edited = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)

class Level(models.Model):
    DIFFICULTY_CHOICES = (
        (VERY_EASY, 'Very Easy'),
        (EASY, 'Easy'),
        (MEDIUM, 'Medium'),
        (HARD, 'Hard'),
        (VERY_HARD, 'Very Hard'),
    )
    LENGTH_CHOICES = (
        (VERY_SHORT, 'Very Short'),
        (SHORT, 'Short'),
        (MEDIUM, 'Medium'),
        (LONG, 'Long'),
        (VERY_LONG, 'Very Long'),
    )
    title = models.CharField(max_length=256)
    major_stage = models.IntegerField()
    minor_stage = models.IntegerField()
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, default=MEDIUM)
    length = models.IntegerField(choices=LENGTH_CHOICES, default=MEDIUM)
    author = models.ForeignKey(Profile)
    description = models.TextField()
    file = models.CharField(max_length=500)
    date_created = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)
    last_played = models.DateTimeField()
    ratings = models.ManyToManyField(Rating)
    comments = models.ManyToManyField(Comment)

    def rating(self):
        return self.ratings.aggregate(models.Sum('value'))['value__sum']

