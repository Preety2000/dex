import json
from fastapi.responses import FileResponse
from flask import Request
from sqlalchemy import inspect, text

from includes.db.connection import active_primary_db
from includes.db.models.owner import Members
from includes.core.globals.entry import app_context


async def export_database(db):

    inspector = inspect(db.bind)
    result = {}
    for table_name in inspector.get_table_names():

        columns_info = inspector.get_columns(table_name)
        columns = [column["name"] for column in columns_info]
        query = text(f'SELECT * FROM "{table_name}"')
        rows = db.execute(query).mappings().all()
        result[table_name] = {"columns": columns, "rows": [dict(row) for row in rows]}

    return result


async def import_database(root, result):

    db = await active_primary_db()
    try:
        inspector = inspect(db.bind)
        existing_tables = inspector.get_table_names()

        for table_name, table_data in result.items():

            if table_name not in existing_tables:
                continue

            columns = table_data["columns"]
            rows = table_data["rows"]

            if not rows or "id" not in columns:
                continue

            # id ko chhodkar update hone wale columns
            update_columns = [column for column in columns if column != "id"]

            for row in rows:

                row_id = row["id"]

                # Check ID exists
                check_query = text(f"""
                    SELECT 1
                    FROM "{table_name}"
                    WHERE "id" = :id
                    LIMIT 1
                    """)

                existing = (db.execute(check_query, {"id": row_id})).first()

                if existing:

                    # UPDATE
                    if update_columns:

                        set_clause = ", ".join(
                            f'"{column}" = :{column}' for column in update_columns
                        )

                        update_query = text(f"""
                            UPDATE "{table_name}"
                            SET {set_clause}
                            WHERE "id" = :id
                            """)

                        db.execute(update_query, row)

                else:

                    # INSERT
                    column_names = ", ".join(f'"{column}"' for column in columns)

                    placeholders = ", ".join(f":{column}" for column in columns)

                    insert_query = text(f"""
                        INSERT INTO "{table_name}"
                        ({column_names})
                        VALUES ({placeholders})
                        """)

                    db.execute(insert_query, row)

        db.commit()

    except Exception:
        db.rollback()
        raise


async def download_db_data(root, templates, request: Request):
    if "upload" == app_context.route.scope_slug:
        return templates.TemplateResponse(
            request=request,
            name="upload_db.html",
        )

    db = await active_primary_db()
    result = await export_database(db)

    if "download" == app_context.route.scope_slug:
        file_path = "backup.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)

        return FileResponse(
            path=file_path, filename="database.json", media_type="application/json"
        )

    if "view" == app_context.route.scope_slug:
        return result

    else:
        return "File not found or invalid route. Please check the URL and try again."
