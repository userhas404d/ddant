from os.path import join
from os import listdir, getcwd, rmdir
from shutil import move

import git

# clone the repo
cloned_repo = git.Repo.clone_from(
                "git@github.com:userhas404d/ddant.git",
                "tempdir"
                )

# Move the cloned contents up a directory
# because we can't clone to an existing directory
for file_name in listdir("tempdir"):
    move(
        join(getcwd(), "tempdir", file_name),
        join(getcwd(), file_name)
        )
rmdir("tempdir")

# init the repo obj
repo = git.Repo(getcwd())

# create a new branch
new_branch = repo.create_head('new_branch')

# checkout the new branch
new_branch.checkout()

# add all files in working dir to a new commit in the newly created branch
repo.git.add('--all')
repo.git.commit(m='test message..')

# push the changes
repo.git.push('--set-upstream', 'origin', new_branch)

# open a PR
repo.create_pull("TEST PR", "TEST Body", 'master', True)
