# Welcome to Jibril's repo

Thank you for investing your time in contributing to Jibril. In this document, you will find everything you need to get started on contributing to Jibril, a Discord bot for chess players.

## Getting started

First, clone the repository with `git clone https://github.com/eniraa/jibril.git`. Afterwards, set your current directory to the directory the repo was cloned in.

Jibril uses Poetry to manage dependencies. You can install it [here](https://python-poetry.org/docs/#installation).

After installing Poetry, simply run `poetry install` to install all dependencies. If something does not work, make sure that you are using Python 3.10. You can force Poetry to use this version if you have it installed via `poetry env use 3.10`, but otherwise, install Python 3.10 [here](https://www.python.org/downloads/).

After installing dependencies, make sure to set up pre-commit hooks. This repository comes with a simple command—`poetry run task precommit`—for ease of use.

### Issues

Should you ever come across a bug, please create an issue [here](https://github.com/eniraa/jibril/issues). Feature requests should also be made here. Please make sure to check that your issue is not a duplicate.

### Changes

Changes should ideally be done in their own branch or fork. Make sure that your commit messages are accurate but concise. After finishing a specific change, open a pull request [here](https://github.com/eniraa/jibril/pulls) and wait for approval, making changes if necessary. Changes are first merged into the [`dev` branch](https://github.com/eniraa/jibril/tree/dev), and after a certain milestone is reached, those changes will be merged into the [`master` branch](https://github.com/eniraa/jibril/tree/master).

Keep in mind that Jibril follows [black](https://black.readthedocs.io/en/stable/the_black_code_style/current_style.html)'s coding style, and enforces other checks such as sorted imports and flake8. Use `poetry run task reformat` to reformat your code to comply with black and isort, and use `poetry run task lint` after staging changes to check for linter compliance.
