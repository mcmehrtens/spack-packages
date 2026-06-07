# Copyright Spack Project Developers. See COPYRIGHT file for details.
#
# SPDX-License-Identifier: (Apache-2.0 OR MIT)

import re

from spack_repo.builtin.build_systems.go import GoPackage

from spack.package import *


class GoSh(GoPackage):
    """A shell parser, formatter, and interpreter. Supports POSIX
    Shell, Bash, Zsh and mksh."""

    homepage = "https://github.com/mvdan/sh"
    git = "https://github.com/mvdan/sh.git"
    url = "https://github.com/mvdan/sh/archive/refs/tags/v3.12.0.tar.gz"
    supplier = "Person: Daniel Martí (mvdan@mvdan.cc)"
    executables = ["^shfmt$"]

    maintainers("mcmehrtens")
    license("BSD-3-Clause", checked_by="mcmehrtens", when="@0.1:")

    version(
        "3.13.1",
        tag="v3.13.1",
        commit="2f3f5e36d9b0f8f14c998d50aa20a28832205ae8",
        get_full_repo=True,
    )
    version(
        "3.13.0",
        tag="v3.13.0",
        commit="5c4d285c3e8fa3b85137b34cec5ce66b98d97bdc",
        get_full_repo=True,
    )
    version("3.12.0", sha256="ac15f42feeba55af29bd07698a881deebed1cd07e937effe140d9300e79d5ceb")

    depends_on("go@1.25:", type="build", when="@3.13:")
    depends_on("go@1.23:", type="build", when="@3.12")

    variant("shfmt", default=True, description="Build and install shfmt")
    variant("gosh", default=False, description="Build and install gosh")
    conflicts("~shfmt~gosh", msg="One of shfmt or gosh must be specified")

    # each of these commands exposed by go-sh has a matching +<name> variant and a ./cmd/<name> dir
    commands = ("shfmt", "gosh")

    resource(
        url="https://proxy.golang.org/github.com/google/renameio/v2/@v/2.0.2.zip",
        sha256="4ea1f7ec938cc2206827f129f40ed9a266f4df30198fcff08de07da4b72276cb",
        when="@3.13.1+shfmt",
    )
    resource(
        url="https://proxy.golang.org/github.com/rogpeppe/go-internal/@v/1.14.1.zip",
        sha256="ab3d18283cef2f46ddfd489b6b14b970eb7dbbb642786f025ee1ac5291dc4e70",
        when="@3.13.1+shfmt",
    )
    resource(
        url="https://proxy.golang.org/mvdan.cc/editorconfig/@v/0.3.0.zip",
        sha256="aa50c43e789b025f04bea950f104314946d2faa5035442bf5f7415eb97860fe1",
        when="@3.13.1+shfmt",
    )
    resource(
        url="https://proxy.golang.org/golang.org/x/sys/@v/0.42.0.zip",
        sha256="99df0ad90183debc80aee0b7489648574c6baa0c1cf5da37aaf591cf2e2d426a",
        when="@3.13.1",
    )
    resource(
        url="https://proxy.golang.org/golang.org/x/term/@v/0.41.0.zip",
        sha256="91ca75a3f454d5ddede1f58c3e4fc8e169c6f3c037223ac0ac76e78234d22828",
        when="@3.13.1",
    )

    @classmethod
    def determine_version(cls, exe):
        output = Executable(exe)("--version", output=str, error=str)
        match = re.search(r"v?(\d+\.\d+\.\d+)", output)
        return match.group(1) if match else None

    @property
    def selected_commands(self):
        return [c for c in self.commands if self.spec.satisfies(f"+{c}")]

    @property
    def sanity_check_is_file(self):
        return [join_path("bin", c) for c in self.selected_commands]

    @property
    def ldflags(self):
        # v3.12 uses ldflags to set version; v3.13+ uses Go's VCS stamping
        if self.spec.satisfies("@:3.12"):
            return [f"-X main.version={self.spec.version}"]
        return []

    def build(self, spec: Spec, prefix: Prefix) -> None:
        with working_dir(self.build_directory):
            args = list(self.std_build_args)
            for cmd in self.selected_commands:
                args[args.index("-o") + 1] = cmd
                go("build", *args, f"./cmd/{cmd}")

    def install(self, spec: Spec, prefix: Prefix) -> None:
        with working_dir(self.build_directory):
            mkdirp(prefix.bin)
            for cmd in self.selected_commands:
                install(cmd, prefix.bin)
