import os

C4D_NECESSARY_FILES = ['Cinema 4D.exe']
C4D_NECESSARY_FOLDERS = ['corelibs', 'resource']

def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default
    
def GetCinemaVersionFromFolder(folderPath: str) -> bool | None:
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
	if not os.path.isfile(curPath):
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
					c4dVersion[i] = safe_cast(line[len(curDefinePart):].strip(), int, -1)
					versionPartCnt += 1
					break
	# validate cinema version
	for v in c4dVersion.values():
		if v == -1:
			return None
	return '.'.join(c4dVersion.values())