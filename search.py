import glob, os, sys, re, os

clear = lambda: os.system('cls' if os.name=='nt' else 'clear')

ABSOLUTE_PATH = os.path.dirname(os.path.realpath(__file__))
ALL_SYMBOL = "*"

pomModule = "pom.xml"
modules_open_tag = "<modules>"
modules_close_tag = "</modules>"
targetBase = "@RequestMapping"
targetPost = "@PostMapping"
targetGet = "@GetMapping"
targetPut = "@PutMapping"
targetDelete = "@DeleteMapping"
targetPatch = "@PatchMapping"
targetParam = "@RequestParam"
targetBody = "@RequestBody"

modules = {}
endpoints = []

printMap = {
  "@RequestMapping": "  [BASE]: ", "@PostMapping": "  -- [POST]: ", "@GetMapping": "  -- [GET]: ", "@PutMapping": "  -- [PUT]: ",
	"@DeleteMapping": "  -- [DELETE]: ", "@PatchMapping": "  -- [PATCH]: ", "@RequestParam": "  ---- [PARAM]: ", "@RequestBody": "  ---- [BODY]: "
}

def format_line(l, method, base):
	formatted_line = l.replace(method, "").replace("(", "").replace(")", "").replace("value", "").replace("=", "").strip()
	if base:
		if formatted_line[1] == '/' and base[-2] == "/": parsed_line = base[:-2] + formatted_line[1:]
		else: parsed_line = base[:-1] + formatted_line[1:]
	else:
		parsed_line = formatted_line
	return parsed_line

def print_format(target, line, base=None, print_value = True):
	if print_value: print(printMap[target], format_line(line, target, base))
	return format_line(line, target, base)

def print_format_body_params(target, line, file_content, print_value = True):
	start = file_content.find(line)
	step_in = file_content[start:].find(target)
	step = 0 
	while file_content[start+step_in+step] != ")" and start+step < len(file_content) - 1:
		if target == targetParam and file_content[start+step_in+step] == "(":
			step += file_content[start+step_in+step:].find(")")
		step += 1
	request_body_raw = file_content[start+step_in:start+step_in+step].strip()
	request_body_formatted = ""
	if request_body_raw.count(',') > 1:
		array = request_body_raw.split("\n")
		if array[0].count(",") == 1:
			format_pos = " ".join(x.strip() for x in array[:2]).strip()
		else:
			commas = 0
			format_pos = ""
			for x in array[0]:
				if commas == 2: break
				if x == ',': commas += 1
				format_pos += x
		request_body_formatted = format_pos[:-1].replace(target, "").strip()
	else:
		if request_body_raw.count("@") > 1:
			request_body_formatted = request_body_raw.split(",")[0].replace(target, "").strip()
		else:
			request_body_formatted = " ".join(x.strip() for x in request_body_raw.split("\n")).replace(target, "").strip()
	if (print_value):
		print(printMap[target], request_body_formatted)
	return {'type': printMap[target], "value": request_body_formatted}

def parse_module(line): return line.replace("<module>", "").replace("</module>", "").strip()

def find_modules(file_content):
	found_modules_open_tag = False
	for line in file_content.split("\n"):
		if modules_close_tag in line:	found_modules_open_tag = False
		if found_modules_open_tag:	modules[parse_module(line)] = []
		if modules_open_tag in line:	found_modules_open_tag = True

def parse_project(files):
	for file in files:
		if os.path.isfile(file):
			try:
				
				with open(file, 'r') as f:
					file_content = f.read()
					if file.endswith(pomModule) and modules_open_tag in file_content:	find_modules(file_content)
					if targetBase in file_content:
						base = ""
						# print("\n  " + "*"*(len(file.split("\\")[-1])+12))
						# print("  |> File: {} <|".format(file.split("\\")[-1]))
						# print("  " + "*"*(len(file.split("\\")[-1])+12))
						for i, line in enumerate(file_content.split("\n")):
							if targetBase in line:
								base = print_format(targetBase, line, print_value=False)
								continue
							target = ""
							if targetPost in line: target = targetPost
							if targetGet in line: target = targetGet 
							if targetPut in line: target = targetPut
							if targetDelete in line: target = targetDelete
							if targetPatch in line: target = targetPatch
							if target != "":
								endpoint = print_format(target, line, base, print_value=False)
								endpoints.append({ "path": endpoint, "line": line, "base": base, "filePath": file, "method": target, 'params': [] })
								continue
							if targetParam in line or targetBody in line:
								_target = targetParam if targetParam in line else targetBody
								param = print_format_body_params(_target, line, file_content, print_value=False)
								for i, x in enumerate(endpoints):
									if x['path'] == endpoint:
										temp_endpoint = x
										temp_endpoint['params'].append(param)
										endpoints[i] = temp_endpoint
								continue
			except Exception as e:
				pass

	for endpoint in endpoints:
		for module in modules:
			print(module)
			if module in endpoint['filePath']:
				temp = modules[module]
				temp.append(endpoint)
				modules[module] = temp
	
	return modules


if __name__ == '__main__':
	path = ABSOLUTE_PATH
	if len(sys.argv) == 2: path = sys.argv[1]
	if not os.path.exists(path): sys.exit("Path does not exist")
	files = glob.glob(path + '/**/*[.java,.xml]', recursive=True)
	
	final_modules = parse_project(files)

	if len(endpoints) <= 0: 
		print("No endpoint found :(")
		sys.exit(1)

	clear()

	while True:

		text_input = input("\n Search something (* for all): ")
		
		clear()

		print("\n")
				
		""" Multi module project """
		if len(final_modules) > 0:
			for module in final_modules:
				if text_input in module or text_input == ALL_SYMBOL:
					print(f"\n [MODULE] {module} \n")
				for endpoint in final_modules[module]:
					if text_input in f"{printMap[endpoint['method']]} {format_line(endpoint['line'], endpoint['method'], endpoint['base'])} \n" or text_input == ALL_SYMBOL:
						print_format(endpoint['method'], endpoint["line"], endpoint["base"])
						for param in endpoint['params']:
							print(param['type'], param['value'])
		else:
			""" Single module project """

			for file in files:
					if os.path.isfile(file) and file.endswith(pomModule):
						try:
								module = file.replace(f"\{pomModule}", "").split("\\")[-1]
								if text_input in f"\n [MODULE] {module} \n\n" or text_input == ALL_SYMBOL:
									print(f"\n [MODULE] {module} \n")
						except Exception as e:
							pass

			for endpoint in endpoints:
					if text_input in f"{printMap[endpoint['method']]} {format_line(endpoint['line'], endpoint['method'], endpoint['base'])} \n" or text_input == ALL_SYMBOL:
						print_format(endpoint['method'], endpoint["line"], endpoint["base"])
						for param in endpoint['params']:
							print(param['type'], param['value'])