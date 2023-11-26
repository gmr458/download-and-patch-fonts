"""Functions, classes and variables"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import json
import os
import platform
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

LogLevel = Enum("LogLevel", ["INFO", "ERROR", "FATAL"])


def log(level: LogLevel, message: str) -> None:
    print(f"[{level.name}] - {datetime.now()} - {message}")


URL_NF_REPO = "https://github.com/ryanoasis/nerd-fonts.git"

TEMP_DIR = os.getenv("TEMP")
if TEMP_DIR is None or TEMP_DIR == "":
    log(LogLevel.FATAL, "Environment variable TEMP does not exists")
    sys.exit(1)

TEMP_DIR_FONTS = os.path.join(TEMP_DIR, "fonts")


@dataclass(frozen=True)
class FontMetadata:
    """Font Metadata"""

    owner: str
    repo: str
    tag: str
    filename: str
    filename_start_with: str
    download_url: str


class Font:
    """Class Font"""

    headers: dict[str, str] = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    def __init__(self, metadata: FontMetadata, token: str):
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
        """Get tag from GitHub API"""
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
        """Get file name from GitHub API"""
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
    """.TTF file"""

    path: str
    enable_stylistic_sets: bool
    stylistic_sets: str


def check_requirements():
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


def get_latest_version_nf(token: str) -> str:
    """Get nerd-fonts latest tag from GitHub API"""
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
    except Exception as err:
        log(LogLevel.ERROR, "error trying to get latest nerd font version")
        print(f"Error {err}, Type: {type(err)}")
        sys.exit(1)


def clone_nerd_fonts_repo(dest_dir: str, tag: str):
    """Clone nerd-fonts repo from GitHub"""
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
    """The font to download is .ttf, there are link that download .zip files"""
    return filename.find(".ttf") != -1 or filename.find(".otf") != -1


def download_and_extract_fonts(
    dest_dir: str, metadata_fonts: list[FontMetadata], token: str
):
    """Download and extract fonts in temp directory /tmp/fonts"""
    if os.path.exists(TEMP_DIR_FONTS) and os.path.isdir(TEMP_DIR_FONTS):
        shutil.rmtree(TEMP_DIR_FONTS)

    log(LogLevel.INFO, f"temporary directory {TEMP_DIR_FONTS} created")
    os.makedirs(TEMP_DIR_FONTS)

    for metadata in metadata_fonts:
        font = Font(metadata, token)
        dest_download = os.path.join(TEMP_DIR_FONTS, font.filename)

        if is_ttf_or_otf(font.filename):
            dest_download = os.path.join(
                dest_dir, "src", "unpatched-fonts", font.filename
            )

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
    """Apply stylistic sets"""
    for file in ttf_otf_files:
        if file.enable_stylistic_sets is True:
            log(
                LogLevel.INFO,
                f"applying stylistic sets {file.stylistic_sets} for {file.path}",
            )
            with subprocess.Popen(
                [
                    "pyftfeatfreeze",
                    "-f",
                    file.stylistic_sets,
                    file.path,
                    file.path,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ) as process:
                process.communicate()
                log(
                    LogLevel.INFO,
                    f"stylistic sets {file.stylistic_sets} applied for {file.path}",
                )


def copy_and_paste_fonts(dest_dir: str, ttf_files: list[TtfOtf]):
    """Copy downloaded fonts and paste in src/unpatched-fonts inside nerd-fonts repo"""
    for file in ttf_files:
        dest_copy = os.path.join(dest_dir, "src", "unpatched-fonts")
        log(LogLevel.INFO, f"copying {file.path} into {dest_copy}")
        shutil.copy(file.path, dest_copy)
        log(LogLevel.INFO, f"{file.path} copied into {dest_copy}")


def path_fonts(dest_dir: str):
    "Path fonts previosly downloaded"

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
            f"patching {os.path.join(path_unpatched_fonts ,path_font_to_patch)}",
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
                f"{os.path.join(path_unpatched_fonts ,path_font_to_patch)} patched",
            )

    path_patched_fonts = os.path.join(dest_dir, "patched-fonts")
    log(LogLevel.INFO, f"all patched fonts are in {path_patched_fonts}")
