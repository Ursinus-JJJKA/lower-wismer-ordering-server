import argparse
import os.path
import secrets
import socket
import subprocess
from urllib.parse import quote_plus

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # 10.254.254.254 should be connecting to nothing
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


WEBSERVER_DEFAULTS = {"DATABASE_URL":"mongodb+srv://<username>:<password>@<atlas_url>.mongodb.net/db_name",
                      "WEBSERVER_PORT":"8000",
            "JWT_SECRET_KEY":secrets.token_hex(32),
            "JWT_ALGORITHM":"HS256",
            "JWT_LIFETIME_MINUTES":30,
            "KITCHEN_JWT_LIFETIME_MINUTES":60*12}
MONGO_DEFAULTS = {"MONGODB_USERNAME":secrets.token_urlsafe(16),
            "MONGODB_PASSWORD":secrets.token_urlsafe(16),
            "MONGODB_PORT":"27017",
            "MONGODB_DB":"food_db"}

parser = argparse.ArgumentParser(description="Handle .env config and run the webserver")
parser.add_argument('--atlas', action="store_true")
parser.add_argument('--new', '--clear-env', action="store_true")
parser.add_argument('-y', '--defaults', action="store_false")


if __name__ == "__main__":
    args = parser.parse_args()

    if not os.path.exists("lwo.key") or not os.path.exists("lwo.crt"):
        generate_cmd = f'openssl req -x509 -newkey rsa:4096 -sha256 -days 365 -nodes -keyout lwo.key -out lwo.crt -addext "subjectAltName=IP:{get_ip()}"'
        subprocess.run(generate_cmd.split())

    if args.atlas:
        if args.new or not os.path.exists(".env"):
            # Generate data
            for field,default in WEBSERVER_DEFAULTS.items():
                res = (args.defaults and input(f"{field}={default}:").strip()) or default
                WEBSERVER_DEFAULTS[field] = res
            # Make .env file
            with open(".env","w") as file:
                file.write('\n'.join(f'{a}={b}' for a,b in WEBSERVER_DEFAULTS.items()))
        # Run docker compose in daemon mode
        subprocess.run(["docker", "compose", "--profile", "atlasdb", "up", "-d"])
    else:
        if args.new or not os.path.exists(".env"):
            # Generate MONGO vars
            for field,default in MONGO_DEFAULTS.items():
                res = (args.defaults and input(f"{field}={default}:").strip()) or default
                MONGO_DEFAULTS[field] = res
            auth = f"{quote_plus(MONGO_DEFAULTS['MONGODB_USERNAME'])}:{quote_plus(MONGO_DEFAULTS['MONGODB_PASSWORD'])}@" if ('MONGODB_USERNAME' in MONGO_DEFAULTS and 'MONGODB_PASSWORD' in MONGO_DEFAULTS) else ""
            WEBSERVER_DEFAULTS["DATABASE_URL"] = f"mongodb://{auth}lwo_db:{MONGO_DEFAULTS['MONGODB_PORT']}/{MONGO_DEFAULTS['MONGODB_DB']}?authSource=admin"
            # Generate WEBSERVER vars
            for field,default in WEBSERVER_DEFAULTS.items():
                res = (args.defaults and input(f"{field}={default}:").strip()) or default
                WEBSERVER_DEFAULTS[field] = res
            # Make .env file
            with open(".env","w") as file:
                file.write('\n'.join(f'{a}={b}' for a,b in MONGO_DEFAULTS.items()))
                file.write('\n\n')
                file.write('\n'.join(f'{a}={b}' for a,b in WEBSERVER_DEFAULTS.items()))
        # Run docker compose in daemon mode
        subprocess.run(["docker", "compose", "--profile", "localdb", "up", "-d"])
