# COMMANDS.md - SuperClaude Command Execution Framework

Command execution framework for Claude Code SuperClaude integration.

## Command System Architecture

### Core Command Structure
```yaml
---
command: "/{command-name}"
category: "Primary classification"
purpose: "Operational objective"
wave-enabled: true|false
performance-profile: "optimization|standard|complex"
---
```

### Command Processing Pipeline
1. **Input Parsing**: `$ARGUMENTS` with `@<path>`, `!<command>`, `--<flags>`
2. **Context Resolution**: Auto-persona activation and MCP server selection
3. **Wave Eligibility**: Complexity assessment and wave mode determination
4. **Execution Strategy**: Tool orchestration and resource allocation
5. **Quality Gates**: Validation checkpoints and error handling

### Integration Layers
- **Claude Code**: Native slash command compatibility
- **Persona System**: Auto-activation based on command context
- **MCP Servers**: Context7, Sequential, Magic, Playwright integration
- **Wave System**: Multi-stage orchestration for complex operations

## Wave System Integration

**Wave Orchestration Engine**: Multi-stage command execution with compound intelligence. Auto-activates on complexity ≥0.7 + files >20 + operation_types >2.

**Wave-Enabled Commands (Director-Level)**:
- **Tier 1**: `/analyze`, `/improve`, `/assess-org`, `/justify-investment`  
- **Tier 2**: `/design`, `/task`, `/align-stakeholders`, `/prepare-slt`

### Strategic Development Commands

**`/design [domain] [flags]`** - System architecture and strategic design decisions
```yaml
---
command: "/design"
category: "Strategic Architecture"  
purpose: "Platform architecture and system design strategy"
wave-enabled: true
performance-profile: "complex"
---
```
- **Auto-Persona**: Martin (architect), Camille (strategic alignment), Rachel (design systems)
- **MCP Integration**: Sequential (strategic analysis), Context7 (patterns), Magic (system design)
- **Tool Orchestration**: [Read, Grep, Sequential, TodoWrite, Task]
- **Arguments**: `[domain]`, `--scope system|platform|organization`, `--stakeholders <list>`, `--<flags>`

### Analysis Commands

**`/analyze $ARGUMENTS`**
```yaml
---
command: "/analyze"
category: "Strategic Analysis & Investigation"
purpose: "Multi-dimensional strategic and system analysis"
wave-enabled: true
performance-profile: "complex"
---
```
- **Auto-Persona**: Diego (leadership), Martin (architecture), Camille (strategic)
- **MCP Integration**: Sequential (primary), Context7 (patterns), Magic (UI analysis)
- **Tool Orchestration**: [Read, Grep, Glob, Sequential, TodoWrite]
- **Arguments**: `[target]`, `@<path>`, `!<command>`, `--<flags>`

### Quality Commands

**`/improve [target] [flags]`**
```yaml
---
command: "/improve"
category: "Strategic Enhancement"
purpose: "Evidence-based strategic improvement and optimization"
wave-enabled: true
performance-profile: "optimization"
---
```
- **Auto-Persona**: Diego (organizational), Martin (technical), Camille (strategic)
- **MCP Integration**: Sequential (logic), Context7 (patterns), Magic (improvements)
- **Tool Orchestration**: [Read, Grep, Glob, Edit, MultiEdit, Sequential]
- **Arguments**: `[target]`, `@<path>`, `!<command>`, `--<flags>`

### Strategic Planning Commands

**`/estimate [target] [flags]`** - Strategic resource estimation and capacity planning
- **Auto-Persona**: Diego (engineering leadership), David (resource planning), Camille (strategic assessment)
- **MCP Integration**: Sequential (analysis), Context7 (industry benchmarks)  
- **Focus**: Team capacity, budget allocation, timeline planning, cross-team dependencies

**`/task [operation] [flags]`** - Strategic project orchestration and long-term initiative management
- **Auto-Persona**: Diego (coordination), Martin (architecture), Camille (strategic alignment)
- **MCP Integration**: Sequential (project analysis), Task (sub-agent delegation)
- **Focus**: Multi-team coordination, strategic initiatives, organizational capabilities

