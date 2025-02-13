#!/usr/bin/env python

import os
from time import sleep
from botocore.errorfactory import ClientError
from config0_common.loggerly import Config0Logger
from config0_common.boto3_common import Boto3Common

class S3_File_boto3(Boto3Common):

    def __init__(self,**kwargs):

        self.classname = 'S3_File_boto3'
        self.logger = Config0Logger(self.classname)
        self.logger.debug("Instantiating %s" % self.classname)
        Boto3Common.__init__(self,'s3',**kwargs)

    def get_url(self,**kwargs):

        s3_bucket = kwargs["s3_bucket"]
        s3_key = kwargs["s3_key"]

        blob_url = os.path.join(s3_bucket,s3_key)

        return "s3://{}".format(blob_url)

    def get(self,**kwargs):

        dstfile = kwargs.get("dstfile")
        s3_key = kwargs.get("s3_key")
        s3_bucket = kwargs.get("s3_bucket")

        return self.client.download_file(s3_bucket,s3_key,dstfile)
        
    def exists(self,s3_bucket,s3_key):

        try:
            self.client.head_object(Bucket=s3_bucket,Key=s3_key)
        except ClientError:
            self.logger.debug('s3 object bucket {} s3_key {} does not exists'.format(s3_bucket,s3_key))
            return False

        return True

    def verify(self,s3_bucket=None,s3_key=None,wait_int=1,retries=60):

        for retry in retries:

            if self.exists(s3_bucket, s3_key):
                return True

            sleep(wait_int)

        return False

    def insert(self,**kwargs):

        srcfile = kwargs["srcfile"]
        s3_bucket = kwargs["s3_bucket"]
        s3_key = kwargs["s3_key"]
        public = kwargs.get("public")
        verify = kwargs.get("verify")

        if not public:
            response = self.client.upload_file(srcfile,s3_bucket,s3_key)
        else:
            response = self.resource.meta.client.upload_file(srcfile,
                                                             s3_bucket,
                                                             s3_key,
                                                             ExtraArgs={'ACL': 'public-read'})

        if verify:
            self.logger.debug("VERIFIED: s3_bucket {}, s3_key {} to be inserted".format(s3_bucket,s3_key))
            return self.verify(s3_bucket,s3_key)

        return response

    def remove(self,s3_bucket,s3_key):

        if not self.exists(s3_bucket,s3_key): return 

        obj = self.resource.Object(s3_bucket,s3_key)

        return obj.delete()

    def presign_upload(self,**kwargs):

        s3_bucket = kwargs["s3_bucket"]
        s3_key = kwargs["s3_key"]
        expire = kwargs.get("expire",300)

        response = self.client.generate_presigned_url(ClientMethod='put_object',
                                                      Params={'Bucket':s3_bucket,'Key':s3_key},
                                                      ExpiresIn=expire)

        return response

    def presign(self,**kwargs):

        s3_bucket = kwargs["s3_bucket"]
        s3_key = kwargs["s3_key"]
        expire = kwargs.get("expire",300)

        response = self.client.generate_presigned_url('get_object', 
                                                      Params={'Bucket':s3_bucket,'Key':s3_key},
                                                      ExpiresIn=expire)

        return response
