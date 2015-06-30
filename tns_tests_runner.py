import os
import platform
import unittest

from helpers import HTMLTestRunner
from helpers._tns_lib import GetCLIBuildVersion
from tests.autocomplete import Autocomplete
from tests.build_linux import Build_Linux
from tests.build_osx import Build_OSX
from tests.create import Create
from tests.debug_linux import Debug_Linux
from tests.debug_osx import Debug_OSX
from tests.deploy_linux import Deploy_Linux
from tests.deploy_osx import Deploy_OSX
from tests.device_linux import Device_Linux
from tests.device_osx import Device_OSX
from tests.emulate_linux import Emulate_Linux
from tests.emulate_osx import Emulate_OSX
from tests.feature_usage_tracking import FeatureUsageTracking
from tests.init_linux import Init_Linux
from tests.init_osx import Init_OSX
from tests.install_linux import Install_Linux
from tests.install_osx import Install_OSX
from tests.library_linux import Library_Linux
from tests.library_osx import Library_OSX
from tests.logtrace import LogTrace
from tests.platform_linux import Platform_Linux
from tests.platform_osx import Platform_OSX
from tests.plugins_linux import Plugins_Linux
from tests.plugins_osx import Plugins_OSX
from tests.prepare_linux import Prepare_Linux
from tests.prepare_osx import Prepare_OSX
from tests.run_linux import Run_Linux
from tests.run_osx import Run_OSX
from tests.version import Version


def RunTests():
    
    print "Platform : ", platform.platform()        
    
    # Android Requirements:
    # - Valid pair of keyStore and password
    #
    # iOS Requirements:
    # - Valid pair of certificate and provisioning profile on your OS X system
    # 
    # Following environment variables should be set:
    # - CLI_PATH - Path to CLI package under test (package file should be named nativescript.tgz)
    # - ANDROID_PATH - Path to Android runtime package under test (package file should be named tns-android.tgz)   
    # - androidKeyStorePath - Specifies the file path to the keystore file which you want to use to code sign your APK  
    # - androidKeyStorePassword - Password for the keystore file
    # - androidKeyStoreAlias
    # - androidKeyStoreAliasPassword
    # - KEYCHAIN - Keychain for signing iOS Apps
    # - KEYCHAIN_PASS - Keychain password
    #
    # Test name convention:
    # 001 - 199 - High priority
    # 200 - 299 - Medium priority
    # 300 - 399 - Low priority
    # 400 - 499 - Negative tests  
    # 
    # TESTRUN Types:
    # SMOKE 
    # - Runs tests with High priority. 
    # DEFAULT
    # - All suites without dependencies on real devices  (all priorities)
    # - Following AVDs should be available
    #    Api17 - Android emulator with API17
    #    Api19 - Android emulator with API19
    # FULL
    # - Runs all tests
    # - At least one real Android device must be attached to Linux hosts
    # - At least one real iOS device must be attached to OSX hosts        
       
    suite = unittest.TestLoader().loadTestsFromTestCase(Version)   

    # Temporary ignore Help tests because of expected breaking changes 
    # suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Help))    
    
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(LogTrace)) 
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Autocomplete))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(FeatureUsageTracking))
                           
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Create))    
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Platform_Linux))    
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Prepare_Linux)) 
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Library_Linux))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Build_Linux))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Plugins_Linux))
    #suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Install_Linux))  
    #suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Init_Linux))
    if 'Darwin' in platform.platform():
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Platform_OSX))
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Prepare_OSX))
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Library_OSX)) 
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Build_OSX))
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Plugins_OSX))   
        #suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Install_OSX))   
        #suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Init_OSX)) 
        
    if ('TESTRUN' in os.environ) and (not "SMOKE" in os.environ['TESTRUN']): 
        suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Emulate_Linux))
        if 'Darwin' in platform.platform():
            suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Emulate_OSX))
    
    if ('TESTRUN' in os.environ) and ("FULL" in os.environ['TESTRUN']):  
            suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Deploy_Linux))
            suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Run_Linux))
            suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Device_Linux))       
            suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Debug_Linux)) 
            if 'Darwin' in platform.platform():
                suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Deploy_OSX))
                suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Run_OSX))
                suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Device_OSX))  
                suite.addTests(unittest.TestLoader().loadTestsFromTestCase(Debug_OSX))  
    
    # Smoke test runs only high priority tests             
    if ('TESTRUN' in os.environ) and ("SMOKE" in os.environ['TESTRUN']): 
        for test in suite:            
            if test._testMethodName.find('test_4') >= 0:
                setattr(test,test._testMethodName,lambda: test.skipTest('Skip negative tests in SMOKE TEST run.'))          
            if test._testMethodName.find('test_3') >= 0:
                setattr(test,test._testMethodName,lambda: test.skipTest('Skip low priority tests in SMOKE TEST run.')) 
            if test._testMethodName.find('test_2') >= 0:
                setattr(test,test._testMethodName,lambda: test.skipTest('Skip medium priority tests in SMOKE TEST run.')) 
                                                                               
    with open ("Report.html", "w") as f:
        descr = "Platform : {0};  nativescript-cli build version : {1}".format(platform.platform(), GetCLIBuildVersion())
        runner = HTMLTestRunner.HTMLTestRunner(stream=f, title='TNS_CLI_tests', description=descr)
        result = runner.run(suite)
    return result

if __name__ == '__main__':
    RunTests()
