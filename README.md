# privacycow

## Install

```console
python3 -m pip install git+https://github.com/schemen/privacycow.git#egg=privacycow
```

### In "developer mode" (editable):


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

```

### First run, Adjust settings, see options further down

```
# configure your config.ini
# run privacycow once, it will create a sample config file at
# ~/.config/privacycow/config.ini
privacycow && vim ~/.config/privacycow/config.ini

```
## Config
Have a look at `config.ini.example` for the sample configuration

```
[DEFAULT]
# The default domain used as an alias domain. I recommend purchasing an
# unrelated domain and adding it to your Mailcow installation. Alternatively
# you can just use your main domain.
RELAY_DOMAIN = example.com
# The address emails will go to if a GOTO is not defined in the
# [$RELAY_DOMAIN] settings section.
GOTO = user@example.com
# These two settings should be self explanatory and will be used if
# there is not a MAILCOW_API_KEY or MAILCOW_INSTANCE setting in the
# [$RELAY_DOMAIN] settings section.
MAILCOW_API_KEY = api_key
MAILCOW_INSTANCE = https://mail.example.com

[example.com]
# The settings to be used when example.com is RELAY_DOMAIN.  RELAY_DOMAIN
# in the [DEFAULT] section is defining this section as the default.
# All three parameters are optional here as if they are not defined
# the setting from DEFAULT will be used instead.
GOTO = another@example.com
MAILCOW_API_KEY = another_api_key
MAILCOW_INSTANCE = https://mail.example.com

[example.org]
# These settings can be used by calling privacycow like this:
# RELAY_DOMAIN=example.org privacycow list
GOTO = user@example.org
# Note we have chosen not to define MAILCOW_API_KEY and
# MAILCOW_INSTANCE here so the values in [DEFAULT] will be used instead.


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
  enable   Enable a alias, stop discarding email or collecting spam.
  list     Lists all aliases with the configured privacy domain.
  spam     Mark all email sent to an alias as spam.

```


## Examples

```
➜  privacycow add -c "terrible place"
Success! The following Alias has been created:
Alias ID:       29
Alias Email:    5b25SxYx9J46lJjk.YVuONdYUUA3ekAgU@example.com
Alias Comment:  terrible place


➜  privacycow disable 29
Success! The following Alias disabled:
Alias ID:       29
Alias Email:    5b25SxYx9J46lJjk.YVuONdYUUA3ekAgU@privacyfwd.ch



➜  privacycow list
ID                        Alias                           Comment       Status
===============================================================================
22   pQf6qmgMxpa8C.c1Q3sdpDZarqf4ggCe2@example.com  bad actor        Active
28   mX4WjTjHcJwa96Vk.xEKpPKbgArysoWvg@example.com  test             Active
29   5b25SxYx9J46lJjk.YVuONdYUUA3ekAgU@example.com  terrible place   Discard


➜  privacycow spam 28
Success! The following Alias now collects spam:
Alias ID:       28
Alias Email:    mX4WjTjHcJwa96Vk.xEKpPKbgArysoWvg@example.com


➜  privacycow list
ID                        Alias                           Comment       Status
===============================================================================
22   pQf6qmgMxpa8C.c1Q3sdpDZarqf4ggCe2@example.com  bad actor        Active
28   mX4WjTjHcJwa96Vk.xEKpPKbgArysoWvg@example.com  spam (test)      Spam
29   5b25SxYx9J46lJjk.YVuONdYUUA3ekAgU@example.com  terrible place   Discard


```
