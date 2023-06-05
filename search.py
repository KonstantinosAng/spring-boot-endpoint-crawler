import glob, os, sys, os, datetime, uuid, json
from optparse import OptionParser, Option, OptionValueError
from copy import copy

clearTerminal = lambda: os.system('cls' if os.name=='nt' else 'clear')

ABSOLUTE_PATH = os.path.dirname(os.path.realpath(__file__))
ALL_SYMBOL = "*"

POM_MODULE = "pom.xml"
MODULES_OPEN_TAG = "<modules>"
MODULES_CLOSE_TAG = "</modules>"
TARGET_BASE = "@RequestMapping"
TARGET_POST = "@PostMapping"
TARGET_GET = "@GetMapping"
TARGET_PUT = "@PutMapping"
TARGET_DELETE = "@DeleteMapping"
TARGET_PATCH = "@PatchMapping"
TARGET_PARAM = "@RequestParam"
TARGET_BODY = "@RequestBody"

THUNDER_CLIENT = "Thunder Client"

modules = {}
endpoints = []

printMap = {
  TARGET_BASE: "  [BASE]: ", TARGET_POST: "  -- [POST]: ", TARGET_GET: "  -- [GET]: ", 
	TARGET_PUT: "  -- [PUT]: ", TARGET_DELETE: "  -- [DELETE]: ", TARGET_PATCH: "  -- [PATCH]: ", 
	TARGET_PARAM: "  ---- [PARAM]: ", TARGET_BODY: "  ---- [BODY]: "
}

methodMap = {
	TARGET_POST: "POST", TARGET_GET: "GET", TARGET_PUT: "PUT", 
	TARGET_DELETE: "DELETE", TARGET_PATCH: "PATCH"
}

def check_bool(option, opt, value):
	try:
		return bool(value)
	except ValueError:
		raise OptionValueError("option %s: invalid bool value: %r" % (opt, value))

class Bool (Option):
	TYPES = Option.TYPES + ("bool",)
	TYPE_CHECKER = copy(Option.TYPE_CHECKER)
	TYPE_CHECKER["bool"] = check_bool

def find_target(line):
	if TARGET_POST in line: return TARGET_POST
	if TARGET_GET in line: return TARGET_GET 
	if TARGET_PUT in line: return TARGET_PUT
	if TARGET_DELETE in line: return TARGET_DELETE
	if TARGET_PATCH in line: return TARGET_PATCH
	if TARGET_PARAM in line: return TARGET_PARAM 
	if TARGET_BODY in line: return TARGET_BODY
	if TARGET_BASE in line: return TARGET_BASE
	return ""

def parse_module(line): return line.replace("<module>", "").replace("</module>", "").strip()

def parse_url(module, path): return "{{{{{}-api}}}}{}".format(module, path.replace('"', ''))

def parse_params(body_params): return json.dumps(body_params, separators=(',', ':'))

def export_json_to_file(module, export_json): 
	with open(f"{module}.json", "w") as outfile: outfile.write(json.dumps(export_json, indent=2))

def get_thunder_json_start(module):
	return {
		"client": THUNDER_CLIENT,
		"collectionName": module,
		"dateExported": str(datetime.datetime.today()),
		"version": "1.1",
		"requests": []
	}

def get_thunder_json_request(col_id, module, path, endpoint, body_params):
	return {
		"_id": str(uuid.uuid4()),
		"colId": col_id,
		"containerId": "",
		"name": parse_url(module, path),
		"url": parse_url(module, path),
		"method": methodMap[endpoint["method"]],
		"created": str(datetime.datetime.today()),
		"modified": str(datetime.datetime.today()),
		"headers": [],
		"params": "",
		"body": {
			"type": "json",
			"raw": parse_params(body_params),
			"form": []
		},
	}

def export_thunder_multi():
	""" Multi module project """
	for module in modules:
		
		export_json = get_thunder_json_start(module)
		
		col_id = str(uuid.uuid4())

		for endpoint in modules[module]:
			path = print_format(endpoint['method'], endpoint["line"], endpoint["base"], print_value=False)
			body_params = {x['value'].split(" ")[-1]: "" for x in endpoint['params'] if x['type'] == printMap[TARGET_BODY]}
			
			export_json['requests'].append(get_thunder_json_request(col_id, module, path, endpoint, body_params))

		export_json_to_file(module, export_json)

def export_thunder_single(files):
	""" Single module project """
	export_json = {}
	module = ""
	for file in files:
		if os.path.isfile(file) and file.endswith(POM_MODULE):
			try:
				module = file.replace(f"\{POM_MODULE}", "").split("\\")[-1]
				export_json = get_thunder_json_start(module)
			except Exception as e: pass

	col_id = str(uuid.uuid4())
	
	for endpoint in endpoints:
		path = print_format(endpoint['method'], endpoint["line"], endpoint["base"], print_value=False)
		body_params = {x['value'].split(" ")[-1]: "" for x in endpoint['params'] if x['type'] == printMap[TARGET_BODY]}
		export_json['requests'].append(get_thunder_json_request(col_id, module, path, endpoint, body_params))
		
	export_json_to_file(module, export_json)

def export_thunder(files):

	if len(modules) > 0: export_thunder_multi()
	
	else: export_thunder_single(files)

