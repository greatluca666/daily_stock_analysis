#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 GitHub Pages 静态网站
将每日股票分析报告 (Markdown) 转换为美观的网页
- 使用 python-markdown + tables/fenced_code/toc 扩展
- 设计风格参考 apps/dsa-web: 青色/紫色渐变 + 深色主题 + 柔和阴影 + 动画
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
    """生成 CSS 样式 - 参考 dsa-web 设计风格"""
    css = r"""
:root {
    --primary: 189 100% 50%;
    --accent: 270 70% 65%;
    --success: 142 76% 36%;
    --warning: 38 92% 50%;
    --danger: 0 84% 60%;
    --background: 222 47% 11%;
    --foreground: 210 40% 98%;
    --card: 222 47% 14%;
    --border: 217 33% 17%;
    --muted: 217 33% 17%;
    --muted-foreground: 215 20% 65%;
    --elevated: 222 47% 16%;
    --hover: 222 47% 18%;
    --radius: 10px;
    --shadow-soft-card: 0 4px 16px rgba(0, 0, 0, 0.24), 0 0 0 1px rgba(255, 255, 255, 0.04);
    --shadow-soft-card-strong: 0 8px 24px rgba(0, 0, 0, 0.32), 0 0 0 1px rgba(255, 255, 255, 0.06);
}

* { margin: 0; padding: 0; box-sizing: border-box; }

html { scroll-behavior: smooth; }

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC",
        "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif;
    background: hsl(var(--background));
    color: hsl(var(--foreground));
    line-height: 1.7;
    -webkit-font-smoothing: antialiased;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 24px;
}

header.site-header {
    background: linear-gradient(135deg, 
        hsla(var(--accent), 0.2) 0%, 
        hsla(var(--primary), 0.15) 50%,
        hsla(var(--background), 1) 100%);
    padding: 64px 20px 80px;
    text-align: center;
    position: relative;
    overflow: hidden;
}
header.site-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at 30% 50%, hsla(var(--primary), 0.15), transparent 50%),
                radial-gradient(circle at 70% 50%, hsla(var(--accent), 0.12), transparent 50%);
    pointer-events: none;
}
header.site-header h1 {
    font-size: 2.5rem;
    letter-spacing: .5px;
    margin-bottom: 12px;
    position: relative;
    background: linear-gradient(135deg, hsl(var(--primary)), hsl(var(--accent)));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: fadeIn 0.6s ease-out;
}
header.site-header p {
    font-size: 1.05rem;
    color: hsl(var(--muted-foreground));
    position: relative;
    animation: fadeIn 0.8s ease-out;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes slideUp {
    from { opacity: 0; transform: translateY(16px); }
    to { opacity: 1; transform: translateY(0); }
}

.stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 16px;
    margin: -40px 0 32px;
    animation: slideUp 0.5s ease-out 0.2s both;
}
.stat-card {
    background: hsl(var(--card));
    padding: 22px 24px;
    border-radius: var(--radius);
    box-shadow: var(--shadow-soft-card);
    border: 1px solid hsl(var(--border));
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}
.stat-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-soft-card-strong);
}
.stat-card h3 {
    color: hsl(var(--muted-foreground));
    font-size: .85rem;
    text-transform: uppercase;
    letter-spacing: .08em;
    font-weight: 600;
    margin-bottom: 10px;
}
.stat-card .value {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, hsl(var(--primary)), hsl(var(--accent)));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.stat-card .value.text {
    -webkit-text-fill-color: hsl(var(--foreground));
    background: none;
    font-size: 1.2rem;
}

.section-title {
    font-size: 1.5rem;
    font-weight: 700;
    margin: 40px 0 20px;
    display: flex;
    align-items: center;
    gap: 8px;
    color: hsl(var(--foreground));
}

.reports-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
    gap: 20px;
    animation: slideUp 0.5s ease-out 0.4s both;
}
.report-card {
    background: hsl(var(--card));
    border-radius: var(--radius);
    padding: 24px;
    box-shadow: var(--shadow-soft-card);
    border: 1px solid hsl(var(--border));
    transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
    display: flex;
    flex-direction: column;
    gap: 12px;
    text-decoration: none;
    color: inherit;
}
.report-card:hover {
    transform: translateY(-4px);
    box-shadow: var(--shadow-soft-card-strong), 0 0 20px hsla(var(--primary), 0.2);
    border-color: hsla(var(--primary), 0.4);
}
.report-card .meta {
    display: flex;
    justify-content: space-between;
    align-items: center;
    color: hsl(var(--muted-foreground));
    font-size: .88rem;
}
.badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 999px;
    font-size: .78rem;
    font-weight: 600;
    border: 1px solid transparent;
}
.badge.stock  { 
    background: hsla(var(--primary), 0.15); 
    color: hsl(var(--primary)); 
    border-color: hsla(var(--primary), 0.3); 
}
.badge.market { 
    background: hsla(var(--warning), 0.15); 
    color: hsl(var(--warning)); 
    border-color: hsla(var(--warning), 0.3); 
}

.report-card h3 {
    font-size: 1.1rem;
    line-height: 1.45;
    color: hsl(var(--foreground));
}
.report-card .summary {
    color: hsl(var(--muted-foreground));
    font-size: .94rem;
    line-height: 1.6;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}
.report-card .read-more {
    margin-top: auto;
    color: hsl(var(--primary));
    font-weight: 600;
    align-self: flex-start;
}

.empty-state {
    background: hsl(var(--card));
    border: 1px dashed hsl(var(--border));
    border-radius: var(--radius);
    padding: 48px;
    text-align: center;
    color: hsl(var(--muted-foreground));
}

.report-content {
    background: hsl(var(--card));
    border-radius: var(--radius);
    padding: 40px 48px;
    box-shadow: var(--shadow-soft-card);
    border: 1px solid hsl(var(--border));
    margin: 28px 0 40px;
    animation: slideUp 0.45s ease-out;
}
.report-content h1,
.report-content h2,
.report-content h3,
.report-content h4 {
    color: hsl(var(--foreground));
    line-height: 1.35;
    margin-top: 1.8em;
    margin-bottom: .7em;
    font-weight: 700;
}
.report-content > h1:first-child { margin-top: 0; }
.report-content h1 { 
    font-size: 2rem; 
    padding-bottom: 16px; 
    border-bottom: 2px solid hsl(var(--border));
    background: linear-gradient(135deg, hsl(var(--primary)), hsl(var(--accent)));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.report-content h2 { 
    font-size: 1.5rem; 
    padding-left: 14px; 
    border-left: 4px solid hsl(var(--primary)); 
}
.report-content h3 { font-size: 1.2rem; color: hsl(var(--primary)); }
.report-content h4 { font-size: 1.05rem; color: hsl(var(--muted-foreground)); }
.report-content p { margin: 0 0 1em; color: hsl(var(--foreground)); }
.report-content strong { color: hsl(var(--foreground)); font-weight: 700; }
.report-content em { color: hsl(var(--muted-foreground)); }
.report-content a { 
    color: hsl(var(--primary)); 
    text-decoration: none; 
    border-bottom: 1px dashed hsl(var(--primary)); 
}
.report-content a:hover { border-bottom-style: solid; }
.report-content ul,
.report-content ol { margin: 0 0 1em 1.6em; }
.report-content li { margin-bottom: .4em; }
.report-content blockquote {
    margin: 1.2em 0;
    padding: 14px 20px;
    border-left: 4px solid hsl(var(--accent));
    background: hsl(var(--elevated));
    color: hsl(var(--muted-foreground));
    border-radius: 0 8px 8px 0;
}
.report-content hr {
    border: 0;
    border-top: 1px solid hsl(var(--border));
    margin: 2.5em 0;
}

.report-content code {
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    font-size: .9em;
    background: hsla(var(--primary), 0.12);
    color: hsl(var(--primary));
    padding: 3px 7px;
    border-radius: 5px;
}
.report-content pre {
    background: hsl(222 47% 9%);
    color: hsl(210 40% 92%);
    padding: 20px 22px;
    border-radius: var(--radius);
    overflow-x: auto;
    margin: 1.2em 0;
    font-size: .9rem;
    line-height: 1.6;
    box-shadow: inset 0 0 0 1px rgba(255, 255, 255, .04);
    border: 1px solid hsl(var(--border));
}
.report-content pre code {
    background: transparent;
    color: inherit;
    padding: 0;
}

.table-wrap {
    overflow-x: auto;
    margin: 1.4em 0;
    border-radius: var(--radius);
    border: 1px solid hsl(var(--border));
    box-shadow: var(--shadow-soft-card);
    background: hsl(var(--card));
}
.report-content table {
    width: 100%;
    border-collapse: collapse;
    font-size: .94rem;
}
.report-content thead th {
    background: hsl(var(--elevated));
    color: hsl(var(--foreground));
    font-weight: 700;
    text-align: left;
    padding: 13px 16px;
    border-bottom: 2px solid hsl(var(--border));
    white-space: nowrap;
}
.report-content tbody td {
    padding: 12px 16px;
    border-bottom: 1px solid hsl(var(--border));
    color: hsl(var(--muted-foreground));
    vertical-align: top;
}
.report-content tbody tr:hover td { 
    background: hsl(var(--hover)); 
    color: hsl(var(--foreground)); 
}
.report-content tbody tr:last-child td { border-bottom: none; }

.report-content table td:first-child,
.report-content table th:first-child { padding-left: 20px; }
.report-content table td:last-child,
.report-content table th:last-child { padding-right: 20px; }

.report-content .admonition {
    border-radius: var(--radius);
    padding: 16px 20px;
    margin: 1.4em 0;
    border-left: 4px solid hsl(var(--primary));
    background: hsla(var(--primary), 0.08);
    color: hsl(var(--foreground));
}
.report-content .admonition.warning { 
    border-color: hsl(var(--warning)); 
    background: hsla(var(--warning), 0.08); 
}
.report-content .admonition.danger  { 
    border-color: hsl(var(--danger));  
    background: hsla(var(--danger), 0.08); 
}
.report-content .admonition.tip     { 
    border-color: hsl(var(--success)); 
    background: hsla(var(--success), 0.08); 
}
.report-content .admonition-title { font-weight: 700; margin-bottom: .4em; }

.back-link {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    margin: 20px 0;
    color: hsl(var(--primary));
    text-decoration: none;
    font-weight: 600;
    transition: transform 0.2s ease;
}
.back-link:hover { transform: translateX(-4px); }

footer.site-footer {
    text-align: center;
    padding: 40px 20px 60px;
    color: hsl(var(--muted-foreground));
    font-size: .9rem;
    border-top: 1px solid hsl(var(--border));
    margin-top: 56px;
    background: hsl(var(--card));
}
footer.site-footer a { 
    color: hsl(var(--primary)); 
    text-decoration: none; 
}
footer.site-footer a:hover { text-decoration: underline; }

@media (max-width: 768px) {
    header.site-header { padding: 48px 18px 64px; }
    header.site-header h1 { font-size: 1.8rem; }
    .container { padding: 18px; }
    .reports-grid { grid-template-columns: 1fr; }
    .report-content { padding: 24px; }
    .report-content h1 { font-size: 1.6rem; }
    .report-content h2 { font-size: 1.3rem; }
    .stats { margin-top: -28px; }
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
            <a class="report-card" href="{href}">
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
                <p style="font-size:1.1rem;margin-bottom:8px;">📭 暂无分析报告</p>
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
    <p style="margin-top:10px;">
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
