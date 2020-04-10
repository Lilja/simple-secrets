# simple\_secret
A tool to use secrets in builds.

Example use.
```
$ ./simple_secret.py --get http.port
80
```

Why use this and not an established tool like [vault](https://www.vaultproject.io/)? My usecase can't be bothered to install a vault instance and maintain it. Simplicity is key.


## Configure

Specify a `Secretsfile` with the following contents:

`http.port`

now run `./simple_secret.py --configure`
```
$ ./simple_secret.py --configure
Please enter a value for http.port: 
```
Specify a value, like 80.
```
$ ./simple_secret.py --configure
Please enter a value for http.port: 80
$ ./simple_secret.py --get http.port
80
$ ./simple_secret.py --set http.port 1234
$ ./simple_secret.py --get http.port
1234
```

The secrets are stored in `.secrets`.


## install

`curl https://raw.githubusercontent.com/Lilja/simple-secrets/master/install.sh | bash -x`
