import os, re

def GetPrefsFolderPath():
	path: str = os.path.join(GetAppDataPath(), 'c4d-version-manager')
	os.makedirs(path, exist_ok=True)
	return path

def GetAppDataPath():
	return os.getenv('APPDATA')

# Tries to cast given value to type, falls back to default if error
def SafeCast(val, to_type, default=None):
	try:
		return to_type(val)
	except (ValueError, TypeError):
		return default

# Gathers information about cinema
class C4DInfo:
	def __init__(self, dir: str, ver: list[str], dirPrefs: str | None = None) -> None:
		self.version: list[str] = ver
		self.directory: str = dir
		self.directoryPrefs: str = dirPrefs if dirPrefs else ''

	def GetPathExecutable(self) -> str:
		return os.path.join(self.directory, 'Cinema 4D.exe')

	def GetPathConfigCinema(self) -> str:
		return os.path.join(self.GetPathFolderResource(), 'config.cinema4d.txt')
	
	def GetPathFolderRoot(self) -> str:
		return self.directory
	
	def GetPathFolderResource(self) -> str:
		return os.path.join(self.directory, 'resource')
	
	def GetPathFolderPrefs(self) -> str:
		return self.directoryPrefs

	def GetPathFolderPlugins(self) -> str:
		return os.path.join(self.directoryPrefs, 'plugins')
	
	def GetVersionString(self, formatted: bool = True, full: bool = False) -> str:
		major: str = self.version[0]
		if len(major) == 4: # new convention
			return '.'.join(self.version if full else self.version[:-1])
		return self.GetVersionMajor(formatted) + '.' + ''.join(self.version[1:])

	def GetVersionMajor(self, formatted: bool = True) -> str:
		major: str = self.version[0]
		return ('R' if len(major) != 4 and formatted else '') + major

# Tries to find corresponding preferences folder in the APPDATA directory
def FindC4DPrefsFolder(folderPath: str) -> str | None:
	appDataMaxonPath: str = os.path.join(GetAppDataPath(), 'Maxon')
	if not os.path.isdir(appDataMaxonPath):
		return None
	
	c4dDirName: str = os.path.basename(folderPath)
	c4dDirNameLen: int = len(c4dDirName)
	suffixPattern: str = '^_[A-Z0-9]{8}'

	dirNames: list[str] = [f.name for f in os.scandir(appDataMaxonPath) if f.is_dir()]
	for dir in dirNames:
		if not dir.startswith(c4dDirName):
			continue
		suffix: str = dir[c4dDirNameLen:]
		if not re.match(suffixPattern, suffix):
			continue
		return os.path.join(appDataMaxonPath, dir)
	return None

# Checks given folder path for containing Cinema 4D version
C4D_NECESSARY_FILES = ['Cinema 4D.exe']
C4D_NECESSARY_FOLDERS = ['corelibs', 'resource']
def GetC4DInfoFromFolder(folderPath: str) -> C4DInfo | None:
	for file in C4D_NECESSARY_FILES:
		curPath: str = os.path.join(folderPath, file)
		if not os.path.isfile(curPath):
			return None
	for file in C4D_NECESSARY_FOLDERS:
		curPath: str = os.path.join(folderPath, file)
		if not os.path.isdir(curPath):
			return None

	# Get Cinema version
	versionPath: str = os.path.join(folderPath, 'resource', 'version.h')
	if not os.path.isfile(versionPath):
		return None

	C4V_VERSION_PART_PREFIX: str = '#define C4D_V'
	c4dVersion: dict = {1: -1, 2: -1, 3: -1, 4: -1}
	versionPartCnt: int = 0
	with open(versionPath) as fp:
		while versionPartCnt < 4:
			line: str = fp.readline().strip()
			if line is None:
				break
			for i in range(1, 5):
				curDefinePart: str = C4V_VERSION_PART_PREFIX + str(i)
				if line.startswith(curDefinePart):
					c4dVersion[i] = SafeCast(line[len(curDefinePart):].strip(), int, -1)
					versionPartCnt += 1
					break
	# validate cinema version
	for v in c4dVersion.values():
		if v == -1:
			return None

	versionStringsList: list[str] = [str(v) for v in c4dVersion.values()]
	prefsFolder: str | None = FindC4DPrefsFolder(folderPath)
	return C4DInfo(folderPath, versionStringsList, prefsFolder)

# Traverses directory until maxDepth, returns dict: path -> c4d_version
def FindCinemaPackagesInFolder(path, maxDepth = 3) -> dict[str, C4DInfo]:
	c4dRootInfo: C4DInfo | None = GetC4DInfoFromFolder(path)
	if c4dRootInfo:
		return {path: c4dRootInfo}

	ret: dict[str, C4DInfo] = dict()

	dirs: set[str] = set()
	dirs.update([f.path for f in os.scandir(path) if f.is_dir()])
	currentDepth: int = 0
	while len(dirs) and currentDepth < maxDepth:
		newDirs: list[str] = []
		for p in dirs:
			c4dInfo: C4DInfo | None = GetC4DInfoFromFolder(p)
			if c4dInfo:
				ret[p] = c4dInfo
				continue
			newDirs.append(p)
		dirs = newDirs
		currentDepth += 1
	return ret