// Extract and display diagrams from project analysis files
class DiagramExtractor {
    static extractDiagramsFromMarkdown(markdown) {
        const diagrams = [];
        const xmlRegex = /```xml\s*([\s\S]*?)\s*```/g;
        let match;
        
        while ((match = xmlRegex.exec(markdown)) !== null) {
            const xmlContent = match[1].trim();
            if (xmlContent.includes('<diagram>') || xmlContent.includes('<mxfile>')) {
                diagrams.push({
                    type: 'drawio',
                    content: xmlContent,
                    title: this.extractDiagramTitle(markdown, match.index)
                });
            }
        }
        
        return diagrams;
    }
    
    static extractDiagramTitle(markdown, xmlIndex) {
        // Look for heading before the XML block
        const beforeXml = markdown.substring(0, xmlIndex);
        const headingMatch = beforeXml.match(/#{1,6}\s*([^\n]+)\s*$/m);
        return headingMatch ? headingMatch[1].trim() : 'System Diagram';
    }
    
    static renderDiagram(xmlContent, containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;
        
        try {
            // Parse XML and extract components
            const parser = new DOMParser();
            const xmlDoc = parser.parseFromString(xmlContent, 'text/xml');
            
            // Extract nodes and create visual representation
            const nodes = xmlDoc.querySelectorAll('node');
            const edges = xmlDoc.querySelectorAll('edge');
            
            let diagramHtml = '<div class="diagram-container">';
            
            // Render nodes
            nodes.forEach((node, index) => {
                const label = node.querySelector('label')?.textContent || `Component ${index + 1}`;
                diagramHtml += `
                    <div class="diagram-node" style="position: relative; display: inline-block; margin: 10px;">
                        <div class="node-box">
                            ${label}
                        </div>
                    </div>
                `;
            });
            
            diagramHtml += '</div>';
            container.innerHTML = diagramHtml;
            
        } catch (error) {
            console.error('Error rendering diagram:', error);
            container.innerHTML = `
                <div class="diagram-error">
                    <p>Unable to render diagram</p>
                    <details>
                        <summary>Raw XML</summary>
                        <pre>${xmlContent}</pre>
                    </details>
                </div>
            `;
        }
    }
}

// Add diagram styles
const diagramStyles = `
    .diagram-container {
        padding: 20px;
        background: #f8f9fa;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    .diagram-node {
        margin: 10px;
    }
    
    .node-box {
        padding: 12px 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 8px;
        font-weight: bold;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        text-align: center;
        min-width: 120px;
    }
    
    .diagram-error {
        padding: 20px;
        background: #f8d7da;
        border: 1px solid #f5c6cb;
        border-radius: 6px;
        color: #721c24;
    }
    
    .diagram-error pre {
        background: #fff;
        padding: 10px;
        border-radius: 4px;
        overflow-x: auto;
        font-size: 12px;
        margin-top: 10px;
    }
`;

// Inject styles
const styleSheet = document.createElement('style');
styleSheet.textContent = diagramStyles;
document.head.appendChild(styleSheet);