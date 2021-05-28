
import logging

from flask import Flask
from globus_action_provider_tools import (ActionProviderDescription,
    ActionRequest, ActionStatus, ActionStatusValue, AuthState)
from globus_action_provider_tools.flask import ActionProviderBlueprint

from .helpers import iso_tz_now, load_schema
from .persistence import store_action, lookup_action_by_id, delete_action_by_id

log = logging.getLogger(__name__)

GLOBUS_AUTH_CLIENT_ID = "45aa9047-b21d-44c0-8abf-7023b532cb5b"
GLOBUS_AUTH_CLIENT_SECRET = "DdO/n8HAon8Yw0btHm51SeSZzQhpOLdNbAa+8pBhCII="
GLOBUS_AUTH_SCOPE = "https://auth.globus.org/scopes/45aa9047-b21d-44c0-8abf-7023b532cb5b/esgf_extract_action_all"
GLOBUS_AUTH_CLIENT_NAME = "ESGF Demo Metadata Extract Action Provider"


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

@provider_bp.action_run
def run_action(request: ActionRequest, auth: AuthState) -> ActionStatus:
    action = ActionStatus(
        status=ActionStatusValue.ACTIVE,
        display_status=ActionStatusValue.ACTIVE,
        start_time=iso_tz_now(),
        completion_time=None,
        creator_id=auth.effective_identity,
        monitor_by=request.monitor_by,
        manage_by=request.manage_by,
        details={"Running": True}
    )
    store_action(action, request, {})
    return action

@provider_bp.action_status
def action_status(action_id: str, auth: AuthState):
    action, request, extra_info = lookup_action_by_id(action_id)
    # Do any polling or other work to update the status. Dummy result with the
    # simple work_done value here
    work_done = False
    if work_done:
        action.status = ActionStatusValue.SUCCEEDED
        action.display_status = action.status
        # If GMeta can be captured in a few KB, we can add the following
        action.details = {
            "GMetaEntries": []
        }
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

if __name__ == '__main__':
    main()
