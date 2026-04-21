---
name: gemini-system
description: Execute multimodal processing tasks via Gemini CLI. Provides templates for chart analysis, PDF extraction, and financial research.
disable-model-invocation: true
allowed-tools: "Bash(gemini *) Read Write"
---

# Gemini CLI Integration

Delegate multimodal tasks to Gemini CLI (Gemini 2.5 Pro).

## Usage

Invoke with `/gemini-system` followed by the task type.

## Task Templates

### Chart Analysis
```bash
gemini -p "Analyze this price chart:
1. Key support/resistance levels with prices
2. Chart patterns (H&S, triangles, wedges, flags)
3. Trend direction and strength
4. Volume profile analysis
5. Confidence level for each finding (High/Medium/Low)
$ARGUMENTS" -f {chart_file}
```

### PDF Report Extraction
```bash
gemini -p "Extract from this financial report:
1. Key findings and conclusions
2. Numerical data and statistics (in table format)
3. Risk factors mentioned
4. Market outlook and predictions
$ARGUMENTS" -f {pdf_file}
```

### Multi-Chart Comparison
```bash
gemini -p "Compare these charts:
1. Correlation patterns
2. Divergence points
3. Relative strength assessment
4. Leading/lagging relationships
$ARGUMENTS" -f {chart1} -f {chart2}
```

### Financial Research
```bash
gemini -p "Research the following financial topic:
$ARGUMENTS

Provide:
- Key findings with sources
- Data points in table format
- Confidence levels
- Caveats and limitations"
```

## Notes
- Use `-p` flag for non-interactive (headless) mode
- Use `-f` to attach files (images, PDFs)
- Gemini excels at visual/multimodal tasks
- For text-only deep reasoning, prefer Codex instead
- See `.claude/rules/gemini-delegation.md` for routing guidelines
