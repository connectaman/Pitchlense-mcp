# Knowledge Graph Feature

## Overview

The Knowledge Graph feature builds a comprehensive dependency network for startups, visualizing:

- **Center Node (Root)**: The company being analyzed
- **Left Side Nodes**: Dependencies (what the company relies on)
- **Right Side Nodes**: Dependents (who/what relies on the company)

For each node, the system fetches:
- Latest news articles
- Stock prices (when applicable)
- Export/Import data for India, US, and China
- Market information and trends

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Knowledge Graph Builder                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│  │ Perplexity  │    │  SerpAPI    │    │   Gemini    │    │
│  │   Search    │───▶│    News     │───▶│  LLM (JSON) │    │
│  └─────────────┘    └─────────────┘    └─────────────┘    │
│         │                  │                    │            │
│         ▼                  ▼                    ▼            │
│  Identify Deps/     Fetch News &        Structure Final     │
│  Dependents         Market Data         Knowledge Graph     │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Dependency Identification (Perplexity)
```python
Input: Startup description
Output: List of entities the company depends on
Example:
  - AI Company → GPU Manufacturers (NVIDIA)
  - Coffee Shop → Coffee Bean Suppliers (Ethiopia, Colombia)
  - Fintech → Payment Processors (Stripe, Plaid)
```

### 2. Dependent Identification (Perplexity)
```python
Input: Startup description
Output: List of entities that depend on the company
Example:
  - AI Company → Healthcare Industry, Finance Sector
  - Payment Platform → E-commerce, Retail, SaaS companies
```

### 3. Node Data Enrichment (SerpAPI + Perplexity)
For each identified entity:
```python
{
  "entity_name": "NVIDIA",
  "entity_type": "company",
  "position": "left",  # dependency
  "news": [
    {
      "title": "NVIDIA announces new H200 GPU",
      "link": "https://...",
      "source": "TechCrunch",
      "date": "2024-10-14"
    }
  ],
  "market_data": {
    "stock_ticker": "NVDA",
    "stock_price": "$XXX",
    "52_week_high": "$XXX",
    "52_week_low": "$XXX"
  },
  "trade_data": {
    "india": "Import statistics...",
    "us": "Production data...",
    "china": "Export data..."
  },
  "hover_info": "GPU manufacturer, critical for AI training"
}
```

### 4. Graph Structuring (Gemini LLM)
Final JSON structure:
```json
{
  "root": {
    "id": "company_root",
    "name": "Company Name",
    "type": "company",
    "description": "Brief description",
    "position": {"x": 0, "y": 0}
  },
  "nodes": [
    {
      "id": "dep_1",
      "name": "NVIDIA",
      "type": "dependency",
      "category": "company",
      "position": {"x": -2, "y": 1},
      "relationship": "provides GPU infrastructure",
      "news": [...],
      "market_data": {...},
      "hover_info": "..."
    }
  ],
  "edges": [
    {
      "from": "company_root",
      "to": "dep_1",
      "relationship": "depends on",
      "strength": 0.9
    }
  ],
  "metadata": {
    "total_dependencies": 8,
    "total_dependents": 6,
    "llm_processed": true
  }
}
```

## Usage

### As a Standalone Tool

```python
from pitchlense_mcp import KnowledgeGraphMCPTool, GeminiLLM

# Initialize
kg_tool = KnowledgeGraphMCPTool()
kg_tool.set_llm_client(GeminiLLM())

# Generate graph
startup_description = """
Your company description here...
"""

result = kg_tool.generate_knowledge_graph(
    startup_text=startup_description,
    company_name="YourCompany"
)

print(result)
```

### In Cloud Function

The knowledge graph is automatically generated when you call the main cloud function:

```bash
curl -X POST https://your-cloud-function-url \
  -H "Content-Type: application/json" \
  -d '{
    "startup_text": "Your company description...",
    "use_mock": false
  }'
```

Response includes:
```json
{
  "startup_analysis": {...},
  "knowledge_graph": {
    "root": {...},
    "nodes": [...],
    "edges": [...]
  },
  "news": {...},
  ...
}
```

## Visualization

### Recommended Libraries

1. **D3.js** (Most flexible)
   - Force-directed graphs
   - Custom layouts
   - Interactive tooltips

2. **vis.js** (Easy to use)
   - Pre-built network visualization
   - Good performance
   - Built-in physics simulation