### Director-Level Strategic Commands

**`/assess-org [scope] [flags]`** - Organizational health assessment
- **Enhanced Auto-Activation**: --platform-health + --team-readiness when scope includes "platform" or "team"
- **Auto-Persona**: Diego (coordination), Camille (strategic), Marcus (adoption)
- **MCP Integration**: Sequential (primary) + Context7 for organizational patterns
- **Pipeline Trigger**: Auto-suggests `/justify-investment` for resource needs identified
- **Executive Integration**: Auto-prepares executive summary with --executive-brief

**`/prepare-slt [topic] [flags]`** - VP-level technology presentations and strategic communications
- **Enhanced Auto-Activation**: --executive-brief + --stakeholder-align always active
- **Auto-Persona**: Camille (executive communication), Alvaro (business value), David (budget)
- **MCP Integration**: Sequential (strategic analysis) + Context7 (presentation patterns)
- **VP-Specific Preparation**: Auto-detects VP audience (Product/Engineering/Design) and tailors messaging
- **Context-Aware Preparation**: Auto-detects topic type and activates relevant domain personas
- **Executive Optimization**: Forces --single-question + --uc for executive efficiency
- **VP Audience Detection**: Automatically generates VP-specific talking points and strategic narratives

**`/align-stakeholders [initiative] [flags]`** - Cross-functional alignment & coordination
- **Enhanced Auto-Activation**: --stakeholder-align + context-specific domain personas
- **Auto-Persona**: Diego (coordination), Camille (strategic), Rachel (design systems)
- **MCP Integration**: Sequential (complex relationship analysis) + Context7 (collaboration patterns)
- **Integration**: Auto-coordinates with `/assess-org` and `/prepare-slt` for comprehensive alignment
- **Dependency Mapping**: Auto-generates cross-team dependency analysis and communication strategies

**`/justify-investment [type] [flags]`** - Strategic investment business cases
- **Enhanced Auto-Activation**: --vendor-eval for technology, --platform-health for platform investments
- **Auto-Persona**: Alvaro (business value), David (financial), Camille (strategic executive communication)
- **MCP Integration**: Sequential (comprehensive ROI analysis) + Context7 (industry benchmarks)
- **Business Case Automation**: Auto-generates ROI models, risk assessments, and competitive analysis
- **Executive Integration**: Auto-prepares for `/prepare-slt` pipeline with business-focused presentations

### VP-Specific Strategic Commands

**`/prep-vp-product [topic] [flags]`** - VP of Product meeting preparation
- **Enhanced Auto-Activation**: --vp-product-prep + --executive-brief always active
- **Auto-Persona**: Alvaro (business value), Rachel (UX impact), Camille (strategic communication)
- **MCP Integration**: Sequential (business analysis) + Magic (UX visualization) + Context7 (product patterns)
- **Business Focus**: Platform ROI, user experience impact, product roadmap alignment, competitive differentiation
- **Output Optimization**: Product-focused metrics, user journey impact, business value correlation

**`/prep-vp-engineering [topic] [flags]`** - VP of Engineering meeting preparation  
- **Enhanced Auto-Activation**: --vp-engineering-prep + --executive-brief always active
- **Auto-Persona**: Diego (engineering leadership), Martin (technical architecture), David (resource planning)
- **MCP Integration**: Sequential (technical analysis) + Context7 (engineering leadership patterns)
- **Technical Focus**: Team velocity, platform adoption, technical debt, resource optimization, engineering excellence
- **Output Optimization**: Engineering metrics, team performance, technical strategy alignment, resource justification

**`/prep-vp-design [topic] [flags]`** - VP of Design meeting preparation
- **Enhanced Auto-Activation**: --vp-design-prep + --executive-brief always active  
- **Auto-Persona**: Rachel (design leadership), Camille (strategic alignment), Marcus (adoption metrics)
- **MCP Integration**: Magic (design system analysis) + Sequential (strategic alignment) + Context7 (design patterns)
- **Design Focus**: Design system adoption, accessibility compliance, user experience consistency, cross-team design coordination
- **Output Optimization**: Design impact metrics, consistency scores, accessibility compliance rates, design system ROI

