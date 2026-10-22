from includes.core.globals.entry import app_context


class Function:
    def filter(self, query, table, limit=None):
        if limit:
            (
                new_query_lists,
                app_context.params.paginator,
                app_context.params.results,
            ) = app_context.function.paginator(query, limit, table)
        else:
            new_query_lists = query.all()

        return new_query_lists
