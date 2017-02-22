"""
A wrapper of the tns commands.
"""
import os
import time

from core.osutils.command import run
from core.osutils.file import File
from core.osutils.folder import Folder
from core.osutils.os_type import OSType
from core.osutils.process import Process
from core.settings.settings import TNS_PATH, SUT_ROOT_FOLDER, DEVELOPMENT_TEAM, CLI_PATH, BRANCH, TEST_RUN_HOME, \
    COMMAND_TIMEOUT, OUTPUT_FILE, CURRENT_OS
from core.settings.strings import config_release, codesign, config_debug
from core.tns.tns_installed_platforms import Platforms
from core.tns.tns_verifications import TnsAsserts
from core.xcode.xcode import Xcode


class Tns(object):

    @staticmethod
    def __get_platform_string(platform=Platforms.NONE):
        if platform is Platforms.NONE:
            return ""
        if platform is Platforms.ANDROID:
            return "android"
        if platform is Platforms.IOS:
            return "ios"
        return platform

    @staticmethod
    def __get_app_id_from_app_name(app_name):
        return app_name.replace(" ", "").replace("-", "").replace("_", "").replace("\"", "")

    @staticmethod
    def __get_app_name_from_attributes(attributes={}):
        app_name = ""
        for k, v in attributes.iteritems():
            if k == "--path":
                app_name = v
        return app_name

    @staticmethod
    def run_tns_command(command, tns_path=None, attributes={}, log_trace=False, timeout=COMMAND_TIMEOUT, wait=True):
        cmd = TNS_PATH + " " + command
        if tns_path is not None:
            cmd = tns_path + " " + command
        if len(attributes) != 0:
            for k, v in attributes.iteritems():
                cmd += " " + k + " " + v
        if log_trace:
            cmd += " --log trace"
        print cmd
        output = run(command=cmd, timeout=timeout, wait=wait)
        return output

    @staticmethod
    def update_modules(path):
        if " " in path:
            path = "\"" + path + "\""
        if "release" in BRANCH.lower():
            version = Tns.run_tns_command("", attributes={"--version": ""})
            Tns.plugin_remove("tns-core-modules", attributes={"--path": path}, assert_success=False)
            output = Tns.plugin_add("tns-core-modules@" + version, attributes={"--path": path}, assert_success=False)
        else:
            Tns.plugin_remove("tns-core-modules", attributes={"--path": path}, assert_success=False)
            output = Tns.plugin_add("tns-core-modules@next", attributes={"--path": path})
        assert "undefined" not in output, "Something went wrong when modules are installed."
        return output

    @staticmethod
    def ensure_app_resources(path):
        app_resources_path = os.path.join(path, "app", "App_Resources")
        if File.exists(app_resources_path):
            pass
        else:
            print "AppResources not found. Will copy from default template..."
            src = os.path.join(TEST_RUN_HOME, "sut", "template-hello-world", "App_Resources")
            dest = os.path.join(TEST_RUN_HOME, path, "app", "App_Resources")
            Folder.copy(src, dest)

    @staticmethod
    def create_app(app_name, attributes={}, log_trace=False, assert_success=True, update_modules=True,
                   force_clean=True):

        if force_clean:
            if File.exists(app_name):
                # Hack for Windows OS (kill processes that keep folder in use)
                if CURRENT_OS == OSType.WINDOWS:
                    Process.kill('node')
                    Process.kill('aapt')
                    Process.kill('java')  # This will break the CI.
                Folder.cleanup(app_name)
        path = app_name
        attributes_to_string = ""
        for k, v in attributes.iteritems():
            if "--path" in k:
                path = v
            attributes_to_string = "".join("{0} {1}".format(k, v))
        attr = {}
        if not any(s in attributes_to_string for s in ("--ng", "--template", "--tsc")):
            attr = {"--template": SUT_ROOT_FOLDER + os.path.sep + "template-hello-world"}
        attr.update(attributes)
        if app_name is None:
            output = Tns.run_tns_command("create ", attributes=attr, log_trace=log_trace)
        else:
            output = Tns.run_tns_command("create \"" + app_name + "\"", attributes=attr, log_trace=log_trace)
        if assert_success:
            TnsAsserts.created(app_name=app_name, output=output)
        if update_modules:
            Tns.update_modules(path)
        Tns.ensure_app_resources(path)
        return output

    @staticmethod
    def create_app_ts(app_name, attributes={}, log_trace=False, assert_success=True, update_modules=True):
        """
        Create TypeScript application based on hello-world-ts template in GitHub (branch is respected)
        :param app_name: Application name.
        :param attributes: Additional attributes for `tns create` command.
        :param log_trace: If true runs with `--log trace`.
        :param assert_success: If true application is verified once it is created.
        :param update_modules: If true update modules (branch is respected).
        :return: output of `tns create command`
        """

        # TODO: Remove this hacks once we have proper structure on shares (or rework how we set branch is settings)
        if "release" in BRANCH.lower():
            branch = "release"
        else:
            branch = "master"

        attr = {"--template": "https://github.com/NativeScript/template-hello-world-ts.git#" + branch}
        attributes.update(attr)
        output = Tns.create_app(app_name=app_name, attributes=attributes, log_trace=log_trace,
                                assert_success=assert_success,
                                update_modules=update_modules)
        if assert_success:
            TnsAsserts.created_ts(app_name=app_name, output=output)
        return output

    @staticmethod
    def create_app_ng(app_name, attributes={}, log_trace=False, assert_success=True, update_modules=True):

        # TODO: Remove this hacks once we have proper structure on shares (or rework how we set branch is settings)
        if "release" in BRANCH.lower():
            branch = "release"
        else:
            branch = "master"

        attr = {"--template": "https://github.com/NativeScript/template-hello-world-ng.git#" + branch}
        attributes.update(attr)
        output = Tns.create_app(app_name=app_name, attributes=attributes, log_trace=log_trace,
                                assert_success=assert_success,
                                update_modules=update_modules)
        if assert_success:
            assert "nativescript-angular" in output

        return output

    @staticmethod
    def platform_add(platform=Platforms.NONE, version=None, attributes={}, assert_success=True, log_trace=False,
                     tns_path=None):

        #######################################################################################
        # Add platforms
        #######################################################################################

        platform_string = Tns.__get_platform_string(platform)

        if version is not None:
            platform_string = platform_string + "@" + version

        output = Tns.run_tns_command("platform add " + platform_string, attributes=attributes, log_trace=log_trace,
                                     tns_path=tns_path)

        #######################################################################################
        # Verify platforms added (if assert_success=True)
        #######################################################################################

        app_name = Tns.__get_app_name_from_attributes(attributes)
        if assert_success:
            TnsAsserts.platform_added(app_name=app_name, platform=platform, output=output)
        return output

    @staticmethod
    def platform_remove(platform=Platforms.NONE, attributes={}, assert_success=True, log_trace=False, tns_path=None):
        platform_string = Tns.__get_platform_string(platform)
        output = Tns.run_tns_command("platform remove " + platform_string, attributes=attributes, log_trace=log_trace,
                                     tns_path=tns_path)

        app_name = Tns.__get_app_name_from_attributes(attributes)
        if assert_success:
            assert "Platform {0} successfully removed".format(platform_string) in output
            assert "error" not in output
            if platform is Platforms.ANDROID:
                assert not File.exists(app_name + TnsAsserts.PLATFORM_ANDROID)
            if platform is Platforms.IOS:
                assert not File.exists(app_name + TnsAsserts.IOS)
        return output

    @staticmethod
    def platform_update(platform=Platforms.NONE, version=None, attributes={}, assert_success=True, log_trace=False,
                        tns_path=None):
        platform_string = Tns.__get_platform_string(platform)
        if version is not None:
            platform_string = platform_string + "@" + version
        output = Tns.run_tns_command("platform update " + platform_string, attributes=attributes, log_trace=log_trace,
                                     tns_path=tns_path)
        if assert_success:
            assert "Successfully updated to version" in output, "Failed to update platform. Log: " + output
        return output

    @staticmethod
    def platform_add_android(version=None, attributes={}, assert_success=True, log_trace=False, tns_path=None):
        return Tns.platform_add(platform=Platforms.ANDROID, version=version, attributes=attributes,
                                assert_success=assert_success,
                                log_trace=log_trace,
                                tns_path=tns_path)

    @staticmethod
    def platform_add_ios(version=None, attributes={}, assert_success=True, log_trace=False, tns_path=None):
        return Tns.platform_add(Platforms.IOS, version=version, attributes=attributes, assert_success=assert_success,
                                log_trace=log_trace,
                                tns_path=tns_path)

    @staticmethod
    def platform_list(attributes={}, assert_success=True, log_trace=False, tns_path=None):
        return Tns.run_tns_command("platform list", attributes=attributes, log_trace=log_trace, tns_path=tns_path)

    @staticmethod
    def plugin_add(name, attributes={}, log_trace=False, assert_success=True):
        output = Tns.run_tns_command("plugin add " + name, attributes=attributes, log_trace=log_trace)
        if assert_success:
            assert "Successfully installed plugin {0}".format(name.replace("@next", "")) in output
        return output

    @staticmethod
    def plugin_remove(name, attributes={}, log_trace=False, assert_success=True):
        output = Tns.run_tns_command("plugin remove " + name, attributes=attributes, log_trace=log_trace)
        if assert_success:
            assert "Successfully removed plugin {0}".format(name.replace("@next", "")) in output
        return output

    @staticmethod
    def prepare_android(attributes={}, assert_success=True, log_trace=False, tns_path=None):
        output = Tns.run_tns_command("prepare android ", attributes=attributes, log_trace=log_trace, tns_path=tns_path)
        if assert_success:
            assert "Project successfully prepared" in output
        return output

    @staticmethod
    def prepare_ios(attributes={}, assert_success=True, log_trace=False, tns_path=None):
        output = Tns.run_tns_command("prepare ios ", attributes=attributes, log_trace=log_trace, tns_path=tns_path)
        if assert_success:
            assert "Project successfully prepared" in output
        return output

    @staticmethod
    def build_android(attributes={}, assert_success=True, tns_path=None):
        output = Tns.run_tns_command("build android", attributes=attributes, tns_path=tns_path)
        if assert_success:
            assert "BUILD SUCCESSFUL" in output, "Build failed!"
            assert "Project successfully built" in output, "Build failed!"
            app_name = Tns.__get_app_name_from_attributes(attributes=attributes)
            app_id = Tns.__get_app_id_from_app_name(app_name)
            base_app_path = app_name + TnsAsserts.PLATFORM_ANDROID + "build/outputs/apk/" + app_id
            if "--release" in attributes.keys():
                apk_path = base_app_path + "-release.apk"
            else:
                apk_path = base_app_path + "-debug.apk"
            apk_path = apk_path.replace("\"", "")  # Handle projects with space
            assert File.exists(apk_path), "Apk file does not exist at " + apk_path
        return output

    @staticmethod
    def build_ios(attributes={}, assert_success=True, tns_path=None):
        if "8." in Xcode.get_version():
            # TODO: Use "--provision" instead.
            attr = {"--teamId": DEVELOPMENT_TEAM}
            attributes.update(attr)
        output = Tns.run_tns_command("build ios", attributes=attributes, tns_path=tns_path)
        if assert_success:
            assert "BUILD SUCCEEDED" in output
            assert "Project successfully built" in output
            assert "ERROR" not in output
            assert codesign in output
            app_name = Tns.__get_app_name_from_attributes(attributes=attributes)
            app_id = Tns.__get_app_id_from_app_name(app_name)
            app_name = app_name.replace("\"", "")  # Handle projects with space

            # Verify release/debug builds
            if "--release" in attributes.keys():
                assert config_release in output
            else:
                assert config_debug in output

            # Verify simulator/device builds
            if "--forDevice" in attributes.keys():
                assert "build/device/" + app_id + ".app" in output
                assert File.exists(app_name + "/platforms/ios/build/device/" + app_id + ".ipa")
            else:
                assert "build/emulator/" + app_id + ".app" in output
                assert File.exists(app_name + "/platforms/ios/build/emulator/" + app_id + ".app")
                assert File.exists(app_name + "/platforms/ios/" + app_id + "/" + app_id + "-Prefix.pch")
        return output

    @staticmethod
    def deploy_android(attributes={}, assert_success=True, log_trace=False, timeout=COMMAND_TIMEOUT, tns_path=None):
        output = Tns.run_tns_command("deploy android", attributes=attributes, log_trace=log_trace, timeout=timeout,
                                     tns_path=tns_path)
        if assert_success:
            assert "Project successfully built" in output
            assert "Successfully installed on device" in output
        return output

    @staticmethod
    def deploy_ios(attributes={}, assert_success=True, log_trace=False, timeout=COMMAND_TIMEOUT, tns_path=None):
        if "8." in Xcode.get_version():
            attr = {"--teamId": DEVELOPMENT_TEAM}
            attributes.update(attr)
        output = Tns.run_tns_command("deploy ios", attributes=attributes, log_trace=log_trace, timeout=timeout,
                                     tns_path=tns_path)
        if assert_success:
            assert "Project successfully built" in output
            assert "Successfully installed on device" in output
        return output

    @staticmethod
    def run_android(attributes={}, assert_success=True, log_trace=False, timeout=COMMAND_TIMEOUT, tns_path=None,
                    wait=True):
        output = Tns.run_tns_command("run android", attributes=attributes, log_trace=log_trace, timeout=timeout,
                                     tns_path=tns_path, wait=wait)
        if assert_success:
            assert "Project successfully built" in output
            assert "Successfully installed on device with identifier" in output
        return output

    @staticmethod
    def run_ios(attributes={}, assert_success=True, log_trace=False, timeout=COMMAND_TIMEOUT, tns_path=None):
        if "8." in Xcode.get_version():
            attr = {"--teamId": DEVELOPMENT_TEAM}
            attributes.update(attr)
        output = Tns.run_tns_command("run ios", attributes=attributes, log_trace=log_trace, timeout=timeout,
                                     tns_path=tns_path)
        if assert_success:
            assert "Project successfully built" in output
            assert "Successfully installed on device with identifier" in output
        return output

    @staticmethod
    def livesync(platform=None, attributes={}, log_trace=True, assert_success=True):
        command = "livesync "
        if platform is not None:
            command += platform
        attributes.update({"--justlaunch": ""})
        output = Tns.run_tns_command(command, attributes=attributes, log_trace=log_trace)

        if assert_success:
            assert "Project successfully prepared" in output
            if platform is "android":
                assert "Transferring project files..." in output
                assert "Applying changes..." in output
                assert "Successfully synced application" in output
                time.sleep(10)
            elif platform is "ios":
                assert "Project successfully prepared" in output
        return output

    @staticmethod
    def init(attributes={}, assert_success=True, tns_path=None):
        output = Tns.run_tns_command("init", attributes=attributes, tns_path=tns_path)
        if assert_success:
            assert "Project successfully initialized" in output
        return output

    @staticmethod
    def install(attributes={}, assert_success=True, tns_path=None):
        output = Tns.run_tns_command("install", attributes=attributes, tns_path=tns_path)
        if assert_success:
            assert "Project successfully created" in output
        return output

    @staticmethod
    def disable_reporting():
        Tns.run_tns_command("usage-reporting disable")
        Tns.run_tns_command("error-reporting disable")

    @staticmethod
    def wait_for_log(log_file, string_list, timeout=10, check_interval=3, clean_log=True):
        """
        Wait until log file contains list of string.
        :param log_file: Path to log file.
        :param string_list: List of strings.
        :param timeout: Timeout.
        :param check_interval: Check interval.
        :param clean_log: Specify if content of log file should be delete after check.
        """
        t_end = time.time() + timeout
        all_items_found = False
        log = ""
        while time.time() < t_end:
            log = File.read(log_file)
            for item in string_list:
                not_found_item = None
                if item in log:
                    print "'{0}' found.".format(item)
                else:
                    not_found_item = item
            if not_found_item is None:
                all_items_found = True
                print "Log contains: {0}".format(string_list)
                break
            else:
                print "'{0}' NOT found. Wait...".format(item)
                time.sleep(check_interval)
            if "BUILD FAILED" in log:
                print "BUILD FAILED. No need to wait more time!"
                break

        if clean_log and CURRENT_OS is not OSType.WINDOWS:
            File.write(file_path=OUTPUT_FILE, text="")

        if all_items_found:
            pass
        else:
            print "##### OUTPUT BEGIN #####\n"
            print log
            print "##### OUTPUT END #####\n"
            print ""
            assert False, "Output does not contain {0}".format(string_list)
