import json
import os
import re

from includes.core.globals.fun import load_json
from includes.core.globals.entry import app_context
from includes.core.repo.dir_manager import folder
from includes.utils.utils import json_response


class TextExplorer:
    def __init__(self):
        self.deft = {}

    async def load_language(self):
        languages = {}

        for file_name in os.listdir(folder.language):
            if file_name.endswith(".json"):
                lang = os.path.splitext(file_name)[0]
                file_path = os.path.join(folder.language, file_name)

                with open(file_path, "r", encoding="utf-8") as f:
                    languages[lang] = json.load(f)

        return languages

    async def get(self, language, resource):

        languageName = ["English", "Hindi", "Sanskrit", "Tamil", "Telugu"]
        languageShoer = ["en", "hi", "sa", "ta", "te"]
        languageCode = languageShoer.index(language)

        languages = getattr(app_context, "languages", await self.load_language())

        fallback_language = languages.get("en")
        active_language = languages.get(language)

        language = getattr(
            app_context, "language", await load_json(app_context.folder, "lang")
        )

        translated_texts = {
            fallback_language[key]: active_language.get(key)
            for key in fallback_language.keys()
            if key in active_language
        }

        return json_response(
            {
                "language": [languageName[languageCode], language, languageCode],
                "lists": translated_texts,
                "languages": active_language,
            }
        )

        for n, value in language.items():
            org = re.sub(r"\s+", "", value[0].lower())
            orm = value[languageCode]
            self.deft[org.lower()] = orm

        if resource == "setting":
            lists = [
                "profiles",
                "Edit Account",
                "Change passwords",
                "Verify password",
                "Are you Teacher",
                "Sync",
                "Logout",
                "Password",
                "Enter Password",
                "Edit",
                "Website",
                "Name",
                "User Name",
                "Biography",
                "Gender",
                "Type the word above",
                "This won’t be part of your public profile.",
                "Editing your links is only available on mobile. Visit the MyApplication app and edit your profile to change the websites in your biography.",
                "Submit",
                "Enter Captcha",
                "Old Password",
                "Enter Old Password",
                "Enter the current password associated with your account to verify your identity.",
                "New Password",
                "Enter New Password",
                "Create a new password for your account. Ensure it meets the required security guidelines.",
                "Confirm Password",
                "Enter Confirm Password",
                "Re-enter the new password to confirm it matches and avoid mistakes.",
                "By using this method you can check the password of the login account. This method is used so that you can remember your password before logging out.",
                "Prefer not to say",
                "Female",
                "Male",
                "Theme",
                "Applies to new tabs, pages, dialogues and other menus",
                "Overall Appearance",
                "Overall Setting",
                "Captcha not verified!",
                "Restore default values across all customizable settings",
            ]

            nelist = {}
            for item in lists:
                ints = self.deft.get(re.sub(r"\s+", "", item.lower()))
                ints = ints if ints else item

                if isinstance(ints, list):
                    nelist[ints[0]] = ints[1]

                else:
                    nelist[item] = ints

            return json_response(
                {
                    "language": [languageName[languageCode], language, languageCode],
                    "lists": nelist,
                }
            )

        return "str(self.list)"
