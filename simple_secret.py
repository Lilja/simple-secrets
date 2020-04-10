#!/usr/bin/env python3
import argparse
import sys
import functools

template_file = "Secretsfile"
secrets_file = ".secrets"


def recursive_get(d, *keys):
    return functools.reduce(lambda c, k: c.get(k, {}), keys, d)


def recursive_set(obj, key, val):
    k = key[0]
    if len(key) > 1:
        if k not in obj:
            obj[k] = {}
        obj[k] = recursive_set(obj[k], key[1:], val)
    else:
        obj[key[0]] = val
    return obj


def parse_secret_value(trimmed_line):
    splitted = trimmed_line.split("=")

    trimmed_value = splitted[1].strip()
    if trimmed_value[0] == '"':
        trimmed_value = trimmed_value[1:]

    if trimmed_value[-1] == '"':
        trimmed_value = trimmed_value[:-1]

    return trimmed_value




def parse_secret_key(trimmed_line):
    return trimmed_line.split("=")[0].strip().split('.')


def understand_secrets_file(secrets_file_contents):
    output = {}

    def validate_line(line):
        if len(line.split('=')) != 2:
            raise Exception('Secrets file corrupt.')

    for line in secrets_file_contents.splitlines():
        trimmed_line = line.strip()

        if trimmed_line:
            if trimmed_line[0] == '#':
                continue
            validate_line(line)
            key = parse_secret_key(trimmed_line)
            val = parse_secret_value(trimmed_line)

            recursive_set(output, key, val)

    return output


def understand_template_file(template_file_contents):

    def _inner():
        for line in template_file_contents.splitlines():
            trimmed_line = line.strip()

            if trimmed_line:

                if trimmed_line[0] == '#':
                    continue
                yield trimmed_line.split('.')

    return list(_inner())


def fail(msg):
    print(msg)
    exit(1)


def open_file_and_print(val, secrets_file):

    with open(secrets_file, 'r') as o:
        obj = understand_secrets_file(o.read())
        ans = recursive_get(obj, *val.split('.'))

        if not ans:
            fail("Secret not found")
        else:
            print(ans)


def write_secrets_file(obj, secrets_file_fo):
    def json_to_txt(context, _obj):
        for (key, value) in _obj.items():
            if type(value) == dict:
                for x in json_to_txt(context + [key], value):
                    yield x
            else:
                key = ((".".join(context)) + '.' + key)
                yield (key + " = " + value)


    for x in [
        "# Internal file for simple_secret. Please use the CLI to change these values.",
        "# For example: simple_secret --set http.port 80"
    ]:
        secrets_file_fo.write('{}\n'.format(x))

    for x in json_to_txt([], obj):
        secrets_file_fo.write('{}\n'.format(x))


def open_file_and_write(key, val):
    with open(secrets_file, 'r') as o:
        obj = understand_secrets_file(o.read())
        recursive_set(obj, key, val)

    with open(secrets_file, 'w') as o:
        write_secrets_file(obj, o)


def prompt_user(key):
    return input("Please enter a value for {}: ".format(key))


def sync():
    missed = False
    secrets = {}
    with open(template_file, 'r') as temp_file:
        templates = understand_template_file(temp_file.read())

        with open(secrets_file, 'r') as o:
            secrets = understand_secrets_file(o.read())

            for template in templates:
                x = recursive_get(secrets, *template)

                if not x:
                    missed = True
                    value = prompt_user('.'.join(template))
                    recursive_set(secrets, template, value)

    if missed:
        with open(secrets_file, 'w') as o:
            write_secrets_file(secrets, o)


def truncate_and_populate():
    secrets = {}
    with open(template_file, 'r') as temp_file:
        templates = understand_template_file(temp_file.read())

        for template in templates:
            x = recursive_get(secrets, *template)

            value = prompt_user('.'.join(template))
            recursive_set(secrets, template, value)

    with open(secrets_file, 'w') as o:
        write_secrets_file(secrets, o)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Secrets hidden from source control')
    parser.add_argument(
        '--get', type=str, help='an integer for the accumulator', action='store'
    )
    parser.add_argument(
        '--configure', help='an integer for the accumulator', action='store_true'
    )
    parser.add_argument(
        '--set', type=str,
        help='an integer for the accumulator', action='store',
        nargs=2
    )
    parser.add_argument(
        '--sync',
        help='an integer for the accumulator', action='store_true',
    )
    args = vars(parser.parse_args())

    if args['get']:
        val = args['get']

        open_file_and_print(args['get'], secrets_file)
    elif args['set']:
        set_key, set_value = args['set']
        open_file_and_write(set_key.split('.'), set_value)
    elif args['sync']:
        sync()
    elif args['configure']:
        truncate_and_populate()
    else:
        raise NotImplemented
