"""Optional Swagger entry point entirely under the existing /api/ proxy."""
from copy import deepcopy

from flask import jsonify, render_template, request, url_for


def register_public_swagger(app, api):
    if not app.config.get("PUBLIC_SWAGGER_ENABLED", False):
        return

    def asset_url(filename):
        return url_for("public_swagger_asset", filename=filename)

    @app.get("/api/docs/", strict_slashes=False)
    def public_swagger_ui():
        html = render_template(
            "swagger-ui.html", title=api.title,
            specs_url=url_for("public_swagger_schema"), swagger_static=asset_url,
        )
        return html, 200, {"Cache-Control": "no-store"}

    @app.get("/api/docs/swagger.json")
    def public_swagger_schema():
        schema = deepcopy(api.__schema__)
        # nginx terminates HTTPS and passes the public host/protocol to Flask.
        # Override cached origin fields only for this response, not the shared schema.
        schema["host"] = request.host
        is_https = request.is_secure or request.headers.get("X-Forwarded-Proto") == "https"
        schema["schemes"] = ["https" if is_https else "http"]
        response = jsonify(schema)
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/api/docs/assets/<path:filename>")
    def public_swagger_asset(filename):
        return app.view_functions["restx_doc.static"](filename=filename)
