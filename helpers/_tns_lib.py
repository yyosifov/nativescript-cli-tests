'''
Wraper around tns commands
'''
import os
import platform
import shutil

from helpers._os_lib import run_aut, file_exists, extract_archive
from time import sleep

tnsPath = os.path.join('node_modules', '.bin', 'tns')
nativescriptPath = os.path.join('node_modules', '.bin', 'nativescript')
androidRuntimePath = "tns-android.tgz"
iosRuntimePath = "tns-ios.tgz"
androidRuntimeSymlinkPath = os.path.join('tns-android', 'package')
iosRuntimeSymlinkPath = os.path.join('tns-ios', 'package')

androidKeyStorePath = os.environ.get('androidKeyStorePath')
androidKeyStorePassword = os.environ.get('androidKeyStorePassword')
androidKeyStoreAlias = os.environ.get('androidKeyStoreAlias')
androidKeyStoreAliasPassword = os.environ.get('androidKeyStoreAliasPassword')

if 'Darwin' in platform.platform():
    keychain = os.environ.get('KEYCHAIN')
    keychainPass = os.environ.get('KEYCHAIN_PASS', '')


def install_cli(path_to_package=None):
    '''Install {N} CLI specified in CLI_PATH environment variable'''

    if 'CLI_PATH' in os.environ:
        location = os.path.join(os.environ['CLI_PATH'], "nativescript.tgz")
        shutil.copy2(
            location.strip(),
            (os.path.join(
                os.getcwd(),
                "nativescript.tgz")))
    if path_to_package is not None:
        shutil.copy2(
            path_to_package,
            (os.path.join(
                os.getcwd(),
                "nativescript.tgz")))

    installCommand = "npm i nativescript.tgz"
    output = run_aut(installCommand)
    assert "ERR" "error" "FiberFuture" "dev-post-install" not in output, "{N} CLI installation failed."
    assert file_exists("node_modules/.bin/tns"), "{N} CLI installation failed."
    print output

def get_android_runtime():
    '''Copy android runtime form ANDROID_PATH to local folder'''

    if 'ANDROID_PATH' in os.environ:
        location = os.path.join(os.environ['ANDROID_PATH'], androidRuntimePath)
        shutil.copy2(
            location.strip(),
            (os.path.join(
                os.getcwd(),
                androidRuntimePath)))
    if file_exists(os.path.join(os.getcwd(), androidRuntimePath)):
        extract_archive(
            androidRuntimePath,
            os.path.splitext(androidRuntimePath)[0])

def get_ios_runtime():
    '''Copy android runtime form IOS_PATH to local folder'''

    if 'IOS_PATH' in os.environ:
        location = os.path.join(os.environ['IOS_PATH'], iosRuntimePath)
        shutil.copy2(
            location.strip(),
            (os.path.join(
                os.getcwd(),
                iosRuntimePath)))
    if file_exists(os.path.join(os.getcwd(), iosRuntimePath)):
        extract_archive(iosRuntimePath, os.path.splitext(iosRuntimePath)[0])

        current_dir = os.getcwd()
        os.chdir(os.path.join(current_dir, iosRuntimeSymlinkPath))
        run_aut("npm install")
        os.chdir(current_dir)

def uninstall_cli():
    '''Uninstall local {N} installation'''

    output = run_aut("npm rm nativescript")
    print output

def create_project(proj_name, path=None, app_id=None, copy_from=None):

    # If --copy-from is not specified explicitly then project will copy
    # template-hello-world
    if copy_from is None:
        copy_from = "template-hello-world"

    command = tnsPath + " create {0}".format(proj_name)

    if path is not None:
        command += " --path " + path
    if app_id is not None:
        command += " --appid " + app_id
    if copy_from is not None:
        command += " --copy-from " + copy_from

    output = run_aut(command)
    assert "Project {0} was successfully created".format(proj_name.replace("\"", "")) in output
    return output


def platform_add(platform=None, framework_path=None, path=None, symlink=False, assertSuccess=True):

    command = tnsPath + " platform add"

    if platform is not None:
        command += " {0}".format(platform)

    if framework_path is not None:
        command += " --frameworkPath {0}".format(framework_path)

    if path is not None:
        command += " --path {0}".format(path)

    if symlink is True:
        command += " --symlink"

    output = run_aut(command)

    if assertSuccess:
        assert "Copying template files..." in output
        assert "Project successfully created" in output

    return output


