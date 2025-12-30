## High-Level Comparison

| Feature                      | setuptools                                  | build (PEP 517)                                    | Poetry                                              |
|------------------------------|---------------------------------------------|----------------------------------------------------|-----------------------------------------------------|
| **Primary Role**             | Metadata + build scripts (`setup.py`)       | Front‑end for PEP 517 backends (e.g. setuptools)   | Full project & dependency manager                   |
| **Configuration**            | `setup.py` / `setup.cfg`                    | `pyproject.toml` → `[build-system]` + backend      | `pyproject.toml` → `[tool.poetry]`                  |
| **Dependency Management**    | External (pip, requirements.txt)            | External (pip, requirements.txt)                   | Built‑in, lockfile (`poetry.lock`)                  |
| **Build Invocation**         | `python setup.py sdist bdist_wheel`         | `python -m build`                                  | `poetry build`                                       |
| **Environment Isolation**    | via `venv` / `virtualenv` manually          | via `venv` / `virtualenv` manually                 | `poetry shell` (auto‐managed venv)                  |
| **Locking**                  | No                                           | No                                                 | Yes (`poetry.lock`)                                 |
| **Versioning Support**       | Manual or `setuptools_scm` plugin           | Manual or via backend plugins                      | Built‑in `version` field, can use `poetry version`  |
| **Publishing**               | `twine upload dist/*`                       | `twine upload dist/*`                              | `poetry publish [--build]`                          |
| **Ideal for**                | Legacy projects & ultra‑custom scripts      | Standardized builds via PEP 517                    | New projects seeking full-stack dependency + build  |

---

## Example Project Using **setuptools**

### Structure
```
my_pkg/
├── src/
│   └── my_pkg/
│       ├── __init__.py
│       └── core.py
├── tests/
│   └── test_core.py
├── setup.py
└── setup.cfg
```

### setup.cfg
```ini
[metadata]
name = my-pkg
version = 0.1.0
author = Alice Dev
description = A sample package using setuptools
long_description = file: README.md
license = MIT
classifiers =
    Programming Language :: Python :: 3.9
    License :: OSI Approved :: MIT License

[options]
package_dir =
    = src
packages = find:
python_requires = >=3.7
install_requires =
    requests>=2.25
```

### setup.py
```python
#!/usr/bin/env python
from setuptools import setup

if __name__ == "__main__":
    setup()
```

### Build & Publish
```bash
# Create source and wheel
python setup.py sdist bdist_wheel

# Upload to PyPI
pip install twine
twine upload dist/*
```

---

## Example Project Using **build** (PEP 517)

### Structure
```
my_pkg/
├── src/my_pkg/__init__.py
├── src/my_pkg/core.py
├── tests/test_core.py
└── pyproject.toml
```

### pyproject.toml
```toml
[build-system]
requires = ["setuptools>=42", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "my-pkg"
version = "0.1.0"
description = "Sample PEP 517 package"
authors = [{ name = "Alice Dev", email = "alice@example.com" }]
readme = "README.md"
license = { text = "MIT" }
dependencies = [
  "requests>=2.25",
]
dynamic = ["classifiers"]
```

### Build & Publish
```bash
# Install the build frontend
pip install build

# Build sdist + wheel into dist/
python -m build

# Upload with twine
pip install twine
twine upload dist/*
```

---

## Example Project Using **Poetry**

### Structure
```
my-poetry-pkg/
├── my_pkg/
│   ├── __init__.py
│   └── core.py
├── tests/test_core.py
└── pyproject.toml
```

### pyproject.toml
```toml
[tool.poetry]
name = "my-poetry-pkg"
version = "0.1.0"
description = "A sample package managed by Poetry"
authors = ["Alice Dev <alice@example.com>"]
license = "MIT"
readme = "README.md"

[tool.poetry.dependencies]
python = ">=3.7,<4.0"
requests = "^2.25"

[tool.poetry.dev-dependencies]
pytest = "^7.0"

[tool.poetry.scripts]
my-pkg-cli = "my_pkg.core:main"

[build-system]
requires = ["poetry-core>=1.5.0"]
build-backend = "poetry.core.masonry.api"
```

### Workflow
```bash
# Install / create virtualenv automatically
cd my-poetry-pkg
poetry install

# Enter venv subshell
poetry shell

# Add a new dependency and update lockfile
poetry add numpy

# Bump version (semver)
poetry version patch  # => 0.1.1

# Run tests
poetry run pytest

# Build package (sdist & wheel)
poetry build

# Publish to PyPI (will ask for credentials)
poetry publish --build
```

---

## Deep‑Dive: Pros & Cons

| Aspect                     | setuptools                                       | PEP 517 (`build`)                            | Poetry                                                       |
|----------------------------|--------------------------------------------------|----------------------------------------------|--------------------------------------------------------------|
| **Simplicity**             | ✔ “Just” write `setup.py`; however, grows verbose for custom steps. | ✔ Encourages declarative `pyproject.toml`.   | ✔ Very user‑friendly CLI; `poetry new` scaffolds projects.   |
| **Flexibility**            | ✔ Full Python in setup scripts                   | ✗ Metadata only in TOML, custom hooks harder | ✗ Can’t easily drop in custom build logic outside plugin API |
| **Isolation**              | ✗ You manage venv yourself                        | ✗ Same as setuptools                          | ✔ Built‑in venv management                                    |
| **Lockfiles**              | ✗ A gap: must use pip‑compile/requirements.txt    | ✗ Same                                         | ✔ Ensures exact reproducibility via `poetry.lock`             |
| **PEP Compliance**         | ✗ `setup.py` is legacy; migrating to `pyproject.toml` encouraged | ✔ Fully PEP 517/518–compliant                 | ✔ Compliant and uses poetry‑core                                |
| **Extensibility**          | ✔ Easy to hook into any step in code              | ✗ Limited to backend plugin APIs              | ✗ Extensions via plugins (less mature than setuptools)         |

---

## When to Use What?

1. **Existing / Legacy Projects**  
   Stick with **setuptools** if you have a mature codebase already structured around `setup.py`/`setup.cfg`—especially if you have custom `cmdclass` steps.

2. **Standards‑First Build**  
   Use **build** (PEP 517) if you want a minimal, declarative build manifest in `pyproject.toml` and don’t need a full dependency manager.

3. **Greenfield + Full‑Stack Management**  
   Adopt **Poetry** for new projects where you want:  
   - Dependency resolution + lockfiles  
   - Version management (`poetry version …`)  
   - Automatic venv isolation  
   - One‑stop CLI for test, lint, build, publish  

---

## Summary

- **setuptools** remains the workhorse for Python packaging, with full scripting power.  
- **build** brings you up to modern PEP 517 standards with only minimal config.  
- **Poetry** adds batteries‑included dependency management, lockfiles, and versioning, making it ideal for most new projects.
