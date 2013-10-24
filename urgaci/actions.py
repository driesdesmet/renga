
import sys
import os
from subprocess import call


def webserver_start():
    """
    Starts the webserver that is running the Django instance
    """


def webserver_restart():
    """
    Restarts the webserver that is running the Django instance
    """
    try:
        run("kill -HUP $(cat %s)" % env.gunicorn_pid_file)
    except:
        webserver_start()
        

def deploy(appname, branch):
    """
    Deploy an application.
    """

    if branch=="develop":
        appname = appname + "_staging" 
    webappsdir = os.environ.get("URGACI_APPS", os.path.join(os.environ["HOME"], "webapps"))
    os.environ['GIT_WORK_TREE'] = os.path.join(webappsdir, application)
    os.system("git checkout -f %s" % branch)