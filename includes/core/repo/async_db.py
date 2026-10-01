import os
from fastapi.responses import FileResponse
import aiosqlite
from io import BytesIO
from fastapi import HTTPException
# pip install svglib reportlab
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from io import BytesIO


ALLOWED_EXTENSIONS = {
    "images": {"png", "jpg", "jpeg", "gif"},
    "svg": {"svg"},
    "pdf": {"pdf"},
    "videos": {"mp4", "webm"},
    "audios": {"mp3", "mp4"},
}

# Dictionary to map MIME types to category
mime_types = {
    "image": [
        "image/jpeg",  # JPEG image
        "image/png",  # PNG image
        "image/gif",  # GIF image
        "image/bmp",  # BMP image
        "image/tiff",  # TIFF image
        "image/svg+xml",  # SVG image
        "image/webp",  # WebP image
        "image/ico",  # ICO image
        "image/heif",  # HEIF image
        "image/heic",  # HEIC image
    ],
    "video": [
        "video/mp4",  # MPEG-4 Video
        "video/webm",  # WebM Video
        "video/ogg",  # Ogg Video
        "video/avi",  # Audio Video Interleave
        "video/mpeg",  # MPEG Video
        "video/quicktime",  # QuickTime Video
        "video/x-msvideo",  # Microsoft Video
        "video/x-ms-wmv",  # Windows Media Video
        "video/x-flv",  # Flash Video
        "video/3gpp",  # 3GPP Video
        "video/3gpp2",  # 3GPP2 Video
        "video/x-matroska",  # Matroska Video
        "video/x-m4v",  # M4V Video
    ],
    "audio": [
        "audio/mpeg",  # MP3 audio
        "audio/wav",  # WAV audio
        "audio/ogg",  # Ogg Vorbis audio
        "audio/aac",  # AAC audio
        "audio/flac",  # FLAC audio
        "audio/midi",  # MIDI audio
        "audio/x-m4a",  # M4A audio
        "audio/webm",  # WebM audio
        "audio/opus",  # Opus audio
        "audio/3gpp",  # 3GPP audio
        "audio/3gpp2",  # 3GPP2 audio
        "audio/pcm",  # PCM audio
        "audio/x-ms-wma",  # Windows Media Audio
        "audio/ts",  # MPEG-TS audio
    ],
    "pdf": [
        "application/pdf",  # Standard PDF format
        "application/x-pdf",  # Alternative name for PDF
        "application/acrobat",  # Old MIME type for PDF
        "application/vnd.pdf",  # Vendor-specific type, rarely used
    ],
}


class AsyncSQLiteDB:
    def __init__(self, database):
        self.db_path = os.path.join("db_folder", f"{database}.db")
        os.makedirs("db_folder", exist_ok=True)
        self.conn = None

    async def connect(self):
        self.conn = await aiosqlite.connect(self.db_path)
        await self.conn.execute(
            "PRAGMA journal_mode=WAL"
        )  # Faster for concurrent reads/writes
        await self.conn.execute("PRAGMA synchronous=NORMAL")
        await self.conn.commit()

    async def create_table(self, table_name, columns):
        column_definitions = ", ".join(columns)
        create_table_sql = (
            f"CREATE TABLE IF NOT EXISTS {table_name} ({column_definitions})"
        )
        async with self.conn.execute(create_table_sql):
            await self.conn.commit()

    async def insert(self, table_name, data):
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["?"] * len(data))
        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        async with self.conn.execute(insert_sql, tuple(data.values())):
            await self.conn.commit()
        return True

    async def insert_many(self, table_name, data_list):
        """Bulk insert for speed."""
        if not data_list:
            return
        columns = ", ".join(data_list[0].keys())
        placeholders = ", ".join(["?"] * len(data_list[0]))
        insert_sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        async with self.conn.executemany(
            insert_sql, [tuple(d.values()) for d in data_list]
        ):
            await self.conn.commit()

    async def get(self, table_name, condition=None, params=()):
        query = f"SELECT * FROM {table_name}"
        if condition:
            query += f" WHERE {condition}"
        async with self.conn.execute(query, params) as cursor:
            result = await cursor.fetchall()
        return result

    async def save(self, table_name, filename, content):
        """Insert or update with a single query."""
        sql = f"""
        INSERT INTO {table_name} (filename, content) VALUES (?, ?)
        ON CONFLICT(filename) DO UPDATE SET content = excluded.content
        """
        await self.conn.execute(sql, (filename, content))
        await self.conn.commit()

    async def delete(self, table_name, condition, params=()):
        delete_sql = f"DELETE FROM {table_name} WHERE {condition}"
        await self.conn.execute(delete_sql, params)
        await self.conn.commit()

    async def close(self):
        await self.conn.close()


# Assume AsyncSQLiteDB is defined as in the previous code
async def main():
    db = AsyncSQLiteDB("test_db")
    await db.connect()
    await db.create_table(
        "data",
        [
            "id INTEGER PRIMARY KEY AUTOINCREMENT",
            "filename TEXT UNIQUE",
            "content TEXT",
        ],
    )
    await db.insert("data", {"filename": "file1.txt", "content": "Hello World"})
    data_list = [
        {"filename": "file2.txt", "content": "Python is fun"},
        {"filename": "file3.txt", "content": "SQLite async"},
        {"filename": "file4.txt", "content": "Fast DB handler"},
    ]
    await db.insert_many("data", data_list)

    print("Bulk rows inserted ✅")

    # 5️⃣ Get all rows
    all_rows = await db.get("data")
    print("All rows:", all_rows)

    # 6️⃣ Get rows with condition
    row = await db.get("data", "filename = ?", ("file2.txt",))
    print("Conditional get:", row)

    # 7️⃣ Save (insert or update)
    await db.save("data", "file2.txt", "Updated content!")
    print("Saved/Updated file2.txt ✅")

    # 8️⃣ Delete a row
    await db.delete("data", "filename = ?", ("file4.txt",))
    print("Deleted file4.txt ✅")

    # 9️⃣ Close connection
    await db.close()
    print("Database connection closed ✅")

def svg_to_png_bytesio(svg_path: str, width: int = None, height: int = None) -> BytesIO:
    drawing = svg2rlg(svg_path)

    # Optionally resize
    if width and height:
        scale_x = width / drawing.width
        scale_y = height / drawing.height
        drawing.width = width
        drawing.height = height
        drawing.scale(scale_x, scale_y)

    buffer = BytesIO()
    renderPM.drawToFile(drawing, buffer, fmt="PNG")
    buffer.seek(0)
    return buffer


def videos(folder, filename):
    file_path = os.path.join(folder, filename)

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    return FileResponse(path=file_path, media_type="video/mp4", filename=filename)
