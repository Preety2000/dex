import os
from pathlib import Path
from typing import Optional, Union


class Folders:
    """Production-ready directory path management class using Pathlib and Properties."""

    def __init__(self, root_dir: Optional[Union[str, Path]] = None):
        # Base root directory initialization (string or Path object)
        self._root = Path(root_dir) if root_dir else Path(os.getcwd())

    def _get_path(self, *path_segments) -> Path:
        """Path ko join karta hai aur agar folder maujood nahi hai toh automatically bana deta hai."""
        full_path = self._root.joinpath(*path_segments)
        full_path.mkdir(parents=True, exist_ok=True)  # Auto-create directory if not exists
        return full_path
    
    def _get_file_path(self, *path_segments) -> Path:
        """Path ko join karta hai aur agar folder maujood nahi hai toh automatically bana deta hai."""
        full_path = self._root.joinpath(*path_segments)
        return full_path
    
    # Root & Base Folders
    @property
    def root(self) -> Path:
        self._root.mkdir(parents=True, exist_ok=True)
        return self._root

    @property
    def static_folder(self) -> Path:
        return self._get_path("static")

    @property
    def upload_folder(self) -> Path:
        return self._get_path("uploads")

    @property
    def db_folder(self) -> Path:
        return self._get_path("database")

    # Static Sub-Folders
    @property
    def static_svg(self) -> Path:
        return self._get_path("static", "svg")

    @property
    def static_img(self) -> Path:
        return self._get_path("static", "img")

    @property
    def static_js(self) -> Path:
        return self._get_path("static", "script")

    @property
    def static_css(self) -> Path:
        return self._get_path("static", "css")

    @property
    def static_json(self) -> Path:
        return self._get_path("static", "json")

    # Upload Sub-Folders
    @property
    def image_folder(self) -> Path:
        return self._get_path("uploads", "images")

    @property
    def svg_folder(self) -> Path:
        return self._get_path("uploads", "svg")

    @property
    def pdf_folder(self) -> Path:
        return self._get_path("uploads", "pdf")

    @property
    def video_folder(self) -> Path:
        return self._get_path("uploads", "videos")

    @property
    def audio_folder(self) -> Path:
        return self._get_path("uploads", "audios")

    # Database Sub-Folders
    @property
    def member_folder(self) -> Path:
        return self._get_path("database", "member")

    @property
    def educore(self) -> Path:
        return self._get_path("database", "educore")

    @property
    def rqh(self) -> Path:
        return self._get_path("database", "rqh")

    @property
    def ex_context(self) -> Path:
        return self._get_path("database", "ex_context")

    @property
    def exnr(self) -> Path:
        return self._get_path("database", "exnr")

    # Other Custom Folders
    @property
    def language(self) -> Path:
        return self._get_path("static", "json", "lang")




    # Helper Methods
    def ensure_directories_exist(self) -> None:
        """App ke saare folders agar system par nahi hain, toh unhe create kar deta hai."""
        for attr in dir(self):
            prop = getattr(type(self), attr, None)
            if isinstance(prop, property):
                path_obj: Path = getattr(self, attr)
                path_obj.mkdir(parents=True, exist_ok=True)

    def exports(self, name: str) -> Optional[str]:
        """Dynamic lookup ke liye (getattr fallback mechanism)."""
        path_obj = getattr(self, name, None)
        return str(path_obj) if path_obj else None


    def imports(self, name, joinName, folderName):
        # joinName और folderName को जोड़कर एक नया पथ बनाता है और उसे 'name' के नाम से एट्रीब्यूट के रूप में सेट करता है
        # joinName एट्रीब्यूट का मान प्राप्त करता है
        joinName = self.exports(joinName)

        # दोनों पथों को जोड़ता है
        join = os.path.join(joinName, folderName)

        # नए पथ को 'name' एट्रीब्यूट के रूप में सेट करता है
        setattr(self, name, join)
        return join

    def ensure_directory(self, parent_dir, child_dir):
        """
        Create directory only if it does not exist.
        """

        full_path = os.path.join(parent_dir, child_dir)

        if not os.path.exists(full_path):
            os.makedirs(full_path, exist_ok=True)

        return full_path

    def remove(self, name):
        # अगर एट्रीब्यूट नाम का कोई एट्रीब्यूट मौजूद है तो उसे हटा देता है
        if hasattr(self, name):
            delattr(self, name)

    # सुनिश्चित करता है कि 'folders' लिस्ट में दिए गए सभी डायरेक्टरी मौजूद हों। अगर नहीं हैं, तो उन्हें बनाता है।
    def ensure_directories_exist(self):
        for _, folder in self:
            if not os.path.exists(folder):
                os.makedirs(folder)

    def is_path(self, id):
        # चेक करता है कि दिए गए 'id' नाम का एट्रीब्यूट मौजूद है या नहीं, अगर नहीं तो नेस्टेड डिक्शनरी में खोजता है
        if hasattr(self, id):
            return getattr(self, id)

        # सभी एट्रीब्यूट्स में से डिक्शनरी की तलाश करता है
        for key, value in vars(self).items():
            if isinstance(value, dict):

                # अगर कोई डिक्शनरी मिले तो उसमें id की तलाश करता है
                result = self.__class__(value).is_array(id)
                if result:
                    return result

        return None

    def __iter__(self):
        # Folders के एट्रीब्यूट्स को key-value जोड़ों के रूप में इटरेट करने की अनुमति देता है
        return iter(vars(self).items())

    @property
    def json(self):
        # Folders के सभी एट्रीब्यूट्स को एक डिक्शनरी में बदलकर उसे लौटाता है
        return {key: value for key, value in vars(self).items()}

    def get_svg_files(self, folder):
        # दिए गए फोल्डर में सभी .svg फ़ाइलों को खोजता है, पढ़ता है और उनकी सामग्री को एक डिक्शनरी के रूप में लौटाता है

        # एक खाली Array (संभवत: कस्टम क्लास) बनाता है
        svg_files_data = {}

        # फोल्डर में सभी फाइलों को सूचीबद्ध करता है
        for file in os.listdir(folder):
            # चेक करता है कि फाइल का नाम '.svg' से खत्म होता है या नहीं
            if file.endswith(".svg"):

                # फाइल का पूरा पथ बनाता है
                file_path = os.path.join(folder, file)
                # फाइल को UTF-8 एन्कोडिंग के साथ खोलता है
                with open(file_path, "r", encoding="utf-8") as svg_file:
                    # फाइल की सामग्री को पढ़ता है
                    file_content = svg_file.read()

                    # फाइल का नाम (बिना .svg के) और उसकी सामग्री को svg_files_data में जोड़ता है
                    svg_files_data.update({file.replace(".svg", ""): file_content})

        # svg_files_data की JSON प्रस्तुति को लौटाता है
        return svg_files_data


# Initialize Folders with the root path
folder = Folders()

# Ensure all directories exist
folder.ensure_directories_exist()
