---
name: ir-analysis
description: Investor-focused corporate analysis from IR materials. Extracts insights from annual reports, earnings calls, disclosures, and ESG data using Gemini (PDF/text) and Codex (financial modeling).
allowed-tools: "Bash(python *) Bash(uv *) Bash(codex *) Bash(gemini *) Read Write Edit Glob Grep"
---

# IR Analysis — Investor-Focused Corporate Analysis

Analyze corporate disclosures and IR materials from an investor's perspective.

## Workflow

### Step 1: Target and Scope
Ask the user:
1. Target company (ticker / name)
2. Analysis depth (quick overview, standard, deep dive)
3. Focus area (overall, financial health, growth, risk, governance, or custom)
4. Available materials (URLs, PDFs, or fetch automatically)

### Step 2: Gather IR Materials
Using data-engineer subagent, collect:
- **Financial filings**: Annual report (10-K / 有価証券報告書), quarterly (10-Q / 四半期報告書)
- **Earnings materials**: Earnings release, presentation slides, supplemental data
- **Earnings call transcript**: Management commentary and Q&A
- **Timely disclosures**: TDnet (Japan) / EDGAR (US) / exchange filings
- **Guidance**: Management forecasts, mid-term plans, capital allocation policy
- **ESG/Governance**: ESG report, corporate governance report, proxy statement

### Step 3: Financial Statement Analysis via Codex
Delegate quantitative analysis to Codex:
```bash
codex --approval-mode suggest "Analyze these financial statements as an equity investor:

Company: {company}
Data: {financial_data}

Perform:
1. Profitability trend (revenue, operating margin, net margin — 3-5 year)
2. Balance sheet health (debt/equity, interest coverage, current ratio)
3. Cash flow quality (FCF yield, operating CF vs net income, capex intensity)
4. Return metrics (ROE decomposition via DuPont, ROIC vs WACC)
5. Per-share metrics (EPS growth, BPS growth, DPS growth, payout ratio)
6. Peer comparison (vs sector median for key metrics)

Flag: accounting red flags, one-time items distorting trends, off-balance-sheet risks"
```

### Step 4: Qualitative Analysis via Gemini
Send IR documents to Gemini for text/PDF analysis:
```bash
gemini -p "Analyze this corporate document from an investor's perspective:

Extract:
1. BUSINESS MODEL: Revenue drivers, competitive advantages (moat), market position
2. GROWTH STRATEGY: Management's stated growth plan, M&A strategy, R&D investment
3. RISK FACTORS: Key risks disclosed, litigation, regulatory, concentration
4. MANAGEMENT TONE: Confidence level, forward-looking language, hedging language
5. GUIDANCE: Quantitative forecasts, assumptions, track record vs prior guidance
6. CAPITAL ALLOCATION: Dividend policy, buyback history, investment priorities
7. RED FLAGS: Inconsistencies between narrative and numbers, vague language on specific topics

Provide confidence level (High/Medium/Low) for each finding." -f {document}
```

### Step 5: Earnings Call Analysis via Gemini
If transcript is available:
```bash
gemini -p "Analyze this earnings call transcript:

1. KEY THEMES: Top 3 topics management emphasized
2. ANALYST CONCERNS: What did analysts push back on or probe deeply?
3. MANAGEMENT CONFIDENCE: Verbal cues (hedging, certainty, deflection)
4. FORWARD GUIDANCE: Any changes to outlook, new commitments, or withdrawn targets?
5. SURPRISES: Anything unexpected vs prior quarter messaging?
6. SENTIMENT SHIFT: More bullish/bearish/neutral vs previous call?" -f {transcript}
```

### Step 6: ESG & Governance Assessment
Evaluate non-financial factors:
- **Environmental**: Carbon targets, climate risk disclosure, transition plan
- **Social**: Employee metrics (turnover, diversity), supply chain practices
- **Governance**: Board independence, executive compensation alignment, shareholder rights
- **Controversies**: Recent incidents, regulatory actions, reputational issues

### Step 7: Investment Thesis Synthesis
Combine quantitative and qualitative findings into an investment thesis:

```markdown
## Investment Thesis: {Company}

### Bull Case
- {Key growth driver with evidence}
- {Competitive advantage with moat analysis}
- {Valuation argument}

### Bear Case
- {Primary risk with quantification}
- {Competitive threat}
- {Valuation concern}

### Key Metrics
| Metric | Current | 3Y Avg | Sector Median | Assessment |
|--------|---------|--------|---------------|------------|
| ROE | X% | X% | X% | ✅/⚠️/❌ |
| FCF Yield | X% | X% | X% | ✅/⚠️/❌ |
| Debt/Equity | X | X | X | ✅/⚠️/❌ |
| EPS Growth | X% | X% | X% | ✅/⚠️/❌ |

### Catalysts (Positive)
- {Upcoming event that could drive upside}

### Risks to Monitor
- {Specific risk with trigger condition}

### Management Assessment
- Track record: {guidance accuracy over last N quarters}
- Capital allocation: {rating with evidence}
- Alignment: {insider ownership, compensation structure}
```

### Step 8: Output
Save analysis to `reports/ir/`:
- `{company}_{date}_ir_analysis.md` — Full investment thesis
- `{company}_{date}_financials.csv` — Key metrics time series
- `{company}_{date}_peer_comparison.csv` — Peer group comparison

### Step 9: Integration with Trading
Feed results into other skills:
- `/equity-screener` — Use IR insights to refine screening criteria
- `/strategy-design` — Incorporate fundamental signals into quant strategies
- `/earnings-calendar` — Align position sizing with IR-derived conviction level
