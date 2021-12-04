# Jibril

[![Quality Check](https://github.com/eniraa/jibril/actions/workflows/quality.yml/badge.svg)](https://github.com/eniraa/jibril/actions/workflows/quality.yml)
[![Python](https://img.shields.io/static/v1?label=Python&message=3.10&color=blue&logo=Python&style=flat)](https://www.python.org/downloads/)
[![License](https://img.shields.io/github/license/eniraa/jibril?style=flat)](./LICENSE)
[![Code Style](https://img.shields.io/static/v1?label=code%20style&message=black&color=000000&style=flat)](https://github.com/psf/black)
[![FOSSA Status](https://app.fossa.com/api/projects/custom%2B26877%2Fgithub.com%2Feniraa%2Fjibril.svg?type=small)](https://app.fossa.com/projects/custom%2B26877%2Fgithub.com%2Feniraa%2Fjibril?ref=badge_small)

![Jibril](https://doggo.ninja/EDdDZE.png)

A Discord bot for chat games.

## Features

Jibril is still in its infancy. Much of the planned functionality is not yet implemented. Please see the wiki for more information on Jibril's functionality.

## Running

Make sure that you set environment variables before running Jibril. The easiest way to do so would be to use a `.env` file. Here is a sample `.env` file:

```ini
# don't worry! this token is not real.
DISCORD_TOKEN=XeTRS2sRfzcVVrLlbjS2amyV.r3HTBg.By28qXEAH0DWDFVD1KZpMuIwxc8
# comma delimited guild id's, this is for guild-specific commands for quick debugging. omit this line in production.
HOME_GUILDS=899204296275550249,715607808028049459
# channel id for uploading attachments. discord likes to prohibit attachments in slash commands, so this is a workaround.
UPLOAD_CHANNEL=915256113841180732
```

Jibril uses [Poetry](https://python-poetry.org/docs/#installation) to manage dependencies. After installing Poetry, simply run `poetry install` to install all dependencies. If something does not work, make sure that you are using Python 3.10. You can force Poetry to use this version if you have it installed via `poetry env use 3.10`, but otherwise, install [Python 3.10](https://www.python.org/downloads/). After this, simply run `poetry shell` to enter the the virtual environment, and then run `python jibril/main.py`.

Alternatively, a Dockerfile is provided in the repository. You can run Jibril in a Docker container by running `docker build -t jibril .` and then `docker run --env-file  .env jibril`.

## Authors

- eniraa ([エニラ#9201](https://canary.discord.com/users/393172660630323200))
- Alijradi2003 ([A07 King's Indian Attack#1320](https://canary.discord.com/users/660929334969761792))

## License

Jibril uses the GPLv3 license. See the LICENSE file for more information.
