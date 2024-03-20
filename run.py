import argparse
import os.path
import secrets
import subprocess
from urllib.parse import quote_plus

WEBSERVER_DEFAULTS = {"DATABASE_URL":"mongodb+srv://<username>:<password>@<atlas_url>.mongodb.net/db_name",
                      "WEBSERVER_PORT":"8000",
            "JWT_SECRET_KEY":secrets.token_hex(32),
            "JWT_ALGORITHM":"HS256",
            "JWT_LIFETIME_MINUTES":15}
MONGO_DEFAULTS = {"MONGODB_USERNAME":"REPLACEME",
            "MONGODB_PASSWORD":secrets.token_urlsafe(16),
            "MONGODB_PORT":"27017",
            "MONGODB_DB":"food_db"}

parser = argparse.ArgumentParser(description="Handle .env config and run the webserver")
parser.add_argument('--atlas', action="store_true")
parser.add_argument('--new', '--clear-env', action="store_true")
#TODO add someday cmd data passing
#parser.add_argument('-y', '--no-interact', action="store_true")


if __name__ == "__main__":
    args = parser.parse_args()

    if args.atlas:
        if args.new or not os.path.exists(".env"):
            # Generate data
            for field,default in WEBSERVER_DEFAULTS.items():
                res = (True and input(f"{field}={default}:").strip()) or default
                WEBSERVER_DEFAULTS[field] = res
            # Make .env file
            with open(".env","w") as file:
                file.write('\n'.join(f'{a}={b}' for a,b in WEBSERVER_DEFAULTS.items()))

        # Run docker compose in daemon mode
        subprocess.run(["docker", "build", "-t", "lower-wismer-ordering-server-webserver", "."])
        subprocess.run(["docker", "run", "-d", "--name", "lwo-webserver-solo-container", "-p", f"{WEBSERVER_DEFAULTS['WEBSERVER_PORT']}:8000", "lower-wismer-ordering-server-webserver"])
    else:
        if args.new or not os.path.exists(".env"):
            # Generate MONGO vars
            for field,default in MONGO_DEFAULTS.items():
                res = (True and input(f"{field}={default}:").strip()) or default
                MONGO_DEFAULTS[field] = res
            auth = f"{quote_plus(MONGO_DEFAULTS['MONGODB_USERNAME'])}:{quote_plus(MONGO_DEFAULTS['MONGODB_PASSWORD'])}@" if ('MONGODB_USERNAME' in MONGO_DEFAULTS and 'MONGODB_PASSWORD' in MONGO_DEFAULTS) else ""
            WEBSERVER_DEFAULTS["DATABASE_URL"] = f"mongodb://{auth}lwo_db:{MONGO_DEFAULTS['MONGODB_PORT']}/{MONGO_DEFAULTS['MONGODB_DB']}?authSource=admin"
            # Generate WEBSERVER vars
            for field,default in WEBSERVER_DEFAULTS.items():
                res = (True and input(f"{field}={default}:").strip()) or default
                WEBSERVER_DEFAULTS[field] = res

            # Make .env file
            with open(".env","w") as file:
                file.write('\n'.join(f'{a}={b}' for a,b in MONGO_DEFAULTS.items()))
                file.write('\n\n')
                file.write('\n'.join(f'{a}={b}' for a,b in WEBSERVER_DEFAULTS.items()))
        
        # Run docker compose in daemon mode
        subprocess.run(["docker", "compose", "up", "-d"])
