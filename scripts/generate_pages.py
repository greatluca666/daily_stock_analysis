#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 GitHub Pages 静态网站
将每日股票分析报告 (Markdown) 转换为美观的网页
- 使用 python-markdown + tables/fenced_code/toc 扩展
- 现代化 UI，支持深色卡片、表格美化、代码高亮、响应式布局
"""

import re
from pathlib import Path
from datetime import datetime
from typing import List, Dict
from html import escape

import markdown

REPORTS_DIR = Path("reports")
DOCS_DIR = Path("docs")

MD_EXTENSIONS = [
    "tables",
    "fenced_code",
    "sane_lists",
    "nl2br",
    "toc",
    "admonition",
    "attr_list",
]

MD_EXTENSION_CONFIGS = {
    "toc": {"permalink": False},
}


def ensure_dirs():
    DOCS_DIR.mkdir(exist_ok=True)
    (DOCS_DIR / "reports").mkdir(exist_ok=True)
    (DOCS_DIR / "css").mkdir(exist_ok=True)


def parse_report_date(filename: str) -> datetime:
    match = re.search(r"(\d{8})", filename)
    if match:
        try:
            return datetime.strptime(match.group(1), "%Y%m%d")
        except ValueError:
            pass
    return datetime.now()


def extract_title(content: str, fallback: str) -> str:
    for line in content.split("\n"):
        line = line.strip()
        if line.startswith("# "):
            return line[2:].strip()
    return fallback


def extract_summary(content: str, max_chars: int = 220) -> str:
    text = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
    text = re.sub(r"!\[[^\]]*\]\([^\)]*\)", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", text)
    text = re.sub(r"[#>*_`|\-]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars] + ("…" if len(text) > max_chars else "")


def get_all_reports() -> List[Dict]:
    reports: List[Dict] = []
    if not REPORTS_DIR.exists():
        return reports

    for file in REPORTS_DIR.glob("*.md"):
        if file.name.startswith("."):
            continue
        date = parse_report_date(file.name)
        with open(file, "r", encoding="utf-8") as f:
            content = f.read()

        is_market = "market_review" in file.name.lower() or "大盘" in content[:80]
        title = extract_title(content, f"{date.strftime('%Y年%m月%d日')} 股票分析报告")

        reports.append({
            "filename": file.name,
            "date": date,
            "date_str": date.strftime("%Y-%m-%d"),
            "title": title,
            "summary": extract_summary(content),
            "content": content,
            "is_market_review": is_market,
        })

    reports.sort(key=lambda x: x["date"], reverse=True)
    return reports


def render_markdown(md_text: str) -> str:
    md = markdown.Markdown(
        extensions=MD_EXTENSIONS,
        extension_configs=MD_EXTENSION_CONFIGS,
        output_format="html5",
    )
    html = md.convert(md_text)
    html = re.sub(
        r"<table>",
        '<div class="table-wrap"><table>',
        html,
    )
    html = re.sub(r"</table>", "</table></div>", html)
    return html


def generate_css():
    css = r"""
:root {
    --primary: #2563eb;
    --primary-dark: #1d4ed8;
    --accent: #8b5cf6;
    --success: #10b981;
    --warning: #f59e0b;
    --danger: #ef4444;
    --bg: #f6f8fb;
    --bg-soft: #eef2f7;
    --card: #ffffff;
    --text: #111827;
    --text-soft: #4b5563;
    --muted: #6b7280;
    --border: #e5e7eb;
    --code-bg: #0f172a;
    --code-text: #e2e8f0;
    --table-header-bg: #f1f5f9;
    --table-row-alt: #f9fafb;
    --shadow-sm: 0 1px 2px rgba(15, 23, 42, .06);
    --shadow-md: 0 4px 14px rgba(15, 23, 42, .08);
    --shadow-lg: 0 12px 32px rgba(15, 23, 42, .12);
    --radius: 14px;
}

