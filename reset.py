import subprocess
import shutil

subprocess.run(["docker", "compose", "down"])
shutil.rmtree("postgres",True)
subprocess.run(["docker", "rmi", "lower-wismer-ordering-server-webserver"])