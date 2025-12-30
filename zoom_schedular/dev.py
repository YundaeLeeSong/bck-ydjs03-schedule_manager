#!/usr/bin/env python3
"""
dev.py: Comprehensive report script to understand Python interpreter environment behavior.

This script prints detailed, annotated insights into:
    - Python interpreter details (version, executable paths)
    - Virtual environment activation and its effects
    - sys.path inspection (used for module resolution)
    - PYTHONPATH and related environment variables
    - site-packages and user-site directories
    - sysconfig mappings showing where components are installed
    - Automatically detected source/asset directories appended to sys.path

This is especially useful for understanding how Python's environment resolution works,
particularly in relation to virtual environments (`venv`) and `PYTHONPATH`.

Usage:
    python dev.py [init|build|test|run]

Author: Jaehoon Song

Notes:
1. Each subprocess.run(..., shell=True) starts a new, independent shell.
2. cwd="t" changes the working directory before starting the shell.
3. So, use subprocess.run("echo $PWD", shell=True, check=True, cwd="changed_working_directory")

    # Detect OS and run the appropriate command to print working directory in 't'
    project_path = Path("t")
    if platform.system() == "Windows": subprocess.run(f'cmd /V:ON /C "\
                                                      echo !CD! \
                                                      &&\
                                                      cd {project_path} \
                                                      &&\
                                                      echo !CD!\
                                                      "', shell=True, check=True)
    if platform.system() == "Linux": subprocess.run("\
                                                    echo $PWD \
                                                    ", shell=True, check=True, cwd="t")
    if platform.system() == "Darwin": subprocess.run("echo $PWD", shell=True, check=True, cwd="t")
"""


import subprocess
import sys
import os
import site
import sysconfig
import pprint
from pathlib import Path
from textwrap import indent
import argparse
import platform
import re


# Constants
# Dynamically determine APP_PKG from current folder name
current_folder = Path.cwd().name
match = re.match(r"([^-]+)-([A-Za-z0-9_]+)$", current_folder)
if match:
    APP_PKG = match.group(2).lower()
    print("=============================================================================...")
    print(f"project name is specified...... APP_PKG='{APP_PKG}'")
    print("=============================================================================...")
else:
    raise RuntimeError(f"Project folder name '{current_folder}' does not follow the required '{{env}}-{{project_name}}' convention.")





APP_ENTRY_POINT="cli.py"                     # Change this to your entry point module
CLI_CONTENT = f"""# cli.py
from {APP_PKG}.__main__ import main

if __name__ == "__main__":
    main()
"""
CLI_PATH=Path(APP_ENTRY_POINT)

MAIN_DIR = "src/main/python"
TEST_DIR = "src/test/python"
LIB_DIRS = ['lib', 'libs']


# For Python <3.8 fallback to pkg_resources (deprecated)
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
try:
    import pkg_resources
except ImportError:
    print(
        "[ERROR] 'pkg_resources' is NOT available.\n"
        "You may need to upgrade your Python or install 'setuptools'.\n"
        "Try:\n\n"
        "    pip install setuptools\n"
    )
    raise








def print_section(title):
    print(f"\n{'=' * 80}\n{title}\n{'=' * 80}\n")

def python_version_info():
    print_section("Python Interpreter Information")
    print(f"Python Version              : {sys.version}")
    print(f"Interpreter Implementation  : {sys.implementation.name}")
    print(f"Executable Path             : {sys.executable}")
    print(f"sys.prefix                  : {sys.prefix}")
    print(f"sys.base_prefix             : {getattr(sys, 'base_prefix', 'Not available')}")
    print(f"sys.base_exec_prefix        : {getattr(sys, 'base_exec_prefix', 'Not available')}")

def detect_virtual_environment():
    print_section("Virtual Environment Status")
    base_prefix = getattr(sys, 'base_prefix', sys.prefix)
    is_venv = sys.prefix != base_prefix
    print(f"Virtual Environment Active? : {is_venv}")
    print(f"VIRTUAL_ENV Environment Var : {os.environ.get('VIRTUAL_ENV', 'Not set')}")
    if is_venv:
        print("\nNote: You are inside a virtual environment. sys.path will be isolated\n"
              "from the global interpreter. Installed packages will go into the venv site-packages.")

