from toolchain import CythonRecipe, shprint
from os.path import join, exists
from os import chdir
import sh
import shutil

import logging

class FFPyplayerRecipe(CythonRecipe):
    version = "v4.1.0"
    url = "https://github.com/michele-comitini/ffpyplayer/archive/visibility-of-functions-in-misc.zip"
    library = "libffpyplayer.a"
    depends = ["python"]
    pbx_frameworks = [
        "CoreVideo", "CoreMedia", "CoreImage", "AVFoundation", "UIKit",
        "CoreMotion", 'VideoToolbox']
    # pbx_libraries = ["libiconv"]
    pre_build_ext = True

    def prebuild_arch(self, arch):
        # common to all archs
        if  self.has_marker("patched"):
            return
        self.apply_patch('fix-cython.patch')

        mobile_ffmpeg_git = 'https://github.com/tanersener/mobile-ffmpeg/archive/v4.2.zip'
        a
        ffmpeg_config = (
        ' --disable-armv7 --disable-armv7s --disable-i386 --disable-arm64e'
        ' --enable-ios-audiotoolbox --enable-ios-avfoundation --enable-ios-coreimage  --enable-ios-bzip2 --enable-ios-videotoolbox --enable-ios-zlib'
        ' --enable-gmp'
        ' --enable-opus --enable-shine --enable-soxr --enable-twolame --enable-speex'
        ' --enable-libvpx --enable-snappy'
        )

    def get_recipe_env(self, arch):
        env = super(FFPyplayerRecipe, self).get_recipe_env(arch)
        env["CC"] += " -I{} -I{}".format(
            join(self.ctx.dist_dir, "include", arch.arch, "libffi"),
            join(self.ctx.dist_dir, "include", "common", "sdl2_mixer")
        )
        env['CFLAGS'] += ' -Wno-implicit-function-declaration -fno-strict-aliasing'

        env["SDL_INCLUDE_DIR"] = join(self.ctx.dist_dir, "include",
            "common", "sdl2")
        env["SDL_LIB_DIR"] = join(self.ctx.dist_dir, 'lib')

        # env["FFMPEG_INCLUDE_DIR"] = join(self.ctx.dist_dir, "include",
        #                                 arch.arch, "ffmpeg")
        # env["FFMPEG_LIB_DIR"] = join(self.get_recipe(
        #     'ffmpeg', self.ctx).get_build_dir(arch.arch), "dist", 'lib')
        env["FFMPEG_INCLUDE_DIR"] = '/Users/ivc/kivy/mobile-ffmpeg/prebuilt/ios-universal/ffmpeg-universal/include'
        env["FFMPEG_LIB_DIR"] = '/Users/ivc/kivy/mobile-ffmpeg/prebuilt/ios-universal/ffmpeg-universal/lib'
        env["CONFIG_POSTPROC"] = "0"

        env["USE_SDL2_MIXER"] = '1'
        env['HAS_SDL2'] = '1'
        # import sys
        # env['PYTHONPATH'] = '/Users/ivc/kivy/.env3/lib/python3.7/site-packages'

        return env

    def install_python_package(self, name=None, env=None, is_dir=True):
        """Automate the installation of a Python package into the target
        site-packages.

        It will works with the first filtered_archs, and the name of the recipe.
        """
        arch = self.filtered_archs[0]
        if name is None:
            name = self.name
        if env is None:
            env = self.get_recipe_env(arch)
        logging.info("Install {} into the site-packages".format(name))
        build_dir = self.get_build_dir(arch.arch)
        chdir(build_dir)
        hostpython = sh.Command(self.ctx.hostpython)
        iosbuild = join(build_dir, "iosbuild")

        # Fix error: bad install directory or PYTHONPATH
        # You are attempting to install a package to a directory that is not
        # on PYTHONPATH and which Python does not read ".pth" files from.
        cmd = sh.Command("sed")
        shprint(cmd, "-i", "", "s/setuptools/distutils.core/g", "./setup.py", _env=env)

        shprint(hostpython, "setup.py", "install", "-O2",
                "--prefix", iosbuild,
                _env=env)
        dest_dir = join(self.ctx.site_packages_dir, name)
        #self.remove_junk(iosbuild)
        if is_dir:
            if exists(dest_dir):
                shutil.rmtree(dest_dir)
            func = shutil.copytree
        else:
            func = shutil.copy
        func(
            join(iosbuild, "lib",
                 self.ctx.python_ver_dir, "site-packages", name),
            dest_dir)


recipe = FFPyplayerRecipe()

