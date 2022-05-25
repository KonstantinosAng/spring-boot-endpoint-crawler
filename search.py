import glob, os, sys
from time import time

ABSOLUTE_PATH = os.path.dirname(os.path.realpath(__file__))
targetBase = "@RequestMapping"
targetPost = "@PostMapping"
targetGet = "@GetMapping"
targetPut = "@PutMapping"
targetDelete = "@DeleteMapping"
targetPatch = "@PatchMapping"
targetParam = "@RequestParam"
targetBody = "@RequestBody"

printMap = {
  "@RequestMapping": "[BASE]: ", "@PostMapping": "-- [POST]: ", "@GetMapping": "-- [GET]: ", "@PutMapping": "-- [PUT]: ",
	"@DeleteMapping": "-- [DELETE]: ", "@PatchMapping": "-- [PATCH]: ", "@RequestParam": "---- [PARAM]: ", "@RequestBody": "---- [BODY]: "
}

def format_line(l, method, base):
	formatted_line = l.replace(method, "").replace("(", "").replace(")", "").replace("value", "").replace("=", "").strip()
	if base:
		if formatted_line[1] == '/' and base[-2] == "/": parsed_line = base[:-2] + formatted_line[1:]
		else: parsed_line = base[:-1] + formatted_line[1:]
	else:
		parsed_line = formatted_line
	return parsed_line

def print_format(target, line, base=None):
	print(printMap[target], format_line(line, target, base))
	return format_line(line, target, base)

def print_format_body_params(target, line, file_content):
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
		request_body_formatted = " ".join(x.strip() for x in request_body_raw.split("\n")).replace(target, "").strip()
	print(printMap[target], request_body_formatted)

if __name__ == '__main__':
	path = ABSOLUTE_PATH
	if len(sys.argv) == 2: path = sys.argv[1]
	if not os.path.exists(path): sys.exit("Path does not exist")
	files = glob.glob(path + '/**', recursive=True)
	start_time = time()
	for file in files:
		if os.path.isfile(file):
			try:
				with open(file, 'r') as f:
					file_content = f.read()
					if targetBase in file_content:
						base = ""
						print("\n" + "*"*(len(file.split("\\")[-1])+12))
						print("|> File: {} <|".format(file.split("\\")[-1]))
						print("*"*(len(file.split("\\")[-1])+12))
						for i, line in enumerate(file_content.split("\n")):
							if targetBase in line:
								base = print_format(targetBase, line)
								continue
							if targetPost in line: 
								print_format(targetPost, line, base)
								continue
							if targetGet in line: 
								print_format(targetGet, line, base)
								continue
							if targetPut in line:
								print_format(targetPut, line, base)
								continue
							if targetDelete in line:
								print_format(targetDelete, line, base)
								continue
							if targetPatch in line:
								print_format(targetPatch, line, base)
								continue
							if targetParam in line:
								print_format_body_params(targetParam, line, file_content)
								continue
							if targetBody in line:
								print_format_body_params(targetBody, line, file_content)
								continue
			except Exception as e:
				pass

	print("\n TOTAL_TIME: {} sec\n".format(time() - start_time))