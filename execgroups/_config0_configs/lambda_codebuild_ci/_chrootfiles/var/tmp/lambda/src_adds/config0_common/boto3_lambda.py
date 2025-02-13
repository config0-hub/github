#!/usr/bin/env python

import json
from config0_common.loggerly import Config0Logger
from config0_common.boto3_common import Boto3Common

class Lambda_boto3(Boto3Common):

    def __init__(self,**kwargs):

        self.classname = 'Lambda_boto3'
        self.logger = Config0Logger(self.classname)
        self.logger.debug("Instantiating %s" % self.classname)
        Boto3Common.__init__(self,'lambda',**kwargs)

    def run(self,**kwargs):

        name = kwargs["name"]
        message = kwargs["message"]

        response = self.client.invoke(FunctionName=name,
                                      InvocationType='Event',
                                      Payload=json.dumps(message))

        return response
