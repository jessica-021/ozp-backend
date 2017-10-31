from pprint import pprint
from django.http import HttpResponse
from channels.handler import AsgiHandler
from channels.auth import channel_session_user, channel_session_user_from_http


@channel_session_user_from_http
def http_consumer(message):
    # Make standard HTTP response - access ASGI path attribute directly
    pprint(vars(message))
    pprint(vars(message.user))
    response = HttpResponse("Hello world! You asked for %s" % message.content['path'])
    # Encode that response into message format (ASGI)
    for chunk in AsgiHandler.encode_response(response):
        message.reply_channel.send(chunk)


def ws_message(message):
    # ASGI WebSocket packet-received and send-packet message types
    # both have a "text" key for their textual data.
    # pprint(vars(message))
    message.reply_channel.send({
        "text": message.content['text'],
    })
