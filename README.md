# sNET-TUI

Welcome to the sNET Terminal User Interface, a Python-based application that allows users to interact with the SingularityNET command-line-interface. This guide will help you set up and run the application on your local machine.

## Prerequisites

Before starting, ensure you have the following installed:

- Git

The run script will prompt you to install the following dependancies (if required):

- [Python](https://www.python.org) >= 3.10

- [pip](https://pypi.org/project/pip/) **_Python package manager_**

- [venv](https://docs.python.org/3/library/venv.html) **_Python virtual-environment manager_**

- [Homebrew](https://brew.sh) **_Package manager (MacOS only)_**

- [Chocolatey](https://chocolatey.org) **_Package manager (Windows only)_**

## Installation

To get started with sNET-TUI, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/vbrltech/sNET-TUI.git
   ```
2. Navigate to the cloned directory:
   ```bash
   cd sNET-TUI
   ```

## Running the application

**For Linux Operating Systems (Bash):**

```bash
bash linux_run.sh
```

**For MacOS (Zsh/Bash):**

```bash
sh macos_run.sh
```

**For Windows Operating Systems (CMD):**

**_Double click the "windows_run.sh" file, or run the following in CMD_**

```powershell
windows_run.bat
```

**NOTE:**

First startup will take longer than usual, as the script will check and install base dependancies, generate a virtual environment and install the python requirements. The scripts are simple and commented, please read through them so you understand what is being done on your machine.
