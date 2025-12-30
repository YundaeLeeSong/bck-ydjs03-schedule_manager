# alpaca_tradebot

A minimal Python package scaffolded without build tools.

## `venv` Installation

```bash
# from project root
source ../venv/Scripts/activate && pip install setuptools && clear
```

## Usage

```python
from alpaca_tradebot.math_utils import add
print(add(1, 2))  # 3
```



# Alpaca TradeBot

A simple Python trading bot scaffold for interacting with the Alpaca API. This project provides a basic package structure to help you get started with developing and testing your own trading strategies using Alpaca.

## Project Structure

- `src/alpaca_tradebot/` - Main source code for the trading bot.
- `tests/` - Unit and integration tests for the bot.

## Getting Started

### 1. Set up your virtual environment


---

## dev.py Utility Script

`dev.py` is a comprehensive utility script designed to help developers understand and manage their Python interpreter environment and project structure. It provides detailed insights into how Python resolves modules, activates virtual environments, and organizes dependencies. Additionally, it automates build, test, and run workflows for your project.

### Features

* **Interpreter Information**: Prints Python version, implementation, executable location, and prefix settings.
* **Virtual Environment Detection**: Identifies whether a virtual environment is active and displays related environment variables.
* **sys.path Inspection**: Lists all paths Python uses to resolve imports, including project directories and site-packages.
* **Environment Variables**: Shows key variables like `PYTHONPATH`, `PATH`, and `VIRTUAL_ENV`, plus a sample of additional variables.
* **Site-Packages Locations**: Reports global and user-specific site-packages directories.
* **sysconfig Paths**: Displays installation paths for scripts, libraries, and other components.
* **Automatic Path Management**: Detects common library/source directories (`src`, `lib`, `libs`, `src/test/python`) and injects them into `sys.path`, with optional persistent `.pth` support.
* **Build Automation**: Installs or updates tools like `pipreqs` and `PyInstaller`, generates a `requirements.txt`, and creates a one-file executable.
* **Testing**: Runs your test suite via Python's `unittest` discovery.
* **Project Run**: Launches your application via its package entry point.

---

## Prerequisites

* Python 3.6 or newer
* `setuptools` (for `pkg_resources` support)
* A Unix-like shell or Windows PowerShell/CMD

## Getting Started

1. **Clone your repository** and place `dev.py` at the root of your project.
2. Adjust the following constants at the top of the script if necessary:

   ```python
   APP_PKG = "your_package_name"      # Your Python package name
   APP_ENTRY_POINT = "cli.py"         # Entry point script inside your package
   MAIN_DIR = "src/main/python"       # Main source directory
   TEST_DIR = "src/test/python"       # Test directory
   LIB_DIRS = ['lib', 'libs']          # Additional library directories
   ```
3. Make `dev.py` executable (optional):

   ```bash
   chmod +x dev.py
   ```

## Usage

Run the script with one of four actions:

```bash
python dev.py <action>
```

| Action  | Description                                                                                                |
| ------- | ---------------------------------------------------------------------------------------------------------- |
| `init`  | Detects environment, updates `sys.path`, and prints detailed interpreter and path info.                    |
| `build` | Installs build tools, generates `requirements.txt`, installs deps, and packages your app with PyInstaller. |
| `test`  | Discovers and runs unit tests in your test directory.                                                      |
| `run`   | Executes your application via `python -m your_package`.                                                    |

### Examples

* **Initialize dev environment**:

  ```bash
  python dev.py init
  ```

* **Build standalone executable**:

  ```bash
  python dev.py build
  ```

* **Run tests**:

  ```bash
  python dev.py test
  ```

* **Launch application**:

  ```bash
  python dev.py run
  ```

## How It Works

* **Initialization (`init`)**: The script inspects the running interpreter, checks for `venv`, modifies `sys.path` to include your source folders, and writes `.pth` entries for persistence.
* **Build (`build`)**: It uses `pipreqs` to generate `requirements.txt` based on imports, installs missing packages, then runs `PyInstaller` to produce a single binary.
* **Testing (`test`)**: Leverages Python's built-in `unittest` discovery mechanism for verbose test output.
* **Run (`run`)**: Uses `subprocess` to call your package as a module, making development launches consistent.

## Customization & Extensibility

* **Directory Layout**: Modify `MAIN_DIR`, `TEST_DIR`, or `LIB_DIRS` to suit your project's structure.
* **Persistent Paths**: The `.pth` file is created in your `platlib` directory to ensure paths survive across interpreter sessions.
* **Build Tools**: Extend the `build()` function to add tools like `flake8`, `black`, or other linters/formatters.

## Troubleshooting

* **Missing `pkg_resources`**: Install `setuptools`:

  ```bash
  pip install --upgrade setuptools
  ```
* **Permission Errors**: On Unix-like systems, ensure you have write access to the `site-packages` directory or run commands with appropriate privileges.
* **Unexpected `sys.path`**: If you see duplicate or missing entries, verify your environment variables (`PYTHONPATH`) and check for existing `.pth` files.

## License

This project is licensed under the MIT License. Feel free to adapt and extend for your own development workflows.

---

*Generated by dev.py utility documentation guidelines.*
