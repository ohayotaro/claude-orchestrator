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

## Output Requirements

Gemini responses must include:
- Structured Markdown with sections
- Numerical data in table format
- Confidence level (High/Medium/Low)
- Analysis limitations and assumptions
