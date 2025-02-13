#!/usr/bin/env python

from config0_common.common import print_json
from config0_common.loggerly import Config0Logger
from config0_common.boto3_common import Boto3Common

class S3_Bucket_boto3(Boto3Common):

    def __init__(self,**kwargs):

        self.classname = 'S3_Bucket_boto3'
        self.logger = Config0Logger(self.classname)
        self.logger.debug("Instantiating %s" % self.classname)
        Boto3Common.__init__(self,'s3',**kwargs)

    def exists(self,**kwargs):

        name = kwargs["name"]

        try:
            if self.resource.Bucket(name).creation_date is not None:
                return True
        except:
            return

    def enable_permissions(self,**kwargs):

        permissions = kwargs.get("permissions")
        name = kwargs["name"]

        bucket_acl = self.resource.BucketAcl(name)

        if permissions == "all":
            permissions = "http://acs.amazonaws.com/groups/global/AllUsers"
            response = bucket_acl.put(ACL='public-read')
        else:
            permissions = "http://acs.amazonaws.com/groups/global/AuthenticatedUsers"
            response = bucket_acl.put(ACL='authenticated-read')

        return response

    def enable_encryption(self,**kwargs):

        name = kwargs["name"]
        ServerSideEncryptionConfiguration = {'Rules': [{'ApplyServerSideEncryptionByDefault': {'SSEAlgorithm': 'AES256'}},]}

        response = self.client.put_bucket_encryption(Bucket=name, 
                                                     ServerSideEncryptionConfiguration=ServerSideEncryptionConfiguration)

        return response

    def set_expire_days(self,**kwargs):

        name = kwargs["name"]
        expire_days = kwargs.get("expire_days")
        
        expire = {"Rules":[{"Status":"Enabled","Prefix":"","Expiration":{"Days":expire_days}}]}

        response = self.client.put_bucket_lifecycle(Bucket=name,
                                                    LifecycleConfiguration=expire)

        return response
        
    def create(self,**kwargs):

        name = kwargs["name"]
        encryption = kwargs.get("encryption")
        clobber = kwargs.get("clobber")
        expire_days = kwargs.get("expire_days")
        location_contraint = kwargs.get("location_contraint")

        if self.exists(**kwargs):
            self.logger.debug('bucket name = {} already exists'.format(name))
            if not clobber: return
            self.destroy(force=True,**kwargs)

        if location_contraint:
            location = {'LocationConstraint': self.aws_default_region}

            self.client.create_bucket(Bucket=name,
                                      CreateBucketConfiguration=location)
        else:
            self.client.create_bucket(Bucket=name)

        if encryption: self.enable_encryption(**kwargs)
        if expire_days: self.set_expire_days(**kwargs)

        results = {"name":name}

        if location_contraint: 
            results["location_contraint"] = location_contraint
            results["region"] = self.aws_default_region

        if kwargs.get("encryption"): results["encryption"] = True
        if kwargs.get("expire_days"): results["expire_days"] = expire_days

        return results

    def destroy(self,**kwargs):

        name = kwargs["name"]
        force = kwargs.get("force",True)

        if not self.exists(**kwargs):
            self.logger.debug('bucket name = {} does not exists'.format(name))
            return
      
        if force:
            bucket = self.resource.Bucket(name)
            bucket.objects.all().delete()

        self.client.delete_bucket(Bucket=name)

        return True

    def list(self,**kwargs):

        response = self.s3.list_buckets()

        output = []

        for bucket in response['Buckets']:
            output.append({bucket["Name"]})

        raw = kwargs.get('raw')
        if not output: return 
        if raw: return output
        print_json(output)

    def list_files(self,name,**kwargs):

        raw = kwargs.get("raw")
        keys = kwargs.get("keys")

        bucket = self.resource.Bucket(name)

        all_objects = bucket.objects.all()

        _contents = []
        _keys = []

        for _object in all_objects.objects.all():

            _content = { "bucket_name":_object.bucket_name,
                         "key":_object.key }

            _contents.append(_content)
            _keys.append(_object.key)

        if not _contents and keys: return []
        if not _contents: return 

        if keys: return _keys
        if raw: return _contents
        print_json(_contents)
