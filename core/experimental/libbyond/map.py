import subprocess

dm_path = 'C:\\Program Files\\BYOND\\bin\\dm.exe'
dme_path = 'C:\\Documents and Settings\\CRASH\\Desktop\\Darkside\\Darkside.dme'

process = subprocess.Popen('%s -code_tree "%s"' % (dm_path, dme_path), stdout = subprocess.PIPE)
open('tree.txt', 'w').write(process.stdout.read())