"""Script Contains DevOps-like automation functionality to help support the development, deployment, and management of the Zaphod Flask web app.

Important Note: This script relies on values set within a config.ini. By default, that file is pulled from project_root/utils/config.ini. However, this has default values within it. Therefore, one must either:
- edit the default 'config.ini' file as appropriate.
- OR, create a separate copy of the .ini file, edit as appropriate, and then pass the file name in when invoking the script using the -C / --config argument.
    """

import argparse
import os
import shutil
import subprocess
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

    process = subprocess.Popen(
        'powershell.exe', stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = process.communicate(dedent(commands).encode('utf-8'))

    if out:
        print("{} - stdout:\n{}".format(build_package_wheel.__name__, out.decode('utf-8')))
    if err:
        print("{} - stderr:\n{}".format(build_package_wheel.__name__, err.decode('utf-8')))
    print_section_footer()


def refresh_build():  # -r
    execute_cleanpy()  # -c
    generate_virtual_environment()  # -v
    build_package_wheel()  # -b


def main():
    argument_parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
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
        "-r", "--refresh-build",
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
    elif args.refresh_build:
        refresh_build()
    else:
        print("\n*No args passed to this script, therefore no script actions "
              "performed. See help message ('project_utils.py -h') for help.*\n")


if __name__ == "__main__":
    main()
