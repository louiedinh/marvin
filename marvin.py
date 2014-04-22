#!/usr/bin/python

import binascii
import ConfigParser
import imaplib
import re
import time
import subprocess
import os

subject_pattern = re.compile(r"Subject:(?P<subject>.*)\r\n")
first_word_pattern = re.compile(r"(?P<first>[a-zA-Z]+)\W+(?P<rest>.*)")

class OrgModeTask(object):
    """
    A task that knows how to insert itself into Org-Mode
    """
    CATEGORY_TEMPLATE_MAP= {"inbox": "i", "listening": "l", "todo": "t"}

    def __init__(self, data):
        # Try to figure out the category and task.
        match = first_word_pattern.search(data.strip())
        if not match or match.group("first").lower() not in OrgModeTask.CATEGORY_TEMPLATE_MAP:
            self.category = "inbox"
            self.task_description = data
        else:
            self.category = match.group("first").lower()
            self.task_description = match.group("rest")

        print "Task: %s - %s" % (self.category, self.task_description)

    def dispatch(self):
        """ 
        Insert into org mode
        Executes: emacsclient org-protocol:/capture:/d/IgnoredURL/IgnoredTitle/Task
        """
        command = "emacsclient"
        argument = "org-protocol:/capture:/%s/Ignored/Ignored/%s" % (OrgModeTask.CATEGORY_TEMPLATE_MAP[self.category], 
                                                                     self.task_description)
        subprocess.call([command, argument])
        print "%s %s"%(command, argument)

class Daemon(object):
    def __init__(self, config_filename, secret_filename):
        self.connection = None
        # Read in configurations
        config = ConfigParser.ConfigParser()
        config.read(config_filename)
        self.hostname = config.get('server', 'hostname')
        self.username = config.get('account', 'username')
        self.mailbox = config.get('settings', 'mailbox')

        secret = ConfigParser.ConfigParser()
        secret.read(secret_filename)
        self.password = binascii.unhexlify(secret.get('account', 'password'))

        self.tasks = []

    def open_connection(self, verbose=False):
        if verbose: print "Connecting to: %s" % self.hostname
        self.connection = imaplib.IMAP4_SSL(self.hostname)
        if verbose: print "Logging in as: %s" % self.username
        self.connection.login(self.username, self.password)
        self.connection.select(self.mailbox)

    def fetch_tasks(self, finalized=False):
        """
        Query the email box for new (unread) tasks
        Return them as Task objects
        """
        typ, data= self.connection.search(None, "UNSEEN")
        msg_ids = data[0].split()
        if not msg_ids:
            print "No unread messages. Done."
            return
        # Fetch the subject lines
        message_parts =  "(BODY[HEADER.FIELDS (SUBJECT)])" if finalized else "(BODY.PEEK[HEADER.FIELDS (SUBJECT)])"
        typ, data = self.connection.fetch(",".join(msg_ids), message_parts)
        # Parse
        for response_part in [d for d in data if isinstance(d,tuple)]:
            match_obj = subject_pattern.search(response_part[1])
            if not match_obj: continue
            subject = match_obj.group("subject")
            self.tasks.append(OrgModeTask(data=subject))

    def dispatch_tasks(self):
        for task in self.tasks:
            task.dispatch()
        # Clear tasks once they've been dispatched
        self.tasks = []

    def start(self, finalized=False):
        self.open_connection(verbose=True)
        print "Starting fetch..."
        self.fetch_tasks(finalized=finalized)
        self.dispatch_tasks()
        self.connection.logout()

if __name__ == '__main__':
    daemon = Daemon(config_filename="marvin.config", secret_filename="marvin.secret")
    daemon.start(finalized=True)
