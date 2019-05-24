from django.urls import path


from . import views

urlpatterns = [
    #path('', views.index, name='index'),
    path('', views.dashboard, name='index'),
    path('content_diff', views.htmldiffview, name='content_diff'),
    path('dashboard', views.dashboard, name='dashboard'),

    # test sites
    path('test_reply', views.test_reply, name='test_reply')
]
