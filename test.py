import simple_secret as s
from unittest import mock


def test_recursive_get():
    obj = {
        "hello": "hej",
        "nested": {
            "test": True
        }

    }
    assert s.recursive_get(obj, 'hello2') == {}
    assert s.recursive_get(obj, 'hello') == "hej"

    assert s.recursive_get(obj, *['nested', 'test']) == True

def test_recursive_set():
    obj = {}
    assert s.recursive_set(obj, ['hello2'], 'Lol')
    assert obj['hello2'] == 'Lol'

    assert s.recursive_set(obj, ['hello', 'test'], 1)
    assert obj['hello']['test'] == 1

    assert s.recursive_set(obj, ['hello', 'test2'], 5)
    assert obj['hello']['test2'] == 5


def test_secrets_file():
    understand_secrets_file = """
    a.b.c = 5
    a.b.d = asdf
    a.b.e="foo"
    a.b.f = "foo"
    """

    output = s.understand_secrets_file(understand_secrets_file)

    assert output['a']['b']['c'] == '5'
    assert output['a']['b']['d'] == "asdf"
    assert output['a']['b']['e'] == "foo"
    assert output['a']['b']['f'] == "foo"


def test_template_file():
    template_file = """
    a.b.c
    a.b.d
    a.b.e
    a.b.f
    """

    output = s.understand_template_file(template_file)

    assert output[0] == ['a', 'b', 'c']
    assert output[1] == ['a', 'b', 'd']
    assert output[2] == ['a', 'b', 'e']
    assert output[3] == ['a', 'b', 'f']



def test_write_secrets_file():
    secrets_file_fo = mock.Mock()
    output = {'a': {"b": {"c": "d"}}}
    s.write_secrets_file(output, secrets_file_fo)

    print(secrets_file_fo.write.call_args_list[0])
    assert secrets_file_fo.write.call_count == 3
    expected = [
        '# Internal file for simple_secret. Please use the CLI to change these values.\n',
        '# For example: simple_secret --set http.port 80\n',
        'a.b.c = d\n',
    ]
    for (idx, (args, _)) in enumerate(secrets_file_fo.write.call_args_list):
        assert args[0] == expected[idx]

