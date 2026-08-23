"""Read-only audit-log service for SmartLoan Analytics."""

from database import get_connection
from modules.authentication import Session


def list_audit_logs(session: Session, limit: int = 200) -> list[dict]:
    if not session.can("manage_users"):
        raise PermissionError("Only an Administrator can view audit logs.")

    limit = max(1, min(int(limit), 1000))

    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT
                a.log_id,
                COALESCE(u.username, 'SYSTEM') AS username,
                a.action,
                a.details,
                a.created_at
            FROM audit_logs a
            LEFT JOIN users u ON u.user_id=a.user_id
            ORDER BY a.log_id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [dict(row) for row in rows]
