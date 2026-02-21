# Copyright 2021 The Layout Parser team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os

import pooch


_CACHE_DIR = os.path.join(os.path.expanduser("~"), ".cache", "layoutparser")


class PathHandler:
    """Minimal base class replacing iopath.common.file_io.PathHandler."""

    def _get_supported_prefixes(self):
        return []

    def _get_local_path(self, path, **kwargs):
        raise NotImplementedError

    def _open(self, path, mode="r", **kwargs):
        raise NotImplementedError


class _PathManager:
    def __init__(self):
        self._handlers = {}

    def register_handler(self, handler):
        for prefix in handler._get_supported_prefixes():
            self._handlers[prefix] = handler

    def get_local_path(self, path, **kwargs):
        for prefix, handler in self._handlers.items():
            if path.startswith(prefix):
                return handler._get_local_path(path, **kwargs)

        # Default: HTTP(S) download via pooch
        if path.startswith("http://") or path.startswith("https://"):
            os.makedirs(_CACHE_DIR, exist_ok=True)
            return pooch.retrieve(
                url=path,
                known_hash=None,
                path=_CACHE_DIR,
            )

        # Local path
        return path

    def open(self, path, mode="r", **kwargs):
        local = self.get_local_path(path)
        return open(local, mode, **kwargs)


PathManager = _PathManager()
