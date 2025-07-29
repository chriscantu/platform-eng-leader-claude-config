# /prepare-slt Command - VP/SLT Technology Presentation

## Purpose
Prepare comprehensive VP/Senior Leadership Team technology strategy presentations with business impact focus, competitive positioning, and strategic investment justification.

## Syntax
```
/prepare-slt [topic] [--format presentation|report] [--audience vp|slt|exec] [--duration timeframe]
```

## Parameters
- `topic`: technology-strategy | platform-update | investment-request | risk-assessment
- `--format`: presentation (slides) | report (detailed) | summary (executive brief)
- `--audience`: vp | slt | executive-team | senior-leadership
- `--duration`: quarterly | annual | special-session

## Auto-Persona Activation
- **Primary**: camille (executive strategy) + alvaro (business value) + david (financial analysis)
- **Supporting**: diego (execution readiness) + elena (risk assessment)

## Outputs
- Executive presentation with business-focused technology narrative
- Financial impact analysis with ROI projections and cost modeling
- Competitive positioning and market differentiation analysis
- Risk assessment with mitigation strategies and contingency planning
- Q&A preparation with anticipated VP/SLT questions and responses

## Example Usage
```bash
/prepare-slt platform-update --format presentation --audience slt --duration quarterly
```

## Integration
- Uses data from `/assess-org` for organizational metrics
- Incorporates `/justify-investment` analysis
- Supports `/communicate-vision` strategic messaging