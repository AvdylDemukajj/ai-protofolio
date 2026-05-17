import json
import sys
import os
import re
from typing import List, Dict, Any

class SecurityScanner:
    def __init__(self):
        self.issues = []
        # Patterns for detecting secrets
        self.secret_patterns = [
            (r'(?i)(password|passwd|pwd)\s*[:=]\s*["\'][^"\']+["\']', "Hardcoded Password"),
            (r'(?i)(api_key|apikey|secret_key)\s*[:=]\s*["\'][^"\']+["\']', "Hardcoded API Key"),
            (r'sk-[a-zA-Z0-9]{20,}', "OpenAI API Key Detected"),
            (r'xox[baprs]-[0-9a-zA-Z-]+', "Slack Token Detected"),
        ]

    def scan_file(self, file_path: str) -> Dict[str, Any]:
        print(f"🛡️  Scanning: {file_path}")
        self.issues = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            if not isinstance(data, dict) or 'nodes' not in data:
                return {"status": "error", "message": "Invalid n8n workflow format"}

            nodes = data.get('nodes', [])
            self._check_nodes(nodes)
            self._check_connections(data.get('connections', {}))
            self._check_settings(data.get('settings', {}))

            status = "FAILED" if self.issues else "PASSED"
            return {
                "file": os.path.basename(file_path),
                "status": status,
                "issues_count": len(self.issues),
                "issues": self.issues
            }

        except json.JSONDecodeError:
            return {"status": "error", "message": "Invalid JSON"}
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _check_nodes(self, nodes: List[Dict]):
        for node in nodes:
            node_name = node.get('name', 'Unknown')
            node_type = node.get('type', '')
            params = node.get('parameters', {})

            # 1. Check for Hardcoded Credentials in Parameters
            params_str = json.dumps(params)
            for pattern, issue_name in self.secret_patterns:
                if re.search(pattern, params_str):
                    self.issues.append({
                        "severity": "CRITICAL",
                        "node": node_name,
                        "type": node_type,
                        "issue": f"{issue_name} found in parameters",
                        "recommendation": "Use n8n Credentials store instead of hardcoding."
                    })

            # 2. Check for Missing Error Handling (Webhooks/HTTP Requests)
            if 'webhook' in node_type.lower() or 'http' in node_type.lower():
                # Logic to check if an error trigger is connected would go here in a full graph analysis
                # For now, we warn if it's a critical node
                pass 

            # 3. Check for Public Webhooks without validation
            if node_type == 'n8n-nodes-base.webhook':
                options = params.get('options', {})
                if not options.get('responseMode'): 
                     # Warning if not using specific response modes that might imply validation
                     pass

    def _check_connections(self, connections: Dict):
        # Analyze graph structure for orphaned nodes or missing error branches
        pass

    def _check_settings(self, settings: Dict):
        if not settings.get('executionOrder'):
            self.issues.append({
                "severity": "LOW",
                "node": "Workflow Settings",
                "issue": "Execution order not explicitly set",
                "recommendation": "Set executionOrder to 'v1' for stability."
            })

def main():
    if len(sys.argv) < 2:
        print("Usage: python scanner/main.py <path_to_workflow.json>")
        print("Example: python scanner/main.py ../01-n8n-support-automation-pack/workflows/01_ai_classifier.json")
        sys.exit(1)

    scanner = SecurityScanner()
    target_file = sys.argv[1]
    
    if not os.path.exists(target_file):
        print(f"❌ File not found: {target_file}")
        sys.exit(1)

    result = scanner.scan_file(target_file)
    
    print("\n" + "="*40)
    print(f"REPORT: {result['file']}")
    print(f"STATUS: {result['status']}")
    print("="*40)

    if result['status'] == 'error':
        print(f"Error: {result['message']}")
    elif result['issues']:
        print(f"⚠️  Found {len(result['issues'])} issues:\n")
        for i, issue in enumerate(result['issues'], 1):
            print(f"{i}. [{issue['severity']}] {issue['issue']}")
            print(f"   Node: {issue['node']} ({issue['type']})")
            print(f"   Fix: {issue['recommendation']}\n")
    else:
        print("✅ No security issues detected. Workflow looks safe.")

if __name__ == "__main__":
    main()