from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from typing import Type, Dict, Any, List, Optional
import re
import json

class CodeAnalysisRequest(BaseModel):
    """Input schema for Code Analysis Tool."""
    code_snippet: Optional[str] = Field(None, description="The code snippet to analyze (optional)")
    requirements: str = Field(..., description="Description of what needs to be built or requirements")
    language: str = Field(..., description="Target programming language (e.g., Python, JavaScript, Java, etc.)")
    project_type: str = Field(..., description="Type of project (web app, API, script, mobile app, etc.)")

class CodeAnalysisTool(BaseTool):
    """Tool for analyzing code and providing improvement suggestions."""

    name: str = "Code Analysis and Improvement Tool"
    description: str = (
        "Analyzes provided code snippets and suggests improvements. Provides best practices "
        "recommendations for different programming languages, suggests code structure improvements "
        "and patterns, identifies potential issues, recommends libraries and frameworks, "
        "and generates code templates and boilerplate structures as text output."
    )
    args_schema: Type[BaseModel] = CodeAnalysisRequest

    def _analyze_code_snippet(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze a code snippet for potential improvements."""
        issues = []
        improvements = []
        
        language_lower = language.lower()
        
        # Generic code analysis patterns
        if len(code.split('\n')) > 100:
            issues.append("Code is quite long - consider breaking into smaller functions/methods")
        
        # Language-specific analysis
        if language_lower in ['python']:
            if 'import *' in code:
                issues.append("Avoid wildcard imports - use specific imports instead")
            if re.search(r'except:\s*$', code, re.MULTILINE):
                issues.append("Use specific exception handling instead of bare except clauses")
            if 'global ' in code:
                issues.append("Consider avoiding global variables - use function parameters or class attributes")
            if not re.search(r'def \w+\([^)]*\):', code) and len(code.split('\n')) > 10:
                improvements.append("Consider organizing code into functions for better readability")
                
        elif language_lower in ['javascript', 'js']:
            if 'var ' in code:
                improvements.append("Consider using 'let' or 'const' instead of 'var' for better scoping")
            if '==' in code:
                improvements.append("Consider using '===' for strict equality comparison")
            if 'function(' in code and 'arrow' not in code:
                improvements.append("Consider using arrow functions for cleaner syntax where appropriate")
                
        elif language_lower in ['java']:
            if not re.search(r'public class \w+', code):
                improvements.append("Ensure proper class structure with access modifiers")
            if 'System.out.println' in code and 'main' not in code:
                improvements.append("Consider using a logging framework instead of System.out.println")
                
        # Check for common patterns
        if re.search(r'password|secret|key', code, re.IGNORECASE):
            issues.append("Potential hardcoded credentials detected - use environment variables or config files")
            
        if len(re.findall(r'if\s*\(.*\)\s*{', code)) > 5:
            improvements.append("Consider refactoring complex conditional logic into separate methods")
            
        return {
            "issues": issues,
            "improvements": improvements
        }

    def _get_best_practices(self, language: str, project_type: str) -> List[str]:
        """Get best practices for specific language and project type."""
        practices = []
        language_lower = language.lower()
        project_lower = project_type.lower()
        
        # Language-specific best practices
        if language_lower == 'python':
            practices.extend([
                "Follow PEP 8 style guidelines",
                "Use virtual environments for dependency management",
                "Write docstrings for functions and classes",
                "Use type hints for better code clarity",
                "Implement proper error handling with specific exceptions",
                "Use list comprehensions and generator expressions when appropriate"
            ])
            
        elif language_lower in ['javascript', 'js']:
            practices.extend([
                "Use strict mode ('use strict')",
                "Implement proper error handling with try/catch",
                "Use modern ES6+ features appropriately",
                "Implement proper async/await patterns",
                "Use meaningful variable and function names",
                "Avoid callback hell with promises or async/await"
            ])
            
        elif language_lower == 'java':
            practices.extend([
                "Follow Java naming conventions",
                "Use interfaces for abstraction",
                "Implement proper exception handling",
                "Use generics for type safety",
                "Follow SOLID principles",
                "Use proper access modifiers"
            ])
            
        # Project-type specific practices
        if 'web' in project_lower:
            practices.extend([
                "Implement proper input validation and sanitization",
                "Use HTTPS for secure communication",
                "Implement proper session management",
                "Follow RESTful API design principles"
            ])
            
        elif 'api' in project_lower:
            practices.extend([
                "Implement proper API versioning",
                "Use appropriate HTTP status codes",
                "Implement rate limiting",
                "Provide comprehensive API documentation",
                "Use proper authentication and authorization"
            ])
            
        return practices

    def _get_recommended_libraries(self, language: str, project_type: str, requirements: str) -> Dict[str, List[str]]:
        """Get recommended libraries and frameworks."""
        recommendations = {"frameworks": [], "libraries": [], "tools": []}
        language_lower = language.lower()
        project_lower = project_type.lower()
        req_lower = requirements.lower()
        
        if language_lower == 'python':
            if 'web' in project_lower or 'api' in project_lower:
                recommendations["frameworks"].extend(["FastAPI", "Flask", "Django"])
                recommendations["libraries"].extend(["requests", "pydantic", "sqlalchemy"])
            
            if 'data' in req_lower or 'analysis' in req_lower:
                recommendations["libraries"].extend(["pandas", "numpy", "matplotlib", "seaborn"])
                
            if 'test' in req_lower:
                recommendations["libraries"].extend(["pytest", "unittest", "mock"])
                
            recommendations["tools"].extend(["black (formatting)", "flake8 (linting)", "mypy (type checking)"])
            
        elif language_lower in ['javascript', 'js']:
            if 'web' in project_lower:
                recommendations["frameworks"].extend(["React", "Vue.js", "Angular"])
                recommendations["libraries"].extend(["axios", "lodash", "moment.js"])
                
            if 'api' in project_lower or 'backend' in project_lower:
                recommendations["frameworks"].extend(["Express.js", "Fastify", "Koa.js"])
                
            if 'test' in req_lower:
                recommendations["libraries"].extend(["Jest", "Mocha", "Cypress"])
                
            recommendations["tools"].extend(["ESLint (linting)", "Prettier (formatting)", "Webpack (bundling)"])
            
        elif language_lower == 'java':
            if 'web' in project_lower or 'api' in project_lower:
                recommendations["frameworks"].extend(["Spring Boot", "Spring MVC", "Quarkus"])
                
            if 'test' in req_lower:
                recommendations["libraries"].extend(["JUnit", "Mockito", "TestNG"])
                
            recommendations["tools"].extend(["Maven/Gradle (build)", "SonarQube (code quality)", "SpotBugs (static analysis)"])
            
        return recommendations

    def _get_architecture_suggestions(self, project_type: str, requirements: str) -> List[str]:
        """Get architecture suggestions based on project type and requirements."""
        suggestions = []
        project_lower = project_type.lower()
        req_lower = requirements.lower()
        
        # General architecture patterns
        suggestions.append("Follow separation of concerns principle")
        suggestions.append("Implement proper error handling and logging")
        suggestions.append("Use dependency injection for better testability")
        
        if 'api' in project_lower:
            suggestions.extend([
                "Implement layered architecture (Controller, Service, Repository)",
                "Use DTO/VO patterns for data transfer",
                "Implement proper validation at API boundaries",
                "Consider implementing CQRS pattern for complex operations"
            ])
            
        elif 'web' in project_lower:
            suggestions.extend([
                "Use MVC or MVP pattern",
                "Implement proper state management",
                "Use component-based architecture",
                "Implement proper routing structure"
            ])
            
        if 'database' in req_lower:
            suggestions.extend([
                "Use repository pattern for data access",
                "Implement proper database connection pooling",
                "Consider using ORM for database operations"
            ])
            
        if 'scale' in req_lower or 'large' in req_lower:
            suggestions.extend([
                "Consider microservices architecture",
                "Implement proper caching strategy",
                "Use event-driven architecture where appropriate",
                "Consider implementing Circuit Breaker pattern"
            ])
            
        return suggestions

    def _get_security_considerations(self, language: str, project_type: str) -> List[str]:
        """Get security considerations for the project."""
        security = []
        project_lower = project_type.lower()
        
        # General security practices
        security.extend([
            "Never hardcode sensitive information (passwords, API keys)",
            "Use environment variables for configuration",
            "Implement proper input validation and sanitization",
            "Use secure communication protocols (HTTPS/TLS)"
        ])
        
        if 'web' in project_lower or 'api' in project_lower:
            security.extend([
                "Implement proper authentication and authorization",
                "Protect against common vulnerabilities (XSS, CSRF, SQL injection)",
                "Use secure session management",
                "Implement rate limiting to prevent abuse",
                "Validate and sanitize all user inputs",
                "Use CORS properly for cross-origin requests"
            ])
            
        if 'database' in project_lower:
            security.extend([
                "Use parameterized queries to prevent SQL injection",
                "Implement proper database access controls",
                "Encrypt sensitive data at rest"
            ])
            
        return security

    def _generate_code_template(self, language: str, project_type: str, requirements: str) -> str:
        """Generate a basic code template structure."""
        language_lower = language.lower()
        project_lower = project_type.lower()
        
        template = f"# {project_type.title()} Template for {language.title()}\n\n"
        
        if language_lower == 'python':
            if 'api' in project_lower:
                template += """# FastAPI Example Structure
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI(title="Your API", version="1.0.0")

class ItemModel(BaseModel):
    name: str
    description: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    # Implement your logic here
    return {"item_id": item_id}

@app.post("/items/")
async def create_item(item: ItemModel):
    # Implement creation logic
    return item

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
"""
            elif 'script' in project_lower:
                template += """# Python Script Template
import argparse
import logging
import sys
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def main(args: argparse.Namespace) -> None:
    \"\"\"Main function to implement your logic.\"\"\"
    try:
        # Implement your main logic here
        logger.info("Script started")
        # Your code here
        logger.info("Script completed successfully")
    except Exception as e:
        logger.error(f"Script failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Your script description")
    parser.add_argument("--input", help="Input parameter", required=True)
    parser.add_argument("--output", help="Output parameter", default="output.txt")
    
    args = parser.parse_args()
    main(args)
"""
                
        elif language_lower in ['javascript', 'js']:
            if 'web' in project_lower:
                template += """// React Component Template
import React, { useState, useEffect } from 'react';

const YourComponent = () => {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch data on component mount
    const fetchData = async () => {
      try {
        const response = await fetch('/api/data');
        const result = await response.json();
        setData(result);
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h1>Your Component</h1>
      {/* Render your component here */}
    </div>
  );
};

export default YourComponent;
"""
            elif 'api' in project_lower:
                template += """// Express.js API Template
const express = require('express');
const cors = require('cors');
const helmet = require('helmet');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Routes
app.get('/', (req, res) => {
  res.json({ message: 'Hello World!' });
});

app.get('/api/items/:id', (req, res) => {
  try {
    const { id } = req.params;
    // Implement your logic here
    res.json({ id, message: 'Item retrieved' });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

app.post('/api/items', (req, res) => {
  try {
    const data = req.body;
    // Implement creation logic
    res.status(201).json({ message: 'Item created', data });
  } catch (error) {
    res.status(400).json({ error: error.message });
  }
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
"""
                
        return template

    def _run(self, code_snippet: Optional[str], requirements: str, language: str, project_type: str) -> str:
        """Run the code analysis and return structured recommendations."""
        try:
            analysis_result = {
                "analysis_summary": f"Code analysis for {language} {project_type} project",
                "requirements": requirements
            }
            
            # Analyze code snippet if provided
            if code_snippet:
                code_analysis = self._analyze_code_snippet(code_snippet, language)
                analysis_result["code_analysis"] = {
                    "issues_found": code_analysis["issues"],
                    "improvement_suggestions": code_analysis["improvements"]
                }
            else:
                analysis_result["code_analysis"] = {
                    "note": "No code snippet provided for analysis"
                }
            
            # Get recommendations
            analysis_result["best_practices"] = self._get_best_practices(language, project_type)
            analysis_result["architecture_suggestions"] = self._get_architecture_suggestions(project_type, requirements)
            analysis_result["recommended_libraries"] = self._get_recommended_libraries(language, project_type, requirements)
            analysis_result["security_considerations"] = self._get_security_considerations(language, project_type)
            analysis_result["code_template"] = self._generate_code_template(language, project_type, requirements)
            
            # Format the output as a readable string
            output = f"""
# Code Analysis Report for {language.title()} {project_type.title()}

## Requirements
{requirements}

## Code Analysis
"""
            
            if code_snippet:
                output += f"""
### Issues Found:
{chr(10).join('• ' + issue for issue in analysis_result["code_analysis"]["issues_found"]) if analysis_result["code_analysis"]["issues_found"] else '• No major issues detected'}

### Improvement Suggestions:
{chr(10).join('• ' + improvement for improvement in analysis_result["code_analysis"]["improvement_suggestions"]) if analysis_result["code_analysis"]["improvement_suggestions"] else '• No specific improvements suggested'}
"""
            else:
                output += "\n• No code snippet provided for analysis\n"
            
            output += f"""
## Best Practices
{chr(10).join('• ' + practice for practice in analysis_result["best_practices"])}

## Architecture Suggestions
{chr(10).join('• ' + suggestion for suggestion in analysis_result["architecture_suggestions"])}

## Recommended Libraries & Frameworks
### Frameworks:
{chr(10).join('• ' + framework for framework in analysis_result["recommended_libraries"]["frameworks"]) if analysis_result["recommended_libraries"]["frameworks"] else '• No specific frameworks recommended'}

### Libraries:
{chr(10).join('• ' + library for library in analysis_result["recommended_libraries"]["libraries"]) if analysis_result["recommended_libraries"]["libraries"] else '• No specific libraries recommended'}

### Development Tools:
{chr(10).join('• ' + tool for tool in analysis_result["recommended_libraries"]["tools"]) if analysis_result["recommended_libraries"]["tools"] else '• No specific tools recommended'}

## Security Considerations
{chr(10).join('• ' + security for security in analysis_result["security_considerations"])}

## Code Structure Template

```{language.lower()}
{analysis_result["code_template"]}

---
This analysis provides guidance for building a {project_type} in {language}. Implement these recommendations gradually and adapt them to your specific use case.
"""
            
            return output
            
        except Exception as e:
            return f"Error during code analysis: {str(e)}"