3. **Cytoscape.js** (For complex graphs)
   - Advanced layouts
   - Biological network visualization
   - Great for hierarchical structures

### Sample D3.js Implementation

```javascript
// knowledge-graph-viz.js
import * as d3 from 'd3';

function renderKnowledgeGraph(graphData) {
  const width = 1200;
  const height = 800;
  
  // Create SVG
  const svg = d3.select("#graph-container")
    .append("svg")
    .attr("width", width)
    .attr("height", height);
  
  // Prepare data
  const nodes = [graphData.root, ...graphData.nodes];
  const links = graphData.edges.map(e => ({
    source: e.from,
    target: e.to,
    label: e.relationship
  }));
  
  // Create force simulation
  const simulation = d3.forceSimulation(nodes)
    .force("link", d3.forceLink(links).id(d => d.id))
    .force("charge", d3.forceManyBody().strength(-400))
    .force("center", d3.forceCenter(width / 2, height / 2))
    .force("x", d3.forceX(d => {
      if (d.type === "dependency") return width * 0.25;
      if (d.type === "dependent") return width * 0.75;
      return width / 2;
    }).strength(0.5));
  
  // Draw links
  const link = svg.append("g")
    .selectAll("line")
    .data(links)
    .enter().append("line")
    .attr("stroke", "#999")
    .attr("stroke-width", 2);
  
  // Draw nodes
  const node = svg.append("g")
    .selectAll("circle")
    .data(nodes)
    .enter().append("circle")
    .attr("r", d => d.id === "company_root" ? 20 : 12)
    .attr("fill", d => {
      if (d.id === "company_root") return "#ff6b6b";
      if (d.type === "dependency") return "#4ecdc4";
      return "#45b7d1";
    })
    .on("mouseover", showTooltip)
    .on("mouseout", hideTooltip)
    .call(d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended));
  
  // Add labels
  const label = svg.append("g")
    .selectAll("text")
    .data(nodes)
    .enter().append("text")
    .text(d => d.name)
    .attr("font-size", "12px")
    .attr("dx", 15)
    .attr("dy", 4);
  
  // Tooltip
  const tooltip = d3.select("body").append("div")
    .attr("class", "tooltip")
    .style("opacity", 0)
    .style("position", "absolute")
    .style("background", "white")
    .style("border", "1px solid #ddd")
    .style("padding", "10px")
    .style("border-radius", "5px")
    .style("box-shadow", "0 2px 4px rgba(0,0,0,0.1)");
  
  function showTooltip(event, d) {
    let html = `<strong>${d.name}</strong><br/>`;
    if (d.relationship) html += `<em>${d.relationship}</em><br/>`;
    
    // Show news
    if (d.news && d.news.length > 0) {
      html += `<br/><strong>Latest News:</strong><br/>`;
      d.news.slice(0, 3).forEach(article => {
        html += `• <a href="${article.link}" target="_blank">${article.title}</a><br/>`;
      });
    }
    
    // Show market data
    if (d.market_data) {
      html += `<br/><strong>Market Data:</strong><br/>`;
      html += `Ticker: ${d.market_data.stock_ticker || 'N/A'}<br/>`;
      html += `Price: ${d.market_data.stock_price || 'N/A'}`;
    }
    
    tooltip.html(html)
      .style("left", (event.pageX + 10) + "px")
      .style("top", (event.pageY - 10) + "px")
      .style("opacity", 1);
  }
  
  function hideTooltip() {
    tooltip.style("opacity", 0);
  }
  
  // Update positions
  simulation.on("tick", () => {
    link
      .attr("x1", d => d.source.x)
      .attr("y1", d => d.source.y)
      .attr("x2", d => d.target.x)
      .attr("y2", d => d.target.y);
    
    node
      .attr("cx", d => d.x)
      .attr("cy", d => d.y);
    
    label
      .attr("x", d => d.x)
      .attr("y", d => d.y);
  });
  
  // Drag functions
  function dragstarted(event) {
    if (!event.active) simulation.alphaTarget(0.3).restart();
    event.subject.fx = event.subject.x;
    event.subject.fy = event.subject.y;
  }
  
  function dragged(event) {
    event.subject.fx = event.x;
    event.subject.fy = event.y;
  }
  
  function dragended(event) {
    if (!event.active) simulation.alphaTarget(0);
    event.subject.fx = null;
    event.subject.fy = null;
  }
}

// Usage
fetch('/api/knowledge-graph')
  .then(res => res.json())
  .then(data => renderKnowledgeGraph(data.knowledge_graph));
```

