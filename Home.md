---
cssclasses:
  - dashboard
  - command-center
  - neo-dashboard
tags:
  - 导航
type: dashboard
status: active
created: 2026-07-06
updated: 2026-07-10
---

# Obsidian 工作台

> 先处理最新输入，再把真正值得留下的内容推进到长期知识库。

## 系统概览

```dataviewjs
const pages = dv.pages()
  .where(p => p.file.path !== dv.current().file.path)
  .where(p => !p.file.path.includes("模板/"))
  .where(p => !p.file.path.includes(".trash/"));

const byStatus = status => pages.where(p => p.status === status).length;
const taggedInbox = pages.where(p => (p.file.tags || []).includes("#inbox")).length;
const inbox = byStatus("inbox") + taggedInbox;
const seed = byStatus("seed");
const growing = byStatus("growing");
const evergreen = pages.where(p => p.status === "evergreen" || p.type === "evergreen").length;
const archive = byStatus("archive");
const parsePageDate = value => {
  if (!value) return null;
  if (value.toJSDate) return value.toJSDate();
  if (value instanceof Date) return value;
  const normalized = String(value).replaceAll("/", "-");
  const parsed = new Date(normalized);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
};
const pageActivityDate = page => parsePageDate(page.updated ?? page.created ?? page.date);
const weekAgo = Date.now() - 7 * 24 * 60 * 60 * 1000;
const recent = pages.where(p => {
  const activityDate = pageActivityDate(p);
  return activityDate && activityDate.getTime() >= weekAgo;
}).length;
const openTasks = dv.pages().file.tasks.where(t => !t.completed).length;
const active = inbox + seed + growing + evergreen;
const health = active === 0 ? 0 : Math.round((evergreen / active) * 100);
const today = new Date().toLocaleDateString("zh-CN", { month: "long", day: "numeric", weekday: "long" });
const systemState = health >= 45 ? "高复用" : health >= 20 ? "生长期" : "输入期";

const shell = dv.el("div", "", { cls: "cc-dashboard-shell" });
shell.innerHTML = `
  <section class="cc-hero">
    <div class="cc-hero-main">
      <div class="cc-kicker">KNOWLEDGE OS / ${today}</div>
      <div class="cc-hero-title">今日重点：处理新输入</div>
      <div class="cc-hero-subtitle">当前系统处于「${systemState}」状态。优先查看定时任务生成的最新文档，再处理其中的待读、深读和入库动作。</div>
      <div class="cc-hero-readout">
        <span>${pages.length}<small>笔记</small></span>
        <span>${recent}<small>本周入库</small></span>
        <span>${openTasks}<small>待办</small></span>
      </div>
    </div>
    <div class="cc-orbit-panel">
      <div class="cc-orbit-score">${health}%</div>
      <div class="cc-orbit-label">知识健康度</div>
      <div class="cc-meter cc-meter-hero"><span style="width:${Math.max(4, health)}%"></span></div>
    </div>
  </section>

  <section class="cc-pipeline">
    ${[
      ["inbox", inbox, "捕获"],
      ["seed", seed, "筛选"],
      ["growing", growing, "生长"],
      ["evergreen", evergreen, "复用"],
      ["archive", archive, "归档"]
    ].map(([label, value, hint]) => `
      <div class="cc-stage">
        <div class="cc-stage-label">${label}</div>
        <div class="cc-stage-value">${value}</div>
        <div class="cc-stage-hint">${hint}</div>
      </div>
    `).join("")}
  </section>

  <section class="cc-heatmap-card">
    <div class="cc-heatmap-head">
      <div>
        <div class="cc-section-kicker">ACTIVITY HEATMAP</div>
        <div class="cc-section-title">知识库活跃热力图</div>
      </div>
      <div class="cc-heatmap-legend">
        <span>少</span>
        <i></i><i></i><i></i><i></i><i></i>
        <span>多</span>
      </div>
    </div>
    <div class="cc-heatmap-mount"></div>
  </section>

  <section class="cc-stat-grid">
    ${[
      ["全库笔记", pages.length, "所有可检索笔记"],
      ["本周入库", recent, "基于元数据日期"],
      ["Inbox", inbox, "待判断输入"],
      ["Seed", seed, "等待发芽"],
      ["Growing", growing, "正在生长"],
      ["Evergreen", evergreen, "可复用观点"],
      ["待办", openTasks, "未完成任务"],
      ["健康度", `${health}%`, "常青占比"]
    ].map(([label, value, hint]) => `
      <div class="cc-stat-card">
        <div class="cc-stat-label">${label}</div>
        <div class="cc-stat-value">${value}</div>
        <div class="cc-stat-hint">${hint}</div>
      </div>
    `).join("")}
  </section>
