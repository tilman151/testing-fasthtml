# Testing FastHTML

This is the companion repository for the [Testing FastHTML Dashboards](https://krokotsch.eu/posts/testing-fasthtml) blog post.

## Installation

This repository uses [uv](https://github.com/astral-sh/uv) for dependency management.
You can install it globally via:

```bash
pipx install uv
```

Afterward, you can set up the environment to run any test via:

```bash
uv run --frozen poe setup_end2end
```

This will install all Python dependencies, ollama, and Chromium for the end-to-end tests.
Alternatively, you can install only the Python dependencies via:

```bash
uv sync --frozen
```

## Running the Tests

First activate the virtual environment via:

```bash
source .venv/bin/activate
```

Then run one of the following commands:

| Command         | Description               |
|-----------------|---------------------------|
| poe unit        | Run all unit tests        |
| poe integration | Run all integration tests |
| poe e2e         | Run all end-to-end tests  |

## Contributing

If you find a bug or want to give feedback, please open an issue or a pull request.
