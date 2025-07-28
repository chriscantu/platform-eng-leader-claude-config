# /assess-org Command - Organizational Health Assessment

## Purpose
Comprehensive assessment of engineering organization health, team performance, and cultural metrics for Director-level strategic decision making.

## Syntax
```
/assess-org [scope] [--focus domain] [--timeframe period] [--stakeholders list]
```

## Parameters
- `scope`: team | department | organization | cross-functional
- `--focus`: culture | performance | retention | capabilities | processes
- `--timeframe`: quarterly | annual | trending
- `--stakeholders`: list of stakeholder groups to include in assessment

## Auto-Persona Activation
- **Primary**: diego (engineering leadership) + camille (organizational strategy)
- **Supporting**: david (resource analysis) + marcus (culture assessment)

## Outputs
- Executive summary with key metrics and trends
- Team performance scorecards with benchmarking
- Cultural health indicators and improvement recommendations
- Resource allocation and capability gap analysis
- Strategic recommendations for organizational development

## Example Usage
```bash
/assess-org organization --focus performance --timeframe quarterly --stakeholders "product,design,executive"
```

## Integration
- Links to `/plan-succession` for leadership development
- Feeds into `/justify-investment` for resource planning
- Supports `/develop-culture` initiatives