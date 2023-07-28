import os, sys, datetime as dt, git

BUILD_PATH = os.path.join(os.getcwd(), 'build')
BUILDINFO_FILENAME = 'build.txt'

def createBuildInfo(appName: str) -> None:
	gitStr: str = ''
	try:
		repo = git.Repo(search_parent_directories=True)
		gitStr = repo.head.object.hexsha
		if gitStr and len(gitStr) >= 12:
			gitStr = f'{gitStr[:12]} {dt.datetime.fromtimestamp(repo.head.object.committed_date).strftime("%d/%m/%Y %H:%M:%S")}'
	except:
		pass
	
	os.makedirs(BUILD_PATH, exist_ok=True)
	with open(os.path.join(BUILD_PATH, BUILDINFO_FILENAME), 'w') as f:
		f.write(f'{dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}{os.linesep}')
		if gitStr:
			f.write(f'{gitStr}{os.linesep}')

if __name__ == '__main__':
	if len(sys.argv) < 2:
		print('Usage: buildinfo.py APP_NAME')
		sys.exit(0)
	
	appName = sys.argv[1]
	BUILD_PATH = os.path.join(BUILD_PATH, appName)
	
	createBuildInfo(appName)