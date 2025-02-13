#!/usr/bin/env python

import os
import json
import sys
import requests
from config0_common.common import b64_decode

class SlackNotify(object):

    def __init__(self,**kwargs):

        self.username = kwargs["username"]
        self.header_text = kwargs["header_text"]
        self.divider = { "type": "divider" }

        self._set_base()

    def _setup(self,inputargs):

        self.inputargs = inputargs

        slack_webhook_b64 = inputargs.get("slack_webhook_b64")

        if not slack_webhook_b64: 
            slack_webhook_b64 = os.environ.get("SLACK_WEBHOOK_B64")

        if not slack_webhook_b64: 
            return

        # this variables need to be set
        try:
            self.url = b64_decode(slack_webhook_b64)
        except:
            self.url = None

        if not self.url: 
            return

        self.title = None
        self.payload = []
        self.message = []
        self.link = []

        return True

    def _set_misc(self):

        self.icon_emoji = self.inputargs.get("icon_emoji",":arrows_counterclockwise:")
        self.channel = self.inputargs.get("slack_channel")

    def _set_base(self):

        self.slack_data = { "username": self.username,
                            "blocks": [] }

    def _set_headers(self):

        self.header = { "type": "header",
                        "text": { "type": "plain_text",
                                  "text": self.header_text,
                                  "emoji": True }
                        }

    def _set_title(self):

        text = self.inputargs.get("title")
        if not text: text = "This is the summary"

        self.title = { "type": "section",
                       "text": { "type": "plain_text",
                                 "text": text,
                                 "emoji": True }
                       }

    def _set_payload(self):

        payload = self.inputargs.get("payload")
        if not payload: return

        self.payload.append(self.divider)
        self.payload.append({ "type": "section",
                              "text": { "type": "plain_text",
                                        "text": json.dumps(payload,indent=4),
                                        "emoji": True }
                              })

    def _set_link(self):

        link = self.inputargs.get("link")
        if not link: return 

        self.link.append( { "type": "section",
                            "text": { "type": "mrkdwn",
                                      "text": "<{}|Codebuild Details>".format(link) },
                            "accessory": { "type": "button",
                                           "text": { "type": "plain_text",
                                                     "text": "View",
                                                     "emoji": True },
                                           "value": "build_details",
                                           "url": link,
                                           "action_id": "button-action" }
                            } )

    def _set_message(self):

        message = self.inputargs.get("message")
        if not message: return 

        self.message.append(self.divider)
        self.message.append({ "type": "section",
                                      "text": { "type": "plain_text",
                                                "text": message,
                                                }
                              } )

    def _assemble(self):

        self._set_headers()
        self._set_title()
        self._set_payload()
        self._set_message()
        self._set_link()
        self._set_misc()

        if self.channel: self.slack_data["channel"] = self.channel
        self.slack_data["icon_emoji"] = self.icon_emoji
        if self.header: self.slack_data["blocks"].append(self.header)
        self.slack_data["blocks"].append(self.divider)
        if self.title: self.slack_data["blocks"].append(self.title)
        if self.payload: self.slack_data["blocks"].extend(self.payload)
        if self.message: self.slack_data["blocks"].extend(self.message)
        if self.link: self.slack_data["blocks"].extend(self.link)
        self.slack_data["blocks"].append(self.divider)

    def _send_message(self):

        byte_length = str(sys.getsizeof(self.slack_data))
        headers = {'Content-Type': "application/json", 'Content-Length': byte_length}

        response = requests.post(self.url, data=json.dumps(self.slack_data), headers=headers)

        if response.status_code == 200: return True

        raise Exception(response.status_code, response.text)

    def run(self,inputargs):

        status = self._setup(inputargs=inputargs)

        if not status: 
            return

        self._assemble()
        self._send_message()

if __name__ == '__main__':

    main = SlackNotify()
    main.run(inputargs=b64_decode(os.environ["SLACK_INPUTARGS"]))
