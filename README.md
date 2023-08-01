### Useful links:
* https://backstage.maxon.net/topic/3064/cinema-4d-icon-pack
* Save/restore UI layout: https://stackoverflow.com/questions/23279125/python-pyqt4-functions-to-save-and-restore-ui-widget-values

### TODOs:
* C4D instances interaction:
	* Show which c4d instances status on tiles: currently running, closed
	* Allow to activate, kill, restart c4d instances
	* Enable/Disable actions depending on current state (no restart before running)
	* Extend grouping to group by state: running, killed, closed, not started
* Group/Filter/Sort
	* Create layout
	* Add functionality to the layout
	* Adjust appearing behavior (executing action should toggle tag/filter window state, rather than always openning it)
* Tag window improvements
	* Space bar pressed while dragging applies tag but doesn't break dragging
	* default folded/unfolded group when grouping by tags
	* tags customization opportunities:
		* tag contains arguments to run c4d with
		* tag contains sheets of arguments that are injected into context menu
		* can be custom scripts to run before running c4d (overkill!)
* Auto saving options
	* Store last selected group/filter/sort settings
	* Store last layout (tags & filter/sort window states)
	* Store device where the window is positioned
* Preferences
	* layouts and layout behavior
	* saving/loading preferences
	* functionality: app behavior reflects settings
	* prepare a list of c4d that are in cache but not found on system anymore
	* Register global shortcut to open window from background
		* Hide on lost focus checkbox in preferences (have doubts it'd be convenient, may be worth testing)
* Tiles desktop view
	* A separate tab with draggable c4d tiles that work with search, but doesn't have any grouping options
* Shortcuts window in 'Help' section

* tags with scripts

### Bugs:
	* Normalize slashes in paths


* Done ~~Means to sort tags (e.g. via context menu)~~

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