
---

# 📘 Learning & Practice Repository 

## Overview

This repository is a **structured learning workspace** that combines:

* 📚 Curated **resources & references**
* ✍️ **Exercises** (theory → practice)
* 🧩 **Code snippets** for quick lookup
* 🛠 **Small projects** for hands-on learning
* 🧪 Reproducible **Python environments**

It is designed to support **incremental learning**, **experimentation**, and **clean execution** without dependency conflicts.

---

## Repository Goals

* Keep **learning materials and executable code in one place**
* Enforce **repeatable environments**
* Allow **independent sub-projects** without breaking the global setup
* Encourage **clean structure and documentation**

---

## Repository Structure

```text
.
├── resources/
│   ├── articles/
│   ├── books/
│   └── links.md
│
├── exercises/
│   ├── beginner/
│   ├── intermediate/
│   └── advanced/
│
├── snippets/
│   ├── python/
│   ├── algorithms/
│   └── utilities/
│
├── projects/
│   ├── project_01/
│   │   ├── src/
│   │   ├── tests/
│   │   ├── requirements.txt
│   │   └── README.md
│   └── project_02/
│
├── scripts/
│   ├── setup.py
│   └── run_all.py
│
├── requirements.txt
├── pyproject.toml (optional)
├── .gitignore
├── .venv/               # optional global environment
└── README.md
```

---

## Environment Management

This repository supports **two valid environment strategies**:

---

### Option 1: Global Virtual Environment (Recommended for learning & scripts)

Use a single environment at the repository root when:

* Dependencies are shared
* Projects are lightweight
* You want faster setup

#### Create the environment

```bash
python -m venv .venv
```

#### Activate the environment

**Linux / macOS**

```bash
source .venv/bin/activate
```

**Windows (PowerShell)**

```powershell
.venv\Scripts\Activate.ps1
```

#### Install dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

All scripts, exercises, and snippets can now be run from the root.

---

### Option 2: Per-Project Virtual Environments (Recommended for isolation)

Each project under `projects/` **may define its own environment** if it has:

* Specialized dependencies
* Conflicting versions
* Independent execution requirements

Example:

```text
projects/project_01/
├── .venv/
├── requirements.txt
├── src/
└── README.md
```

#### Setup (inside the project directory)

```bash
python -m venv .venv
source .venv/bin/activate   # or Windows equivalent
pip install -r requirements.txt
```

> Each project README must clearly state whether it uses the **global environment** or a **local one**.

---

## Running Code

### Running a script from the root

```bash
python scripts/run_all.py
```

### Running an exercise

```bash
python exercises/beginner/exercise_01.py
```

### Running a project

```bash
cd projects/project_01
python src/main.py
```
---
### Node.js example
```bash
nvm install
npm install
```

A repository-level environment must never silently assume a runtime.
If it exists, it must be documented.
---

## Content Guidelines

### Resources

* Markdown only
* Prefer **original sources**
* Avoid outdated links
* Explain *why* a resource is useful

### Exercises

* Self-contained
* Clearly state the objective
* Include expected output or validation logic

### Code Snippets

* Minimal
* Single responsibility
* No hidden dependencies

### Projects

Each project **must include**:

* `README.md`
* Clear entry point
* Dependency list
* Instructions to run

---

## Dependency Rules

* **Global dependencies** go in root `requirements.txt`
* **Project-specific dependencies** go in the project folder
* Do **not** mix system Python with repository execution
* Do **not** commit virtual environments (`.venv` must be git-ignored)

---

## Python Version

Unless stated otherwise:

* Minimum supported version: **Python 3.10**
* Verify with:

  ```bash
  python --version
  ```

---

## Contribution Guidelines

* Keep commits small and focused
* Do not break existing exercises or scripts
* Update README files when behavior changes
* Prefer clarity over cleverness

---

## Common Issues & Troubleshooting

### Virtual environment not activating

* Ensure you are not inside another active environment
* On Windows, confirm script execution is allowed

### Import errors

* Confirm the correct environment is active
* Verify `pip list` matches expected dependencies

### Script not found

* Run commands from the repository root unless stated otherwise

---

## License

This repository is intended for **educational and personal use**.
Add a license file if you plan to distribute or reuse externally.

---