### React Component Example

```jsx
import React, { useEffect, useRef } from 'react';
import * as d3 from 'd3';

const KnowledgeGraphVisualization = ({ graphData }) => {
  const svgRef = useRef();
  
  useEffect(() => {
    if (!graphData) return;
    
    // Clear previous graph
    d3.select(svgRef.current).selectAll("*").remove();
    
    // Render using the function above
    renderKnowledgeGraph(graphData);
  }, [graphData]);
  
  return (
    <div>
      <h2>Dependency Knowledge Graph</h2>
      <div id="graph-container" ref={svgRef}></div>
    </div>
  );
};

export default KnowledgeGraphVisualization;
```

## API Response Format

### Success Response
```json
{
  "root": {
    "id": "company_root",
    "name": "NeuralTech AI",
    "type": "company",
    "description": "AI startup developing LLMs",
    "position": {"x": 0, "y": 0}
  },
  "nodes": [
    {
      "id": "dep_nvidia",
      "name": "NVIDIA",
      "type": "dependency",
      "category": "company",
      "position": {"x": -2, "y": 1},
      "relationship": "provides GPU infrastructure for AI training",
      "news": [
        {
          "title": "NVIDIA Q3 earnings beat expectations",
          "link": "https://...",
          "source": "Reuters",
          "date": "2024-10-14",
          "snippet": "..."
        }
      ],
      "market_data": {
        "stock_ticker": "NVDA",
        "stock_price": "$450.25",
        "52_week_high": "$502.66",
        "52_week_low": "$325.12"
      },
      "trade_data": {
        "india": "India imports $2.5B in semiconductors annually",
        "us": "Largest GPU manufacturer, 80% market share",
        "china": "Export restrictions on advanced AI chips"
      },
      "hover_info": "Critical GPU provider for AI/ML workloads"
    }
  ],
  "edges": [
    {
      "from": "company_root",
      "to": "dep_nvidia",
      "relationship": "depends on",
      "strength": 0.95
    }
  ],
  "metadata": {
    "total_dependencies": 8,
    "total_dependents": 6,
    "llm_processed": true,
    "model": "gemini-2.5-flash"
  }
}
```

### Error Response
```json
{
  "error": "Knowledge graph generation error: API key missing"
}
```

## Environment Variables

Required:
- `GEMINI_API_KEY`: For LLM-based structuring
- `PERPLEXITY_API_KEY`: For dependency analysis and market data
- `SERPAPI_API_KEY`: For news fetching

## Examples

See `examples/knowledge_graph_example.py` for complete examples:
- AI Company (GPU dependencies)
- Coffee Startup (commodity dependencies)
- Fintech (payment infrastructure dependencies)

## Best Practices

1. **Hover Information**: Keep it concise but informative
   - Entity name and relationship
   - Top 3-5 news headlines
   - Key market metrics
   
2. **Node Positioning**: 
   - Use force-directed layout for organic arrangement
   - Apply directional forces (left for deps, right for dependents)
   - Allow user to drag nodes for custom arrangement
   
3. **Performance**: 
   - Limit to 15-20 nodes for clarity
   - Lazy load detailed information on hover/click
   - Cache API responses
   
4. **Updates**:
   - Refresh news daily
   - Update stock prices in real-time or hourly
   - Regenerate graph when startup info changes

## Troubleshooting

### Issue: No dependencies identified
**Solution**: Ensure startup description includes:
- Technology stack
- Supply chain information
- Infrastructure details

### Issue: Missing market data
**Solution**: Check that:
- Entity names are correct (e.g., "NVIDIA" not "Nvidia GPUs")
- Perplexity API key is valid
- API rate limits not exceeded

### Issue: Graph looks cluttered
**Solution**: 
- Reduce number of nodes (limit to top 8 per side)
- Increase canvas size
- Implement collapsible node groups

## Future Enhancements

1. **Real-time Updates**: WebSocket connections for live stock/news
2. **Multi-level Graphs**: Expand nodes to show sub-dependencies
3. **Risk Scoring**: Color-code nodes based on dependency risk
4. **Time Series**: Show how dependencies change over time
5. **Geographic View**: Map view showing trade routes
6. **Sentiment Analysis**: Analyze news sentiment for each node

