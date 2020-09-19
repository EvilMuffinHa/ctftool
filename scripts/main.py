import argparse
import sys
import os
import json


def localpath():
	return "/".join(os.path.realpath(__file__).split("/")[:-2]) + "/"




if __name__ == "__main__":
	argvs = sys.argv

	if len(argvs) < 2:
		print("ctftool --help")
		sys.exit(1)

	# noinspection SpellCheckingInspection
	if argvs[1] == "-h" or argvs[1] == "--help":
		print()
		print("Usage: ctftool [-h] COMMAND")
		print()
		print("A tool for managing ctf writeups and storage")
		print()
		print("Options:\n\t-h, --help\tDisplays the help menu")
		print()
		print("Commands:")
		print(" create\t\tCreates a directory for the ctf")
		print(" addchall\tCreates a CTF chall and adds a writeup boilerplate")
		print(" settings\tChange local CTF settings")
		print(" finish\t\tMarks a chall as FINISHED")
		print(" list\t\tLists all chall info")
		print(" rm\t\tRemove a CTF chall")
		print(" setchall\tSets chall settings (add --help or -h on a setting for more information)")
		print(" groups\t\tLists all groups")
		print(" statuses\tLists all statuses")

	elif argvs[1] == "create":
		with open(localpath() + "config.json", "r") as f:
			js = json.load(f)
		parser = argparse.ArgumentParser(description="Creates a directory for the ctf")
		parser.add_argument("name", type=str, help="The name of the ctf")
		parser.add_argument("--setgroup", type=str, nargs="+", help="Manually sets the groups for this ctf", default=js["groups"])
		parser.add_argument("--setstatuses", type=str, nargs="+", help="Manually sets the statuses for this ctf", default=js["status"])
		args = parser.parse_args(argvs[2:])
		os.system('mkdir "' + args.name + '"')
		with open(localpath() + "pyignore.txt", "r") as f:
			text = f.read()
		print("Initializing ctf and git...")
		js_string = json.dumps({"groups":args.setgroup, "status":args.setstatuses})
		actions = 'cd "' + args.name + '" && git init && mkdir .ctfinit && touch README.' \
				'md && echo "# ' + args.name + '" > README.md && touch .ctfinit' \
				'/name && echo "' + args.name + '" > .ctfinit/name ' \
				'&& touch .gitignore && echo "' + text + '" > .gitignore ' \
				'&& touch .ctfinit/config.json && echo \'' + js_string + '\' > .ctfinit/config.json '
		print("Initialized empty CTF repository in " + os.getcwd() + "/" + args.name + "/.ctfinit/")
		os.system(actions)
		os.chdir(args.name)
	elif argvs[1] == "addchall":
		cwd = os.getcwd()
		ctfinit = False
		while cwd != "" and not ctfinit:
			cfiles = [d for d in os.listdir('.')]
			if not ".ctfinit" in cfiles:
				if cwd == "/":
					cwd = ""
				else:
					os.chdir("..")
					cwd = os.getcwd()

			else:
				ctfinit = True
		if cwd == "":
			print("fatal: not a ctf repository (or any of the parent directories): .ctfinit")
			sys.exit(1)

		with open(".ctfinit/config.json", "r") as f:
			js = json.load(f)
		parser = argparse.ArgumentParser(description="Creates a CTF chall and adds a writeup boilerplate")
		parser.add_argument("name", type=str, help="Name of the chall")
		parser.add_argument("-p", "--points", type=int, default=0, help="Sets the points earned for the chall")
		parser.add_argument("-g", "--group", type=str, default=js["groups"][0], help="Sets the chall type",
							choices=js["groups"])
		parser.add_argument("-s", "--status", type=str, default=js["status"][0], help="Sets the status",
							choices=js["status"])
		parser.add_argument("-n", "--nosol", action="store_true")
		args = parser.parse_args(argvs[2:])

		if args.name in [d for d in os.listdir(".") if os.path.isdir(d)]:
			print("fatal: chall folder already exists")
			sys.exit(1)
		if "\n" in list(args.name) or "|" in list(args.name):
			print("fatal: chall name cannot include pipes or newlines")
			sys.exit(1)
		os.system('mkdir "' + args.name + '"')
		text = "name: " + args.name + "\npoints: " + str(args.points) + "\ngroup: " + args.group + "\nstatus: " + args.status
		challtext = "name: " + args.name + "\ngroup: " + args.group
		if args.nosol:
			os.system('cd "' + args.name + '" && touch README.md && echo "# ' + args.name + '\n###### [Back](../README.md)'
						'" > README.md && touch .chall && echo "' + challtext + '" > .chall')
		else:
			os.system('cd "' + args.name + '" && touch README.md && echo "# ' + args.name + '\n###### [Back](../README.md)'
					'\n###### [Solution](solution.sh) " > README.md && touch solution.sh && chmod +x solution.sh && touch .chall && echo "' + challtext + '" > .chall')
		os.chdir(".ctfinit")
		cfiles = [d for d in os.listdir('.')]
		if not args.group in cfiles:
			os.mkdir(args.group)
		os.system('touch "' + args.group + "/" + args.name + '" && echo "' + text + '" > "' + args.group + "/" + args.name + '"')
		os.chdir("..")


		with open('README.md', 'r') as f:
			md = f.read()

		if "## " + args.group in md.split("\n"):

			splitted = md.split("\n\n")
			returned_text = ""
			for index, val in enumerate(splitted):
				if val.startswith("## " + args.group):
					position = index
					header = "## " + args.group + "\nName | Points\n-----|--------"
					lines = splitted[position].split("-----|--------")[1].split("\n")
					nums = []
					for i in lines[1:]:
						try:
							nums.append(int(i.split("| ")[1]))
						except IndexError:
							pass
					for index1, val1 in enumerate(nums):
						if val1 >= args.points:
							lines.insert(index1+1, "[" + args.name + "](" + args.name.replace(" ", "%20") + "/README.md) | " + str(args.points))
							break
						if index1 == len(nums) - 1:
							lines.append("[" + args.name + "](" + args.name.replace(" ", "%20") + "/README.md) | " + str(args.points))
							break
					returned_text += header + "\n".join(lines) + "\n\n"
				else:
					returned_text += val + "\n\n"
			with open("README.md", 'w') as rfile:
				rfile.write(returned_text[0:-2])
		else:
			returned_text = md + "\n## " + args.group + "\nName | Points\n-----|--------\n" + "[" + args.name + "](" + args.name.replace(" ", "%20") + "/README.md) | " + str(args.points) + "\n"
			with open("README.md", 'w') as rfile:
				rfile.write(returned_text)
		os.system("git add --all")
		os.system('git commit -am "Challenge ' + args.name + ' created"')
		print("Challenge " + args.name + " added with settings - \nPoints: " + str(args.points) + "\nGroup: " + args.group + "\nStatus: " + args.status)
	elif argvs[1] == "settings":
		cwd = os.getcwd()
		ctfinit = False
		while cwd != "" and not ctfinit:
			cfiles = [d for d in os.listdir('.')]
			if not ".ctfinit" in cfiles:
				if cwd == "/":
					cwd = ""
				else:
					os.chdir("..")
					cwd = os.getcwd()

			else:
				ctfinit = True
		if cwd == "":
			print("fatal: not a ctf repository (or any of the parent directories): .ctfinit")
			sys.exit(1)
		parser = argparse.ArgumentParser(description="Change local CTF settings")
		parser.add_argument("setting", type=str, help="Setting choice", choices=["addgroup", "rmgroup", "addstatus", "rmstatus"])
		parser.add_argument("value", type=str, help="Setting the value")
		args = parser.parse_args(argvs[2:])
		if args.setting == "addgroup":
			with open(".ctfinit/config.json", "r") as f:
				js = json.load(f)
			if args.value in js["groups"]:
				print("fatal: group already exists")
				sys.exit(1)
			js["groups"].append(args.value)
			if args.value == "name" or args.value == "config.json":
				print("fatal: cannot name the group " + args.value)
				sys.exit(1)
			with open(".ctfinit/config.json", "w") as f:
				json.dump(js, f)
			os.system("git add --all")
			os.system('git commit -am "Group ' + args.value + ' added"')
			print("Group " + args.value + " added!")
		if args.setting == "addstatus":
			with open(".ctfinit/config.json", "r") as f:
				js = json.load(f)
			if args.value in js["status"]:
				print("fatal: status already exists")
				sys.exit(1)
			js["status"].append(args.value)
			with open(".ctfinit/config.json", "w") as f:
				json.dump(js, f)
			os.system("git add --all")
			os.system('git commit -am "Status ' + args.value + ' added"')
			print("Status " + args.value + " added!")
		if args.setting == "rmstatus":
			with open(".ctfinit/config.json", "r") as f:
				js = json.load(f)
			if len(js["status"]) == 1:
				print("fatal: cannot remove status if only 1 status exists")
				sys.exit(1)
			if args.value not in js["status"]:
				print("fatal: status not found")
				sys.exit(1)
			if args.value == "FINISHED":
				print("fatal: you cannot remove the finished status")
				sys.exit(1)
			del js["status"][js["status"].index(args.value)]
			for i in [d for d in os.listdir(".ctfinit") if os.path.isdir(d)]:
				for j in os.listdir(".ctfinit/" + i):
					with open(".ctfinit/" + i + "/" + j, "r") as f:
						text = f.read()
					splitted = text.split("\n")
					if splitted[3][8:] == args.value:
						splitted[3] = "status: " + js["status"][0]
					with open(".ctfinit/" + i + "/" + j, "w") as f:
						f.write("\n".join(splitted))
			os.system("git add --all")
			os.system('git commit -am "Status ' + args.value + ' deleted"')
			print("Status " + args.value + " removed!")
		if args.setting == "rmgroup":
			with open(".ctfinit/config.json", "r") as f:
				js = json.load(f)
			if len(js["groups"]) == 1:
				print("fatal: cannot remove group if only 1 group exists")
				sys.exit(1)
			if args.value not in js["groups"]:
				print("fatal: group not found")
				sys.exit(1)
			del js["groups"][js["groups"].index(args.value)]
			with open(".ctfinit/config.json", "w") as f:
				json.dump(js, f)
			if js["groups"][0] not in os.listdir('.ctfinit'):
				os.system('mkdir ".ctfinit/' + js["groups"][0] + '"')
			try:
				for i in os.listdir(".ctfinit/" + args.value):

					with open('README.md', 'r') as f:
						md = f.read()

					if "## " + js["groups"][0] in md.split("\n"):

						splitted = md.split("\n\n")
						returned_text = ""
						for index, val in enumerate(splitted):
							if val.startswith("## " + js["groups"][0]):
								position = index
								header = "## " + js["groups"][0] + "\nName | Points\n-----|--------"
								lines = splitted[position].split("-----|--------")[1].split("\n")
								nums = []
								for i in lines[1:]:
									try:
										nums.append(int(i.split("| ")[1]))
									except IndexError:
										pass
								for index1, val1 in enumerate(nums):
									if val1 >= js["groups"][0]:
										with open(".ctfinit/" + args.value + '/' + i, 'r') as f:
											points = int(f.read().split("\n")[1][8:])
										lines.insert(index1 + 1,
													 "[" + i + "](" + i + "/README.md) | " + str(points))
										break
									if index1 == len(nums) - 1:
										lines.append("[" + args.name + "](" + args.name + "/README.md) | " + str(points))
										break
								returned_text += header + "\n".join(lines) + "\n\n"
							elif val.startswith("## " + args.value):
								pass
							else:
								returned_text += val + "\n\n"
						with open("README.md", 'w') as rfile:
							rfile.write(returned_text[0:-2])
					else:
						with open(".ctfinit/" + args.value + '/' + i, 'r') as f:
							points = int(f.read().split("\n")[1][8:])
						returned_text = md + "\n## " + js["groups"][0] + "\nName | Points\n-----|--------\n" + "[" + i + "](" + i.replace(" ", "%20") + "/README.md) | " + str(
							points) + "\n"

						returned_text = "\n\n".join([i for i in returned_text.split("\n\n") if not i.startswith("## " + args.value)])

						with open("README.md", 'w') as rfile:
							rfile.write(returned_text)
			except FileNotFoundError:
				pass


			try:
				for i in os.listdir('.ctfinit/' + args.value):
					os.system('mv ".ctfinit/' + args.value + '/' + i + '" ".ctfinit/' + js["groups"][0] + '/' + i + '"')
				os.system("rm -rf .ctfinit/" + args.value)
			except:
				os.system("rm -rf .ctfinit/" + args.value)
			for i in os.listdir(".ctfinit/" + js["groups"][0]):
				with open(".ctfinit/" + js["groups"][0] + "/" + i, "r") as f:
					nsplit = f.read().split("\n")
				nsplit[2] = "group: " + js["groups"][0]
				with open(".ctfinit/" + js["groups"][0] + "/" + i, "w") as f:
					f.write("\n".join(nsplit))
				with open(i + "/.chall", "r") as f:
					challsplit = f.read().split("\n")
				challsplit[1] = "group: " + js["groups"][0]
				with open(i + "/.chall", "w") as f:
					f.write("\n".join(challsplit))

			os.system("git add --all")
			os.system('git commit -am "Group ' + args.value + ' removed"')
			print("Removed group " + args.value + " and transferred challs in group to " + js["groups"][0])
	elif argvs[1] == "finish":
		cwd = os.getcwd()
		ctfinit = False
		while cwd != "" and not ctfinit:
			cfiles = [d for d in os.listdir('.')]
			if not ".chall" in cfiles:
				if cwd == "/":
					cwd = ""
				else:
					os.chdir("..")
					cwd = os.getcwd()

			else:
				ctfinit = True
		if cwd == "":
			print("fatal: not a chall folder (or any of the parent directories): .chall")
			sys.exit(1)
		parser = argparse.ArgumentParser(description="Marks a chall as FINISHED")
		parser.add_argument("-f", "--flag", type=str, help="Adds the flag to the information", default="")
		args = parser.parse_args(argvs[2:])
		with open(".chall", "r") as f:
			text = f.read()
		name = text.split("\n")[0][6:]
		group = text.split("\n")[1][7:]
		os.chdir("../.ctfinit/" + group)
		with open(name, "r") as f:
			stored = f.read()
		newstat = "status: FINISHED"
		splitted = stored.split("\n")
		if args.flag != "":
			splitted[4] = args.flag
		splitted[3] = newstat
		returned = "\n".join(splitted)
		with open(name, "w") as f:
			f.write(returned)
		os.system("git add --all")
		os.system('git commit -am "Finished chall ' + name + '"')
		print("Finished chall " + name + "!")
	elif argvs[1] == "list":
		cwd = os.getcwd()
		ctfinit = False
		while cwd != "" and not ctfinit:
			cfiles = [d for d in os.listdir('.')]
			if not ".ctfinit" in cfiles:
				if cwd == "/":
					cwd = ""
				else:
					os.chdir("..")
					cwd = os.getcwd()

			else:
				ctfinit = True
		if cwd == "":
			print("fatal: not a ctf repository (or any of the parent directories): .ctfinit")
			sys.exit(1)
		if len(argvs) == 3 and argvs[2] in ["-h", "--help"]:
			print()
			print("Usage: list")
			print()
			print("Lists all chall info")
			sys.exit(1)
		elif len(argvs) == 3 and argvs[2] not in ["-h", "--help"]:
			print("fatal: list requires no arguments")
			sys.exit(1)
		if len(argvs) > 3:
			print("fatal: list requires no arguments")
			sys.exit(1)
		for i in os.listdir(".ctfinit"):
			if i != "name" and i != "config.json":
				print(i.upper())
				for j in os.listdir('.ctfinit/' + i):
					with open(".ctfinit/" + i + "/" + j, "r") as f:
						info = f.read()
					name = info.split("\n")[0][6:]
					points = info.split("\n")[1][8:]
					group = info.split("\n")[2][7:]
					status = info.split("\n")[3][8:]
					try:
						if info.split("\n")[4] != "":
							flag = "  ( " + info.split("\n")[4] + " )"
						else:
							flag = ""
					except:
						flag = ""
					line = "\t" + name + " - " + points + ": " + status + flag
					print(line)
	elif argvs[1] == "rm":
		cwd = os.getcwd()
		ctfinit = False
		while cwd != "" and not ctfinit:
			cfiles = [d for d in os.listdir('.')]
			if not ".ctfinit" in cfiles:
				if cwd == "/":
					cwd = ""
				else:
					os.chdir("..")
					cwd = os.getcwd()

			else:
				ctfinit = True
		if cwd == "":
			print("fatal: not a ctf repository (or any of the parent directories): .ctfinit")
			sys.exit(1)
		parser = argparse.ArgumentParser(description="Remove a CTF chall")
		parser.add_argument("name", type=str, help="Name of the challenge")
		parser.add_argument("-f", "--force",  help="Ignore y/n question", action="store_true")
		args = parser.parse_args(argvs[2:])
		if not args.name in os.listdir("."):
			print("fatal: chall folder not found")
			sys.exit(1)
		with open(args.name + "/.chall", "r") as f:
			text = f.read()
		group = text.split("\n")[1][7:]
		if not args.force:
			yesno = input("Are you sure you want to delete " + args.name + "? [Y/n] ")
			if not yesno == "Y":
				sys.exit(0)
		os.system('rm -r "' + args.name + '"')
		os.remove(".ctfinit/" + group + "/" + args.name)
		with open("README.md", "r") as f:
			md = f.read()
		tb = md.split("## " + group + "\nName | Points\n-----|--------")
		tb1 = tb[1].split("\n##")
		tb2 = tb1[0].split("\n")
		for index, val in enumerate(tb2):
			if val.startswith("[" + args.name):
				correctind = index
		del tb2[correctind]
		if len(tb2) > 2:
			tb1[0] = "\n".join(tb2)
			tb[1] = "\n##".join(tb1)
			returned = ("## " + group + "\nName | Points\n-----|--------").join(tb)
		else:
			tb1[0] = "".join(tb2)
			tb[1] = "\n##".join(tb1).lstrip()
			returned = "".join(tb)
			if returned.endswith("\n\n"):
				returned = returned[:-1]
		with open("README.md", "w") as f:
			f.write(returned)
		os.system("git add --all")
		os.system('git commit -am "Chall ' + args.name + ' deleted"')
		print("Removed " + args.name + "!")
	elif argvs[1] == "setchall":
		cwd = os.getcwd()
		ctfinit = False
		while cwd != "" and not ctfinit:
			cfiles = [d for d in os.listdir('.')]
			if not ".chall" in cfiles:
				if cwd == "/":
					cwd = ""
				else:
					os.chdir("..")
					cwd = os.getcwd()

			else:
				ctfinit = True
		if cwd == "":
			print("fatal: not a chall folder (or any of the parent directories): .chall")
			sys.exit(1)
		parser = argparse.ArgumentParser(description="Sets chall settings (add --help or -h on a setting for more information)")
		parser.add_argument("setting", type=str, help="Setting of the chall", choices=["name", "group", "points", "status", "solution", "flag"])
		parser.add_argument("value", type=str, help="New value of setting")
		args = parser.parse_args(argvs[2:])
		if args.setting == "status":
			if args.value in ["-h", "--help"]:
				print("Allowed values: existing statuses")
				sys.exit(1)
			with open(".chall", "r") as f:
				basic_info = f.read()
			name = basic_info.split("\n")[0][6:]
			group = basic_info.split("\n")[1][7:]
			os.chdir("..")
			with open(".ctfinit/" + group + "/" + name, "r") as f:
				allinfo = f.read()
			with open(".ctfinit/config.json", "r") as f:
				js = json.load(f)
			splitted = allinfo.split("\n")
			if args.value not in js["status"]:
				print("fatal: status does not exist")
				sys.exit(1)
			splitted[3] = "status: " + args.value
			with open(".ctfinit/" + group + "/" + name, "w") as f:
				f.write("\n".join(splitted))
			os.system("git add --all")
			os.system('git commit -am "Status of chall ' + name + ' changed to ' + args.value + '"')
			print("Status changed to " + args.value + "!")
		if args.setting == "name":
			if args.value in ["-h", "--help"]:
				print("Allowed values: allowed foldernames")
				sys.exit(1)
			with open(".chall", "r") as f:
				t = f.read()
				group = t.split("\n")[1][7:]
				name = t.split("\n")[0][6:]
			os.chdir("..")
			with open(".ctfinit/" + group + "/" + name, "r") as f:
				t1 = f.read()
				points = t1.split("\n")[1][8:]
				status = t1.split("\n")[3][8:]
			os.remove(".ctfinit/" + group + "/" + name)
			with open("README.md", "r") as f:
				md = f.read()
			tb = md.split("## " + group + "\nName | Points\n-----|--------")
			tb1 = tb[1].split("\n##")
			tb2 = tb1[0].split("\n")
			for index, val in enumerate(tb2):
				if val.startswith("[" + name):
					correctind = index
			del tb2[correctind]
			if len(tb2) > 2:
				tb1[0] = "\n".join(tb2)
				tb[1] = "\n##".join(tb1)
				returned = ("## " + group + "\nName | Points\n-----|--------").join(tb)
			else:
				tb1[0] = "".join(tb2)
				tb[1] = "\n##".join(tb1).lstrip()
				returned = "".join(tb)
				if returned.endswith("\n\n"):
					returned = returned[:-1]
			with open("README.md", "w") as f:
				f.write(returned)
			with open(name + "/.chall", "w") as f:
				f.write("name: " + args.value + "\ngroup: " + group)

			with open('README.md', 'r') as f:
				md = f.read()

			if "## " + group in md.split("\n"):

				splitted = md.split("\n\n")
				returned_text = ""
				for index, val in enumerate(splitted):
					if val.startswith("## " + group):
						position = index
						header = "## " + group + "\nName | Points\n-----|--------"
						lines = splitted[position].split("-----|--------")[1].split("\n")
						nums = []
						for i in lines[1:]:
							try:
								nums.append(int(i.split("| ")[1]))
							except IndexError:
								pass
						for index1, val1 in enumerate(nums):
							if val1 >= args.points:
								lines.insert(index1 + 1, "[" + args.value + "](" + args.value.replace(" ",
																									"%20") + "/README.md) | " + str(
									points))
								break
							if index1 == len(nums) - 1:
								lines.append(
									"[" + args.value + "](" + args.value.replace(" ", "%20") + "/README.md) | " + str(
										points))
								break
						returned_text += header + "\n".join(lines) + "\n\n"
					else:
						returned_text += val + "\n\n"
				with open("README.md", 'w') as rfile:
					rfile.write(returned_text[0:-2])
			else:
				returned_text = md + "\n## " + group + "\nName | Points\n-----|--------\n" + "[" + args.value + "](" + args.value.replace(
					" ", "%20") + "/README.md) | " + str(points) + "\n"
				with open("README.md", 'w') as rfile:
					rfile.write(returned_text)
			try:
				os.mkdir(".ctfinit/" + group)
			except:
				pass
			with open(name + "/README.md", "r") as f:
				challmd = f.read()
			cmsplitted = challmd.split("\n")
			cmsplitted[0] = "# " + args.value
			with open(name + "/README.md", "w") as f:
				f.write("\n".join(cmsplitted))
			os.system('mv "' + name + '/" "' + args.value + '/"')
			text = "name: " + args.value + "\npoints: " + points + "\ngroup: " + group + "\nstatus: " + status
			os.system('touch ".ctfinit/' + group + "/" + args.value + '" && echo "' + text + '" > ".ctfinit/' + group + "/" + args.value + '"')
			os.system("git add --all")
			os.system('git commit -am "Name of chall ' + name + ' changed to ' + args.value + '"')
			print("Name changed to " + args.value + "! Please change directory to update the name of the folder. ")
		if args.setting == "solution":
			if args.value in ["-h", "--help"]:
				print("Allowed values: ( 1, 0, True, False )")
				sys.exit(1)
			with open(".chall", "r") as f:
				t = f.read()
				group = t.split("\n")[1][7:]
				name = t.split("\n")[0][6:]
			if args.value not in ["True", "False", "1", "0"]:
				print("fatal: not a choice (True, False, 1, 0)")
				sys.exit(1)
			if args.value in ["True", "1"]:
				if "solution.sh" not in os.listdir("."):
					os.system("touch solution.sh && chmod +x solution.sh")
					with open("README.md", "r") as f:
						md = f.read()
					splitted = md.split("\n")
					splitted.insert(2, "###### [Solution](solution.sh)")
					with open("README.md", "w") as f:
						f.write("\n".join(splitted))
					os.system("git add --all")
					os.system('git commit -am "Solution added to ' + name + '!"')
					print("Solution added to " + name)
				else:
					print("fatal: solution already exists for this chall")
					sys.exit(1)
			else:
				if "solution.sh" in os.listdir("."):
					os.remove("solution.sh")
					with open("README.md", "r") as f:
						md = f.read()
					splitted = md.split("\n")
					del splitted[2]
					with open("README.md", "w") as f:
						f.write("\n".join(splitted))

					os.system("git add --all")
					os.system('git commit -am "Solution removed from ' + name + '"')
					print("Solution removed from " + name)
				else:
					print("fatal: no solution exists")
					sys.exit(1)
		if args.setting == "group":
			if args.value in ["-h", "--help"]:
				print("Allowed values: existing groups")
				sys.exit(1)

			with open("../.ctfinit/config.json") as f:
				js = json.load(f)

			if args.value not in js["groups"]:
				print("fatal: group does not exist")
				sys.exit(1)

			with open(".chall", "r") as f:
				t = f.read()
				group = t.split("\n")[1][7:]
				name = t.split("\n")[0][6:]
			os.chdir("..")
			with open(".ctfinit/" + group + "/" + name, "r") as f:
				t1 = f.read()
				points = t1.split("\n")[1][8:]
				status = t1.split("\n")[3][8:]
			os.remove(".ctfinit/" + group + "/" + name)
			with open("README.md", "r") as f:
				md = f.read()
			tb = md.split("## " + group + "\nName | Points\n-----|--------")
			tb1 = tb[1].split("\n##")
			tb2 = tb1[0].split("\n")
			for index, val in enumerate(tb2):
				if val.startswith("[" + name):
					correctind = index
			del tb2[correctind]
			if len(tb2) > 2:
				tb1[0] = "\n".join(tb2)
				tb[1] = "\n##".join(tb1)
				returned = ("## " + group + "\nName | Points\n-----|--------").join(tb)
			else:
				tb1[0] = "".join(tb2)
				tb[1] = "\n##".join(tb1).lstrip()
				returned = "".join(tb)
				if returned.endswith("\n\n"):
					returned = returned[:-1]
			with open("README.md", "w") as f:
				f.write(returned)
			with open(name + "/.chall", "w") as f:
				f.write("name: " + name + "\ngroup: " + args.value)

			with open('README.md', 'r') as f:
				md = f.read()

			if "## " + args.value in md.split("\n"):

				splitted = md.split("\n\n")
				returned_text = ""
				for index, val in enumerate(splitted):
					if val.startswith("## " + args.value):
						position = index
						header = "## " + args.value + "\nName | Points\n-----|--------"
						lines = splitted[position].split("-----|--------")[1].split("\n")
						nums = []
						for i in lines[1:]:
							try:
								nums.append(int(i.split("| ")[1]))
							except IndexError:
								pass
						for index1, val1 in enumerate(nums):
							if val1 >= args.points:
								lines.insert(index1 + 1, "[" + name + "](" + name.replace(" ",
																									"%20") + "/README.md) | " + str(
									points))
								break
							if index1 == len(nums) - 1:
								lines.append(
									"[" + name + "](" + name.replace(" ", "%20") + "/README.md) | " + str(
										points))
								break
						returned_text += header + "\n".join(lines) + "\n\n"
					else:
						returned_text += val + "\n\n"
				with open("README.md", 'w') as rfile:
					rfile.write(returned_text[0:-2])
			else:
				returned_text = md + "\n## " + args.value + "\nName | Points\n-----|--------\n" + "[" + name + "](" + name.replace(
					" ", "%20") + "/README.md) | " + str(points) + "\n"
				with open("README.md", 'w') as rfile:
					rfile.write(returned_text)
			try:
				os.mkdir(".ctfinit/" + args.value)
			except:
				pass
			text = "name: " + name + "\npoints: " + points + "\ngroup: " + args.value + "\nstatus: " + status
			os.system('touch ".ctfinit/' + args.value + "/" + name + '" && echo "' + text + '" > ".ctfinit/' + args.value + "/" + name + '"')
			os.system("git add --all")
			os.system('git commit -am "Group of chall ' + name + ' changed to ' + args.value + '"')
			print("Group of chall " + name + " changed to " + args.value)
		if args.setting == "points":
			if args.value in ["-h", "--help"]:
				print("Allowed values: ( integers )")
				sys.exit(1)
			try:
				pointval = int(args.value)
			except TypeError:
				print("fatal: non-integer points are not valid")
				sys.exit(1)
			with open(".chall", "r") as f:
				t = f.read()
				group = t.split("\n")[1][7:]
				name = t.split("\n")[0][6:]
			os.chdir("..")
			with open(".ctfinit/" + group + "/" + name, "r") as f:
				t1 = f.read()
				points = t1.split("\n")[1][8:]
				status = t1.split("\n")[3][8:]
			os.remove(".ctfinit/" + group + "/" + name)
			with open("README.md", "r") as f:
				md = f.read()
			tb = md.split("## " + group + "\nName | Points\n-----|--------")
			tb1 = tb[1].split("\n##")
			tb2 = tb1[0].split("\n")
			for index, val in enumerate(tb2):
				if val.startswith("[" + name):
					correctind = index
			del tb2[correctind]
			if len(tb2) > 2:
				tb1[0] = "\n".join(tb2)
				tb[1] = "\n##".join(tb1)
				returned = ("## " + group + "\nName | Points\n-----|--------").join(tb)
			else:
				tb1[0] = "".join(tb2)
				tb[1] = "\n##".join(tb1).lstrip()
				returned = "".join(tb)
				if returned.endswith("\n\n"):
					returned = returned[:-1]
			with open("README.md", "w") as f:
				f.write(returned)
			with open(name + "/.chall", "w") as f:
				f.write("name: " + name + "\ngroup: " + group)

			with open('README.md', 'r') as f:
				md = f.read()

			if "## " + group in md.split("\n"):

				splitted = md.split("\n\n")
				returned_text = ""
				for index, val in enumerate(splitted):
					if val.startswith("## " + group):
						position = index
						header = "## " + group + "\nName | Points\n-----|--------"
						lines = splitted[position].split("-----|--------")[1].split("\n")
						nums = []
						for i in lines[1:]:
							try:
								nums.append(int(i.split("| ")[1]))
							except IndexError:
								pass
						for index1, val1 in enumerate(nums):
							if val1 >= pointval:
								lines.insert(index1 + 1, "[" + name + "](" + name.replace(" ",
																						  "%20") + "/README.md) | " + str(
									pointval))
								break
							if index1 == len(nums) - 1:
								lines.append(
									"[" + name + "](" + name.replace(" ", "%20") + "/README.md) | " + str(
										pointval))
								break
						returned_text += header + "\n".join(lines) + "\n\n"
					else:
						returned_text += val + "\n\n"
				with open("README.md", 'w') as rfile:
					rfile.write(returned_text[0:-2])
			else:
				returned_text = md + "\n## " + group + "\nName | Points\n-----|--------\n" + "[" + name + "](" + name.replace(
					" ", "%20") + "/README.md) | " + str(pointval) + "\n"
				with open("README.md", 'w') as rfile:
					rfile.write(returned_text)
			try:
				os.mkdir(".ctfinit/" + args.value)
			except:
				pass
			text = "name: " + name + "\npoints: " + str(pointval) + "\ngroup: " + group + "\nstatus: " + status
			os.system(
				'touch ".ctfinit/' + args.value + "/" + name + '" && echo "' + text + '" > ".ctfinit/' + group + "/" + name + '"')
			os.system("git add --all")
			os.system('git commit -am "Points of chall ' + name + ' changed to ' + args.value + '"')
			print("Points of chall " + name + " changed to " + args.value)
		if args.setting == "flag":
			if args.value in ["-h", "--help"]:
				print("Allowed values: ( <flagname>, 0, \"\", False )")
				sys.exit(1)
			with open(".chall", "r") as f:
				t = f.read()
				group = t.split("\n")[1][7:]
				name = t.split("\n")[0][6:]
			os.chdir("..")
			if args.value in ["", "0", "False"]:
				with open("../.ctfinit/" + group + "/" + name, "r") as f:
					text = f.read()
				if len(text.split("\n")) == 4:
					print("fatal: flag missing")
					sys.exit(0)
				else:
					r = text.split("\n")
					del r[4]
					with open("../.ctfinit/" + group + "/" + name, "w") as f:
						f.write("\n".join(r))

					os.system('git commit -am "Flag of chall ' + name + ' removed"')
					print("Flag of chall " + name + " removed.")
			else:
				with open("../.ctfinit/" + group + "/" + name, "r") as f:
					text = f.read()
				rr = text.split("\n")
				if len(rr) == 4:
					rr.append(args.value)
				else:
					rr[4] = args.value
				with open("../.ctfinit/" + group + "/" + name, "w") as f:
					f.write("\n".join(rr))
				os.system("git add --all")
				os.system('git commit -am "Flag of chall ' + name + ' changed to ' + args.value + '"')
				print("Flag of chall " + name + " changed to " + args.value)
	elif argvs[1] == "info":
		cwd = os.getcwd()
		ctfinit = False
		while cwd != "" and not ctfinit:
			cfiles = [d for d in os.listdir('.')]
			if not ".chall" in cfiles:
				if cwd == "/":
					cwd = ""
				else:
					os.chdir("..")
					cwd = os.getcwd()

			else:
				ctfinit = True
		if cwd == "":
			print("fatal: not a chall folder (or any of the parent directories): .chall")
			sys.exit(1)

		if len(argvs) == 3 and argvs[2] in ["-h", "--help"]:
			print()
			print("Usage: list")
			print()
			print("Shows specific chall info")
			sys.exit(1)
		elif len(argvs) == 3 and argvs[2] not in ["-h", "--help"]:
			print("fatal: info requires no arguments")
			sys.exit(1)
		if len(argvs) > 3:
			print("fatal: info requires no arguments")
			sys.exit(1)
		with open(".chall", "r") as f:
			t = f.read()
			name = t.split("\n")[0][6:]
			group = t.split("\n")[1][7:]
		with open("../.ctfinit/" + group + "/" + name, "r") as f:
			print(f.read())
	elif argvs[1] == "groups":
		cwd = os.getcwd()
		ctfinit = False
		while cwd != "" and not ctfinit:
			cfiles = [d for d in os.listdir('.')]
			if not ".ctfinit" in cfiles:
				if cwd == "/":
					cwd = ""
				else:
					os.chdir("..")
					cwd = os.getcwd()

			else:
				ctfinit = True
		if cwd == "":
			print("fatal: not a ctf repository (or any of the parent directories): .ctfinit")
			sys.exit(1)

		if len(argvs) == 3 and argvs[2] in ["-h", "--help"]:
			print()
			print("Usage: groups")
			print()
			print("Lists all groups")
			sys.exit(1)
		elif len(argvs) == 3 and argvs[2] not in ["-h", "--help"]:
			print("fatal: groups requires no arguments")
			sys.exit(1)
		if len(argvs) > 3:
			print("fatal: groups requires no arguments")
			sys.exit(1)
		with open(".ctfinit/config.json", "r") as f:
			js = json.load(f)
		for i in js["groups"].keys():
			print(f"{i}")
	elif argvs[1] == "statuses":
		cwd = os.getcwd()
		ctfinit = False
		while cwd != "" and not ctfinit:
			cfiles = [d for d in os.listdir('.')]
			if not ".ctfinit" in cfiles:
				if cwd == "/":
					cwd = ""
				else:
					os.chdir("..")
					cwd = os.getcwd()

			else:
				ctfinit = True
		if cwd == "":
			print("fatal: not a ctf repository (or any of the parent directories): .ctfinit")
			sys.exit(1)

		if len(argvs) == 3 and argvs[2] in ["-h", "--help"]:
			print()
			print("Usage: statuses")
			print()
			print("Lists all statuses")
			sys.exit(1)
		elif len(argvs) == 3 and argvs[2] not in ["-h", "--help"]:
			print("fatal: statuses requires no arguments")
			sys.exit(1)
		if len(argvs) > 3:
			print("fatal: statuses requires no arguments")
			sys.exit(1)
		with open(".ctfinit/config.json", "r") as f:
			js = json.load(f)
		for i in js["status"].keys():
			print(f"{i}")

	else:
		print("ctftool --help")
		sys.exit(1)




# add setchall to change settings of challs, add a help menu