`;

const currentYear = new Date().getFullYear();
const toLocalDateKey = date => {
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60 * 1000);
  return local.toISOString().slice(0, 10);
};
const dailyCounts = new Map();
for (const page of pages) {
  const activityDate = pageActivityDate(page);
  if (!activityDate || activityDate.getFullYear() !== currentYear) continue;
  const day = toLocalDateKey(activityDate);
  dailyCounts.set(day, (dailyCounts.get(day) || 0) + 1);
}

const heatmapEntries = Array.from(dailyCounts.entries()).map(([date, count]) => ({
  date,
  intensity: count,
  color: "knowledge",
  content: `${date}: ${count} 条记录`
}));

const heatmapMount = shell.querySelector(".cc-heatmap-mount");
const heatmapColors = {
  knowledge: ["#dbeafe", "#a7f3d0", "#34d399", "#0ea5e9", "#2563eb"]
};

if (heatmapMount && typeof window.renderHeatmapCalendar === "function") {
  window.renderHeatmapCalendar(heatmapMount, {
    year: currentYear,
    colors: heatmapColors,
    entries: heatmapEntries,
    intensityScaleStart: 1,
    intensityScaleEnd: Math.max(5, ...Array.from(dailyCounts.values(), value => value || 0)),
    showCurrentDayBorder: true
  });
} else if (heatmapMount) {
  const days = 112;
  const todayStart = new Date();
  todayStart.setHours(0, 0, 0, 0);
  const cells = [];
  for (let offset = days - 1; offset >= 0; offset--) {
    const day = new Date(todayStart);
    day.setDate(todayStart.getDate() - offset);
    const date = toLocalDateKey(day);
    const count = dailyCounts.get(date) || 0;
    const level = count === 0 ? 0 : Math.min(5, Math.ceil((count / Math.max(1, ...dailyCounts.values())) * 5));
    cells.push(`<span class="cc-heatmap-cell level-${level}" title="${date}: ${count} 次更新"></span>`);
  }
  heatmapMount.innerHTML = `<div class="cc-heatmap-fallback">${cells.join("")}</div>`;
}
```

## 常用入口

- [[Inbox/快速捕获|快速捕获]]
- [[Reading Candidates/示例输入|阅读候选]]
- [[Knowledge/Seed/Seed 指南|Seed 队列]]
- [[Knowledge/Growing/Growing 指南|Growing 队列]]
- [[Knowledge/Evergreen/Evergreen 指南|Evergreen 知识]]
- [[模板/知识笔记|知识笔记模板]]
- [[工作台使用指南|工作台使用指南]]

## 今日输入

```dataviewjs
const escapeHtml = value => String(value ?? "")
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;");

const formatDate = value => value?.toFormat ? value.toFormat("yyyy-MM-dd") : String(value ?? "");

const internalLink = (path, label) => {
  const clean = path.replace(/\.md$/, "");
  return `<a class="internal-link" data-href="${escapeHtml(clean)}" href="${escapeHtml(clean)}">${escapeHtml(label)}</a>`;
};

const generatedDateKey = page => formatDate(page.date ?? page.file.name);

const generatedDocs = dv.pages()
  .where(p => p.file.path.includes("Reading Candidates/"))
  .sort(generatedDateKey, "desc")
  .array();

const latestDoc = generatedDocs[0];
const previousDoc = generatedDocs[1];
const latestDocTasks = latestDoc
  ? Array.from(latestDoc.file.tasks ?? [])
  : [];
const openCandidates = latestDocTasks.filter(t => !t.completed);

const taskStats = page => {
  const tasks = page ? Array.from(page.file.tasks ?? []) : [];
  return {
    open: tasks.filter(t => !t.completed).length,
    done: tasks.filter(t => t.completed).length
  };
};

const markdownLink = value => {
  const match = String(value ?? "").match(/\[([^\]]+)\]\((https?:\/\/[^)]+)\)/);
  return match ? { label: match[1], url: match[2] } : null;
};

const externalLink = (url, label) => url
  ? `<a class="external-link" href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer">${escapeHtml(label)}</a>`
  : `<span>${escapeHtml(label)}</span>`;

