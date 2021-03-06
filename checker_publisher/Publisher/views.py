from django.shortcuts import render
from django.http.response import HttpResponse
from .models import Channel, Sended
import requests
import json
import uuid
import base64
from .twitter_api import Tapi
from .media_upload import GifTweet
from .parser import parse_twitter

# Create your views here.


def dashboard(request):
    """
    Form to store the media setup
    API keys etc...
    """
    print(request)
    res = render(request, 'dashboard.html', {'id': uuid.uuid4()})
    return res


def search_project(request):
    """
    Handles project request
    """
    id = request.GET.get('project_id')
    token = request.GET.get('token')
    url = 'https://intranet.hbtn.io/projects/' + id + '.json'
    param = {'auth_token': token}
    resp = requests.get(url, params=param, headers={'Content-Type': 'application/json'})
    if resp.status_code == 200:
        js = resp.json()
        js['p'] = resp.json()['name']
        html = render(request, 'project.html', js)
        return html
    else:
        print(resp.status_code, resp.reason)
        return HttpResponse()


def check_task(request):
    """
    ask for a new correction
    """
    token = request.GET.get('token')
    id = request.GET.get('task')
    url = 'https://intranet.hbtn.io/tasks/' + id + '/start_correction.json?auth_token='+ token
    param = {}
    resp = requests.post(url, data=param, headers={'Content-Type': 'application/json'})
    if resp.status_code == 200:
        while True:
            uri = 'https://intranet.hbtn.io/correction_requests/' +\
                str(resp.json()['id']) + '.json?auth_token=' + token
            corr = requests.get(uri, headers={'Content-Type': 'application/json'})
            if (corr.json()['status'] == 'Sent'):
                pass
            elif (corr.json()['status'] == 'Done'):
                html = render(request, 'checker.html', corr.json()['result_display'])
                print(html)
                return html
            else:
                print('error')
                break
    return HttpResponse(json.dumps(resp.json()), content_type='application/json')


def send_twitter(filename, message, twitter):
    """
    Send the image via twitter Using Tapi
    """
    api = Tapi(twitter.api_key,
                twitter.api_secret,
                twitter.token,
                twitter.token_secret)
    # Accessing Twitter
    # Creating API handler instance
    
    uploader = GifTweet(filename, api)
    uploader.upload_init('image/png')
    uploader.upload_append()
    uploader.upload_finish()
    uploader.check_status()
    # Get the message
    
    return uploader.post(message).json()
    # return 'done'


def send_image(request):
    """
    Send image to channels
    """
    try:
        channels = ''.join(request.POST.get('channels')).split(',')
        token = request.POST.get('token')
        url = 'https://intranet.hbtn.io/users/me.json?auth_token=' + token
        user = requests.get(url)

        print('channels', channels)
        if channels[0] == '':
            return HttpResponse(status=305)
        # saving image in disk
        image = bytes(request.POST.get('image').split(',')[1], 'utf-8')
        image = base64.decodebytes(image)
        with open('test.png', 'wb') as fil:
            fil.write(image)
        filename = 'test.png'
        message = request.POST.get('content')
        resp = []
        for channel in channels:
            media = Channel.objects.filter(name=channel)
            if len(media) == 0:
                return HttpResponse(json.dumps({'media': channel}), status=404, content_type='application/json')
            else:
                pass
        for channel in channels:
            media = Channel.objects.filter(name=channel)
            if channel == 'twitter':
                resp.append(send_twitter(filename, message, media[0]))
            if channel == 'slack':
                pass
        # print(resp)
        resp = parse_twitter(resp[0], user.json()['email'])
        print(resp)
        template = render(request, 'sended_messages.html', {'messages': [resp]})
        return template
    except Exception as e:
        print(e)
        return HttpResponse(status=403)

def save_channel(request):
    """
    save the channel model
    """
    print(request.GET)
    token = request.GET.get('publisher_token')
    url = 'https://intranet.hbtn.io/users/me.json?auth_token=' + token
    resp = requests.get(url)
    channel = Channel.objects.filter(name=request.GET.get('channel'), email=resp.json()['email'])
    if len(channel) == 0:
        channel = Channel()
    else:
        channel = channel[0]
    channel.name = request.GET.get('channel')
    channel.api_key = request.GET.get('api_key')
    channel.api_secret = request.GET.get('api_secret')
    channel.token = request.GET.get('token')
    channel.token_secret = request.GET.get('token_secret')
    channel.email = resp.json()['email']
    channel.save()
    print(channel)
    return HttpResponse()


def check_channel(request):
    """
    Chek if a channel already exists return the dict
    """
    name = request.GET.get('channel')
    token = request.GET.get('token')
    url = 'https://intranet.hbtn.io/users/me.json?auth_token=' + token
    resp = requests.get(url)
    channel = Channel.objects.filter(email=resp.json()['email'])
    print(Channel.objects.all())
    if len(channel) == 0:
        return HttpResponse(status=404)
    return HttpResponse(json.dumps(channel[0].to_dict()), content_type='application/json')


def sended(request):
    """
    return the sended messages objects
    """
    token = request.GET.get('token')
    url = 'https://intranet.hbtn.io/users/me.json?auth_token=' + token
    resp = requests.get(url)
    sends = Sended.objects.filter(email=resp.json()['email'])
    objs = [s.to_dict() for s in sends]
    template = render(request, 'sended_messages.html', {'messages': objs})
    return template