def filter_and_print_values(files):
	""" Multi module project """
	if len(modules) > 0:
		for module in modules:
			if text_input in module or text_input == ALL_SYMBOL:	print(f"\n [MODULE] {module} \n")
			for endpoint in modules[module]:
				if text_input in f"{printMap[endpoint['method']]} {format_line(endpoint['line'], endpoint['method'], endpoint['base'])} \n" or text_input == ALL_SYMBOL:
					print_format(endpoint['method'], endpoint["line"], endpoint["base"])
					for param in endpoint['params']:	print(param['type'], param['value'])
	else:
		""" Single module project """
		for file in files:
				if os.path.isfile(file) and file.endswith(POM_MODULE):
					try:
							module = file.replace(f"\{POM_MODULE}", "").split("\\")[-1]
							if text_input in f"\n [MODULE] {module} \n\n" or text_input == ALL_SYMBOL:	print(f"\n [MODULE] {module} \n")
					except Exception as e:
						pass

		for endpoint in endpoints:
				if text_input in f"{printMap[endpoint['method']]} {format_line(endpoint['line'], endpoint['method'], endpoint['base'])} \n" or text_input == ALL_SYMBOL:
					print_format(endpoint['method'], endpoint["line"], endpoint["base"])
					for param in endpoint['params']:	print(param['type'], param['value'])

def format_line(l, method, base):
	formatted_line = l.replace(method, "").replace("(", "").replace(")", "").replace("value", "").replace("=", "").strip()
	if base:
		if formatted_line[1] == '/' and base[-2] == "/": parsed_line = base[:-2] + formatted_line[1:]
		else: parsed_line = base[:-1] + formatted_line[1:]
	else: parsed_line = formatted_line
	return parsed_line

def print_format(target, line, base=None, print_value = True):
	if print_value: print(printMap[target], format_line(line, target, base))
	return format_line(line, target, base)

def find_modules(file_content):
	found_modules_open_tag = False
	for line in file_content.split("\n"):
		if MODULES_CLOSE_TAG in line:	found_modules_open_tag = False
		if found_modules_open_tag:	modules[parse_module(line)] = []
		if MODULES_OPEN_TAG in line:	found_modules_open_tag = True

def find_paths_in_controller(file, file_content):
	base = ""

	for i, line in enumerate(file_content.split("\n")):

		target = find_target(line)
		
		if target == "": continue
		
		if TARGET_BASE in line:
			base = print_format(TARGET_BASE, line, print_value=False)
			continue

		if TARGET_PARAM in line or TARGET_BODY in line:
			param = print_format_body_params(target, line, file_content, print_value=False)
			for i, x in enumerate(endpoints):
				if x['path'] == endpoint:
					temp_endpoint = x
					temp_endpoint['params'].append(param)
					endpoints[i] = temp_endpoint
			continue
			
		endpoint = print_format(target, line, base, print_value=False)
		endpoints.append({ 
			"path": endpoint, "line": line, "base": base, "filePath": file, 
			"fileName": file.split("\\")[-1], "method": target, 'params': [] 
		})

def create_final_modules():
	for endpoint in endpoints:
		for module in modules:
			if module in endpoint['filePath']:
				temp = modules[module]
				temp.append(endpoint)
				modules[module] = temp

def parse_multiple_body_params(request_body_raw, target):
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
	return format_pos[:-1].replace(target, "").strip()

def parse_body_param(request_body_raw, target):
	
	if request_body_raw.count(',') > 1:	return parse_multiple_body_params(request_body_raw, target)
	
	if request_body_raw.count("@") > 1:	return request_body_raw.split(",")[0].replace(target, "").strip()
		
	return " ".join(x.strip() for x in request_body_raw.split("\n")).replace(target, "").strip()

def print_format_body_params(target, line, file_content, print_value = True):
	start = file_content.find(line)
	step_in = file_content[start:].find(target)
	step = 0 
	
	while file_content[start+step_in+step] != ")" and start+step < len(file_content) - 1:
		if target == TARGET_PARAM and file_content[start+step_in+step] == "(": step += file_content[start+step_in+step:].find(")")
		step += 1
	
	request_body_raw = file_content[start+step_in:start+step_in+step].strip()
	request_body_formatted = parse_body_param(request_body_raw, target)
	
	if (print_value): print(printMap[target], request_body_formatted)

	return {'type': printMap[target], "value": request_body_formatted}

def parse_project(files):
	for file in files:
		if os.path.isfile(file):
			try:
				with open(file, 'r') as f:
					file_content = f.read()
					if file.endswith(POM_MODULE) and MODULES_OPEN_TAG in file_content:	find_modules(file_content)
					if TARGET_BASE in file_content:	find_paths_in_controller(file, file_content)
			except Exception:
				pass

	create_final_modules()
	
	return modules


if __name__ == '__main__':

	parser = OptionParser(option_class=Bool)
	parser.add_option('-f', '--path', action='store', default=ABSOLUTE_PATH, type='string', dest='path', help='String: path to repository')
	parser.add_option('-s', '--search', action='store', default=False, type='bool', dest='search', help='Boolean: pass to search in api endpoints')
	parser.add_option('-t', '--export-thunder', action='store', default=False, type='bool', dest='export_thunder', help='Boolean: pass to export endpoints in thunder client json format')
	parser.add_option('-p', '--export-postman', action='store', default=False, type='bool', dest='export_postman', help='Boolean: pass to export endpoints in thunder client json format')

	(options, args) = parser.parse_args()

	if not os.path.exists(options.path): sys.exit("Path does not exist")
	
	files = glob.glob(options.path + '/**/*[.java,.xml]', recursive=True)
	
	parse_project(files)

	if len(endpoints) <= 0: 
		print("No endpoint found :(")
		sys.exit(1)

	if (options.search): clearTerminal()

	if options.search:

		while True:

			text_input = input("\n Search something (* for all): ")
			
			clearTerminal()

			print("\n")
					
			filter_and_print_values(files)
		
	elif options.export_thunder:

		export_thunder(files)
			

	elif options.export_postman:

		print("coming soon")
	
	else:
		print("pass --help to see the available options")