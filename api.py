import json
from flask import request
from flask_restx import Namespace, Resource
from app.api.decorators import api_key_required, role_required
from app.api.models import model_404, model_result
from app.database import row2dict, session_scope
from app.core.lib.sql import SqlSelect

_api_ns = Namespace(name="osysBoard", description="osysBoard namespace", validate=True)

response_result = _api_ns.model("Result", model_result)
response_404 = _api_ns.model("Error", model_404)


def create_api_ns():
    return _api_ns


@_api_ns.route("/query", endpoint="osysBoard_query")
class GetResultQuery(Resource):
    @api_key_required
    @role_required("admin")
    @_api_ns.doc(params={
        'query': 'SQL query',
    })

    @_api_ns.response(200, "List rows", response_result)
    def get(self):
        """
        Get result select query
        """
        query = request.args.get('query', None)
        if not query:
            return {"error": "query is required"}, 400
        
        result = SqlSelect(query)
        result = [dict(row) for row in result]
        return {"success": True, "result": result}, 200



