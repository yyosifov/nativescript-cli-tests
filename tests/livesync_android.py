import os
import shutil
import time
import unittest

from helpers._os_lib import cleanup_folder, replace, cat_app_file
from helpers._tns_lib import ANDROID_RUNTIME_PATH, \
    create_project_add_platform, live_sync, run
from helpers.device import given_real_device, \
    stop_emulators, stop_simulators, get_physical_device_id

# pylint: disable=R0201, C0111


class LiveSync_Android(unittest.TestCase):

    # LiveSync Tests on Android Device

    @classmethod
    def setUpClass(cls):

        stop_emulators()
        stop_simulators()

    def setUp(self):

        print ""
        print "#####"
        print self.id()
        print "#####"
        print ""

        cleanup_folder('./TNS_App')
        given_real_device(platform="android")

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    def test_001_LiveSync_Android_XmlJsCss_TnsModules_Files(self):
        create_project_add_platform(
            proj_name="TNS_App",
            platform="android",
            framework_path=ANDROID_RUNTIME_PATH)
        run(platform="android", path="TNS_App")

        replace("TNS_App/app/main-page.xml", "TAP", "TEST")
        replace("TNS_App/app/main-view-model.js", "taps", "clicks")
        replace("TNS_App/app/app.css", "30", "20")

        replace("TNS_App/node_modules/tns-core-modules/LICENSE", "2015", "9999")
        replace(
            "TNS_App/node_modules/tns-core-modules/application/application-common.js",
            "(\"globals\");",
            "(\"globals\"); // test")

        live_sync(platform="android", path="TNS_App")

        output = cat_app_file("android", "TNSApp", "app/main-page.xml")
        assert "<Button text=\"TEST\" tap=\"{{ tapAction }}\" />" in output
        output = cat_app_file("android", "TNSApp", "app/main-view-model.js")
        assert "this.set(\"message\", this.counter + \" clicks left\");" in output
        output = cat_app_file("android", "TNSApp", "app/app.css")
        assert "font-size: 20;" in output

        output = cat_app_file("android", "TNSApp", "app/tns_modules/LICENSE")
        assert "Copyright (c) 9999 Telerik AD" in output
        output = cat_app_file(
            "android",
            "TNSApp",
            "app/tns_modules/application/application-common.js")
        assert "require(\"globals\"); // test" in output

    # This test executes the Run -> LiveSync -> Run work flow on an android
    # device with API level 21.
    def test_002_LiveSync_Android_Device_XmlFile_run(self):
        create_project_add_platform(
            proj_name="TNS_App",
            platform="android",
            framework_path=ANDROID_RUNTIME_PATH)
        run(platform="android", path="TNS_App")

        device_id = get_physical_device_id(platform="android")
        replace("TNS_App/app/main-page.xml", "TAP", "TEST")
        live_sync(platform="android", device=device_id, path="TNS_App")

        output = cat_app_file("android", "TNSApp", "app/main-page.xml")
        assert "<Button text=\"TEST\" tap=\"{{ tapAction }}\" />" in output

        replace("TNS_App/app/main-page.xml", "TEST", "RUN")
        run(platform="android", path="TNS_App")

        output = cat_app_file("android", "TNSApp", "app/main-page.xml")
        assert "<Button text=\"RUN\" tap=\"{{ tapAction }}\" />" in output

    def test_201_LiveSync_Android_AddNewFiles(self):
        create_project_add_platform(
            proj_name="TNS_App",
            platform="android",
            framework_path=ANDROID_RUNTIME_PATH)
        run(platform="android", path="TNS_App")

        shutil.copyfile("TNS_App/app/main-page.xml", "TNS_App/app/test.xml")
        shutil.copyfile("TNS_App/app/main-page.js", "TNS_App/app/test.js")
        shutil.copyfile("TNS_App/app/app.css", "TNS_App/app/test.css")

        os.makedirs("TNS_App/app/test")
        shutil.copyfile(
            "TNS_App/app/main-view-model.js",
            "TNS_App/app/test/main-view-model.js")

        live_sync(platform="android", path="TNS_App")
        time.sleep(5)

        output = cat_app_file("android", "TNSApp", "app/test.xml")
        assert "<Button text=\"TAP\" tap=\"{{ tapAction }}\" />" in output
        output = cat_app_file("android", "TNSApp", "app/test.js")
        assert "page.bindingContext = vmModule.mainViewModel;" in output
        output = cat_app_file("android", "TNSApp", "app/test.css")
        assert "color: #284848;" in output
        output = cat_app_file("android", "TNSApp", "app/test/main-view-model.js")
        assert "HelloWorldModel.prototype.tapAction" in output

    @unittest.skip("TODO: Not implemented.")
    def test_202_LiveSync_Android_DeleteFiles(self):
        pass

    @unittest.skip("TODO: Implement this test.")
    def test_203_LiveSync_Android_Watch(self):
        pass

    def test_301_LiveSync_Beforerun(self):
        create_project_add_platform(
            proj_name="TNS_App",
            platform="android",
            framework_path=ANDROID_RUNTIME_PATH)
        run(platform="android", path="TNS_App")

        replace("TNS_App/app/main-page.xml", "TAP", "TEST")
        output = live_sync(path="TNS_App", assert_success=False)

        assert "Multiple device platforms detected (iOS and Android). Specify platform or device on command line" in output

    @unittest.skip("TODO: Implement this test..")
    def test_302_LiveSync_Android_MultipleDevice(self):
        pass

    # TODO:
    # - test to detect a deleted file
    # - test to check change in a file that is not being used will not affect the app
    # - test to check JavaScript, XML and CSS do not crash the app
