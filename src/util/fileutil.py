"""
tvutils.fileutil Module

This module provides utility functions for working with files and JSON data.

Classes:
    JsonUtil: Provides methods for reading and writing JSON data to files.
    LastWrite: A class for reading and writing information to a file with a timestamp.
    LoginReadWrite: A class for reading and writing login information with authentication tokens.

Usage:
    - Use the `JsonUtil` class to read and write JSON data to files.
    - The `LastWrite` class is used to store data with a timestamp and read it back.
    - The `LoginReadWrite` class handles login information and authentication tokens.
    - When using `LoginReadWrite`, provide a username and password to generate
      a unique file path for storage.

Note:
    - The `JsonUtil` class provides methods for writing JSON data to files and reading it back.
    - The `LastWrite` class stores data with a timestamp and can be used for various purposes.
    - The `LoginReadWrite` class is designed for storing and retrieving
      authentication tokens securely.

"""

import logging
from datetime import datetime
import hashlib
import json
import time
import os
from pathlib import Path
from typing import Any, Annotated

from annotated_types import MinLen

logger = logging.getLogger(__name__)


class FUtil:
    """
    Utility class for modifying file paths by adding prefixes or suffixes to file names.

    Methods:
        - addprefix(file_path: str | Path, prefix: str) -> str | Path:
            Adds a prefix to the file name in the given file path.

        - addsuffix(file_path: str | Path, suffix: str) -> str | Path:
            Adds a suffix to the file name in the given file path.

        - class_test():
            Performs unit tests on the addprefix and addsuffix methods to validate their
            functionality.
    """

    @classmethod
    def addprefix(cls, file_path: str| Path, prefix: str) -> str | Path:
        """
        Adds a prefix to the file name in the given file path.

        Args:
            file_path (str | Path): The file path to modify.
            prefix (str): The prefix to add to the file name.

        Returns:
            str | Path: The modified file path with the added prefix.
        """
        path_was_str, path = (True, Path(file_path)) if isinstance(file_path, str) else (
        False, file_path)

        # Extract the file name and its extension (if present)
        file_name = path.name
        file_stem = file_name.split('.')[0]
        file_extension = file_name.split('.')[-1] if len(file_name.split('.')) > 1 else ''

        # Add the prefix to the file stem and reconstruct the file name
        if len(file_extension) == 0:
            new_file_name = f"{prefix}{file_stem}"
            assert len(file_stem) > 0, "Both parts cannot be zero"
        elif len(file_stem) == 0:
            new_file_name = f".{prefix}{file_extension}"
        else:
            new_file_name = f"{prefix}{file_stem}.{file_extension}"

        # Construct the new file path
        new_file_path = path.parent / new_file_name

        return str(new_file_path) if path_was_str else new_file_path

    @classmethod
    def addsuffix(cls, file_path: str | Path, suffix: str) -> str | Path:
        """
        Adds a suffix to the file name in the given file path.

        Args:
            file_path (str | Path): The file path to modify.
            suffix (str): The suffix to add to the file name.

        Returns:
            str | Path: The modified file path with the added suffix.
        """
        path_was_str, path = (True, Path(file_path)) if isinstance(file_path, str) else (
            False, file_path)

        # Extract the file name and its extension (if present)
        file_name = path.name
        file_stem = file_name.split('.')[0]
        file_extension = file_name.split('.')[-1] if len(file_name.split('.')) > 1 else ''

        # Add the suffix to the file stem and reconstruct the file name
        if len(file_extension) == 0:
            new_file_name = f"{file_stem}{suffix}"
            assert len(file_stem) > 0, "Both parts cannot be zero"
        elif len(file_stem) == 0:
            new_file_name = f".{file_extension}{suffix}"
        else:
            new_file_name = f"{file_stem}{suffix}.{file_extension}"

        # Construct the new file path
        new_file_path = path.parent / new_file_name

        return str(new_file_path) if path_was_str else new_file_path


    @classmethod
    def get_file_path__cur_dir(cls, fname: Annotated[str, MinLen(2)],
                               cur_file_path: Annotated[str, MinLen(10)]=__file__) -> Path:
        """Given a string return filepath in cur directory"""
        _fname = fname.strip()
        assert len(_fname) > 1
        return Path(cur_file_path).parent.joinpath(_fname)

    @classmethod
    def class_test(cls):
        """
        Performs unit tests to validate the addprefix and addsuffix methods.

        This method runs various test cases to ensure the correctness of the addprefix and
        addsuffix functions.
        """
        for dpath in ["dd/", "dd1/dd2/", "/dd1/dd2/"]:
            assert cls.addprefix(dpath + "bb.txt", "pp") == dpath + "ppbb.txt"
            assert cls.addprefix(dpath + "ff", "pp") == dpath + "ppff"
            assert cls.addprefix(dpath + ".bb", "pp") == dpath + ".ppbb"
            assert cls.addsuffix(dpath + "bb.txt", "ss") == dpath + "bbss.txt"
            assert cls.addsuffix(dpath + "ff", "ss") == dpath + "ffss"
            assert cls.addsuffix(dpath + ".bb", "ss") == dpath + ".bbss"

