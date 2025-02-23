"""
This script provides utilities for managing font repositories and applying stylistic sets
to font files. It includes functionality for downloading, extracting, patching, and
organizing font files.

Dependencies:
- `git`
- `fontforge`
- `unzip`
- `pyftfeatfreeze`
"""

import glob
import json
import os
import platform
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

# Enum for logging levels
LogLevel = Enum("LogLevel", ["INFO", "WARNING", "ERROR", "FATAL"])


def log(level: LogLevel, message: str) -> None:
    """
    Logs a message with a given log level and timestamp.

    Args:
        level (LogLevel): The severity level of the log message.
        message (str): The log message to display.
    """
    print(f"[{level.name}] - {datetime.now()} - {message}")


# URL for the Nerd Fonts repository
URL_NF_REPO = "https://github.com/ryanoasis/nerd-fonts.git"

# Path to the temporary directory for file operations
TEMP_DIR = "/tmp"

if platform.system() == "Windows":
    TEMP_DIR = os.getenv("TEMP")

if TEMP_DIR is None or TEMP_DIR == "":
    log(LogLevel.FATAL, "temporal folder does not exists")
    sys.exit(1)

# Path to a specific temporary fonts directory
TEMP_DIR_FONTS = os.path.join(TEMP_DIR, "fonts")


@dataclass(frozen=True)
class FontMetadata:
    """
    Represents metadata for a font file.

    Attributes:
        owner (str): The owner of the repository.
        repo (str): The repository name.
        tag (str): The release tag.
        filename (str): The name of the font file.
        filename_start_with (str): The starting pattern for the filename.
        download_url (str): The URL to download the font file.
    """

    owner: str
    repo: str
    tag: str
    filename: str
    filename_start_with: str
    download_url: str


class Font:
    """
    Represents a font and its associated operations.

    Attributes:
        headers (dict): HTTP headers for API requests.
        owner (str): The repository owner.
        repo (str): The repository name.
        tag (str): The release tag for the font.
        filename (str): The filename of the font.
        download_url (str): The download URL of the font.
    """

    headers: dict[str, str] = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    def __init__(self, metadata: FontMetadata, token: str):
        """
        Initializes the Font instance.

        Args:
            metadata (FontMetadata): The metadata for the font.
            token (str): The GitHub API token.
        """
        self.headers["Authorization"] = f"Bearer {token}"
        self.owner = metadata.owner
        self.repo = metadata.repo
        self.tag = metadata.tag or self.get_tag()
        self.filename = metadata.filename or self.get_filename(
            metadata.filename_start_with
        )
        self.download_url = (
            metadata.download_url
            or "https://github.com/"
            f"{self.owner}/{self.repo}"
            f"/releases/download/{self.tag}/{self.filename}"
        )

    def get_tag(self) -> str:
        """
        Retrieves the latest release tag for the font.

        Returns:
            str: The latest release tag.

        Raises:
            SystemExit: If an HTTP 401 Unauthorized error occurs.
        """
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/releases/latest"

        req = urllib.request.Request(url=url, headers=self.headers)

        try:
            with urllib.request.urlopen(req) as response:
                data = json.load(response)
                return data["tag_name"]
        except urllib.error.HTTPError as err:
            if str(err) == "HTTP Error 401: Unauthorized":
                log(LogLevel.ERROR, "Invalid token")
                sys.exit(1)

        return "none"

    def get_filename(self, filename_start_with="") -> str:
        """
        Retrieves the filename of a font asset.

        Args:
            filename_start_with (str): The starting pattern for the filename.

        Returns:
            str: The name of the font file.
        """
        url = f"https://api.github.com/repos/{self.owner}/{self.repo}/releases/latest"

        req = urllib.request.Request(url=url, headers=self.headers)

        try:
            with urllib.request.urlopen(req) as response:
                data = json.load(response)

                if len(data["assets"]) == 1:
                    return data["assets"][0]["name"]

                for asset in data["assets"]:
                    if asset["name"].find(filename_start_with) != -1:
                        return asset["name"]
        except urllib.error.HTTPError as err:
            if str(err) == "HTTP Error 401: Unauthorized":
                log(LogLevel.ERROR, "Invalid token")
                sys.exit(1)

        return "none"


