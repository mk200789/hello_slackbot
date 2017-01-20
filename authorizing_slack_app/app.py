from flask import Flask, redirect, request
import requests
import json
import urllib, urlparse, urllib2
import os
from flask import render_template

AUTHORIZE_URL = "https://slack.com/oauth/authorize"
ACCESS_TOKEN_URL = "https://slack.com/api/oauth.access"

CLIENT_ID = os.environ.get('SLACK_CLIENT_ID')
CLIENT_SECRET = os.environ.get('SLACK_CLIENT_SECRET')


temp_url = ""
temp_access_code = ""

def get_authorize_url():
    '''
    Obtains authorize url link with given client_id.
    '''

    authSetting = {'client_id': CLIENT_ID,
                   'scope': 'incoming-webhook, bot'}
    params = urllib.urlencode(authSetting)
    authURL = AUTHORIZE_URL + '?' + params

    return authURL

def get_access_token(code):
	print "code: ", code
	authSetting = {
		'client_id': CLIENT_ID,
		'client_secret': CLIENT_SECRET,
		'code': code,
		'redirect_uri': 'http://localhost:5000/done'
	}
	authSettingUrl = urllib.urlencode(authSetting)
	req = urllib2.Request(ACCESS_TOKEN_URL, authSettingUrl)
	content = urllib2.urlopen(req)
	jsonlist = json.load(content)
	
	#access token
	# access_token = jsonlist["access_token"]
	return

app = Flask(__name__)

@app.route('/')
def index():
	global temp_url
	temp_url = get_authorize_url()
	return render_template('auth.html', url_link="/authorized")


@app.route('/authorized')
def authorized():
	global temp_url
	return redirect(temp_url)

@app.route('/done')
def done():
	print "temp_access_code: ", request.args.get('code')
	get_access_token(request.args.get('code'))
	return "done"


if __name__ == '__main__':
	app.debug = True
	app.run()