class JsonUtil:
    """
    A utility class for reading and writing JSON data to and from files.

    This class provides methods to write JSON data to a file and read JSON data
    from a file. It ensures that the data is properly formatted and can handle
    both dictionaries and lists.

    Methods:
        write(filepath: str | Path, json_data: dict | list):
            Writes JSON data to a file.

        read(filepath: str | Path) -> dict | list | None:
            Reads JSON data from a file and returns it as a dictionary or list.

    Usage:
    You can use this class to save and retrieve JSON data to and from files in
    your application. It helps in maintaining structured data storage.
    """
    @staticmethod
    def write(filepath: str | Path, json_data: dict | list, file_in_curr_dir: bool = False,
              cur_file_path: Annotated[str, MinLen(10)] = __file__):
        """
        Writes JSON data to a file.
        Args:
             filepath (str): The path to the JSON file.
             json_data (dict|list): The JSON data to be written (dictionary or list).
             file_in_curr_dir (bool): The filepath is filename and in curr_dir of fileutil.py
             cur_file_path (str): Current filepath
        Raises:
            AssertionError: If json_data is not a dictionary or list.
        """
        assert isinstance(json_data, (dict, list)), "Data is not json"
        if isinstance(filepath, Path):
            path_fpath = filepath
        elif isinstance(filepath, str):
            if file_in_curr_dir:
                path_fpath = FUtil.get_file_path__cur_dir(filepath, cur_file_path)
            else:
                path_fpath = Path(filepath)
        else:
            raise NotImplementedError
        path_fpath.parent.resolve().mkdir(
            parents=True, exist_ok=True)
        assert not path_fpath.is_dir()
        with open(path_fpath, mode='w', encoding="UTF-8") as outfile:
            json.dump(json_data, outfile, indent = 4)

    @staticmethod
    def read(filepath: str | Path, file_in_curr_dir: bool = False,
             cur_file_path: Annotated[str, MinLen(10)] = __file__):
        """
        Reads JSON data from a file.
        Args:
            filepath (str): The path to the JSON file.
            file_in_curr_dir (bool): The filepath is filename and in curr_dir of fileutil.py
            cur_file_path (str): Current filepath
        Returns:
              dict|list: The parsed JSON data (dictionary or list),
                         or None if an error occurs during parsing.

        """
        val = None

        if isinstance(filepath, Path):
            path_fpath = filepath
        elif isinstance(filepath, str):
            if file_in_curr_dir:
                path_fpath = FUtil.get_file_path__cur_dir(filepath, cur_file_path)
            else:
                path_fpath = Path(filepath)
        else:
            raise NotImplementedError

        if not path_fpath.is_file():
            logger.error('File %s does not exist', str(path_fpath))
            return None
        try:
            with open(path_fpath, mode='r', encoding="UTF-8") as outfile:
                if not outfile.readable():
                    logger.error('File %s is not readable', str(path_fpath))
                    return None
                val = json.load(outfile)
        except json.JSONDecodeError as _jde:
            logger.error('Error while converting json')
            val = None
        except OSError as _ode:
            logger.error('Cannot read from the filepath %s', str(path_fpath))
            val = None
        return val


