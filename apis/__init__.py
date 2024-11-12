"""Initialize the api system for the backend"""

import re
import subprocess
from flask_restx import Api, Resource


api = Api(
    title="CWL Validator API",
    description="The backend api system for the CWL Validator",
    doc="/docs",
)


@api.route("/echo", endpoint="echo")
class HelloEverynyan(Resource):
    """Test if the server is active"""

    @api.response(200, "Success")
    @api.response(400, "Validation Error")
    def get(self):
        """Returns a simple 'Server Active' message"""

        return "Server active!"



@api.route("/validate", endpoint="validate")
class ValidateCWL(Resource):
    """Validate a CWL file"""
    @api.response(200, "Success")
    @api.response(400, "Validation Error")
    @api.expect(api.parser().add_argument("file_path", type=str, help="The file path or URL of the CWL file", required=True))
    def post(self):
        """Validate a CWL file"""

        file_path = api.payload.get('file_path')

        def clean_output(output):
            # Remove ANSI escape codes
            ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
            cleaned_output = ansi_escape.sub('', output).strip()
            # Remove INFO messages and unnecessary whitespace, and replace newlines with spaces
            cleaned_lines = []
            for line in cleaned_output.splitlines():
                if not line.startswith("INFO"):
                    cleaned_lines.append(line.strip())
            return " ".join(cleaned_lines)

        try:
            result = subprocess.run(
                ["cwltool", "--validate", file_path],
                capture_output=True,
                text=True,
                check=True,
            )
            stdout_clean = clean_output(result.stdout)
            stderr_clean = clean_output(result.stderr)
            return {"message": "Validation successful", "output": stdout_clean, "error": stderr_clean}, 200
        except subprocess.CalledProcessError as e:
            stdout_clean = clean_output(e.stdout)
            stderr_clean = clean_output(e.stderr)
            return {"message": "Validation failed", "output": stdout_clean, "error": stderr_clean}, 400
        except Exception as e:
            print("An unexpected error occurred.")
            print(str(e))
            return {"message": "An unexpected error occurred", "error": str(e)}, 500


@api.route("/validate-citation", endpoint="validate-citation")
class ValidateCitation(Resource):
    """Validate a CITATION.cff file"""
    @api.response(200, "Success")
    @api.response(400, "Validation Error")
    @api.expect(api.parser().add_argument("file_path", type=str, help="The URL or path of the CITATION file", required=True))
    def post(self):
        """Validate a CITATION.cff file"""
        file_path = api.payload.get('file_path')
        if file_path.startswith("http://") or file_path.startswith("https://"):
            cmd = ["cffconvert", "--validate", "-u", file_path]
        else:
            cmd = ["cffconvert", "--validate", file_path]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True,
            )

            stdout_clean = result.stdout
            stderr_clean = result.stderr
            return {"message": "valid", "output": stdout_clean, "error": stderr_clean}, 200
        except subprocess.CalledProcessError as e:
            stdout_clean = e.stdout
            stderr_clean = re.search(r'jsonschema.exceptions.ValidationError:.*', e.stderr).group(0) if e.stderr else "Unknown error"
            return {"message": "invalid", "output": stdout_clean, "error": stderr_clean}, 400
        except Exception as e:
            print(str(e))
            return {"message": "An unexpected error occurred", "error": str(e)}, 500
