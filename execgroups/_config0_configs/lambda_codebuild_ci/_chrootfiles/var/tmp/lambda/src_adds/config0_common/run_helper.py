#!/usr/bin/python

import os
import json
import boto3
import traceback
from time import time

from config0_common.common import id_generator
from config0_common.common import b64_encode
from config0_common.common import b64_decode
from config0_common.common import rm_rf
from config0_common.common import print_json

from config0_common.common import new_run_id
from config0_common.common import get_queue_id
from config0_common.common import execute_http_post
from config0_common.boto3_dynamo import Dynamodb_boto3
from config0_common.boto3_file import S3_File_boto3
from config0_common.boto3_lambda import Lambda_boto3
from config0_common.loggerly import Config0Logger
from config0_common.notify_slack import SlackNotify
#from config0_common.boto3_stepfunc import Stepfun_boto3

class Config0Reporter(object):

    def __init__(self,**kwargs):
  
        self.start_time = int(time())

        self.classname = "Config0Reporter"
        self.logger = Config0Logger(self.classname)

        self.slack = SlackNotify(username="ElasticDevNotifyBot",
                                 header_text="Config0")

        self.dynamodb_boto3 = Dynamodb_boto3()
        
        self.file = S3_File_boto3()

        session = boto3.Session()
        self.ssm = session.client('ssm')
        self.lambda_client = Lambda_boto3()

        _runs = os.environ.get("BUILD_RUNS",
                               "ci-shared-runs")
        
        _settings = os.environ.get("BUILD_SETTINGS",
                                   "ci-shared-settings")
        
        self.table_runs = self.dynamodb_boto3.set(table=_runs)
        self.table_settings = self.dynamodb_boto3.set(table=_settings)

        self.run_id = kwargs.get("run_id")
        self.trigger_id = kwargs.get("trigger_id")
        self.build_id = kwargs.get("build_id")
        self.step_func = kwargs.get("step_func")

        self.cdonly = True
        self.webhook_info = None
        self.queue_host = None
        self.active = None
        self.token = None
        self.data = None
        self.order = None
        self.status = None
        self.phase = None
        self.config0_url = None
        self.trigger_info = {}
        self.run_info = {}

        self.docker_repo_name = None

        self.results = { "msg":None,
                         "done":None,
                         "chk_t0":None,
                         "chk_count":None,
                         "step_func":self.step_func,
                         "status":None,
                         "build_status":None,
                         "log":"",
                         "close":None,
                         "initialized":True,
                         "update":None,
                         "notify":None,
                         "continue":True,
                         "_id":self.run_id,
                         "run_id":self.run_id,
                         "trigger_id":self.trigger_id }

    def notify(self):

        inputargs = self._get_notify_inputargs()

        if not inputargs: 
            return

        try:
            self.slack.run(inputargs)
        except:
            _err_mesg = traceback.format_exc()
            print(f"ERROR: could not slack notify:\n {_err_mesg}")

    def set_trigger_info(self):

        if not self.trigger_id and self.build_id:
            self._load_run()
            self.trigger_id = self.run_info["trigger_id"]

        if not self.trigger_id:
            self.trigger_info = False
            return {
                "status":False,
                "failed_message":"self.trigger_id is None/False"
            }

        match = {"_id":self.trigger_id}
        self.logger.debug("looking for trigger match {}".format(match))
        query = self.table_settings.get(match)

        if not query.get("Item"):
            return {
                "status": False,
                "failed_message": "trigger_id info is not found"
            }

        try:
            self.trigger_info = query["Item"]
        except:
            self.trigger_info = False
            return {
                "status":False,
                "failed_message":"Item not for trigger info not found in db"
            }

        return {"status":True}

    def setup(self):

        set_info = self.set_trigger_info()

        if set_info.get("status") is False:
            self.add_log(set_info.get("failed_message"))
            self.results["status"] = "failed"
            self.results["msg"] = set_info.get("failed_message")
            self.results["notify"] = True
            return set_info

        self.ssm_callback_key = self.trigger_info["ssm_callback_key"]
        self.ssm_ssh_key = self.trigger_info["ssm_ssh_key"]
        self.user_endpoint = self.trigger_info["user_endpoint"]
        self.s3_bucket = self.trigger_info["s3_bucket"]
        self.s3_bucket_tmp = self.trigger_info["s3_bucket_tmp"]
        self.s3_bucket_cache = self.trigger_info["s3_bucket_cache"]
        self.s3_bucket_output = self.trigger_info["s3_bucket_output"]
        
        self.build_name = self.trigger_info.get("build_name",
                                                self.trigger_info["codebuild_name"])

        self.ecr_repository_uri = self.trigger_info.get("ecr_repository_uri")
        self.ecr_repo_name = self.trigger_info.get("ecr_repo_name")

        self.docker_username = self.trigger_info.get("docker_username")
        self.docker_repository_uri = self.trigger_info.get("docker_repository_uri")
        self.docker_repo_name = self.trigger_info.get("docker_repo_name")

        self.s3_key = f"{self.build_name}/runs/{self.run_id}"

        try:
            self.build_timeout = int(self.trigger_info.get("build_timeout",444))
        except:
            self.build_timeout = 444

        # this is a new run
        if not self.run_id: 
            self.run_id = new_run_id()
            self.results["run_id"] = self.run_id
            self.results["_id"] = self.run_id
            self.s3_key = "{}/runs/{}".format(self.build_name,
                                              self.run_id)
            self._init_new_data()
            return {"status":True}

        self.logger.debug("provided run_id {}".format(self.run_id))

        # existing run
        self._load_run()

        if self.webhook_info:
            self.commit_hash = self.webhook_info["commit_hash"]

        _get_status = self.get_data()

        if _get_status:
            self.logger.debug("got existing run data from s3")
        else:
            self.logger.error("could not get data from s3")

        return {"status":True}

    def put_data(self):

        srcfile = os.path.join("/tmp",
                               id_generator())

        _data_hash = b64_encode(json.dumps(self.data))

        with open(srcfile, 'w') as _file:
            _file.write(_data_hash)

        self.file.insert(s3_bucket=self.s3_bucket_tmp,
                         s3_key=self.s3_key,
                         srcfile=srcfile)

        rm_rf(srcfile)

        return True
                
    def get_data(self):

        dstfile = os.path.join("/tmp",
                               id_generator())

        self.file.get(s3_bucket=self.s3_bucket_tmp,
                      s3_key=self.s3_key,
                      dstfile=dstfile)

        _datab64 = open(dstfile,"r").read()
        _decoded = b64_decode(_datab64)

        try:
            self.data = json.loads(_decoded)
        except:
            self.data = _decoded

        self.active = True

        rm_rf(dstfile)

        return True

    def _init_new_data(self):

        values = {
            "status": "running",
            "start_time": str(int(time())),
            "automation_phase": "continuous_delivery",
            "job_name": "docker_ci",
            "run_title": "docker_ci",
            "sched_name": "docker_ci",
            "sched_type": "build"
        }

        if self.trigger_info.get("project_id"): 
            values["project_id"] = self.trigger_info["project_id"]

        if self.trigger_info.get("schedule_id"): 
            values["schedule_id"] = self.trigger_info["schedule_id"]

        if self.trigger_info.get("sched_type"): 
            values["sched_type"] = self.trigger_info["sched_type"]

        if self.trigger_info.get("sched_name"): 
            values["sched_name"] = self.trigger_info["sched_name"]

        if self.trigger_info.get("run_title"): 
            values["run_title"] = self.trigger_info["run_title"]

        if self.trigger_info.get("job_name"): 
            values["job_name"] = self.trigger_info["job_name"]

        values["first_jobs"] = [ values["job_name"] ]
        values["final_jobs"] = [ values["job_name"] ]
        values["orders"] = []
        values["run_id"] = self.run_id

        self.data = values

        return values

    def _load_run(self):

        if self.run_info and self.webhook_info:
            return

        if not self.build_id:

            _match = {"_id":self.run_id}

            try:
                self.run_info = self.table_runs.get(_match)["Item"]
            except:
                self.run_info = None

        else:
            self.run_info = self.table_runs.search_key(key="build_id",
                                                       value=self.build_id)["Items"][0]

            if not self.run_id:
                self.run_id = self.run_info["_id"]

        if not self.run_info: 
            raise Exception("cannot find run_info")

        try:
            self.webhook_info = b64_decode(self.run_info["webhook_info_hash"])
        except:
            self.webhook_info = None

        return 

    def new_order(self,**kwargs):

        self.order = {
            "queue_id": get_queue_id(size=15),
            "start_time": str(self.start_time),
            "role": kwargs["role"],
            "human_description": kwargs["human_description"],
            "status": kwargs.get("status","in_progress")
        }

        return self.order

    def add_log(self,log=None):

        if log: 
            self.results["log"] = self.results["log"] + "\n" + log

        return self.results["log"]

    def finalize_order(self):

        self.stop_time = int(time())
        self.order["status"] = self.results["status"]
        self.order["stop_time"] = str(self.stop_time)
        self.order["checkin"] = self.stop_time
        self.order["total_time"] = self.stop_time - self.start_time 

        if self.order["total_time"] < 1: 
            self.order["total_time"] = 1

        self.order["total_time"] = int(self.order["total_time"])

        if self.results.get("status") in [ "timed_out" ]:
            _default_msg = "TIMED_OUT: {}".format(self.order["human_description"])
            self.order["status"] = "timed_out"
        elif self.results.get("status") in [ 'failed', False, "false", "timed_out" ]:
            _default_msg = "FAILED: {}".format(self.order["human_description"])
            self.order["status"] = "failed"
        else:
            _default_msg = "SUCCESS: {}".format(self.order["human_description"])
            self.order["status"] = "completed"

        self.add_log(log="")
        self.add_log(log=_default_msg)
        self.add_log(log="")

        self.logger.debug("#"*32)
        self.logger.debug(_default_msg)
        self.logger.debug("#"*32)

        self.order["log"] = self.results["log"]

        if self.data:
            self.data["orders"].append(self.order)

        return self.order

    def close_pipeline(self):

        self.data["status"] = self.results.get("status")
        self.data["stop_time"] = str(int(time()))
        self.data["total_time"] = int(self.data["stop_time"]) - int(self.data["start_time"])

        if not self.data.get("orders"): 
            return self.data

        self._update_orders_in_data()

        for order in self.data["orders"]:

            # one failure is failure of the pipeline
            if order.get("status") in [ "timed_out" ]:
                self.data["status"] = "timed_out"
                break

            if order.get("status") in ["failed","timed_out","unsuccessful"]:
                self.data["status"] = "failed"
                break

    def _update_orders_in_data(self):

        if not self.data.get("orders"): 
            return self.data

        wt = 1
        
        # place other fields orders
        for order in self.data["orders"]:

            if self.trigger_info.get("project_id"): 
                order["project_id"] = self.trigger_info["project_id"]

            if self.trigger_info.get("schedule_id"): 
                order["schedule_id"] = self.trigger_info["schedule_id"]

            if self.trigger_info.get("sched_type"): 
                order["sched_type"] = self.trigger_info["sched_type"]

            if self.trigger_info.get("sched_name"): 
                order["sched_name"] = self.trigger_info["sched_name"]

            if self.trigger_info.get("job_name"): 
                order["job_name"] = self.trigger_info["job_name"]

            if self.trigger_info.get("job_instance_id"): 
                order["job_instance_id"] = self.trigger_info["job_instance_id"]

            order["automation_phase"] = "continuous_delivery"
            order["wt"] = wt
            wt += 1

        return self.data

    def _repo_publish_vars(self):

        #publish_vars = self.webhook_info

        if not self.webhook_info:
            self.webhook_info = {}
     
        if self.webhook_info and "status" in self.webhook_info: 
            del self.webhook_info["status"]

        if self.docker_repository_uri:
            self.webhook_info["docker_repository_uri"] = self.docker_repository_uri

        return self.webhook_info

    def _eval_data(self):

        if not self.data.get("commit") and self.webhook_info:
            self.data["commit"] = self.webhook_info

        _publish_vars = self.data.get("publish_vars")

        if not _publish_vars: 
            _publish_vars = {}

        _repo_publish_vars = self._repo_publish_vars()
        
        _publish_vars = dict(_publish_vars,
                             **_repo_publish_vars)

        if self.results.get("publish_vars"):
            
            _publish_vars = dict(_publish_vars,
                                 **self.results["publish_vars"])

        self.data["publish_vars"] = _publish_vars

        return self._update_orders_in_data()

    def _get_inputargs_http(self):

        if not self.token:
            _ssm_info = self.ssm.get_parameter(Name=self.ssm_callback_key,
                                               WithDecryption=True)
            self.token = _ssm_info["Parameter"]["Value"]

        if self.phase: 
            name = "{}-{}".format(self.build_name,
                                  self.phase)
        else:
            name = self.build_name

        api_endpoint = "https://{}/{}".format(self.user_endpoint,
                                              "api/v1.0/run")

        inputargs = {
            "verify": False,
            "headers": {
                'content-type': 'application/json',
                "Token": self.token},
            "api_endpoint": api_endpoint,
            "name": name
        }

        if self.cdonly:
            self.data["automation_phase"] = "continuous_delivery"
            self.data["cdonly"] = "true"

        if os.environ.get("DEBUG_LAMBDA"):
            print("*"*32)
            print("")
            print_json(self.data)
            print("")
            print("*"*32)

        inputargs["data"] = json.dumps(self.data)

        return inputargs

    def update_saas(self):

        inputargs = self._get_inputargs_http()
        results = execute_http_post(**inputargs)

        print("%"*32)
        print("")
        print("Sent results to {}".format(inputargs["api_endpoint"]))

        if os.environ.get("DEBUG"):
            print("")
            print_json(results)

        print("")
        print("%"*32)

        self._get_config0_url(**results)

        return results

    def eval_results(self):

        try:
            self._eval_data()
        except:
            self.logger.error("could not eval data")

        # if not initialized, then we never got into build pipeline
        # e.g. webhook never triggered anything
        if not self.results.get("initialized") and self.phase == "load_webhook":
            self.results["continue"] = False
            if self.results.get("notify"):
                self.notify()
            return self.results

        # do not update if close is True
        if not self.results.get("close") and self.results.get("update"):
            try:
                self.put_data()
            except:
                self.logger.warn("could not put data")

        if self.results.get("notify"): 
            self.notify()

        # evaluate if close now and return results
        if self.results.get("close"):

            self.results["continue"] = False

            try:
                self.put_data()
            except:
                self.logger.warn("could not put data")

            try:
                self.close_pipeline()
            except:
                self.logger.warn("could not close pipeline")

            try:
                self.update_saas()
            except:
                self.logger.warn("could not update saas")

            if self.results.get("status") in ["failed","timed_out",False,"false"]:
                failed_message = self.results.get("traceback")

                if not failed_message:
                    failed_message = self.results.get("failed_message")

                if not failed_message:
                    failed_message = "codebuild ci failed"

                print_json(self.results)
                raise Exception(failed_message)

            return self.results

        return self.results

    def _get_notify_message(self):

        message = "status: {}".format(self.results.get("status"))

        _message = "git repo: {}".format(self.trigger_info.get("git_repo"))
        message = message + "\n" + _message

        if self.run_info:
            _message = "commit hash: {}".format(self.run_info.get("commit_hash"))
            message = message + "\n" + _message

            _message = "build_id: {}".format(self.run_info.get("build_id"))
            message = message + "\n" + _message

        if self.config0_url:
            _message = "url: {}".format(self.config0_url)
            message = message + "\n" + _message

        if self.results.get("traceback"):
            message = message + "\n" + "#"*32
            message = message + "\n" + "# Traceback         "
            message = message + "\n" + "#"*32
            message = message + "\n" + ""
            message = message + "\n" + self.results["traceback"]
            message = message + "\n" + ""
            message = message + "\n" + "#"*32

        return message

    def _get_config0_url(self,**kwargs):

        '''
        https://app.config0.com/williaumwu/debug-auto-04/598
        '''

        try:
            run_seq_id = kwargs["api"]["response"]["results"]["run_seq_id"]
            nickname = kwargs["api"]["response"]["results"]["nickname"]
            saas_env = kwargs["api"]["response"]["results"]["saas_env"]
        except:
            return 

        self.config0_url = "https://{}.config0.com/{}/{}/{}".format(saas_env,
                                                                 nickname,
                                                                 self.trigger_info["project"],
                                                                 run_seq_id)

        return self.config0_url

    def get_docker_token(self,**kwargs):

        self.docker_token = None

        if not self.trigger_info.get("ssm_docker_token"): 
            return

        try:
            _ssm_info = self.ssm.get_parameter(Name=self.trigger_info["ssm_docker_token"],
                                               WithDecryption=True)
            self.docker_token = _ssm_info["Parameter"]["Value"]
        except:
            self.logger.warn("could not fetch docker_token")

        return self.docker_token

    def _get_notify_inputargs(self,**kwargs):

        if not self.trigger_info.get("ssm_slack_webhook_b64"): 
            self.logger.warn("ssm_slack_webhook_b64 not found - notification not enabled")
            return

        try:
            _ssm_info = self.ssm.get_parameter(Name=self.trigger_info["ssm_slack_webhook_b64"],
                                               WithDecryption=True)
            self.slack_webhook_b64 = _ssm_info["Parameter"]["Value"]
        except:
            self.logger.warn("could not fetch slack webhook")
            return

        message = self._get_notify_message()

        inputargs = { "message":message }
        inputargs["slack_webhook_b64"] = self.slack_webhook_b64

        if self.results.get("status") in [ "failed", "timed_out", False, "false"]:
            inputargs["emoji"] = ":x:"
        elif self.results.get("status") in [ "successful", "success", True, "true"]:
            inputargs["emoji"] = ":white_check_mark:"
        else:
            inputargs["emoji"] = ":information_source:"

        if kwargs.get("title"):
            inputargs["title"] = kwargs["title"]
        else:
            inputargs["title"] = '{} - Summary'.format(inputargs["emoji"])

        if self.config0_url: inputargs["link"] = self.config0_url

        if self.trigger_info.get("slack_channel"): 
            inputargs["slack_channel"] = self.trigger_info["slack_channel"]
        
        return inputargs

    def _eval_set_fail(self):

        self.start_time = int(time())
        human_description = 'Setup failed phase "{}"'.format(self.phase)
        inputargs = {"human_description": human_description,"role": "run_helper/internal"}
        self.new_order(**inputargs)

        self.results["log"] = "#"*32
        self.add_log('# Failed setup for the lambda "{}" function'.format(self.phase))
        self.add_log("#"*32)
        self.add_log("")

    def _eval_exec_fail(self):

        self.start_time = int(time())
        human_description = 'Run failed phase "{}"'.format(self.phase)
        inputargs = {"human_description": human_description,"role": "run_helper/internal"}
        self.new_order(**inputargs)

        self.results["log"] = "#"*32
        self.add_log('# Failed execution for the lambda "{}" function'.format(self.phase))
        self.add_log("#"*32)
        self.add_log("")

    def _update_internal_failure(self,failed_message):

        self.add_log(failed_message)
        self.results["status"] = "failed"
        self.results["traceback"] = failed_message
        self.results["notify"] = True
        self.results["close"] = True

        self.finalize_order()
        self._save_run_info()

    def _print_run_results(self):

        if not os.environ.get("DEBUG_LAMBDA") and not self.results.get("step_func"):
            return

        results = self.results.copy()

        if results.get("log"):
            del results["log"]

        if results.get("publish_vars"):
            del results["publish_vars"]

        print("+"*32)
        print_json(results)
        print("+"*32)

    def _eval_step_func(self,e_status=None):

        if not self.results.get("step_func"):
            return

        self._print_run_results()

        # special keywords for check_codebuild
        if e_status == "check_codebuild/_continue":
            print("." * 32)
            print("." * 32)
            print("check_codebuild running in step function - should continue in loop")
            print("." * 32)
            print("." * 32)
            return self.results

        if e_status == "check_codebuild/_failed":
            raise Exception('codebuild failed - status: "{}", build_id: "{}"'.format(self.results.get("status"),
                                                                                      self.build_id))

        if e_status == "check_codebuild/_discontinue":
            results = {
                "continue": False,
                "build_id": self.build_id
            }
            return self.update_with_chks(results=results)

    def run(self,**kwargs):

        try:
            self.logger.debug("running setup")
            setup_info = self.setup()
        except Exception:
            failed_message = traceback.format_exc()
            self.logger.error(failed_message)
            self._eval_set_fail()
            self._update_internal_failure(failed_message)
            return self.eval_results()

        if setup_info.get("status") is False:
            self.logger.error(setup_info.get("failed_message"))
            self._eval_set_fail()
            self._update_internal_failure(setup_info.get("failed_message"))
            return self.eval_results()

        # execute method will be in the
        # class inheriting this class
        e_status = None
        try:
            e_status = self.execute(**kwargs)
        except Exception:
            _traceback = traceback.format_exc()
            self.logger.error(_traceback)
            self._eval_exec_fail()
            self._update_internal_failure(_traceback)
            return self.eval_results()

        step_func_info = self._eval_step_func(e_status=e_status)

        if step_func_info:
            return step_func_info

        self._print_run_results()

        return self.eval_results()
