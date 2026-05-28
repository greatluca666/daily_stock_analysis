# GitHub Pages 自动发布指南

本指南将帮助你将每日股票分析报告自动发布到 GitHub Pages，创建一个可以随时访问的在线报告网站。

## 📋 功能特性

- ✅ 每日自动生成并发布股票分析报告
- ✅ 美观的网页界面展示历史报告
- ✅ 支持个股分析和大盘复盘分类
- ✅ 响应式设计，支持手机和电脑访问
- ✅ 自动统计报告数量和更新时间
- ✅ 零成本托管在 GitHub Pages

## 🚀 快速开始

### 步骤 1：启用 GitHub Pages

1. 进入你的仓库：https://github.com/greatluca666/daily_stock_analysis
2. 点击 `Settings`（设置）
3. 在左侧菜单找到 `Pages`
4. 在 **Source** 下拉菜单中选择 `GitHub Actions`
5. 点击 `Save`（保存）

### 步骤 2：手动触发首次发布

由于工作流需要在分析完成后自动触发，你可以先手动运行一次：

1. 进入 `Actions` 标签页
2. 选择 `发布到 GitHub Pages` 工作流
3. 点击 `Run workflow` → `Run workflow`

### 步骤 3：访问你的网站

发布完成后，你的网站将在以下地址可用：

```
https://greatluca666.github.io/daily_stock_analysis/
```

## 📊 工作原理

### 自动化流程

```
每日分析运行 → 生成报告 → 保存到 reports/ → 触发 Pages 发布 → 更新网站
```

1. **每日分析**：`00-daily-analysis.yml` 工作流每天运行，生成股票分析报告
2. **自动触发**：分析完成后，自动触发 `publish-to-pages.yml` 工作流
3. **生成网站**：`scripts/generate_pages.py` 脚本将 Markdown 报告转换为 HTML 网页
4. **发布上线**：自动部署到 GitHub Pages

### 文件结构

```
daily_stock_analysis/
├── .github/workflows/
│   ├── 00-daily-analysis.yml      # 每日分析工作流
│   └── publish-to-pages.yml       # GitHub Pages 发布工作流
├── scripts/
│   └── generate_pages.py          # 网站生成脚本
├── reports/                        # 分析报告存储目录
│   ├── report_20260528.md
│   └── market_review_20260528.md
└── docs/                           # 生成的网站文件（自动生成）
    ├── index.html
    ├── css/
    │   └── style.css
    └── reports/
        └── *.html
```

## 🎨 网站功能

### 首页

- 📊 统计卡片：显示总报告数、个股分析数、大盘复盘数、最新更新时间
- 📋 报告列表：以卡片形式展示所有历史报告
- 🏷️ 分类标签：区分个股分析和大盘复盘
- 📅 日期排序：最新报告显示在最前面

### 报告详情页

- 📄 完整的 Markdown 渲染
- 🎯 清晰的标题和段落
- 📊 代码块和列表支持
- ⬅️ 返回首页链接

## 🔧 自定义配置

### 修改网站样式

编辑 `scripts/generate_pages.py` 中的 `generate_css()` 函数来自定义样式：

```python
def generate_css():
    css_content = """
    :root {
        --primary-color: #2563eb;  # 主题色
        --success-color: #10b981;  # 成功色
        ...
    }
    """
```

### 修改网站标题

在 `generate_index_page()` 函数中修改：

```python
<h1>📈 每日股票分析</h1>
<p>AI 驱动的智能股票分析系统</p>
```

## 🐛 故障排查

### 问题 1：网站无法访问

**解决方案**：
1. 检查 GitHub Pages 是否已启用（Settings → Pages）
2. 确认 Source 设置为 `GitHub Actions`
3. 查看 Actions 运行日志，确认发布工作流成功执行

### 问题 2：报告没有更新

**解决方案**：
1. 检查每日分析工作流是否成功运行
2. 确认 `reports/` 目录中有新的报告文件
3. 手动触发 `发布到 GitHub Pages` 工作流

### 问题 3：样式显示异常

**解决方案**：
1. 清除浏览器缓存
2. 检查 `docs/css/style.css` 文件是否正确生成
3. 查看浏览器控制台是否有 CSS 加载错误

## 📝 注意事项

1. **报告保留**：GitHub Pages 会保留所有历史报告，建议定期清理旧报告以节省空间
2. **访问权限**：如果仓库是私有的，GitHub Pages 也将是私有的（需要 GitHub Pro）
3. **更新延迟**：从报告生成到网站更新通常需要 1-2 分钟
4. **文件大小**：单个报告文件建议不超过 1MB，以确保快速加载

## 🎯 下一步

- [ ] 添加搜索功能
- [ ] 支持按日期筛选报告
- [ ] 添加报告对比功能
- [ ] 集成图表可视化
- [ ] 添加 RSS 订阅

## 📞 需要帮助？

如果遇到问题，可以：
1. 查看 [GitHub Actions 运行日志](https://github.com/greatluca666/daily_stock_analysis/actions)
2. 提交 [Issue](https://github.com/greatluca666/daily_stock_analysis/issues)
3. 查看原项目文档

---

**免责声明**：本网站展示的股票分析报告仅供参考，不构成投资建议。投资有风险，入市需谨慎。