def show_sys_path():
    print_section("sys.path Inspection")
    print("sys.path determines where Python looks for modules to import.")
    for i, path in enumerate(sys.path):
        label = "(current directory)" if path == '' else ""
        print(f"[{i:2}] {path} {label}")

def remove_ansi_codes(s):
    """
    Removes ANSI escape codes from the input string.
    If there is only one ANSI escape code, returns '(ANSI escape codes) checkout manually'.
    Otherwise, returns the original string.
    """
    import re
    ansi_escape = re.compile(r'\x1b\[[0-9;]*m')
    matches = ansi_escape.findall(s)
    if len(matches) == 1: return '(ANSI escape codes) checkout manually'
    return s


def show_environment_variables():
    print_section("Relevant Environment Variables")
    tracked_keys = ['PYTHONPATH', 'PATH', 'VIRTUAL_ENV']
    for key in tracked_keys:
        print(f"{key:<15}: {os.environ.get(key, 'Not set')}")

    print("\nSample of Environment Variables:")
    for k, v in list(os.environ.items()):
        print(f"{k:<40}= {remove_ansi_codes(v)}")
    sample = list(os.environ.items())[:7]
    for k, v in sample:
        print(f"{k:<20}= {remove_ansi_codes(v)}")
    if len(os.environ) > 7:
        print(f"... plus {len(os.environ) - 7} more variables")

def show_site_packages():
    print_section("site-packages Locations")
    try:
        site_pkgs = site.getsitepackages()
        print("Global site-packages:")
        for path in site_pkgs:
            print(f"  - {path}")
    except AttributeError:
        print("site.getsitepackages() is not available in this environment.")
    print(f"\nUser site-packages         : {site.getusersitepackages()}")

def show_sysconfig_paths():
    print_section("sysconfig Installation Paths")
    print("These show where standard components (scripts, libs, etc.) are installed:")
    paths = sysconfig.get_paths()
    formatted = pprint.pformat(paths, indent=2)
    print(indent(formatted, prefix="  "))

def write_pth_file(persisted_paths):
    """
    Writes discovered paths to a .pth file in the user site-packages directory
    so they are persistently added to sys.path on future interpreter sessions.
    """
    user_site = Path(sysconfig.get_paths()["platlib"])
    user_site.mkdir(parents=True, exist_ok=True)
    pth_file = user_site / "local-packages.pth"

    existing_lines = set()
    if pth_file.exists():
        existing_lines = set(line.strip() for line in pth_file.read_text().splitlines())

    new_lines = [p for p in persisted_paths if p not in existing_lines]
    if new_lines:
        with pth_file.open("a") as f:
            for path in new_lines:
                f.write(f"{path}\n")
        print("Persistent paths added to .pth file:")
        for path in new_lines:
            print(f"  - {path}")
    else:
        print("No new persistent paths needed to be added. Already up to date.")
    print("The .pth file is located at:")
    print(f"  {pth_file}")
    print(f"\nGlobal site-packages       : {sysconfig.get_paths()["platlib"]}")

def update_sys_path():
    """
    Detects non-package organizing directories (e.g., 'lib', 'libs', 'src') that do not contain
    __init__.py files and appends them to sys.path (temporarily and permanently).

    Conventions followed:
    - Folder names like 'lib', 'libs', 'src' are commonly used to organize modules.
    - Only bare folders (not Python packages) are added to avoid import conflicts.
    - The sys.path is only updated if the path is not already present.
        - Avoids duplication in sys.path or persistent entries.
    """
    print_section("Auto-Detect & Append Organizational Folders to sys.path")
    cwd = Path.cwd()
    candidates = [MAIN_DIR, TEST_DIR] + LIB_DIRS
    added = []
    

    for folder_name in candidates:
        candidate_path = cwd / folder_name
        if candidate_path.is_dir():
            init_file = candidate_path / '__init__.py'
            if not init_file.exists() and str(candidate_path) not in sys.path:
                # sys.path.append(str(candidate_path))
                sys.path.insert(0, str(candidate_path)) # sys.path.append(str(candidate_path))
                added.append(str(candidate_path))

    if added:
        print("The following organizing folders were added to sys.path (temporarily & persistently):")
        for path in added:
            print(f"  - {path}")
        write_pth_file(added)
    else:
        print("No bare organizing folders (lib, libs, src) were found to add.")





















