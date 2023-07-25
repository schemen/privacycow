#!/usr/bin/env python3
import configparser
import re
from random import choice, randint, randrange
import socket
from os import environ as env, makedirs
from os.path import isfile, expanduser
from shutil import copyfile

import click
import requests
import texttable
import urllib3.util.connection as urllib3_cn
from faker import Faker
from faker.providers import person
from unidecode import unidecode
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
TEMPLATE = env.get('TEMPLATE')
if not TEMPLATE:
    if RELAY_DOMAIN in config and 'TEMPLATE' in config[RELAY_DOMAIN]:
        TEMPLATE = config[RELAY_DOMAIN]['TEMPLATE']
    else:
        TEMPLATE = None

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

    try:
        r = requests.get(MAILCOW_INSTANCE + API_ENDPOINT, headers=headers, )
        r.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)

    table = texttable.Texttable()
    table.set_deco(texttable.Texttable.HEADER)
    table.set_max_width(0)
    table.header(["ID", "Alias", "Comment", "Active"])

    for i in r.json():
        if i["domain"] == RELAY_DOMAIN:
            if i["goto"] == "null@localhost":
                active = "Discard"
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

    address = generate_realish_name(TEMPLATE) if TEMPLATE is not None else (
        f'{readable_random_string(randint(3, 9))}.'
        f'{readable_random_string(randint(3, 9))}')
    address = f'{address}@{RELAY_DOMAIN}'
    data = {"address":  address,
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
@click.option('-g', '--goto', default=GOTO,
              help='Goto address "mail@example.com". If no option is passed, GOTO env variable or config.ini will be used.')
@click.pass_context
def enable(ctx, alias_id, goto):
    """Enable a alias, which disables "Silently Discard". """
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
        string += choice(CONSONANTS)
        string += choice(VOWELS)
    return string


def generate_realish_name(template):
    """
    generate a real-ish name using faker

    template should be a string containing idenitifying name parts
    in this format:

    {name_part:gender:language}

    name_part should be one of prefix, first_name, last_name, suffix, number
    gender should be f, m or n for female, male or non-binary
    language should be a BCP47 language tag (see: https://www.iana.org/assignments/language-subtag-registry/language-subtag-registry)

    {first_name} would generate a random first name of any gender
    {first_name:f:en-GB} would generate a british english female first name
    {first_name:fr} would generate a french first name
    {first_name:m} would generate a male first name

    if genders are required then it is suggested that the user ensures
    that each name_part is followed by a gender even though they are optional

    if the name_part is number then the user can optionally supply a lower
    and upper range like this: {number:1:100}.  a random integer between the
    lower and upper range will be returned.  if only one range number is
    supplied (for example {number:999}) then the number will be assumed
    to be the upper range with the lower range being 1.  if no numbers
    are provided then the range will be 0 to 1000.
    """

    # define mappings
    gender = {
        'f': '_female',
        'm': '_male',
        'n': '_nonbinary'}
    known = {
        'number': [],
        'prefix': [],
        'first_name': [],
        'last_name': [],
        'suffix': []}

    # find all the parts in the template that need creating
    # these are the parts between the {}
    parts = re.findall(r'{([\w:-]+)}', template)
    for part in parts:
        # split the part by colon
        part = part.split(':')
        name = part[0]
        # if the first part is not a known type then ignore it
        if name not in known.keys():
            continue
        # if we have more than one part then we have genders and
        # languages to consider
        if len(part) > 1:
            sex = gender.get(part[1], '')
            lang = part[1] if not sex else None
            lang = part[2] if (
                lang is None and len(part) > 2) else lang
        else:
            sex = ''
            lang = None

        # create a new fake identity
        try:
            fake = Faker(lang, use_weighting=False)
            fake.add_provider(person)
        except AttributeError:
            fake = Faker(use_weighting=False)

        # generate the fake part
        generated = None
        while generated is None or generated in known[name]:
            if name == 'number':
                if lang is None:
                    if len(part) == 3:
                        range = [int(ppp) for ppp in part[1:]]
                    elif len(part) == 2:
                        range = [0, int(part[1])]
                    else:
                        range = [0, 1000]
                else:
                    range = [int(ppp) for ppp in part]
                range[1] += 1
                generated = str(randrange(*range))
            else:
                generated = getattr(fake, f'{name}{sex}').__call__()
                generated = re.sub(r'[^\w]+', '', generated)
        known[name].append(generated)

        # replace the part in the template
        template = template.replace(f"{{{':'.join(part)}}}", generated, 1)

    # remove accented characters and make lower case
    template = unidecode(template).lower()

    # check the username is valid for an email address
    # see: https://emailregex.com/
    username = re.compile(
        r'(?:[a-z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+/=^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")')
    if not re.fullmatch(username, template):
        raise ValueError(
            'There was an error when generating a real-ish username, '
            'please check the TEMPLATE value in your config file for '
            f'[{RELAY_DOMAIN}] - "{template}" is not valid.')

    # return the re-generated template string
    return template


# Mailcow IPv6 support relies on a docker proxy which in case would nullify the use of the whitelist.
# This patch forces the connection to use IPv4
def allowed_gai_family():
    """
        https://stackoverflow.com/a/46972341
    """
    return socket.AF_INET


urllib3_cn.allowed_gai_family = allowed_gai_family

## Uncomment if you want to use it without installing it
# if __name__ == '__main__':
#     cli()
