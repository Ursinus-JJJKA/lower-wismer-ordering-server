import shutil, subprocess

compose_ps_res = subprocess.run(["docker", "compose", "ps"],capture_output=True)
if "mongo_db" in compose_ps_res.stdout.decode():
    subprocess.run(["docker", "compose", "down", "--volumes"])
else:
    subprocess.run(["docker", "stop", "lwo-webserver-solo-container"])
    subprocess.run(["docker", "rm", "lwo-webserver-solo-container"])
shutil.rmtree("dbdata", ignore_errors=True)
subprocess.run(["docker", "rmi", "lower-wismer-ordering-server-webserver"])
