#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成 GitHub Pages 静态网站
将每日股票分析报告转换为美观的网页
"""

import os
import json
from pathlib import Path
from datetime import datetime
import re
from typing import List, Dict

# 配置
REPORTS_DIR = Path("reports")
DOCS_DIR = Path("docs")
TEMPLATE_DIR = Path("scripts/templates")


def ensure_dirs():
    """确保必要的目录存在"""
    DOCS_DIR.mkdir(exist_ok=True)
    (DOCS_DIR / "reports").mkdir(exist_ok=True)
    (DOCS_DIR / "css").mkdir(exist_ok=True)


def parse_report_date(filename: str) -> datetime:
    """从文件名解析日期"""
    match = re.search(r'(\d{8})', filename)
    if match:
        date_str = match.group(1)
        return datetime.strptime(date_str, '%Y%m%d')
    return datetime.now()


def get_all_reports() -> List[Dict]:
    """获取所有报告文件"""
    reports = []
    
    if not REPORTS_DIR.exists():
        return reports
    
    for file in REPORTS_DIR.glob("*.md"):
        if file.name.startswith('.'):
            continue
            
        date = parse_report_date(file.name)
        
        # 读取报告内容的前几行作为摘要
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            summary = '\n'.join(lines[:10]) if len(lines) > 10 else content
        
        reports.append({
            'filename': file.name,
            'date': date,
            'date_str': date.strftime('%Y-%m-%d'),
            'title': f"{date.strftime('%Y年%m月%d日')} 股票分析报告",
            'summary': summary,
            'content': content,
            'is_market_review': 'market_review' in file.name.lower()
        })
    
    # 按日期倒序排列
    reports.sort(key=lambda x: x['date'], reverse=True)
    return reports


def convert_md_to_html(md_content: str) -> str:
    """简单的 Markdown 转 HTML（基础版本）"""
    html = md_content
    
    # 标题
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    
    # 粗体
    html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
    
    # 列表
    html = re.sub(r'^\- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
    
    # 段落
    html = re.sub(r'\n\n', '</p><p>', html)
    html = '<p>' + html + '</p>'
    
    # 代码块
    html = re.sub(r'```(.+?)```', r'<pre><code>\1</code></pre>', html, flags=re.DOTALL)
    
    return html


def generate_css():
    """生成 CSS 样式文件"""
    css_content = """
:root {
    --primary-color: #2563eb;
    --success-color: #10b981;
    --warning-color: #f59e0b;
    --danger-color: #ef4444;
    --bg-color: #f9fafb;
    --card-bg: #ffffff;
    --text-color: #1f2937;
    --text-secondary: #6b7280;
    --border-color: #e5e7eb;
}

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    background: var(--bg-color);
    color: var(--text-color);
    line-height: 1.6;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
}

header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 40px 20px;
    text-align: center;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

header h1 {
    font-size: 2.5rem;
    margin-bottom: 10px;
}

header p {
    font-size: 1.1rem;
    opacity: 0.9;
}

.stats {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin: 30px 0;
}

.stat-card {
    background: var(--card-bg);
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    text-align: center;
}

.stat-card h3 {
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin-bottom: 10px;
}

.stat-card .value {
    font-size: 2rem;
    font-weight: bold;
    color: var(--primary-color);
}

.reports-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
    gap: 20px;
    margin: 30px 0;
}

.report-card {
    background: var(--card-bg);
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: transform 0.2s, box-shadow 0.2s;
    cursor: pointer;
}

.report-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.report-card .date {
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin-bottom: 10px;
}

.report-card h3 {
    color: var(--text-color);
    margin-bottom: 15px;
}

.report-card .badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 500;
    margin-bottom: 10px;
}

.badge.stock {
    background: #dbeafe;
    color: #1e40af;
}

.badge.market {
    background: #fef3c7;
    color: #92400e;
}

.report-card .summary {
    color: var(--text-secondary);
    font-size: 0.9rem;
    line-height: 1.5;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    overflow: hidden;
}

.report-card .read-more {
    color: var(--primary-color);
    text-decoration: none;
    font-weight: 500;
    margin-top: 10px;
    display: inline-block;
}

.report-content {
    background: var(--card-bg);
    border-radius: 10px;
    padding: 40px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    margin: 30px 0;
}

.report-content h1 {
    color: var(--text-color);
    margin-bottom: 20px;
    padding-bottom: 15px;
    border-bottom: 2px solid var(--border-color);
}

.report-content h2 {
    color: var(--text-color);
    margin-top: 30px;
    margin-bottom: 15px;
}

.report-content h3 {
    color: var(--text-color);
    margin-top: 20px;
    margin-bottom: 10px;
}

.report-content p {
    margin-bottom: 15px;
    line-height: 1.8;
}

.report-content pre {
    background: #f3f4f6;
    padding: 15px;
    border-radius: 5px;
    overflow-x: auto;
    margin: 15px 0;
}

