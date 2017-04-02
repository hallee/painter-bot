import os
import cv2
import urllib2
import scipy.misc
import numpy as np
from neuralstyle import generate
from flask import Flask, request, jsonify, abort

app = Flask(__name__)

# @route('/hello')
@app.route('/hello', methods=['POST'])
def hello():
    print(request)

    token = request.form.get('token', None)  # TODO: validate the token
    text = request.form.get('text', None)

    print(token)
    print(text)
    return 'Hello World!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8089)