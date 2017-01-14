import json
import os
from json import JSONEncoder
from typing import List
from os import scandir

from pygmalion.common.pygmalion_config import PygmalionConfig


class FileInformation:
    def __init__(self, name: str, size_in_bytes: int):
        self.name = name
        self.size_in_bytes = size_in_bytes


class DirectoryInformation:
    def __init__(self, name, files, directories=[]):
        self.name = name
        self.directories = directories
        self.files = files


class FileScanner:
    def __init__(self, root_directory: str, max_depth=2):
        self.max_depth = max_depth
        self.root_directory = root_directory

    def scan(self) -> str:
        info = self.scan_recursively(self.root_directory, 0)
        return json.dumps(info, ensure_ascii=False, cls=DirectoryInformationEncoder)

    def scan_recursively(self, directory, depth) -> DirectoryInformation:
        if depth > self.max_depth:
            return None
        directories = []
        files = []
        for file in scandir(directory):
            if file.is_dir():
                directory_info = self.scan_recursively(file.path, depth + 1)
                if directory_info:
                    directories.append(directory_info)
            else:
                files.append(FileInformation(file.name, file.stat().st_size))
        return DirectoryInformation(os.path.basename(directory), files, directories)


class DirectoryInformationEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, FileInformation):
            return {"name": o.name, "size_in_bytes": o.size_in_bytes}
        elif isinstance(o, DirectoryInformation):
            result = {"name": o.name}
            if o.directories:
                result["directories"] = self.default(o.directories)
            if o.files:
                result["files"] = self.default(o.files)
            return result
        elif isinstance(o, List):
            return [self.default(x) for x in o]

        return JSONEncoder.default(self, o)