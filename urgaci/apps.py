import os
from subprocess import call
import dotenv

class ApplicationDirDoesNotExistError(Exception):
    def __init__(self):
        self.msg = """This application has no working directory on this server yet. Was looking for: %s.""" % os.environ["GIT_WORK_TREE"]
    def __str__(self):
        return repr(self.msg)


class WebApplication(object):

    def __init__(self, appname, branch="master", staging=False):
        os.environ["GIT_DIR"] = os.path.join(os.environ.get("GITREPO_DIR", os.environ["HOME"]), appname + ".git")
        
        self.branch = branch
        
        if staging:
            self.name = appname + "_staging"
            self.branch = "develop"

        webappsdir = os.environ.get("WEBAPPS_DIR", os.path.join(os.environ["HOME"], "webapps"))
        git_work_tree = os.path.join(webappsdir, self.name)
        os.environ["GIT_WORK_TREE"] = git_work_tree
        self.configfile = os.path.join(os.environ["GIT_WORK_TREE"], ".env") 


    def __str__(self):
        return repr(self.name)
    

    def config(self):
        """Configure the application and write it to the configuration file."""

        f = open(self.configfile, "w")
        answer = raw_input("Use a virtual environment? [y/n] ")
        if answer == "y" or answer == "Y":
            f.write("VIRTUALENV=1")
        f.close()

    def initialize(self):
        """initilize the application so the webserver knows about it."""
        call(["mkdir", "-p", os.environ["GIT_WORK_TREE"]])

    
    def create(self):
        """ Create a new application on this server """
        self.initialize()
        self.config()
        dotenv.read_dotenv(self.configfile)
        
        if "VIRTUALENV" in os.environ:
            virtualenv_basedir = os.environ.get("WORKON_HOME", os.path.join(os.environ["HOME"], ".virtualenvs"))
            call(["virtualenv", os.path.join(virtualenv_basedir, self.name)])
        

    def checkout(self):
        if not os.path.isdir(os.environ["GIT_WORK_TREE"]):
            raise ApplicationDirDoesNotExistError()
        
        os.chdir(os.environ["GIT_WORK_TREE"])
        call(["git", "checkout", "-f", self.branch])
        call(["git", "reset", "--hard"])


    def install_requirements(self):
        pippath="pip"
        if "VIRTUALENV" in os.environ:
            virtualenv=os.path.join(os.environ.get("WORKON_HOME", os.path.join(os.environ["HOME"], ".virtualenvs")), self.name)
            pippath=os.path.join(virtualenv, pippath)
        os.chdir(os.environ["GIT_WORK_TREE"])
        call([pippath, "install", "--upgrade", "-r", "requirements.txt"])

    
    def deploy(self):
        """
        Deploy an application.
        """
        self.checkout()
        dotenv.read_dotenv(os.path.join(os.environ["GIT_WORK_TREE"], ".env"))
        self.install_requirements()