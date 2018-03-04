from django.shortcuts import render, redirect
from django.db.models import Q

from django.contrib import messages

from .models import *

import random

def index(request):
    return render(request, 'type_type/index.html')
    
def reg_log(request):
    return render(request, 'type_type/login.html')

def login(request):
    if request.method == 'POST':
        errors = User.objects.login_validator(request.POST)
        if 'user' in errors:
            request.session['id'] = errors['user'].id
            request.session['username'] = errors['user'].username
            return redirect('/dashboard')
        else:
            for tag, error in errors.iteritems():
                messages.error(request, error, extra_tags=tag)
            return redirect('/')
    else:
        return redirect('/')
        

def register(request):
    if request.method == 'POST':
        errors = User.objects.register_validator(request.POST)
        if 'user' in errors:
            request.session['id'] = errors['user'].id
            request.session['username'] = errors['user'].username
            return redirect('/dashboard')
        else:
            for tag, error in errors.iteritems():
                messages.error(request, error, extra_tags=tag)
            return redirect('/')  
    else:
        return redirect('/')

def dashboard(request):
    if 'id' not in request.session:
        return redirect('/')
    else:
        user = User.objects.get(id=request.session['id'])
        open_projects = Project.objects.filter(Q(status=1, writer1=user) | Q(status=1, writer2=user))
        # open_projects = Project.objects.filter(Q(status=1) & Q(writer1=user) | Q(status=1) & Q(writer2=user))
        closed_projects = Project.objects.filter(Q(status=2) & Q(writer1=user) | Q(status=2) & Q(writer2=user))

        if len(user.invited_user.all()) < 3:
            all_invites=user.invited_user.all()
        else:
            all_invites = Invite.objects.filter(invitee=user)
            i_range = list(range(0, len(all_invites)))
            index = random.sample(i_range, 3)
            invites = [all_invites[index[0]], all_invites[index[1]], all_invites[index[2]]]


        if len(User.objects.all())<4:
            users = User.objects.exclude(id=user.id)
        else:
            all_users = User.objects.exclude(id=user.id)
            ui_range = list(range(0, len(all_users)))
            user_index = random.sample(ui_range, 3)
            users = [all_users[user_index[0]], all_users[user_index[1]], all_users[user_index[2]]]

        context = {
            'user' : user,
            'open_projects' : open_projects,
            'closed_projects' : closed_projects,
            'invites' : all_invites,
            'users' : users
        }
        return render(request, 'type_type/dashboard.html', context)


def show_user(request, id):
    if 'id' not in request.session:
        return redirect('/')
    else:
        user = User.objects.get(id=id)
        projects = Project.objects.filter(Q(status=2, writer1=user) | Q(status=2, writer2=user))
        context = {
            'user' : user,
            'projects' : projects
        }
        return render(request, 'type_type/show_user.html', context) 

def invite(request, id):
    if 'id' not in request.session:
        return redirect('/')
    else:
        inviter = User.objects.get(id=request.session['id'])
        invitee = User.objects.get(id=id)
        Invite.objects.create(inviter=inviter, invitee=invitee)
        return redirect('/dashboard')

def accept_invite(request, id):
    if 'id' not in request.session:
        return redirect('/')
    else:
        session_user = User.objects.get(id=request.session['id'])
        inviter = User.objects.get(id=id)
        #need something here to delete invite from table. need way to keep track of invite
        Project.objects.create(writer1=session_user, writer2=inviter, writer_turn=session_user)
        project_id = Project.objects.get(writer1=session_user, writer2=inviter, status=1).id
        # project = Project.objects.create(writer1=session_user, writer2=inviter, writer_turn=session_user)
        # project.save()
        # invite = Invite.objects.get(invitee=user)
        return redirect('/projects/' + str(project_id) + '/edit')

def show_project(request, id):
    if 'id' not in request.session:
        return redirect('/')
    else:
        # user = User.objects.get(id=request.session['id'])
        project = Project.objects.get(id=id)
        context = {
            'project' : project
        }
        return render('/type_type/show_project.html', context)

def edit_project(request, id):
    if 'id' not in request.session:
        return redirect('/')
    else:
        user = User.objects.get(id=request.session['id'])
        project = Project.objects.get(id=id)

        if project.writer1 == user:
            other_user = project.writer2
        else:
            other_user = project.writer1
        #     other_turn = "not_turn"
        # else:
        #     user_turn = "not_turn" 
        #     other_turn = "turn"
        words = Word.objects.filter(project=project)        

        context = {
            'user' : user,
            'project' : project,
            'other_user': other_user,
            'words' : words
        }
        return render(request, 'type_type/edit_project.html', context)

def add_word(request, id):
    if 'id' not in request.session:
        return redirect('/')
    elif request.method != "POST":
        return redirect('/dashboard')
    else:
        errors = Word.objects.word_validator(request.POST)
        if len(errors)>0:
            for tag, error in errors.iteritems():
                messages.error(request, error, extra_tags=tag)
            return redirect('/projects/' + str(id) +'/edit')
        else:
            return redirect('/projects/'+ str(id) +'/edit')

def all_users(request):
    if 'id' not in request.session:
        return redirect('/')
    else:
        users = User.objects.exclude(id=request.session['id'])
        session_user = User.objects.get(id=request.session['id'])
        context = {
            'users': users,
            'session_user': session_user
        }
        return render(request, 'type_type/all_users.html', context)

def view_invites(request, id):
    if 'id' not in request.session:
        return redirect('/')
    else:
        user = User.objects.get(id=id)
        invites = Invite.objects.filter(invitee=user)
        context= {
            'invites' : invites
        }
        return render(request, 'type_type/view_invites.html', context)

def delete_word(request, proj_id, word_id):
    if 'id' not in request.session:
        return redirect('/')
    else:
        word = Word.objects.get(id=word_id)
        word.status = 2
        word.deleter = User.objects.get(id=request.session['id'])
        word.save()
        project = Project.objects.get(id=proj_id)
        project.turn_move = "add"
        user= User.objects.get(id=request.session['id'])
        if project.writer1 == user:
            project.writer_turn = project.writer2
        else:
            project.writer_turn = project.writer1
        project.save()
        return redirect('/projects/'+ str(proj_id) +'/edit')


def logout(request):
    request.session.clear()
    return redirect('/')