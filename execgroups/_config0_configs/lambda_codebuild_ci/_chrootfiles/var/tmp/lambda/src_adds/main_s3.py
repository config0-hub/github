#!/usr/bin/env python

import shutil
import os
import boto3
from config0_common.common import execute5

from config0_common.common import b64_encode
from config0_common.common import rm_rf
from config0_common.loggerly import Config0Logger
from config0_common.run_helper import Config0Reporter

class PkgCodeToS3(Config0Reporter):

    '''

    This is not currently being used.

    It was initially built to be packaged as lambda function to:

    1) retrieve git_url and s3 bucket from environment variables
    2) retrieve ssh deploy key either from the environment variable or SSM in AWS
    3) clone the commit hash for the code repository and upload as a zip file to s3 bucket

    '''

    def __init__(self,**kwargs):

        self.classname = "PkgCodeToS3"

        self.logger = Config0Logger(self.classname)

        Config0Reporter.__init__(self,**kwargs)
        self.phase = "pkgcode-to-s3"

        session = boto3.Session()
        self.ssm = session.client('ssm')

        self.private_key_path = "/tmp/id_rsa"
        self.clone_dir = "/tmp/code/src"
        self.base_ssh = "GIT_SSH_COMMAND='ssh -i {} -o StrictHostKeyChecking=no -o IdentitiesOnly=yes'".format(self.private_key_path)
        #self.base_ssh = "export HOME=/tmp/config0; GIT_SSH_COMMAND='ssh -i {} -o StrictHostKeyChecking=no -o IdentitiesOnly=yes'".format(self.private_key_path)

        rm_rf(self.private_key_path)
        rm_rf(self.clone_dir)
        #rm_rf("/tmp/config0")
        #os.system("mkdir -p /tmp/config0")

        self._set_order()

        self.maxtime = 180

    def _set_order(self):

        human_description = "Fetch code and upload to s3"
        inputargs = { "human_description":human_description }
        inputargs["role"] = "s3/upload"
        self.new_order(**inputargs)

    def _set_s3_key(self):

        self.local_src = str("/tmp/{}.zip".format(self.commit_hash))
        self.pkg_name = str("code-{}".format(self.commit_hash[0:6]))

        _key = str("src/{}/{}/source.zip".format(self.git_repo,self.pkg_name))

        self.remote_src = "s3://{}/{}".format(self.s3_bucket_tmp,_key)

    def _write_private_key(self):

        private_key_hash = os.environ.get("PRIVATE_KEY_HASH")

        if not private_key_hash and self.ssm_ssh_key:
            _ssm_info = self.ssm.get_parameter(Name=self.ssm_ssh_key,WithDecryption=True)
            private_key_hash = _ssm_info["Parameter"]["Value"]

        if not private_key_hash:
            msg = "private_key_hash not found"
            raise Exception(msg)

        cmd = 'echo "{}" | base64 -d > {}'.format(private_key_hash,self.private_key_path)
        execute5(cmd)

        os.chmod(self.private_key_path, 0o600)

    def _fetch_code(self):

        cmd = "mkdir -p {}".format(self.clone_dir)
        execute5(cmd)

        os.chdir(self.clone_dir)

        # this assumes the commit hash within the last 10 years/commits
        cmds = []
        cmd = "git init"
        cmds.append(cmd)
        cmd = 'git remote add origin "{}"'.format(self.git_url)
        cmds.append(cmd)

        if self.git_depth:
            cmd = '{} git fetch --quiet origin --depth {}'.format(self.base_ssh,self.git_depth)
        else:
            cmd = '{} git fetch --quiet origin'.format(self.base_ssh)

        cmds.append(cmd)

        if self.git_depth:
            cmd = '{} git fetch --quiet --depth {} origin {}'.format(self.base_ssh,self.git_depth,self.commit_hash)
        else:
            cmd = '{} git fetch --quiet origin {}'.format(self.base_ssh,self.commit_hash)

        cmds.append(cmd)
        cmd = '{} git checkout --quiet -f {}'.format(self.base_ssh,self.commit_hash)
        cmds.append(cmd)
        cmd = 'rm -rf .git'
        cmds.append(cmd)

        for _cmd in cmds: 
            print("#"*32)
            print("")
            print(_cmd)
            print("")
            execute5(_cmd)

    def _archive_code(self):

        os.chdir(self.clone_dir)
        shutil.make_archive('/tmp/{}'.format(self.commit_hash),'zip',verbose=True)

        # for some reason, if set self.s3_key and insert it here
        # the upload to s3 is an ascii file

        self.file.insert(s3_bucket=self.s3_bucket_tmp,
                         s3_key=str("src/{}/code-{}/source.zip".format(self.git_repo,self.commit_hash[0:6])),
                         srcfile=self.local_src)

        print("#"*32)
        print("")
        print("Uploading code {}".format(self.remote_src))
        print("")
        print("#"*32)

    def _save_run_info(self):

        buildspec = self._get_user_buildspec()
        if buildspec: self.run_info["buildspec"] = buildspec
        #if buildspec: self.run_info["buildspec"] = b64_encode(buildspec)

        self.run_info["s3_location"] = self.remote_src
        self.run_info["pkg_name"] = self.pkg_name
        self.table_runs.insert(self.run_info)

        msg = "trigger_id: {} saved".format(self.trigger_id)
        self.add_log(msg)

    def _get_user_buildspec(self):

        #os.chdir(self.clone_dir)

        _file_path = os.path.join(self.clone_dir,self.buildspec_file)
        if not os.path.exists(_file_path): return

        self.file.insert(s3_bucket=self.s3_bucket_tmp,
                         s3_key=str("src/{}/code-{}/buildspec.yml".format(self.git_repo,self.commit_hash[0:6])),
                         srcfile=_file_path)

        _key = str("src/{}/code-{}/buildspec.yml".format(self.git_repo,self.commit_hash[0:6]))

        return "arn:aws:s3:::{}/{}".format(self.s3_bucket_tmp,_key)

    def execute(self):

        self.git_url = self.run_info["git_url"]
        self.ssm_ssh_key = self.trigger_info["ssm_ssh_key"]
        self.git_repo = self.trigger_info["git_repo"]
        self.git_depth = self.run_info.get("git_depth")
        self.buildspec_file = self.trigger_info.get("buildspec_file","buildspec.yml")

        self._set_s3_key()
        self._write_private_key()
        self._fetch_code()
        self._archive_code()

        self.results["msg"] = "code fetched git_repo {}, commit_hash {} to {}".format(self.git_repo,
                                                                                      self.commit_hash,
                                                                                      self.remote_src)

        self.results["update"] = True
        self.results["publish_vars"] = {"src":self.remote_src}

        self.add_log("#"*32)
        self.add_log("# Summary")
        self.add_log(log="# Code fetched and uploaded")
        self.add_log(log='# Git Repo: "{}"'.format(self.git_repo))
        self.add_log(log='# Commit hash: "{}"'.format(self.commit_hash))
        self.add_log(log='# Remote Location: "{}"'.format(self.remote_src))
        self.add_log("#"*32)

        self.finalize_order()
        self._save_run_info()

        return True
