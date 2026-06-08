import os
import pathlib
import sys

from setuptools import Extension, setup

if sys.version_info < (3, 6):
    raise RuntimeError("aiohttp 3.x requires Python 3.6+")


NO_EXTENSIONS: bool = bool(os.environ.get("AIOHTTP_NO_EXTENSIONS"))
HERE = pathlib.Path(__file__).parent
IS_GIT_REPO = (HERE / ".git").exists()
IS_CPYTHON = sys.implementation.name == "cpython"


if not IS_CPYTHON:
    NO_EXTENSIONS = True


if IS_GIT_REPO and not (HERE / "vendor/llhttp/README.md").exists():
    print("Install submodules when building from git clone", file=sys.stderr)
    print("Hint:", file=sys.stderr)
    print("  git submodule update --init", file=sys.stderr)
    sys.exit(2)


# NOTE: makefile cythonizes all Cython modules

_BROTLI_VENDOR = "aiohttp/_vendored/brotli_src"
_brotli_extension = Extension(
    "aiohttp._vendored._brotli",
    sources=[
        f"{_BROTLI_VENDOR}/python/_brotli.c",
        f"{_BROTLI_VENDOR}/c/common/constants.c",
        f"{_BROTLI_VENDOR}/c/common/context.c",
        f"{_BROTLI_VENDOR}/c/common/dictionary.c",
        f"{_BROTLI_VENDOR}/c/common/platform.c",
        f"{_BROTLI_VENDOR}/c/common/shared_dictionary.c",
        f"{_BROTLI_VENDOR}/c/common/transform.c",
        f"{_BROTLI_VENDOR}/c/dec/bit_reader.c",
        f"{_BROTLI_VENDOR}/c/dec/decode.c",
        f"{_BROTLI_VENDOR}/c/dec/huffman.c",
        f"{_BROTLI_VENDOR}/c/dec/prefix.c",
        f"{_BROTLI_VENDOR}/c/dec/state.c",
        f"{_BROTLI_VENDOR}/c/dec/static_init.c",
        f"{_BROTLI_VENDOR}/c/enc/backward_references.c",
        f"{_BROTLI_VENDOR}/c/enc/backward_references_hq.c",
        f"{_BROTLI_VENDOR}/c/enc/bit_cost.c",
        f"{_BROTLI_VENDOR}/c/enc/block_splitter.c",
        f"{_BROTLI_VENDOR}/c/enc/brotli_bit_stream.c",
        f"{_BROTLI_VENDOR}/c/enc/cluster.c",
        f"{_BROTLI_VENDOR}/c/enc/command.c",
        f"{_BROTLI_VENDOR}/c/enc/compound_dictionary.c",
        f"{_BROTLI_VENDOR}/c/enc/compress_fragment.c",
        f"{_BROTLI_VENDOR}/c/enc/compress_fragment_two_pass.c",
        f"{_BROTLI_VENDOR}/c/enc/dictionary_hash.c",
        f"{_BROTLI_VENDOR}/c/enc/encode.c",
        f"{_BROTLI_VENDOR}/c/enc/encoder_dict.c",
        f"{_BROTLI_VENDOR}/c/enc/entropy_encode.c",
        f"{_BROTLI_VENDOR}/c/enc/fast_log.c",
        f"{_BROTLI_VENDOR}/c/enc/histogram.c",
        f"{_BROTLI_VENDOR}/c/enc/literal_cost.c",
        f"{_BROTLI_VENDOR}/c/enc/memory.c",
        f"{_BROTLI_VENDOR}/c/enc/metablock.c",
        f"{_BROTLI_VENDOR}/c/enc/static_dict.c",
        f"{_BROTLI_VENDOR}/c/enc/static_dict_lut.c",
        f"{_BROTLI_VENDOR}/c/enc/static_init.c",
        f"{_BROTLI_VENDOR}/c/enc/utf8_util.c",
    ],
    include_dirs=[f"{_BROTLI_VENDOR}/c/include"],
)

extensions = [
    Extension("aiohttp._websocket", ["aiohttp/_websocket.c"]),
    Extension(
        "aiohttp._http_parser",
        [
            "aiohttp/_http_parser.c",
            "aiohttp/_find_header.c",
            "vendor/llhttp/build/c/llhttp.c",
            "vendor/llhttp/src/native/api.c",
            "vendor/llhttp/src/native/http.c",
        ],
        define_macros=[("LLHTTP_STRICT_MODE", 0)],
        include_dirs=["vendor/llhttp/build"],
    ),
    Extension("aiohttp._helpers", ["aiohttp/_helpers.c"]),
    Extension("aiohttp._http_writer", ["aiohttp/_http_writer.c"]),
    _brotli_extension,
]


build_type = "Pure" if NO_EXTENSIONS else "Accelerated"
if IS_CPYTHON and NO_EXTENSIONS:
    setup_kwargs = {"ext_modules": [_brotli_extension]}
elif NO_EXTENSIONS:
    setup_kwargs = {}
else:
    setup_kwargs = {"ext_modules": extensions}

print("*********************", file=sys.stderr)
print("* {build_type} build *".format_map(locals()), file=sys.stderr)
print("*********************", file=sys.stderr)
setup(**setup_kwargs)
