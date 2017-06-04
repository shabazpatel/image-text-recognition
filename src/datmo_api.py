import os
import subprocess
import json
import re
from flask import Flask, request, jsonify
from inspect import getmembers, isfunction
import user_api_functions


app = Flask(__name__)
functions_list = [o for o in getmembers(user_api_functions) if isfunction(o[1])]

@app.route('/<func_name>', methods=['POST'])
def api_root(func_name):
    for function in functions_list:
        if function[0] == func_name:
            try:
                json_req_data = request.get_json()
                if json_req_data:
                    res = function[1](json_req_data)
            except Exception as e:
                return jsonify({"error": "Something is wrong"})
            return jsonify({"result": res})
    output_string = 'function: %s not found' % func_name
    return jsonify({"error": output_string})


@app.route('/scripts/<script_name>', methods=['POST'])
def script_root(script_name):
    current_path = os.path.dirname(os.path.abspath(__file__))
    scripts_path = os.path.join(current_path, 'scripts')
    for file in os.listdir(scripts_path):
        file_name = os.path.basename(os.path.normpath(file))
        if file_name.startswith('api_') and re.sub(r'api_', '', file_name, 1) == script_name:
            full_script_path = os.path.join(scripts_path, file)
            res = ""
            try:
                serialized_json = ''
                json_req_data = request.get_json()
                if json_req_data:
                    serialized_json = "'%s'" % json.dumps(json_req_data)
                output = subprocess.check_output([full_script_path, serialized_json])
                if output:
                    try:
                        res = json.loads(output)
                    except Exception as e:
                        print "Error while deserializing script: %s output, error: %s" % (file, str(e))
            except Exception as e:
                return jsonify({"error": "Something is wrong"})
            return jsonify({"result": res})
    output_string = 'script: %s not found' % script_name
    return jsonify({"error": output_string})

if __name__ == '__main__':
    app.run(host='0.0.0.0')