@dataclass(frozen=True)
class TtfOtf:
    """
    Represents a TrueType or OpenType font.

    Attributes:
        path (str): The file path to the font.
        enable_stylistic_sets (bool): Whether to enable stylistic sets.
        stylistic_sets (str): The stylistic sets to apply.
    """

    path: str
    enable_stylistic_sets: bool
    stylistic_sets: str


def check_requirements():
    """
    Checks if the necessary dependencies are installed.

    Exits the program if a dependency is missing.
    """
    if shutil.which("git") is None:
        log(LogLevel.ERROR, "git is required")
        sys.exit(1)

    if shutil.which("fontforge") is None:
        log(LogLevel.ERROR, "fontforge is required")
        sys.exit(1)

    if shutil.which("unzip") is None:
        log(LogLevel.ERROR, "unzip is required")
        sys.exit(1)

    if shutil.which("pyftfeatfreeze") is None:
        log(LogLevel.ERROR, "pyftfeatfreeze is required")
        sys.exit(1)


def get_latest_version_nf(token: str) -> str | None:
    """
    Fetches the latest release version tag of the Nerd Fonts repository.

    Args:
        token (str): The GitHub API token.

    Returns:
        str: The latest version tag.

    Raises:
        SystemExit: If the request fails or an error occurs.
    """
    url = "https://api.github.com/repos/ryanoasis/nerd-fonts/releases/latest"
    headers: dict[str, str] = {
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    req = urllib.request.Request(url=url, headers=headers)

    try:
        with urllib.request.urlopen(req) as response:
            data = json.load(response)
            return data["tag_name"]
    except urllib.error.HTTPError as err:
        if err.code == 401:
            log(LogLevel.ERROR, "the github api token is invalid or expired")
            sys.exit(1)
    except Exception as err:
        log(LogLevel.ERROR, "error trying to get latest nerd font version")
        print(f"Error {err}, Type: {type(err)}")
        sys.exit(1)


def clone_nerd_fonts_repo(dest_dir: str, tag: str):
    """
    Clones the Nerd Fonts repository and checks out a specific tag.

    Args:
        dest_dir (str): The destination directory for the cloned repository.
        tag (str): The release tag to check out.

    Raises:
        SystemExit: If the destination directory is not empty.
    """
    if os.path.exists(dest_dir):
        content = os.listdir(dest_dir)
        if len(content) > 0:
            log(
                LogLevel.ERROR,
                "the destination directory has other directories or files",
            )
            sys.exit(1)

    log(LogLevel.INFO, f"cloning repository {URL_NF_REPO} into {dest_dir}")
    with subprocess.Popen(
        [
            "git",
            "clone",
            "--filter=blob:none",
            "--sparse",
            URL_NF_REPO,
            dest_dir,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as process:
        process.communicate()
        log(LogLevel.INFO, f"repository {URL_NF_REPO} cloned")

    with subprocess.Popen(
        [
            "git",
            "sparse-checkout",
            "add",
            "bin",
            "css",
            "src/glyphs",
            "src/svgs",
        ],
        cwd=dest_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as process:
        process.communicate()
        log(LogLevel.INFO, "directories bin, css, src/glyphs and src/svgs added")

    with subprocess.Popen(
        [
            "git",
            "checkout",
            tag,
        ],
        cwd=dest_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ) as process:
        process.communicate()
        log(LogLevel.INFO, f"`git checkout {tag}` executed")

    path_patched_fonts = os.path.join(dest_dir, "patched-fonts")
    os.makedirs(path_patched_fonts)
    log(LogLevel.INFO, f"{path_patched_fonts} directory created")

    path_unpatched_fonts = os.path.join(dest_dir, "src", "unpatched-fonts")
    os.makedirs(path_unpatched_fonts)
    log(LogLevel.INFO, f"{path_unpatched_fonts} directory created")


def is_ttf_or_otf(filename: str) -> bool:
    """
    Determines whether a given file is a TrueType or OpenType font.

    Args:
        filename (str): The name of the file.

    Returns:
        bool: True if the file is a .ttf or .otf font, False otherwise.
    """
    return filename.find(".ttf") != -1 or filename.find(".otf") != -1


def download_and_extract_fonts(
    metadata_fonts: list[FontMetadata],
    token: str,
):
    """
    Downloads and extracts font files based on the provided metadata.

    Args:
        dest_dir (str): The directory to store the extracted font files.
        metadata_fonts (list[FontMetadata]): A list of font metadata.
        token (str): The GitHub API token.
    """
    if os.path.exists(TEMP_DIR_FONTS) and os.path.isdir(TEMP_DIR_FONTS):
        shutil.rmtree(TEMP_DIR_FONTS)

    log(LogLevel.INFO, f"temporary directory {TEMP_DIR_FONTS} created")
    os.makedirs(TEMP_DIR_FONTS)

    for metadata in metadata_fonts:
        font = Font(metadata, token)
        dest_download = os.path.join(TEMP_DIR_FONTS, font.filename)

        log(LogLevel.INFO, f"downloading {font.download_url} into {dest_download}")
        urllib.request.urlretrieve(font.download_url, dest_download)
        log(LogLevel.INFO, f"{font.download_url} downloaded into {dest_download}")

        if is_ttf_or_otf(font.filename):
            continue

        dest_extract = os.path.join(TEMP_DIR_FONTS, font.repo)
        log(LogLevel.INFO, f"extracting {dest_download} into {dest_extract}")
        with subprocess.Popen(
            [
                "unzip",
                "-q",
                dest_download,
                "-d",
                dest_extract,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ) as process:
            process.communicate()
            log(LogLevel.INFO, f"{dest_download} extracted into {dest_extract}")


def apply_stylistic_sets(ttf_otf_files: list[TtfOtf]):
    """
    Applies stylistic sets to the provided font files.

    Args:
        ttf_otf_files (list[TtfOtf]): A list of font files and their stylistic sets.
    """
    for file in ttf_otf_files:
        if file.enable_stylistic_sets is True:
            paths = glob.glob(file.path)
            if len(paths) == 0:
                log(
                    LogLevel.WARNING,
                    f"the path {file.path} may be incorrect, stylistic sets will not be applied",
                )
                continue
            path = paths[0]

            log(
                LogLevel.INFO,
                f"applying stylistic sets {file.stylistic_sets} for {path}",
            )
            with subprocess.Popen(
                [
                    "pyftfeatfreeze",
                    "-f",
                    file.stylistic_sets,
                    path,
                    path,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ) as process:
                process.communicate()
                log(
                    LogLevel.INFO,
                    f"stylistic sets {file.stylistic_sets} applied for {path}",
                )


def copy_and_paste_fonts(dest_dir: str, ttf_files: list[TtfOtf]):
    """
    Copies and pastes font files to the destination directory.

    Args:
        dest_dir (str): The destination directory.
        ttf_files (list[TtfOtf]): A list of font files to copy.
    """
    for file in ttf_files:
        paths = glob.glob(file.path)
        if len(paths) == 0:
            log(
                LogLevel.WARNING,
                f"the path {file.path} may be incorrect, this font file will not be copied and pasted",
            )
            continue
        path = paths[0]

        dest_copy = os.path.join(dest_dir, "src", "unpatched-fonts")
        log(LogLevel.INFO, f"copying {path} into {dest_copy}")
        shutil.copy(path, dest_copy)
        log(LogLevel.INFO, f"{path} copied into {dest_copy}")


def path_fonts(dest_dir: str):
    """
    Patches previously downloaded fonts.

    Args:
        dest_dir (str): The directory containing unpatched fonts.
    """
    path_unpatched_fonts = os.path.join(dest_dir, "src", "unpatched-fonts")

    log(LogLevel.INFO, f"patching fonts in {path_unpatched_fonts}")

    fonts_to_path = os.listdir(path_unpatched_fonts)

    fontforge_exe = "fontforge"
    if platform.system() == "Windows":
        fontforge_exe += ".cmd"

    for font in fonts_to_path:
        path_font_to_patch = os.path.join("src", "unpatched-fonts", font)
        log(
            LogLevel.INFO,
            f"patching {os.path.join(path_unpatched_fonts, path_font_to_patch)}",
        )
        with subprocess.Popen(
            [
                fontforge_exe,
                "-script",
                "font-patcher",
                path_font_to_patch,
                "--complete",
                "--mono",
                "--outputdir",
                "patched-fonts",
            ],
            cwd=dest_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ) as process:
            process.communicate()
            log(
                LogLevel.INFO,
                f"{os.path.join(path_unpatched_fonts, path_font_to_patch)} patched",
            )

    path_patched_fonts = os.path.join(dest_dir, "patched-fonts")
    log(LogLevel.INFO, f"all patched fonts are in {path_patched_fonts}")
