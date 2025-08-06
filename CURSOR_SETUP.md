# Cursor IDE Setup Guide for SuperClaude

This guide helps you set up Cursor IDE to work seamlessly with the SuperClaude platform engineering leadership framework.

## Quick Setup (5 minutes)

### 1. Open SuperClaude Directory in Cursor

```bash
cd platform-eng-leader-claude-config
cursor .
```

**✅ That's it!** The framework automatically activates with all personas and strategic context.

### 2. Verify Setup

Open any file in the `workspace/` directory and try these commands:

```
"Help me prepare for a VP meeting using diego persona"
"Review this document with the martin technical architecture perspective"
"What would alvaro say about the ROI of this initiative?"
```

You should see responses that demonstrate persona-specific expertise and platform leadership context.

## How It Works

### Automatic Framework Loading

When you open this directory in Cursor, these files automatically provide context:

- **`CLAUDE.md`**: Main entry point that loads all framework components
- **`framework/PERSONAS.md`**: All 12 strategic personas and their expertise
- **`framework/COMMANDS.md`**: Strategic command system and workflows
- **All framework files**: Principles, rules, flags, and strategic tools

### Cursor Integration Files

The repository includes Cursor-specific integration:

- **`.cursorrules`**: Cursor automatically loads SuperClaude context
- **`CURSOR_CONTEXT.md`**: Additional context for Cursor's AI features
- **Auto-activation**: Personas activate based on your conversation context

## Working with Strategic Documents

### Recommended Workflow

1. **Open the SuperClaude directory** in Cursor
2. **Navigate to `workspace/` subdirectories** for your strategic work
3. **Use natural language** to activate personas and get strategic guidance
4. **Reference templates** in `workspace/` for structured strategic planning

### Strategic Document Types

**Meeting Preparation** (`workspace/meeting-prep/`):
```
"Help me prepare for my VP 1-on-1 using the template"
"What questions should I anticipate from senior leadership?"
"Review my talking points for strategic clarity"
```

**Initiative Planning** (`workspace/current-initiatives/`):
```
"Help me build the business case for this platform initiative"
"What technical risks should I consider for this architecture?"
"How do I quantify the ROI of this design system investment?"
```

**Strategic Analysis** (`workspace/strategic-docs/`):
```
"Analyze our competitive position in platform capabilities"
"Help me assess our team's capability maturity"
"What should be in our technology radar for next year?"
```

### Persona Activation Examples

**Engineering Leadership** (diego persona):
```
"How do I coordinate this initiative across multiple teams?"
"What's the best way to communicate this technical decision to other directors?"
"Help me plan resource allocation for platform vs. feature work"
```

**Executive Communication** (camille persona):
```
"Help me translate this technical investment into business terms"
"What's the strategic framework for this VP presentation?"
"How do I position this platform capability as competitive advantage?"
```

**Business Value** (alvaro persona):
```
"What's the ROI calculation for this platform investment?"
"How do I demonstrate user impact from these platform improvements?"
"What market differentiation does this capability provide?"
```

**Financial Planning** (david persona):
```
"Help me build the budget justification for this team expansion"
"What's the TCO analysis for this vendor vs. build decision?"
"How do I optimize resource allocation across platform capabilities?"
```

## Advanced Features

### Multi-Persona Consultation

```
"I need diego and alvaro perspectives on this cross-team platform initiative"
"What would rachel and elena say about design system accessibility compliance?"
"Give me camille and david viewpoints on this strategic vendor partnership"
```

### Strategic Memory Integration

The framework includes persistent memory across sessions:
```
"Reference our previous discussion about the design system strategy"
"What were the outcomes from my last VP meeting preparation?"
"How does this initiative relate to our Q1 strategic planning?"
```

### Executive Communication Protocols

All interactions automatically follow VP/SLT communication best practices:
- Single-question focus for executive efficiency
- Business impact translation from technical details
- Evidence-based recommendations with quantifiable metrics
- Stakeholder-specific messaging optimization

## File Organization

### Recommended Structure

```
workspace/
├── current-initiatives/     # Active platform initiatives
├── meeting-prep/           # Meeting preparation materials
│   ├── vp-1on1s/          # VP/senior leadership meetings
│   ├── slt-reviews/       # Senior leadership team reviews
│   └── stakeholder-meetings/ # Cross-team coordination
├── strategic-docs/        # Long-term strategic planning
├── vendor-evaluations/    # Vendor and partnership assessments
└── budget-planning/       # Budget and resource planning
```

### Working with Templates

1. **Copy templates** from template files in each directory
2. **Customize for your specific situation**
3. **Use persona guidance** to enhance strategic thinking
4. **Version control** your strategic documents as they evolve

## Troubleshooting

### Framework Not Loading
- Ensure you opened the `platform-eng-leader-claude-config` directory (not a subdirectory)
- Check that `CLAUDE.md` is in the root directory
- Restart Cursor if needed

### Personas Not Activating
- Mention persona names explicitly: "using diego persona"
- Use strategic keywords that trigger auto-activation
- Check that you're working in the SuperClaude directory

### Context Not Available
- Verify all framework files are present in `framework/` directory
- Ensure you're working within the SuperClaude directory tree
- Try explicit persona activation with specific strategic context

## Tips for Maximum Effectiveness

✅ **Be specific** about the strategic context and persona needed  
✅ **Reference templates** for structured strategic planning  
✅ **Use business language** to get executive-level guidance  
✅ **Ask follow-up questions** to deepen strategic analysis  
✅ **Combine multiple personas** for comprehensive perspective  
✅ **Leverage memory system** for cross-session strategic intelligence  

---

**Ready to start?** Open the SuperClaude directory in Cursor and begin your strategic platform engineering work with all 12 personas and frameworks at your disposal!