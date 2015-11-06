import platform
import unittest

from helpers._os_lib import run_aut, check_output
from helpers._tns_lib import TNSPATH, NPATH

# pylint: disable=R0201, C0111


class Help(unittest.TestCase):

    def setUp(self):

        print ""
        print "#####"
        print self.id()
        print "#####"
        print ""

    def tearDown(self):
        pass

    def test_001_TNSHelp(self):
        output = run_aut(TNSPATH + " help")
        assert check_output(output, 'help_output.txt')
        assert not "error" in output

    def test_002_NativescriptHelp(self):
        output = run_aut(NPATH + " help")
        assert check_output(output, 'help_output.txt')
        assert not "error" in output

    @unittest.skip(
        "Skipped because of https://github.com/NativeScript/nativescript-cli/issues/249")
    def test_003_TNSHelp(self):
        output = run_aut(TNSPATH + " -help")
        assert check_output(output, 'help_output.txt')
        assert not "error" in output

    def test_004_TNSHelp(self):
        output = run_aut(TNSPATH + " --help")
        assert check_output(output, 'help_output.txt')
        assert not "error" in output

    def test_005_TNSHelp(self):
        output = run_aut(TNSPATH + " -h")
        assert check_output(output, 'help_output.txt')
        assert not "error" in output

    def test_006_TNSHelp(self):
        output = run_aut(TNSPATH + " /?")
        assert check_output(output, 'help_output.txt')
        assert not "error" in output

    def test_200_TNSHelp_Create(self):
        output = run_aut(TNSPATH + " create --help")
        assert check_output(output, 'create_help_output.txt')
        assert not "error" in output

    def test_201_TNSHelp_Create(self):
        output = run_aut(TNSPATH + " create -h")
        assert check_output(output, 'create_help_output.txt')
        assert not "error" in output

    def test_202_TNSHelp_Create(self):
        output = run_aut(TNSPATH + " create ?")
        assert check_output(output, 'create_help_output.txt')
        assert not "error" in output

    def test_203_TNSHelp_Platform(self):
        output = run_aut(TNSPATH + " platform -h")
        assert check_output(output, 'platform_help_output.txt')
        assert not "error" in output

    def test_204_TNSHelp_Platform_Add(self):
        output = run_aut(TNSPATH + " platform add -h")
        assert check_output(output, 'platform_add_help_output.txt')
        assert not "error" in output

    def test_205_TNSHelp_Platform_AddAndroid(self):
        output = run_aut(TNSPATH + " platform add android -h")
        assert check_output(output, 'platform_add_help_output.txt')

    def test_206_TNSHelp_prepare(self):
        output = run_aut(TNSPATH + " prepare -h")
        assert check_output(output, 'prepare_help_output.txt')
        assert not "error" in output

    def test_207_TNSHelp_build(self):
        output = run_aut(TNSPATH + " build -h")
        assert check_output(output, 'build_help_output.txt')
        assert not "error" in output

    def test_208_TNSHelp_Build_Android(self):
        output = run_aut(TNSPATH + " build android -h")
        assert check_output(output, 'buildandroid_help_output.txt')
        assert not "error" in output

    def test_209_TNSHelp_Build_iOS(self):
        output = run_aut(TNSPATH + " build ios -h")
        assert check_output(output, 'buildios_help_output.txt')
        assert not "error" in output

    def test_210_TNSHelp_Deploy(self):
        output = run_aut(TNSPATH + " deploy -h")
        assert check_output(output, 'deploy_help_output.txt')
        assert not "error" in output

    def test_211_TNSHelp_Emulate(self):
        output = run_aut(TNSPATH + " emulate -h")
        assert check_output(output, 'emulate_help_output.txt')
        assert not "error" in output

    def test_212_TNSHelp_Emulate_Android(self):
        output = run_aut(TNSPATH + " emulate android -h")
        if 'Darwin' in platform.platform():
            assert check_output(output, 'emulate_android_help_osx_output.txt')
        else:
            assert check_output(output, 'emulate_android_help_output.txt')

    def test_213_TNSHelp_run(self):
        output = run_aut(TNSPATH + " run -h")
        assert check_output(output, 'run_help_output.txt')
        assert not "error" in output

    def test_214_TNSHelp_Device(self):
        output = run_aut(TNSPATH + " device -h")
        assert check_output(output, 'device_help_output.txt')
        assert not "error" in output

    def test_215_TNSHelp_Device_Log(self):
        output = run_aut(TNSPATH + " device log -h")
        assert check_output(output, 'devicelog_help_output.txt')
        assert not "error" in output

    def test_216_TNSHelp_Device_ListApplications(self):
        output = run_aut(TNSPATH + " device list-applications -h")
        assert check_output(output, 'devicelist_help_output.txt')
        assert not "error" in output

    def test_217_TNSHelp_Device_run(self):
        output = run_aut(TNSPATH + " device run -h")
        assert check_output(output, 'devicerun_help_output.txt')
        assert not "error" in output

    def test_218_TNSHelp_Debug(self):
        output = run_aut(TNSPATH + " debug -h")
        assert check_output(output, 'debug_help_output.txt')
        assert not "error" in output

    def test_219_TNSHelp_DebugAndroid(self):
        output = run_aut(TNSPATH + " debug android -h")
        assert check_output(output, 'debug_android_help_output.txt')
        assert not "error" in output

    def test_220_TNSHelp_DebugIOS(self):
        output = run_aut(TNSPATH + " debug ios -h")
        assert check_output(output, 'debug_ios_help_output.txt')
        assert not "error" in output

    def test_221_TNSHelp_FeatureUsageTracking(self):
        output = run_aut(TNSPATH + " feature-usage-tracking -h")
        assert check_output(output, 'feature_help_output.txt')
        assert not "error" in output

    def test_400_TNSHelp_InvalidCommand(self):
        output = run_aut(TNSPATH + " invalidCommand")
        assert "Unknown command 'invalidcommand'. Use 'tns help' for help." in output

    def test_401_TNSHelp_InvalidCommand(self):
        output = run_aut(TNSPATH + " 4")
        assert "Unknown command '4'. Use 'tns help' for help." in output