* { margin: 0; padding: 0; box-sizing: border-box; }

html { scroll-behavior: smooth; }

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
        "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    line-height: 1.7;
    -webkit-font-smoothing: antialiased;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 24px;
}

header.site-header {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 60%, #db2777 100%);
    color: #fff;
    padding: 56px 20px 64px;
    text-align: center;
    box-shadow: var(--shadow-md);
}
header.site-header h1 {
    font-size: 2.4rem;
    letter-spacing: .5px;
    margin-bottom: 8px;
}
header.site-header p {
    font-size: 1.05rem;
    opacity: .9;
}

.stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin: -32px 0 28px;
}
.stat-card {
    background: var(--card);
    padding: 20px 22px;
    border-radius: var(--radius);
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border);
}
.stat-card h3 {
    color: var(--muted);
    font-size: .85rem;
    text-transform: uppercase;
    letter-spacing: .08em;
    font-weight: 600;
    margin-bottom: 8px;
}
.stat-card .value {
    font-size: 1.9rem;
    font-weight: 700;
    background: linear-gradient(135deg, var(--primary), var(--accent));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.stat-card .value.text {
    -webkit-text-fill-color: var(--text);
    background: none;
    font-size: 1.2rem;
}

.section-title {
    font-size: 1.4rem;
    font-weight: 700;
    margin: 32px 0 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.reports-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(330px, 1fr));
    gap: 18px;
}
.report-card {
    background: var(--card);
    border-radius: var(--radius);
    padding: 22px;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border);
    transition: transform .18s ease, box-shadow .18s ease, border-color .18s ease;
    display: flex;
    flex-direction: column;
    gap: 10px;
}
.report-card:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow-md);
    border-color: #c7d2fe;
}
.report-card .meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: var(--muted);
    font-size: .88rem;
}
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: .78rem;
    font-weight: 600;
    border: 1px solid transparent;
}
.badge.stock  { background: #dbeafe; color: #1e40af; border-color: #bfdbfe; }
.badge.market { background: #fef3c7; color: #92400e; border-color: #fde68a; }

.report-card h3 {
    font-size: 1.08rem;
    line-height: 1.45;
    color: var(--text);
}
.report-card .summary {
    color: var(--text-soft);
    font-size: .94rem;
    line-height: 1.6;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
.report-card .read-more {
    margin-top: auto;
    color: var(--primary);
    font-weight: 600;
    text-decoration: none;
    align-self: flex-start;
}
.report-card .read-more:hover { color: var(--primary-dark); }

.empty-state {
    background: var(--card);
    border: 1px dashed var(--border);
    border-radius: var(--radius);
    padding: 40px;
    text-align: center;
    color: var(--muted);
}

.report-content {
    background: var(--card);
    border-radius: var(--radius);
    padding: 40px 44px;
    box-shadow: var(--shadow-sm);
    border: 1px solid var(--border);
    margin: 24px 0 36px;
}
.report-content h1,
.report-content h2,
.report-content h3,
.report-content h4 {
    color: var(--text);
    line-height: 1.35;
    margin-top: 1.6em;
    margin-bottom: .6em;
    font-weight: 700;
}
.report-content > h1:first-child { margin-top: 0; }
.report-content h1 { font-size: 1.9rem; padding-bottom: 14px; border-bottom: 2px solid var(--border); }
.report-content h2 { font-size: 1.45rem; padding-left: 12px; border-left: 4px solid var(--primary); }
.report-content h3 { font-size: 1.18rem; color: var(--primary-dark); }
.report-content h4 { font-size: 1.02rem; color: var(--text-soft); }
.report-content p { margin: 0 0 1em; color: var(--text); }
.report-content strong { color: var(--text); font-weight: 700; }
.report-content em { color: var(--text-soft); }
.report-content a { color: var(--primary); text-decoration: none; border-bottom: 1px dashed var(--primary); }
.report-content a:hover { color: var(--primary-dark); }
.report-content ul,
.report-content ol { margin: 0 0 1em 1.4em; }
.report-content li { margin-bottom: .35em; }
.report-content blockquote {
    margin: 1em 0;
    padding: 12px 18px;
    border-left: 4px solid var(--accent);
    background: var(--bg-soft);
    color: var(--text-soft);
    border-radius: 0 8px 8px 0;
}
.report-content hr {
    border: 0;
    border-top: 1px solid var(--border);
    margin: 2em 0;
}

.report-content code {
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    font-size: .92em;
    background: #eef2ff;
    color: #3730a3;
    padding: 2px 6px;
    border-radius: 4px;
}
.report-content pre {
    background: var(--code-bg);
    color: var(--code-text);
    padding: 18px 20px;
    border-radius: 10px;
    overflow-x: auto;
    margin: 1em 0;
    font-size: .9rem;
    line-height: 1.55;
    box-shadow: inset 0 0 0 1px rgba(255, 255, 255, .04);
}
.report-content pre code {
    background: transparent;
    color: inherit;
    padding: 0;
}

.table-wrap {
    overflow-x: auto;
    margin: 1.2em 0;
    border-radius: 10px;
    border: 1px solid var(--border);
    box-shadow: var(--shadow-sm);
    background: var(--card);
}
.report-content table {
    width: 100%;
    border-collapse: collapse;
    font-size: .94rem;
}
.report-content thead th {
    background: var(--table-header-bg);
    color: var(--text);
    font-weight: 700;
    text-align: left;
    padding: 12px 14px;
    border-bottom: 2px solid var(--border);
    white-space: nowrap;
}
.report-content tbody td {
    padding: 11px 14px;
    border-bottom: 1px solid var(--border);
    color: var(--text-soft);
    vertical-align: top;
}
.report-content tbody tr:nth-child(even) td { background: var(--table-row-alt); }
.report-content tbody tr:hover td { background: #eef2ff; color: var(--text); }
.report-content tbody tr:last-child td { border-bottom: none; }

.report-content table td:first-child,
.report-content table th:first-child { padding-left: 18px; }
.report-content table td:last-child,
.report-content table th:last-child { padding-right: 18px; }

.report-content .admonition {
    border-radius: 10px;
    padding: 14px 18px;
    margin: 1.2em 0;
    border-left: 4px solid var(--primary);
    background: #eff6ff;
    color: var(--text);
}
.report-content .admonition.warning { border-color: var(--warning); background: #fffbeb; }
.report-content .admonition.danger  { border-color: var(--danger);  background: #fef2f2; }
.report-content .admonition.tip     { border-color: var(--success); background: #ecfdf5; }
.report-content .admonition-title { font-weight: 700; margin-bottom: .3em; }

.back-link {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin: 18px 0;
    color: var(--primary);
    text-decoration: none;
    font-weight: 600;
}
.back-link:hover { color: var(--primary-dark); }

footer.site-footer {
    text-align: center;
    padding: 36px 20px 56px;
    color: var(--muted);
    font-size: .9rem;
    border-top: 1px solid var(--border);
    margin-top: 48px;
    background: var(--card);
}
footer.site-footer a { color: var(--primary); text-decoration: none; }
footer.site-footer a:hover { text-decoration: underline; }

@media (max-width: 768px) {
    header.site-header { padding: 40px 18px 56px; }
    header.site-header h1 { font-size: 1.7rem; }
    .container { padding: 18px; }
    .reports-grid { grid-template-columns: 1fr; }
    .report-content { padding: 22px; }
    .report-content h1 { font-size: 1.5rem; }
    .report-content h2 { font-size: 1.2rem; }
    .stats { margin-top: -24px; }
}
"""
    with open(DOCS_DIR / "css" / "style.css", "w", encoding="utf-8") as f:
        f.write(css)


def html_shell(title: str, body: str, css_path: str = "css/style.css") -> str:
    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="AI 驱动的每日股票分析报告">
    <title>{escape(title)}</title>
    <link rel="stylesheet" href="{css_path}">
</head>
<body>
{body}
</body>
</html>
"""


def generate_index_page(reports: List[Dict]):
    total = len(reports)
    stock_count = len([r for r in reports if not r["is_market_review"]])
    market_count = len([r for r in reports if r["is_market_review"]])
    latest = reports[0]["date_str"] if reports else "暂无"

    cards_html = ""
    if reports:
        for r in reports:
            badge_cls = "market" if r["is_market_review"] else "stock"
            badge_text = "大盘复盘" if r["is_market_review"] else "个股分析"
            href = "reports/" + r["filename"].replace(".md", ".html")
            cards_html += f"""
            <a class="report-card" href="{href}" style="text-decoration:none;color:inherit;">
                <div class="meta">
                    <span>📅 {r['date_str']}</span>
                    <span class="badge {badge_cls}">{badge_text}</span>
                </div>
                <h3>{escape(r['title'])}</h3>
                <div class="summary">{escape(r['summary'])}</div>
                <span class="read-more">查看详情 →</span>
            </a>"""
    else:
        cards_html = """
            <div class="empty-state">
                <p style="font-size:1.1rem;margin-bottom:6px;">📭 暂无分析报告</p>
                <p>下次每日分析任务运行后，报告将自动出现在这里。</p>
            </div>"""

    body = f"""
<header class="site-header">
    <h1>📈 每日股票分析</h1>
    <p>AI 驱动的智能股票分析系统</p>
</header>

<div class="container">
    <div class="stats">
        <div class="stat-card"><h3>总报告数</h3><div class="value">{total}</div></div>
        <div class="stat-card"><h3>个股分析</h3><div class="value">{stock_count}</div></div>
        <div class="stat-card"><h3>大盘复盘</h3><div class="value">{market_count}</div></div>
        <div class="stat-card"><h3>最新更新</h3><div class="value text">{latest}</div></div>
    </div>

    <div class="section-title">📊 历史报告</div>
    <div class="reports-grid">{cards_html}
    </div>
</div>

<footer class="site-footer">
    <p>🤖 由 AI 自动生成 · 数据仅供参考，不构成投资建议</p>
    <p style="margin-top:8px;">
        <a href="https://github.com/greatluca666/daily_stock_analysis" target="_blank" rel="noopener">GitHub 仓库</a>
    </p>
</footer>
"""
    with open(DOCS_DIR / "index.html", "w", encoding="utf-8") as f:
        f.write(html_shell("每日股票分析 · 历史报告", body))


def generate_report_pages(reports: List[Dict]):
    for r in reports:
        rendered = render_markdown(r["content"])
        body = f"""
<header class="site-header">
    <h1>📈 每日股票分析</h1>
    <p>{r['date_str']}</p>
</header>

<div class="container">
    <a href="../index.html" class="back-link">← 返回首页</a>

    <article class="report-content">
        {rendered}
    </article>

    <a href="../index.html" class="back-link">← 返回首页</a>
</div>

<footer class="site-footer">
    <p>🤖 由 AI 自动生成 · 数据仅供参考，不构成投资建议</p>
</footer>
"""
        out = DOCS_DIR / "reports" / r["filename"].replace(".md", ".html")
        with open(out, "w", encoding="utf-8") as f:
            f.write(html_shell(r["title"], body, css_path="../css/style.css"))


def main():
    print("🚀 开始生成 GitHub Pages 网站...")
    ensure_dirs()
    reports = get_all_reports()
    print(f"📊 找到 {len(reports)} 个报告")
    print("🎨 生成样式文件...")
    generate_css()
    print("📄 生成首页...")
    generate_index_page(reports)
    print("📝 生成报告详情页...")
    generate_report_pages(reports)
    print("✅ 网站生成完成！")
    print(f"📁 输出目录: {DOCS_DIR.absolute()}")


if __name__ == "__main__":
    main()
