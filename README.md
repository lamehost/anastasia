# Anastasia

Anastasia is a **VERY** minimalist REST API that mimics [some of imgur's methods](https://apidocs.imgur.com/#de179b6a-3eda-4406-a8d7-1fb06c17cb9c).

## Methods
| Method | Path | Headers | In-Path attibute | Body | Returns |
|--------|------|---------|------------------|------|---------|
| GET | /api/3/image/{image_hash} | image_hash | None | Image file |
| DELETE | /api/3/image/{image_hash} | None | image_hash | None | None |
| POST | /api/3/upload | None | None | Image file | JSON with meta |

## Syntax
```
usage: anastasia
```

## Configuration
Configuration is provided in 2 ways depending on the component you want to configure:
 * **API configuration**: Provided via .env file named **anastasia.cfg**
 * **Uvicorn**: Provided via environment variables

### API configuration directives:
- **folder**: Path to the folder where images are stored
- **contact_name**: App administrator's name. The value will show up on the swagger GUI
- **contact_url**: App administrator's website. The value will show up on the swagger GUI
- **contact_email**: App administrator's email address. The value will show up on the swagger GUI
- **enable_gui**: If set, enables the webgui at root path.
- **enable_docs**: If set, enables API docs at `/api/docs/`

#### Sample .env file
```
# Image folder
folder=images/

# API frontend stuff
contact_name="Average Joe"
contact_url="http://www.example.com"
contact_email="averagejoe@example.com"

# Activate GUI
# enable_gui=true

# Activate API docs
# enable_docs=true

# Baseurl for API response (usefull in case your app is behind a load balancer)
# baseurl="https://www.example.com/"
```

### Uvicorn configuration directives:
 - **ANASTASIA_HOST**: IP Address to bind to (default: 0.0.0.0)
 - **ANASTASIA_PORT**: TCP port to bind to (default: 8000)
 - **ANASTASIA_DEBUG**: If set, turns uvicorn debug on (default: disabled)
 - **ANASTASIA_ENV**: Environment configuration file for Anastasia (see above)

## Docker
In order to run Anastasia within docker you have to mount the .env file and publish the port:
```
docker run -it --rm -p 80:8000 -v $(pwd)/anastasia.cfg:/anastasia.cfg  -v $(pwd)/images:/images anastasia
```
