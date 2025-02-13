#!/usr/bin/env python

import boto3
from time import time

from config0_common.loggerly import Config0Logger
from config0_common.run_helper import Config0Reporter

class TriggerCodebuild(Config0Reporter):

    def __init__(self,**kwargs):

        self.classname = "TriggerCodebuild"

        self.logger = Config0Logger(self.classname)

        Config0Reporter.__init__(self,**kwargs)
        self.phase = "trigger-codebuild"
        
        session = boto3.Session()
        self.codebuild_client = session.client('codebuild')
        self.s3 = boto3.resource('s3')

        self.build_id = None
        self.build_id_suffix = None
        self.codebuild_log = None

    def _set_order(self):

        human_description = "Trigger build {}".format(self.build_name)
        inputargs = {
            "human_description": human_description,
            "role": "codebuild/build"
        }
        self.order = self.new_order(**inputargs)

    def _get_build_env_vars(self):

        self.s3_location = self.run_info["s3_location"]
        self.s3_bucket_output = self.trigger_info["s3_bucket_output"]
        self.get_docker_token()

        env_vars = []

        #)
        _env_var = { 'name': 'COMMIT_HASH',
                     'value': self.commit_hash,
                     'type': 'PLAINTEXT' }

        env_vars.append(_env_var)

        #)
        _env_var = { 'name': 'S3_LOCATION',
                     'value': self.s3_location,
                     'type': 'PLAINTEXT' }

        env_vars.append(_env_var)

        #)
        _env_var = { 'name': 'S3_BUCKET_OUTPUT',
                     'value': self.s3_bucket_output,
                     'type': 'PLAINTEXT' }

        env_vars.append(_env_var)

        #)
        _env_var = { 'name': 'AWS_DEFAULT_REGION',
                     'value': self.trigger_info["aws_default_region"],
                     'type': 'PLAINTEXT' }

        env_vars.append(_env_var)

        #)
        if self.docker_username:
            _env_var = { 'name': 'DOCKER_USERNAME',
                         'value': self.docker_username,
                         'type': 'PLAINTEXT' }

            env_vars.append(_env_var)

        #)
        if self.docker_token:
            _env_var = { 'name': 'DOCKER_TOKEN',
                         'value': self.docker_token,
                         'type': 'PLAINTEXT' }

            env_vars.append(_env_var)

        #)
        if self.ecr_repo_name:

            _env_var = { 'name': 'ECR_REPO_NAME',
                         'value': self.ecr_repo_name,
                         'type': 'PLAINTEXT' }

            env_vars.append(_env_var)

        #)
        if self.ecr_repository_uri:

            _env_var = { 'name': 'ECR_REPOSITORY_URI',
                         'value': self.ecr_repository_uri,
                         'type': 'PLAINTEXT' }

            env_vars.append(_env_var)

        #)
        if self.docker_repo_name:

            _env_var = { 'name': 'DOCKER_REPO_NAME',
                         'value': self.docker_repo_name,
                         'type': 'PLAINTEXT' }

            env_vars.append(_env_var)

        #)
        if self.docker_repository_uri:

            _env_var = { 'name': 'DOCKER_REPOSITORY_URI',
                         'value': self.docker_repository_uri,
                         'type': 'PLAINTEXT' }

            env_vars.append(_env_var)

        return env_vars

    def _run_build(self):

        self.buildspec = self.run_info.get("buildspec")

        if not self.buildspec:
            new_build = self.codebuild_client.start_build(projectName=self.build_name,
                                                          environmentVariablesOverride=self._get_build_env_vars())
        else:
            new_build = self.codebuild_client.start_build(projectName=self.build_name,
                                                          buildspecOverride=self.buildspec,
                                                          environmentVariablesOverride=self._get_build_env_vars())
                                            
        self.build_id = new_build['build']['id']
        self.data["build_id"] = self.build_id
        self.build_id_suffix = self.build_id.split(":")[1]
        self.build_expire = int(time()) + int(self.build_timeout)

        self.run_info["build_id"] = self.build_id
        self.run_info["build_expire"] = str(self.build_expire)

    def _save_run_info(self):

        self.table_runs.insert(self.run_info)
        msg = "trigger_id: {} saved".format(self.trigger_id)
        self.add_log(msg)

    def execute(self):

        self._set_order()
        self._run_build()
        self.results["build_id"] = self.build_id
        self.results["update"] = True

        summary_msg = "# Triggered \n# trigger_id: {} \n# build_id: {} \n".format(self.trigger_id,
                                                                                  self.build_id)

        self.add_log("#"*32)
        self.add_log("# Summary")
        self.add_log(summary_msg)
        self.add_log("#"*32)

        self.finalize_order()
        self._save_run_info()

        return True
