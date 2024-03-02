import os.path
import subprocess

if not os.path.exists(".env") and os.path.exists(".env_sample"):
    print("Interactively creating the .env file")
    with open(".env_sample","r") as sample_file:
        data = sample_file.read()
    with open(".env","w") as file:
        for line in data.split():
            a,d = line.split('=')
            b = input(f"{a}= (default is {d})") or d
            file.write(f"{a}={b}\n")

# Run docker compose in daemon mode
subprocess.run(["docker", "compose", "up", "-d"])
