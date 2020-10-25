import pytest
import re
from subprocess import Popen, PIPE
import signal
from time import sleep
import requests
import json

# Use this fixture to get the URL of the server. It starts the server for you,
# so you don't need to.
@pytest.fixture
def url():
    url_re = re.compile(r' \* Running on ([^ ]*)')
    server = Popen(["python3", "server.py"], stderr=PIPE, stdout=PIPE)
    line = server.stderr.readline()
    local_url = url_re.match(line.decode())
    if local_url:
        yield local_url.group(1)
        # Terminate the server
        server.send_signal(signal.SIGINT)
        waited = 0
        while server.poll() is None and waited < 5:
            sleep(0.1)
            waited += 0.1
        if server.poll() is None:
            server.kill()
    else:
        server.kill()
        raise Exception("Couldn't get URL from local server")

# Testing a successful list
def test_success_http(url):
    requests.delete(url + 'clear')
    data_in = {
        'email': 'email@example.com',
        'password': 'password',
        'name_first': 'Andreea',
        'name_last': 'Viss',
    }
    response = requests.post(url + 'auth/register', json = data_in)
    payload = response.json()
    token = payload['token']

    data_in = {
        'token': token,
        'name': 'Channel1',
        'is_public': True,
    }
    response = requests.post(url + 'channels/create', json = data_in)
    payload = response.json()
    channel_id = payload['channel_id']
    
    data_in = {
        'token': token,
    }

    response = requests.get(url + 'channels/list', params = data_in)
    payload = response.json()
    assert(payload == {
        'channels': [
            {
                'channel_id': channel_id,
                'name': 'Channel1',
            }
        ]
    })
    requests.delete(url + 'clear')

# Test multiple channels under a user
def test_several_success_http(url):
    requests.delete(url + 'clear')
    data_in = {
        'email': 'email@example.com',
        'password': 'password',
        'name_first': 'Andreea',
        'name_last': 'Viss',
    }
    response = requests.post(url + 'auth/register', json = data_in)
    payload = response.json()
    token = payload['token']
    
    data_in = {
        'token': token,
        'name': 'Channel1',
        'is_public': True,
    }
    response = requests.post(url + 'channels/create', json = data_in)
    payload = response.json()
    channel_id = payload['channel_id']

    data_in = {
        'token': token,
        'name': 'Channel2',
        'is_public': False,
    }
    response = requests.post(url + 'channels/create', json = data_in)
    payload = response.json()
    channel_id2 = payload['channel_id']

    data_in = {
        'token': token,
    }

    response = requests.get(url + 'channels/list', json = data_in)
    payload = response.json()
    assert(payload == {
        'channels': [
            {
                'channel_id': channel_id,
                'name': 'Channel1',
            },
            {
                'channel_id': channel_id2,
                'name': 'Channel2',
            }
        ]
    })
    requests.delete(url + 'clear')

