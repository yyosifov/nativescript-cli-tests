"""
Tests for livesync command in context of iOS simulator
"""

import shutil
import time

from core.device.emulator import Emulator
from core.device.simulator import Simulator
from core.osutils.file import File
from core.osutils.folder import Folder
from core.osutils.watcher import Watcher
from core.settings.settings import SIMULATOR_NAME, IOS_RUNTIME_SYMLINK_PATH, TNS_PATH
from core.tns.tns import Tns


#########################################
# test_001
#   -> first run the app and then run full sync with xml, css and js
#   -> verify if simualtor is started run and livesync reuse running simulators
# test_101 - test_133
#   -> test livesync --watch with xml,css,js and add/delete files
# test_301
#   -> run full sync directly with out run before that
#########################################

class LiveSyncSimulator(Watcher):
    @classmethod
    def setUpClass(cls):

        # setup simulator
        Emulator.stop_emulators()
        Simulator.stop_simulators()

        Simulator.delete(SIMULATOR_NAME)
        Simulator.create(SIMULATOR_NAME, 'iPhone 6', '9.0')
        Simulator.create(SIMULATOR_NAME, 'iPhone 6', '9.1')
        Simulator.create(SIMULATOR_NAME, 'iPhone 6', '9.2')

        Simulator.start(SIMULATOR_NAME, '9.1')
        Folder.cleanup('TNS_App')
        Folder.cleanup('appTest')

        # setup app
        Tns.create_app(app_name="TNS_App", copy_from="data/apps/livesync-hello-world")
        Tns.platform_add(platform="ios", framework_path=IOS_RUNTIME_SYMLINK_PATH, path="TNS_App", symlink=True)
        output = Tns.run(platform="ios", emulator=True, path="TNS_App", assert_success=False)
        assert "Starting iOS Simulator" not in output

        # replace
        File.replace("TNS_App/app/main-page.xml", "TAP", "TEST")
        File.replace("TNS_App/app/main-view-model.js", "taps", "clicks")
        File.replace("TNS_App/app/app.css", "30", "20")

        File.replace("TNS_App/node_modules/tns-core-modules/LICENSE", "Copyright", "MyCopyright")
        File.replace(
                "TNS_App/node_modules/tns-core-modules/application/application-common.js",
                "(\"globals\");", "(\"globals\"); // test")

        # livesync
        command = TNS_PATH + " livesync ios --emulator --watch --path TNS_App --log trace"
        print command
        cls.start_watcher(command)

    def setUp(self):
        print ""
        print "#####"
        print self.id()
        print "#####"
        print ""

        # TODO: check is --watch still running? if not - start it again?

    def tearDown(self):
        pass

    @classmethod
    def tearDownClass(cls):
        cls.terminate_watcher()
        Simulator.stop_simulators()

        Folder.cleanup('TNS_App')
        Folder.cleanup('appTest')

    def test_001_full_livesync_ios_simulator_xml_js_css_tns_files(self):
        self.wait_for_text_in_output("prepared")
        time.sleep(3)  # ... than delete these.

        Simulator.file_contains("TNSApp", "app/main-page.xml", text="<Button text=\"TEST\" tap=\"{{ tapAction }}\" />")
        Simulator.file_contains("TNSApp", "app/main-view-model.js", text="this.set(\"message\", this.counter + \" clicks left\");")
        Simulator.file_contains("TNSApp", "app/app.css", text="font-size: 20;")
        Simulator.file_contains("TNSApp", "app/tns_modules/LICENSE", text="MyCopyright")
        Simulator.file_contains("TNSApp", "app/tns_modules/application/application-common.js",text="require(\"globals\"); // test")

    # Add new files
    def test_101_livesync_ios_simulator_watch_add_xml_file(self):
        shutil.copyfile("TNS_App/app/main-page.xml", "TNS_App/app/test/test.xml")
        self.wait_for_text_in_output("app/test/test.xml to")

        Simulator.file_contains("TNSApp", "app/test/test.xml", text="<Button text=\"TEST\" tap=\"{{ tapAction }}\" />")

    def test_102_livesync_ios_simulator_watch_add_js_file(self):
        shutil.copyfile("TNS_App/app/app.js", "TNS_App/app/test/test.js")
        self.wait_for_text_in_output("app/test/test.js to")
        time.sleep(3)
        Simulator.file_contains("TNSApp", "app/test/test.js", text="application.start();")

    def test_103_livesync_ios_simulator_watch_add_css_file(self):
        shutil.copyfile("TNS_App/app/app.css", "TNS_App/app/test/test.css")
        self.wait_for_text_in_output("app/test/test.css to")
        time.sleep(1)
        Simulator.file_contains("TNSApp", "app/test/test.css", text="color: #284848;")

    # Change in files
    def test_111_livesync_ios_simulator_watch_change_xml_file(self):
        File.replace("TNS_App/app/main-page.xml", "TEST", "WATCH")
        self.wait_for_text_in_output("app/main-page.xml to")
        time.sleep(1)
        Simulator.file_contains("TNSApp", "app/main-page.xml", text="<Button text=\"WATCH\" tap=\"{{ tapAction }}\" />")

    def test_112_livesync_ios_simulator_watch_change_js_file(self):
        File.replace("TNS_App/app/main-view-model.js", "clicks", "tricks")
        self.wait_for_text_in_output("app/main-view-model.js to")
        time.sleep(3)
        Simulator.file_contains("TNSApp", "app/main-view-model.js", text="this.set(\"message\", this.counter + \" tricks left\");")

    def test_113_livesync_ios_simulator_watch_change_css_file(self):
        File.replace("TNS_App/app/app.css", "#284848", "green")
        self.wait_for_text_in_output("app/app.css to")
        Simulator.file_contains("TNSApp", "app/app.css", text="color: green;")

    # Delete files
    def test_121_livesync_ios_simulator_watch_delete_xml_file(self):
        File.remove("TNS_App/app/test/test.xml")
        self.wait_for_text_in_output("app/test/test.xml")
        time.sleep(3)
        Simulator.file_contains("TNSApp", "app/test/test.xml", text="No such file or directory")

    def test_122_livesync_ios_simulator_watch_delete_js_file(self):
        File.remove("TNS_App/app/test/test.js")
        self.wait_for_text_in_output("app/test/test.js")
        time.sleep(3)
        Simulator.file_contains("TNSApp", "app/test/test.js", text="No such file or directory")

    def test_123_livesync_ios_simulator_watch_delete_css_file(self):
        File.remove("TNS_App/app/test/test.css")
        self.wait_for_text_in_output("app/test/test.css")
        time.sleep(3)
        Simulator.file_contains("TNSApp", "app/test/test.css", text="No such file or directory")

    # Add files to a new folder
    def test_131_livesync_ios_simulator_watch_add_xml_file_to_new_folder(self):
        Folder.create("TNS_App/app/folder")
        self.wait_for_text_in_output("TNS_App/app/folder/")
        shutil.copyfile("TNS_App/app/main-page.xml", "TNS_App/app/folder/test.xml")
        self.wait_for_text_in_output("app/folder/test.xml file with")
        time.sleep(3)
        Simulator.file_contains("TNSApp", "app/folder/test.xml", text="<Button text=\"WATCH\" tap=\"{{ tapAction }}\" />")
    #         remove("TNS_App/app/folder")
    #         self.wait_for_text_in_output("app/folder/")
    #
    #         Simulator.file_contains("TNSApp", "app/folder/test.xml")
    #         assert "No such file or directory" in output

    def test_132_livesync_ios_simulator_watch_add_js_file_to_new_folder(self):
        shutil.copyfile("TNS_App/app/app.js", "TNS_App/app/folder/test.js")
        self.wait_for_text_in_output("app/folder/test.js to")
        time.sleep(3)
        Simulator.file_contains("TNSApp", "app/folder/test.js", text="application.start();")

    def test_133_livesync_ios_simulator_watch_add_css_file_to_new_folder(self):
        shutil.copyfile("TNS_App/app/app.css", "TNS_App/app/folder/test.css")
        self.wait_for_text_in_output("app/folder/test.css to")
        time.sleep(1)
        Simulator.file_contains("TNSApp", "app/folder/test.css", text="color: green;")

    def test_301_livesync_ios_simulator_before_run(self):

        # TODO: Add test for https://github.com/NativeScript/nativescript-cli/issues/1548 after it is fixed

        self.terminate_watcher()
        Folder.cleanup('appTest')
        Simulator.stop_simulators()
        Tns.create_app(app_name="appTest")
        Tns.platform_add(platform="ios", framework_path=IOS_RUNTIME_SYMLINK_PATH, path="appTest", symlink=True)

        # replace
        File.replace("appTest/app/main-page.xml", "TAP", "MYTAP")
        File.replace("appTest/app/main-view-model.js", "taps", "clicks")
        File.replace("appTest/app/app.css", "30", "20")

        File.replace("appTest/node_modules/tns-core-modules/LICENSE", "Copyright", "MyCopyright")
        File.replace(
                "appTest/node_modules/tns-core-modules/application/application-common.js",
                "(\"globals\");", "(\"globals\"); // test")

        output = Tns.livesync(platform="ios", emulator=True, path="appTest", log_trace=True)
        assert "" in output
        time.sleep(3)

        Simulator.file_contains("appTest", "app/main-page.xml", text="MYTAP")
        Simulator.file_contains("appTest", "app/main-view-model.js", text="clicks left" )
        Simulator.file_contains("appTest", "app/app.css", text="font-size: 20;")
        Simulator.file_contains("appTest", "app/tns_modules/LICENSE", text="MyCopyright")
        Simulator.file_contains("appTest", "app/tns_modules/application/application-common.js", text="require(\"globals\"); // test")
