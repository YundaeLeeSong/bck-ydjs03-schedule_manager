#!/usr/bin/env python3
"""
runner.py: Project Task Runner & Environment Manager.

This script manages development tasks:
- Environment introspection (init)
- Dependency & Executable building (build)
- Testing (test)
- Application execution (run)
- Cleanup (clean)

It automatically detects the application package based on the presence of
'__main__.py' within 'src/main/python'.

Usage:
    python runner.py [init|build|test|run|clean] [--args ...]
"""

import sys
import os
import subprocess
import argparse
import platform
import shutil
import site
from pathlib import Path

# --- Configuration ---
SRC_MAIN = Path("src/main/python")
SRC_TEST = Path("src/test/python")
LIB_DIRS = [Path("lib"), Path("libs")]
BUILD_ARTIFACTS = ["build", "dist", "__pycache__", ".spec"]

class ProjectContext:
    """
    Discovers and holds project context information.

    This class is responsible for identifying the project root, the main application
    package name by looking for a `__main__.py` file, and setting up the entry point
    filename for build tools.

    Attributes:
        root_dir (Path): The absolute path to the project's root directory.
        app_package (str or None): The name of the detected application package
            (the folder containing `__main__.py`), or None if not found.
        app_entry_point (str): The filename used as the entry point for PyInstaller
            (default is 'cli.py').
    """

    def __init__(self):
        """
        Initialize the ProjectContext.

        Detects the current working directory and attempts to identify the
        application package name.
        """
        self.root_dir = Path.cwd()
        self.app_package = self._detect_app_package()
        self.app_entry_point = "cli.py"  # Temporary entry point for PyInstaller

    def _detect_app_package(self):
        """
        Identify the main application package.

        Scans `src/main/python` for a subdirectory containing `__main__.py`.
        If that fails, it attempts to deduce the package name from the current
        directory name using a specific naming convention (e.g., `env-projectname`).

        Returns:
            str or None: The detected package name, or None if detection fails.
        """
        if not SRC_MAIN.exists():
            return None
        
        for item in SRC_MAIN.iterdir():
            if item.is_dir() and (item / "__main__.py").exists():
                return item.name
        
        # Fallback: Try to guess from current directory name if standard structure fails
        # (Preserving original logic behavior as fallback)
        import re
        match = re.match(r"([^-]+)-([A-Za-z0-9_]+)$", self.root_dir.name)
        if match:
            return match.group(2).lower()
        return None

