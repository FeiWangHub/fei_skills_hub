---
name: dependency-upgrade
description: Manage major dependency version upgrades with compatibility analysis, staged rollout, and comprehensive testing. Use when upgrading framework versions, updating major dependencies, or managing breaking changes in libraries.
---
# Dependency Upgrade
Master major dependency version upgrades, compatibility analysis, staged upgrade strategies, and comprehensive testing approaches.
## When to Use This Skill
- Upgrading major framework versions
- Updating security-vulnerable dependencies
- Modernizing legacy dependencies
- Resolving dependency conflicts
- Planning incremental upgrade paths
- Testing compatibility matrices
- Automating dependency updates
## Semantic Versioning Review
```
MAJOR.MINOR.PATCH (e.g., 2.3.1)
MAJOR: Breaking changes
MINOR: New features, backward compatible
PATCH: Bug fixes, backward compatible
^2.3.1 = >=2.3.1 <3.0.0 (minor updates)
~2.3.1 = >=2.3.1 <2.4.0 (patch updates)
2.3.1 = exact version
```
## Dependency Analysis
### Audit Dependencies
```bash
# npm
npm outdated
npm audit
npm audit fix
# yarn
yarn outdated
yarn audit
# Check for major updates
npx npm-check-updates
npx npm-check-updates -u # Update package.json
```
### Analyze Dependency Tree
```bash
# See why a package is installed
npm ls package-name
yarn why package-name
# Find duplicate packages
npm dedupe
yarn dedupe
# Visualize dependencies
npx madge --image graph.png src/
```
## Compatibility Matrix
```javascript
const compatibilityMatrix = {
  react: {
    "16.x": {
      "react-dom": "^16.0.0",
      "react-router-dom": "^5.0.0",
      "@testing-library/react": "^11.0.0",
    },
    "17.x": {
      "react-dom": "^17.0.0",
      "react-router-dom": "^5.0.0 || ^6.0.0",
      "@testing-library/react": "^12.0.0",
    },
    "18.x": {
      "react-dom": "^18.0.0",
      "react-router-dom": "^6.0.0",
      "@testing-library/react": "^13.0.0",
    },
  },
};
```
## Staged Upgrade Strategy
### Phase 1: Planning
```bash
# 1. Identify current versions
npm list --depth=0
# 2. Check for breaking changes
# Read CHANGELOG.md and MIGRATION.md
# 3. Create upgrade plan
echo "Upgrade order:
1. TypeScript
2. React
3. React Router
4. Testing libraries
5. Build tools" > UPGRADE_PLAN.md
```
### Phase 2: Incremental Updates
```bash
# Don't upgrade everything at once!
# Step 1: Update TypeScript
npm install typescript@latest
# Test
npm run test
npm run build
# Step 2: Update React (one major version at a time)
npm install react@17 react-dom@17
# Test again
npm run test
# Step 3: Continue with other packages
npm install react-router-dom@6
```
### Phase 3: Validation
```javascript
describe("Dependency Compatibility", () => {
  it("should have compatible React versions", () => {
    const reactVersion = require("react/package.json").version;
    const reactDomVersion = require("react-dom/package.json").version;
    expect(reactVersion).toBe(reactDomVersion);
  });
  it("should not have peer dependency warnings", () => {
    // Run npm ls and check for warnings
  });
});
```
## Breaking Change Handling
### Identifying Breaking Changes
```bash
curl https://raw.githubusercontent.com/facebook/react/master/CHANGELOG.md
```
### Codemod for Automated Fixes
```bash
npx jscodeshift -t <transform-url> <path>
npx jscodeshift -t https://raw.githubusercontent.com/reactjs/react-codemod/master/transforms/rename-unsafe-lifecycles.js src/
npx jscodeshift -t https://raw.githubusercontent.com/reactjs/react-codemod/master/transforms/rename-unsafe-lifecycles.js --parser=tsx src/
npx jscodeshift -t <transform-url> --dry src/
```
## Testing Strategy
### Unit Tests
```bash
npm run test
npm install @testing-library/react@latest
```
### Integration Tests
```javascript
describe("App Integration", () => {
  it("should render without crashing", () => {
    render(<App />);
  });
  it("should handle navigation", () => {
    const { getByText } = render(<App />);
    fireEvent.click(getByText("Navigate"));
    expect(screen.getByText("New Page")).toBeInTheDocument();
  });
});
```
### Visual Regression Tests
```bash
npx playwright test --ui
npx percy snapshot .
```
## Automated Dependency Management
### Renovate Config
```json
{
  "extends": ["config:base"],
  "major": { "enabled": true },
  "minor": { "enabled": true },
  "patch": { "enabled": false },
  "labels": ["dependencies", "automated"]
}
```
### Dependabot Config
```yaml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    major:
      update: "minor"
```
## Rollback Procedures
```bash
# Rollback to previous versions
npm install react@16 react-dom@16
# Check git status
git status
# Revert package.json changes if needed
git checkout package.json package-lock.json
npm install
```
