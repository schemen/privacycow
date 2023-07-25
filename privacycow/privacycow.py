#!/usr/bin/env python3
import configparser
import random
import socket
from os import environ as env, makedirs
from os.path import isfile, expanduser
from shutil import copyfile

import click
import requests
import texttable
import urllib3.util.connection as urllib3_cn
from pkg_resources import Requirement, resource_filename


def read_config(file):
    config = configparser.ConfigParser()
    config.read(file)
    return config


config_path = expanduser('~/.config/privacycow/')

if isfile(config_path + "config.ini"):
    config = read_config(config_path + "config.ini")
else:
    makedirs(config_path, exist_ok=True)
    samplefile = resource_filename(Requirement.parse("privacycow"), "privacycow/config.ini.example")
    copyfile(samplefile, config_path + "config.ini")
    config = read_config(config_path + "config.ini")
    click.echo("Privacycow ran for the first time.\nMake sure you check your config file at %s" % config_path + "config.ini")

RELAY_DOMAIN = env.get('RELAY_DOMAIN', config['DEFAULT']['RELAY_DOMAIN'])
MAILCOW_API_KEY = env.get('MAILCOW_API_KEY')
if not MAILCOW_API_KEY:
    if RELAY_DOMAIN in config and 'MAILCOW_API_KEY' in config[RELAY_DOMAIN]:
        MAILCOW_API_KEY = config[RELAY_DOMAIN]['MAILCOW_API_KEY']
    else:
        MAILCOW_API_KEY = config['DEFAULT']['MAILCOW_API_KEY']
MAILCOW_INSTANCE = env.get("MAILCOW_INSTANCE")
if not MAILCOW_INSTANCE:
    if RELAY_DOMAIN in config and 'MAILCOW_INSTANCE' in config[RELAY_DOMAIN]:
        MAILCOW_INSTANCE = config[RELAY_DOMAIN]['MAILCOW_INSTANCE']
    else:
        MAILCOW_INSTANCE = config['DEFAULT']['MAILCOW_INSTANCE']
GOTO = env.get('GOTO')
if not GOTO:
    if RELAY_DOMAIN in config and 'GOTO' in config[RELAY_DOMAIN]:
        GOTO = config[RELAY_DOMAIN]['GOTO']
    else:
        GOTO = config['DEFAULT']['GOTO']


VOWELS = "aeiou"
CONSONANTS = "bcdfghjklmnpqrstvwxyz"


@click.group()
@click.option('--debug/--no-debug')
@click.pass_context
def cli(ctx, debug, ):
    ctx.ensure_object(dict)
    ctx.obj['DEBUG'] = debug
    if debug:
        click.echo("Debug is enabled")


@cli.command()
@click.pass_context
def list(ctx):
    """Lists all aliases with the configured privacy domain."""
    API_ENDPOINT = "/api/v1/get/alias/all"
    headers = {'X-API-Key': MAILCOW_API_KEY}
    possible_domains = [RELAY_DOMAIN] + [ccc for ccc in config.sections() if ccc != RELAY_DOMAIN]

    try:
        r = requests.get(MAILCOW_INSTANCE + API_ENDPOINT, headers=headers, )
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    table = texttable.Texttable()
    table.set_deco(texttable.Texttable.HEADER)
    table.set_max_width(0)
    table.header(["ID", "Alias", "Comment", "Status"])

    for i in r.json():
        if i["domain"] in possible_domains:
            if i["goto"] == "null@localhost":
                active = "Discard"
            elif i["goto"] == "spam@localhost":
                active = "Spam"
            else:
                active = "Active"

            table.add_row([i["id"], i["address"], i["public_comment"], active])

    click.echo(table.draw())


@cli.command()
@click.option('-g', '--goto', default=GOTO,
              help='Goto address "mail@example.com". If no option is passed, GOTO env variable or config.ini will be used.')
@click.option('-c', '--comment', default=None,
              help='Public Comment string, use "service description" as an example. If no option is passed, comment will be empty.')
