# Painter Bot

A chat bot for Slack that 'paints' pictures. 

Uses neural networks for [style transfer](https://github.com/yusuketomoto/chainer-fast-neuralstyle). 


## Requirements

* Requires an Nvidia GPU; GTX 980, 1080, or Titan X recommended
* Ubuntu 14.04 or 16.04
* [Caffe](https://github.com/BVLC/caffe) built with GPU support and CUDNN acceleration
* `python-pip`:
        pip install chainer slackclient numpy 

## Getting Started

1. Create a new [bot integration](https://my.slack.com/services/new/bot)
2. Name the bot `painterbot` (or change the name [here](/tools/print_bot_id.py#L5))
3. Export your API token as an environment variable:

        export SLACK_BOT_TOKEN='xoxb-XXXXXXXXXXXXXX'

4. Determine your bot's ID: 

        python tools/print_bot_id.py
        export BOT_ID='XXXXXXXXX'