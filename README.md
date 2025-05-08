Work-in-progress (WIP) tool to allow users to branch from and re-run the most recent commit while excluding chosen files (e.g., binary files).

There are three important commits:

* Root commit: the most recent commit.

* Intermediate commit: the commit records the addition of a newline to the end of each kept file and does `git rm` for each excluded file. Excluded files are copied so the user has backups, but those copies are not tracked. Copies are prefixed with "recommit-copy-".

* Final commit: restores the state of the kept files based on the root commit.

The user can then manually take action, such as switching to the old branch, removing the most recent commit (e.g., using `git rebase`), and squash merging the new branch into the old branch (e.g., `git merge --squash`).

* Tool is WIP, not guaranteed to be error-free.*
