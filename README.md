# NULPAP

Usage Guide

(All the actions sholbe be perfomed in python virtual environment)

1. Download poetry (follow the instructions provided by documentation https://python-poetry.org/docs/#installation)
2. Download the 'Project' folder to any directory on your computer (excluding Desktop)
3. Using your terminal (cmd or PowerShell for Windows) move inside 'Project' folder (.../Project>) and type 'poetry install' (this will install all the required dependecies)
4. Open the 'Project' folder as a python project (PyCharm is recommended)
5. Use IDE's Terminal, move to 'project' folder (cd .\project\ in PyCharm) and invoke waitress-serve --host (your localhost ip) --port=88 --call "__init__:create_app" command
6. Now follow http://localhost:88/api/v1/hello-world-11 and you should see "Hello world 11" text.
7. Terminate your terminal when done.
