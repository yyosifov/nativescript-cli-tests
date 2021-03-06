"""
Test for building projects with iOS platform
"""
import os

from core.base_class.BaseClass import BaseClass
from core.osutils.command import run
from core.osutils.file import File
from core.osutils.folder import Folder
from core.settings.settings import IOS_RUNTIME_PATH, TNS_PATH, TEST_RUN_HOME, ANDROID_RUNTIME_PATH
from core.settings.strings import *
from core.tns.tns import Tns
from core.xcode.xcode import Xcode


class BuildiOSTests(BaseClass):
    app_name_dash = "test-app"
    app_name_space = "Test App"
    app_name_noplatform = "Test_AppNoPlatform"
    app_name_ios = "testapp_ios"

    @classmethod
    def setUpClass(cls):
        logfile = os.path.join("out", cls.__name__ + ".txt")
        BaseClass.setUpClass(logfile)

        File.remove("TestApp.app")
        File.remove("TestApp.ipa")

        Xcode.cleanup_cache()

    def setUp(self):
        BaseClass.setUp(self)

        Folder.cleanup(self.app_name_dash)
        Folder.cleanup(self.app_name_space)
        Folder.cleanup(self.app_name_ios)
        Folder.cleanup(self.app_name_noplatform)
        Folder.cleanup(self.app_name_noplatform + '/platforms/ios/build')

        Folder.cleanup(self.app_name)

    @classmethod
    def tearDownClass(cls):
        File.remove("TestApp.app")
        File.remove("TestApp.ipa")

        Folder.cleanup(cls.app_name)
        Folder.cleanup(cls.app_name_noplatform)
        Folder.cleanup(cls.app_name_dash)
        Folder.cleanup(cls.app_name_space)

    def test_001_build_ios(self):
        Tns.create_app(self.app_name)
        Tns.platform_add_ios(attributes={"--path": self.app_name, "--frameworkPath": IOS_RUNTIME_PATH})
        Tns.build_ios(attributes={"--path": self.app_name})

    def test_002_build_ios_release_fordevice(self):
        Tns.create_app(self.app_name)
        Tns.platform_add_android(attributes={"--path": self.app_name, "--frameworkPath": ANDROID_RUNTIME_PATH})
        Tns.platform_add_ios(attributes={"--path": self.app_name, "--frameworkPath": IOS_RUNTIME_PATH})
        Tns.build_ios(attributes={"--path": self.app_name, "--forDevice": "", "--release": ""})

        # Verify no aar and frameworks in platforms folder
        assert not File.pattern_exists(self.app_name + "/platforms/ios", "*.aar")
        assert not File.pattern_exists(self.app_name + "/platforms/ios/TestApp/app/tns_modules", "*.framework")

        # Verify ipa has both armv7 and arm64 archs
        run("mv " + self.app_name + "/platforms/ios/build/device/TestApp.ipa TestApp-ipa.tgz")
        run("tar -xvf TestApp-ipa.tgz")
        output = run("lipo -info Payload/TestApp.app/TestApp")
        assert "armv7" in output
        assert "arm64" in output

    def test_200_build_ios_release(self):
        Tns.create_app(self.app_name)
        Tns.platform_add_ios(attributes={"--path": self.app_name, "--frameworkPath": IOS_RUNTIME_PATH})
        Tns.build_ios(attributes={"--path": self.app_name, "--release": ""})

    def test_201_build_ios_fordevice(self):
        Tns.create_app(self.app_name)
        Tns.platform_add_ios(attributes={"--path": self.app_name, "--frameworkPath": IOS_RUNTIME_PATH})
        Tns.build_ios(attributes={"--path": self.app_name, "--forDevice": ""})

    def test_211_build_ios_inside_project(self):
        Tns.create_app(self.app_name)
        Tns.platform_add_ios(attributes={"--path": self.app_name,
                                         "--frameworkPath": IOS_RUNTIME_PATH
                                         })
        Folder.navigate_to(self.app_name)
        output = Tns.build_ios(tns_path=os.path.join("..", TNS_PATH), attributes={"--path": self.app_name},
                               assert_success=False)
        Folder.navigate_to(TEST_RUN_HOME, relative_from_current_folder=False)
        assert "build/emulator/TestApp.app" in output
        assert File.exists(self.app_name + "/platforms/ios/build/emulator/TestApp.app")

    def test_213_build_ios_platform_not_added_or_platforms_deleted(self):
        Tns.create_app(self.app_name_noplatform)
        Tns.build_ios(attributes={"--path": self.app_name_noplatform})
        Folder.cleanup(self.app_name_noplatform + '/platforms')
        Tns.build_ios(attributes={"--path": self.app_name_noplatform}, assert_success=False)

    def test_300_build_ios_with_dash(self):
        Tns.create_app(self.app_name_dash)
        Tns.platform_add_ios(attributes={"--path": self.app_name_dash, "--frameworkPath": IOS_RUNTIME_PATH})
        Tns.build_ios(attributes={"--path": self.app_name_dash})

        # Verify project id
        output = File.read(self.app_name_dash + os.sep + "package.json")
        assert app_identifier in output

    def test_301_build_ios_with_space(self):
        Tns.create_app(self.app_name_space)
        Tns.platform_add_ios(attributes={"--path": "\"" + self.app_name_space + "\"",
                                         "--frameworkPath": IOS_RUNTIME_PATH})

        Tns.build_ios(attributes={"--path": "\"" + self.app_name_space + "\""})

    def test_302_build_ios_with_ios_in_path(self):
        Tns.create_app(self.app_name_ios)
        Tns.platform_add_ios(attributes={"--path": self.app_name_ios, "--frameworkPath": IOS_RUNTIME_PATH})
        Tns.build_ios(attributes={"--path": self.app_name_ios})

    def test_310_build_ios_with_copy_to(self):
        File.remove("TestApp.app")
        Tns.create_app(self.app_name)
        Tns.platform_add_ios(attributes={"--path": self.app_name, "--frameworkPath": IOS_RUNTIME_PATH})
        Tns.build_ios(attributes={"--path": self.app_name, "--copy-to": "./"})
        assert File.exists("TestApp.app")

    def test_311_build_ios_release_with_copy_to(self):
        File.remove("TestApp.ipa")
        Tns.create_app(self.app_name)
        Tns.platform_add_ios(attributes={"--path": self.app_name, "--frameworkPath": IOS_RUNTIME_PATH})
        Tns.build_ios(attributes={"--path": self.app_name, "--forDevice": "", "--release": "", "--copy-to": "./"})
        assert File.exists("TestApp.ipa")

    def test_400_build_ios_with_wrong_param(self):
        Tns.create_app(self.app_name_noplatform)
        output = Tns.build_ios(attributes={"--path": self.app_name_noplatform, "--" + invalid: ""},
                               assert_success=False)
        assert invalid_option.format(invalid) in output
        assert error not in output.lower()
