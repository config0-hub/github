#!/usr/bin/env python
#

import os
import logging
#import auxiliary_module

class Config0Logger(object):

    def __init__(self,name,**kwargs):

        self.classname = 'Config0Logger'

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)

        # create file handler which logs even debug messages
        logdir = "/tmp/config0/log"
        os.system("mkdir -p {}".format(logdir))
        logfile = "{}/{}".format(logdir,"config0_main.log")

        fh = logging.FileHandler(logfile)
        fh.setLevel(logging.DEBUG)

        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

        self.direct = logger
        self.aggregate_msg = None

    def aggmsg(self,message,new=False,prt=None,cmethod="debug"):

        if not self.aggregate_msg: new = True

        if not new: 
            self.aggregate_msg = "{}\n{}".format(self.aggregate_msg,message)
        else:
            self.aggregate_msg = "\n{}".format(message)

        if not prt: return self.aggregate_msg

        msg = self.aggregate_msg
        self.print_aggmsg(cmethod)

        return msg

    def print_aggmsg(self,cmethod="debug"):

        _method = 'self.{}({})'.format(cmethod,"self.aggregate_msg")
        eval(_method)
        self.aggregate_msg = ""

    def debug_highlight(self,message):
        self.direct.debug("+"*32)
        self.direct.debug(message)
        self.direct.debug("+"*32)

    def info(self,message):
        self.direct.info(message)

    def debug(self,message):
        self.direct.debug(message)

    def critical(self,message):
        self.direct.critical("!"*32)
        self.direct.critical(message)
        self.direct.critical("!"*32)

    def error(self,message):
        self.direct.error("*"*32)
        self.direct.error(message)
        self.direct.error("*"*32)

    def warn(self,message):
        self.direct.warn("-"*32)
        self.direct.warn(message)
        self.direct.warn("-"*32)
