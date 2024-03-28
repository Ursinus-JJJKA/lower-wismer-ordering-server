import shutil, subprocess

compose_ps_res = subprocess.run(["docker", "compose", "ps"],capture_output=True)
if "mongo_db" in compose_ps_res.stdout.decode():
    profile = "localdb"
else:
    profile = "atlasdb"
subprocess.run(["docker", "compose", "--profile", profile, "down", "--volumes"])
shutil.rmtree("dbdata", ignore_errors=True)
subprocess.run(["docker", "rmi", "lower-wismer-ordering-server-webserver"])
