# MODEL-SELECTION.md - Intelligent Cost-Optimized Model Routing

Cost-effective model selection system for Director-level strategic leadership while maintaining quality standards.

## Cost Optimization Philosophy

**Primary Directive**: "Strategic quality where it matters | Cost efficiency for routine tasks | Automatic escalation for executive contexts"

**Cost Savings Target**: 60-70% reduction through intelligent model routing while preserving strategic decision quality.

## Model Selection Matrix

### **Sonnet 4 (Cost-Effective)** - 60-70% cost savings
**Use Cases**:
- Technical analysis and code review
- Platform health monitoring and metrics
- Documentation generation and updates
- Standard cross-team coordination
- Routine vendor evaluation tasks
- Non-executive communications
- Design system implementation
- Compliance monitoring (non-critical)

**Auto-Activation Triggers**:
- Complexity score <0.7
- No executive personas active (camille/alvaro)
- Non-VP/SLT context
- Routine monitoring keywords: "status", "update", "review", "monitor"
- Technical implementation: "code", "implementation", "deploy", "test"

### **Opus (Premium Quality)** - Strategic value justifies cost
**Use Cases**:
- VP/SLT presentations and strategic communications
- Investment business cases >$100K
- Executive-level strategic planning and org design
- High-stakes vendor negotiations >$250K
- Critical compliance assessments (audit/legal)
- Complex architectural decisions with >2 year impact
- Crisis management and incident response

**Auto-Activation Triggers**:
- Complexity score ≥0.7
- Executive personas active (camille/alvaro/david)
- VP/SLT context detected
- Executive keywords: "VP", "executive", "board", "strategic", "investment"
- High-value decisions: ">$100K", "business case", "ROI analysis"
- Risk management: "compliance", "legal", "audit", "security incident"

## Intelligent Routing Algorithm

### **Primary Selection Logic**
```yaml
1. Executive Context Detection (98% confidence)
   → VP/SLT mentions → Opus
   → Strategic personas (camille/alvaro) → Opus
   → Investment >$100K → Opus

2. Business Impact Assessment
   → High Impact (0.8+) → Opus
   → Medium Impact (0.5-0.8) → Sonnet 4 (with escalation option)
   → Standard Impact (<0.5) → Sonnet 4

3. Persona-Based Routing
   → camille/alvaro/david (Executive) → Opus
   → diego/rachel/martin (Platform) → Sonnet 4
   → sofia/elena/marcus (Operations) → Sonnet 4

4. Complexity-Based Routing
   → Multi-stakeholder coordination → Opus
   → Cross-team dependencies → Sonnet 4
   → Technical implementation → Sonnet 4
```

### **Auto-Escalation Rules**
```yaml
# Automatic escalation from Sonnet 4 → Opus
- Executive context detected mid-conversation
- Investment value escalates >$100K
- VP/SLT stakeholders mentioned
- Strategic risk identified (legal/compliance)
- Quality degradation detected
```

### **Cost Control Mechanisms**
```yaml
# Prevent unnecessary Opus usage
- Confirmation prompt for non-obvious Opus selections
- Daily/weekly Opus usage tracking
- Auto-suggest Sonnet 4 alternatives
- Batch processing for multiple similar tasks
```

## Context-Specific Model Selection

### **Executive Communication Pipeline**
```yaml
VP/SLT Contexts → Always Opus:
- "VP of Product meeting tomorrow"
- "Board presentation prep"
- "Executive team strategy session"
- "Investment committee review"
- "Budget planning with SLT"
```

### **Platform Operations Pipeline**
```yaml
Platform Tasks → Sonnet 4 (Cost-Effective):
- "Platform health dashboard update"
- "Weekly adoption metrics review"
- "Cross-team coordination meeting prep"
- "Design system component analysis"
- "Developer experience improvements"
```

### **Strategic Decision Pipeline**
```yaml
High-Stakes Decisions → Opus:
- "Architecture decision >$250K impact"
- "Vendor negotiation >$500K annual"
- "Organizational restructuring plan"
- "Compliance audit preparation"
- "Security incident response strategy"
```

## Quality Gates and Safeguards

### **Quality Preservation Rules**
```yaml
# Never compromise quality for cost on:
- VP/SLT communications (reputation risk)
- Investment decisions >$100K (financial risk)
- Legal/compliance matters (regulatory risk)
- Security incidents (business risk)
- Organizational design (people risk)
```

### **Automatic Quality Checks**
```yaml
# Sonnet 4 → Opus escalation triggers:
- Response quality score <0.8
- Strategic inconsistency detected
- Executive stakeholder satisfaction <0.9
- Business impact underestimated
- Risk assessment incomplete
```

## Cost Optimization Metrics

### **Target Cost Savings**
- **Overall**: 60-70% cost reduction
- **Routine Tasks**: 85-90% cost reduction (Sonnet 4)
- **Strategic Tasks**: Cost optimization through efficiency, not model downgrade
- **ROI Target**: >10:1 cost savings vs strategic value preservation

### **Quality Maintenance**
- **Executive Satisfaction**: >95% (VP/SLT communications)
- **Strategic Decision Quality**: No degradation from baseline
- **Risk Management**: Zero compromise on legal/compliance/security
- **Platform Outcomes**: Maintain adoption and velocity metrics

## Implementation Strategy

### **Phase 1: Conservative Routing** (Weeks 1-2)
- High confidence Sonnet 4 tasks only
- Manual confirmation for borderline cases
- Quality monitoring and feedback collection

### **Phase 2: Intelligent Automation** (Weeks 3-4)
- Automated routing based on confidence thresholds
- Auto-escalation rules implementation
- Cost tracking and optimization analytics

### **Phase 3: Advanced Optimization** (Weeks 5+)
- Machine learning-based routing refinement
- Predictive cost optimization
- Advanced quality preservation mechanisms

## Integration with SuperClaude Framework

### **Persona Integration**
```yaml
Executive Personas (Opus Priority):
- camille: Strategic technology + exec advisory → Opus
- alvaro: Platform ROI + business value → Opus
- david: Investment allocation + financial → Opus

Platform Personas (Cost-Effective):
- diego: Engineering leadership → Sonnet 4 (escalate for exec context)
- rachel: Design systems → Sonnet 4
- marcus: Platform adoption → Sonnet 4
```

### **MCP Server Coordination**
```yaml
# Model selection influences MCP server usage
Opus Sessions:
- Enhanced Executive Communication server usage
- Premium Strategic Analytics features
- Advanced Context7 organizational patterns

Sonnet 4 Sessions:
- Standard MCP server features
- Cost-optimized caching strategies
- Efficient context management
```

### **Flag System Integration**
```yaml
# New cost-optimization flags
--cost-optimize: Auto-select most cost-effective model
--opus-required: Force Opus for quality-critical tasks
--budget-mode: Maximum cost savings with quality gates
--exec-mode: Executive context with premium quality assurance
```

## Monitoring and Optimization

### **Cost Tracking Dashboard**
- Daily/weekly Opus vs Sonnet 4 usage
- Cost per strategic outcome delivered
- Quality metrics by model selection
- ROI analysis of model routing decisions

### **Continuous Improvement**
- A/B testing of routing decisions
- Quality feedback integration
- Cost optimization pattern recognition
- Strategic value correlation analysis
