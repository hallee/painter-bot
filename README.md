# Slack Painter Bot Command

A slash command for Slack that 'paints' pictures. 

Uses neural networks for [style transfer](https://github.com/yusuketomoto/chainer-fast-neuralstyle). 


## Requirements

* Requires an Nvidia GPU; GTX 980, 1080, or Titan X recommended
* Ubuntu 14.04 or 16.04
* [Caffe](https://github.com/BVLC/caffe) built with GPU support and CUDNN acceleration
* `python-pip`:

        pip install chainer slackclient numpy flask

## Getting Started

1. Create a new [Slack app](https://api.slack.com/apps)
2. Export your app's API token as an environment variable:

        export SLACK_BOT_TOKEN='xoxb-XXXXXXXXXXXXXX'

    You can place this in `~/.bashrc` to set the environment variable for every shell.

3. Install [Localtunnel](https://localtunnel.github.io/www/):

        npm install -g localtunnel

    Localtunnel will route external traffic to your local machine, and provides an HTTPS link that we can use for slack integration. Choose a unique subdomain - we will use `painterbotexample`

4. Run Localtunnel on port 8089:

        lt --port 8089 --subdomain painterbotexample

    This means our external domain will be `https://painterbotexample.localtunnel.me`.

5. Create a new [slash command](https://api.slack.com/slash-commands). Set the command as `/painterbot`, and the 'Request URL' as `https://painterbotexample.localtunnel.me\hello`. 



