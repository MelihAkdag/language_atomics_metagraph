# language_atomics_metagraph
Repository to explore atomics of language as knowledge primitives.

## Development Setup

### 1. Install uv
This project uses `uv` as package manager.
If you haven't already, install [uv](https://docs.astral.sh/uv), preferably using it's ["Standalone installer"](https://docs.astral.sh/uv/getting-started/installation/#__tabbed_1_2) method: <br>
..on Windows:
```sh
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```
..on MacOS and Linux:
```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
```
(see [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/) for all / alternative installation methods.)

Once installed, you can update `uv` to its latest version, anytime, by running:
```sh
uv self update
```

### 2. Install Python
This project requires Python 3.10 or later. <br>
If you don't already have a compatible version installed on your machine, the probably most comfortable way to install Python is through `uv`:
```sh
uv python install
```
This will install the latest stable version of Python into the uv Python directory, i.e. as a uv-managed version of Python.

Alternatively, and if you want a standalone version of Python on your machine, you can install Python either via `winget`:
```sh
winget install --id Python.Python
```
or you can download and install Python from the [python.org](https://www.python.org/downloads/) website.

### 3. Clone the repository
Clone the mvx repository into your local development directory:
```sh
git clone https://github.com/MelihAkdag/language_atomics_metagraph.git
```
Change into the project directory after cloning:
```sh
cd language_atomics_metagraph
```

### 4. Install dependencies
Run `uv sync` to create a virtual environment and install all project dependencies into it.

```sh
uv sync
```

> **Note**: `uv` will create a new virtual environment called `.venv` in the project root directory when running
> `uv sync` the first time. 

### 5. (Optional) Activate the virtual environment
When using `uv`, there is in almost all cases no longer a need to manually activate the virtual environment. <br>
`uv` will find the `.venv` virtual environment in the working directory or any parent directory, and activate it on the fly whenever you run a command via `uv` inside your project folder structure:
```sh
uv run <command>
```

However, you still _can_ manually activate the virtual environment if needed.
When developing in an IDE, for instance, this can in some cases be necessary depending on your IDE settings.
To manually activate the virtual environment, run one of the "known" legacy commands: <br>
..on Windows:
```sh
.venv\Scripts\activate.bat
```
..on Linux:
```sh
source .venv/bin/activate
```

### 6. Adding new libraries to the virtual environment

To add new dependencies to your project, use the `uv add` command:

```sh
uv add <package-name>
```

For example, to add `requests`:
```sh
uv add requests
```

This will:
- Install the package into your virtual environment
- Add the package to your `pyproject.toml` file
- Update the `uv.lock` file with the exact versions


To add a package with a specific version constraint:
```sh
uv add "numpy>=1.24,<2.0"
```

After adding packages, the changes are automatically synchronized. Other developers can then run `uv sync` to install the newly added dependencies.
