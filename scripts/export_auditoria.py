import argparse
import csv
import os
from datetime import datetime
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

DEFAULT_DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://escola_admin:troque-esta-senha@localhost:5432/escola_iam",
)
DEFAULT_OUTPUT_DIR = Path(os.getenv("AUDIT_EXPORT_DIR", "./evidencias/auditoria"))


def parse_args():
    parser = argparse.ArgumentParser(
        description="Exporta logs de auditoria da escola para CSV compatível com fiscalização do TCM/BA."
    )
    parser.add_argument("--database-url", default=DEFAULT_DATABASE_URL)
    parser.add_argument("--inicio", help="Data inicial no formato YYYY-MM-DD")
    parser.add_argument("--fim", help="Data final no formato YYYY-MM-DD")
    parser.add_argument("--rota", help="Filtra por rota sensível específica")
    parser.add_argument("--saida", help="Caminho do CSV de saída")
    return parser.parse_args()


def sanitize_for_csv(value):
    if isinstance(value, str) and value.startswith(("=", "+", "-", "@")):
        return f"'{value}"
    return value


def build_query(args):
    filters = []
    params = []

    if args.inicio:
        filters.append("accessed_at >= %s")
        params.append(datetime.fromisoformat(args.inicio))

    if args.fim:
        filters.append("accessed_at < (%s::date + INTERVAL '1 day')")
        params.append(args.fim)

    if args.rota:
        filters.append("route = %s")
        params.append(args.rota)

    where_clause = f"WHERE {' AND '.join(filters)}" if filters else ""
    query = f"""
        SELECT
            id,
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
        FROM audit_access_logs
        {where_clause}
        ORDER BY accessed_at ASC
    """
    return query, params


def export_csv(database_url: str, output_path: Path, args):
    output_path.parent.mkdir(parents=True, exist_ok=True)
    query, params = build_query(args)

    with psycopg.connect(database_url, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(query, params)
            rows = cur.fetchall()

    sanitized_rows = [
        {key: sanitize_for_csv(value) for key, value in row.items()} for row in rows
    ]

    with output_path.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(
            csvfile,
            fieldnames=[
                "id",
                "user_id",
                "user_role",
                "route",
                "action",
                "ip_address",
                "user_agent",
                "legal_basis",
                "accessed_at",
                "correlation_id",
                "notes",
            ],
        )
        writer.writeheader()
        writer.writerows(sanitized_rows)

    return len(rows)


def main():
    args = parse_args()
    timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    output_path = Path(args.saida) if args.saida else DEFAULT_OUTPUT_DIR / f"auditoria_tcm_ba_{timestamp}.csv"
    total = export_csv(args.database_url, output_path, args)
    print(f"Arquivo gerado: {output_path} | registros exportados: {total}")


if __name__ == "__main__":
    main()