class TaskRunner:
    """
    Executes development tasks for the project.

    This class handles the logic for initialization, building, testing, running,
    and cleaning the project. It relies on `ProjectContext` for project-specific
    details.

    Attributes:
        ctx (ProjectContext): The project context containing paths and package info.
        python_exe (str): The path to the currently running Python executable.
    """

    def __init__(self):
        """
        Initialize the TaskRunner.

        Sets up the project context and captures the current Python executable path.
        """
        self.ctx = ProjectContext()
        self.python_exe = sys.executable

    def _run_cmd(self, cmd, cwd=None, check=True, shell=True):
        """
        Helper method to execute shell commands.

        Args:
            cmd (str): The command string to execute.
            cwd (str or Path, optional): The working directory for the command.
                Defaults to None (current working directory).
            check (bool, optional): If True, raise a CalledProcessError if the
                command returns a non-zero exit code. Defaults to True.
            shell (bool, optional): If True, the command is executed through the
                shell. Defaults to True.

        Raises:
            SystemExit: If the command fails (and `check` is True), the script
                exits with the command's return code.
        """
        print(f"[{cmd}]")
        try:
            subprocess.run(cmd, cwd=cwd, check=check, shell=shell)
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")
            sys.exit(e.returncode)

    def _ensure_package(self, package):
        """
        Ensure a Python package is installed.

        Checks if the package can be imported. If not, attempts to install it
        using pip.

        Args:
            package (str): The name of the package to check/install.
        """
        try:
            __import__(package)
        except ImportError:
            print(f"Installing missing tool: {package}...")
            self._run_cmd(f"{self.python_exe} -m pip install {package}")

    def init(self):
        """
        Inspect the environment and configure `sys.path`.

        Prints information about the Python interpreter and virtual environment.
        Detects source and library directories (`src/main/python`, `src/test/python`,
        `lib`, etc.) and adds them to a user-local `.pth` file so they are
        automatically available in future Python sessions.
        """
        print("=" * 60)
        print("Environment Initialization & Inspection")
        print("=" * 60)
        
        # Python Info
        print(f"Python Version: {sys.version.split()[0]}")
        print(f"Executable:     {self.python_exe}")
        
        # Virtual Env
        in_venv = sys.prefix != getattr(sys, 'base_prefix', sys.prefix)
        print(f"In Venv:        {in_venv}")
        
        # Path Configuration
        print("\nConfiguring sys.path...")
        paths_to_add = []
        
        # Normalize sys.path for comparison (handle Windows path format differences)
        sys_path_normalized = {Path(p).resolve() for p in sys.path if Path(p).exists()}
        
        # Check all directories
        all_dirs = [SRC_MAIN, SRC_TEST] + LIB_DIRS
        print("Checking directories:")
        for p in all_dirs:
            abs_path = p.resolve() if p.exists() else None
            if abs_path:
                if abs_path not in sys_path_normalized:
                    paths_to_add.append(abs_path)
                    print(f"  ✓ {p} -> {abs_path} (will be added)")
                else:
                    print(f"  - {p} -> {abs_path} (already in sys.path)")
            else:
                print(f"  ✗ {p} (not found)")

        if paths_to_add:
            self._update_pth_file(paths_to_add)
            print("\nAdded paths to local-packages.pth:")
            for p in paths_to_add:
                print(f"  + {p}")
        else:
            print("\n  (No new paths to add)")

        print("\nCurrent sys.path:")
        for p in sys.path[:5]: # Show first 5
            print(f"  - {p}")
        if len(sys.path) > 5: print("    ...")

    def _update_pth_file(self, paths):
        """
        Update the `.pth` file in the user site-packages directory.

        This allows the added paths to persist across Python sessions.

        Args:
            paths (list of Path): A list of Path objects to add to the `.pth` file.
        """
        try:
            user_site = Path(site.getusersitepackages())
            if not user_site.exists():
                user_site.mkdir(parents=True)
            
            pth_file = user_site / "local-packages.pth"
            existing = set()
            if pth_file.exists():
                existing = set(pth_file.read_text().splitlines())
            
            new_lines = [str(p) for p in paths if str(p) not in existing]
            if new_lines:
                with pth_file.open("a") as f:
                    for line in new_lines:
                        f.write(f"{line}\n")
        except Exception as e:
            print(f"Warning: Could not write .pth file: {e}")

    def build(self):
        """
        Build the project using PyInstaller.

        Steps:
        1. Ensures `pipreqs` and `PyInstaller` are installed.
        2. Generates `requirements.txt` using `pipreqs`.
        3. Installs dependencies from `requirements.txt`.
        4. Creates a temporary entry point script (`cli.py`).
        5. Runs `pyinstaller` to create a single-file executable.
        6. Cleans up temporary files.
        """
        if not self.ctx.app_package:
            print("Error: Could not detect application package (containing __main__.py).")
            return

        print(f"Building package: {self.ctx.app_package}")
        
        # Ensure tools
        self._ensure_package("pipreqs")
        self._ensure_package("PyInstaller") # import name is usually different, handled by pip
        
        # Generate requirements
        print("\nGenerating requirements.txt...")
        # Reinstall pipreqs to fix any broken launcher scripts (especially on Windows)
        self._run_cmd(f"{self.python_exe} -m pip install --force-reinstall --no-deps pipreqs")
        # Now call pipreqs normally
        self._run_cmd("pipreqs . --force --ignore ext,docs,doc,scripts,script,downloads,build,dist")
        
        # Install requirements
        print("Installing dependencies...")
        self._run_cmd(f"{self.python_exe} -m pip install -r requirements.txt")
        Path("requirements.txt").unlink(missing_ok=True)

        # Create temporary CLI entry point
        cli_content = f"from {self.ctx.app_package}.__main__ import main\nif __name__ == '__main__': main()"
        Path(self.ctx.app_entry_point).write_text(cli_content)

        try:
            # Run PyInstaller
            print("\nRunning PyInstaller...")
            # Reinstall PyInstaller to fix any broken launcher scripts (especially on Windows)
            self._run_cmd(f"{self.python_exe} -m pip install --force-reinstall --no-deps PyInstaller")
            
            # Construct search paths for PyInstaller
            search_paths = [str(SRC_MAIN.absolute())]
            for lib in LIB_DIRS:
                if lib.exists():
                    search_paths.append(str(lib.absolute()))
            
            # Join paths with os.pathsep (';' on Windows, ':' on Unix)
            paths_arg = f'--paths "{os.pathsep.join(search_paths)}"'
            
            cmd = (
                f"pyinstaller --onefile {paths_arg} --add-data \".env{';' if platform.system() == 'Windows' else ':'}.\" "
                f"--name {self.ctx.app_package} {self.ctx.app_entry_point}"
            )
            self._run_cmd(cmd)
        finally:
            # Cleanup temp entry point
            Path(self.ctx.app_entry_point).unlink(missing_ok=True)
            # Cleanup spec file
            Path(f"{self.ctx.app_package}.spec").unlink(missing_ok=True)

    def test(self):
        """
        Run unit tests.

        Discovers and runs tests in `src/test/python`. It temporarily sets
        `PYTHONPATH` to include `src/main/python` so that tests can import
        the application modules.
        """
        if not SRC_TEST.exists():
            print(f"Test directory {SRC_TEST} not found.")
            return
        
        print(f"Running tests in {SRC_TEST}...")
        # Build PYTHONPATH with src/main/python and lib directories
        env = os.environ.copy()
        pythonpath_parts = [str(SRC_MAIN.absolute())]
        for lib_dir in LIB_DIRS:
            if lib_dir.exists():
                pythonpath_parts.append(str(lib_dir.absolute()))
        # Add existing PYTHONPATH if present
        if env.get('PYTHONPATH'):
            pythonpath_parts.append(env['PYTHONPATH'])
        env["PYTHONPATH"] = os.pathsep.join(pythonpath_parts)
        
        cmd = f"{self.python_exe} -m unittest discover -s {SRC_TEST} -v"
        subprocess.run(cmd, shell=True, env=env)

    def run(self):
        """
        Run the application.

        Executes the application module (e.g., `python -m mypackage`) with
        `PYTHONPATH` configured to include `src/main/python`.
        """
        if not self.ctx.app_package:
            print("Error: Could not detect application package.")
            return

        print(f"Running {self.ctx.app_package}...")
        env = os.environ.copy()
        # Build PYTHONPATH with src/main/python and lib directories
        pythonpath_parts = [str(SRC_MAIN.absolute())]
        for lib_dir in LIB_DIRS:
            if lib_dir.exists():
                pythonpath_parts.append(str(lib_dir.absolute()))
        # Add existing PYTHONPATH if present
        if env.get('PYTHONPATH'):
            pythonpath_parts.append(env['PYTHONPATH'])
        env["PYTHONPATH"] = os.pathsep.join(pythonpath_parts)
        
        try:
            subprocess.run(f"{self.python_exe} -m {self.ctx.app_package}", shell=True, env=env)
        except KeyboardInterrupt:
            print("\nStopped by user.")

    def clean(self):
        """
        Clean build artifacts.

        Removes directories and files created during the build process, such as
        `build/`, `dist/`, `__pycache__`, and `.spec` files. Also removes the
        local `.pth` file from site-packages.
        """
        print("Cleaning up...")
        for item in BUILD_ARTIFACTS:
            path = Path(item)
            if path.exists():
                if path.is_dir():
                    shutil.rmtree(path)
                else:
                    path.unlink()
                print(f"Removed {path}")
        
        # Clean local-packages.pth
        try:
            user_site = Path(site.getusersitepackages())
            pth_file = user_site / "local-packages.pth"
            if pth_file.exists():
                pth_file.unlink()
                print(f"Removed {pth_file}")
        except Exception:
            pass

def main():
    """
    Main entry point for the script.

    Parses command-line arguments and dispatches control to the appropriate
    `TaskRunner` method.
    """
    parser = argparse.ArgumentParser(description="Project Task Runner")
    parser.add_argument("action", choices=["init", "build", "test", "run", "clean"], help="Action to perform")
    
    args = parser.parse_args()
    runner = TaskRunner()

    if args.action == "init":
        runner.init()
    elif args.action == "build":
        runner.build()
    elif args.action == "test":
        runner.test()
    elif args.action == "run":
        runner.run()
    elif args.action == "clean":
        runner.clean()

if __name__ == "__main__":
    main()