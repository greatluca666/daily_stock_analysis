#!/bin/bash
# 此脚本用于在每日分析工作流中添加自动提交报告的步骤
# 
# 使用方法：
# 1. 在 .github/workflows/00-daily-analysis.yml 的 "显示运行结果" 步骤之后
# 2. 添加以下步骤：

cat << 'WORKFLOW_STEP'

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
            git diff HEAD~1 --name-only | grep "reports/"
          fi

WORKFLOW_STEP
