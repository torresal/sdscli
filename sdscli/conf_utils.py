from __future__ import absolute_import
from __future__ import print_function

import os, yaml, logging, traceback


log_format = "[%(asctime)s: %(levelname)s/%(name)s/%(funcName)s] %(message)s"
logging.basicConfig(format=log_format, level=logging.INFO)


def get_user_config_path():
    """Return path to user configuration."""

    return os.path.expanduser(os.path.join('~', '.sds', 'config'))


class YamlConfError(Exception):
    """Exception class for YamlConf class."""
    pass


class YamlConf(object):
    """YAML configuration class."""

    def __init__(self, file):
        """Construct YamlConf instance."""

        logging.info("file: {}".format(file))
        self._file = file
        with open(self._file) as f:
            self._cfg = yaml.load(f)

    @property
    def file(self):
        return self._file

    @property
    def cfg(self):
        return self._cfg

    def get(self, key):
        try:
            return self._cfg[key]
        except KeyError as e:
            raise(YamlConfError("Configuration '{}' doesn't exist in {}.".format(key, self._file)))


class SettingsConf(YamlConf):
    """Settings YAML configuration class."""

    def __init__(self, file=None):
        "Construct SettingsConf instance."""

        if file is None: file = get_user_config_path()
        super(SettingsConf, self).__init__(file)