@click.pass_context
def add(ctx, goto, comment):
    """Create a new random alias."""
    API_ENDPOINT = "/api/v1/add/alias"
    headers = {'X-API-Key': MAILCOW_API_KEY}

    data = {"address": readable_random_string(random.randint(3, 9)) + "."
                       + readable_random_string(random.randint(3, 9)) + "@" + RELAY_DOMAIN,
            "goto": goto,
            "public_comment": comment,
            "active": 1}

    try:
        r = requests.post(MAILCOW_INSTANCE + API_ENDPOINT, headers=headers, json=data)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    data = r.json()

    click.echo("Success! The following Alias has been created:")
    click.echo("Alias ID:       %s" % data[0]["msg"][2])
    click.echo("Alias Email:    %s" % data[0]["msg"][1])
    click.echo("Alias Comment:  %s" % data[0]["log"][3]["public_comment"])


@cli.command()
@click.argument('alias_id')
@click.pass_context
def disable(ctx, alias_id):
    """Disable a alias, done by setting the "Silently Discard" option. """
    API_ENDPOINT = "/api/v1/edit/alias"
    headers = {'X-API-Key': MAILCOW_API_KEY}

    data = {"items": [alias_id], "attr": {"goto_null": "1"}}

    try:
        r = requests.post(MAILCOW_INSTANCE + API_ENDPOINT, headers=headers, json=data)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    data = r.json()

    click.echo("Success! The following Alias disabled:")
    click.echo("Alias ID:       %s" % data[0]["log"][3]["id"][0])
    click.echo("Alias Email:    %s" % data[0]["msg"][1])


@cli.command()
@click.argument('alias_id')
@click.pass_context
def spam(ctx, alias_id):
    """Mark all email sent to an alias as spam."""

    API_ENDPOINT = f"/api/v1/get/alias/{alias_id}"
    headers = {'X-API-Key': MAILCOW_API_KEY}

    try:
        r = requests.get(MAILCOW_INSTANCE + API_ENDPOINT, headers=headers, )
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    API_ENDPOINT = "/api/v1/edit/alias"
    data = {
        "items": [alias_id],
        "attr": {
            "goto_spam": "1",
            "public_comment": (
                f'spam ({r.json()["public_comment"]})')}}

    try:
        r = requests.post(MAILCOW_INSTANCE + API_ENDPOINT, headers=headers, json=data)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    data = r.json()

    click.echo("Success! The following Alias now collects spam:")
    click.echo("Alias ID:       %s" % data[0]["log"][3]["id"][0])
    click.echo("Alias Email:    %s" % data[0]["msg"][1])
    click.echo("Alias Comment:  %s" % data[0]["log"][3]["public_comment"])


@cli.command()
@click.argument('alias_id')
@click.option('-g', '--goto', default=GOTO,
              help='Goto address "mail@example.com". If no option is passed, GOTO env variable or config.ini will be used.')
@click.pass_context
def enable(ctx, alias_id, goto):
    """Enable a alias, stop discarding email or collecting spam. """
    API_ENDPOINT = "/api/v1/edit/alias"
    headers = {'X-API-Key': MAILCOW_API_KEY}

    data = {"items": [alias_id], "attr": {"goto": goto}}

    try:
        r = requests.post(MAILCOW_INSTANCE + API_ENDPOINT, headers=headers, json=data)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    data = r.json()

    click.echo("Success! The following Alias enabled:")
    click.echo("Alias ID:       %s" % data[0]["log"][3]["id"][0])
    click.echo("Alias Email:    %s" % data[0]["msg"][1])


@cli.command()
@click.argument('alias_id')
@click.pass_context
def delete(ctx, alias_id):
    """Delete a alias."""

    API_ENDPOINT = "/api/v1/delete/alias"
    headers = {'X-API-Key': MAILCOW_API_KEY}

    data = [alias_id]

    try:
        r = requests.post(MAILCOW_INSTANCE + API_ENDPOINT, headers=headers, json=data)
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    data = r.json()

    click.echo("Success! The following Alias has been deleted:")
    click.echo("Alias ID:       %s" % data[0]["log"][3]["id"][0])
    click.echo("Alias Email:    %s" % data[0]["msg"][1])


def readable_random_string(length: int) -> str:
    string = ''
    for x in range(int(length / 2)):
        string += random.choice(CONSONANTS)
        string += random.choice(VOWELS)
    return string


# Mailcow IPv6 support relies on a docker proxy which in case would nullify the use of the whitelist.
# This patch forces the connection to use IPv4
def allowed_gai_family():
    """
        https://stackoverflow.com/a/46972341
    """
    return socket.AF_INET


urllib3_cn.allowed_gai_family = allowed_gai_family

## Uncomment if you want to use it without installing it
#if __name__ == '__main__':
#    cli()
