# Cinema 4D Version Manager

C4D Version Manager is a tiny GUI app that finds and collects all your Cinema 4D instances in one place and helps searching and managing them more efficiently comparing to the common built-in tools.

<img src="/docs/screenshot_main.png" width="640" height="529" />

## Getting Started

### Pre-built package

1. Download latest version from [Releases](https://github.com/wi1k1n/cinema4d_version_manager/releases)
2. Add some search paths to the list (d&d from explorer works), e.g. *C:\Program Files* and *D:\Downloads*
3. Save preferences using [Save Preferences] button
4. Close preferences and rescan your paths: Edit -> Rescan (or Ctrl+F5)
5. Your c4d installations/packages should appear as tiles
6. You can already run C4D instances by clicking on icon (or via context menu on them)
7. \* Learn shortcuts to make your workflow more efficient (Help -> Shortcuts)

#### Tags workflow

1. Create tags in tags window (*double click*)
2. Assign them to c4d tiles (d&d).
3. Use *Shift + d&d* to remove tag
4. Save tags and tag assignments using *Ctrl+S*

#### Managing C4D processes

1. Clicking on tile can run/restart/kill C4D (check shortcuts)
2. Colored square flag shows current C4D state:
	- 🟩 - c4d is currently running
	- 🟦 - c4d was closed and detached
	- 🟥 - c4d was forcely killed

### From source code

The following dependencies are required:

* Python 3 (3.10.0 is originally used)
* [PyQt5](https://pypi.org/project/PyQt5/)
* [pywin32](https://pypi.org/project/pywin32/)
* [keyboard](https://pypi.org/project/keyboard/)
* [requests](https://github.com/psf/requests)

For packaging additional dependencies are required:

* [GitPython](https://github.com/gitpython-developers/GitPython)
* [PyInstaller](https://pyinstaller.org/en/stable/)
* [Pillow](https://github.com/python-pillow/Pillow)

## Resources:
* Awesome Ronald's C4D icons: https://backstage.maxon.net/topic/3064/cinema-4d-icon-pack

### TODOs:
* [○] C4D instances interaction:
	* [X] Show which c4d instances status on tiles: currently running, closed
	* [X] Allow to activate, kill, restart c4d instances
		* [ ] Activate window (virtual desktops?)
	* [ ] Enable/Disable actions depending on current state (no restart before running)
	* [X] Extend grouping to group by state: running, killed, closed, not started
	* [ ] Kill all action
* [○] Group/Filter/Sort
	* [○] Create layout
	* [ ] Add functionality to the layout
	* [X] Adjust appearing behavior (executing action should toggle tag/filter window state, rather than always openning it)
* [○] Tag window improvements
	* [ ] Space bar pressed while dragging applies tag but doesn't break dragging
	* [X] Means to sort tags (e.g. via context menu)
	* [ ] default folded/unfolded group when grouping by tags
	* [ ] tags customization opportunities:
		* [ ] tag contains arguments to run c4d with
		* [ ] tag contains sheets of arguments that are injected into context menu
		* [ ] can be custom scripts to run before running c4d (overkill!)
	* [X] group to the tag in the tag manager (change grouping to "group by tag", + fold all except selected tag)
* [ ] Auto saving options
	* [ ] Store last selected group/filter/sort settings
	* [ ] Store last layout (tags & filter/sort window states)
	* [ ] Store device where the window is positioned
* [○] Preferences
	* [X] layouts and layout behavior
	* [X] saving/loading preferences
	* [X] functionality: app behavior reflects settings
	* [ ] prepare a list of c4d that are in cache but not found on system anymore
	* [ ] Register global shortcut to open window from background
		* [ ] Hide on lost focus checkbox in preferences (have doubts it'd be convenient, may be worth testing)
	* ~~[ ] custom regex instead of "trim c4d version"~~
	* [X] Add "Nothing found, change search paths and Rescan (Ctrl + F5)" label if no cinema was found
* [ ] Regular Tiles view
	* [ ] Show string from build.txt
	* [X] double click on empty space -> default grouping (set default in preferences)
	* [ ] try saving scrollbar position, such that after updatetiles it stays where it was
	* [X] Revisit modifiers with clicks -> unify UX-wise
	* [ ] Small triangle sign on top-right corner of each tile, showing that c4d is installed
* [ ] Tiles desktop view
	* [ ] A separate tab with draggable c4d tiles that work with search, but doesn't have any grouping options
* [X] Shortcuts window in 'Help' section
* [X] Change gitlab to github logo, + private -> public access
* [X] Ctrl+Shift+B -> Bugs tracking -> Open issues on github/gitlab
* [ ] Ctrl+O -> add search path and open preferences
* [X] Esc -> Close shortcuts window

### Bugs:
* [X] Color picker for tags is behind edit window
* [ ] Inconsistent disabling entries in preferences on load
* [X] Normalize slashes in paths

### Group/Filter/Sort research
* [+] Grouping - Single layer (at least for now)
	* [+] Search paths
	* [+] Tags
	* [+] Major versions
	* ~~Package/installer (? same as search paths?)~~
	* [-] New installations

* Filtering - with negation
	* Search string
	* plus Same as grouping

* Sorting
	* By version (major, complex?)
	* By date (creation date)
	* Tags custom order / alphabetically / by number of tags

Grouping Filtering Sorting (GFS) should inherit preset concept (one can save these settings as presets for quickly applying GFS settings)