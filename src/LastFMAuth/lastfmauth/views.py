# Create your views here.
import urllib
import urllib2
import json
import hashlib

from django.http import *
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

from api import APIWrapper
from models import LastFMUser

API_KEY = 'YOUR_API_KEY'
API_SECRET = 'YOUR_API_SECRET'

TOKEN_URL = 'http://www.last.fm/api/auth'
API_URL = 'http://ws.audioscrobbler.com/2.0/'


def main(request):
    if request.user.is_authenticated():
        user = request.user
        lastfm_user = user.get_profile()
        print lastfm_user.user.username
        print user.username
        return render_to_response( 'main.html', { 'lastfmuser' : lastfm_user }, context_instance=RequestContext( request ) )
    else:
        return render_to_response( 'main.html', context_instance=RequestContext( request ) )

def auth( request ):
    params = {
        'api_key' : API_KEY,
    }
    data = urllib.urlencode( params )
    return HttpResponseRedirect( '%s?%s' % ( TOKEN_URL, data ) )

    return render_to_response( 'main.html', context_instance=RequestContext( request ) )

def callback( request ):
    request_token = request.GET.get( 'token' )

    api_sig = hashlib.md5('api_key%smethodauth.getSessiontoken%s%s' % ( API_KEY, request_token, API_SECRET ) ).hexdigest( )

    params = {
        'method' : 'auth.getSession',
        'api_key' : API_KEY,
        'token' : request_token,
        'api_sig' : api_sig,
        'format' : 'json',
    }

    data = urllib.urlencode( params )
    req = urllib2.Request( API_URL + '?' + data )

    response = urllib2.urlopen( req )
    session_key = json.loads( response.read( ) )['session']['key']

    api = APIWrapper( session_key, API_KEY, API_SECRET )

    data = api.query( 'user.getinfo', {}, authenticated=True )
    print data

    try:
        user = User.objects.get( username = data['user']['name'] )
    except User.DoesNotExist:
        user = User.objects.create_user( username = data['user']['name'], email='', password='' )
        user.save()

    images = data['user']['image']
    for image in images:
        if image['size'] == u'large':
            img = image['#text']

    user, created = LastFMUser.objects.get_or_create( user=user, defaults={
                            'url' : data['user']['url'], 
                            'image' : img, 
                            'playcount' : data['user']['playcount'], 
                            'age' : data['user']['age']} )
    user = authenticate( username=data['user']['name'], password='' )
    login( request, user )

    return HttpResponseRedirect( reverse( 'auth_main' ) )

def unauth( request ):
    request.session.clear()
    logout( request )
    return HttpResponseRedirect( reverse( 'auth_main' ) )
