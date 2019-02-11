from os.path import join
from toolchain import CythonRecipe,shprint
from toolchain import shprint
import os
import sh
from os import walk, chdir
import fnmatch
import shutil
import sys


class PymunkRecipe(CythonRecipe):
    name = "pymunk"
    version = '5.4.2'
    url = 'https://pypi.python.org/packages/5e/bd/e67edcffdee3d0a1e3ebf0050bb9746a61d616f5502ceedddf0f7fd0a896/pymunk-{version}.zip'
    depends = ['cffi', 'host_setuptools']
    library = "libpymunk.a"
    cythonize = False

    def get_recipe_env(self, arch):
        env = super(PymunkRecipe, self).get_recipe_env(arch)
        # env['CFLAGS'] = '' + env['OTHER_CFLAGS']
        env['LD'] = '/Users/ivc/kivy/.buildozer/ios/platform/kivy-ios/tools/liblink'
        # env['LDFLAGS'] += " -shared -llog"
        # env['LDFLAGS'] += ' -L{}'.format(join(self.ctx.ndk_platform, 'usr', 'lib'))
        # env['LDFLAGS'] += " --sysroot={}".format(self.ctx.ndk_platform)
        # env['LIBS'] = env.get('LIBS', '') + ' -landroid'
        # env['LDFLAGS'] = env['LDFLAGS'].replace('--sysroot /Applications/Xcode.app/Contents/Developer/Platforms/iPhoneSimulator.platform/Developer/SDKs/iPhoneSimulator12.1.sdk', '').replace('-miphoneos-version-min=7.0', '')
        print('Env pymunk: ')
        for x,i in env.items():
            print(x,i)
        print('-'*30)
        return env

    def install(self):
        print('-'*30, '\nInstall')
        arch = [arch for arch in self.filtered_archs if arch.arch == 'arm64'][0]
        build_dir = self.get_build_dir(arch.arch)
        os.chdir(build_dir)
        # manually create expected directory in build directory
        scripts_dir = join("build", "scripts-3.7")
        if not os.path.exists(scripts_dir):
            os.makedirs(scripts_dir)
        hostpython = sh.Command(self.ctx.hostpython)

        # install cffi in hostpython
        #
        # XXX: installs, module import works, but FFI fails to instanciate:
        #
        # myhost:kivy-ios user$ ./dist/hostpython/bin/python
        # Could not find platform dependent libraries <exec_prefix>
        # Consider setting $PYTHONHOME to <prefix>[:<exec_prefix>]
        # Python 2.7.1 (r271:86832, Nov  4 2016, 10:41:44)
        # [GCC 4.2.1 Compatible Apple LLVM 7.3.0 (clang-703.0.31)] on darwin
        # Type "help", "copyright", "credits" or "license" for more information.
        # >>> import cffi
        # >>> cffi.api.FFI()
        # Traceback (most recent call last):
        #   File "<stdin>", line 1, in <module>
        #   File "/.../kivy-ios/dist/hostpython/lib/python2.7/site-packages/cffi/api.py", line 56, in __init__
        #     import _cffi_backend as backend
        # ImportError: dynamic module does not define init function (init_cffi_backend)
        #
        #r = self.get_recipe('hostlibffi', self.ctx)
        #build_env = r.get_recipe_env(arch)
        #args = [hostpython, "setup.py", "install"]
        #shprint(*args, _env=build_env)

        # install cffi in root site packages
        build_env = self.get_recipe_env(arch)
        dest_dir = join(self.ctx.dist_dir, "root", "python3")
        pythonpath = join(dest_dir, 'lib', 'python3.7', 'site-packages')
        build_env['PYTHONPATH'] = pythonpath
        args = [hostpython, "setup.py", "build_ext", "install", "--prefix", dest_dir]
        shprint(*args, _env=build_env)

recipe = PymunkRecipe()
