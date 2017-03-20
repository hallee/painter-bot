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
        # try:
        req = urllib2.urlopen(
            urllib2.Request(imgURL, headers={'Authorization': 'Bearer %s' % os.environ.get('SLACK_BOT_TOKEN')})
        )
        arr = np.asarray(bytearray(req.read()), dtype=np.uint8)
        img = cv2.imdecode(arr,-1) # 'load it as it is'
        stylized = stylize(img)

        scipy.misc.imsave('stylized.png', stylized)

        slack_client.api_call('files.upload', channels=channel, filename='painting.png', file=open('stylized.png', 'rb'), initial_comment='Enjoy your painting!')

        # slack_client.api_call("chat.postMessage", channel=channel,
        #                   text='Enjoy your painting!', as_user=True)

        # except:
        #     print('Error parsing image, send a Slack message')
        #     pass
    else:
        # Non-image bot mention, handle with a message or something
        pass


    

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
