#!/usr/bin/env python

from main_codebuild import TriggerCodebuild as Main
import json

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
            message = json.loads(event['Records'][0]['Sns']['Message'])
        except:
            message = event
    else:
        message = event

    print("")
    print(("message: " + json.dumps(message, indent=2)))
    print("")

    main = Main(**message)
    results = main.run()

    return { 'statusCode': 200,
             'continue':results["continue"],
             'body': json.dumps(results) }

