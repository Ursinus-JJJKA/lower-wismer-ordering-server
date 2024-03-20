This will be some webserver that hosts the system that the app will post orders to and the queues will read from

## Virtual environment
Using a virtual environment is not required, but it slightly helps with IDE hints

- If you wish to use a virtual environment for development, run the following command `python -m venv python-venv`.
- Then activate the virtual environment. On Windows, the command is `python-venv\Scripts\activate`. If you get an error when using Powershell about "running scripts is disabled", run `cmd` first then retry the previous command.
- Then, install the dependencies with `pip install -r requirements.txt`.
- Now select the virtual environment as the interpreter for your IDE. For VSCode, you can select the python interpreter in the bottom right corner when on a python file.

Note that there is a funny issue where the VSCode extension for Python virtual environments seems to cache the .env file and load those into the environment for any terminals. As a result, docker-compose will read those values first even if they are stale. To fix this, close and relaunch VSCode and have it relaunch the terminal; that's what fixed it for me finally. Restarting the extension might work but I'm not entirely sure. This might help: https://code.visualstudio.com/docs/python/environments.

## Starting the server

Make sure python and docker are installed. Run the command `python run.py`. If there is no .env file, it will create one. You can also force recreation by passing the `--new` flag. To connect to an Altas cloud backend, use the `--atlas` flag. Then, the script will run the docker compose file. To pause the server without deleting the database, run `docker compose stop`. To stop and delete the database run `python reset.py` (this will also delete the docker image for the webserver).

Note: Docker does not seem to like running the starting command over an SSH connection. From what I can tell, it has some credential problem when attempting to pull the python image in the build stage for the webserver image. Just don't do it I guess.

## General developer notes

To test the endpoints of the server, you should use the Swagger API. It is autogenerated by the fastapi framework and is very useful. Goto localhost:8000/docs to see it. In theory, you could use curl to test it, but that would suck so don't.

If weird things are happening after changing the .env file, try restarting your IDE. See the note in the Virtual environment section

File purposes
- main.py tells the database client to start and aggregates the endpoints from the routers
- The routers folder holds files that contain the HTTP endpoints for such items
- The __init__ files are mainly to make python happy
- The crud.py file should contain the functions that modify the database. These functions should be called from the routers
- The database.py file just tries to get the driver to mongo ready
- dependencies.py is unused at the time of writing
- exceptions.py is used for creating exception type to make control flow easier (hopefully)
- schemas.py contain the structure of requests and reponses that the server deals with

Debugging notes
- If the server returns HTTP 500, the python code likely has a bug. See the logs from the docker container for info.
- If the server returns HTTP 422, the python function handling that endpoint rejected your input. Look at your request, the type annotations of the function, and the schema objects.

## Notes on modifying the database schema

Technically, MongoDB (and most NoSQL engines) are schema-less. However, we are using validators with mongo to essentially force a particular schema for consistency.
If you wish to modify the schema, make sure to modify the validators, the example documents (also located inside the init.js file), and the schemas in the schema.py file.

I wish we could write a script to generate the schema.py file from the validators, but this is likely impossible since some attributes should not be included in certain schemas (like how orders are not allowed to change the dateOrdered field in update requests, or hypothetically a hashed password field for users should NEVER be sent to the frontend) and it would be hard to make a script to do it correctly.
