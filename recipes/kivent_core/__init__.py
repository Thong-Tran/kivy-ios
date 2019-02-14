"""
Author: Lawrence Du
E-mail: larrydu88@gmail.com
"""

from toolchain import CythonRecipe, shprint
import sh
from os.path import join, abspath
from os import environ, chdir, walk, getcwd
import fnmatch
import logging

logger = logging.getLogger(__name__)


class KiventCoreRecipe(CythonRecipe):
    version = 'master'
    url = 'https://github.com/kivy/kivent/archive/{version}.zip'
    name = 'kivent_core'
    library = "libkivent_core.a"
    depends = ['libffi','kivy'] #note: unsure if libffi is necessary here
    pre_build_ext=False
    subbuilddir = False
    cythonize = True
    pbx_frameworks = ["OpenGLES"] #note: This line may be unnecessary


    def get_recipe_env(self, arch):
        env = super(KiventCoreRecipe,self).get_recipe_env(arch)
        env['PATH'] = env.get('PATH', '')
        env['CYTHONPATH'] = self.get_recipe(
            'kivy', self.ctx).get_build_dir(arch.arch)
        dest_dir = join (self.ctx.dist_dir, "root", "python3")
        env['PYTHONPATH'] = join(dest_dir, 'lib', 'python3.7', 'site-packages')

        return env


    def get_build_dir(self,arch, sub=False):
        """
        Call this to get the correct build_dir, where setup.py is located which is
        actually under modules/core/setup.py
        """
        builddir = super(KiventCoreRecipe, self).get_build_dir(str(arch))
        if sub or self.subbuilddir:
            core_build_dir = join (builddir, 'modules', 'core')
            logger.info("Core build directory is located at {}".format(core_build_dir))
            return core_build_dir
        else:
            logger.info("Building in {}".format(builddir))
            return builddir

    def build_arch(self, arch):
        """
        Override build.arch to avoid calling setup.py here (Call it in
        install() instead).
        """

        build_env = self.get_recipe_env(arch)
        hostpython = sh.Command(self.ctx.hostpython)
        self.subbuildir = True
        if self.pre_build_ext:
            try:
                shprint(hostpython, "setup.py", "build_ext", "-g",
                        _env=build_env)
            except:
                pass

        cyenv = environ.copy()
        # cyenv['PATH'] = environ['PATH']
        cyenv['CYTHONPATH'] = self.get_recipe(
            'kivy', self.ctx).get_build_dir(arch.arch)
        dest_dir = join (self.ctx.dist_dir, "root", "python3")
        cyenv['PYTHONPATH'] = join(dest_dir, 'lib', 'python3.7', 'site-packages')
        # for i,j in cyenv.items():
        #     print(i,j, '\n')
        self.cythonize_build(cyenv, build_dir="./modules/core/kivent_core")

        cwd = getcwd()
        build_dir = self.get_build_dir(arch.arch,sub=True)
        logger.info("Building kivent_core {} in {}".format(arch.arch,build_dir))
        chdir(build_dir)
        shprint(hostpython, "setup.py", "build_ext", "-g",
                _env=build_env)
        self.biglink()
        self.subbuilddir=False
        chdir(cwd)


    def install(self):
        """
        This method simply builds the command line call for calling
        kivent_core/modules/core/setup.py

        This constructs the equivalent of the command
        "$python2.7 setup.py build_ext install"
        only with the environment variables altered for each different architecture
        The appropriate version of kivy also needs to be added to the path, and this
        differs for each architecture (i386, x86_64, armv7, etc)

        Note: This method is called by build_all() in toolchain.py

        """
        arch = list(self.filtered_archs)[0]

        build_dir = self.get_build_dir(arch.arch,sub=True)
        logger.info("Building kivent_core {} in {}".format(arch.arch,build_dir))
        chdir(build_dir)
        hostpython = sh.Command(self.ctx.hostpython)

        #Get the appropriate environment for this recipe (including CYTHONPATH)
        #build_env = arch.get_env()
        build_env = self.get_recipe_env(arch)

        dest_dir = join (self.ctx.dist_dir, "root", "python3")
        build_env['PYTHONPATH'] = join(dest_dir, 'lib', 'python3.7', 'site-packages')

        #Add Architecture specific kivy path for 'import kivy' to PYTHONPATH
        arch_kivy_path = self.get_recipe('kivy', self.ctx).get_build_dir(arch.arch)
        build_env['PYTHONPATH'] = join( build_env['PYTHONPATH'],':',arch_kivy_path)

        #Make sure you call kivent_core/modules/core/setup.py
        subdir_path = self.get_build_dir(str(arch),sub=True)
        setup_path = join(subdir_path,"setup.py")


        #Print out directories for sanity check
        logger.info("ENVS", build_env)
        logger.info("ROOT",self.ctx.root_dir)
        logger.info("BUILD",self.ctx.build_dir)
        logger.info("INCLUDE", self.ctx.include_dir)
        logger.info("DISTDIR", self.ctx.dist_dir)
        logger.info("ARCH KIVY LOC",self.get_recipe('kivy', self.ctx).get_build_dir(arch.arch))

        shprint(hostpython, setup_path, "build_ext", "install", _env=build_env)

    def cythonize_file(self, env, build_dir, filename):
        short_filename = filename
        if filename.startswith(build_dir):
            short_filename = filename[len(build_dir) + 1:]
        logger.info(u"Cythonize {}".format(short_filename))
        cmd = sh.Command(join(self.ctx.root_dir, "tools", "cythonize.py"))
        shprint(sh.Command('python3'), cmd, filename, _env=env)

    def cythonize_build(self, env, build_dir="."):
        for root, dirnames, filenames in walk(build_dir):
            for filename in fnmatch.filter(filenames, "*.pyx"):
                self.cythonize_file(env, build_dir, abspath(join(root, filename)))


recipe = KiventCoreRecipe()
