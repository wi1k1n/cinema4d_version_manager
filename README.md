### Useful links:
* https://backstage.maxon.net/topic/3064/cinema-4d-icon-pack
* Save/restore UI layout: https://stackoverflow.com/questions/23279125/python-pyqt4-functions-to-save-and-restore-ui-widget-values

### TODOs:
* C4D instances interaction:
	* Show which c4d instances status on tiles: currently running, closed
	* Allow to activate, kill, restart c4d instances
* Group/Filter/Sort
	* Create layout
	* Add functionality to the layout
	* Adjust appearing behavior (executing action should toggle tag/filter window state, rather than always openning it)
* Tag window improvements
	* Space bar pressed while dragging applies tag but doesn't break dragging
	* default folded/unfolded group when grouping by tags
* Auto saving options
	* Store last selected group/filter/sort settings
	* Store last layout (tags & filter/sort window states)
	* Store device where the window is positioned
* Preferences
	* layouts and layout behavior
	* saving/loading preferences
	* functionality: app behavior reflects settings
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