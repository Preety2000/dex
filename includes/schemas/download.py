from includes.utils._sub import configure_page
from includes.core.globals.entry import app_context


class ClassDownload:

    @staticmethod
    def index():
        configure_page(
            template="widget/app_download", title="Download App", suffix=True
        )
        return "widget/app_download"
        return []
