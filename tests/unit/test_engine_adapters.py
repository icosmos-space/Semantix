import pytest

from semantix.engines.fixture import FixtureEngineAdapter
from semantix.query.markdown import build_answer_markdown, rows_to_gpt_vis_column


@pytest.mark.asyncio
async def test_fixture_online_rate():
    adapter = FixtureEngineAdapter()
    result = await adapter.generate_sql("查询各项目最近 7 天的设备在线率。", {})
    assert result.engine == "fixture"
    assert "online_rate" in result.sql


def test_gpt_vis_fence():
    fence = rows_to_gpt_vis_column(
        "近7天设备在线率",
        "project_id",
        "online_rate",
        [{"project_id": "项目A", "online_rate": 0.92}],
    )
    assert fence.startswith("```GPT-Vis")
    assert "vis column" in fence


def test_answer_contains_sql_and_chart():
    md = build_answer_markdown(
        intro="结果：",
        columns=["project_id", "online_rate"],
        rows=[{"project_id": "A", "online_rate": 0.9}],
        sql="SELECT 1",
        chart_category="project_id",
        chart_value="online_rate",
        chart_title="在线率",
    )
    assert "```GPT-Vis" in md
    assert "```sql" in md
