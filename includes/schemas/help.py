from includes.utils._sub import configure_page
from includes.core.globals.entry import app_context
from includes.database.connection import db


class Help:
    def __init__(self, request, params):
        request.state.response = params
        self.request = request
        self.session = db
        self.function = app_context.function

    def index(self, subresource, detail):

        if subresource:
            configure_page(
                request.state.metadata,
                template=f"page/{subresource}",
                title=subresource,
                suffix=True,
            )
            return

        configure_page(
            request.state.metadata, template="page/help", title="Help", suffix=True
        )
        return
