import logging
import re
import secrets
import ssl

import click
from flask import Flask, request
from psycopg import Error as DatabaseError
from werkzeug.exceptions import HTTPException
from werkzeug.security import generate_password_hash

from backend.database import close_db
from backend.routes import accounts, commands, devices, readings
from backend.security import ApiError, PASSWORD_HASH_METHOD, normalize_username
from backend.services.devices import provision_device
from backend.settings import ConfigurationError, Settings, load_settings


def create_app(settings: Settings | None = None) -> Flask:
    settings = settings if settings is not None else load_settings()
    app = Flask(__name__, static_folder=None)
    app.config.update(
        SETTINGS=settings,
        SECRET_KEY=settings.secret_key,
        MAX_CONTENT_LENGTH=16 * 1024,
        DUMMY_PASSWORD_HASH=generate_password_hash(secrets.token_urlsafe(32), method=PASSWORD_HASH_METHOD),
    )
    app.logger.setLevel(settings.log_level)
    app.teardown_appcontext(close_db)
    for blueprint in (accounts.blueprint, devices.blueprint, readings.blueprint, commands.blueprint):
        app.register_blueprint(blueprint)

    @app.before_request
    def require_https():
        if not request.is_secure:
            raise ApiError(400, "https_required", "Use HTTPS to access the API")

    @app.after_request
    def response_headers(response):
        response.headers["Cache-Control"] = "no-store"
        response.headers["X-Content-Type-Options"] = "nosniff"
        if request.is_secure:
            response.headers["Strict-Transport-Security"] = "max-age=31536000"
        if response.status_code == 401:
            response.headers["WWW-Authenticate"] = "Bearer"
        return response

    @app.errorhandler(ApiError)
    def api_error(error):
        response = app.json.response({"error": {"code": error.code, "message": error.message}})
        response.status_code = error.status
        if error.retry_after is not None:
            response.headers["Retry-After"] = str(error.retry_after)
        return response

    @app.errorhandler(HTTPException)
    def http_error(error):
        response = error.get_response()
        response.data = app.json.dumps({
            "error": {"code": error.name.lower().replace(" ", "_"), "message": error.description},
        })
        response.content_type = "application/json"
        return response

    @app.errorhandler(DatabaseError)
    def database_error(error):
        app.logger.error("Database operation failed: type=%s", type(error).__name__)
        return {"error": {"code": "database_unavailable", "message": "Storage is temporarily unavailable"}}, 503

    @app.errorhandler(Exception)
    def unexpected_error(error):
        app.logger.error("Request failed: type=%s", type(error).__name__)
        return {"error": {"code": "internal_error", "message": "The request could not be completed"}}, 500

    @app.cli.command("provision-device")
    @click.option("--username", required=True)
    @click.option("--device-id", required=True)
    @click.option("--name", required=True)
    def provision_device_command(username: str, device_id: str, name: str):
        """Assign a device with an existing credential to an account."""
        token = click.prompt("Device token", hide_input=True, confirmation_prompt=True)
        if not re.fullmatch(r"[A-Za-z0-9_-]{16,256}", token):
            raise click.ClickException("Token must contain 16 to 256 URL-safe characters")
        if not name.strip() or len(name) > 100:
            raise click.ClickException("Name must contain 1 to 100 characters")
        try:
            device = provision_device(normalize_username(username), device_id, name.strip(), token)
        except (ApiError, HTTPException) as error:
            raise click.ClickException(str(error)) from None
        except DatabaseError:
            raise click.ClickException("Storage is unavailable; check database configuration and schema") from None
        click.echo(f"Provisioned device {device['id']}")

    return app


def main() -> int:
    try:
        settings = load_settings()
        logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s %(message)s")
        if not settings.tls_cert_file.is_file() or not settings.tls_key_file.is_file():
            raise ConfigurationError("Configure existing BACKEND_TLS_CERT_FILE and BACKEND_TLS_KEY_FILE files")
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.load_cert_chain(settings.tls_cert_file, settings.tls_key_file)
        app = create_app(settings)
        app.run(host=settings.host, port=settings.port, ssl_context=context, debug=False, use_reloader=False)
    except (ConfigurationError, OSError, ValueError) as error:
        logging.getLogger(__name__).error("Backend startup failed: %s", error)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
