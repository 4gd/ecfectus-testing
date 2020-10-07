## Note about Python:

As if often the case, multiple Python versions can be installed at once
on your OS.  This means that there can be multiple binaries, each
corresponding to completely different Python versions at once.

For example:
- `python` can be `2.7`
- `python3` can be `3.6.3`
- `python3.7` can be `3.7.8`

It's up to you with how you manage your Python install, but it is
recommended (on macOS) to use `pyenv`.  See `pyenv` docs for
installation.

## Preliminary

Ensure Python 3 is installed and up-to-date (tested with `3.7.8`;
replace `python` with the correct binary file):
- `python --version`

## Setup

Based on the above, make sure to use the correct Python binary in place
of `python` below.  E.g.: if `python` is actually version `2.7`, but
`python3` is correct, use `python3 -m venv venv`.

- Create and activate venv:
  - `python -m venv venv`
  - `source venv/bin/activate`
- You should now see `(venv)` at the start of your command line, e.g.:
```
(venv) X-Machina:ecfectus-testing barto$
```
- When working inside a Python virtual environment, the `python` binary
is no longer under `/usr/bin` (or wherever it was in the first place);
it's inside your `venv/bin` directory.
- If `venv` was activated correctly, the `python` binary should now
point to the correct Python 3 version, so you can follow the commands
below exactly as written.
- `cp .env.default .env`
- Add the backend's API URL to the `.env` file ("ws://..."). Make sure
to leave `ws://` at the beginning.
- Install all libraries and their dependencies:
  -`python -m pip install -r requirements.txt`

## Execution

Ignore if `venv` is already activated:

Make sure you have activated the `venv`. It is active if you see
`(venv)` at the start of your command line.  If you don't do this, you
will be using the wrong Python binary file and will be missing
dependencies:
- `source venv/bin/activate`

You can now run the test session:
- `python dummy_session.py`

