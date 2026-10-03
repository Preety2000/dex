import json
from fastapi.responses import FileResponse
from flask import Request
from sqlalchemy import inspect, text

from includes.db.connection import (
    active_exam_db,
    active_primary_db,
    active_secondary_db,
)
from includes.db.models.owner import Members
from includes.core.globals.entry import app_context
from includes.utils.utils import get_query_value, get_referer_value


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

    db_count = get_query_value("db", get_referer_value("db", None))

    db = await {
        "1": active_primary_db,
        "2": active_secondary_db,
        "3": active_exam_db,
    }.get(str(db_count), active_primary_db)()

    inserted = 0
    updated = 0
    skipped = 0

    try:
        inspector = inspect(db.bind)
        existing_tables = inspector.get_table_names()

        for table_name, table_data in result.items():

            if table_name not in existing_tables:
                skipped += 1
                continue

            columns = table_data["columns"]
            rows = table_data["rows"]

            if not rows or "id" not in columns:
                skipped += 1
                continue

            update_columns = [column for column in columns if column != "id"]

            for row in rows:

                row_id = row["id"]

                check_query = text(f"""
                    SELECT 1
                    FROM "{table_name}"
                    WHERE "id" = :id
                    LIMIT 1
                """)

                existing = (db.execute(check_query, {"id": row_id})).first()

                if existing:

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
                        updated += 1

                else:

                    column_names = ", ".join(f'"{column}"' for column in columns)

                    placeholders = ", ".join(f":{column}" for column in columns)

                    insert_query = text(f"""
                        INSERT INTO "{table_name}"
                        ({column_names})
                        VALUES ({placeholders})
                    """)

                    db.execute(insert_query, row)
                    inserted += 1

        db.commit()

        return {
            "success": True,
            "inserted": inserted,
            "updated": updated,
            "skipped": skipped,
            "total": inserted + updated,
        }

    except Exception:
        db.rollback()
        raise


async def download_db_data(root, templates, request: Request):
    if "upload" == app_context.route.scope_slug:
        return templates.TemplateResponse(
            request=request,
            name="upload_db.html",
        )

    db_count = get_query_value("db")

    db = await {
        "1": active_primary_db,
        "2": active_secondary_db,
        "3": active_exam_db,
    }.get(str(db_count), active_primary_db)()

    result = await export_database(db)

    if "download" == app_context.route.scope_slug:
        file_path = "database_backup.json"

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2, default=str)

        return FileResponse(
            path=file_path, filename="database.json", media_type="application/json"
        )

    if "view" == app_context.route.scope_slug:
        return result

    else:
        return "File not found or invalid route. Please check the URL and try again."
