import subprocess

# Build the Dockerfile for the webserver
# subprocess.run(["docker", "build", "-t", "lwo_webserver", "."])

# Run docker compose in daemon mode
subprocess.run(["docker", "compose", "up", "-d"])
