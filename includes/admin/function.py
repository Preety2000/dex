from includes.core.globals.entry import app_context


class Function:
    def __init__(self, state):

        self.request = app_context.request
        self.function = app_context.function

    def filter(self, query, table, limit=None):
        if limit:
            (
                new_query_lists,
                app_context.params.paginator,
                app_context.params.results,
            ) = self.function.paginator(query, limit, table)
        else:
            new_query_lists = query.all()

        return new_query_lists
