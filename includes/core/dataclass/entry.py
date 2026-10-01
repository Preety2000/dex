import json
import os
import re
from typing import Any
from dataclasses import dataclass, field
from includes.function import Functions
from includes.schemas.router_schema import DynamicURLRoute
from includes.core.repo.dir_manager import Folders


@dataclass
class GlobleCatchs:
    id: int = None
    get_with_terms: list = None


@dataclass
class AppContext:
    request: Any = None
    setting: Any = None
    route: "DynamicURLRoute" = field(init=False)

    exam_session = Any = None
    main_session = Any = None
    secondary_session = Any = None

    db: str | None = None
    title: str | None = None
    db_key: str = "hindi"
    stor_refrash: bool | None = None

    templates: str = "error"
    catch: dict[str, Any] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)
    response: dict[str, Any] = field(default_factory=dict)
    languages: dict[str, Any] = field(default_factory=dict)

    folder: "Folders" = field(init=False)
    function: "Functions" = field(init=False)

    def __post_init__(self):
        self.folder = Folders()
        self.function = Functions(self)

        # Load Languages
        for file_name in os.listdir(self.folder.language):
            if file_name.endswith(".json"):
                lang = os.path.splitext(file_name)[0]
                file_path = os.path.join(self.folder.language, file_name)
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                self.languages[lang] = data

    def set(self, name: str | int, value: Any):
        setattr(self, str(name), value)
        return value

    def get(self, name: str | int, default: Any = None):
        return getattr(self, str(name), default)

    def set_languages(self, lang: dict):

        lang_code = ["en", "hi", "sa", "ta", "te"][
            int(self.setting.setting_session.get("languageCode", 0))
        ]

        fallback_language = self.languages.get("en")
        active_language = self.languages.get(lang_code)

        self.request.state.menuname = {
            re.sub(r"\s+", "", fallback_language[key].lower()): active_language.get(key)
            for key in fallback_language.keys()
            if key in active_language
        }

        self.request.state.language_data = active_language
        return self.request.state.menuname

    async def active_exam_db(self):
        """Active exam database"""

        if self.db.exam_session is None:
            return await self.db.configure_exam()

        return self.db.exam_session

    async def active_primary_db(self):
        """Active primary database"""

        if self.db.main_session is None:
            return await self.db.config_primary_db()

        return self.db.main_session