const parseCandidates = sourceText => {
  const candidates = [];
  let current = null;

  for (const [lineIndex, line] of String(sourceText ?? "").split("\n").entries()) {
    const taskMatch = line.match(/^- \[([ xX])\] (.+)$/);
    if (taskMatch) {
      current = {
        title: taskMatch[2].trim(),
        lineIndex,
        completed: taskMatch[1].toLowerCase() === "x",
        original: null,
        source: null
      };
      candidates.push(current);
      continue;
    }

    if (!current) continue;

    const originalMatch = line.match(/^\s+- 原文链接：(.+)$/);
    if (originalMatch) current.original = markdownLink(originalMatch[1]);

    const sourceMatch = line.match(/^\s+- BestBlogs 来源页：(.+)$/);
    if (sourceMatch) current.source = markdownLink(sourceMatch[1]);
  }

  return candidates.map(candidate => {
    const link = candidate.original?.url ? candidate.original : candidate.source;
    return {
      title: candidate.title,
      lineIndex: candidate.lineIndex,
      completed: candidate.completed,
      url: link?.url ?? ""
    };
  });
};

const input = dv.el("div", "", { cls: "cc-input-host" });

const renderInput = async () => {
  const sourceText = latestDoc ? await dv.io.load(latestDoc.file.path) : "";
  const parsedCandidates = parseCandidates(sourceText);
  const linkedCandidates = parsedCandidates.length
    ? parsedCandidates
    : openCandidates.map(task => ({ title: task.text, url: "", lineIndex: -1, completed: false }));
  const visibleCandidates = linkedCandidates.filter(candidate => !candidate.completed);
  const completedCandidates = linkedCandidates.filter(candidate => candidate.completed);
  const previousStats = taskStats(previousDoc);

  const candidateRows = visibleCandidates.map((candidate, index) => `
    <li class="cc-candidate-row">
      <button class="cc-candidate-done" type="button" data-line="${candidate.lineIndex}" aria-label="标记完成">${index + 1}</button>
      <div>${externalLink(candidate.url, candidate.title)}</div>
    </li>
  `).join("");

  input.innerHTML = latestDoc ? `
    <section class="cc-input-card">
      <article class="cc-input-source">
        <div class="cc-section-kicker">LATEST INPUT</div>
        <div class="cc-section-title">今日输入来源</div>
        <div class="cc-input-title">${internalLink(latestDoc.file.path, latestDoc.title ?? latestDoc.file.name)}</div>
        <div class="cc-input-meta">
          <span>${formatDate(latestDoc.date ?? latestDoc.file.name)}</span>
          <span>${escapeHtml(latestDoc.status ?? "inbox")}</span>
          <span>${visibleCandidates.length} 项待处理</span>
        </div>
        <div class="cc-input-copy">候选标题可直接打开对应网页；需要批量勾选、补充或入库时，再打开来源清单统一处理。</div>
        <div class="cc-input-actions">${internalLink(latestDoc.file.path, "打开候选清单")}</div>
        ${previousDoc ? `
          <div class="cc-previous-input">
            <div class="cc-previous-label">上一期阅读候选</div>
            <div class="cc-previous-title">${internalLink(previousDoc.file.path, previousDoc.title ?? previousDoc.file.name)}</div>
            <div class="cc-previous-meta">
              <span>${formatDate(previousDoc.date ?? previousDoc.file.name)}</span>
              <span>${previousStats.open} 待处理</span>
              <span>${previousStats.done} 已完成</span>
            </div>
          </div>
        ` : ""}
      </article>
      <article class="cc-input-preview">
        <div class="cc-section-kicker">CANDIDATE PREVIEW</div>
        <div class="cc-section-title">待判断候选</div>
        <ul class="cc-candidate-list">
          ${candidateRows || `<li class="cc-empty-row">最新输入里暂无未完成候选</li>`}
        </ul>
        <div class="cc-input-meter">
          <span><b>${visibleCandidates.length}</b><small>待处理</small></span>
          <span><b>${completedCandidates.length}</b><small>已完成</small></span>
        </div>
      </article>
    </section>
  ` : `<section class="cc-input-card"><div class="cc-empty-row">暂无定时任务生成文档</div></section>`;

  input.querySelectorAll(".cc-candidate-done").forEach(button => {
    button.addEventListener("click", async event => {
      event.preventDefault();
      event.stopPropagation();

      const lineIndex = Number(button.dataset.line);
      if (!latestDoc || Number.isNaN(lineIndex) || lineIndex < 0) return;

      const file = app.vault.getAbstractFileByPath(latestDoc.file.path);
      if (!file) return;

      const currentText = await app.vault.read(file);
      const lines = currentText.split("\n");
      if (!lines[lineIndex]) return;
      if (!/^- \[ \] /.test(lines[lineIndex])) return;

      lines[lineIndex] = lines[lineIndex].replace(/^- \[ \] /, "- [x] ");
      await app.vault.modify(file, lines.join("\n"));
      await renderInput();
    });
  });
};

