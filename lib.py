"""Functions, classes and variables"""

from dataclasses import dataclass
import json
import os
import platform
import shutil
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request

URL_NF_REPO = "https://github.com/ryanoasis/nerd-fonts.git"

TEMP_DIR = os.getenv("TEMP")
if TEMP_DIR is None or TEMP_DIR == "":
    print("Environment variable TEMP does not exists")
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
                print("Invalid token")
                sys.exit()

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
                print("Invalid token")
                sys.exit()

        return "none"


@dataclass(frozen=True)
class TtfOtf:
    """.TTF file"""

    path: str
    enable_stylistic_sets: bool
    stylistic_sets: str


def check_requirements():
    if shutil.which("git") is None:
        print("git is required")
        sys.exit(0)

    if shutil.which("fontforge") is None:
        print("fontforge is required.")
        sys.exit(0)

    if shutil.which("unzip") is None:
        print("unzip is required.")
        sys.exit(0)

    if shutil.which("pyftfeatfreeze") is None:
        print("pyftfeatfreeze is required.")
        sys.exit(0)


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
        print(f"Error {err}, Type: {type(err)}")
        sys.exit()


def clone_nerd_fonts_repo(dest_dir: str, tag: str):
    """Clone nerd-fonts repo from GitHub"""
    if os.path.exists(dest_dir):
        content = os.listdir(dest_dir)
        if len(content) > 0:
            print("The destination directory has other directories or files.")
            sys.exit(0)

    print(f"Cloning {URL_NF_REPO}")
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
        print(f"{URL_NF_REPO} cloned.\n")

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
        print("Directories bin, css, src/glyphs and src/svgs added.\n")

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
        print(f"git checkout {tag} done.\n")

    os.makedirs(os.path.join(dest_dir, "patched-fonts"))
    os.makedirs(os.path.join(dest_dir, "src", "unpatched-fonts"))


def is_ttf_or_otf(filename: str) -> bool:
    """The font to download is .ttf, there are link that download .zip files"""
    return filename.find(".ttf") != -1 or filename.find(".otf") != -1


def download_and_extract_fonts(
    dest_dir: str, metadata_fonts: list[FontMetadata], token: str
):
    """Download and extract fonts in temp directory /tmp/fonts"""
    if os.path.exists(TEMP_DIR_FONTS) and os.path.isdir(TEMP_DIR_FONTS):
        shutil.rmtree(TEMP_DIR_FONTS)

    os.makedirs(TEMP_DIR_FONTS)

    for metadata in metadata_fonts:
        font = Font(metadata, token)
        dest = os.path.join(TEMP_DIR_FONTS, font.filename)

        if is_ttf_or_otf(font.filename):
            dest = os.path.join(dest_dir, "src", "unpatched-fonts", font.filename)

        print(f"Downloading {font.download_url}")
        urllib.request.urlretrieve(font.download_url, dest)
        print(f"{font.filename} downloaded.\n")

        if is_ttf_or_otf(font.filename):
            continue

        print(f"Extracting {font.filename}")
        with subprocess.Popen(
            [
                "unzip",
                "-q",
                os.path.join(TEMP_DIR_FONTS, font.filename),
                "-d",
                os.path.join(TEMP_DIR_FONTS, font.repo),
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ) as process:
            process.communicate()
            print(f"{font.filename} extracted.\n")


def apply_stylistic_sets(ttf_files: list[TtfOtf]):
    """Apply stylistic sets"""
    for file in ttf_files:
        if file.enable_stylistic_sets is True:
            print(f"Applying stylistic sets for {file.path}")
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
                print(f"Stylistic sets {file.stylistic_sets} applied for {file.path}\n")


def copy_and_paste_fonts(dest_dir: str, ttf_files: list[TtfOtf]):
    """Copy downloaded fonts and paste in src/unpatched-fonts inside nerd-fonts repo"""
    for file in ttf_files:
        shutil.copy(file.path, os.path.join(dest_dir, "src", "unpatched-fonts"))


def path_fonts(dest_dir: str):
    "Path fonts previosly downloaded"
    print(f"Patching fonts in {dest_dir}/src/unpatched-fonts\n")

    fonts_to_path = os.listdir(os.path.join(dest_dir, "src", "unpatched-fonts"))

    fontforge_exe = "fontforge"
    if platform.system() == "Windows":
        fontforge_exe += ".cmd"

    for font in fonts_to_path:
        print(f"Patching {font}")
        with subprocess.Popen(
            [
                fontforge_exe,
                "-script",
                "font-patcher",
                os.path.join("src", "unpatched-fonts", font),
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
            print(f"{font} patched.\n")

    print(f"All patched fonts are in {dest_dir}/patched-fonts")
