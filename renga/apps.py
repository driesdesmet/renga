import os
import subprocess
from .helpers import generate_key
import dotenv
import getpass
import socket

class ApplicationDirDoesNotExistError(Exception):
    def __init__(self):
        self.msg = """This application has no working directory on this server yet. Was looking for: %s.""" % os.environ["GIT_WORK_TREE"]
    def __str__(self):
        return repr(self.msg)


class WebApplication(object):

    def __init__(self, appname, branch="master"):
        # Use GITREPOS envvar to locate the bare repo for this application or fallback to users' home directory.
        os.environ["GIT_DIR"] = os.path.join(os.environ.get("GITREPOS", os.environ["HOME"]), appname + ".git")
        
        self.branch = branch
        self.wsgi_module = appname + ".wsgi"
        
        if self.branch == "master":
            self.name = appname
        else:
            self.name = appname + "_" + self.branch
        
        webappsdir = os.environ.get("WEBAPPS_DIR", os.path.join(os.environ["HOME"], "webapps"))
        git_work_tree = os.path.join(webappsdir, self.name)
        os.environ["GIT_WORK_TREE"] = git_work_tree
        self.configfile = os.path.join(os.environ["GIT_WORK_TREE"], ".env")
        self.read_config()


    def __str__(self):
        return repr(self.name)

    
    def read_config(self):
        if os.path.isfile(self.configfile):
            dotenv.read_dotenv(self.configfile)
            if "VIRTUALENV" in os.environ:
                os.environ["PATH"] = ":".join([os.path.join(os.environ["VIRTUALENV"], "bin"), os.environ["PATH"]])
            self.configured = True
        else:
            self.configured = False


    def config(self):
        """Configure the application and write it to the configuration file."""

        f = open(self.configfile, "w")
        
        
        f.write("MEDIA_URL='/media/'\n")
        f.write("MEDIA_ROOT='public/media'\n")
        f.write("STATIC_URL='/static/'\n")
        f.write("STATIC_ROOT='public/static'\n")
        f.write("GUNICORN_WORKERS=1\n")

        answer = raw_input("Use a virtual environment? [Y/n] ") or "y"
        if answer == "y" or answer == "Y":
            virtualenv = os.path.join(os.environ.get("WORKON_HOME", os.path.join(os.environ["HOME"], ".virtualenvs")), self.name)
            f.write("VIRTUALENV=%s\n" % virtualenv)
            subprocess.call(["virtualenv", virtualenv])

        answer = int(raw_input("LISTEN_ON_PORT: [12345] ") or 12345 )
        f.write("LISTEN_ON_PORT=%d\n" % answer)
        
        answer = raw_input("Database password: [%s] " % self.name) or self.name
        f.write("DATABASE_URL='postgres://%s:%s@localhost/%s'\n" % (self.name, answer, self.name))

        f.write("DJANGO_SECRET_KEY='%s'\n" % generate_key())
        f.close()
        self.read_config()

    
    def initialize(self):
        """
        initilize the application so the webserver knows about it.
        """
        if "webfaction" in socket.gethostname():
            pass
        else:
            subprocess.call(["mkdir", "-p", os.environ["GIT_WORK_TREE"]])

    
    def info(self):
        print "GIT_DIR: ", os.environ["GIT_DIR"]
        print "BRANCH: ", self.branch
        print "CONFIGFILE: ", self.configfile
        print "CONFIGURED: ", self.configured
    

    def _webserver_command(self):
        return ("gunicorn --chdir=%(chdir)s --log-file=%(logfile)s -b 127.0.0.1:%(port)s -D -w %(workers)s --pid %(pidfile)s %(wsgimodule)s:application" %
            {'chdir': os.environ["GIT_WORK_TREE"],
             'pidfile': os.path.join(os.environ["GIT_WORK_TREE"], "webserver.pid"),
             'wsgimodule': self.wsgi_module,
             'port': os.environ["LISTEN_ON_PORT"],
             'workers': os.environ["GUNICORN_WORKERS"],
             'logfile': os.path.join(os.environ["HOME"], "logs", "user", "gunicorn_%s.log" % self.name),
             }
            )


    def webserver_start(self):
        """
        Starts the webserver that is running the Django instance
        """
        command = self._webserver_command()
        print "Starting webserver with command: ", command
        subprocess.check_call(command, shell=True)


    def webserver_stop(self):
        command = "kill $(cat %s)" % os.path.join(os.environ["GIT_WORK_TREE"], "webserver.pid")
        print "Stopping webserver with command: ", command
        subprocess.check_call(command, shell=True)

    
    def webserver_restart(self):
        """
        Restarts the webserver that is running the Django instance
        """
        try:
            command = "kill -HUP $(cat %s)" % os.path.join(os.environ["GIT_WORK_TREE"], "webserver.pid")
            subprocess.check_call(command, shell=True)
            print "Stopped webserver with command: ", command
        except subprocess.CalledProcessError:
            self.webserver_start()


    def create(self):
        """ Create a new application on this server """
        self.initialize()
        self.config()
        

    def checkout(self):
        if not os.path.isdir(os.environ["GIT_WORK_TREE"]):
            raise ApplicationDirDoesNotExistError()
        
        os.chdir(os.environ["GIT_WORK_TREE"])
        subprocess.call(["git", "checkout", "-f", self.branch])
        subprocess.call(["git", "reset", "--hard"])
        # Delete all .pyc files to make sure nothing stays behind. They are not tracked by git, so a git reset doesn't get rid of them.
        subprocess.call('find . -name "*.pyc" -exec rm -f {} \;', shell=True)


    def install_requirements(self):
        # pip relies on GIT_WORK_TREE and GIT_DIR to function properly, so delete it from the current environment first.
        gwt = os.environ["GIT_WORK_TREE"]
        gitdir = os.environ["GIT_DIR"]
        del(os.environ["GIT_WORK_TREE"])
        del(os.environ["GIT_DIR"])

        subprocess.call("pip install --upgrade -r %s" % os.path.join(gwt, "requirements.txt"), shell=True)
        # Now restore the environment to what it was.
        os.environ["GIT_WORK_TREE"] = gwt
        os.environ["GIT_DIR"] = gitdir

    
    def deploy(self):
        """
        Deploy an application.
        """
        print self.configfile
        if self.configured:
            self.checkout()
            self.install_requirements()
            self.webserver_restart()

        else:
            print "Application does not yet exist. Please create it first with 'create <appname>'."
