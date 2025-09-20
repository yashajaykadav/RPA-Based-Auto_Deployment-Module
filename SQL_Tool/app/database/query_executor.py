import time
import pyodbc
import psycopg2
from datetime import datetime


class QueryExecutor:
    def __init__(self, db_manager, message_queue):
        self.db_manager = db_manager
        self.message_queue = message_queue

    def execute_query(self, databases, query):
        """Execute query against multiple databases and return aggregate info."""
        # Normalize query into string
        if isinstance(query, list):
            query = " ".join(query)
        elif not isinstance(query, str):
            query = str(query)

        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        if not databases:
            raise ValueError("No databases selected")

        start_time = time.time()
        overall_total_rows = 0
        databases_info = []

        # Split statements by semicolon
        statements = [s.strip() for s in query.split(";") if s.strip()]
        if not statements:
            raise ValueError("No valid SQL statements found")

        for db in databases:
            db_info = self._execute_on_database(db, statements)
            databases_info.append(db_info)
            overall_total_rows += db_info["total_rows"]

        total_exec_time = time.time() - start_time

        # Send results to UI
        self._send_results(databases_info, total_exec_time, overall_total_rows)

        # Return full structure to controller
        return {
            "exec_time": total_exec_time,
            "total_rows": overall_total_rows,
            "databases_info": databases_info,  # includes results_struct for saving
        }

    def _execute_on_database(self, db, statements):
        """Run list of statements on one database and collect results."""
        db_start_time = time.time()
        db_total_rows = 0
        db_errors = []
        db_statement_count = 0
        db_results_text = []
        db_results_struct = []

        try:
            self.message_queue.put(("status", f"🔄 Connecting to {db}..."))

            with self.db_manager.database_connection(db) as conn:
                cursor = conn.cursor()

                for i, statement in enumerate(statements, 1):
                    db_statement_count += 1
                    try:
                        cursor.execute(statement)

                        rows = []
                        if cursor.description:
                            while True:
                                batch = cursor.fetchmany(1000)
                                if not batch:
                                    break
                                rows.extend(batch)

                        result_text = self._format_query_results(cursor, rows, db, i)
                        db_results_text.append(result_text)

                        db_results_struct.append({
                            "database": db,
                            "statement_num": i,
                            "result": result_text,
                            "success": True
                        })

                        if cursor.description:
                            db_total_rows += len(rows)

                        # FIX: This method only exists for pyodbc, not psycopg2.
                        # Make it conditional to prevent errors.
                        if isinstance(conn, pyodbc.Connection):
                            while cursor.nextset():
                                pass
                        
                        # FIX: Commit after each successful statement for correct behavior.
                        conn.commit()

                    # FIX: Catch errors from BOTH drivers for generic handling.
                    except (pyodbc.Error, psycopg2.Error) as e:
                        # Rollback the transaction on error
                        if conn:
                            conn.rollback()
                            
                        error_msg = f"\nError in Query {i} on {db}: {str(e).strip()}\n"
                        db_results_text.append(error_msg)
                        db_errors.append(f"Query {i}: {str(e).strip()}")
                        db_results_struct.append({
                            "database": db,
                            "statement_num": i,
                            "result": error_msg,
                            "success": False,
                            "error": str(e).strip()
                        })

        except Exception as e:
            error_msg = f"\nConnection error with {db}: {str(e).strip()}\n"
            db_results_text.append(error_msg)
            db_errors.append(f"Connection: {str(e).strip()}")
            db_results_struct.append({
                "database": db, "statement_num": 0, "result": error_msg,
                "success": False, "error": str(e).strip()
            })

        db_exec_time = time.time() - db_start_time

        return {
            "name": db,
            "exec_time": db_exec_time,
            "total_rows": db_total_rows,
            "status": "Success" if not db_errors else "Error",
            "statement_count": db_statement_count,
            "errors": db_errors,
            "results": db_results_text,
            "results_struct": db_results_struct
        }

    def _format_query_results(self, cursor, rows, db_name, statement_num):
        """Format query results for display with enhanced tabular styling."""
        if not cursor.description:
            return (
                f"\n{'═' * 80}\n"
                f"📋 Query {statement_num} executed on {db_name}\n"
                f"{'═' * 80}\n"
                f"✅ Rows affected: {cursor.rowcount}\n"
                f"{'═' * 80}\n"
            )

        column_names = [c[0] for c in cursor.description]
        if not rows:
            return (
                f"\n{'═' * 80}\n"
                f"📋 Results from Query {statement_num} on {db_name}\n"
                f"{'═' * 80}\n"
                f"⚠️  No rows returned\n"
                f"{'═' * 80}\n"
            )

        # Column width bounds
        min_width = 8
        max_width = 30
        col_widths = []
        # sample first 100 rows for performance
        for i, name in enumerate(column_names):
            name_w = len(str(name))
            data_ws = [len(str(row[i])) for row in rows[:100]] if rows else [0]
            width = max(min_width, min(max_width, max(name_w, max(data_ws) if data_ws else 0)))
            col_widths.append(width)

        def trunc(text, width):
            text = str(text)
            return text if len(text) <= width else text[: width - 3] + "..."

        header_line = f"\n{'═' * 100}\n"
        title_line = f"📋 Results from Query {statement_num} on {db_name} (Showing {len(rows):,} rows)\n"
        separator_line = f"{'═' * 100}\n"

        top = "┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐"
        hdr = "│ " + " │ ".join(str(n).ljust(w) for n, w in zip(column_names, col_widths)) + " │"
        mid = "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤"

        body = []
        for row in rows:
            body.append("│ " + " │ ".join(trunc(v, w).ljust(w) for v, w in zip(row, col_widths)) + " │")

        bot = "└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘"
        total_line = f"\n✅ Total rows: {len(rows):,}\n{'═' * 100}\n"

        return "\n".join([header_line, title_line, separator_line, top, hdr, mid, *body, bot, total_line])

    def _send_results(self, databases_info, total_exec_time, overall_total_rows):
        """Send execution summary and results to the UI message queue."""
        summary = self._generate_execution_summary(databases_info, total_exec_time, overall_total_rows)
        self.message_queue.put(("execution_summary", summary))
        for db_info in reversed(databases_info):
            for result in db_info["results"]:
                self.message_queue.put(("result", result))

    def _generate_execution_summary(self, databases_info, total_exec_time, overall_total_rows):
        """Generate a compact execution summary table."""
        lines = []
        lines.append("=" * 100)
        lines.append("EXECUTION SUMMARY")
        lines.append("=" * 100)
        lines.append(f"Total Execution Time: {total_exec_time:.3f} seconds")
        lines.append(f"Overall Total Rows  : {overall_total_rows:,}")
        lines.append(f"Databases Processed : {len(databases_info)}")
        lines.append(f"Executed At         : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("")
        lines.append("DATABASE EXECUTION DETAILS")
        lines.append("=" * 100)

        headers = ["Database", "Time(s)", "Rows", "Statements", "Status", "Errors"]
        widths = [20, 10, 12, 12, 10, 30]

        hdr_row = "|" + "|".join(f" {h:<{w-1}}" for h, w in zip(headers, widths)) + "|"
        sep_row = "|" + "|".join("-" * w for w in widths) + "|"
        lines.append(hdr_row)
        lines.append(sep_row)

        for db_info in reversed(databases_info):
            db_name = db_info["name"][:19]
            row_vals = [
                db_name,
                f"{db_info['exec_time']:.3f}",
                f"{db_info['total_rows']:,}",
                str(db_info["statement_count"]),
                db_info["status"],
                ("None" if not db_info.get("errors") else
                 (db_info["errors"][0][:27] + "..." if len(db_info["errors"][0]) > 27 else db_info["errors"][0])
                 if len(db_info["errors"]) == 1 else f"{len(db_info['errors'])} error(s)")
            ]
            lines.append("|" + "|".join(f" {str(val):<{w-1}}" for val, w in zip(row_vals, widths)) + "|")

        lines.append(sep_row)
        lines.append("=" * 100)
        lines.append("")
        return "\n".join(lines)
