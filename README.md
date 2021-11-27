<p align="center">
    <img alt="zaphod logo" src="https://github.com/ryanwarrick/zaphod/blob/master/docs/images/zaphod.jpg?raw=true" height="100">
</p>

![license](https://img.shields.io/github/license/ryanwarrick/zaphod)
![GitHub last commit](https://img.shields.io/github/last-commit/ryanwarrick/zaphod)
[![](https://tokei.rs/b1/github/ryanwarrick/zaphod)](https://github.com/ryanwarrick/zaphod)
[![](https://tokei.rs/b1/github/ryanwarrick/zaphod?category=files)](https://github.com/ryanwarrick/zaphod)
[![code with hearth by ryanwarrick](https://img.shields.io/badge/%3C%2F%3E%20with%20%E2%99%A5%20by-ryanwarrick-ff1414.svg?style=flat-square)](https://github.com/ryanwarrick)

# Summary
Zaphod is a website built using Flask, and several other open-source tools, as a self-education project and for use as a personal website.

**Want a demo?** Check out a live version of the website at [ryanwarrick.com](https://ryanwarrick.com).

Zaphod has two primary 'content' sections:
* Blog: a home for chronological, temporal posts
* Articles: a home for long(er)-form, or perennial, articles

When I began work on Zaphod, I was looking to build a very basic blog website as an exercise to learn more about Flask. As the project progressed, I was excited to learn about and incorporate additional tools with which I was previously unfamiliar including Nginx, Bootstrap, SQLite, Gunicorn, and more.

# Technology
## Web Stack
Zaphod is responsible for the front-end, back-end, and database elements of the web stack. Other elements of the web stack are also covered below.

* Front-End
  * Basics: HTML, CSS, & JS
  * Styles: [Bootstrap](https://getbootstrap.com/)
* Back-End
  * [Python](https://www.python.org/)
  * [Flask](https://flask.palletsprojects.com/) (Python library)
* Server
  * [Gunicorn](https://gunicorn.org/): Python WSGI HTTP Server for UNIX
  * [Nginx](https://www.nginx.com/): Reverse Proxy Server (proxies requests to Gunicorn)
* Database
  * [SQLite](https://www.sqlite.org/index.html)
* Infrastructure
  * Primary Deployment:
    * Provider: Google Cloud Platform
    * VM: Low-performance HW. Running Linux 4.19 (Debian 10 - Buster)
  * Alternate Deployment (For Testing):
    * Provider: Amazon AWS
    * VM: Low-performance HW. Running Linux 4.14 (Amazon Linux 2)
* Dev-Ops
  * zaphod_ansible (separate project):
    * A 'deployment helper' DevOps tool I built for Zaphod.
    * For more info, see the zaphod_ansible [write-up](http://ryanwarrick.com/career/projects/zaphod_ansible) on the website or check out the GitHub [repo](https://github.com/ryanwarrick/zaphod_ansible).
  * utils/utils.py:
    * A 'development/build helper' script I built for Zaphod. The cmd-line tool generates virtual environments for development/build purposes. Additionally, the tool also builds packages (wheels) for use by zaphod_ansible in deployments.

## OSI Layers
Of course, the OSI model's layers are abstract and don't fit perfectly to reality, but for illustrative purposes I find it to be a helpful way to think about systems and environments.

Note: For illustrative purposes, I am including a simplified OSI layer table below. OSI model layers are abstract and some elements of an environment or system operate in multiple layers when the model is applied to reality. Therefore, take the simplified table with a grain of salt.

| Layer | Technology                              | Cloud Hosting | Zaphod_Ansible | Zaphod |
| ----- | --------------------------------------- | ------------- | -------------- | ------ |
| 1-3   | Cloud Hosting*                          | x             | -              | -      |
| 4-6   | Linux (TCP, socket, TLS)                | -             | x              | -      |
| 7     | Python, Gunicorn, & Nginx - (HTTP, TLS) | -             | -              | x      |

\* Cloud Hosting:
* VM serving live version of this package/site ([ryanwarrick.com](https://ryanwarrick.com)):
  * Cloud Provider: Google Cloud Platform
  * Machine Type: e2-micro (low-end / free-tier)
  * Network Interface: Static External IP Address
  * Kernel: Linux 4.19
  * Distro: Debian 10 (Buster)
* Alternate VM serving test version of this package/site:
  * Cloud Provider: AWS
  * Machine Type: t2.micro (low-end / free-tier)
  * Network Interface: Static External IP Address
  * Kernel: Linux 5.4
  * Distro: Ubuntu 20.04 (Focal)

# Installation
To keep it simple, the bulk of this README will focus on **manual** steps to get Zaphod up and running.

### Automation Note:
Interested in an automated approach to package building and deployment tasks? I built some helpers to assist with that:
- utils/utils.py: A 'development/build helper' script in this repo
- zaphod_ansible: A 'deployment helper' DevOps tool found in a separate repo

For more details on DevOps/automation for this project, see the [DevOps](#DevOps) section of this document.

## Python Environment
It's strongly suggested that you build and/or install this project within a Python Virtual Environment.

I would suggest the following:
* Create a virtual environment on your local dev machine. See [Flask's docs on virtual environments](https://flask.palletsprojects.com/en/2.0.x/installation/#virtual-environments).
* Install the package's requirements to your local virtual environment, including 'dev' extras:
  * Console command: `<path to virtual environment's python executable> -m pip install -e .[dev]`

## Packaging from Source and Installing Resulting Package
(Note: If you're only looking to run this app locally in a test capacity, then you can skip this section of building/installing a package).

Once your virtual environment is created, activated, and properly equipped with dependencies, then you're ready to build and install the package:
1. Create a built package in the form of a Python distribution "wheel" from source by executing the following command in the virtual environment: `python setup.py bdist_wheel`.
2. Find the resulting built package .whl file at `{project_root}/dist/*.whl`. The file name follows the following format: `{project name}-{version}-{python tag}-{abi tag}-{platform tag}.whl`.
3. Copy the wheel distribution file to the machine targeted for deployment.
4. Within an activated virtual environment on your deployment machine, install the package using the following command: `pip install {wheel_filename}`.

# App Configuration
The project includes a "config.py" configuration file with placeholder content. To properly configure the project for deployment, one must create an instance-specific configuration file. This step ensures that proper security can be enforced for the website (sessions, cookies, etc.).

To create an instance-specific configuration file:
- Make a copy of `{project_root}\zaphod\config.py`.
- Name the copy `config.py` and save the file within the instance folder.
  - See [Flask's docs on instance folders](https://flask.palletsprojects.com/en/2.0.x/config/#instance-folders) for more info.
  - If you can't find your folder, then you may need to launch your application once so that the folder is auto-magically created in the correct location.
- Within the `<instance folder path>\config.py` file, overwrite the placeholder "SECRET_KEY" value of 'dev' with a properly generated, unique key:
    - Generate a SECRET_KEY value via the following console command: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
    - Save the resulting output as the value of 'SECRET_KEY' in the `config.py` file.

# App Content Data
Zaphod is designed so one can easily write content (.md or .html files) for the website, and then simply place them within the instance directory for consumption and presentation by the app.

During the initial launch of the app within your deployment/production virtual environment, the app will automatically create an instance directory.
 - See [Flask's docs on instance folders](https://flask.palletsprojects.com/en/2.0.x/config/#instance-folders) for info.
  
Once created, you can now load the directory with content for Zaphod to use and display. Zaphod expects the following structure (note articles & blog dirs):
```
INSTANCE_DIR_PATH:
|   config.py
|   zaphod.sqlite
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

Note: Blog/article content is only read from files into a database once upon execution of the `flask init-db` command. After database initialization, the website only reads content data from the database. Therefore, one has to re-initialize the database and re-launch the website if they want to see modifications of content files to be reflected on the website.

# Launch Web Application
Note: Perform these tasks from within the virtual environment (local or remote, as needed) created in a previous step.

1. Set 'FLASK_APP' environment variable.

    Context: 'zaphod' is the name of the package (dir) that contains the site within the greater project (project root)):

    - Bash: `export FLASK_APP=zaphod`
    - CMD: `set FLASK_APP=zaphod`
    - PowerShell: `$env:FLASK_APP = "zaphod"`

2. Initialize database:
    - All platforms: `flask init-db`

3. Launch web app (options listed from least desirable to 'best practice')...
    - From source (for development/testing - using Flask's built-in server not suitable for production): `flask run --host=127.0.0.1 --port=8000`
    - From package without a proxy server (for testing):
      - Note: There are many available deployment options found on the [Deployment Options](https://flask.palletsprojects.com/en/2.0.x/deploying/) Flask docs page.
      - Note on my choice of deployment option: Currently, I chose to deploy to production using gunicorn (a Python WSGI HTTP Server for UNIX).
          - Gunicorn Server Launch Command: `gunicorn -b 0.0.0.0:8000 "zaphod:create_app()"`
    - **PREFERRED (PRODUCTION) OPTION**: From package with Gunicorn HTTP server and Nginx proxy server:
      - Per Flask documentation and forum/community guidance, I chose to host the app in production using Gunicorn (Python WSGI HTTP Server) behind an Nginx reverse proxy server.
      - To host the Flask app behind Gunicorn and Nginx, see this well-made, helpful tutorial article published by DigitalOcean regarding ['How to Serve Flask Applications with Gunicorn and Nginx...'](https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-20-04) (or [archive.org link](https://web.archive.org/web/20210221003604/https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-gunicorn-and-nginx-on-ubuntu-20-04))
        - Note that the tutorial is for Ubuntu systems; however, I found the procedures to work just fine with Debian 10 too.

# DevOps
After spending time testing this project, I quickly saw the need for automation of various repetitive tasks related to virtual environment management, packaging, and deployment. Therefore, I created two DevOps tools to help with these tasks.

* utils/utils.py:
  * 'Development/build helper' cmd-line utility
  * Responsible for automation of:
    * testing/development virtual environment management
    * building project packages from source
* Zaphod_ansible:
  * 'Deployment helper' DevOps tool
  * Responsible for automation of (on/to production server):
    * configuration (networking, project dirs, etc.)
    * installing and configuring required apps/services
    * uploading site instance files
    * configuring TLS certificates
  * For more info, see the [zaphod_ansible](https://github.com/ryanwarrick/zaphod_ansible) GitHub repo.

# Files Not in Change Management (Manual Backups Required)
Some files within projects are not controlled by change management as specified by the .gitignore config because they contain sensitive data, therefore it's not appropriate to sync them to a change management repository.

Sensitive files:
* <project_root>/instance/* (instance-specific content, config, and db files - entire dir)

To avoid data loss of these files that aren't Git tracked, make sure to backup these files to a different location, as appropriate.

# TODO - Possible Future Improvements:
Below are some, but not all, possible future improvements to be developed for the project.
- [ ] Add skeleton/filler data in examples dir under project root so that other users can work from examples when creating custom instance data including: blog post files, article files, project_repos file, resume, etc.
- [ ] Improve styling of the website (colors, spacing, etc.)
- [ ] Explore configurations/options available within Flask to improve security posture and remediate vulnerabilities
- [ ] Write and integrate tests (pytest or others) to the development process.
