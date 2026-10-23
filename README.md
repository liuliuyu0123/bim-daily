# BIM 日知：每日采集部署版

## 当前功能
- 国内/国际新闻 RSS、arXiv BIM 科研预印本采集。
- 每日北京时间约 09:15 运行；支持 Actions 手动运行。
- 去重、最多保留 250 条记录；每天保存 JSON 历史快照。
- 来源失败时保留历史内容并显示真实状态；全来源失败时工作流标记失败。
- 页面搜索、分类和浏览器本地收藏。

## 部署（必须完成，上传包本身不等于已启用）
1. 解压 ZIP，将 index.html、data、scripts、.github 文件夹按原目录上传到 main。注意 .github/workflows/daily.yml 必须存在；不要只上传 index.html。
2. 仓库 Settings → Pages → Source 改为 GitHub Actions。
3. 仓库 Actions → Daily BIM update and deploy → Run workflow。
4. 检查工作流绿色完成及数据中的 sources 状态，再打开 https://liuliuyu0123.github.io/bim-daily/。
5. 工作流提交 data 文件和快照并直接部署 Pages。无需 API 密钥或付费摘要服务。

## 数据说明与限制
自动内容保留来源的原文标题；论文附原文摘要并标记预印本。当前没有自动中文翻译或 AI 摘要功能。此前人工整理的中文简介作为历史记录保留，不会伪装成今日新闻。更新时间与来源状态在页面显示。历史快照见仓库 data/archive。
GitHub 调度可能延迟；公开仓库长期无活动时定时任务可能停用，应定期检查 Actions。数据源可能限流或不可达；失败时不会清空历史。
初始 news.json 为历史种子数据。请以首次成功工作流的日志判断采集是否可用。
