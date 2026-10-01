import base64
import io
from pathlib import Path
from typing import Optional, Dict, Any

from PIL import Image, ImageOps, ImageColor, ImageDraw

# ============================================================
# Optional dependencies
# ============================================================

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None

try:
    import cairosvg
except ImportError:
    cairosvg = None

try:
    import cv2
except ImportError:
    cv2 = None

try:
    from mutagen import File as MutagenFile
except ImportError:
    MutagenFile = None


# ============================================================
# Exceptions
# ============================================================


class ThumbnailError(Exception):
    pass


class UnsupportedFileTypeError(ThumbnailError):
    pass


# ============================================================
# Thumbnail
# ============================================================


class Thumbnail:

    # Default thumbnail size
    DEFAULT_WIDTH = 200
    DEFAULT_HEIGHT = 200

    # --------------------------------------------------------
    # Supported extensions
    # --------------------------------------------------------

    IMAGE_EXTENSIONS = {
        ".jpg",
        ".jpeg",
        ".png",
        ".webp",
        ".gif",
        ".bmp",
        ".tif",
        ".tiff",
        ".ico",
        ".heic",
        ".heif",
        ".avif",
    }

    PDF_EXTENSIONS = {
        ".pdf",
    }

    SVG_EXTENSIONS = {
        ".svg",
        ".svgz",
    }

    VIDEO_EXTENSIONS = {
        ".mp4",
        ".mov",
        ".avi",
        ".mkv",
        ".webm",
        ".mpeg",
        ".mpg",
        ".m4v",
        ".3gp",
        ".flv",
        ".wmv",
        ".ts",
        ".mts",
        ".m2ts",
    }

    AUDIO_EXTENSIONS = {
        ".mp3",
        ".m4a",
        ".aac",
        ".wav",
        ".flac",
        ".ogg",
        ".oga",
        ".opus",
        ".wma",
        ".aiff",
        ".aif",
        ".ape",
        ".alac",
    }

    # ========================================================
    # PUBLIC API
    # ========================================================

    @classmethod
    def create(
        cls,
        file_path: str,
        width: Optional[int] = None,
        height: Optional[int] = None,
        fit: str = "contain",
        video_position: float = 0.1,
        background: str = "#ffffff",
        size: int = None,
    ) -> Dict[str, Any]:
        """
        Universal thumbnail generator.

        Args:
            file_path:
                Input file path.

            width:
                Thumbnail width.
                Default = 200

            height:
                Thumbnail height.
                Default = 200

            fit:
                "contain" = complete content visible
                "cover"   = fill complete box and crop if needed

            video_position:
                Video frame position.
                0.0 = beginning
                0.5 = middle
                1.0 = end

            background:
                Background color for contain mode.

        Returns:
            {
                "success": True,
                "mime_type": "image/png",
                "format": "png",
                "width": 200,
                "height": 200,
                "base64": "...",
                "data_url": "data:image/png;base64,...",
                "source": "...",
                "extension": ".jpg",
                "type": "image"
            }
        """

        path = Path(file_path)

        # ----------------------------------------------------
        # Validate file
        # ----------------------------------------------------

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not path.is_file():
            raise ThumbnailError(f"Not a file: {file_path}")

        # ----------------------------------------------------
        # Fit
        # ----------------------------------------------------

        fit = fit.lower().strip()

        if fit not in {"contain", "cover"}:
            raise ValueError("fit must be either 'contain' or 'cover'")

        # ----------------------------------------------------
        # Extension
        # ----------------------------------------------------

        extension = path.suffix.lower()

        # ----------------------------------------------------
        # Determine file type
        # ----------------------------------------------------

        if extension in cls.IMAGE_EXTENSIONS:

            file_type = "image"

            image = cls._from_image(path)

        elif extension in cls.PDF_EXTENSIONS:

            file_type = "pdf"

            image = cls._from_pdf(path)

        elif extension in cls.SVG_EXTENSIONS:

            file_type = "svg"

            image = cls._from_svg(path)

        elif extension in cls.VIDEO_EXTENSIONS:

            file_type = "video"

            image = cls._from_video(
                path,
                video_position,
            )

        elif extension in cls.AUDIO_EXTENSIONS:

            file_type = "audio"

            image = cls._from_audio(path)

        else:

            raise UnsupportedFileTypeError(f"Unsupported file type: {extension}")

        # ----------------------------------------------------
        # Normalize
        # ----------------------------------------------------

        image = cls._normalize_image(image)

        # ----------------------------------------------------
        # Dimensions
        # ----------------------------------------------------

        DEFAULT_WIDTH, DEFAULT_HEIGHT = image.size
        width = cls._validate_dimension(
            width,
            DEFAULT_WIDTH,
            "width",
        )

        height = cls._validate_dimension(
            height,
            DEFAULT_HEIGHT,
            "height",
        )

        # Set the desired width and maintain aspect ratio
        desired_width = 200
        aspect_ratio = height / width
        desired_height = int(desired_width * aspect_ratio)

        image = cls._make_thumbnail(
            image=image,
            width=desired_width,
            height=desired_height,
            fit=fit,
            background=background,
        )

        # ----------------------------------------------------
        # PNG
        # ----------------------------------------------------

        png_bytes = cls._to_webp_bytes(image, size)

        encoded = base64.b64encode(png_bytes).decode("utf-8")

        # ----------------------------------------------------
        # Result
        # ----------------------------------------------------

        return {
            "success": True,
            "mime_type": "image/png",
            "format": "png",
            "width": image.width,
            "height": image.height,
            "base64": encoded,
            "data_url": ("data:image/png;base64," + encoded),
            "source": str(path),
            "extension": extension,
            "type": file_type,
        }

    # ========================================================
    # IMAGE
    # ========================================================

    @classmethod
    def _from_image(
        cls,
        path: Path,
    ) -> Image.Image:

        try:

            with Image.open(path) as img:

                # Correct EXIF orientation
                img = ImageOps.exif_transpose(img)

                # Animated image -> first frame
                if getattr(
                    img,
                    "is_animated",
                    False,
                ):
                    img.seek(0)

                return img.copy()

        except Exception as e:

            raise ThumbnailError(f"Could not read image '{path}': {e}") from e

    # ========================================================
    # PDF
    # ========================================================

    @classmethod
    def _from_pdf(
        cls,
        path: Path,
    ) -> Image.Image:

        if fitz is None:

            raise ThumbnailError(
                "PDF support requires PyMuPDF. " "Install using: pip install PyMuPDF"
            )

        document = None

        try:

            document = fitz.open(str(path))

            if document.page_count == 0:

                raise ThumbnailError("PDF contains no pages.")

            # First page
            page = document.load_page(0)

            # Render at good quality
            matrix = fitz.Matrix(
                2,
                2,
            )

            pixmap = page.get_pixmap(
                matrix=matrix,
                alpha=True,
            )

            image = Image.open(io.BytesIO(pixmap.tobytes("png"))).convert("RGBA")

            return image

        except ThumbnailError:
            raise

        except Exception as e:

            raise ThumbnailError(
                f"Could not generate PDF " f"thumbnail '{path}': {e}"
            ) from e

        finally:

            if document is not None:
                document.close()

    # ========================================================
    # SVG
    # ========================================================

    @classmethod
    def _from_svg(
        cls,
        path: Path,
    ) -> Image.Image:

        if cairosvg is None:

            raise ThumbnailError(
                "SVG support requires CairoSVG. " "Install using: pip install cairosvg"
            )

        try:

            png_bytes = cairosvg.svg2png(
                url=str(path),
                output_width=1000,
            )

            image = Image.open(io.BytesIO(png_bytes)).convert("RGBA")

            return image

        except Exception as e:

            raise ThumbnailError(f"Could not render SVG " f"'{path}': {e}") from e

    # ========================================================
    # VIDEO
    # ========================================================

    @classmethod
    def _from_video(
        cls,
        path: Path,
        position: float = 0.1,
    ) -> Image.Image:

        if cv2 is None:

            raise ThumbnailError(
                "Video support requires OpenCV. "
                "Install using: pip install opencv-python"
            )

        if not 0.0 <= position <= 1.0:

            raise ValueError("video_position must be between 0.0 and 1.0")

        capture = cv2.VideoCapture(str(path))

        if not capture.isOpened():

            raise ThumbnailError(f"Could not open video: {path}")

        try:

            total_frames = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))

            # ------------------------------------------------
            # Seek to requested frame
            # ------------------------------------------------

            if total_frames > 0:

                frame_number = int((total_frames - 1) * position)

                frame_number = max(
                    0,
                    min(
                        frame_number,
                        total_frames - 1,
                    ),
                )

                capture.set(
                    cv2.CAP_PROP_POS_FRAMES,
                    frame_number,
                )

            # ------------------------------------------------
            # Read frame
            # ------------------------------------------------

            success, frame = capture.read()

            if not success or frame is None:

                raise ThumbnailError(f"Could not read video frame: {path}")

            # BGR -> RGB
            frame = cv2.cvtColor(
                frame,
                cv2.COLOR_BGR2RGB,
            )

            return Image.fromarray(frame).convert("RGB")

        except ThumbnailError:
            raise

        except Exception as e:

            raise ThumbnailError(
                f"Could not generate video " f"thumbnail '{path}': {e}"
            ) from e

        finally:

            capture.release()

    # ========================================================
    # AUDIO
    # ========================================================

    @classmethod
    def _from_audio(
        cls,
        path: Path,
    ) -> Image.Image:
        """
        Audio thumbnail priority:

        1. Embedded album art
        2. cover.jpg
        3. cover.png
        4. folder.jpg
        5. album.jpg
        6. Generated audio icon
        """

        # ----------------------------------------------------
        # Embedded artwork
        # ----------------------------------------------------

        artwork = cls._get_embedded_audio_art(path)

        if artwork is not None:
            return artwork

        # ----------------------------------------------------
        # Nearby cover
        # ----------------------------------------------------

        cover_names = [
            "cover.jpg",
            "cover.jpeg",
            "cover.png",
            "folder.jpg",
            "folder.jpeg",
            "folder.png",
            "album.jpg",
            "album.jpeg",
            "album.png",
        ]

        for name in cover_names:

            cover_path = path.parent / name

            if cover_path.exists() and cover_path.is_file():

                try:

                    return cls._from_image(cover_path)

                except Exception:
                    pass

        # ----------------------------------------------------
        # Generated audio thumbnail
        # ----------------------------------------------------

        return cls._create_audio_icon(path.suffix.lower())

    # ========================================================
    # AUDIO ARTWORK
    # ========================================================

    @classmethod
    def _get_embedded_audio_art(
        cls,
        path: Path,
    ) -> Optional[Image.Image]:

        if MutagenFile is None:
            return None

        try:

            audio = MutagenFile(
                str(path),
                easy=False,
            )

            if audio is None:
                return None

            tags = getattr(
                audio,
                "tags",
                None,
            )

            # ------------------------------------------------
            # MP3 ID3 APIC
            # ------------------------------------------------

            if tags:

                for key in tags.keys():

                    if str(key).startswith("APIC"):

                        artwork = tags[key]

                        data = getattr(
                            artwork,
                            "data",
                            None,
                        )

                        if data:

                            return Image.open(io.BytesIO(data)).convert("RGBA")

                # ------------------------------------------------
                # M4A / MP4
                # ------------------------------------------------

                covr = tags.get("covr")

                if covr:

                    data = covr[0]

                    return Image.open(io.BytesIO(data)).convert("RGBA")

            # ------------------------------------------------
            # FLAC
            # ------------------------------------------------

            pictures = getattr(
                audio,
                "pictures",
                None,
            )

            if pictures:

                picture = pictures[0]

                if picture.data:

                    return Image.open(io.BytesIO(picture.data)).convert("RGBA")

        except Exception:
            # Artwork parsing fail ho to
            # default icon use hoga.
            pass

        return None

    # ========================================================
    # DEFAULT AUDIO ICON
    # ========================================================

    @classmethod
    def _create_audio_icon(
        cls,
        extension: str,
    ) -> Image.Image:

        size = 800

        image = Image.new(
            "RGBA",
            (size, size),
            "#202124",
        )

        draw = ImageDraw.Draw(image)

        # ----------------------------------------------------
        # Circle
        # ----------------------------------------------------

        draw.ellipse(
            (
                80,
                80,
                720,
                720,
            ),
            fill="#3F51B5",
        )

        # ----------------------------------------------------
        # Music note stem
        # ----------------------------------------------------

        draw.rounded_rectangle(
            (
                390,
                190,
                450,
                520,
            ),
            radius=20,
            fill="white",
        )

        # ----------------------------------------------------
        # Music note flag
        # ----------------------------------------------------

        draw.polygon(
            [
                (420, 190),
                (610, 245),
                (610, 320),
                (420, 260),
            ],
            fill="white",
        )

        # ----------------------------------------------------
        # Music note head
        # ----------------------------------------------------

        draw.ellipse(
            (
                220,
                470,
                450,
                620,
            ),
            fill="white",
        )

        # ----------------------------------------------------
        # Extension
        # ----------------------------------------------------

        label = extension.replace(
            ".",
            "",
        ).upper()

        try:

            bbox = draw.textbbox(
                (0, 0),
                label,
            )

            text_width = bbox[2] - bbox[0]

            text_height = bbox[3] - bbox[1]

            draw.rounded_rectangle(
                (
                    300,
                    650,
                    500,
                    735,
                ),
                radius=20,
                fill="white",
            )

            draw.text(
                (
                    (size - text_width) / 2,
                    690 - text_height / 2,
                ),
                label,
                fill="#202124",
            )

        except Exception:
            pass

        return image

    # ========================================================
    # NORMALIZE IMAGE
    # ========================================================

    @classmethod
    def _normalize_image(
        cls,
        image: Image.Image,
    ) -> Image.Image:

        if image.mode in {
            "RGBA",
            "LA",
        }:
            return image.convert("RGBA")

        if image.mode == "P":
            return image.convert("RGBA")

        if image.mode == "CMYK":
            return image.convert("RGB")

        if image.mode not in {
            "RGB",
            "RGBA",
        }:
            return image.convert("RGBA")

        return image

    # ========================================================
    # MAKE THUMBNAIL
    # ========================================================

    @classmethod
    def _make_thumbnail(
        cls,
        image: Image.Image,
        width: int,
        height: int,
        fit: str,
        background: str,
    ) -> Image.Image:

        if fit == "contain":

            return cls._contain(
                image,
                width,
                height,
                background,
            )

        return cls._cover(
            image,
            width,
            height,
        )

    # ========================================================
    # CONTAIN
    # ========================================================

    @classmethod
    def _contain(
        cls,
        image: Image.Image,
        width: int,
        height: int,
        background: str,
    ) -> Image.Image:

        source = image.copy()

        ratio = min(
            width / source.width,
            height / source.height,
        )

        new_width = max(
            1,
            int(source.width * ratio),
        )

        new_height = max(
            1,
            int(source.height * ratio),
        )

        source = source.resize(
            (
                new_width,
                new_height,
            ),
            Image.Resampling.LANCZOS,
        )

        bg = cls._parse_color(background)

        canvas = Image.new(
            "RGBA",
            (
                width,
                height,
            ),
            bg,
        )

        x = (width - source.width) // 2

        y = (height - source.height) // 2

        if source.mode == "RGBA":

            canvas.alpha_composite(
                source,
                (
                    x,
                    y,
                ),
            )

        else:

            canvas.paste(
                source,
                (
                    x,
                    y,
                ),
            )

        return canvas

    # ========================================================
    # COVER
    # ========================================================

    @classmethod
    def _cover(
        cls,
        image: Image.Image,
        width: int,
        height: int,
    ) -> Image.Image:

        return ImageOps.fit(
            image,
            (
                width,
                height,
            ),
            method=Image.Resampling.LANCZOS,
            centering=(
                0.5,
                0.5,
            ),
        ).convert("RGBA")

    # ========================================================
    # PNG BYTES
    # ========================================================

    @classmethod
    def _to_png_bytes(
        cls,
        image: Image.Image,
        size: int = None,
    ) -> bytes:
        w, h = image.size

        while True:
            buffer = io.BytesIO()
            image.save(buffer, format="PNG", optimize=True)
            value = buffer.getvalue()

            if not size or len(value) <= size:
                return value

            w = max(1, int(w * 0.9))
            h = max(1, int(h * 0.9))
            image = image.resize((w, h), Image.Resampling.LANCZOS)

    @classmethod
    def _to_webp_bytes(
        cls,
        image: Image.Image,
        size: int = None,
    ) -> bytes:
        for q in range(95, 0, -5) if size else [90]:
            b = io.BytesIO()
            image.save(b, format="WEBP", quality=q, method=6)
            if not size or b.tell() <= size:
                return b.getvalue()
        return b.getvalue()

    # ========================================================
    # VALIDATE DIMENSION
    # ========================================================

    @staticmethod
    def _validate_dimension(
        value: Optional[int],
        default: int,
        name: str,
    ) -> int:

        if value is None:
            return default

        if not isinstance(
            value,
            int,
        ):
            raise TypeError(f"{name} must be an integer.")

        if value <= 0:
            raise ValueError(f"{name} must be greater than 0.")

        return value

    # ========================================================
    # COLOR
    # ========================================================

    @staticmethod
    def _parse_color(
        color: str,
    ):

        if color == "transparent":
            return (
                0,
                0,
                0,
                0,
            )

        try:

            rgb = ImageColor.getrgb(color)

            if len(rgb) == 3:

                return (
                    *rgb,
                    255,
                )

            return rgb

        except Exception:

            return (
                255,
                255,
                255,
                255,
            )


# ============================================================
# SIMPLE FUNCTION API
# ============================================================


def create_thumbnail(
    file_path: str,
    width: Optional[int] = None,
    height: Optional[int] = None,
    fit: str = "contain",
    video_position: float = 0.1,
) -> Dict[str, Any]:

    return Thumbnail.create(
        file_path=file_path,
        width=width,
        height=height,
        fit=fit,
        video_position=video_position,
    )
