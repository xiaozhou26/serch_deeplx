# serch_deeplx

# 寻找合适可用的deeplx

本仓库包含一个使用 asyncio 和 aiohttp 发送异步 HTTP POST 请求并将成功的 URLs 保存到文件中的 Python 脚本。

## 如何使用

1. **Fork 仓库**：点击此页面右上角的 "Fork" 按钮，在你的 GitHub 账户中创建此仓库的副本。

2. **设置 Secrets**：导航到 fork 的仓库的 "Settings" 标签，然后点击 "Secrets"。添加以下 secrets：

- `GIT_USER_EMAIL`：你的 GitHub 邮箱
- `GIT_USER_NAME`：你的 GitHub 用户名
- `GH_PAT`：你的 GitHub 个人访问令牌（PAT）。你可以在 GitHub 账户设置中生成 PAT。

3. **运行 Workflow**：Workflow 设置为每天在 00:00 自动运行。你也可以通过导航到 fork 的仓库的 "Actions" 标签，选择 workflow，然后点击 "Run workflow" 手动触发 workflow。

4. **查看结果**：Workflow 运行后，成功的 URLs 将保存在名为 `success_result.txt` 的文件中。
