# Obsidian Knowledge Workbench

一个可复用、隐私友好的 Obsidian 个人知识管理工作台模板。

它把知识生命周期组织为：

```
Inbox → Seed → Growing → Evergreen → Archive
```

首页包含：

- 知识库概览与知识健康度
- 基于 frontmatter 日期的年度活跃热力图
- 阅读候选预览与快捷完成
- Inbox、Seed、Growing、Evergreen 进化队列
- 可复用的工作台视觉样式

## 快速开始

1. Clone 本仓库。
2. 用 Obsidian 打开仓库根目录。
3. 安装社区插件：

   ```bash
   python3 tools/install-obsidian-plugins.py
   ```

4. 在 Obsidian 设置中安装并启用 **Minimal** 主题。
5. 重启 Obsidian，Homepage 插件会自动打开 `Home.md`。

核心依赖：

- Dataview
- Homepage
- Heatmap Calendar
- Minimal Theme Settings
- Style Settings

## 笔记元数据

工作台优先读取 `updated`、`created`、`date`，避免文件迁移或批量编辑造成的 `file.mtime` 污染。

推荐 frontmatter：

```yaml
---
title: 示例标题
status: growing
created: 2026-07-10
updated: 2026-07-10
---
```

支持的 `status`：

- `inbox`
- `seed`
- `growing`
- `evergreen`
- `archive`

## 隐私说明

这个仓库只包含工作台、样式、必要配置和示例内容，不包含原作者的私人笔记。

`.gitignore` 已默认排除 `Journal/`、`Notes/`、`Private/` 和附件目录。使用自己的目录结构时，请在提交前继续补充忽略规则，并执行：

```bash
git status --short
git ls-files
```

确认没有私人内容后再推送。

## 插件恢复

仓库只保存插件启用列表和必要设置，不保存插件安装包。恢复脚本会根据 Obsidian 官方社区插件索引下载插件。

## License

MIT

