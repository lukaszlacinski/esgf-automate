# esgf-automate
Globus Automate Action Provider For The ESGF Publication Flow

## Basic Install and Testing

Building this project is based on poetry. Make sure you have poetry installed:

```
pip install poetry
```

or

```
pip install pipx
pipx install poetry
```

Then, to get the code installed locally, do:

```
poetry update
poetry install
```

This will create a virtual environment locally. You can test the Action Provider by running:

```
.venv/bin/esgf-extract-local
```

This will start on port 5009. You should be able to see basic information from the Action Provider by running:

```
curl http://localhost:5009/esgf_extract
```

## Testing the Action Methods

To test the Action methods, first, install the Globus Automate Client:

```
pip (or pipx) install globus-automate-client
```

Then try running the Action:

```
globus-automate action run --action-url http://localhost:5009 --body '{"data_path": "", "facets": {}}'
```

You will be prompted to consent with Globus Auth and paste the code into the terminal window.

This should return a result similar to:

```
{
  "action_id": "X2Jaad61WZ1U",
  "completion_time": null,
  "creator_id": "urn:globus:auth:identity:b44bddda-d274-11e5-978a-9f15789a8150",
  "details": {
    "Running": true
  },
  "display_status": "ACTIVE",
  "label": null,
  "manage_by": [],
  "monitor_by": [],
  "release_after": null,
  "start_time": "2021-05-28T12:52:10.157445+00:00",
  "status": "ACTIVE"
}
```

## Building and running with Docker

To help in deployment, the Project is setup to create a Docker image. If you wish to build the image, simply do:

```
docker build -t esgf_extract_ap .
```

After which you an run via Docker as:

```
docker run --publish 5009:5009 esgf_extract_ap
```

This should put you in the same position as the local run script above.

## Developing

On-going development on the Action Provider should be done in the file: esgf_automate/extract_action_provider.py

The skeleton here will perform all authentication and implementation of the Action Provider Interface. At this point, no persistence is in place. It simply emulates persistence with an in-memory dictionary.

