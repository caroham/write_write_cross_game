from django.conf.urls import url
from . import views        
urlpatterns = [
   url(r'^$', views.index),
   url(r'^register_login$', views.reg_log),
   url(r'^login$', views.login),    
   url(r'^register$', views.register),    
   url(r'^dashboard$', views.dashboard),  
   url(r'^projects/(?P<id>\d+)/edit$', views.edit_project), 
   url(r'^projects/(?P<id>\d+)$', views.show_project), 
   url(r'^projects/(?P<id>\d+)/add_word$', views.add_word), 
   url(r'^users$', views.all_users),
   url(r'^users/(?P<id>\d+)$', views.show_user), 
   url(r'^invite/(?P<id>\d+)$', views.invite), 
   url(r'^invites/(?P<id>\d+)/view$', views.view_invites), 
   url(r'^accept/(?P<id>\d+)$', views.accept_invite), 
   url(r'^delete/(?P<proj_id>\d+)/(?P<word_id>\d+)$', views.delete_word), 
   url(r'^logout$', views.logout)
]