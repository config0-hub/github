#d!/usr/bin/python

import hmac
import six
import os
import json
import requests
import ipaddress
from hashlib import sha1
from sys import hexversion
from time import time
from config0_common.common import print_json

#from flask import request
#from flask import Flask
#from flask_restful import Resource
#from flask_restful import Api

#from config0_common.common import id_generator
#from config0_common.boto3_dynamo import Dynamodb_boto3

from config0_common.common import new_run_id
from config0_common.common import b64_encode
from config0_common.loggerly import Config0Logger
from config0_common.run_helper import Config0Reporter

#app = Flask(__name__)
#api = Api(app)

class WebhookProcess(Config0Reporter):

    def __init__(self,**kwargs):
  
        self.classname = "WebhookProcess"
        self.logger = Config0Logger(self.classname)

        self.event_body = kwargs["event_body"]
        step_func = self.event_body.get("step_func")

        Config0Reporter.__init__(self,
                step_func=step_func,
                **kwargs
                )

        self.expire_at = int(os.environ.get("BUILD_TTL","3600"))
        self.basic_events = ["push", "pull_request"]
        self.headers = kwargs["headers"]
        self.phase = "load_webhook"
        self.cdonly = True

        self._set_order()

    def _set_order(self):

        human_description = "Loading webhook information"

        inputargs = {
                "human_description": human_description,
                "role": "github/webhook_read"
        }

        self.new_order(**inputargs)

    #def _check_secret(self):

    #    secret = self.trigger_info["secret"]

    #    header_signature = self.headers.get('X-Hub-Signature')

    #    if not header_signature:
    #        self.logger.warn("header_signature not provided - no secret check")
    #        return

    #    if secret is not None and not isinstance(secret,six.binary_type):
    #        secret = secret.encode('utf-8')

    #    sha_name,signature = header_signature.split('=')

    #    if sha_name != 'sha1':
    #        msg = "sha_name needs to be sha1"
    #        return msg

    #    # HMAC requires the key to be bytes, but event_body is string
    #    try:
    #        mac = hmac.new(secret,msg=self.event_body,digestmod=sha1)
    #    except:
    #        return "cannot determine the mac from secret"

    #    # Python prior to 2.7.7 does not have hmac.compare_digest
    #    if hexversion >= 0x020707F0:
    #        if not hmac.compare_digest(str(mac.hexdigest()), str(signature)):
    #            msg = "Digest does not match signature"
    #            return msg
    #    else:
    #        if not str(mac.hexdigest()) == str(signature):
    #            msg = "Digest does not match signature"
    #            return msg

    #    return True

    #####################################
    # the below limits the source ip
    # but it's challenging to maintain
    #####################################
    #def _get_github_hook_blocks(self):

    #    try:
    #        results = requests.get('https://api.github.com/meta').json()["hooks"]
    #        status = True
    #    except:
    #        status = False
    #        msg_prefix = "Data is missing to check the acceptable ipaddresses"
    #        results = f"{msg_prefix}\n{requests.get('https://api.github.com/meta').json()}"
    #        self.logger.debug(results)

    #    return status,results

    #def _get_bitbucket_hook_blocks(self):

    #    try:
    #        results = [ entry["cidr"] for entry in requests.get('https://ip-ranges.atlassian.com').json()["items"] ]
    #        status = True
    #    except:
    #        status = False
    #        msg_prefix = "Data is missing to check the acceptable ipaddresses"
    #        results = f"{msg_prefix}\n{requests.get('https://ip-ranges.atlassian.com').json()}"
    #        self.logger.debug(results)

    #    return status,results

    #def _get_hook_blocks_by_headers(self):

    #    user_agent = str(self.headers.get('User-Agent')).lower()

    #    if "bitbucket" in user_agent:
    #        status,results = self._get_bitbucket_hook_blocks()
    #        provider = "bitbucket"
    #    else:
    #        status,results = self._get_github_hook_blocks()
    #        provider = "github"

    #    return provider,status,results

    def _chk_event(self):

        user_agent = str(self.headers.get('User-Agent')).lower()

        if "bitbucket" in user_agent:
            event_type = str(self.headers.get('X-Event-Key'))
        else:
            event_type = self.headers.get('X-GitHub-Event')

        if event_type == "ping":
            return "event is ping - nothing done"
        if event_type in self.basic_events:
            return True

        msg = 'event = "{}" must be {}'.format(event_type,self.basic_events)

        return msg

    def _get_webhook_info(self):

        # Get bitbucket fields
        # User-Agent: Bitbucket-Webhooks/2.0
        user_agent = str(self.headers.get('User-Agent')).lower()

        if "bitbucket" in user_agent:
            return self._get_bitbucket_webhook()

        # Get github fields
        event_type = self.headers.get('X-GitHub-Event')

        if event_type:
            return self._get_github_webhook()

    def _get_bitbucket_webhook(self):

        # X-Event-Key: repo:push
        event_type = str(self.headers.get('X-Event-Key'))

        try:
            _payload = json.loads(self.event_body)
        except:
            _payload = self.event_body

        webhook_info = {}

        if event_type == "repo:push": 

            # Make it more like github, just call it push
            event_type = "push"

            commit_info = _payload["push"]["changes"][0]["commits"][0]

            commit_hash = commit_info["hash"]
            webhook_info["message"] = commit_info["message"]

            if commit_info.get("user"):
                webhook_info["author"] = commit_info["author"]["user"]["display_name"]
            else:
                webhook_info["author"] = commit_info["author"]["raw"]

            webhook_info["authored_date"] = commit_info["date"]
            # add these fields to make it consistent with Github
            webhook_info["committer"] = webhook_info["author"]
            webhook_info["committed_date"] = webhook_info["authored_date"]

            webhook_info["url"] = commit_info["links"]["html"]["href"]
            webhook_info["repo_url"] = _payload["repository"]["links"]["html"]["href"]

            # More fields
            webhook_info["compare"] = _payload["push"]["changes"][0]["links"]["html"]["href"]

            try:
                webhook_info["email"] = commit_info["author"]["raw"].split("<")[1].split(">")[0].strip()
            except:
                webhook_info["email"] = commit_info["author"]["raw"]

            webhook_info["branch"] = _payload["push"]["changes"][0]["new"]["name"]

        #if event_type in ["pullrequest:created","pullrequest:updated"]:
        elif event_type in ["pullrequest:created"]:

            # Make it more like github, just call it push
            event_type = "pull_request"

            pullrequest = _payload["pullrequest"]
            source_hash = pullrequest["source"]["commit"]["hash"]
            dest_hash = pullrequest["destination"]["commit"]["hash"]

            # Branch to commit pull request to
            dest_branch = pullrequest["destination"]["branch"]["name"]
            src_branch = pullrequest["source"]["branch"]["name"]
  
            webhook_info["dest_branch"] = dest_branch
            webhook_info["src_branch"] = src_branch
            webhook_info["branch"] = dest_branch

            commit_hash = source_hash
            webhook_info["message"] = pullrequest["title"]
            webhook_info["author"] = pullrequest["author"]["display_name"]
            webhook_info["url"] = pullrequest["source"]["commit"]["links"]["html"]["href"]
            webhook_info["created_at"] = pullrequest["created_on"]
            webhook_info["authored_date"] = pullrequest["created_on"]
            webhook_info["updated_at"] = pullrequest["updated_on"]
            webhook_info["committer"] = None
            webhook_info["committed_date"] = None
            webhook_info["repo_url"] = pullrequest["destination"]["repository"]["links"]["html"]["href"]
            webhook_info["compare"] = f"{webhook_info['repo_url']}/branches/compare/{source_hash}..{dest_hash}"
            #https://bitbucket.org/<username>/<repo_name>/branches/compare/53cb2d5270c6..917c834ee6a6
            #webhook_info["email"] = None

        webhook_info["event_type"] = event_type

        if event_type == "pull_request" or event_type == "push":
            webhook_info["commit_hash"] = commit_hash
            return webhook_info

        msg = f"event_type = {event_type} not allowed"

        return {
            "status": False,
            "msg": msg
        }

    def _get_github_webhook(self):

        try:
            _payload = json.loads(self.event_body)
        except:
            _payload = self.event_body

        event_type = self.headers.get('X-GitHub-Event')

        webhook_info = {}

        if event_type == "push": 
            commit_hash = _payload["head_commit"]["id"]
            webhook_info["message"] = _payload["head_commit"]["message"]
            webhook_info["author"] = _payload["head_commit"]["author"]["name"]
            webhook_info["authored_date"] = _payload["head_commit"]["timestamp"]
            webhook_info["committer"] = _payload["head_commit"]["committer"]["name"]
            webhook_info["committed_date"] = _payload["head_commit"]["timestamp"]
            webhook_info["url"] = _payload["head_commit"]["url"]
            webhook_info["repo_url"] = _payload["repository"]["html_url"]
            webhook_info["compare"] = _payload["compare"]
            webhook_info["email"] = _payload["head_commit"]["author"]["email"]
            webhook_info["branch"] = _payload["ref"].split("refs/heads/")[1]

        elif event_type == "pull_request":
            commit_hash = _payload["pull_request"]["head"]["sha"]
            webhook_info["message"] = _payload["pull_request"]["body"]
            webhook_info["author"] = _payload["pull_request"]["user"]["login"]
            webhook_info["url"] = _payload["pull_request"]["user"]["url"]
            webhook_info["created_at"] = _payload["pull_request"]["created_at"]
            webhook_info["authored_date"] = _payload["pull_request"]["created_at"]
            webhook_info["committer"] = None
            webhook_info["committed_date"] = None
            webhook_info["updated_at"] = _payload["pull_request"]["updated_at"]

            dest_branch = _payload["pull_request"]["base"]["ref"]
            src_branch = _payload["pull_request"]["head"]["ref"]

            webhook_info["dest_branch"] = dest_branch
            webhook_info["src_branch"] = src_branch
            webhook_info["branch"] = dest_branch

        webhook_info["event_type"] = event_type

        if event_type == "pull_request" or event_type == "push":
            webhook_info["commit_hash"] = commit_hash
            return webhook_info

        msg = "event_type = {} not allowed".format(event_type)

        return {
            "status": False,
            "msg": msg
        }

    def _check_trigger_branch(self):

        # check if trigger_branch is in database
        branch = self.webhook_info.get("branch")
        trigger_branch = self.trigger_info["branch"]

        if str(branch) == str(trigger_branch): return True

        msg = "Trigger branch {} does not match branch {} to test and build on".format(str(branch),
                                                                                       trigger_branch)

        return msg

    def _save_run_info(self):
        
        # get run_id
        values = { "status":None }

        keys_to_pass = [ "codebuild_name",
                         "build_name",
                         "git_repo",
                         "git_url",
                         "docker_repository_uri",
                         "ecr_repository_uri",
                         "ecr_repo_name",
                         "docker_repo_name",
                         "docker_username",
                         "privileged_mode",
                         "image_type",
                         "build_image",
                         "build_timeout",
                         "compute_type",
                         "docker_registry",
                         "aws_default_region",
                         "trigger_id",
                         "run_id" ]

        for _key in keys_to_pass:
            if not self.trigger_info.get(_key):
                continue
            values[_key] = self.trigger_info[_key]

        values["checkin"] = int(time())
        values["expire_at"] = values["checkin"] + self.expire_at
        values["phases"] = [ self.phase ]

        if self.webhook_info:
            values["webhook_info_hash"] = b64_encode(self.webhook_info)

            if self.webhook_info.get("commit_hash"):
                values["commit_hash"] = self.webhook_info["commit_hash"]

            values["_id"] = self.run_id
            values["status"] = "in_progress"
        else:
            values["status"] = "failed"
            run_id = new_run_id()
            values["_id"] = run_id
            values["run_id"] = run_id

            try:
                failed_message = self.results["traceback"]
            except:
                failed_message = None

            if failed_message:
                values["failed_message"] = failed_message

        self.table_runs.insert(values)

        msg = "trigger_id: {} saved".format(self.trigger_id)
        self.add_log(msg)

        return 

    def execute(self,**kwargs):

        #) Check trigger event
        if not os.environ.get("DISABLE_EVENT_CHECK") == "true":
            msg = self._chk_event()

            if msg is not True: 
                self.add_log(msg)
                self.results["status"] = None
                self.results["initialized"] = None
                self.results["msg"] = msg
                return False

            _log = "event checked out ok"
            self.logger.debug(_log)
            self.add_log(_log)

        #######################################
        # disable checks
        #######################################
        #) Check secret
        #if not os.environ.get("DISABLE_SECRET_CHECK") == "true":
        #    msg = self._check_secret()

        #    if msg and msg is not True: 
        #        self.add_log(_log)
        #        self.results["status"] = "failed"
        #        self.results["initialized"] = None
        #        self.results["msg"] = msg
        #        self.results["notify"] = True
        #        return False

        #    _log = "secret checked out ok"
        #    self.logger.debug(_log)
        #    self.add_log(_log)
        #######################################

        #) Get webhook_info
        self.webhook_info = self._get_webhook_info()

        if self.webhook_info.get("status") is False:
            msg = self.webhook_info["msg"]
            self.add_log(msg)
            self.results["status"] = "failed"
            self.results["initialized"] = None
            self.results["msg"] = msg
            self.results["notify"] = True
            return False

        self.data["job_name"] = self.webhook_info["commit_hash"][0:6]

        _log = "webhook_info checked out ok"
        self.logger.debug(_log)
        self.add_log(_log)
     
        #) Check trigger branch
        if not os.environ.get("DISABLE_BRANCH_CHECK") == "true":
            msg = self._check_trigger_branch()

            if msg is not True: 
                self.add_log(msg)
                self.results["status"] = None
                self.results["initialized"] = None
                self.results["msg"] = msg
                return False

            _log = "trigger branch checked out ok"
            self.logger.debug(_log)
            self.add_log(_log)

        self.add_log("#"*32)
        self.add_log("# Summary")
        self.add_log("# Webhhook parsed and loaded")
        self.add_log("# trigger_id: {}".format(self.trigger_id))
        self.add_log("# commit_hash: {}".format(self.webhook_info.get("commit_hash")))
        self.add_log("#"*32)

        #) Save run info
        self.finalize_order()
        self._save_run_info()

        self.results["status"] = "successful"
        self.results["msg"] = "webhook processed"
        self.results["initialized"] = True
        self.results["update"] = True
        self.results["publish_vars"] = {"trigger_id":self.trigger_id}

        return True