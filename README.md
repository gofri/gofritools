gofritools - Gofri Toolkit
==========================
__A set of tools for working and investigating code.__

## Warnings


* gofritools is provided as-is, with no guarantee whatsoever. It is not recommended for anyone to use or even examine.
* The code is poorly written and misdesigned, not tested nor documented, and not at all supported by anyone, including (especially) gofri.
* Any usage of this toolkit is on your own responsibility, including side effects like accidental deletion of files, destroying your computer, etc.
* Please, do not use this. Do not expect anyone to help you with it. It does not even worth the time to look at.



## If, for some wierd reason, you decide to use it, do note the following prerequisites (you can use docker quick install, but it takes forever with apt update):
#### Required Python Version:
* python3.8

#### Required Python Packages (pip):
* colorama
* argcomplete

#### Required Utilities (apt-get):
* xclip
* colorized-logs (ansi2txt)

## Docker quick install
wget -O - https://raw.githubusercontent.com/gofri/gofritools/master/install.sh | bash

NOTE:
	for mac, use mac_install.sh. You also need:
	- xquartz up and running + enable network connection
	- add / to Docker-Desktop file sharing
###

## General TODOs:
- element: support integer (0=path, 1=line, etc.)
- argparse needs to be refactored: it's basically good, but needs a module for itself.

### Features
* Add support for sending notification to user when something finishes (send-notify)
* TODO searcher: -iw TODO|XXX|BUG
* passthrough: expects and ignores all args; forwards stdin to stdout
* add stdin from cmdargs (this way also allow to override stdin)

#### Git-specific
* Add check&fix trailing spaces for git diff.
* GitCommit: represent a single git commit (lazy load git diff per need)
* GitLog: Print multiple git commits, works with graphs too. Then we'll use Select to choose commit.
* git branchshow: show entire branch (default --base-branch=master, ref=HEAD)
* git rebase-branch: auto-pick all commits to push
* both git-log and git-branch use git-commit-list underneath
* git diff/etc: act on git-commit-list as well - e.g. diff of entire branch 
* git blame: blame by line when using grep, etc.

# Internal: Arch

## Program stack
* L0: SHELL: <BASH|SSH|etc.> the shell to run on
* L1: PROG: <GREP|FIND|VIM|MELD...> programs and pure logic
* L2: VIRT: <VIRT_*> translate all Res types from prev output to cur input # MISSING: meta={prev_prog, prev_args, etc.}. should be done via representation of Action{prog, agrs, output}
* L3: PIPE: <PIPE|ADD|COMMON|etc.> Link two programs - either pipe stdout to stdin or add/find-common output of two programs (add/common start a new stack)
* L4: STACK: A stack of piped programs (of the form args+meta+output), with running index, etc.
* L5: MULTILINE: A combination of multiple stacks, each representing a different history
* L6: INTERACTIVE: Run multi-line interactive mode. You can switch between lines and merge/add/etc. them (via ADD/COMMON/etc. actions on the HEAD of each stack)

## argparse options
[REAL] = [real programs and general flags]
[VIRT] = [select/element/etc.] << the options depend on the specific type of Result in stdin (SearchResult/GitCommit/etc.)
[INTERACTIVE] = [stepb/stepf/etc.]
[MEDIUM] = [interactive/batch]

The main subparser is the medium choice.
For single=stack mode, just enter the flags.
Passthrough/Interactive modes are implemented using parse_known_args() trick.
Interactive doubles the trick:
- It accepts the general flags (e.g. verbosity) and sets them as default flags during the session.
- It assumes that the rest of the unkown commands are the first command to execute.
  This way calling e.g. `main.py interactive grep ...' enters interactive mode and runs grep as the first command.

<MEDIUM>
	<STACK>
		<FIRST_COMMAND> [REAL]
		<REST_OF_THE_COMMANDS> [REAL] [VIRT] [ # Detect via stdin.isatty()
	<INTERACTIVE> 
		<FIRST_COMMAND> [REAL] + [INTERACTIVE]
		<REST_OF_THE_COMMANDS> [REAL] + [VIRT] + [INTERACTIVE]
		
## Design&Code Reusability
By keeping both the metadata (cmd+args) and the data (cmd output) in the pipe,
while keeping View-related info inside the interactice layer,
we enable a single implementation for both modes.
View-related info might include: show/hide caller/context/etc.
To simplify further, existing functionality (e.g. --caller arg) may become pluggable as a view property.

## argparse output option
The output options are mutually exclusive:
- raw-text: the least-edited version of the content.
- humanize: a human-readable colored version of the content.
- json: json representation of the data.
- pickle: pickle representation of the data.

Note that pickle is always used for piping in bash.
