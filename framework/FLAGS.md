# FLAGS.md - SuperClaude Flag Reference

Flag system for Claude Code SuperClaude framework with auto-activation and conflict resolution.

## Flag System Architecture

**Priority Order**:
1. Explicit user flags override auto-detection
2. Safety flags override optimization flags
3. Performance flags activate under resource pressure
4. Persona flags based on task patterns
5. MCP server flags with context-sensitive activation
6. Wave flags based on complexity thresholds

## Director-Level Strategic Flags

**`--platform-health`**
- Comprehensive platform assessment with adoption metrics + team velocity analysis
- Auto-activates: marcus (adoption), diego (platform), alvaro (business value)
- Triggers platform health dashboard generation with executive summary
- Integration: Sequential + Context7 for industry benchmarking + Magic for visualization

**`--stakeholder-align`**
- Cross-functional coordination planning + alignment strategies + dependency mapping
- Auto-activates: diego (coordination), camille (strategic), rachel (design systems)
- Generates stakeholder-specific talking points + influence maps + communication strategies
- Integration: Sequential for complex relationship analysis + Context7 for collaboration patterns

**`--executive-brief`**
- VP-level focused output with business impact translation + competitive positioning
- Auto-activates: camille (executive communication), alvaro (business value), david (budget)
- Forces --single-question mode for executive efficiency + --uc for conciseness
- Integration: All MCP servers for comprehensive executive materials + strategic context
- VP Audience Optimization: Tailored messaging for VP of Product, VP of Engineering, VP of Design

**`--compliance-scan`**
- Accessibility + regulatory review automation with international scope + audit preparation
- Auto-activates: elena (compliance), rachel (design accessibility)
- Comprehensive WCAG + GDPR + international regulation analysis with remediation plans
- Integration: Sequential + Playwright for accessibility testing + Context7 for regulatory patterns

**`--vendor-eval`**
- Third-party tool assessment with TCO analysis + risk evaluation + contract strategy
- Auto-activates: sofia (vendor management), david (financial analysis), martin (technical integration)
- Complete vendor evaluation framework with security + compliance + exit strategy planning
- Integration: Sequential for comprehensive evaluation + Context7 for industry patterns + limited Magic

**`--team-readiness`**
- Organizational capability evaluation + scaling assessment + cultural readiness + skill gap analysis
- Auto-activates: diego (team coordination), camille (org scaling), marcus (adoption)
- Team capacity analysis + hiring plans + change management strategies + development roadmaps
- Integration: Sequential for systematic team analysis + Context7 for organizational patterns

**`--vp-product-prep`**
- VP of Product meeting preparation with platform business value + user impact + competitive positioning
- Auto-activates: alvaro (business value), rachel (UX impact), camille (strategic communication)
- Product roadmap alignment + platform capability correlation + user experience metrics + market differentiation
- Integration: Sequential for business analysis + Context7 for product patterns + Magic for UX visualization

**`--vp-engineering-prep`**
- VP of Engineering meeting preparation with technical leadership + team performance + platform strategy
- Auto-activates: diego (engineering leadership), martin (technical architecture), david (resource planning)
- Team velocity metrics + technical debt analysis + platform adoption rates + resource optimization strategies
- Integration: Sequential for technical analysis + Context7 for engineering leadership patterns

**`--vp-design-prep`**
- VP of Design meeting preparation with design system strategy + cross-functional design impact + user experience outcomes
- Auto-activates: rachel (design leadership), camille (strategic alignment), marcus (adoption metrics)
- Design system adoption + accessibility compliance + user experience consistency + cross-team design coordination
- Integration: Magic for design system analysis + Sequential for strategic alignment + Context7 for design leadership patterns

**`--weekly-report-gen`**
- Weekly SLT report generation with Jira epic analysis + business value translation + executive formatting
- Auto-activates: camille (executive communication), alvaro (business value), diego (platform coordination)
- Epic completion forecasting + business impact translation + risk assessment + resource implications
- Integration: Sequential for epic analysis + Context7 for business value frameworks + WebFetch for Jira API

