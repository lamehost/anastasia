# Anastasia

# EVERYTHING BELOW THIS LINE IS OUTDATED

Antastia is a  **VERY** minimalistic REST interface for image upload that mimics [some of imgur's methods](https://apidocs.imgur.com/#58306db8-0a6f-4aa1-a021-bdad565f153e).

## Methods
| Methods | Headers | Attibute |
|---------|---------|----------|
| GET | None | fileName |
| DELETE | Authorization | fileName |
| POST | Authorization | fileName |

## Headers
 - Authorization: Client-ID *client_id*

## Syntax
```
usage: anastasia [-h] [-c FILE]

optional arguments:
  -h, --help            show this help message and exit
  -c FILE, --config FILE
                        configuration filename (default: anastasia.cfg)
```

## Configuration
Configuration file is YAML based and loaded at startup.
Default name is *anastasia.cfg* .

## Configuration directives
- client_ids: List of allowed client_id (default: False)
- folder: Folder where images will be stored (default: *images/*)
- port: Port to bind to (ignored with WSGI, default: 8000)
- host: Host to bind to (ignored with WSGI, default: localhost)

### Sample configuration file
```
client_ids:
 - nf9832fn2f9e
folder: images/

# Ignored with WSGI
port: 8000
host: localhost
```

