#!/usr/bin/env python

from time import time
from time import sleep
import os
import json
import string
import random
import requests
import base64
import jinja2
import hashlib
import datetime

def rm_rf(location):

    '''uses the shell to forcefully and recursively remove a file/entire directory.'''

    if not location: return False

    try:
        os.remove(location)
        status = True
    except:
        status = False

    if status is False and os.path.exists(location):
        try:
            os.system("rm -rf %s > /dev/null 2>&1" % (location))
            return True
        except:
            print(("problems with removing %s" % location))
            return False

class DateTimeJsonEncoder(json.JSONEncoder):

    def default(self,obj):

        if isinstance(obj,datetime.datetime):
            #newobject = str(obj.timetuple())
            newobject = '-'.join([ str(element) for element in list(obj.timetuple())][0:6])
            return newobject

        return json.JSONEncoder.default(self,obj)

def print_json(results):
    print((json.dumps(results,sort_keys=True,cls=DateTimeJsonEncoder,indent=4)))

def nice_json(results):

    try:
        _results = json.dumps(results,sort_keys=True,cls=DateTimeJsonEncoder,indent=4)
    except:
        _results = results

    return _results

def execute5(command,exit_error=True):

    _return = os.system(command)

    # Calculate the return value code
    exitcode = int(bin(_return).replace("0b", "").rjust(16, '0')[:8], 2)

    if exitcode != 0 and exit_error:
        failed_msg = 'The system command\n{}\nexited with return code {}'.format(command,exitcode)
        raise RuntimeError(failed_msg)

    results = {"status":True}
    if exitcode != 0: results = {"status":False}
    results["exitcode"] = exitcode

    return results

def b64_encode(obj):

    if isinstance(obj,dict):
        obj = json.dumps(obj)

    _bytes = obj.encode('ascii')
    base64_bytes = base64.b64encode(_bytes)

    # decode the b64 binary in a b64 string
    return base64_bytes.decode('ascii')

def b64_decode(token):

    base64_bytes = token.encode('ascii')
    _bytes = base64.b64decode(base64_bytes)

    try:
        _results = json.loads(_bytes.decode('ascii'))
    except:
        _results = _bytes.decode('ascii')

    return _results

def b64_decode_to_file(token,filepath=None,tojson=True):
  
    #token = token.split("444444")[1]
    base64_bytes = token.encode('ascii')
    _bytes = base64.b64decode(base64_bytes)
  
    try:
        values = json.loads(_bytes.decode('ascii'))
    except:
        values = _bytes.decode('ascii')
  
    if not filepath: return values

    with open(filepath,"w") as f:

        if tojson:
            f.write(json.dumps(values,indent=2))
        else:
            f.write(str(values))

        f.write("\n")

    return values

def templify(trim_blocks=True,**kwargs):

    templateVars = kwargs["template_vars"]
    src_fie = kwargs["src_fie"]
    dst_file = kwargs["dst_file"]

    print(("templateVars {}".format(templateVars)))

    templateLoader = jinja2.FileSystemLoader(searchpath="/")
    templateEnv = jinja2.Environment(loader=templateLoader)
    template = templateEnv.get_template(src_fie)
    outputText = template.render( templateVars )
    writefile = open(dst_file,"w")
    writefile.write(outputText)
    writefile.close()

def get_queue_id(size=6,input_string=None):

    date_epoch =str(int(time()))
    queue_id = "{}{}".format(date_epoch,id_generator(size))

    return queue_id

def id_generator(size=18,chars=string.ascii_lowercase):
    return ''.join(random.choice(chars) for x in range(size))

def new_run_id(**kwargs):

    checkin = str(int(time()))
    _id = "{}{}".format(id_generator()[0:6],checkin)

    return _id

def get_hash_from_string(_string):
    return hashlib.md5(_string.encode('utf-8')).hexdigest()

def eval_insert_failed(call_type,r,name,api_endpoint,data=None):

    desc = "making {} request {}".format(call_type,name)
    eval_results = eval_request_results(name=name,req=r,description=desc)
    if eval_results["success"]: return eval_results

    # Insert failed_message
    eval_results["failed_message"] = "{} failed at {}".format(desc,api_endpoint)

    if not data: return eval_results

    try:
        eval_results["failed_message"] = "{}\n{}".format(eval_results["failed_message"],
                                                         data)
    except:
        eval_results["failed_message"] = "{}\ndata payload contains binary ".format(eval_results["failed_message"])

    return eval_results

def eval_request_results(**kwargs):

    '''
    evalutes the request from api command
    and returns a standard summary and content
    of results
    '''

    req = kwargs["req"]
    name = kwargs.get("name")
    description = kwargs.get("description")

    success = True
    internal_error = None

    status_code = int(req.status_code)

    #status code between 400 and 500 are failures.
    if status_code > 399 and status_code < 600: 
        success = False

    if status_code > 500 and status_code < 600: 
        internal_error = True

    results = {"status_code":status_code}
    results["success"] = success
    results["api"] = {}
    if name: results["name"] = name
    if description: results["description"] = description
    if internal_error: results["internal_error"] = True

    try:
        _json = dict(req.json())
        results["api"]["response"] = _json
    except:
        try:
            results["api"]["response"] = req.json()
        except:
            results["api"]["response"] = None

    return results

def execute_http_post(**kwargs):

    name = kwargs["name"]
    headers = kwargs["headers"]
    api_endpoint = kwargs["api_endpoint"]
    data = kwargs.get("data")
    verify = kwargs.get("verify")

    timeout = int(kwargs.get("timeout",120))
    retries = int(kwargs.get("retries",1))
    sleep_int = int(kwargs.get("sleep_int",2))

    inputargs = {"headers":headers}
    inputargs["timeout"] = timeout

    if verify: 
        inputargs["verify"] = True
    else:
        inputargs["verify"] = False

    if data:
        if isinstance(data,dict): data = json.dumps(data)
        inputargs["data"] = data

    for retry in range(retries):

        print(("execute http post api_endpoint {} retry {}".format(api_endpoint,retry)))

        r = requests.post(api_endpoint,**inputargs)
        results = eval_insert_failed('POST',r,name,api_endpoint,data=data)
        if not results.get("internal_error"): break
        if results["success"]: break
        sleep(sleep_int)

    return results
