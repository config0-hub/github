#!/usr/bin/env python

import os
import json

from main_check_build import CheckBuild as Main
from config0_common.common import print_json

def handler(event, context):

    try:
        event = json.loads(event)
    except:
        print("")
        print("event already a dictionary")
        print("")

    # this is sns trigger
    if "Records" in event:
        try:
            _message = json.loads(event['Records'][0]['Sns']['Message'])
        except:
            _message = event

        message = {
            "phase": "check_build",
            "build_status": _message["detail"]["build-status"],
            "build_arn": _message["detail"]["build-id"]
        }

        message["build_id"] = message["build_arn"].split("/")[-1]

    elif "body" in event:
        try:
            _message = json.loads(event['body'])
        except:
            _message = event
    else:
        message = event

    print("")
    print(("message: " + json.dumps(message, indent=2)))
    print("")

    main = Main(**message)
    results = main.run()

    results = { 'statusCode': 200,
                'continue':results["continue"],
                'body': json.dumps(results) }

    if os.environ.get("DEBUG_LAMBDA"):
        print("*"*32)
        print_json(results)
        print("*"*32)

    return results