## Model Selection & Cost Optimization Flags

**`--cost-optimize`**
- Automatically select most cost-effective model based on task complexity and business impact
- Auto-activates: Sonnet 4 for routine tasks, Opus for executive/strategic contexts
- 60-70% cost savings while preserving strategic decision quality
- Integration: MODEL-SELECTION.md routing logic + quality gates

**`--opus-required`**
- Force Opus model for quality-critical tasks regardless of cost
- Auto-activates: VP/SLT contexts, investment decisions >$100K, strategic planning
- Premium quality assurance for high-stakes decisions
- Integration: Executive personas + strategic complexity detection

**`--budget-mode`**
- Maximum cost savings with quality preservation gates
- Auto-activates: Sonnet 4 default with automatic escalation triggers
- Cost tracking + optimization analytics + quality monitoring
- Integration: Daily/weekly usage tracking + ROI analysis

**`--exec-mode`**
- Executive context with premium quality assurance and Opus prioritization
- Auto-activates: Always Opus for VP/SLT communications + strategic decisions
- Zero compromise on executive satisfaction and strategic outcomes
- Integration: Executive personas + Strategic Analytics + Executive Communication MCP

## Planning & Analysis Flags

**`--plan`**
- Display execution plan before operations
- Shows tools, outputs, and step sequence

**`--think`**
- Multi-file analysis (~4K tokens)
- Enables Sequential MCP for structured problem-solving
- Auto-activates: Import chains >5 files, cross-module calls >10 references
- Auto-enables `--seq` for structured problem-solving

**`--think-hard`**
- Deep architectural analysis (~10K tokens)
- System-wide analysis with cross-module dependencies
- Auto-activates: System refactoring, bottlenecks >3 modules, security vulnerabilities
- Auto-enables `--seq --c7` for comprehensive analysis

**`--ultrathink`**
- Critical system redesign analysis (~32K tokens)
- Maximum depth analysis for complex problems
- Auto-activates: Legacy modernization, critical vulnerabilities, performance degradation >50%
- Auto-enables `--seq --c7 --all-mcp` for comprehensive analysis

## Compression & Efficiency Flags

**`--uc` / `--ultracompressed`**
- 30-50% token reduction using symbols and structured output
- Auto-activates: Context usage >75% or large-scale operations
- Auto-generated symbol legend, maintains technical accuracy

**`--answer-only`**
- Direct response without task creation or workflow automation
- Explicit use only, no auto-activation

**`--single-question`**
- Ask ONE focused question at a time, wait for response before proceeding
- Auto-activates: VP/SLT context, strategic persona sessions, executive communications
- Optimizes for executive efficiency and decision-making clarity

**`--validate`**
- Pre-operation validation and risk assessment
- Auto-activates: Risk score >0.7 or resource usage >75%
- Risk algorithm: complexity*0.3 + vulnerabilities*0.25 + resources*0.2 + failure_prob*0.15 + time*0.1

**`--safe-mode`**
- Maximum validation with conservative execution
- Auto-activates: Resource usage >85% or production environment
- Enables validation checks, forces --uc mode, blocks risky operations

**`--verbose`**
- Maximum detail and explanation
- High token usage for comprehensive output

## MCP Server Control Flags

**`--c7` / `--context7`**
- Enable Context7 for library documentation lookup
- Auto-activates: External library imports, framework questions
- Detection: import/require/from/use statements, framework keywords
- Workflow: resolve-library-id → get-library-docs → implement

**`--seq` / `--sequential`**
- Enable Sequential for complex multi-step analysis
- Auto-activates: Complex debugging, system design, --think flags
- Detection: debug/trace/analyze keywords, nested conditionals, async chains

**`--magic`**
- Enable Magic for UI component generation
- Auto-activates: UI component requests, design system queries
- Detection: component/button/form keywords, JSX patterns, accessibility requirements

**`--play` / `--playwright`**
- Enable Playwright for cross-browser automation and E2E testing
- Detection: test/e2e keywords, performance monitoring, visual testing, cross-browser requirements

