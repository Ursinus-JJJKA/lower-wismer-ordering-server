import subprocess
import shutil

subprocess.run(["docker", "compose", "stop"])
subprocess.run(["docker", "compose", "down", "--volumes"])
shutil.rmtree("dbdata",ignore_errors=True)
subprocess.run(["docker", "rmi", "lower-wismer-ordering-server-webserver"])