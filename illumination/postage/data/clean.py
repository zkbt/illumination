# this tiny blob cleaned some non-breaking spaces from the files
import glob
for f in glob.glob('tpf-*.txt'):
	with open(f) as file:
		lines = file.readlines()
		lines = [l.replace('\xa0', ' ') for l in lines]
	with open(f, 'w') as file:
		file.writelines(lines)
