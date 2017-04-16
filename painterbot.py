import os
import re
import cv2
import json
import urllib2
import requests
import numpy as np
from neuralstyle import generate
from multiprocessing import Process
from slackclient import SlackClient
from flask import Flask, request, jsonify


app = Flask(__name__)
slack_client = SlackClient(os.environ.get('SLACK_APP_TOKEN'))
userImages = {}


# @route('/startconversation')
@app.route('/startconversation', methods=['POST'])
def hello():
    token = request.form.get('token', None)  # TODO: validate the token
    text = request.form.get('text', None)
    user = request.form.get('user_id', None)
    respond = request.form.get('response_url', None)

    url = None
    regexMatch = re.search("(?P<url>https?://[^\s]+)", text)
    if regexMatch is not None:
        url = regexMatch.group("url")

    if url is not None:
        # In case we got a Slack image URL, 
        # we need to fetch it w/ authentication:
        if url[-4:] != '.png' and url[-4:] != '.jpg' and url[-5:] != '.jpeg':
            return('I can\'t paint that. Try something else!')

        if 'slack.com' in url:
            privateURL = urllib2.Request(url, headers={'Authorization': 'Bearer %s' % os.environ.get('SLACK_APP_TOKEN')})
            print('requesting Slack image:')
            req = urllib2.urlopen(privateURL)
            # print(req.read().decode("utf8", 'ignore'))
        else:
            req = urllib2.urlopen(url)

        arr = np.asarray(bytearray(req.read()))
        
        headers = { 'Content-Type' : 'application/json' }

        # Process image
        p = Process(target=processImage, args=(arr, respond, user, headers,))
        # processImage(img, respond, user, headers)
        p.start()
        p.join()

        return 'Working on that...', 200

    else:
        return 'Give me an image URL and I\'ll try to paint it!'


@app.route('/buttonreply', methods=['POST'])
def buttonreply():
    payload = request.form.get('payload', None)
    jsonPayload = json.loads(payload)
    token = jsonPayload['token']  # TODO: validate the token
    user = jsonPayload['user']['id']
    action = jsonPayload['actions'][0]['value']
    respond = jsonPayload['response_url']

    if action == 'delete':
        return jsonify({
            "delete_original": "Yes",
        })

    if user in userImages:
        imageURL = userImages[user]
        headers = {'Content-Type' : 'application/json'}
        initialReply = {
            "response_type": "in_channel",
            "delete_original": "Yes",
            "text": "I made a painting:",
            "attachments": [
                {
                    "title": " ",
                    "image_url": imageURL,
                }
            ]
        }
        r = requests.post(respond, data=json.dumps(initialReply), headers=headers)
        return ''
    else:
        return 'I couldn\'t find your image. Try again!'
    return 'Final Reply'


def uploadImage(img, user):
    imageURL = ''
    _, buffer = cv2.imencode('.jpg', img)
    imageBinary = buffer.tostring()
    # First, upload the image (will be private):
    response = slack_client.api_call('files.upload', filename='Painting.jpg', file=imageBinary)
    if 'file' in response:
        if 'id' in response['file']:
            fileID = response['file']['id']
            # Next, make the image public:
            response = slack_client.api_call('files.sharedPublicURL', file=fileID)

    if 'file' in response:
        if 'permalink_public' in response['file']:
            imageURL = response['file']['permalink_public']
    return imageURL


def processImage(arr, respond, user, headers):
    import cv2
    
    img = cv2.imdecode(arr, -1) # 'load it as it is'

    if img is None:
        response = 'I had trouble parsing that. Try another!'
        r = requests.post(respond, data=json.dumps(response), headers=headers)
        return
    if img.shape is None:
        response = 'I had trouble parsing that image. Try another!'
        r = requests.post(respond, data=json.dumps(response), headers=headers)
        return

    img = cv2.resize(img, dimensionsKeepAspect(1200, 1200, img.shape[1], img.shape[0]), interpolation = cv2.INTER_AREA)

    styled = img #stylize(img)
    time.sleep(10)
    styled = cv2.cvtColor(styled, cv2.COLOR_BGR2RGB)

    imageURL = uploadImage(styled, user)
    print(imageURL)
    userImages[user] = imageURL

    paintingReply = {
        "response_type": "ephemeral",
        "delete_original": "Yes",
        "text": "Here's your painting:",
        "attachments": [
            {
                "title": " ",
                "image_url": imageURL,
                "fallback": "ERROR",
                "callback_id": "share_painting",
                "color": "#3AA3E3",
                "attachment_type": "default",
                "actions": [
                    {
                        "name": "send",
                        "text": "Send",
                        "type": "button",
                        "value": "send"
                    },
                    {
                        "name": "delete",
                        "text": "Delete",
                        "style": "danger",
                        "type": "button",
                        "value": "delete"
                    }
                ]
            }
        ]
    }

    r = requests.post(respond, data=json.dumps(paintingReply), headers=headers)
    return


def dimensionsKeepAspect(targetWidth, targetHeight, oldWidth, oldHeight):
    """
    Gives resizing dimensions to keep an image within (targetWidth, targetHeight)
    while preserving the original aspect ratio. Does not upsize iamges smaller
    than the target dimensions.
    """
    if (oldWidth < targetWidth) and (oldHeight < targetHeight):
        return (int(oldWidth), int(oldHeight))
    oldAspect = oldWidth/float(oldHeight)
    newAspect = targetWidth/float(targetHeight)
    if oldAspect > newAspect:
        newWidth = targetWidth
        newHeight = targetWidth/oldAspect
        return (int(newWidth), int(newHeight))
    elif oldAspect < newAspect:
        newHeight = targetHeight
        newWidth = targetHeight*oldAspect
        return (int(newWidth), int(newHeight))
    elif oldAspect == newAspect:
        return (int(targetWidth), int(targetHeight))


def stylize(img):
    stylized = generate.stylize(img)
    return stylized


@app.errorhandler(500)
def internal_error(error):
    return "Application error. Try something else!"


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8089)
