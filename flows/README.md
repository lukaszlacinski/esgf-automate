# Flow Definition for the ESGF Ingest / Index Demo

The file `esgf_ingest_flow.json` contains the Flow definition. At present, the flow contains 3 steps:

1. Transfer data from one Globus Endpoint to another. The endpoints and paths are specified in the Input when the Flow is run (see below).

2. Perform the Metadata extract and indexing. The parameters to this are the destination path where the Transfer step deposited the data, and the facets provided as input to the Flow (see below).

3. Email the user who submitted the Flow execution. There are lots of customizations to do here including the sender email address, the text of the message, and the credentials for sending the message. The text can be templated with other values we know in the flow, such as the destination path, or anything that might be returned from the extract step, so if you want a guide on updating text with templating, let me know.

The file `input_schema.json` contains a schema which will validate the input being passed to the Flow when it is run. The input upon running the Flow will be required to pass this validation or the run request will be rejected. Briefly, the schema specifies input of the form:

```
{
  "source_endpoint_id": "<uuid of source endpoint (from user)",
  "destination_endpoint_id": "<uuid of the destination endpoint for the transfer on the data node",
  "source_folder_path": "<path to a FOLDER on source_endpoint_id where the user's data resides>",
  "destination_folder_path": "<path on the destination where the source folder should be copied>",
  "facets": {
    "facet1": "value1",
    "facet2": "value2",
    ...
  }
}
```

