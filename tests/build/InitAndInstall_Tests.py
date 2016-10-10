"""
Test for init and install command

Specs:

Init command should init package.json
Install command should install all listed dependencies (npm install)
"""
import fileinput
import os

from core.base_class.BaseClass import BaseClass
from core.osutils.command import run
from core.osutils.file import File
from core.osutils.folder import Folder
from core.settings.settings import TNS_PATH, CURRENT_OS, OSType, TEST_RUN_HOME, SUT_ROOT_FOLDER
from core.tns.tns import Tns


class InitAndInstallTests(BaseClass):
    def setUp(self):
        BaseClass.setUp(self)
        Folder.cleanup(self.app_name)

    def test_001_init_defaults(self):
        Folder.create(BaseClass.app_name)
        Folder.navigate_to(BaseClass.app_name)
        output = Tns.init(attributes={"--force": ""}, tns_path=os.path.join("..", TNS_PATH), assert_success=False)
        Folder.navigate_to(TEST_RUN_HOME, relative_from_current_folder=False)
        assert "Project successfully initialized" in output

        assert File.exists(self.app_name + "/package.json")
        assert not File.exists(self.app_name + "/app")
        assert not File.exists(self.app_name + "/platform")

        output = File.read(self.app_name + "/package.json")
        assert "org.nativescript.TNSApp" in output
        assert "tns-android" in output
        assert "tns-core-modules" in output
        if CURRENT_OS == OSType.OSX:
            assert "tns-ios" in output

    def test_002_init_path(self):
        Tns.init(attributes={"--path": self.app_name, "--force": ""})
        assert File.exists(self.app_name + "/package.json")
        assert not File.exists(self.app_name + "/app")
        assert not File.exists(self.app_name + "/platform")

        output = File.read(self.app_name + "/package.json")
        assert "org.nativescript.TNSApp" in output
        assert "tns-android" in output
        if CURRENT_OS == OSType.OSX:
            assert "tns-ios" in output

    def test_003_init_update_existing_file(self):
        self.test_002_init_path()
        # Modify existing file
        for line in fileinput.input(self.app_name + "/package.json", inplace=1):
            print line.replace("org.nativescript.TNSApp", "org.nativescript.TestApp"),
        output = File.read(self.app_name + "/package.json")
        assert "org.nativescript.TestApp" in output

        # Overwrite changes
        self.test_002_init_path()

    def test_004_install_defaults(self):
        self.test_002_init_path()
        Tns.install(attributes={"--path": self.app_name})
        assert File.exists(self.app_name + "/platforms/android/build.gradle")

        if CURRENT_OS == OSType.OSX:
            assert File.exists(self.app_name + "/platforms/ios/TNSApp.xcodeproj")

    def test_005_install_node_modules(self):
        self.test_002_init_path()
        Folder.navigate_to(BaseClass.app_name)
        run("npm i gulp --save-dev")
        run("npm i lodash --save")
        Folder.navigate_to(TEST_RUN_HOME, relative_from_current_folder=False)
        output = File.read(self.app_name + "/package.json")
        assert "devDependencies" in output
        assert "gulp" in output
        assert "lodash" in output

        Folder.cleanup(self.app_name + '/node_modules')
        assert not File.exists(self.app_name + "/node_modules")

        Tns.install(attributes={"--path": self.app_name})
        assert File.exists(self.app_name + "/node_modules/lodash")
        assert File.exists(self.app_name + "/node_modules/gulp")

        assert File.exists(self.app_name + "/platforms/android/build.gradle")

        if CURRENT_OS == OSType.OSX:
            assert File.exists(self.app_name + "/platforms/ios/TNSApp.xcodeproj")

    def test_300_install_node_modules_if_node_modules_folder_exists(self):
        self.test_002_init_path()
        Folder.navigate_to(BaseClass.app_name)
        run("npm i gulp --save-dev")
        run("npm i lodash --save")
        Folder.navigate_to(TEST_RUN_HOME, relative_from_current_folder=False)

        output = File.read(self.app_name + "/package.json")
        assert "devDependencies" in output
        assert "gulp" in output
        assert "lodash" in output

        Tns.install(attributes={"--path": self.app_name})
        assert File.exists(self.app_name + "/node_modules/lodash")
        assert File.exists(self.app_name + "/node_modules/gulp")
        assert File.exists(self.app_name + "/platforms/android/build.gradle")
        if CURRENT_OS == OSType.OSX:
            assert File.exists(self.app_name + "/platforms/ios/TNSApp.xcodeproj")

    def test_301_install_and_prepare(self):
        self.test_002_init_path()

        Folder.navigate_to(BaseClass.app_name)
        run("npm i gulp --save-dev")
        run("npm i lodash --save")

        Folder.navigate_to(TEST_RUN_HOME, relative_from_current_folder=False)
        run("cp -R " + SUT_ROOT_FOLDER + os.path.sep + "template-hello-world " + self.app_name + os.path.sep + "app")
        output = File.read(self.app_name + "/package.json")
        assert "devDependencies" in output
        assert "gulp" in output
        assert "lodash" in output

        Tns.install(attributes={"--path": self.app_name})
        assert File.exists(self.app_name + "/node_modules/lodash")
        assert File.exists(self.app_name + "/node_modules/gulp")
        assert File.exists(self.app_name + "/platforms/android/build.gradle")

        Tns.prepare_android(attributes={"--path": self.app_name})
        assert File.exists(self.app_name + "/platforms/android/src/main/assets/app/tns_modules/lodash")
        assert not File.exists(self.app_name + "/platforms/android/src/main/assets/app/tns_modules/gulp")

        if CURRENT_OS == OSType.OSX:
            assert File.exists(self.app_name + "/platforms/ios/TNSApp.xcodeproj")
            Tns.prepare_ios(attributes={"--path": self.app_name})
            assert File.exists(self.app_name + "/platforms/ios/TNSApp/app/tns_modules/lodash")
            assert not File.exists(self.app_name + "/platforms/ios/TNSApp/app/tns_modules/gulp")

    def test_400_install_in_not_existing_folder(self):
        output = Tns.install(attributes={"--path": self.app_name}, assert_success=False)
        assert "No project found" in output
