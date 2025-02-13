#!/usr/bin/env python
#
#import os

from time import sleep
from botocore.errorfactory import ClientError
from boto3.dynamodb.conditions import Key
#from botocore.exceptions import ClientError

from config0_common.loggerly import Config0Logger
from config0_common.boto3_common import Boto3Common

class DynamodbHelper(Boto3Common):

    def __init__(self,**kwargs):

        self.classname = 'DynamodbHelper'
        self.logger = Config0Logger(self.classname)
        self.logger.debug("Instantiating %s" % self.classname)
        Boto3Common.__init__(self,'dynamodb',**kwargs)

        self.table = self.resource.Table(kwargs["table"])

        self.retry_exceptions = ('ProvisionedThroughputExceededException',
                                 'ThrottlingException')

        self.wait_int = 3
        self.total_retries = 20

    def get(self,match,total_retries=None,wait_int=None):

        if not total_retries: 
            total_retries = self.total_retries

        if not wait_int: 
            wait_int = self.wait_int

        retry = 0

        while True:

            try:
                return self.table.get_item(Key=match)
            except ClientError as err:
                if err.response['Error']['Code'] not in self.retry_exceptions:
                    raise Exception(err.response['Error'])
                self.logger.debug('Retry dynamodb get retry={} - need to wait for thread to free up'.format(retry))
                sleep(wait_int)
                retry += 1 
                if retry > total_retries:
                    msg = 'FAILED dynamodb get with retry={} - need to wait for thread to free up'.format(retry)
                    raise Exception(msg)

    def insert(self,values,total_retries=None,wait_int=None):

        if not total_retries: total_retries = self.total_retries
        if not wait_int: wait_int = self.wait_int
        retry = 0

        while True:

            try:
                return self.table.put_item(Item=values)
            except ClientError as err:
                if err.response['Error']['Code'] not in self.retry_exceptions:
                    raise Exception(err.response['Error'])
                self.logger.debug('Retry dynamodb write/update/insert retry={} - need to wait for thread to free up'.format(retry))
                sleep(wait_int)
                retry += 1 
                if retry > total_retries:
                    msg = 'FAILED dynamodb write/update/insert with retry={} - need to wait for thread to free up'.format(retry)
                    raise Exception(msg)

    def search_key(self,key,value,total_retries=None,wait_int=None):

        if not total_retries: 
            total_retries = self.total_retries

        if not wait_int: 
            wait_int = self.wait_int

        retry = 0

        while True:

            self.logger.debug('scanning key "{}" value "{}"'.format(key,value))

            try:
                return self.table.scan(FilterExpression=Key(key).eq(value))
            except ClientError as err:
                if err.response['Error']['Code'] not in self.retry_exceptions:
                    raise Exception(err.response['Error'])
                self.logger.debug('Retry dynamodb search_key retry={} - need to wait for thread to free up'.format(retry))
                sleep(wait_int)
                retry += 1 
                if retry > total_retries:
                    msg = 'FAILED dynamodb search_key with retry={} - need to wait for thread to free up'.format(retry)
                    raise Exception(msg)

    def search(self,total_retries=None,wait_int=None):

        if not total_retries: 
            total_retries = self.total_retries

        if not wait_int: 
            wait_int = self.wait_int
        retry = 0

        while True:

            try:
                return self.table.scan()
            except ClientError as err:
                if err.response['Error']['Code'] not in self.retry_exceptions:
                    raise Exception(err.response['Error'])
                self.logger.debug('Retry dynamodb search retry={} - need to wait for thread to free up'.format(retry))
                sleep(wait_int)
                retry += 1 
                if retry > total_retries:
                    msg = 'FAILED dynamodb search with retry={} - need to wait for thread to free up'.format(retry)
                    raise Exception(msg)

    def update(self,match,update_expression,expression_attribute_values,total_retries=None,wait_int=None):

        if not total_retries: total_retries = self.total_retries
        if not wait_int: wait_int = self.wait_int
        retry = 0

        while True:

            try:
                response = self.table.update_item(Key=match,
                                                  UpdateExpression=update_expression,
                                                  ExpressionAttributeValues=expression_attribute_values,
                                                  ReturnValues="UPDATED_NEW")
                return response
            except ClientError as err:
                if err.response['Error']['Code'] not in self.retry_exceptions:
                    raise Exception(err.response['Error'])
                self.logger.debug('Retry dynamodb update retry={} - need to wait for thread to free up'.format(retry))
                sleep(wait_int)
                retry += 1 
                if retry > total_retries:
                    msg = 'FAILED dynamodb update with retry={} - need to wait for thread to free up'.format(retry)
                    raise Exception(msg)

    def delete(self,match,total_retries=20,wait_int=None):

        if not total_retries: total_retries = self.total_retries
        if not wait_int: wait_int = self.wait_int
        retry = 0

        while True:

            try:
                return self.table.delete_item(Key=match)
            except ClientError as err:
                if err.response['Error']['Code'] not in self.retry_exceptions:
                    raise Exception(err.response['Error'])
                self.logger.debug('Retry dynamodb delete retry={} - need to wait for thread to free up'.format(retry))
                sleep(wait_int)
                retry += 1 
                if retry > total_retries:
                    msg = 'FAILED dynamodb delete with retry={} - need to wait for thread to free up'.format(retry)
                    raise Exception(msg)

    def raw(self):
        return self.table

class Dynamodb_boto3(Boto3Common):

    def __init__(self,**kwargs):

        self.classname = 'Dynamodb_boto3'
        self.logger = Config0Logger(self.classname,logcategory="cloudprovider")
        self.logger.debug("Instantiating %s" % self.classname)

        Boto3Common.__init__(self,'dynamodb',**kwargs)
        self.get_creds_frm_role = None

        if kwargs.get("get_creds_frm_role"): 
            self.get_creds_frm_role = True

        #self.client
        #self.resource

    def set(self,**kwargs):

        _conn = DynamodbHelper(resource=self.resource,
                               table=kwargs["table"],
                               get_creds_frm_role=self.get_creds_frm_role)

        return _conn
