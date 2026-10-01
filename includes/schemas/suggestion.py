from includes.core.globals.entry import app_context


class ClassSuggestion:
    def __init__(self):
        self.request = app_context.request
        self.function = app_context.function
