from includes.core.globals.entry import app_context


def get_request_value(key, default=None):
    return app_context.request.query_params.get(key, default)
