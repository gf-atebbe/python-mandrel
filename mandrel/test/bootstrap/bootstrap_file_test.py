import contextlib
import os
import unittest
import mandrel.exception
from mandrel.test import utils
from test.test_support import EnvironmentVarGuard

class TestBootstrapFile(utils.TestCase):
    def testNoFile(self):
        with utils.workdir(dir='~') as path:
            self.assertRaises(mandrel.exception.MissingBootstrapException, utils.refresh_bootstrapper)

    def testRootImmediate(self):
        with utils.bootstrap_scenario(dir='~') as spec:
            utils.refresh_bootstrapper()
            self.assertEqual(spec[0], mandrel.bootstrap.ROOT_PATH)
            self.assertEqual(spec[1], mandrel.bootstrap.BOOTSTRAP_FILE)

    def testRootNested(self):
        with utils.bootstrap_scenario(dir='~') as spec:
            with utils.tempdir(dir=spec[0]) as nested_a:
                with utils.workdir(dir=nested_a) as nested_b:
                    utils.refresh_bootstrapper()
                    self.assertEqual(spec[0], mandrel.bootstrap.ROOT_PATH)
                    self.assertEqual(spec[1], mandrel.bootstrap.BOOTSTRAP_FILE)

    def testFileEvaluation(self):
        with utils.bootstrap_scenario(text="bootstrap.EVAL_CHECK = bootstrap\nconfig.EVAL_CHECK = config") as spec:
            utils.refresh_bootstrapper()
            # We check that the bootstrap file is evaluated in a scope with:
            # - mandrel.bootstrap bound to local name "bootstrap"
            # - mandrel.config bound to local name "config"
            self.assertIs(mandrel.bootstrap, mandrel.bootstrap.EVAL_CHECK)
            self.assertIs(mandrel.config, mandrel.config.EVAL_CHECK)
            

    def testDefaultSearchPath(self):
        with utils.bootstrap_scenario(dir='~') as spec:
            utils.refresh_bootstrapper()
            self.assertEqual([spec[0]], list(mandrel.bootstrap.SEARCH_PATHS))

    def testDefaultLoggingConfig(self):
        with utils.bootstrap_scenario(dir='~') as spec:
            utils.refresh_bootstrapper()
            self.assertEqual('logging.cfg', mandrel.bootstrap.LOGGING_CONFIG_BASENAME)

    def testNoOSEnv(self):
        """
        Base case: neither variable is defined (the original behaviors)
        """
        with EnvironmentVarGuard() as env:
            with utils.bootstrap_scenario(dir='~') as spec:
                utils.refresh_bootstrapper()
                self.assertEqual(spec[0], mandrel.bootstrap.ROOT_PATH)
                self.assertEqual(spec[1], mandrel.bootstrap.BOOTSTRAP_FILE)

    def testBothOSEnv(self):
        """
        Root is specified, bootstrapper is specified, the specified file does not exist in the specified root
        """
        with EnvironmentVarGuard() as env:
            env.set('MANDREL_ROOT', '/blah')
            env.set('MANDREL_BOOTSTRAP_NAME', 'bootstrapper.py')

            utils.refresh_bootstrapper()
            self.assertEqual(os.getenv('MANDREL_ROOT'), mandrel.bootstrap.ROOT_PATH)
            expected = os.path.join(os.getenv('MANDREL_ROOT'), os.getenv('MANDREL_BOOTSTRAP_NAME'))
            self.assertEqual(expected, mandrel.bootstrap.BOOTSTRAP_FILE)
            self.assertEqual(['/blah'], mandrel.bootstrap.SEARCH_PATHS._list)

    def testBothOSEnvFileExists(self):
        """
        Root is specified, bootstrapper is specified, the specified file exists in the specified root
        """
        with EnvironmentVarGuard() as env:
            env.set('MANDREL_BOOTSTRAP_NAME', 'bootstrapper.py')
            with utils.bootstrap_scenario(text='bootstrap.SEARCH_PATHS.append("/blah/myconf")', dir='~') as spec:
                env.set('MANDREL_ROOT', spec[0])

                utils.refresh_bootstrapper()
                self.assertEqual(spec[0], mandrel.bootstrap.ROOT_PATH)
                expected = os.path.join(spec[0], os.getenv('MANDREL_BOOTSTRAP_NAME'))
                self.assertEqual(expected, mandrel.bootstrap.BOOTSTRAP_FILE)
                self.assertEqual([spec[0], '/blah/myconf'], mandrel.bootstrap.SEARCH_PATHS._list)

    def testOSEnvNoBootstrapName(self):
        """
        Root is specified, bootstrapper is not, Mandrel.py is not present in specified root (should get basic defaults)
        """
        with EnvironmentVarGuard() as env:
            env.set('MANDREL_ROOT', '/blah')

            utils.refresh_bootstrapper()
            self.assertEqual(os.getenv('MANDREL_ROOT'), mandrel.bootstrap.ROOT_PATH)
            expected = os.path.join(os.getenv('MANDREL_ROOT'), 'Mandrel.py')
            self.assertEqual(expected, mandrel.bootstrap.BOOTSTRAP_FILE)
            self.assertEqual(['/blah'], mandrel.bootstrap.SEARCH_PATHS._list)

    def testOSEnvNoBootstrapNameFileExists(self):
        """
        Root is specified, bootstrapper is not, Mandrel.py is present in specified root (should parse the file it finds)
        """
        with EnvironmentVarGuard() as env:
            with utils.bootstrap_scenario(text='bootstrap.SEARCH_PATHS.append("/blah/myconf")', dir='~') as spec:
                env.set('MANDREL_ROOT', spec[0])
                utils.refresh_bootstrapper()
                self.assertEqual(os.getenv('MANDREL_ROOT'), mandrel.bootstrap.ROOT_PATH)
                self.assertEqual(spec[1], mandrel.bootstrap.BOOTSTRAP_FILE)
                self.assertEqual([spec[0], '/blah/myconf'], mandrel.bootstrap.SEARCH_PATHS._list)

    def testOSEnvNoMandrelRoot(self):
        """
        Root is not specified, bootstrapper is specified,
        the specified file does not exist within the file system hierarchy
        """
        with EnvironmentVarGuard() as env:
            env.set('MANDREL_BOOTSTRAP_NAME', 'bootstrapper.py')
            with utils.workdir(dir='~') as path:
                self.assertRaises(mandrel.exception.MissingBootstrapException, utils.refresh_bootstrapper)

    def testOSEnvNoMandrelRootFileExists(self):
        """
        Root is not specified, bootstrapper is specified, the specified file exists
        """
        with EnvironmentVarGuard() as env:
            env.set('MANDREL_BOOTSTRAP_NAME', 'bootstrapper.py')
            with utils.bootstrap_scenario(text='bootstrap.SEARCH_PATHS.append("/blah/myconf")', dir='~') as spec:
                utils.refresh_bootstrapper()
                self.assertEqual(spec[0], mandrel.bootstrap.ROOT_PATH)
                expected = os.path.join(spec[0], os.getenv('MANDREL_BOOTSTRAP_NAME'))
                self.assertEqual(expected, mandrel.bootstrap.BOOTSTRAP_FILE)
                self.assertEqual([spec[0], '/blah/myconf'], mandrel.bootstrap.SEARCH_PATHS._list)

            # Create a folder structure such that starting search path is several levels
            # below where the bootstrap file exists.
            # Make sure that the bootstrap file is found and parsed
            with utils.nested_bootstrap_scenario(text='bootstrap.SEARCH_PATHS.append("/blah/myconf")', dir='~') as spec:
                utils.refresh_bootstrapper()
                self.assertEqual(spec[0], mandrel.bootstrap.ROOT_PATH)
                expected = os.path.join(spec[0], os.getenv('MANDREL_BOOTSTRAP_NAME'))
                self.assertEqual(expected, mandrel.bootstrap.BOOTSTRAP_FILE)
                self.assertEqual([spec[0], '/blah/myconf'], mandrel.bootstrap.SEARCH_PATHS._list)
