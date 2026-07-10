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
3. 首次打开时确认信任此仓库并允许社区插件。
4. Homepage 插件会自动打开 `Home.md`。

所有必需社区插件和 Minimal 主题都已经包含在仓库中，无需额外安装。

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

## 内置依赖

仓库包含以下插件的完整安装包和必要设置：

- Dataview
- Homepage
- Heatmap Calendar
- Minimal Theme Settings
- Style Settings

仓库同时包含 Minimal 主题本体。`tools/install-obsidian-plugins.py` 保留为插件损坏时的修复工具，或需要主动刷新插件版本时使用。

## License

MIT
