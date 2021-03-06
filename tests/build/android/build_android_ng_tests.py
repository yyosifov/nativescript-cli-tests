import os

from core.base_class.BaseClass import BaseClass
from core.osutils.file import File
from core.osutils.folder import Folder
from core.settings.settings import ANDROID_RUNTIME_PATH, \
    ANDROID_KEYSTORE_PASS, ANDROID_KEYSTORE_ALIAS, ANDROID_KEYSTORE_PATH, ANDROID_KEYSTORE_ALIAS_PASS
from core.tns.tns import Tns
from core.tns import angular_helper as angular
from core.settings.strings import *


class BuildAndroidNGTests(BaseClass):
    @classmethod
    def setUpClass(cls):
        logfile = os.path.join("out", cls.__name__ + ".txt")
        BaseClass.setUpClass(logfile)
        Folder.cleanup('./' + cls.app_name)
        Tns.create_app_ng(cls.app_name)
        Tns.platform_add_android(attributes={"--path": cls.app_name, "--frameworkPath": ANDROID_RUNTIME_PATH})

    @classmethod
    def tearDownClass(cls):
        BaseClass.tearDownClass()
        Folder.cleanup(cls.app_name)

    def test_001_build_android_ng_project(self):
        angular.assert_angular_project(self.app_name)
        Tns.build_android(attributes={"--path": self.app_name})
        assert File.exists(os.path.join(self.app_name, debug_apk_path))

    def test_200_build_android_ng_project_release(self):
        print ANDROID_KEYSTORE_PATH
        output = Tns.build_android(attributes={"--keyStorePath": ANDROID_KEYSTORE_PATH,
                                               "--keyStorePassword": ANDROID_KEYSTORE_PASS,
                                               "--keyStoreAlias": ANDROID_KEYSTORE_ALIAS,
                                               "--keyStoreAliasPassword": ANDROID_KEYSTORE_ALIAS_PASS,
                                               "--release": "",
                                               "--path": self.app_name
                                               })
        assert successfully_prepared in output
        assert build_successful in output

        assert successfully_built in output
        assert File.exists(os.path.join(self.app_name, release_apk_path))
