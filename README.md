<p align="center">
    <img alt="zaphod logo" src="https://github.com/ryanwarrick/zaphod/blob/master/docs/images/zaphod.jpg?raw=true" height="100">
</p>

![license](https://img.shields.io/github/license/ryanwarrick/zaphod)
![GitHub last commit](https://img.shields.io/github/last-commit/ryanwarrick/zaphod)
[![GitHub issues](https://img.shields.io/github/issues/ryanwarrick/zaphod)](https://github.com/ryanwarrick/zaphod/issues)
[![](https://tokei.rs/b1/github/ryanwarrick/zaphod)](https://github.com/ryanwarrick/zaphod)
[![](https://tokei.rs/b1/github/ryanwarrick/zaphod?category=files)](https://github.com/ryanwarrick/zaphod)
[![code with hearth by ryanwarrick](https://img.shields.io/badge/%3C%2F%3E%20with%20%E2%99%A5%20by-ryanwarrick-ff1414.svg?style=flat-square)](https://github.com/ryanwarrick)

# Summary
This Web app was built using Python Flask, and many other open source tools, for personal website functionality and self-education purposes. This repo also includes pipeline automation code, documentation, etc.

The web app (website) has two primary sections:
    * Blog: built to showcase chrono-ordered, temperal post content
    * Articles: built to showcase long-form, or just static in nature, article content.

### Vision
I originally planned to build a basic python project that could simply display markdown files as content within a basic Flask web app. As the project progressed, I took the opportunity to extend on core idea by incorporating more technologies so that I could gain experience with tools and concepts I was not previously acquainted with: Bootstrap, JS, SQL (generally &SQLite), Nginx, Gunicorn, and DevOps (scripting and theory).
See the [Technology](#Technology) section below.

# Technology
## Web Stack
This repo contains a python package called Zaphod. Zaphod is responsibile for the Front-End, Back-end, and Database elements of the web stack.

The remaining elements of the web stack are also crucial, therefore I will be documenting how they are configured and interfaced with so that this project is reproducible in its entirety - full stack.

* Front-End
  * Basics: HTML, CSS, & JS
  * Styles: Bootstrap
* Back-End
  * Python
  * Flask (Python library)
* Server
  * Gunicorn: Python WSGI HTTP Server for UNIX
  * Nginx: Reverse Proxy Server in front of Gunicorn
* Database
  * SQLite
* Infrastructure
  * Provider: Google Cloud Platform
  * VM: Low-performance HW. Running Linux 4.19 & Debian 10 (Buster)
* Dev-Ops
  * Automation: Custom python script (cmd-line utility) included in package generates virtual environments, builds packages, pushes and installs packages to a remote machine, and launches server.

## OSI Layers
| Layer | Technology        | In package code | In my environment |
| ----- | ----------------- | --------------- | ----------------- |
| 1 - 3 | Cloud-managed*    | -               | x                 |
| 4     | Unix              | -               | x                 |
| 5     | Unix (socket)     | -               | x                 |
| 6     | Nginx (TLS)       | -               | x                 |
| 7     | Flask Site (HTTP) | x               | -                 |

\* Cloud-managed: VM serving live version of this package/site ([ryanwarrick.com](https://ryanwarrick.com)) currently lives in Google Cloud Platform. It's a low-end (free-tier) VM variant running Ubuntu. Brief VM instance details below:
 - VM Machine Type: e2-micro
 - VM Network Interface: Static External IP Address
 - OS Kernel: Linux 4.19
 - OS Distro: Debian 10 (Buster)

# Installation
To keep it simple, this README will primarily focus on manual steps to get Zaphod up and running.

Note: I have built a custom utility script (included in this repo) that performs DevOps-like functions (locally build from source, build environments, push to PROD, and launch the app). More details coming soon to the [DevOps ](#DevOps-Utilities) section of this document.

## Python Environment
It's strongly suggested that you build and install this project as a built package within a Python Virtual Environment. See [Flask's docs on virtual environments](https://flask.palletsprojects.com/en/2.0.x/installation/#virtual-environments).

Personally, I would suggest:
* Create the package from source in a local venv (also helpful for local debugging).
  * Make sure to install the [wheel](https://pypi.org/project/wheel/) package in this venv
* Install the package (from a wheel) in a venv - most likely on a remote / prod server.


## Packaging from Source and Installing Resulting Package
1. Create a built package in the form of a Python distribution "wheel" from source by executing the following command:

    `
    python setup.py bdist_wheel
    `

2. Find the resulting built package .whl file at `{project_root}/dist/*.whl`. The file name follows the following format: `{project name}-{version}-{python tag}-{abi tag}-{platform tag}.whl`
3. Copy the wheel distribution file to the machine targeted for deployment.
4. Within an activated virtual environment on your remote / prod server(see ["Environment"](#Environment) above), install the package using the following command:

    `
    pip install {wheel_filename}
    `

# App Configuration
The project includes a "config.py" configuration file with placeholder content. To properly configure the project for deployment, one must create a instance specific configuration file. This step ensures that proper security can be enforced for the website (sessions, cookies, etc.).

To create an instance specific configuration file:
- Make a copy of `{project_root}\zaphod\config.py`.
- Name the copy `config.py` and save the file within the instance dir.
  - See [Flask's docs on instance folders](https://flask.palletsprojects.com/en/2.0.x/config/#instance-folders) for info.
  - If you can't find your instance dir, then you may need to launch your application once so it's auto-magically created in the correct location.
- Overwrite the placeholder "SECRET_KEY" value of 'dev' with a properly generated and unique key:
    - Generate a SECRET_KEY value via the following console command:

        `
        python -c "import secrets; print(secrets.token_urlsafe(32))"
        `
    - Save the resulting output as the value of 'SECRET_KEY' in `config.py`.

# App Content Data
Zaphod is designed so one can easily write content (.md or .html files) for the website, and then simply place them within the instance directory for consumption and presentation by the app.

After first launch of the app within your deployment / production virtual environment, the app will create an instance directory for you.
 - See [Flask's docs on instance folders](https://flask.palletsprojects.com/en/2.0.x/config/#instance-folders) for info.
  
Once created, you can now load the directory with content for Zaphod to use and display. Zaphod expects the following structure (note articles & blog dirs):
```
INSTANCE_DIR_PATH:
|___content
    |__articles
    |  |__<Topic1>
    |  |  |__<SubtopicA>
    |  |        <Article1.md>
    |  |__<Topic2>
    |  |     <Article2.html>
    |__blog
          <Post1.md>
          <Post2.html>
          <Post3.md>
``` 

# Launch Web Application
Note: Perform these tasks from within the venv (local or remote venv depending on situation) created in a previous step.

1. Set 'FLASK_APP' environment variable.

    Context: 'zaphod' is the name of the package (dir) that contains the site within the greater project (project root)):

    - Bash: `export FLASK_APP=zaphod`
    - CMD: `set FLASK_APP=zaphod`
    - PowerShell: `$env:FLASK_APP = "zaphod"`

2. Initialize database:
    - All platforms: `flask init-db`

3. Launch web app...
    - From Source (for DEV/TEST - using Flask's built-in server not suitable for PROD): `flask run`
    - From Package without proxy server (for rudimetary PROD):
        - Note on available deployment options: There are many available deployment options found at the Flask docs page on [Deployment Options](https://flask.palletsprojects.com/en/2.0.x/deploying/).
        - Note on my choice of deployment option: Currently, I chose to deploy to PROD using gunicorn (a Python WSGI HTTP Server for UNIX).
            - Gunicorn Server Launch Command: `gunicorn -b 0.0.0.0:8000 "zaphod:create_app()"`
    - PREFERRED: From Package with Nginx proxy server (for PROD):
      - Per Flask documentation and forum/community guidance, I've concluded running Gunicorn (Python WSGI HTTP Server) behind Nginx (Reverse proxy server) to host the app in production.
        - To host the Flask app behind Gunicorn and Nginx, see this incredibly helpful tutorial article published by DigitalOcean regarding ['How to Serve Flask Applications with Gunicorn and Nginx...'](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-20-04). Here's an [Archive.org link](https://web.archive.org/web/20210221003604/https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-20-04), if necessary.
        - Note that the article is written for Ubuntu systems, however I found the procedures to work just fine with my Debian 10 distro.

# Automation
Basic DevOps / development pipeline automation scripting has been built into the `utilities.py` module found within the `{project_root}/utils/` directory.

Additional documentation regarding the utilities offered by this script will be added at a later date.