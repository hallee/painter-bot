import os
import re
import cv2
import base64
import urllib2
import scipy.misc
import numpy as np
# from neuralstyle import generate
from flask import Flask, request, jsonify

app = Flask(__name__)

# @route('/hello')
@app.route('/hello', methods=['POST'])
def hello():
    token = request.form.get('token', None)  # TODO: validate the token
    text = request.form.get('text', None)
    user = request.form.get('user_id', None)

    print(token)
    print(text)
    print(user)
    url = None
    regexMatch = re.search("(?P<url>https?://[^\s]+)", text)
    if regexMatch is not None:
        url = regexMatch.group("url")

    if url is not None:
        # In case we got a Slack image URL, 
        # we need to fetch it w/ authentication:
        if 'slack.com' in url:
            req = urllib2.urlopen(
                urllib2.Request(url, headers={'Authorization': 'Bearer %s' % os.environ.get('SLACK_BOT_TOKEN')})
            )
        else:
            req = urllib2.urlopen(url)

        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        img = cv2.imdecode(arr,-1) # 'load it as it is'
        img = cv2.resize(img, dimensionsKeepAspect(512, 512, img.shape[1], img.shape[0]), interpolation = cv2.INTER_AREA)
        # _, buffer = cv2.imencode('.jpg', img)
        # jpgResponse = base64.b64encode(buffer)

        return jsonify({
            "response_type": "ephemeral",
            "text": ('Here\'s your painting:'),
            "attachments": [
                {
                    "text": " ",
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
        })

    else:
        return 'Give me an image URL and I\'ll try to paint it!'

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8089)