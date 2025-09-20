# app/utils/file_operations.py
import hashlib
from datetime import datetime
from tkinter import filedialog

class FileOperationsManager:
    @staticmethod
    def save_query_log(query_data: dict, server_info: dict):
        """
        Save the executed summary and all per-database results to a .log file.
        Returns (success: bool, message: str).
        Expected query_data keys:
          - query: str
          - start_time: datetime
          - exec_time: float
          - total_rows: int
          - databases: list[str]
          - results: list[dict] with:
              { database: str, statement_num: int, result: str,
                success: bool, error: str (optional) }
        """
        # Basic validations
        if not query_data or not isinstance(query_data, dict):
            return False, "No query data to save"
        if not query_data.get("results"):
            return False, "No query results to save"

        # Build default filename
        q = query_data.get("query", "")
        ts: datetime = query_data.get("start_time", datetime.now())
        ts_str = ts.strftime("%Y%m%d_%H%M%S")
        q_hash = hashlib.md5(q.encode("utf-8")).hexdigest()[:8]
        default_name = f"SQLTool_{ts_str}_{q_hash}.log"

        # Ask where to save
        filepath = filedialog.asksaveasfilename(
            title="Save Query Log",
            initialfile=default_name,
            defaultextension=".log",
            filetypes=[("Log Files", "*.log"), ("Text Files", "*.txt"), ("All Files", "*.*")],
        )
        if not filepath:
            return False, "Save cancelled"

        # Compose header
        server = server_info.get("server") if server_info else "N/A"
        user = server_info.get("username") if server_info else "N/A"
        header_lines = [
            f"SQL Tool Query Log - {ts_str}",
            f"Executed on server: {server}",
            f"User: {user}",
            "-" * 80,
            "",
            "QUERY:",
            q,
            "",
            f"Execution time: {query_data.get('exec_time', 0):.2f} seconds",
            f"Total rows returned: {int(query_data.get('total_rows', 0))}",
            f"Databases queried: {', '.join(query_data.get('databases', []))}",
            "-" * 80,
            "",
            "RESULTS:",
        ]

        # Write file
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(header_lines))

                for item in query_data["results"]:
                    f.write("\n")
                    f.write(f"Database: {item.get('database','N/A')}\n")
                    stmt_num = item.get("statement_num", 0)
                    if isinstance(stmt_num, int) and stmt_num > 0:
                        f.write(f"Query {stmt_num}:\n")
                    if not item.get("success", True):
                        f.write(f"ERROR: {item.get('error','')}\n")
                    # The 'result' field already contains the formatted table or rows
                    f.write(item.get("result", ""))
                    f.write("\n")

                f.write("\n" + "=" * 80 + "\n")
                f.write(f"Log generated at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

            return True, f"Log saved successfully:\n{filepath}"
        except Exception as exc:
            return False, f"Failed to save log file:\n{exc}"
