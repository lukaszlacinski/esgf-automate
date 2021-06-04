import logging
import uuid
from typing import Any, Dict, Optional

from flask import Flask
from globus_action_provider_tools import (
    ActionProviderDescription,
    ActionRequest,
    ActionStatus,
    ActionStatusValue,
    AuthState,
)
from globus_action_provider_tools.flask import ActionProviderBlueprint
from globus_action_provider_tools.flask.apt_blueprint import (
    authorize_action_access_or_404,
)
from globus_action_provider_tools.flask.exceptions import ActionNotFound
from globus_action_provider_tools.utils import shortish_id
from globus_sdk import SearchAPIError, SearchClient

from .helpers import iso_tz_now, load_schema
from .persistence import delete_action_by_id, lookup_action_by_id, store_action


log = logging.getLogger(__name__)

GLOBUS_AUTH_CLIENT_ID = "45aa9047-b21d-44c0-8abf-7023b532cb5b"
GLOBUS_AUTH_CLIENT_SECRET = "DdO/n8HAon8Yw0btHm51SeSZzQhpOLdNbAa+8pBhCII="
GLOBUS_AUTH_SCOPE = "https://auth.globus.org/scopes/45aa9047-b21d-44c0-8abf-7023b532cb5b/esgf_extract_action_all"
GLOBUS_AUTH_CLIENT_NAME = "ESGF Demo Metadata Extract Action Provider"

# TODO: ID of the Search Index we write to
SEARCH_INDEX_ID = "aaa-bbbb-ccc-ddd-eee-fff"

ap_description = ActionProviderDescription(
    globus_auth_scope=GLOBUS_AUTH_SCOPE,
    admin_contact="lukasz@globus.org",
    title="ESGF Metadata Extract",
    subtitle="An Action which will extract metadata from an ESGF dataset",
    synchronous=False,
    input_schema=load_schema(__file__),
    log_supported=False,
)


provider_bp = ActionProviderBlueprint(
    name="ESGFMetadataExtract",
    import_name=__name__,
    url_prefix="/esgf_extract",
    provider_description=ap_description,
    globus_auth_client_name=GLOBUS_AUTH_CLIENT_ID,
)


def _get_search_client(auth: AuthState) -> SearchClient:
    search_authorizer = auth.get_authorizer_for_scope(
        "urn:globus:auth:scope:search.api.globus.org:all"
    )
    sc = SearchClient(authorizer=search_authorizer)
    return sc


def _create_mock_metadata(data_path: str, facets: Dict[str, Any]) -> Dict[str, Any]:
    # TODO, Do something to create the metadata for Search
    return {
        "ingest_type": "GMetaEntry",
        "ingest_data": {
            "subject": f"https://esgf.org/{data_path}",
            "visible_to": ["public"],
            "contents": facets,
        },
    }


def format_search_api_exception(exc: SearchAPIError) -> Dict[str, Any]:
    """
    A function that converts a SearchAPIError into a JSON-able structure
    suitable for returning as an Action's details
    """
    return {
        "error": exc.message,
        "search_http_status": exc.http_status,
        "code": exc.code,
        "error_data": exc.error_data,
    }


@provider_bp.action_run
def run_action(request: ActionRequest, auth: AuthState) -> ActionStatus:
    body = request.body
    print(f"Input Body: {body}")
    ingest_data = _create_mock_metadata(body["data_path"], body["facets"])
    sc = _get_search_client(auth)
    try:
        # resp = sc.ingest(SEARCH_INDEX_ID, ingest_data)
        # Mock the search call
        resp = {"acknowledged": True, "data":  {"task_id": str(uuid.uuid4())}}
    except SearchAPIError as e:
        status = ActionStatusValue.FAILED
        result_details = format_search_api_exception(e)
        action_id = shortish_id()
    else:
        if resp["acknowledged"] is True:
            status = ActionStatusValue.ACTIVE
        else:
            status = ActionStatusValue.FAILED
        # result_details = resp.data
        result_details = resp['data']
        action_id = result_details["task_id"]
    action = ActionStatus(
        action_id=action_id,
        status=status,
        display_status=status,
        start_time=iso_tz_now(),
        completion_time=None,
        creator_id=auth.effective_identity,
        monitor_by=request.monitor_by,
        manage_by=request.manage_by,
        details=result_details,
    )
    store_action(action, request, {})

    return action


@provider_bp.action_status
def action_status(action_id: str, auth: AuthState):
    action, request, extra_info = lookup_action_by_id(action_id)
    if action is None:
        raise ActionNotFound(f"No Action with id {action_id} found")
    authorize_action_access_or_404(action, auth)
    # We query Search to determine if the ingest task is complete or not
    sc = _get_search_client(auth)
    search_task_id = action.action_id
    status: Optional[ActionStatusValue] = None
    try:
        # search_task_info = sc.get_task(search_task_id).data
        # Mock the task status call
        search_task_info = {"state": "SUCCESS"}
        if "error" in search_task_info or search_task_info["state"] == "FAILED":
            status = ActionStatusValue.FAILED
            details = {
                "code": "IngestFailed",
                "description": "Unable to ingest data into the Search Index",
                "details": search_task_info,
            }
        elif search_task_info["state"] == "SUCCESS":
            status = ActionStatusValue.SUCCEEDED
            details = search_task_id
    except SearchAPIError as e:
        status = ActionStatusValue.FAILED
        details = format_search_api_exception(e)
    if status is not None:
        action.status = status
        action.display_status = status
        action.details = details
        store_action(action, request, extra_info)
    return action


@provider_bp.action_cancel
def action_cancel(action_id: str, auth: AuthState):
    action, request, extra_info = lookup_action_by_id(action_id)
    # Do work to cancel the action. If cancel is not possible, this method need
    # not be implemented at all
    canceled = False
    if canceled:
        action.status = ActionStatusValue.FAILED
        action.display_status = action.status
        store_action(action, request, extra_info)
    return action


@provider_bp.action_release
def action_release(action_id: str, auth: AuthState):
    action, request, _ = lookup_action_by_id(action_id)
    delete_action_by_id(action_id)
    return action


def create_app() -> Flask:
    app = Flask(__name__)
    app.config[f"{provider_bp.name.upper()}_CLIENT_ID"] = GLOBUS_AUTH_CLIENT_ID
    app.config[f"{provider_bp.name.upper()}_CLIENT_SECRET"] = GLOBUS_AUTH_CLIENT_SECRET
    app.register_blueprint(provider_bp)
    return app


app = create_app()


def main():
    app.run(debug=True, port=5009)


if __name__ == "__main__":
    main()
