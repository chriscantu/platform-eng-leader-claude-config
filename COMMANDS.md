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
- **Tier 2**: `/design`, `/task`, `/align-stakeholders`, `/prepare-board`

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

**`/assess-org [scope] [flags]`** - Organizational health assessment | Auto-Persona: Diego, Camille, Marcus | MCP: Sequential

**`/prepare-board [topic] [flags]`** - Board-level technology presentations | Auto-Persona: Camille, Alvaro, David | MCP: Sequential, Context7

**`/align-stakeholders [initiative] [flags]`** - Cross-functional alignment & coordination | Auto-Persona: Diego, Camille, Rachel | MCP: Sequential

**`/justify-investment [type] [flags]`** - Strategic investment business cases | Auto-Persona: Alvaro, David, Camille | MCP: Sequential

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
- **Strategic Leadership**: assess-org, prepare-board, align-stakeholders, justify-investment
- **Platform Strategy**: analyze, design, improve
- **Resource Planning**: estimate, task  
- **Sub-Agent Coordination**: spawn, load, index
- **IC-Level Delegation**: Via `/task` with specialized sub-agents for implementation work

### Wave-Enabled Commands (Director-Level)
6 commands: `/analyze`, `/design`, `/improve`, `/task`, `/assess-org`, `/justify-investment`