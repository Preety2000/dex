from includes.database.connection import db
from includes.core.globals.entry import app_context
from includes.database.models.owner import bindOwnerModelsToSession
from includes.database.models.secondary import bindBaseSecondaryModelsToSession


async def initialize_database():
    # Initialize database connections
    await db.configure()

    # bindOwnerModelsToSession(db)
    # bindBaseSecondaryModelsToSession(db)

    # Store in global state
    app_context.db = db
    app_context.model_class = db
    app_context.main_session = db.main_session
    app_context.secondary_session = db.secondary_session

    # Set language for Application
    app_context.preferences = await app_context.setting.preferences()
    app_context.set_languages(app_context.language)
