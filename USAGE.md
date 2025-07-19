# Kimi Possible Usage Guide

## Domain-Specific Research Modes

Kimi Possible now supports different research domains with specialized prompts and strategies:

### Command Line Usage

```bash
# General purpose mode (default)
python kimi-possible.py --domain general

# Content research mode (movies, TV shows, entertainment)
python kimi-possible.py --domain content_research

# Technical research mode (documentation, APIs, programming)
python kimi-possible.py --domain technical_research

# Market research mode (business, trends, analytics)
python kimi-possible.py --domain market_research

# Custom research targets
python kimi-possible.py --domain general --targets "Academic papers" "Scientific journals" "Research databases"

# Using a configuration file
python kimi-possible.py --config config-examples/technical-research.json
```

### Configuration Files

Create JSON configuration files to define custom research domains:

```json
{
  "domain": "technical_research",
  "research_targets": [
    "Official documentation sites",
    "GitHub repositories", 
    "Stack Overflow discussions",
    "Technical blogs and tutorials",
    "API references"
  ]
}
```

### Research Domain Strategies

#### Content Research
- **Best for**: Movies, TV shows, entertainment analysis
- **Sources**: Reddit, Letterboxd, X.com/Twitter, Rotten Tomatoes
- **Approach**: User opinions, ratings, sentiment analysis

#### Technical Research  
- **Best for**: Programming, APIs, technical documentation
- **Sources**: Official docs, Stack Overflow, GitHub, technical blogs
- **Approach**: Authoritative sources, code examples, implementation details

#### Market Research
- **Best for**: Business trends, market analysis, competitive intelligence  
- **Sources**: News, industry reports, social sentiment, company data
- **Approach**: Quantitative data, trends, market indicators

#### General Research
- **Best for**: Any topic with adaptive strategy
- **Sources**: Comprehensive web search across all platforms
- **Approach**: Flexible, context-dependent research methodology

### Examples

```bash
# Research a new JavaScript framework
python kimi-possible.py --domain technical_research
> "Research the latest features in React 19"

# Analyze movie reception
python kimi-possible.py --domain content_research  
> "Find reactions to the new Dune movie"

# Market analysis
python kimi-possible.py --domain market_research
> "Research trends in the electric vehicle market"

# Custom academic research
python kimi-possible.py --domain general --targets "Google Scholar" "arXiv" "PubMed"
> "Find recent papers on machine learning interpretability"
```

## File Operations

All research modes support the same file operations:

- `/add path/to/file` - Add single file to context
- `/add path/to/folder` - Add entire folder to context  
- Automatic file reading, creation, and editing via function calls

## Backward Compatibility

The tool maintains backward compatibility - running without arguments defaults to content research mode (the original behavior).