.report-content code {
    font-family: 'Courier New', monospace;
    font-size: 0.9rem;
}

.back-link {
    display: inline-block;
    margin: 20px 0;
    color: var(--primary-color);
    text-decoration: none;
    font-weight: 500;
}

.back-link:hover {
    text-decoration: underline;
}

footer {
    text-align: center;
    padding: 40px 20px;
    color: var(--text-secondary);
    border-top: 1px solid var(--border-color);
    margin-top: 60px;
}

@media (max-width: 768px) {
    header h1 {
        font-size: 1.8rem;
    }
    
    .reports-grid {
        grid-template-columns: 1fr;
    }
    
    .report-content {
        padding: 20px;
    }
}
"""
    
    css_file = DOCS_DIR / "css" / "style.css"
    with open(css_file, 'w', encoding='utf-8') as f:
        f.write(css_content)


def generate_index_page(reports: List[Dict]):
    """生成首页"""
    total_reports = len(reports)
    stock_reports = len([r for r in reports if not r['is_market_review']])
    market_reports = len([r for r in reports if r['is_market_review']])
    latest_date = reports[0]['date_str'] if reports else '暂无'
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>每日股票分析 - 历史报告</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <header>
        <h1>📈 每日股票分析</h1>
        <p>AI 驱动的智能股票分析系统</p>
    </header>
    
    <div class="container">
        <div class="stats">
            <div class="stat-card">
                <h3>总报告数</h3>
                <div class="value">{total_reports}</div>
            </div>
            <div class="stat-card">
                <h3>个股分析</h3>
                <div class="value">{stock_reports}</div>
            </div>
            <div class="stat-card">
                <h3>大盘复盘</h3>
                <div class="value">{market_reports}</div>
            </div>
            <div class="stat-card">
                <h3>最新更新</h3>
                <div class="value" style="font-size: 1.2rem;">{latest_date}</div>
            </div>
        </div>
        
        <h2 style="margin-top: 40px; margin-bottom: 20px;">📊 历史报告</h2>
        <div class="reports-grid">
"""
    
    for report in reports:
        badge_class = "market" if report['is_market_review'] else "stock"
        badge_text = "大盘复盘" if report['is_market_review'] else "个股分析"
        
        html += f"""
            <div class="report-card" onclick="window.location.href='reports/{report['filename'].replace('.md', '.html')}'">
                <div class="date">📅 {report['date_str']}</div>
                <span class="badge {badge_class}">{badge_text}</span>
                <h3>{report['title']}</h3>
                <div class="summary">{report['summary'][:150]}...</div>
                <a href="reports/{report['filename'].replace('.md', '.html')}" class="read-more">查看详情 →</a>
            </div>
"""
    
    html += """
        </div>
    </div>
    
    <footer>
        <p>🤖 由 AI 自动生成 | 数据仅供参考，不构成投资建议</p>
        <p style="margin-top: 10px;">
            <a href="https://github.com/greatluca666/daily_stock_analysis" target="_blank" style="color: #2563eb;">GitHub 仓库</a>
        </p>
    </footer>
</body>
</html>
"""
    
    index_file = DOCS_DIR / "index.html"
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(html)


def generate_report_pages(reports: List[Dict]):
    """生成每个报告的详情页"""
    for report in reports:
        html_content = convert_md_to_html(report['content'])
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report['title']}</title>
    <link rel="stylesheet" href="../css/style.css">
</head>
<body>
    <header>
        <h1>📈 每日股票分析</h1>
        <p>{report['date_str']}</p>
    </header>
    
    <div class="container">
        <a href="../index.html" class="back-link">← 返回首页</a>
        
        <div class="report-content">
            <h1>{report['title']}</h1>
            {html_content}
        </div>
        
        <a href="../index.html" class="back-link">← 返回首页</a>
    </div>
    
    <footer>
        <p>🤖 由 AI 自动生成 | 数据仅供参考，不构成投资建议</p>
    </footer>
</body>
</html>
"""
        
        report_file = DOCS_DIR / "reports" / report['filename'].replace('.md', '.html')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(html)


def main():
    print("🚀 开始生成 GitHub Pages 网站...")
    
    # 确保目录存在
    ensure_dirs()
    
    # 获取所有报告
    reports = get_all_reports()
    print(f"📊 找到 {len(reports)} 个报告")
    
    # 生成 CSS
    print("🎨 生成样式文件...")
    generate_css()
    
    # 生成首页
    print("📄 生成首页...")
    generate_index_page(reports)
    
    # 生成报告详情页
    print("📝 生成报告详情页...")
    generate_report_pages(reports)
    
    print("✅ 网站生成完成！")
    print(f"📁 输出目录: {DOCS_DIR.absolute()}")


if __name__ == "__main__":
    main()
