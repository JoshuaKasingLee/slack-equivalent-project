import sys
from json import dumps
from flask import Flask, request
from flask_cors import CORS
from error import InputError

import channel 
import channels 
import auth

def defaultHandler(err):
    response = err.get_response()
    print('response', err, err.get_response())
    response.data = dumps({
        "code": err.code,
        "name": "System Error",
        "message": err.get_description(),
    })
    response.content_type = 'application/json'
    return response

APP = Flask(__name__)
CORS(APP)

APP.config['TRAP_HTTP_EXCEPTIONS'] = True
APP.register_error_handler(Exception, defaultHandler)

# Example
@APP.route("/echo", methods=['GET'])
def echo():
    data = request.args.get('data')
    if data == 'echo':
   	    raise InputError(description='Cannot echo "echo"')
    return dumps({
        'data': data
    })

@APP.route("/echo", methods=['GET'])
def channel_details():
    token = request.args.get('token')
    channel_id = request.args.get('channel_id')
    details = channel.channel_details(token,channel_id)
    return dumps(details)




if __name__ == "__main__":
    APP.run(port=0) # Do not edit this port
