"""Script Contains DevOps-like automation functionality to help support the development, deployment, and management of the Zaphod Flask web app.

Important Note: This script relies on values set within a config.ini. By default, that file is pulled from project_root/utils/config.ini. However, this has default values within it. Therefore, one must either:
- edit the default 'config.ini' file as appropriate.
- OR, create a separate copy of the .ini file, edit as appropriate, and then pass the file name in when invoking the script using the -C / --config argument.
    """

import argparse
import configparser
import os
import shutil
import subprocess
import sys
from pathlib import Path
from textwrap import dedent


def delete_dir_in_project_root(dir_name):
    project_root_dir = Path(__file__).resolve().parent.parent

    dir_path = os.path.join(project_root_dir, dir_name)
    if os.path.exists(dir_path) and os.path.isdir(dir_path):
        print("Deleted existing {} dir.".format(dir_name))
        shutil.rmtree(dir_path)


def get_venv_python_exe_file_path():
    project_root_dir = Path(__file__).resolve().parent.parent
    venv_python_exe_file_path = os.path.join(
        project_root_dir, "venv", "Scripts", "python.exe")
    return venv_python_exe_file_path


def print_section_header(func_name):
    print("#######{}#######".format(func_name))


def print_section_footer():
    print("##############")


def load_config_parser(config_file_name) -> configparser.ConfigParser:
    parent_dir = Path(__file__).resolve().parent

    config_file_path = os.path.join(parent_dir, config_file_name)

    # Create the configuration parser
    config_parser = configparser.ConfigParser()

    # Read the configuration file
    try:
        with open(config_file_path) as config_file:
            config_parser.read_file(config_file)
    except IOError:
        print("Error: Config file not found.")
        sys.exit(1)
    return config_parser


def execute_cleanpy():
    print_section_header(execute_cleanpy.__name__)
    console_msg = """\
    Executing cleanpy caller helper function:
     - Invoke cleanpy (cleans project dir of cache/temp files, builds, metadata)
    """
    print(dedent(console_msg))

    command = "cleanpy ..\. --include-builds --include-metadata"
    # subprocess_results = subprocess.run(
    #     command, capture_output=True, text=True, shell=True)
    subprocess_results = subprocess.run(
        command, capture_output=True)
    if subprocess_results.stdout:
        print("{} - stdout:\n{}".format(execute_cleanpy.__name__,
              subprocess_results.stdout))
    if subprocess_results.stderr:
        print("{} - stderr:\n{}".format(execute_cleanpy.__name__,
              subprocess_results.stderr))
    print("Cleaned the project.")
    print_section_footer()


def generate_virtual_environment():
    print_section_header(generate_virtual_environment.__name__)
    console_msg = """\
    Executing venv creation helper function:
     - Purge venv dir
     - Create new venv
     - (venv) upgrade pip
     - (venv) install project's package requirements (including 'dev' extras) per the setup.cfg
    """
    print(dedent(console_msg))

    delete_dir_in_project_root('venv')

    venv_python_exe_file_path = get_venv_python_exe_file_path()

    commands = """\
    python -m venv venv & \
    {venv_python_exe_file_path} -m pip install --upgrade pip & \
    {venv_python_exe_file_path} -m pip install -e .[dev] \
    """.format(venv_python_exe_file_path=venv_python_exe_file_path)
    subprocess_results = subprocess.run(
        commands, capture_output=True, text=True, shell=True)
    if subprocess_results.stdout:
        print("{} - stdout:\n{}".format(generate_virtual_environment.__name__,
              subprocess_results.stdout))
    if subprocess_results.stderr:
        print("{} - stderr:\n{}".format(generate_virtual_environment.__name__,
              subprocess_results.stderr))
    print("Created the virtual environment.")
    print_section_footer()