## Strategic Command Pipelines

**Platform Assessment Pipeline**:
```
/assess-org [scope] --platform-health
  ↓ Auto-triggers
/analyze platform --adoption-metrics  
  ↓ Feeds into
/justify-investment platform --executive-brief
  ↓ Prepares for
/prepare-slt "Platform Strategy Update" --stakeholder-align
```

**Compliance & Risk Pipeline**:
```
/analyze compliance --compliance-scan
  ↓ Auto-triggers  
/improve accessibility --validation-framework
  ↓ Feeds into
/prepare-slt "Compliance Status" --executive-brief
  ↓ With stakeholder coordination
/align-stakeholders compliance --team-readiness
```

**Vendor & Technology Pipeline**:
```
/analyze vendor [tool] --vendor-eval
  ↓ Auto-triggers
/estimate --vendor-roi --tco-analysis
  ↓ Feeds into  
/justify-investment vendor --executive-brief
  ↓ Prepares for
/align-stakeholders procurement --stakeholder-align
```

**Executive Communication Pipeline**:
```
/assess-org platform --platform-health + --team-readiness
  ↓ Generates insights for
/justify-investment platform --executive-brief + --vendor-eval (if applicable)
  ↓ Automatically prepares
/prepare-slt "Strategic Platform Update" --stakeholder-align
  ↓ With follow-up
/align-stakeholders "Platform Adoption Strategy" --team-readiness
```

### Meta & Orchestration Commands

**`/index [query] [flags]`** - Command catalog browsing | Auto-Persona: Mentor, Analyzer | MCP: Sequential

**`/load [path] [flags]`** - Project context loading | Auto-Persona: Analyzer, Architect, Scribe | MCP: All servers

**Iterative Operations** - Use `--loop` flag with improvement commands for iterative refinement

**`/spawn [mode] [flags]`** - Task orchestration | Auto-Persona: Analyzer, Architect, DevOps | MCP: All servers

## IC-Level Task Delegation (Sub-Agent Patterns)

### Implementation Sub-Agents
**Director delegates hands-on technical work through Task tool with specialized sub-agents:**

**Development Tasks**:
- **Build/Deploy**: `/task "Build and deploy [component]" --persona-devops --delegate auto`
- **Feature Implementation**: `/task "Implement [feature]" --persona-frontend --delegate files`  
- **Code Cleanup**: `/task "Refactor and cleanup [module]" --persona-refactorer --delegate auto`

**Analysis Tasks**:  
- **Troubleshooting**: `/task "Debug [issue]" --persona-analyzer --focus root-cause --delegate auto`
- **Documentation**: `/task "Document [system]" --persona-scribe=en --c7 --delegate auto`
- **Testing**: `/task "Test [functionality]" --persona-qa --play --delegate auto`

**Quality Tasks**:
- **Code Review**: `/task "Review code quality for [scope]" --persona-qa --focus quality --delegate auto`
- **Security Audit**: `/task "Security assessment of [component]" --persona-security --validate --delegate auto`

### Director Oversight Pattern
1. **Strategic Direction**: Director defines objectives and success criteria
2. **Task Delegation**: Sub-agents handle implementation details  
3. **Progress Review**: Director receives executive summaries and key insights
4. **Strategic Adjustment**: Director makes course corrections based on sub-agent findings

## Command Execution Matrix

### Performance Profiles
```yaml
optimization: "High-performance with caching and parallel execution"
standard: "Balanced performance with moderate resource usage"
complex: "Resource-intensive with comprehensive analysis"
```

### Director-Level Command Categories
- **Strategic Leadership**: assess-org, prepare-slt, align-stakeholders, justify-investment
- **Platform Strategy**: analyze, design, improve
- **Resource Planning**: estimate, task  
- **Sub-Agent Coordination**: spawn, load, index
- **IC-Level Delegation**: Via `/task` with specialized sub-agents for implementation work

### Wave-Enabled Commands (Director-Level)
6 commands: `/analyze`, `/design`, `/improve`, `/task`, `/assess-org`, `/justify-investment`