#!/usr/bin/env python

import json
from config0_common.loggerly import Config0Logger
from config0_common.boto3_common import Boto3Common

class Stepfun_boto3(Boto3Common):

    def __init__(self,**kwargs):

        self.classname = 'Stepfun_boto3'
        self.logger = Config0Logger(self.classname)
        self.logger.debug("Instantiating %s" % self.classname)
        Boto3Common.__init__(self,'stepfunctions',**kwargs)

    def run(self,**kwargs):
        '''
        state_machine_arn = "{}:{}:{}:{}:{}-{}".format(base_arn,
                                                       region,
                                                       aws_account,
                                                       "stateMachine",
                                                       name)
        '''

        name = kwargs["name"]
        state_machine_arn = kwargs["state_machine_arn"]
        message = kwargs["message"]

        message["step_func"] = True
        message["continue"] = True
        message["is_first_run"] = True

        response = self.step_func_client.start_execution(stateMachineArn=state_machine_arn,
                                                         name=name,
                                                         input=json.dumps(message))

        execution_arn = response.get("executionArn")

        self.logger.debug('triggered execution_arn {}'.format(message,execution_arn))

        return response