def build_package_wheel():
    print_section_header(build_package_wheel.__name__)
    console_msg = """\
    Executing build package wheel helper (sub)function:
     - Purge dist dir
     - Build new package wheel
    """
    print(dedent(console_msg))

    delete_dir_in_project_root('dist')

    venv_python_exe_file_path = get_venv_python_exe_file_path()
    commands = "{} setup.py bdist_wheel".format(venv_python_exe_file_path)

    print("!!!BEFORE BUILD WHEEL PROCESS!!!")
    process = subprocess.Popen(
        'powershell.exe', stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = process.communicate(dedent(commands).encode('utf-8'))
    print("!!!AFTER BUILD WHEEL PROCESS!!!")

    if out:
        print("{} - stdout:\n{}".format(build_package_wheel.__name__, out.decode('utf-8')))
    if err:
        print("{} - stderr:\n{}".format(build_package_wheel.__name__, err.decode('utf-8')))
    print_section_footer()


def push_app_to_production(config_file_name):
    print_section_header(push_app_to_production.__name__)

    console_msg = """\
    Executing push to production helper function:
     - Rename wheel file
     - SFTP transfer wheel file to production server
    """
    print(dedent(console_msg))

    config_parser = load_config_parser(config_file_name)

    local_dist_path = os.path.join(
        Path(__file__).resolve().parent.parent, "dist")

    wheel_file_name = os.listdir(local_dist_path)[0]
    original_path = os.path.join(local_dist_path, wheel_file_name)
    # local_wheel_file_path = os.path.join(local_dist_path, "zaphod.whl") # Issues with renaming wheel files
    # os.rename(original_path, local_wheel_file_path)

    # https://stackoverflow.com/a/65804602
    command = r'"{winscp_console_executable_path}" /ini=nul /command "open sftp://{prod_machine_username}@{prod_machine_ip}/ -hostkey=""{winscp_host_key}"" -privatekey=""{winscp_private_key_file_path}""" "put ""{local_wheel_file_path}"" ""{remote_wheel_file_path}""" exit'.format(
        winscp_console_executable_path=config_parser['WinSCP']['Console Executable Path'],
        prod_machine_username=config_parser['PROD Machine']['Username'],
        prod_machine_ip=config_parser['PROD Machine']['IP'],
        winscp_host_key=config_parser['WinSCP']['Host Key'],
        winscp_private_key_file_path=config_parser['WinSCP']['Private Key File Path'],
        local_wheel_file_path=original_path,
        remote_wheel_file_path=config_parser['PROD Machine']['Remote Wheel File Path']
    )

    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in iter(process.stdout.readline, b''):
        print(line.decode().rstrip())

    print_section_footer()

    # This method of constructing the subprocess.Popen() command is cleaner,
    # however I'm troubled by double quote escaping woes.
    # I'll leave this command construction method here for now, in case I
    # resolve the issue.
    # commands = [
    #     config_parser['WinSCP']['Console Executable Path'],
    #     '/ini=nul',  # No config file, just using arguments
    #     '/command',
    #     "'open sftp://" + \
    #     config_parser['PROD Machine']['Username'] + \
    #     '@' + \
    #     config_parser['PROD Machine']['IP'] + "/" + \
    #     ' -hostkey=""' + config_parser['WinSCP']['Host Key'] + '""' + \
    #     ' -privatekey=' + '""' + \
    #     config_parser['WinSCP']['Private Key File Path'] + '""' + "'",
    #     'exit'
    # ]


def deploy_on_production(config_file_name):
    print_section_header(deploy_on_production.__name__)
    console_msg = """\
    Executing deploy on production helper function:
     - Build SSH connection to production server
     - Send commands to production server via SSH:
        * Stop Nginx (proxy server) service
        * Stop zaphod (gunicorn server) service
        * Install wheel file on production server
        * Create instance directory in venv
        * Create venv/var dir, and venv/var/zaphod-instance dir.
    """
    print(dedent(console_msg))

    config_parser = load_config_parser(config_file_name)

    commands = """
    ssh {prod_machine_username}@{prod_machine_ip} -i ~/.ssh/andromeda_key '
    cd ~/zaphod;
    sudo systemctl stop nginx;
    sudo systemctl stop zaphod;
    rm -r ./venv;
    python3 -m venv venv;
    ./venv/bin/python3 -m pip install --upgrade pip;
    ./venv/bin/python3 -m pip install wheel;
    ./venv/bin/python3 -m pip install ~/zaphod/zaphod-0.0.1-py3-none-any.whl;
    cd ~/zaphod/venv;
    mkdir var;
    cd ~/zaphod/venv/var;
    mkdir zaphod-instance;
    '""".format(
        prod_machine_username=config_parser['PROD Machine']['Username'],
        prod_machine_ip=config_parser['PROD Machine']['IP']
    )
    # ./venv/bin/python3 -m gunicorn -b 0.0.0.0:8000 "zaphod:create_app()";
    commands = ''.join(commands.splitlines())
    process = subprocess.Popen("bash.exe", shell=False, universal_newlines=True,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    out, err = process.communicate(dedent(commands))
    if out:
        print("{} - stdout:\n{}".format(deploy_on_production.__name__, out))
    if err:
        print("{} - stderr:\n{}".format(deploy_on_production.__name__, err))
    print_section_footer()


def push_content_to_production(config_file_name):
    print_section_header(push_content_to_production.__name__)
    console_msg = """\
    Executing push content to production helper function:
     - Send commands to production server via SSH:
        * Pushes updated content from local instance dir to production server instance dir
    """
    print(dedent(console_msg))

    config_parser = load_config_parser(config_file_name)

    local_content_dir_path = os.path.join(
        Path(__file__).resolve().parent.parent, "instance", "content")

    # https://stackoverflow.com/a/65804602
    command = r'"{winscp_console_executable_path}" /ini=nul /command "open sftp://{prod_machine_username}@{prod_machine_ip}/ -hostkey=""{winscp_host_key}"" -privatekey=""{winscp_private_key_file_path}""" "put ""{local_content_dir_path}"" ""{remote_instance_dir_path}""" exit'.format(
        winscp_console_executable_path=config_parser['WinSCP']['Console Executable Path'],
        prod_machine_username=config_parser['PROD Machine']['Username'],
        prod_machine_ip=config_parser['PROD Machine']['IP'],
        winscp_host_key=config_parser['WinSCP']['Host Key'],
        winscp_private_key_file_path=config_parser['WinSCP']['Private Key File Path'],
        local_content_dir_path=local_content_dir_path,
        remote_instance_dir_path=config_parser['PROD Machine']['Remote Instance Dir Path']
    )

    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in iter(process.stdout.readline, b''):
        print(line.decode().rstrip())

    print_section_footer()


def push_config_to_production(config_file_name):
    print_section_header(push_config_to_production.__name__)
    console_msg = """\
    Executing push config to production helper function:
     - Send commands to production server via SSH:
        * Pushes updated config file from local instance dir to production server instance dir
    """
    print(dedent(console_msg))

    config_parser = load_config_parser(config_file_name)

    local_config_file_path = os.path.join(
        Path(__file__).resolve().parent.parent, "instance", "config.py")

    # https://stackoverflow.com/a/65804602
    command = r'"{winscp_console_executable_path}" /ini=nul /command "open sftp://{prod_machine_username}@{prod_machine_ip}/ -hostkey=""{winscp_host_key}"" -privatekey=""{winscp_private_key_file_path}""" "put ""{local_content_dir_path}"" ""{remote_config_file_path}""" exit'.format(
        winscp_console_executable_path=config_parser['WinSCP']['Console Executable Path'],
        prod_machine_username=config_parser['PROD Machine']['Username'],
        prod_machine_ip=config_parser['PROD Machine']['IP'],
        winscp_host_key=config_parser['WinSCP']['Host Key'],
        winscp_private_key_file_path=config_parser['WinSCP']['Private Key File Path'],
        local_content_dir_path=local_config_file_path,
        remote_config_file_path=config_parser['PROD Machine']['Remote Config File Path']
    )

    process = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    for line in iter(process.stdout.readline, b''):
        print(line.decode().rstrip())

    print_section_footer()


def launch_on_production(config_file_name):
    print_section_header(launch_on_production.__name__)
    console_msg = """\
    Executing deploy on production helper function:
     - Send commands to production server via SSH:
        * Initialize application database
        * Start Nginx (proxy server) service
        * Start zaphod (gunicorn server) service
    """
    print(dedent(console_msg))

    config_parser = load_config_parser(config_file_name)

    commands = """
    ssh {prod_machine_username}@{prod_machine_ip} -i ~/.ssh/andromeda_key '
    cd ~/zaphod;
    export FLASK_APP=zaphod;
    ./venv/bin/python3 -m flask init-db;
    sudo systemctl start nginx;
    sudo systemctl start zaphod;
    '""".format(
        prod_machine_username=config_parser['PROD Machine']['Username'],
        prod_machine_ip=config_parser['PROD Machine']['IP']
    )
    commands = ''.join(commands.splitlines())

    process = subprocess.Popen("bash.exe", shell=False, universal_newlines=True,
                               stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = process.communicate(dedent(commands))
    if out:
        print("{} - stdout:\n{}".format(launch_on_production.__name__, out))
    if err:
        print("{} - stderr:\n{}".format(launch_on_production.__name__, err))

    print_section_footer()


def refresh_pipeline(config_file_name):
    execute_cleanpy()  # -c
    generate_virtual_environment()  # -v
    build_package_wheel()  # -b
    push_app_to_production(config_file_name)  # -p
    deploy_on_production(config_file_name)  # -d
    push_content_to_production(config_file_name)  # -a
    push_config_to_production(config_file_name)  # -z
    launch_on_production(config_file_name)  # -l


def main():
    argument_parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    argument_parser.add_argument(
        "-C", "--config",
        default="config.py",
        help="Specify file name of .ini config file in the project_root/utils dir. Default: 'config.py'."
    )
    argument_parser.add_argument(
        "-c", "--cleanpy",
        action="store_true",
        help="Excecute cleanpy to clean project directory."
    )
    argument_parser.add_argument(
        "-v", "--generate-venv",
        action="store_true",
        help="Wipe and recreate virtual environment."
    )
    argument_parser.add_argument(
        "-b", "--build-package-wheel",
        action="store_true",
        help="Builds a package wheel from source."
    )
    argument_parser.add_argument(
        "-p", "--push-app-to-prod",
        action="store_true",
        help="Build a package of the site and push to production."
    )
    argument_parser.add_argument(
        "-d", "--deploy-on-prod",
        action="store_true",
        help="Install the new package on the deployment machine."
    )
    argument_parser.add_argument(
        "-a", "--push-content-to-prod",
        action="store_true",
        help="Pushes updated content from local instance dir to production server instance dir."
    )
    argument_parser.add_argument(
        "-z", "--push-config-to-prod",
        action="store_true",
        help="Launch the application on the deployment machine."
    )
    argument_parser.add_argument(
        "-l", "--launch-on-prod",
        action="store_true",
        help="Launch the application on the deployment machine."
    )
    argument_parser.add_argument(
        "-r", "--refresh-pipeline",
        action="store_true",
        help="Clean project dir, generate new venv, & push to / deploy on production server."
    )
    args = argument_parser.parse_args()

    # Execute appropriate logic per specified optional argument
    if args.cleanpy:
        execute_cleanpy()
    elif args.generate_venv:
        generate_virtual_environment()
    elif args.build_package_wheel:
        build_package_wheel()
    elif args.push_app_to_prod:
        push_app_to_production(args.config)
    elif args.deploy_on_prod:
        deploy_on_production(args.config)
    elif args.push_content_to_prod:
        push_content_to_production(args.config)
    elif args.push_config_to_prod:
        push_config_to_production(args.config)
    elif args.launch_on_prod:
        launch_on_production(args.config)
    elif args.refresh_pipeline:
        refresh_pipeline(args.config)
    else:
        print("\n*No args passed to this script, therefore no script actions "
              "performed. See help message ('project_utils.py -h') for help.*\n")


if __name__ == "__main__":
    main()