renderInput();
```

## 进化队列

```dataviewjs
const escapeHtml = value => String(value ?? "")
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;");

const internalLink = (path, label) => {
  const clean = path.replace(/\.md$/, "");
  return `<a class="internal-link" data-href="${escapeHtml(clean)}" href="${escapeHtml(clean)}">${escapeHtml(label)}</a>`;
};

const parsePageDate = value => {
  if (!value) return null;
  if (value.toJSDate) return value.toJSDate();
  if (value instanceof Date) return value;
  const normalized = String(value).replaceAll("/", "-");
  const parsed = new Date(normalized);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
};

const pageActivityTime = page => {
  const activityDate = parsePageDate(page.updated ?? page.created ?? page.date);
  return activityDate ? activityDate.getTime() : 0;
};

const allPages = dv.pages()
  .where(p => p.file.path !== dv.current().file.path)
  .where(p => !p.file.path.includes("模板/"))
  .where(p => !p.file.path.includes(".trash/"));

const toRows = query => query
  .array()
  .sort((a, b) => pageActivityTime(b) - pageActivityTime(a));

const stages = [
  {
    label: "Inbox",
    hint: "先判断去留",
    action: "清空噪音",
    rows: toRows(allPages.where(p => p.status === "inbox" || (p.file.tags || []).includes("#inbox")))
  },
  {
    label: "Seed",
    hint: "等待筛选",
    action: "决定是否发芽",
    rows: toRows(allPages.where(p => p.status === "seed"))
  },
  {
    label: "Growing",
    hint: "正在沉淀",
    action: "补链接和证据",
    rows: toRows(allPages.where(p => p.status === "growing"))
  },
  {
    label: "Evergreen",
    hint: "可复用观点",
    action: "定期复查",
    rows: toRows(allPages.where(p => p.status === "evergreen" || p.type === "evergreen"))
  }
];

const stageCards = stages.map(stage => {
  const rows = stage.rows.slice(0, 3).map(page => `
    <li>
      ${internalLink(page.file.path, page.title ?? page.file.name)}
      <span>${page.file.folder || "根目录"}</span>
    </li>
  `).join("");

  return `
    <article class="cc-evolution-card">
      <div class="cc-evolution-head">
        <div>
          <div class="cc-section-kicker">${stage.label.toUpperCase()}</div>
          <div class="cc-section-title">${stage.hint}</div>
        </div>
        <b>${stage.rows.length}</b>
      </div>
      <ul class="cc-evolution-list">${rows || `<li class="cc-evolution-empty">暂无条目</li>`}</ul>
      <div class="cc-evolution-action">${escapeHtml(stage.action)}</div>
    </article>
  `;
}).join("");

const evolution = dv.el("div", "", { cls: "cc-evolution-host" });
evolution.innerHTML = `<section class="cc-evolution-grid">${stageCards}</section>`;
```
