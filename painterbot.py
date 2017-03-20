import os
import cv2
import time
import urllib2
import scipy.misc
import numpy as np
from slacker import Slacker
from slackclient import SlackClient
from neuralstyle import generate

# constants
BOT_ID = os.environ.get("BOT_ID")
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
slack = Slacker(os.environ.get('SLACK_BOT_TOKEN'))

abspath = os.path.abspath(__file__)
dname = os.path.dirname(abspath)
os.chdir(dname)

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        contain an image URL. If so, attempts to load the image and sends 
        it to the DNN handler.
    """
    imgURL = ""
    for key in command:
        if key == "file":
            file = command[key]
            for keyf in file:
                if keyf == "url_private":
                    print(file[keyf])
                    imgURL = file[keyf]

    if imgURL != "":
        try:
            slack_client.api_call("chat.postMessage", channel=channel,
                  text='Working on your painting...', as_user=True)
            req = urllib2.urlopen(
                urllib2.Request(imgURL, headers={'Authorization': 'Bearer %s' % os.environ.get('SLACK_BOT_TOKEN')})
            )
            arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
            img = cv2.imdecode(arr,-1) # 'load it as it is'
            img = cv2.resize(img, dimensionsKeepAspect(512, 512, img.shape[1], img.shape[0]), interpolation = cv2.INTER_AREA)
            
            stylized = stylize(img)

            scipy.misc.imsave('stylized.png', stylized)

            slack_client.api_call('files.upload', channels=channel, filename='painting.png', file=open('stylized.png', 'rb'), initial_comment='Enjoy your painting!')
        except Exception as e:
            print(e)
            slack_client.api_call("chat.postMessage", channel=channel,
                  text='I had trouble with that image. Sorry!', as_user=True)
            pass
    else:
        # Non-image bot mention, handle with a message or something
        pass


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
    # cv2.imshow("img", stylized)
    # cv2.waitKey(0)

    return stylized

def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                # ['text'].split(AT_BOT)[1].strip().lower()
                return output, \
                       output['channel']
    return None, None

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 0.25 # quarter-second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
