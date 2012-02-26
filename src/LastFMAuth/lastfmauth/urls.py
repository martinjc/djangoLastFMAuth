from django.conf.urls.defaults import *
from LastFMAuth.lastfmauth.views import *

urlpatterns = patterns( 'LastFMAuth.lastfmauth.views',

    #
    # main page
    url( r'^$', view=main, name='auth_main' ),

    #
    # auth call
    url( r'^auth/$', view=auth, name='auth_auth' ),

    #
    # callback
    url( r'^callback/', view=callback, name='auth_return' ),

    #
    # logout
    url( r'^logout/$', view=unauth, name='auth_logout' ),
)