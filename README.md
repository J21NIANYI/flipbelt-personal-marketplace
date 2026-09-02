# FlipBelt Personal Plugin Marketplace

面向 ChatGPT/Codex 桌面客户端个人空间的独立插件市场。它只安装 **FlipBelt Product Intelligence（个人）** 专家能力；FlipBelt Knowledge MCP 由每位用户在客户端中单独添加并独立完成 OAuth。

## 安装

1. 打开 ChatGPT 桌面客户端，进入个人空间的 **Codex → 插件**。
2. 点击 **添加插件市场**。
3. 按下面内容填写：

   - 来源：`https://github.com/J21NIANYI/flipbelt-personal-marketplace.git`
   - Git 引用：`main`
   - 稀疏路径：留空

4. 添加后打开 **FlipBelt Personal**。
5. 安装 **FlipBelt Product Intelligence（个人）**。
6. 打开 **设置 → MCP 服务器 → 添加服务器**，选择 **Streamable HTTP**，名称填 `flipbelt-kb`，URL 填 `https://wiki.flipbeltchina.com/mcp`，然后保存。
7. 重启 Codex，在 MCP 服务器列表中找到 `flipbelt-kb`，点击“进行身份验证”；由本人完成钉钉登录，组织选择“飞途行远”。
8. 授权完成后完全新建一个 Codex 任务，再测试知识检索、页面读取和素材读取。

图形界面是首选路径，不需要安装 Codex CLI。插件只提供专家能力，不会自动创建或替换 MCP；同名且 URL 正确的 `flipbelt-kb` 已存在时，不要重复添加，只需重新认证。

只有图形界面没有认证入口时才使用 CLI 兜底：

```bash
codex mcp login flipbelt-kb --oauth-client-registration cimd
```

不要附加自定义 `--scopes`，也不要分享浏览器授权地址、`state`、`code`、Token、Cookie 或密钥。

## Grok Build 安装

> 本节适用于 Grok Build 客户端或 CLI，不适用于 grok.com 网页端 Connector。

1. 安装并登录 Grok Build。
2. 在终端执行：

   ```bash
   grok plugin marketplace add J21NIANYI/flipbelt-personal-marketplace
   grok plugin install flipbelt-product-intelligence-personal --trust
   ```

3. 按 Grok Build 当前界面或文档单独添加 Streamable HTTP MCP：名称 `flipbelt-kb`，URL `https://wiki.flipbeltchina.com/mcp`。
4. 启动 Grok Build，输入 `/mcps` 打开 MCP 面板，找到 `flipbelt-kb` 并按提示完成身份验证；钉钉组织选择“飞途行远”。
5. 授权完成后新建会话，依次验证知识检索、页面读取和素材读取。

如果插件或 MCP 没有出现，先执行：

```bash
grok plugin marketplace update
grok inspect
grok mcp doctor flipbelt-kb
```

Grok Build 与 Codex 共用同一个专家插件目录和根 MCP 地址，但 MCP 都由用户分别添加；两端保存独立的安装状态与 OAuth 凭据，不共享登录令牌。

## 与团队仓的区别

- 团队 Workspace 继续使用 `J21NIANYI/flipbelt-plugin-marketplace`，本仓不会替换或更新它。
- 本仓不引用团队 Workspace App，也不内置 `.mcp.json`；用户在客户端图形界面单独添加唯一正式地址 `https://wiki.flipbeltchina.com/mcp`。
- 每位用户保存自己的 OAuth 凭据；插件不会共享账号、令牌或权限。
- Codex 与 Grok Build 使用并列的市场清单，二者始终指向同一个个人插件目录，不复制第二套专家能力。

## 安全边界

- 仓库不包含产品知识正文、员工数据、Token、密钥、部署脚本或生产配置。
- 插件只允许使用 FlipBelt Knowledge 的三个只读工具。
- GitHub 仓库公开只代表安装清单可读取，不授予知识访问权限；MCP 仍按钉钉员工目录和 ACL 失败关闭。

## 来源基线

Product Intelligence 的 `shared/` 与 `skills/` 从本地唯一真源 `flipbelt-product-intelligence@5eaf3f988d491e378cfe97ba5bad1a69ce80e09b` 单向同步，源版本为 `0.2.1`。本仓只改变个人插件名、分发 SemVer、Skills-only Marketplace 清单、公开说明和验证适配，不从团队公开仓复制专家行为；完整来源与同步树摘要见 `SOURCE-PROVENANCE.json`。
