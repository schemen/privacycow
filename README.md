# privacycow

## Install

```console
python3 -m pip install git+https://github.com/schemen/privacycow.git#egg=privacycow
```

In "developer mode" (editable):


using a virtualenv:
```console
virtualenv venv -p python3
source venv/bin/activate
python -m pip install -e .
```

or
```console
python3 -m venv venv
source venv/bin/activate
python -m pip install git+ssh://git@github.com:schemen/privacycow.git#egg=privacycow
```

```x-sh
git clone https://github.com/schemen/privacycow.git && cd privacycow
virtualenv venv -p python3
source venv/bin/activate
pip install -r requirements.txt
deactivate

# configure your config.ini
# run privacycow once, it will create a samply config file at
# ~/.config/privacycow/config.ini
privacy && vim ~/.config/privacycow/config.ini

```
## Config
Have a look at `config.ini.example` for the sample configuration

```
[DEFAULT]
## Domain used as alias domain. I recommend purchasing a unrelated domain and add it to your
## Mailcow installation. Alternatively you can just use your main domain.
RELAY_DOMAIN = privacycow.com 
# The address mails go to.
GOTO = user@example.com
## Those two settings should be self explanatory
MAILCOW_API_KEY = api_key
MAILCOW_INSTANCE = https://mail.example.com

```

## Usage
```
➜  privacycow     
Usage: privacycow [OPTIONS] COMMAND [ARGS]...

Options:
  --debug / --no-debug
  --help                Show this message and exit.

Commands:
  add      Create a new random alias.
  delete   Delete a alias.
  disable  Disable a alias, done by setting the "Silently Discard" option.
  enable   Enable a alias, which disables "Silently Discard".
  list     Lists all aliases with the configured privacy domain.

```
