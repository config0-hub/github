#!/usr/bin/env python

from main_webhook import WebhookProcess as Main
from config0_common.loggerly import Config0Logger
import json
import os

def handler(event, context): 

    classname = 'handler'
    logger = Config0Logger(classname)

    if event["httpMethod"] == "POST":
        if event["body"] and not isinstance(event["body"],dict):
            try:
                event_body = json.loads(event["body"])
            except Exception as e:
                logger.error(e)
                raise e
        elif event["body"] and isinstance(event["body"],dict):
            event_body = event["body"]
        else:
            return {
                "statusCode": 400,
                "body": json.dumps("No json event_body provided...")
            }
    else:
        return {
            "statusCode": 405,
            "body": json.dumps(f"Invalid HTTP Method {event['httpMethod']} supplied")
        }

    path = event["path"]
    trigger_id = path.split("/")[-1]

    if os.environ.get("DEBUG_LAMBDA"):
        event["body"] = event_body
        logger.debug("x"*32)
        logger.debug("")
        logger.debug(json.dumps(event,indent=4))
        logger.debug("")
        logger.debug("x"*32)

    main = Main(trigger_id=trigger_id,
                headers=event["headers"],
                event_body=event_body)

    results = main.run()

    return { 'statusCode': 200,
             'continue':results["continue"],
             'body': json.dumps(results) }

