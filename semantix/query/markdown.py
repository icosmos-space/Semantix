from typing import Any


def rows_to_gpt_vis_column(
    title: str,
    category_key: str,
    value_key: str,
    rows: list[dict[str, Any]],
) -> str:
    lines = ["vis column", f"title {title}", "data"]
    for r in rows:
        lines.append(f"  - category {r.get(category_key, '')}")
        lines.append(f"    value {r.get(value_key, 0)}")
    body = "\n".join(lines)
    return f"```GPT-Vis\n{body}\n```"


def rows_to_markdown_table(columns: list[str], rows: list[dict[str, Any]], *, limit: int = 20) -> str:
    if not columns:
        return "_（无数据）_"
    header = "| " + " | ".join(columns) + " |"
    sep = "| " + " | ".join(["---"] * len(columns)) + " |"
    body_lines = []
    for row in rows[:limit]:
        body_lines.append("| " + " | ".join(str(row.get(c, "")) for c in columns) + " |")
    return "\n".join([header, sep, *body_lines])


def build_answer_markdown(
    *,
    intro: str,
    columns: list[str],
    rows: list[dict[str, Any]],
    sql: str,
    chart_category: str | None = None,
    chart_value: str | None = None,
    chart_title: str | None = None,
) -> str:
    parts = [intro, "", rows_to_markdown_table(columns, rows), ""]
    if chart_category and chart_value and rows:
        parts.append(
            rows_to_gpt_vis_column(
                chart_title or "查询结果",
                chart_category,
                chart_value,
                rows,
            )
        )
        parts.append("")
    parts.append("```sql")
    parts.append(sql)
    parts.append("```")
    return "\n".join(parts)