**`--all-mcp`**
- Enable all MCP servers simultaneously
- Auto-activates: Problem complexity >0.8, multi-domain indicators
- Higher token usage, use judiciously

**`--no-mcp`**
- Disable all MCP servers, use native tools only
- 40-60% faster execution, WebSearch fallback

**`--no-[server]`**
- Disable specific MCP server (e.g., --no-magic, --no-seq)
- Server-specific fallback strategies, 10-30% faster per disabled server

## Sub-Agent Delegation Flags

**`--delegate [files|folders|auto]`**
- Enable Task tool sub-agent delegation for parallel processing
- **files**: Delegate individual file analysis to sub-agents
- **folders**: Delegate directory-level analysis to sub-agents
- **auto**: Auto-detect delegation strategy based on scope and complexity
- Auto-activates: >7 directories or >50 files
- 40-70% time savings for suitable operations

**`--concurrency [n]`**
- Control max concurrent sub-agents and tasks (default: 7, range: 1-15)
- Dynamic allocation based on resources and complexity
- Prevents resource exhaustion in complex scenarios

## Wave Orchestration Flags

**`--wave-mode [auto|force|off]`**
- Control wave orchestration activation
- **auto**: Auto-activates based on complexity >0.8 AND file_count >20 AND operation_types >2
- **force**: Override auto-detection and force wave mode for borderline cases
- **off**: Disable wave mode, use Sub-Agent delegation instead
- 30-50% better results through compound intelligence and progressive enhancement

**`--wave-strategy [progressive|systematic|adaptive|enterprise]`**
- Select wave orchestration strategy
- **progressive**: Iterative enhancement for incremental improvements
- **systematic**: Comprehensive methodical analysis for complex problems
- **adaptive**: Dynamic configuration based on varying complexity
- **enterprise**: Large-scale orchestration for >100 files with >0.7 complexity
- Auto-selects based on project characteristics and operation type

**`--wave-delegation [files|folders|tasks]`**
- Control how Wave system delegates work to Sub-Agent
- **files**: Sub-Agent delegates individual file analysis across waves
- **folders**: Sub-Agent delegates directory-level analysis across waves
- **tasks**: Sub-Agent delegates by task type (security, performance, quality, architecture)
- Integrates with `--delegate` flag for coordinated multi-phase execution

## Scope & Focus Flags

**`--scope [level]`**
- file: Single file analysis
- module: Module/directory level
- project: Entire project scope
- system: System-wide analysis

**`--focus [domain]`**
- performance: Performance optimization
- security: Security analysis and hardening
- quality: Code quality and maintainability
- architecture: System design and structure
- accessibility: UI/UX accessibility compliance
- testing: Test coverage and quality

## Iterative Improvement Flags

**`--loop`**
- Enable iterative improvement mode for commands
- Auto-activates: Quality improvement requests, refinement operations, polish tasks
- Compatible commands: /improve, /refine, /enhance, /fix, /cleanup, /analyze
- Default: 3 iterations with automatic validation

**`--iterations [n]`**
- Control number of improvement cycles (default: 3, range: 1-10)
- Overrides intelligent default based on operation complexity

**`--interactive`**
- Enable user confirmation between iterations
- Pauses for review and approval before each cycle
- Allows manual guidance and course correction

## Persona Activation Flags

**Available Strategic Personas** (Enhanced):
- `--persona-diego`: Engineering leadership, platform strategy, multinational coordination
- `--persona-camille`: Strategic technology, organizational scaling, executive advisory
- `--persona-rachel`: Design systems strategy, cross-functional alignment, UX leadership
- `--persona-alvaro`: Platform investment ROI, business value, stakeholder communication
- `--persona-sofia`: Vendor relationships, tool evaluation, technology partnerships
- `--persona-elena`: Accessibility compliance, legal requirements, audit management
- `--persona-marcus`: Internal adoption, change management, platform marketing
- `--persona-david`: Platform investment allocation, cost optimization, financial planning
- `--persona-martin`: Platform architecture, evolutionary design, technical debt strategy
- `--persona-legal`: International compliance, regulatory navigation, contract strategy
- `--persona-security`: Platform security architecture, threat modeling, risk assessment
- `--persona-data`: Analytics strategy, metrics frameworks, data-driven decision making

