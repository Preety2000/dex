from includes.utils._sub import configure_page
from includes.src.request import Request


class ClassDownload:

    def __init__(self, request: Request):
        self.request = request

    def index(self):
        configure_page(
            self.request.state.metadata,
            template="widget/app_download",
            title="Download App",
            suffix=True,
        )
        return "widget/app_download"
