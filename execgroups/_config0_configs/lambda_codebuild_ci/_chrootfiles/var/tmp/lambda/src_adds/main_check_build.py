#!/usr/bin/env python

import boto3
import gzip
from io import BytesIO
from time import sleep
from time import time

from config0_common.common import rm_rf
from config0_common.loggerly import Config0Logger
from config0_common.run_helper import Config0Reporter

class CheckBuild(Config0Reporter):

    def __init__(self,**kwargs):

        self.classname = "CheckBuild"

        self.logger = Config0Logger(self.classname)

        Config0Reporter.__init__(self,**kwargs)

        self.phase = "check_build"
        
        session = boto3.Session()
        self.codebuild_client = session.client('codebuild')
        self.s3 = boto3.resource('s3')

        self.build_id = kwargs.get("build_id")
        self.build_status = kwargs.get("build_status")

        self.chk_t0 = kwargs.get("chk_t0")
        self.chk_count = kwargs.get("chk_count")

        if not self.chk_count:
            self.chk_count = 0

        self.chk_count +=1

        if self.step_func:
            print("+"*32)
            print("checking codebuild count {}".format(self.chk_count))
            print("+"*32)

        if not self.chk_t0:
            self.chk_t0 = int(time())

        self.cdonly = True
        self.build_id_suffix = None
        self.codebuild_log = None

        self.run_t0 = int(time())
        self.run_maxtime = 800  # lambda maximum is 900
        self.total_maxtime = 1800

    def _set_order(self):

        human_description = 'Check build_id: "{}"'.format(self.build_id)

        inputargs = {
            "human_description": human_description,
            "role": "codebuild/build"
        }

        self.new_order(**inputargs)

    def _set_build_status(self):

        if self.results.get("status"):
            return True

        buildStatus = self.codebuild_client.batch_get_builds(ids=[self.build_id])['builds'][0]['buildStatus']
        print("codebuild status {}".format(buildStatus))

        self.results["build_status"] = buildStatus

        if buildStatus == 'SUCCEEDED': 
            self.results["status"] = "successful"
            return True

        if buildStatus == 'FAILED': 
            self.results["status"] = "failed"
            return True

        if buildStatus == 'FAULT': 
            self.results["status"] = "failed"
            return True

        if buildStatus == 'STOPPED': 
            self.results["status"] = "failed"
            return True
        
        if buildStatus == 'TIMED_OUT': 
            self.results["status"] = "timed_out"
            return True

        return

    def _chk_build(self):

        # see if build is done first
        build_done = self._set_build_status()

        while True:

            if build_done: 
                break

            _t1 = int(time())

            _time_elapsed = _t1 - self.run_t0
            _total_time_elapsed = _t1 - self.chk_t0

            if _total_time_elapsed > self.total_maxtime:
                self.logger.error("total max time exceeded {}".format(self.total_maxtime))
                self.results["status"] = "timed_out"
                break

            # check if lambda function is about to expire
            if _time_elapsed > self.run_maxtime:
                self.logger.warn("lambda run max time exceeded {}".format(self.run_maxtime))
                break

            # check build exceeded total build time alloted
            if _t1 > self.build_expire:
                self.results["status"] = "timed_out"
                self.logger.error("build timed out: after {} seconds.".format(str(self.build_timeout)))
                break

            sleep(5)

            build_done = self._set_build_status()

        if self.results.get("status"):
            self._loop_set_log()

        return

    def _loop_set_log(self):

        maxtime = 30
        t0 = int(time())

        _logname = f"codebuild/logs/{self.build_id_suffix}.gz"
        self.logger.debug(f"retrieving log: s3://{self.s3_bucket_tmp}/{_logname}")

        while True:

            _time_elapsed = int(time()) - t0

            if _time_elapsed > maxtime:
                self.logger.debug(f"time expired to retrieved log {str(_time_elapsed)} seconds")
                return False

            self._set_log(_logname)

            if self.codebuild_log: 
                break

            sleep(2)

    def _set_log(self,_logname):

        if self.codebuild_log: 
            return True

        _dstfile = '/tmp/{}.gz'.format(self.build_id_suffix)

        try:
            self.s3.Bucket(self.s3_bucket_tmp).download_file(_logname,_dstfile)
            rm_rf(_dstfile)
            obj = self.s3.Object(self.s3_bucket_tmp,_logname)
            _read = obj.get()['Body'].read()
        except:
            return

        gzipfile = BytesIO(_read)
        gzipfile = gzip.GzipFile(fileobj=gzipfile)
        log = gzipfile.read().decode('utf-8')

        self.codebuild_log = log

        return log

    def _save_run_info(self):

        self.run_info["build_status"] = self.results["status"]
        self.table_runs.insert(self.run_info)

        msg = "trigger_id: {} saved".format(self.trigger_id)
        self.add_log(msg)

    def _get_build_summary(self):

        if self.results["status"] == "successful":
            summary_msg = "# Successful \n# trigger_id {} \n# build_id {}".format(self.trigger_id,self.build_id)
        elif self.results["status"] == "timed_out":
            summary_msg = "# Timed out \n# trigger_id {} \n# build_id {}".format(self.trigger_id,self.build_id)
        elif self.build_id is False:
            self.results["status"] = "failed"
            summary_msg = "# Never Triggered \n# trigger_id {}".format(self.trigger_id)
        elif self.build_id:
            self.results["status"] = "failed"
            summary_msg = "# Failed \n# trigger_id {} \n# build_id {}".format(self.trigger_id,self.build_id)
        else:
            self.results["status"] = "failed"
            summary_msg = "# Never Triggered \n# trigger_id {}".format(self.trigger_id)

        return summary_msg

    def update_with_chks(self,results=None):

        if not results:
            results = self.results

        if not results.get("chk_t0"):
            results["chk_t0"] = self.chk_t0

        results["chk_count"] = self.chk_count

        return results

    def execute(self):

        self.build_id = self.run_info["build_id"]
        self.build_expire = int(self.run_info["build_expire"])
        self.build_id_suffix = self.build_id.split(":")[1]

        self._chk_build()
        self.update_with_chks()

        if self.results.get("step_func") and not self.results.get("status"):
            return "check_codebuild/_continue"

        if not self.codebuild_log:
            _log = 'failed to retrieved log \nbuild_id "{}"'.format(self.build_id)
        else:
            _log = self.codebuild_log

        if self.results.get("step_func"):
            print(_log)

            if self.results.get("status") != "successful":
                return "check_codebuild/_failed"

            return "check_codebuild/_discontinue"

        # status should be set at this point
        self.results["continue"] = False
        self.results["close"] = True
        self.results["update"] = True
        self.results["done"] = True

        if self.results.get("status") != "successful":
            self.results["notify"] = True

        # we only set order once we are completely done
        self._set_order()
        self.add_log(_log)

        # at this point, the build finishes
        # either failed, timed_out, or successful
        summary_msg = self._get_build_summary()

        self.add_log("#"*32)
        self.add_log("# Summary")
        self.add_log(summary_msg)
        self.add_log("#"*32)

        self.results["msg"] = summary_msg
        self.results["notify"] = True

        self.finalize_order()
        self._save_run_info()
        self.update_with_chks()

        return True