## Introspection & Transparency Flags

**`--introspect` / `--introspection`**
- Deep transparency mode exposing thinking process
- Auto-activates: SuperClaude framework work, complex debugging
- Transparency markers: 🤔 Thinking, 🎯 Decision, ⚡ Action, 📊 Check, 💡 Learning
- Conversational reflection with shared uncertainties

## Flag Integration Patterns

### MCP Server Auto-Activation

**Auto-Activation Logic**:
- **Context7**: External library imports, framework questions, documentation requests
- **Sequential**: Complex debugging, system design, any --think flags
- **Magic**: UI component requests, design system queries, frontend persona
- **Playwright**: Testing workflows, performance monitoring, QA persona

### Flag Precedence

1. Safety flags (--safe-mode) > optimization flags
2. Explicit flags > auto-activation
3. Thinking depth: --ultrathink > --think-hard > --think
4. --no-mcp overrides all individual MCP flags
5. Scope: system > project > module > file
6. Last specified persona takes precedence
7. Wave mode: --wave-mode off > --wave-mode force > --wave-mode auto
8. Sub-Agent delegation: explicit --delegate > auto-detection
9. Loop mode: explicit --loop > auto-detection based on refinement keywords
10. --uc auto-activation overrides verbose flags

### Context-Based Auto-Activation

**Director-Level Context Auto-Activation** (Enhanced):
- **Budget/Financial Context**: "budget", "cost", "ROI", "investment", "resource allocation", "budget meeting" → --executive-brief + david + camille + alvaro
- **Compliance Context**: "compliance", "accessibility", "GDPR", "audit", "legal", "a11y", "WCAG" → --compliance-scan + elena + rachel + --validate
- **Vendor/Partnership Context**: "vendor", "tool evaluation", "contract", "partnership", "procurement" → --vendor-eval + sofia + david + martin
- **Platform Strategy Context**: "platform adoption", "design system", "developer experience", "DevEx", "platform health" → --platform-health + diego + marcus + rachel
- **Executive Communication**: "VP", "executive", "presentation", "VP of Product", "VP of Engineering", "VP of Design", "SLT", "leadership team" → --executive-brief + --single-question + camille
- **Weekly Reporting**: "weekly report", "SLT report", "sprint summary", "epic status", "business value" → --weekly-report-gen + camille + alvaro + diego
- **Security Context**: "security", "threat", "vulnerability", "security audit", "risk assessment" → --compliance-scan + security + elena + --validate
- **Legal Context**: "legal requirements", "contract negotiation", "regulatory compliance", "privacy law" → --compliance-scan + legal + elena + --validate
- **Analytics Context**: "metrics", "analytics", "data", "KPI", "dashboard", "measurement" → --platform-health + data + alvaro + diego

**VP-Specific Context Auto-Activation**:
- **VP of Product Context**: "VP of Product", "product roadmap", "user experience metrics", "business value" → --vp-product-prep + alvaro + rachel + camille
- **VP of Engineering Context**: "VP of Engineering", "my boss", "engineering leadership", "team performance", "technical strategy" → --vp-engineering-prep + diego + martin + david
- **VP of Design Context**: "VP of Design", "design strategy", "design system adoption", "user experience consistency" → --vp-design-prep + rachel + camille + marcus
- **Team/Org Context**: "team readiness", "scaling", "capability", "organizational" → --team-readiness + diego + camille + marcus
- **Stakeholder Context**: "stakeholder", "alignment", "coordination", "cross-functional" → --stakeholder-align + diego + camille + rachel

**Wave Auto-Activation**: complexity ≥0.7 AND files >20 AND operation_types >2
**Sub-Agent Auto-Activation**: >7 directories OR >50 files OR complexity >0.8
**Loop Auto-Activation**: polish, refine, enhance, improve keywords detected
