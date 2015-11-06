import os
import shutil
import unittest

from helpers._os_lib import cleanup_folder, replace, cat_app_file, uninstall_app
from helpers._tns_lib import IOS_RUNTIME_PATH, \
    create_project_add_platform, live_sync, run
from helpers.device import given_real_device, \
    stop_emulators, stop_simulators, get_physical_device_id

# pylint: disable=R0201, C0111


class LiveSync_iOS(unittest.TestCase):

    # LiveSync Tests on iOS Device

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
        given_real_device(platform="ios")
        uninstall_app("TNSApp", platform="ios", fail=False)

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        uninstall_app("TNSApp", platform="ios", fail=False)

    def test_001_LiveSync_iOS_XmlJsCss_TnsModules_Files(self):
        create_project_add_platform(
            proj_name="TNS_App",
            platform="ios",
            framework_path=IOS_RUNTIME_PATH)
        run(platform="ios", path="TNS_App")

        replace("TNS_App/app/main-page.xml", "TAP", "TEST")
        replace("TNS_App/app/main-view-model.js", "taps", "clicks")
        replace("TNS_App/app/app.css", "30", "20")

        replace("TNS_App/node_modules/tns-core-modules/LICENSE", "2015", "9999")
        replace(
            "TNS_App/node_modules/tns-core-modules/application/application-common.js",
            "(\"globals\");",
            "(\"globals\"); // test")

        live_sync(platform="ios", path="TNS_App")

        output = cat_app_file("ios", "TNSApp", "app/main-page.xml")
        assert "<Button text=\"TEST\" tap=\"{{ tapAction }}\" />" in output
        output = cat_app_file("ios", "TNSApp", "app/main-view-model.js")
        assert "this.set(\"message\", this.counter + \" clicks left\");" in output
        output = cat_app_file("ios", "TNSApp", "app/app.css")
        assert "font-size: 20;" in output

        output = cat_app_file("ios", "TNSApp", "app/tns_modules/LICENSE")
        assert "Copyright (c) 9999 Telerik AD" in output
        output = cat_app_file(
            "ios",
            "TNSApp",
            "app/tns_modules/application/application-common.js")
        assert "require(\"globals\"); // test" in output

    def test_002_LiveSync_iOS_Device_XmlFile(self):
        create_project_add_platform(
            proj_name="TNS_App",
            platform="ios",
            framework_path=IOS_RUNTIME_PATH)
        run(platform="ios", path="TNS_App")

        device_id = get_physical_device_id(platform="ios")
        replace("TNS_App/app/main-view-model.js", "taps", "clicks")
        live_sync(platform="ios", device=device_id, path="TNS_App")

        output = cat_app_file("ios", "TNSApp", "app/main-view-model.js")
        assert "this.set(\"message\", this.counter + \" clicks left\");" in output

#         replace("TNS_App/app/main-view-model.js", "clicks", "runs")
#         run(platform="ios", path="TNS_App")

#         output = cat_app_file("ios", "TNSApp", "app/main-view-model.js")
#         assert "this.set(\"message\", this.counter + \" runs left\");" in output

    def test_201_LiveSync_iOS_AddNewFiles(self):
        create_project_add_platform(
            proj_name="TNS_App",
            platform="ios",
            framework_path=IOS_RUNTIME_PATH)
        run(platform="ios", path="TNS_App")

        shutil.copyfile("TNS_App/app/main-page.xml", "TNS_App/app/test.xml")
        shutil.copyfile("TNS_App/app/main-page.js", "TNS_App/app/test.js")
        shutil.copyfile("TNS_App/app/app.css", "TNS_App/app/test.css")

        os.makedirs("TNS_App/app/test")
        shutil.copyfile(
            "TNS_App/app/main-view-model.js",
            "TNS_App/app/test/main-view-model.js")

        live_sync(platform="ios", path="TNS_App")

        output = cat_app_file("ios", "TNSApp", "app/test.xml")
        assert "<Button text=\"TAP\" tap=\"{{ tapAction }}\" />" in output
        output = cat_app_file("ios", "TNSApp", "app/test.js")
        assert "page.bindingContext = vmModule.mainViewModel;" in output
        output = cat_app_file("ios", "TNSApp", "app/test.css")
        assert "color: #284848;" in output
        output = cat_app_file("ios", "TNSApp", "app/test/main-view-model.js")
        assert "HelloWorldModel.prototype.tapAction" in output

    @unittest.skip("TODO: Not implemented.")
    def test_202_LiveSync_iOS_DeleteFiles(self):
        pass

    @unittest.skip("TODO: Implement this test.")
    def test_203_LiveSync_iOS_Watch(self):
        pass
