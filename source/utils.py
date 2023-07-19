import os

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

# Checks given folder path for containing Cinema 4D version
C4D_NECESSARY_FILES = ['Cinema 4D.exe']
C4D_NECESSARY_FOLDERS = ['corelibs', 'resource']
def GetCinemaVersionFromFolder(folderPath: str) -> str | None:
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
	return '.'.join([str(v) for v in c4dVersion.values()])

# Traverses directory until maxDepth, returns dict: path -> c4d_version
def FindCinemaPackagesInFolder(path, maxDepth = 3) -> dict[str, str]:
	c4dRootVersion: str | None = GetCinemaVersionFromFolder(path)
	if c4dRootVersion:
		return {path: c4dRootVersion}

	ret: dict[str, str] = dict()

	dirs: set[str] = set()
	dirs.update([f.path for f in os.scandir(path) if f.is_dir()])
	currentDepth: int = 0
	while len(dirs) and currentDepth < maxDepth:
		newDirs: list[str] = []
		for p in dirs:
			c4dVersion: str | None = GetCinemaVersionFromFolder(p)
			if c4dVersion:
				ret[p] = c4dVersion
				continue
			newDirs.append(p)
		dirs = newDirs
		currentDepth += 1
	return ret