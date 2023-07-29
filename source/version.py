import os

C4DL_VERSION = '0.0.1'
BUILD_VERSION = ''

def _loadBuildInfo(rootPath: str):
	global BUILD_VERSION
	try:
		with open(os.path.join(rootPath, 'build.txt'), 'r') as f:
			buildDateStr: str = ''
			buildCommitStr: str = ''
			while line := f.readline():
				line = line.rstrip()
				if not len(line):
					continue
				if not len(buildDateStr):
					buildDateStr = line
					continue
				if not len(buildCommitStr):
					buildCommitStr = line
					break
			BUILD_VERSION = buildCommitStr
	except:
		pass