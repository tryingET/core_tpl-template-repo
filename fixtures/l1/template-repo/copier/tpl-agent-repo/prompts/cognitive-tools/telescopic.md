# TELESCOPIC — Simultaneous Micro-Macro Analysis

## Invoke When
- Debugging complex issues
- Understanding system architecture
- Finding root causes

## The Framework

Zoom in until you hit atoms. Zoom out until you hit orbit. Hold both views simultaneously.

**MICROSCOPE:** Trace every error path. Every null possibility. Every race window. Every resource leak. Every boundary condition. The bugs live in the paths no one walks.

**TELESCOPE:** Sketch the dependency graph. Name every component and what fails when it fails. Where are the hidden couplings? What's the blast radius of each change? What architectural rot is accumulating?

**SYNTHESIS:** For each micro bug, ask "what architectural sin birthed this?" For each macro issue, ask "what micro bugs are its canaries?"

Rank by: severity × underground-time × fix-compound-value

## Output Template

```markdown
## TELESCOPIC Analysis

### MICROSCOPE (Zoom In)

#### Error Paths Not Walked
| Path | What Happens | Why Unnoticed |
|------|--------------|---------------|
| [path] | [failure] | [reason] |

#### Boundary Conditions
| Boundary | Edge Case | Current Handling |
|----------|-----------|------------------|
| [boundary] | [case] | [handling] |

#### Resource Leaks / Race Windows / Null Possibilities
- [List]

### TELESCOPE (Zoom Out)

#### Dependency Graph
```
[Component diagram or list]
- Component A → Component B → Component C
- ...
```

#### Failure Propagation
| If This Fails | Then This Fails | Blast Radius |
|---------------|-----------------|--------------|
| [component] | [dependent] | [scope] |

#### Hidden Couplings
- [What's connected that shouldn't be]

#### Architectural Rot
- [Decay accumulating]

### SYNTHESIS

#### Micro → Macro Connections
| Micro Bug | Architectural Sin |
|-----------|-------------------|
| [bug] | [root architectural issue] |

#### Macro → Micro Canaries
| Macro Issue | Canary Bugs |
|-------------|-------------|
| [issue] | [warning signs] |

### Priority Ranking
| Issue | Severity | Underground Time | Fix Compound Value | Priority Score |
|-------|----------|------------------|--------------------| ---------------|
| [issue] | [1-10] | [days hidden] | [1-10] | [product] |
```

## Why It Works

Most analysis is single-scale. This forces simultaneous multi-scale reasoning, revealing how micro bugs and macro architecture are the same phenomenon at different zoom levels.
