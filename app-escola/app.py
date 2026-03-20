import logging
import os
import uuid
from datetime import datetime, timezone
from pathlib import Path

from flask import Flask, jsonify, request
import psycopg
from psycopg.rows import dict_row

app = Flask(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://escola_admin:troque-esta-senha@localhost:5432/escola_iam",
)
APP_LOG_PATH = Path(os.getenv("APP_LOG_PATH", "./access.log"))
SCHOOL_NAME = os.getenv("SCHOOL_NAME", "Escola Municipal PoC LGPD")

APP_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename=APP_LOG_PATH,
    level=logging.INFO,
    format="%(message)s",
)

ROUTE_METADATA = {
    "/alunos": {
        "action": "READ",
        "legal_basis": "LGPD Art. 7º, III e Art. 23",
        "dataset": "dados_cadastrais_alunos",
    },
    "/financeiro": {
        "action": "READ",
        "legal_basis": "LGPD Art. 23 e controle interno municipal",
        "dataset": "dados_financeiros_escolares",
    },
    "/matriculas": {
        "action": "READ",
        "legal_basis": "ECA + política de gestão escolar",
        "dataset": "status_matriculas",
    },
}


def get_connection():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def ensure_schema():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS audit_access_logs (
                    id BIGSERIAL PRIMARY KEY,
                    user_id VARCHAR(120) NOT NULL,
                    user_role VARCHAR(60) NOT NULL,
                    route VARCHAR(120) NOT NULL,
                    action VARCHAR(30) NOT NULL DEFAULT 'READ',
                    ip_address INET,
                    user_agent TEXT,
                    legal_basis VARCHAR(120) NOT NULL,
                    accessed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    correlation_id UUID NOT NULL,
                    notes TEXT
                )
                """
            )
        conn.commit()


def resolve_correlation_id() -> str:
    correlation_id = request.headers.get("X-Correlation-ID")
    try:
        return str(uuid.UUID(correlation_id)) if correlation_id else str(uuid.uuid4())
    except (ValueError, TypeError, AttributeError):
        return str(uuid.uuid4())


def persist_access_log(route: str):
    user_id = request.headers.get("X-Authentik-Username", "anonimo")
    user_role = request.headers.get("X-Authentik-Groups", "sem-perfil")
    correlation_id = resolve_correlation_id()
    user_agent = request.headers.get("User-Agent", "desconhecido")
    ip_address = request.headers.get("X-Forwarded-For", request.remote_addr)
    metadata = ROUTE_METADATA[route]
    accessed_at = datetime.now(timezone.utc)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO audit_access_logs (
                    user_id,
                    user_role,
                    route,
                    action,
                    ip_address,
                    user_agent,
                    legal_basis,
                    accessed_at,
                    correlation_id,
                    notes
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s::uuid, %s)
                """,
                (
                    user_id,
                    user_role,
                    route,
                    metadata["action"],
                    ip_address,
                    user_agent,
                    metadata["legal_basis"],
                    accessed_at,
                    correlation_id,
                    f"dataset={metadata['dataset']}",
                ),
            )
        conn.commit()

    logging.info(
        {
            "timestamp": accessed_at.isoformat(),
            "user_id": user_id,
            "user_role": user_role,
            "route": route,
            "ip_address": ip_address,
            "correlation_id": correlation_id,
            "school": SCHOOL_NAME,
        }
    )

    return {
        "user_id": user_id,
        "user_role": user_role,
        "route": route,
        "timestamp": accessed_at.isoformat(),
        "correlation_id": correlation_id,
    }


ensure_schema()


@app.get("/health")
def healthcheck():
    return jsonify({"status": "ok", "school": SCHOOL_NAME})


@app.get("/alunos")
def alunos():
    audit_event = persist_access_log("/alunos")
    return jsonify(
        {
            "rota": "/alunos",
            "descricao": "Consulta simulada de dados sensíveis dos alunos.",
            "auditoria": audit_event,
        }
    )


@app.get("/financeiro")
def financeiro():
    audit_event = persist_access_log("/financeiro")
    return jsonify(
        {
            "rota": "/financeiro",
            "descricao": "Consulta simulada de dados financeiros vinculados ao aluno.",
            "auditoria": audit_event,
        }
    )


@app.get("/matriculas")
def matriculas():
    audit_event = persist_access_log("/matriculas")
    return jsonify(
        {
            "rota": "/matriculas",
            "descricao": "Consulta simulada do status de matrícula e histórico escolar.",
            "auditoria": audit_event,
        }
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
