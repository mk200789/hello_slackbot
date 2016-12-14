import os
import time
from slackclient import SlackClient
import sys
import json

try:
    import apiai
except ImportError:
    sys.path.append(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir)
    )
    import apiai

#bot name
BOT_NAME = 'hello-slackbot'

#get bot id
BOT_ID = os.environ.get('SLACK_BOT_ID')

#get slack bot token
SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')

#get aiapi access token
APIAI_ACCESS_TOKEN = os.environ.get('APIAI_DEVELOPER_ACCESS_TOKEN')

#set slack client
slack_client = SlackClient(SLACK_BOT_TOKEN)

#set apiai client
apiai_client = apiai.ApiAI(APIAI_ACCESS_TOKEN)


# constants
AT_BOT = "<@" + BOT_ID + ">"
EXAMPLE_COMMAND = "do"

def parse_slack_output(slack_rtm_output):
	output_list = slack_rtm_output

	if output_list and len(output_list) > 0:
		for output in output_list:
			if len(output.keys()) < 9:
				if output and 'text' in output and AT_BOT in output['text']:
					# return text after the @ mention, whitespace removed
					return output['text'].split(AT_BOT)[1].strip().lower(), output['channel']
				elif output and 'text' in output and output['channel'].startswith('D'):
					return output['text'].strip().lower(), output['channel']
	return None, None


def handle_command(command, channel):
	attachments = []
	response = "Not sure what you mean. \nPlease use the " + EXAMPLE_COMMAND + "* command with numbers :robot_face:"
	request = apiai_client.text_request()
	request.query = command
	r = request.getresponse().read()
	ai_response = json.loads(r)['result']
	if ai_response['action'] == 'smalltalk.greetings' or ai_response['action'] == 'smalltalk.user':
		response = ai_response['fulfillment']['speech']
	elif command.startswith(EXAMPLE_COMMAND):
		response = "Sure...write some more code then I can do that!"
		attachments = [{
			"text": "Do you want to see a youtube video?",
			"attachment_type": "default",
			"color": "#dd2e4e",
			"actions": [{
				"name": "yes",
				"text": "Yes",
				"type": "button",
				"value": "yes",
				"confirm": {
					"title": "Are you sure?",
					"text": "It's gonna be awesome if you do!",
					"ok_text": "Yes",
					"dismiss_text": "No"
					}
				},{
				"name": "no",
				"text": "No",
				"type": "button",
				"value": "no"
				}
			]
		}]
	slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True, attachments= attachments)



if __name__ == '__main__':
	READ_WEBSOCKET_DELAY = 0.5 #per second
	if slack_client.rtm_connect():
		print(BOT_NAME + " connected and running!")
		while True:
			rtm = slack_client.rtm_read()

			command, channel = parse_slack_output(rtm)

			if command and channel:
				handle_command(command, channel)

			time.sleep(READ_WEBSOCKET_DELAY)
	else:
		print(BOT_NAME+ " not connected!")