from includes.utils._sub import configure_page
from includes.core.globals.entry import app_context


class Help:
    def __init__(self, request, params):
        app_context.response = params
        self.request = request
        self.session = app_context.db
        self.function = app_context.function

    def index(self, subresource, detail):

        if subresource:
            configure_page(template=f"page/{subresource}", title=subresource, suffix=True)
            return

        configure_page(template="page/help", title="Help", suffix=True)
        return
