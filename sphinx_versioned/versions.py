"""Collect and sort version strings."""

import os
import pathlib
from git import Repo
from loguru import logger as log


class GitVersions(object):
    def __init__(self, git_root, build_directory) -> None:
        self.git_root = git_root
        self.build_directory = pathlib.Path(build_directory)

        # for detached head
        self._active_branch = None

        if not self.build_directory.exists():
            self.build_directory.mkdir(parents=True, exist_ok=True)

        self.repo = Repo(git_root)
        if self.repo.bare:
            self.repo = Repo(os.getcwd())
            if self.repo.bare:
                log.error("Bare repo")
                exit(-1)
        log.success("Latched into the git repo")

        self._parse_branches()
        pass

    def _parse_branches(self) -> bool:
        self._raw_branches = self.repo.branches
        self._raw_tags = self.repo.tags
        self._branches = {x.name: self.build_directory / x.name for x in self._raw_branches}
        self._tags = {x.name: self.build_directory / x.name for x in self._raw_tags}
        return True

    @property
    def branches(self) -> dict:
        return {
            x: "../" + str(y.relative_to(self.build_directory) / "index.html")
            for x, y in self._branches.items()
        }

    @property
    def tags(self) -> dict:
        return {
            x: "../" + str(y.relative_to(self.build_directory) / "index.html") for x, y in self._tags.items()
        }

    def checkout(self, name, *args, **kwargs):
        self._active_branch = name
        return self.repo.git.checkout(name, *args, **kwargs)

    @property
    def active_branch(self, *args, **kwargs):
        if self._active_branch:
            return self._active_branch
        return self.repo.active_branch
