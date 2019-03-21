from toolchain import CythonRecipe, shprint
from os.path import join
import sh


class FFPyplayerRecipe(CythonRecipe):
    version = "v4.0.1"
    url = "https://github.com/matham/ffpyplayer/archive/{version}.zip"
    library = "libffpyplayer.a"
    depends = ["python", "ffmpeg"]
    pbx_frameworks = [
        "CoreVideo", "CoreMedia", "CoreImage", "AVFoundation", "UIKit",
        "CoreMotion"]
    pbx_libraries = ["libiconv"]
    pre_build_ext = True

    def prebuild_arch(self, arch):
        # common to all archs
        if  self.has_marker("patched"):
            return
        self.apply_patch('fix-cython.patch')
        # self.apply_patch('fix.patch')

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

        env["FFMPEG_INCLUDE_DIR"] = join(self.ctx.dist_dir, "include",
            arch.arch, "ffmpeg")
        env["FFMPEG_LIB_DIR"] = join(self.get_recipe(
            'ffmpeg', self.ctx).get_build_dir(arch.arch), "dist", 'lib')
        # env["CONFIG_POSTPROC"] = "0"

        env["USE_SDL2_MIXER"] = '1'
        env['HAS_SDL2'] = '1'
        # env["OTHER_CFLAGS"] += ' -I'+join(self.ctx.dist_dir, "include",
        #     "common", "sdl2_mixer")
        return env


recipe = FFPyplayerRecipe()

