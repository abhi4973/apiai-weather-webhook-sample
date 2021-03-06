#!/usr/bin/env python

from __future__ import print_function
from future.standard_library import install_aliases
install_aliases()

from urllib.parse import urlparse, urlencode
from urllib.request import urlopen, Request
from urllib.error import HTTPError

import json
import os

from flask import Flask, jsonify, request, make_response

# Flask app should start in global layout
app = Flask(__name__)


@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    result = {} # an empty dictionary

    # fulfillment text is the default response that is returned to the dialogflow request
    result["fulfillmentText"] = "your response message here"

    # you can also make rich respones like basic card, simple responses, list, table card etc.
    # you can refer this for rich response formats
    # https://github.com/dialogflow/fulfillment-webhook-json

    # you can also use custom payloads for different services like messenger or google assistant
    # below is an example of google assistant payload
    # the following paylod contains a simple response, a basic card and some suggestion chips.

    reply["payload"] = {
        "google": {
        "expectUserResponse": True,
        "richResponse": {
            "items": [
            {
                "simpleResponse": {
                    "displayText": 'text to be displayed',
                    "textToSpeech": 'text that will be used for text to speech'
                }
            },
            {
                "basicCard": {
                    "title": "card title",
                    "subtitle": "card subtitle",
                    "imageDisplayOptions": "WHITE"
                }
            }
            ],
            "suggestions": [
                {
                    "title": "chip 1"
                },
                {
                    "title": "chip 2"
                }
            ],
        }
        }
    }

    # jsonify the result dictionary
    # this will make the response mime type to application/json
    result = jsonify(result)

    # return the result json
    return make_response(result)

def results():
    # build a request object
    req = request.get_json(force=True)

    # fetch action from json
    action = req.get('queryResult').get('action')

    # return a fulfillment response
    return {'fulfillmentText': 'This is a response from webhook.'}


def processRequest(req):
    if req.get("result").get("action") != "yahooWeatherForecast":
        return {}
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = makeYqlQuery(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + urlencode({'q': yql_query}) + "&format=json"
    result = urlopen(yql_url).read()
    data = json.loads(result)
    res = makeWebhookResult(data)
    return res


def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"


def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    fullfillment = "Today in " + location.get('city') + ": " + condition.get('text') + \
             ", the temperature is " + condition.get('temp') + " " + units.get('temperature')

    print("Response:")
    print(fullfillment)

    return {
        "speech": fullfillmentText,
        "fullfillment": fullfillmentText,
        # "data": data,
        # "contextOut": [],
        "source": "apiai-weather-webhook-sample"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=False, port=port, host='0.0.0.0')

