---
title: How Capital Becomes Infrastructure
---

<div class="home-hero">
  <div class="home-hero-label">TZD Labs · Systems Research</div>
  <h1 class="home-hero-title">How capital becomes<br>infrastructure.</h1>
  <p class="home-hero-sub">Capital moves fast. Infrastructure doesn't. This project traces the gap: what gets built, where it lands, and how decisions made in one room become obligations for everyone else.</p>
</div>

<hr>

```js
const dives = await FileAttachment("data/deep_dives.json").json();

function arcBadge(steps) {
  return steps.flatMap((s, i) => {
    const cls = s === "Land" ? "arc-step arc-land" : "arc-step";
    const node = html`<span class="${cls}">${s}</span>`;
    return i < steps.length - 1
      ? [node, html`<span class="arc-arrow">→</span>`]
      : [node];
  });
}

function makeCard(d) {
  const isActive = d.status === "Active";
  const cls = `article-card ${isActive ? "article-active" : "article-scoping"}`;
  const statusCls = d.url ? "article-status" : "article-status article-status-scoping";
  const statusText = d.url ? d.status : "Coming Soon";
  const inner = html`<div>
    <div class="article-meta">
      <span class="article-id">${d.id}</span>
      <span class="${statusCls}">${statusText}</span>
    </div>
    <div class="article-title">${d.focus}</div>
    <div class="article-subtitle">${d.topic}</div>
    <p class="article-desc">${d.question}</p>
    <div class="article-arc">${arcBadge(d.arc)}</div>
  </div>`;
  return d.url
    ? html`<a class="${cls}" href=".${d.url}">${inner}</a>`
    : html`<div class="${cls}">${inner}</div>`;
}

display(html`<div class="article-grid">${dives.map(makeCard)}</div>`);
```

<hr>

<div class="home-arc">
  <div class="home-arc-label">Analytical Arc</div>
  <div class="home-arc-chain">
    <div class="home-arc-step">
      <div class="arc-node">Commit</div>
      <div class="arc-desc">Financial commitment — hyperscaler capex, project finance, PPAs, policy subsidy</div>
    </div>
    <div class="arc-connector">→</div>
    <div class="home-arc-step">
      <div class="arc-node">Convert</div>
      <div class="arc-desc">What physical asset? Durability class: structural, policy-dependent, or demand-thesis-dependent?</div>
    </div>
    <div class="arc-connector">→</div>
    <div class="home-arc-step">
      <div class="arc-node">Land</div>
      <div class="arc-desc">Where — geography, grid node, utility territory, labor market</div>
    </div>
    <div class="arc-connector">→</div>
    <div class="home-arc-step">
      <div class="arc-node">Distribute</div>
      <div class="arc-desc">Who benefits? Who bears long-term cost if the demand thesis misses?</div>
    </div>
  </div>
</div>
