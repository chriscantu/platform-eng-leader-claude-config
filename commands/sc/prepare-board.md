# /prepare-board Command - Board-Level Technology Presentation

## Purpose
Prepare comprehensive board-level technology strategy presentations with business impact focus, competitive positioning, and strategic investment justification.

## Syntax
```
/prepare-board [topic] [--format presentation|report] [--audience board|exec|investors] [--duration timeframe]
```

## Parameters
- `topic`: technology-strategy | platform-update | investment-request | risk-assessment
- `--format`: presentation (slides) | report (detailed) | summary (executive brief)
- `--audience`: board | executive-team | investors | audit-committee
- `--duration`: quarterly | annual | special-session

## Auto-Persona Activation
- **Primary**: camille (executive strategy) + alvaro (business value) + david (financial analysis)
- **Supporting**: diego (execution readiness) + elena (risk assessment)

## Outputs
- Executive presentation with business-focused technology narrative
- Financial impact analysis with ROI projections and cost modeling
- Competitive positioning and market differentiation analysis
- Risk assessment with mitigation strategies and contingency planning
- Q&A preparation with anticipated board questions and responses

## Example Usage
```bash
/prepare-board platform-update --format presentation --audience board --duration quarterly
```

## Integration
- Uses data from `/assess-org` for organizational metrics
- Incorporates `/justify-investment` analysis
- Supports `/communicate-vision` strategic messaging