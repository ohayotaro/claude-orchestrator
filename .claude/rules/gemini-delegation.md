# Gemini Delegation Rules

## When to Delegate to Gemini CLI

### Multimodal Input
- Chart image analysis and pattern recognition
- PDF report data extraction
- Screenshot analysis
- Handwritten notes / whiteboard reading

### Visual Analysis
- Technical chart pattern recognition
- Correlation heatmap interpretation
- Performance dashboard evaluation
- Multi-chart cross-comparison

### Research
- Latest market trend information
- Economic indicator impact analysis
- Academic paper financial data extraction
- Regulatory change impact assessment

## Command Templates

### Chart Analysis
```bash
gemini -p "Analyze this price chart: 1. Key S/R levels 2. Chart patterns 3. Trend direction 4. Volume profile" -f chart.png
```

### PDF Report Parsing
```bash
gemini -p "Extract from this financial report: 1. Key findings 2. Numerical data 3. Risk factors 4. Market outlook" -f report.pdf
```

### Multi-file Comparison
```bash
gemini -p "Compare these two charts: 1. Correlation patterns 2. Divergence points 3. Relative strength" -f chart1.png -f chart2.png
```

## Failure Handling

When a Gemini CLI call fails (non-zero exit code, timeout, or empty output):

1. **Notify the user immediately** with:
   - What was being delegated (task description, attached files)
   - The error (exit code, stderr, or "empty response")
   - Which skill step was affected
2. **Do NOT silently skip the step** — if the task involves multimodal input, no other AI can substitute without the file.
3. **Offer alternatives:**
   - Retry the same command
   - Proceed without Gemini but flag the result as **incomplete** (mark clearly in output: "Gemini analysis unavailable — visual/document analysis not performed")
   - User runs Gemini interactively in a separate terminal (`! gemini -p "..." -f {file}`)
4. **Log the failure** — if structured logging is active, emit a log event.

## Output Requirements

Gemini responses must include:
- Structured Markdown with sections
- Numerical data in table format
- Confidence level (High/Medium/Low)
- Analysis limitations and assumptions