def prepare(path=None, platform=None, logTrace=False, assertSuccess=True):

    command = tnsPath + " prepare"

    if platform is not None:
        command += " {0}".format(platform)

    if path is not None:
        command += " --path {0}".format(path)

    if logTrace:
        command += " --log trace"

    output = run_aut(command)

    if assertSuccess:
        assert ("Project successfully prepared" in output)

    return output


def library_add(platform=None, libPath=None, path=None, assertSuccess=True):

    command = tnsPath + " library add"

    if platform is not None:
        command += " {0}".format(platform)

    if libPath is not None:
        command += " {0}".format(libPath)

    if path is not None:
        command += " --path {0}".format(path)

    output = run_aut(command)

    if assertSuccess:
        if platform is "android":
            assert ("was successfully added for android platform" in output)
        else:
            assert (
                "The iOS Deployment Target is now 8.0 in order to support Cocoa Touch Frameworks." in output)

    return output

def plugin_add(plugin=None, path=None, assert_success=True):

    command = tnsPath + " plugin add"

    if plugin is not None:
        command += " {0}".format(plugin)

    if path is not None:
        command += " --path {0}".format(path)

    output = run_aut(command)

    if assert_success:
        assert "Successfully installed plugin {0}".format(plugin) in output

    return output

def build(
        platform=None,
        mode=None,
        path=None,
        forDevice=False,
        logTrace=False,
        assertSuccess=True):

    command = tnsPath + " build"

    if platform is not None:
        command += " {0}".format(platform)

    if mode is not None:
        command += " --{0}".format(mode)

    if forDevice:
        command += " --forDevice"

    if path is not None:
        command += " --path {0}".format(path)

    if logTrace:
        command += " --log trace"

    output = run_aut(command)

    if assertSuccess:
        assert ("Project successfully prepared" in output)
        if platform is "android":
            assert ("BUILD SUCCESSFUL" in output)
        else:
            assert ("BUILD SUCCEEDED" in output)
        assert ("Project successfully built" in output)
        assert not ("ERROR" in output)

    return output


def run(
        platform=None,
        emulator=False,
        device=None,
        path=None,
        justLaunch=True,
        assertSuccess=True):

    command = tnsPath + " run"

    if platform is not None:
        command += " {0}".format(platform)

    if emulator:
        command += " --emulator"

    if device is not None:
        command += " --device {0}".format(device)

    if path is not None:
        command += " --path {0}".format(path)

    if justLaunch:
        command += " --justlaunch"

    output = run_aut(command)

    if assertSuccess:
        assert ("Project successfully prepared" in output)
        assert ("Project successfully built" in output)
        if platform is "android":
            assert ("Successfully deployed on device with identifier" in output)
        else:
            if emulator:
                assert ("Session started without errors." in output)
            else:
                assert ("Successfully deployed on device" in output)
                assert (
                    "Successfully run application org.nativescript." in output)

    return output


def live_sync(
        platform=None,
        emulator=False,
        device=None,
        watch=False,
        path=None,
        assertSuccess=True):

    command = tnsPath + " livesync"

    if platform is not None:
        command += " {0}".format(platform)

    if emulator:
        command += " --emulator"

    if device is not None:
        command += " --device {0}".format(device)

    if watch:
        command += " --watch"

    if path is not None:
        command += " --path {0}".format(path)

    output = run_aut(command + " --log trace")

    if assertSuccess:
        assert ("Project successfully prepared" in output)
        if platform is "android":
            assert ("Transferring project files..." in output)
            assert ("Successfully transferred all project files." in output)
            assert ("Applying changes..." in output)
            assert ("Successfully synced application org.nativescript." in output)
            sleep(10)

    return output


def create_project_add_platform(proj_name, platform=None, framework_path=None, symlink=False):
    create_project(proj_name)
    platform_add(platform, framework_path, proj_name, symlink)


def get_cli_version():
    return run_aut(tnsPath + " --version")