class LastWrite:
    """
    A class for reading and writing information to a file with a timestamp.

    Attributes:
    _fpath (str or Path): The file path where data will be stored.
    _time_key (str): The key used to store the timestamp in the data.

    Methods:
    read_info(key_list: list or str or None = None) -> tuple:
        Read information from the file, optionally filtering by a list of keys.

    write_info(mydata: dict, ignore_old_data: bool = False):
        Write data to the file, optionally ignoring existing data.

    """

    def __init__(self, file_path: str | Path):
        """
        Initializes an instance of LastWrite.

        Args:
            file_path (str or Path): The file path where data will be stored.
        """
        self._fpath = file_path
        self._time_key = "_ltime"

    def read_info(self, key_list: list | str | None = None) -> (Any, list | dict):
        """
        Read information from the file, optionally filtering by a list of keys.

        Args:
            key_list (list, str, or None): A list of keys to filter the data.
                If None, returns all data.

        Returns:
            tuple: A tuple containing the timestamp and filtered data.
        """
        assert key_list is None or isinstance(key_list, (list, str)), "Wrong type"
        if isinstance(key_list, str):
            key_list = [key_list]
        json_val = JsonUtil.read(self._fpath)
        if json_val is None:
            return None, None
        val = {}
        if key_list is None:
            val = json_val
        else:
            for key_id in key_list:
                val[key_id] = json_val.get(key_id, "")
        return json_val[self._time_key], val

    def write_info(self, mydata: dict, ignore_old_data: bool = False):
        """
        Write data to the file, optionally ignoring existing data.

        Args:
            mydata (dict): The data to be written to the file.
            ignore_old_data (bool): If True, ignore existing data and replace it.

        """
        assert isinstance(mydata, dict), "Wrong type"
        assert isinstance(ignore_old_data, bool), "Wrong type"
        json_val = {self._time_key: time.time(),
                    "strtime": datetime.now().strftime("%m/%d/%Y, %H:%M:%S")}
        json_val.update(mydata)
        _, file_val = self.read_info(key_list = None)
        if file_val is not None and not ignore_old_data:
            file_val.update(json_val)
            json_val = file_val
        JsonUtil.write(self._fpath, json_val)


class LoginReadWrite(LastWrite):
    """
    A class for reading and writing login information with authentication tokens.

    Inherits from LastWrite.

    Methods:
    __init__(username: str, password: str):
        Initializes an instance of LoginReadWrite with a username and password.

    fun_get_login_info() -> str or None:
        Get the authentication token if it's still valid.

    fun_put_login_info(token: str):
        Store the authentication token.

    """

    def __init__(self, username: str, password: str):
        """
            Initializes an instance of LoginReadWrite with a username and password.
            It generates a unique file path based on the username and password hashes.
            Args:
                username (str): The user's username.
                password (str): The user's password.
        """
        hash_val = f"{self.__get_hash_str(username)}{self.__get_hash_str(password)}.json"
        login_dir_str = os.environ.get(
            "DUMMY")
        login_dir = Path(login_dir_str) if login_dir_str is not None \
            else Path(__file__).parent.joinpath("test").resolve()
        self.__fpath = login_dir.joinpath(hash_val)
        self._authkey = "auth_token"
        super().__init__(self.__fpath)

    @staticmethod
    def __get_hash_str(mystr: str) -> str:
        return hashlib.md5(mystr.encode('utf-8')).hexdigest()[-5:]

    def fun_get_login_info(self):
        """
        Get the authentication token if it's still valid.

        Returns:
            str or None: The authentication token if valid, or None if expired.
        """
        read_time, token = super().read_info([self._authkey])
        if token is None:
            return token
        now_time = time.time()
        if read_time - now_time > 3600:
            return None
        return token[self._authkey]

    def fun_put_login_info(self, token: str):
        """
        Store the authentication token.

        Args:
            token (str): The authentication token to be stored.
        """
        json_val = {self._authkey: token}
        super().write_info(json_val)

    @classmethod
    def class_test(cls):
        """
        Performs unit tests to validate the addprefix and addsuffix methods.

        This method runs various test cases to ensure the correctness of the
        fun_put_login_info functions.
        """
        os.environ["DUMMY"] = "test"
        lrw = LoginReadWrite("user", "pass")
        token = "sample_test_fileutil"
        lrw.fun_put_login_info(token)
        assert lrw.fun_get_login_info() == token


if __name__ == "__main__":
    LoginReadWrite.class_test()
    FUtil.class_test()
