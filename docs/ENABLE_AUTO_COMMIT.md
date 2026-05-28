# 如何启用报告自动提交

## 问题说明

当前 GitHub Actions 生成的报告只保存在临时 Artifacts 中，没有提交到仓库，导致 GitHub Pages 无法读取历史报告。

## 解决方案

需要在 `.github/workflows/00-daily-analysis.yml` 文件中添加一个步骤，在分析完成后自动提交报告到仓库。

## 手动添加步骤

### 方法 1：通过 GitHub 网页编辑

1. 访问：https://github.com/greatluca666/daily_stock_analysis/edit/main/.github/workflows/00-daily-analysis.yml

2. 找到文件末尾的 `- name: 显示运行结果` 步骤（大约在第 600 行左右）

3. 在该步骤**之后**添加以下内容：

```yaml
      
      - name: 提交报告到仓库
        if: success()
        run: |
          git config --local user.email "github-actions[bot]@users.noreply.github.com"
          git config --local user.name "github-actions[bot]"
          
          # 添加报告文件
          git add reports/*.md 2>/dev/null || true
          
          # 检查是否有新文件需要提交
          if git diff --staged --quiet; then
            echo "📝 没有新的报告文件需要提交"
          else
            REPORT_DATE=$(date +'%Y-%m-%d')
            git commit -m "chore: 自动提交每日股票分析报告 ${REPORT_DATE}"
            git push
            echo "✅ 报告已提交到仓库"
            echo "📊 报告文件："
            git diff HEAD~1 --name-only | grep "reports/" || true
          fi
```

4. 点击 `Commit changes`

### 方法 2：使用 Claude Code（推荐）

如果你在本地有这个仓库的克隆，可以让我直接帮你编辑文件。

## 验证

添加步骤后，下次运行每日分析时：

1. 分析完成后会自动提交报告到 `reports/` 目录
2. 提交后会自动触发 GitHub Pages 发布
3. 你的网站会显示最新的报告

## 测试

手动触发一次分析来测试：

1. 访问：https://github.com/greatluca666/daily_stock_analysis/actions/workflows/00-daily-analysis.yml
2. 点击 `Run workflow`
3. 选择 `force_run: true`（跳过交易日检查）
4. 点击 `Run workflow`
5. 等待完成后，检查 `reports/` 目录是否有新文件

## 注意事项

- ✅ 已修改 `.gitignore`，允许提交 `reports/` 目录
- ✅ 已创建 `reports/.gitkeep` 确保目录存在
- ⚠️ 需要手动添加上述工作流步骤（文件太大无法自动更新）

## 需要帮助？

如果你在本地有仓库克隆，告诉我，我可以直接帮你编辑文件！
