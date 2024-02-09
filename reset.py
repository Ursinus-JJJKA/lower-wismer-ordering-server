import subprocess
import shutil

subprocess.run(["docker", "compose", "down"])
shutil.rmtree("mongodata",ignore_errors=True)
subprocess.run(["docker", "rmi", "lower-wismer-ordering-server-webserver"])