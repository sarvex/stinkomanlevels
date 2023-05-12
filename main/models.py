from django.db import models
from django.contrib.auth.models import User

D_VERY_EASY, D_EASY, D_MEDIUM, D_HARD, D_VERY_HARD = range(5)
L_SHORT, L_MEDIUM, L_LONG = range(3)
THUMBS_DOWN, NO_RATING, THUMBS_UP = (-1, 0, 1)

class Profile(models.Model):
    user = models.ForeignKey(User, unique=True)
    activated = models.BooleanField()
    activate_code = models.CharField(max_length=256)
    date_activity = models.DateTimeField(auto_now=True)
    logon_count = models.IntegerField()

    def __unicode__(self):
        return self.user.username

    def points(self):
        user_level_ratings = Rating.objects.filter(level__author=self)
        if user_level_ratings.count() == 0:
            return 0
        points = user_level_ratings.aggregate(models.Sum('value'))['value__sum']
        bias = user_level_ratings.filter(owner=self).filter(value=THUMBS_UP).count()
        return points - bias

class Rating(models.Model):
    RATING_CHOICES = (
        (THUMBS_UP, 'Thumbs Up'),
        (NO_RATING, 'No Rating'),
        (THUMBS_DOWN, 'Thumbs Down'),
    )
    owner = models.ForeignKey(Profile)
    value = models.IntegerField(choices=RATING_CHOICES, default=NO_RATING)
    level = models.ForeignKey('Level')
    date_created = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "%s gives %i to %s" % (self.owner, self.value, self.level.title)

class Comment(models.Model):
    owner = models.ForeignKey(Profile)
    text = models.TextField()
    date_edited = models.DateTimeField(auto_now=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return f"{self.owner}: {self.text[:30]}"

class LevelComment(Comment):
    level = models.ForeignKey('Level')

class ProfileComment(Comment):
    profile = models.ForeignKey('Profile')

class Level(models.Model):
    DIFFICULTY_CHOICES = (
        (D_VERY_EASY, 'Very Easy'),
        (D_EASY, 'Easy'),
        (D_MEDIUM, 'Medium'),
        (D_HARD, 'Hard'),
        (D_VERY_HARD, 'Very Hard'),
    )
    LENGTH_CHOICES = (
        (L_SHORT, 'Short'),
        (L_MEDIUM, 'Medium'),
        (L_LONG, 'Long'),
    )
    title = models.CharField(max_length=255, unique=True)
    major_stage = models.IntegerField()
    minor_stage = models.IntegerField()
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, default=D_MEDIUM)
    length = models.IntegerField(choices=LENGTH_CHOICES, default=L_MEDIUM)
    author = models.ForeignKey(Profile)
    description = models.TextField(blank=True)
    file = models.CharField(max_length=500)
    date_created = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)
    last_played = models.DateTimeField(null=True, blank=True)

    def rating(self):
        if self.rating_set.count() == 0:
            return 0
        else:
            return self.rating_set.all().aggregate(models.Sum('value'))['value__sum']

    def difficulty_str(self):
        return dict(Level.DIFFICULTY_CHOICES)[self.difficulty]

    def length_str(self):
        return dict(Level.LENGTH_CHOICES)[self.length]

    def __unicode__(self):
        return self.title

