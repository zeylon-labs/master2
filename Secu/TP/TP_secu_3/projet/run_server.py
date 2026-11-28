import argparse
import json
from pathlib import Path
import secrets
import ssl

from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from tools.paths import ACCOUNT, DEFAULT_RESOURCES, SERVER_CERT, SERVER_KEY, secret


HTTP_DEMO_MESSAGE = "Silex-Lilas-28"


def create_account(directory, username, password, message):
    if not all((username.strip(), password, message.strip())):
        raise ValueError("L’identifiant, le mot de passe et le message sont obligatoires.")
    account = {
        "username": username,
        "password_hash": generate_password_hash(password, method="scrypt:32768:8:3"),
        "message": message,
    }
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / ACCOUNT).open("x", encoding="utf-8") as output:
        json.dump(account, output, ensure_ascii=False, indent=2)


def create_app(account=None):
    app = Flask(__name__)
    if account is None:
        @app.get("/")
        def http_demo():
            return render_template("club.html", message=HTTP_DEMO_MESSAGE)

        return app

    app.config.update(SECRET_KEY=secrets.token_bytes(32), SESSION_COOKIE_SECURE=True,
                      SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Strict")

    @app.after_request
    def prevent_caching(response):
        response.headers["Cache-Control"] = "no-store"
        return response

    @app.get("/")
    def club():
        if session.get("member") != account["username"]:
            return render_template("club.html"), 401
        return render_template("club.html", message=account["message"], member=True)

    @app.post("/connexion")
    def login():
        session.clear()
        valid = check_password_hash(account["password_hash"], request.form.get("password", ""))
        if not valid or request.form.get("username") != account["username"]:
            return render_template("club.html", error="Identifiant ou mot de passe incorrect."), 401
        session["member"] = account["username"]
        return redirect(url_for("club"), code=303)

    @app.post("/deconnexion")
    def logout():
        session.clear()
        return redirect(url_for("club"), code=303)

    return app


def server_context(directory, password):
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    context.load_cert_chain(directory / SERVER_CERT, directory / SERVER_KEY, password)
    return context


def main():
    parser = argparse.ArgumentParser(description="Serveur local du club privé")
    parser.add_argument("mode", nargs="?", choices=("http", "https", "creer-compte"), default="https")
    parser.add_argument("--resources", type=Path, default=DEFAULT_RESOURCES)
    parser.add_argument("--port", type=int)
    parser.add_argument("--identifiant", default="membre")
    args = parser.parse_args()
    try:
        if args.mode == "creer-compte":
            create_account(args.resources, args.identifiant,
                           secret("TP_COMPTE_MDP", "Mot de passe du compte : "),
                           secret("TP_MESSAGE", "Message mensuel du club : "))
            print("Compte créé pour", args.identifiant)
            return
        if args.mode == "http":
            app, context, port = create_app(), None, 8081
        else:
            account = json.loads((args.resources / ACCOUNT).read_text(encoding="utf-8"))
            context = server_context(args.resources, secret("TP_SERVEUR_MDP", "Mot de passe de la clé serveur : "))
            app, port = create_app(account), 8443
        app.run(host="127.0.0.1", port=args.port or port, ssl_context=context, debug=False)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"Erreur de démarrage : {exc}\n")


if __name__ == "__main__":
    main()
