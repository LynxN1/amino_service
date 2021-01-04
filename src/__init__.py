import json
import requests

with open("version.json") as info_file:
    info = json.load(info_file)

__version__ = info["version"]
__author__ = info["author"]
__newest__ = json.loads(requests.get("https://github.com/LynxN1/amino_service/raw/master/version.json").text)["version"]

if __version__ != __newest__:
    print(f"New version of Amino Service available! ({__newest__})\n")
