
import sys
import os



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
