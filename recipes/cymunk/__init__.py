"""
Author: Lawrence Du
E-mail: larrydu88@gmail.com
"""

from toolchain import CythonRecipe,shprint
import os
from os.path import join
import sh

class CymunkRecipe(CythonRecipe):
    version = 'master'
    url = 'https://github.com/kivy/cymunk/archive/{version}.zip'
    name = 'cymunk'
    library = "libcymunk.a"
    depends = ['hostpython']
    cythonize = True

    def prebuild_arch(self, arch):
        if self.has_marker("patched"):
            return
        self.apply_patch("fix-chipmunk-header.patch")
        self.set_marker("patched")

    '''
    def build_arch(self, arch):
        """
        Override build.arch to avoid calling setup.py here (Call it in 
        install() instead).
        """
        self.cythonize_build()
        self.biglink()
    '''

    def install(self):
        """
        Do the equivalent of
        python setup.py build_ext install
        while setting the proper environment variables
        
        """
        arch = list(self.filtered_archs)[0]
        build_env = self.get_recipe_env(arch)
        hostpython = sh.Command(self.ctx.hostpython)
        subdir_path = self.get_build_dir(arch.arch)
        setup_path = join(subdir_path,"setup.py")
        dest_dir = join (self.ctx.dist_dir, "root", "python3")
        build_env['PYTHONPATH'] = join(dest_dir, 'lib', 'python3.7', 'site-packages')

        #Note: Throws error if PATH is not set. I am not sure if this will cause problems
        # in other architectures.
        build_env['PATH']= os.environ.get('PATH')
        
        shprint(hostpython,
                setup_path,
                "build_ext",
                #"--compiler=mingw32", #note: throws clang error
                "install",
                "--prefix", dest_dir,
                _env=build_env)

recipe = CymunkRecipe()
