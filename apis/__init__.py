"""Initialize the api system for the backend"""

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