def build():
    """
    Installs and updates build automation tools like PyInstaller and pipreqs.
    """
    def is_installed(package_name):
        try:
            pkg_resources.get_distribution(package_name)
            return True
        except pkg_resources.DistributionNotFound:
            return False
    # print(is_installed("numpy"))       # True if installed
    # print(is_installed("notapackage")) # False
    print_section("Build Automation Tools")
    # build automation tools
    pkgs = [
        "pipreqs", 
        "pyinstaller"
    ]
    for pkg in pkgs:
        if is_installed(pkg): print(f"{pkg} is already installed.")
        if not is_installed(pkg): subprocess.run(f"{sys.executable} -m pip install --upgrade {pkg}", shell=True, check=True)
    # build
    CLI_PATH.write_text(CLI_CONTENT) # [pyinstaller] Temporarily generate cli.py with the required content
    subprocess.run("pipreqs . --force --ignore docs,doc,scripts,script,downloads", shell=True, check=True)
    subprocess.run("pip install -r requirements.txt && rm requirements.txt", shell=True, check=True)
    subprocess.run(f"pyinstaller --onefile --add-data \".env;.\" --name {APP_PKG} {APP_ENTRY_POINT} && rm *.spec", shell=True, check=True)
    if CLI_PATH.exists(): CLI_PATH.unlink() # [pyinstaller] Delete cli.py after build










def test():
    """
    Runs the test suite for the project.
    """
    print_section("Running Tests")
    if not Path(TEST_DIR).is_dir():
        print(f"Test directory '{TEST_DIR}' does not exist.")
        return
    # tests 
    subprocess.run(f"{sys.executable} -m unittest discover -s {TEST_DIR} -v", shell=True, check=True)


    # Detect OS and run the appropriate command to print working directory in 't'
    project_path = Path("t")
    if platform.system() == "Windows": subprocess.run(f'cmd /V:ON /C "\
                                                      echo !CD! \
                                                      &&\
                                                      cd {project_path} \
                                                      &&\
                                                      echo !CD!\
                                                      "', shell=True, check=True)
    if platform.system() == "Linux": subprocess.run("\
                                                    echo $PWD \
                                                    ", shell=True, check=True, cwd="t")
    if platform.system() == "Darwin": subprocess.run("echo $PWD", shell=True, check=True, cwd="t")

def run():
    """
    Main function to run the project.
    """
    print_section(f"Running your project..! ({APP_PKG})")
    # run 
    try:
        subprocess.run(f"{sys.executable} -m {APP_PKG}", shell=True, check=True)
    except KeyboardInterrupt:
        print("\nExecution interrupted by user (Ctrl+C).")
    except subprocess.CalledProcessError as e:
        print(f"Error running project: {e}")
    except Exception:
        pass  # Ignore all other errors

def init():
    python_version_info()
    detect_virtual_environment()
    update_sys_path()
    show_sys_path()
    show_environment_variables()
    show_site_packages()
    show_sysconfig_paths()
    print("\nDone. Use this information to understand your Python interpreter environment, especially how it behaves inside vs. outside a virtual environment.")

def reset():
    """
    Deletes the local-packages.pth file from the user site-packages directory if it exists.
    """
    user_site = Path(sysconfig.get_paths()["platlib"])
    pth_file = user_site / "local-packages.pth"
    print_section("Resetting local-packages.pth")
    if pth_file.exists():
        pth_file.unlink()
        print(f"Deleted: {pth_file}")
    else:
        print(f"No .pth file found at: {pth_file}")

def main():
    """
    Main entry point for the script. Parses command-line arguments and calls the appropriate function.
    """
    parser = argparse.ArgumentParser(
        description="Project utility script",
        usage="python dev.py {init|build|test|run|reset}"
    )
    parser.add_argument(
        "action",
        choices=["init", "build", "test", "run", "reset"],
        help="Action to perform (choose from: init, build, test, run, reset)"
    )
    if len(sys.argv) != 2:
        parser.print_help()
        sys.exit(1)
    args = parser.parse_args()
    if args.action == "init": init()
    if args.action == "build": build()
    if args.action == "test": test()
    if args.action == "run": run()
    if args.action == "reset": reset()

if __name__ == '__main__':
    main()