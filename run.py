import subprocess

# Run docker compose in daemon mode
subprocess.run(["docker", "compose", "up", "-d"])
