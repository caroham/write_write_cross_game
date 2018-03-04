from __future__ import unicode_literals

from django.db import models

import datetime

import re
import bcrypt

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
LETTER_REGEX = re.compile(r'^[a-zA-Z ]+$')


class UserManager(models.Manager):
    def register_validator(self, postData):
        errors = {}
        if len(postData['username']) < 1:
            errors["un_req"] = "Username is required"
        elif len(postData['username']) < 2:
            errors["un_len"] = "User name must be at least 2 characters"
        elif not LETTER_REGEX.match(postData['username']):
            errors["un_regex"] = "Username can only consist of letters"
        if len(User.objects.all()) > 0:
            if len(User.objects.filter(username = postData['username'])) > 0:
                errors["un_unique"] = "Username must be unique"

        elif len(postData['pw']) < 1:
            errors["pw_req"] = "Password is required"
        elif len(postData['pw']) < 8:
            errors["pw_len"] = "Password must be at least 8 characters long"
        elif postData['pw'] != postData['pw_confirm']:
            errors["pw_confirm"] = "Passwords must match"

        if len(errors) < 1:
            user = User.objects.create(username=postData['username'], password = bcrypt.hashpw(postData['pw'].encode(), bcrypt.gensalt()))
            errors['user'] = user
        return errors

    def login_validator(self, postData):
        errors = {}
        if len(User.objects.filter(username = postData['username'])) < 1:
            errors["un_pw"] = "Incorrect login information"
        else:
            hash1 = User.objects.get(username = postData['username']).password
            if bcrypt.checkpw(postData['pw'].encode(), hash1.encode()) == False:
                errors["un_pw"] = "Incorrect login information"
        if len(errors) < 1:
            user = User.objects.get(username = postData['username'])
            errors['user'] = user
        
        return errors

class WordManager(models.Manager):
    def word_validator(self, postData):
        errors = {}
        if len(postData['word']) < 1:
            errors["word_req"] = "A word is required"
        elif not LETTER_REGEX.match(postData['word']):
            errors['word_letter'] = "Word can only consist of letters"

        if len(errors) < 1:
            user = User.objects.get(id=postData['user_id'])
            project = Project.objects.get(id=postData['project_id'])
            Word.objects.create(word=postData['word'], project=project, creator=user)
            #check this
            if project.writer1==user:
                project.writer_turn=project.writer2
                project.save()
            else:
                project.writer_turn=project.writer1
                project.save()
            #check this
            if len(project.project_words.all())<2:
                project.turn_move = "add"
                project.save()
            elif len(project.project_words.all())<3:
                project.turn_move = "delete"
                project.save()
            else:
                last_action = project.project_words.all().order_by("-updated_at")[0]
                s_last_action = project.project_words.all().order_by("-updated_at")[1]
                #check this
                if last_action.deleter != None or s_last_action.deleter != None:
                    project.turn_move = "add"
                    project.save()
                else:
                    project.turn_move = "delete"
                    project.save()
        return errors

class User(models.Model):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    # inviter = models.ManyToManyField('self', related_name="invitee")
    objects = UserManager()

class Project(models.Model):
    writer1 = models.ForeignKey(User, related_name="w1_projects")
    writer2 = models.ForeignKey(User, related_name="w2_projects")
    # writer_turn = models.IntegerField(default=1)
    # writers = models.ManyToManyField(User, related_name="projects")
    writer_turn = models.ForeignKey(User, related_name="projects_turn")
    turn_move = models.CharField(max_length=6, default="add")
    # status==1 means game is still open, status==2 means game closed
    status = models.IntegerField(default=1)
    # once game is closed, title will be technically updated rather than created
    title = models.CharField(max_length=65, default="Untitled")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    updated_by = models.ForeignKey(User, related_name="updater", null=True)

class Word(models.Model):
    word = models.CharField(max_length=45)
    creator = models.ForeignKey(User, related_name="created_words")
    project = models.ForeignKey(Project, related_name="project_words")
    deleter = models.ForeignKey(User, related_name="deleted_words", null=True)
    # status==1 means word is still in project, status==2 means word has been "deleted"
    status = status = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = WordManager()

class Invite(models.Model):
    inviter = models.ForeignKey(User, related_name="inviting_user")
    invitee = models.ForeignKey(User, related_name="invited_user")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)