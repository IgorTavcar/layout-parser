# Copyright 2021 The Layout Parser team and Paddle Detection model
# contributors. All rights reserved.
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
import logging
import tarfile

import pooch

from ..base_catalog import PathHandler, PathManager, _CACHE_DIR

MODEL_CATALOG = {
    "PubLayNet": {
        "ppyolov2_r50vd_dcn_365e": "https://paddle-model-ecology.bj.bcebos.com/model/layout-parser/ppyolov2_r50vd_dcn_365e_publaynet.tar",
    },
    "TableBank": {
        "ppyolov2_r50vd_dcn_365e": "https://paddle-model-ecology.bj.bcebos.com/model/layout-parser/ppyolov2_r50vd_dcn_365e_tableBank_word.tar",
    },
}

# fmt: off
LABEL_MAP_CATALOG = {
    "PubLayNet": {
        0: "Text",
        1: "Title",
        2: "List",
        3: "Table",
        4: "Figure"},
    "TableBank": {
        0: "Table"
    },
}
# fmt: on


# Paddle model package everything in tar files, and each model's tar file should contain
# the following files in the list:
_TAR_FILE_NAME_LIST = [
    "inference.pdiparams",
    "inference.pdiparams.info",
    "inference.pdmodel",
]


def _get_untar_directory(tar_file: str) -> str:

    base_path = os.path.dirname(tar_file)
    file_name = os.path.splitext(os.path.basename(tar_file))[0]
    target_folder = os.path.join(base_path, file_name)

    return target_folder


def _untar_model_weights(model_tar):
    """untar model files"""

    model_dir = _get_untar_directory(model_tar)

    if not os.path.exists(
        os.path.join(model_dir, _TAR_FILE_NAME_LIST[0])
    ) or not os.path.exists(os.path.join(model_dir, _TAR_FILE_NAME_LIST[2])):
        # the path to save the decompressed file
        os.makedirs(model_dir, exist_ok=True)
        with tarfile.open(model_tar, "r") as tarobj:
            for member in tarobj.getmembers():
                filename = None
                for tar_file_name in _TAR_FILE_NAME_LIST:
                    if tar_file_name in member.name:
                        filename = tar_file_name
                if filename is None:
                    continue
                file = tarobj.extractfile(member)
                with open(os.path.join(model_dir, filename), "wb") as model_file:
                    model_file.write(file.read())
    return model_dir


def is_cached_folder_exists_and_valid(cached):
    possible_extracted_model_folder = _get_untar_directory(cached)
    if not os.path.exists(possible_extracted_model_folder):
        return False
    for tar_file in _TAR_FILE_NAME_LIST:
        if not os.path.exists(os.path.join(possible_extracted_model_folder, tar_file)):
            return False
    return True


class LayoutParserPaddleModelHandler(PathHandler):
    """
    Resolve anything that's in LayoutParser model zoo.
    """

    PREFIX = "lp://paddledetection/"

    def _get_supported_prefixes(self):
        return [self.PREFIX, "https://paddle-model-ecology.bj.bcebos.com"]

    def _get_local_path(self, path, **kwargs):
        if path.startswith(self.PREFIX):
            model_name = path[len(self.PREFIX) :]
            dataset_name, *model_name, data_type = model_name.split("/")

            if data_type == "weight":
                model_url = MODEL_CATALOG[dataset_name]["/".join(model_name)]
            else:
                raise ValueError(f"Unknown data_type {data_type}")
            return self._get_local_path(model_url, **kwargs)

        # Direct URL download for paddle model tar files
        logger = logging.getLogger(__name__)
        os.makedirs(_CACHE_DIR, exist_ok=True)

        cached = pooch.retrieve(
            url=path,
            known_hash=None,
            path=_CACHE_DIR,
        )

        if path.endswith(".tar"):
            model_dir = _untar_model_weights(cached)
            logger.info("URL {} cached in {}".format(path, model_dir))
            return model_dir

        return cached

    def _open(self, path, mode="r", **kwargs):
        return open(self._get_local_path(path), mode, **kwargs)


PathManager.register_handler(LayoutParserPaddleModelHandler())
