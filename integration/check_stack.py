import json
import subprocess
import time
import urllib.request
import urllib.error
from uuid import uuid4
from pathlib import Path

import os
import shutil

# Somente ambiente descartável definido em compose.ci.yml.
DOCKER = shutil.which("docker")
if not DOCKER:
    raise RuntimeError("Docker não encontrado no PATH")
PROJECT = os.environ.get("CI_COMPOSE_PROJECT", "jabuti-ci")
BASE = [DOCKER, "compose", "-p", PROJECT, "-f", "compose.ci.yml"]
API_KEY = "ci-only-api-key-not-for-production-123456789"
checks = []
email = "integration-" + uuid4().hex + "@example.com"


def compose(*args):
    result = subprocess.run(BASE + list(args), capture_output=True, text=True, timeout=90)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def request(method, path, data=None, auth=True):
    headers = {"Content-Type": "application/json"}
    if auth:
        headers["X-API-Key"] = API_KEY
    req = urllib.request.Request(
        "http://127.0.0.1:18015" + path,
        data=json.dumps(data).encode() if data is not None else None,
        headers=headers,
        method=method,
    )
    try:
        response = urllib.request.urlopen(req, timeout=15)
    except urllib.error.HTTPError as error:
        response = error
    body = response.read()
    return response.status, json.loads(body) if body else None


def check(name, condition):
    assert condition, name
    checks.append(name)
    print("PASS: " + name, flush=True)


for _ in range(40):
    try:
        status, health = request("GET", "/health")
        if status == 200:
            break
    except (OSError, ValueError):
        pass
    time.sleep(1)
else:
    raise AssertionError("API nao iniciou")
check("PostgreSQL e Redis disponiveis", health["database"] == "ok" and health["redis"] == "ok")
check(
    "Migracao PostgreSQL alinhada aos modelos",
    "No new upgrade operations" in compose("exec", "-T", "app", "alembic", "check"),
)
check("Processo sem privilegios root", compose("exec", "-T", "app", "id", "-u") == "10001")
check("CRUD exige autenticacao", request("GET", "/usuarios/", auth=False)[0] == 401)
status, user = request(
    "POST", "/usuarios/", {"nome": "Teste Integracao", "email": email, "idade": 30}
)
check("Criacao no PostgreSQL", status == 201)
uid = user["id"]
check(
    "Email duplicado retorna 409",
    request("POST", "/usuarios/", {"nome": "Teste", "email": email, "idade": 20})[0] == 409,
)
check("Valores invalidos retornam 422", request("PUT", "/usuarios/" + uid, {"idade": -1})[0] == 422)
check("Leitura por UUID", request("GET", "/usuarios/" + uid)[1] == user)
request("GET", "/usuarios/")
check(
    "Registro realmente armazenado no Redis",
    json.loads(compose("exec", "-T", "cache", "redis-cli", "get", "usuarios:id:" + uid))["id"]
    == uid,
)
check(
    "Lista realmente armazenada no Redis",
    compose("exec", "-T", "cache", "redis-cli", "exists", "usuarios:list:10:0:nome") == "1",
)
check(
    "TTL aplicado",
    0 < int(compose("exec", "-T", "cache", "redis-cli", "ttl", "usuarios:id:" + uid)) <= 5,
)
status, updated = request("PUT", "/usuarios/" + uid, {"nome": "Atualizado"})
check(
    "Atualizacao e invalidacao de listas",
    status == 200
    and compose("exec", "-T", "cache", "redis-cli", "exists", "usuarios:list:10:0:nome") == "0",
)
check(
    "Cache individual atualizado",
    json.loads(compose("exec", "-T", "cache", "redis-cli", "get", "usuarios:id:" + uid))["nome"]
    == "Atualizado",
)
compose("stop", "cache")
try:
    check(
        "CRUD funciona durante falha do Redis",
        request("GET", "/usuarios/" + uid)[1]["nome"] == "Atualizado",
    )
    check(
        "Escrita funciona durante falha do Redis",
        request("PUT", "/usuarios/" + uid, {"idade": 31})[0] == 200,
    )
    check(
        "Health continua 200 sem Redis",
        request("GET", "/health")[0] == 200 and request("GET", "/health")[1]["redis"] == "down",
    )
finally:
    compose("start", "cache")
    compose("restart", "app")
for _ in range(40):
    try:
        if request("GET", "/health")[1]["redis"] == "ok":
            break
    except (OSError, ValueError):
        pass
    time.sleep(1)
else:
    raise AssertionError("Redis nao reconectou")
time.sleep(6)
check(
    "Banco persiste apos reinicio e expiracao do cache",
    request("GET", "/usuarios/" + uid)[1]["idade"] == 31,
)
check("Exclusao retorna 204", request("DELETE", "/usuarios/" + uid)[0] == 204)
check(
    "Cache removido na exclusao",
    compose("exec", "-T", "cache", "redis-cli", "exists", "usuarios:id:" + uid) == "0",
)
check("Registro excluido retorna 404", request("GET", "/usuarios/" + uid)[0] == 404)
Path("integration-results.json").write_text(
    json.dumps({"passed": len(checks), "checks": checks}, indent=2), encoding="utf-8"
)
print(str(len(checks)) + " verificacoes de integracao aprovadas")
