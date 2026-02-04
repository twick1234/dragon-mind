# Legacy Code Modernization Plan

**Author:** CustomerChu 🐉  
**Date:** 2026-02-04  
**Status:** Proposal  
**Requested by:** J

---

## 1. Problem Statement

J has large legacy Java repositories that need to be:
1. **Documented** - Understand what exists
2. **Modernized** - Rewrite in React + SpringBoot
3. **Business Logic Preserved** - Critical requirement

### Current State
- Huge repos, impossible to read manually
- TreeSitter + Python scripts already extract:
  - Class/method metadata
  - Full stack call graphs
  - Dependencies

### Challenge
How to use AI agents effectively to understand and modernize while preserving business logic?

---

## 2. Proposed Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 LEGACY MODERNIZATION PIPELINE                │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐     ┌──────────────┐     ┌─────────────┐  │
│  │   LEGACY     │     │  KNOWLEDGE   │     │  MODERN     │  │
│  │   CODEBASE   │────►│    GRAPH     │────►│  CODEBASE   │  │
│  │   (Java)     │     │   (Brain)    │     │(React/Spring)│  │
│  └──────────────┘     └──────────────┘     └─────────────┘  │
│         │                    │                    │          │
│         ▼                    ▼                    ▼          │
│  ┌──────────────┐     ┌──────────────┐     ┌─────────────┐  │
│  │  TreeSitter  │     │    Agents    │     │   Tests     │  │
│  │   Extract    │     │   Analyze    │     │  Validate   │  │
│  └──────────────┘     └──────────────┘     └─────────────┘  │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Phase 1: Ingest Legacy Code to Knowledge Graph

### 3.1 Data to Ingest

| Entity | Source | Purpose |
|--------|--------|---------|
| Classes | TreeSitter | Structure understanding |
| Methods | TreeSitter | Function inventory |
| Call Graph | TreeSitter | Dependency mapping |
| Business Rules | Code comments + patterns | Logic preservation |
| Database Queries | SQL extraction | Data model understanding |
| API Endpoints | Annotation parsing | Interface contracts |
| Config Files | File parsing | Environment setup |

### 3.2 Knowledge Graph Schema Extension

```javascript
// Add to @chu-collective/knowledge-graph

// Legacy code entities
store.legacy.addClass({ 
  name: 'PaymentService',
  package: 'com.example.payment',
  file: 'src/main/java/...',
  methods: ['process', 'validate', 'refund'],
  annotations: ['@Service'],
  dependencies: ['OrderService', 'BankGateway']
});

store.legacy.addMethod({
  class: 'PaymentService',
  name: 'process',
  params: ['Order order', 'PaymentMethod method'],
  returns: 'PaymentResult',
  calls: ['validate', 'BankGateway.charge', 'OrderService.markPaid'],
  businessLogic: 'Processes payment, validates amount, charges bank, updates order'
});

store.legacy.addCallEdge({
  from: 'PaymentService.process',
  to: 'BankGateway.charge',
  type: 'sync'
});

store.legacy.addBusinessRule({
  id: 'BR-001',
  description: 'Orders over $10000 require manager approval',
  location: 'PaymentService.validate:45',
  logic: 'if (order.amount > 10000) requireApproval()'
});
```

### 3.3 Ingestion Script

```javascript
// bin/ingest-legacy.js
const kg = require('@chu-collective/knowledge-graph');
const treesitterOutput = require('./treesitter-output.json');

const store = kg.create('./legacy-knowledge.db');

// Ingest classes
for (const cls of treesitterOutput.classes) {
  store.legacy.addClass(cls);
}

// Ingest methods
for (const method of treesitterOutput.methods) {
  store.legacy.addMethod(method);
}

// Ingest call graph
for (const edge of treesitterOutput.callGraph) {
  store.legacy.addCallEdge(edge);
}

console.log(`Ingested ${store.legacy.stats()}`);
```

---

## 4. Phase 2: AI-Assisted Documentation

### 4.1 Agent Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                 DOCUMENTATION WORKFLOW                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. ChuScout queries KG for module boundaries               │
│     └──► Identifies domains: Payment, Order, User, etc.     │
│                                                              │
│  2. ChuMemory generates docs for each domain                │
│     └──► README, class diagrams, sequence diagrams          │
│                                                              │
│  3. ChuCoder identifies patterns & anti-patterns            │
│     └──► Technical debt inventory                           │
│                                                              │
│  4. Human reviews & validates                               │
│     └──► Confirms business logic understanding              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 4.2 Query Examples

```javascript
// What does PaymentService depend on?
store.query(`
  MATCH (PaymentService)-[:CALLS]->(dep)
  RETURN dep.name, count(*) as calls
  ORDER BY calls DESC
`);

// What business rules exist in Order domain?
store.legacy.businessRules({ domain: 'Order' });

// Draw call graph for checkout flow
store.legacy.callGraph({ 
  entryPoint: 'CheckoutController.submit',
  depth: 5,
  format: 'mermaid'
});
```

### 4.3 Generated Documentation

```markdown
# Payment Domain

## Overview
The Payment domain handles all payment processing for orders.

## Key Classes
- PaymentService - Main payment orchestrator
- BankGateway - External bank integration
- PaymentValidator - Business rule validation

## Business Rules
- BR-001: Orders over $10000 require manager approval
- BR-002: Failed payments trigger 3 retry attempts
- BR-003: Refunds must be processed within 30 days

## Call Flow (Mermaid)
sequenceDiagram
    CheckoutController->>PaymentService: process(order)
    PaymentService->>PaymentValidator: validate(order)
    PaymentService->>BankGateway: charge(amount)
    BankGateway-->>PaymentService: PaymentResult
    PaymentService->>OrderService: markPaid(orderId)
```

---

## 5. Phase 3: Modernization

### 5.1 Mapping Strategy

| Legacy (Java) | Modern (React + SpringBoot) |
|---------------|----------------------------|
| JSP Pages | React Components |
| Servlets | REST Controllers |
| EJB Services | Spring Services |
| JDBC | Spring Data JPA |
| XML Config | YAML + Annotations |

### 5.2 Business Logic Extraction

**Critical:** Extract business rules as testable specifications BEFORE rewriting.

```javascript
// Extract business rules as test specs
store.legacy.businessRules().forEach(rule => {
  generateTestSpec(rule);
});

// Output: test/business-rules/BR-001.test.js
describe('BR-001: Orders over $10000 require manager approval', () => {
  it('should require approval for large orders', () => {
    const order = { amount: 15000 };
    expect(paymentService.requiresApproval(order)).toBe(true);
  });
  
  it('should not require approval for small orders', () => {
    const order = { amount: 5000 };
    expect(paymentService.requiresApproval(order)).toBe(false);
  });
});
```

### 5.3 Modernization Workflow

```
1. Extract business rule as test
2. Write new implementation (React/SpringBoot)
3. Run test - must pass
4. Compare behavior with legacy
5. Human validates
6. Mark rule as migrated in KG
```

---

## 6. Tools Needed

### 6.1 Knowledge Graph Extensions
- Legacy code schema (classes, methods, calls)
- Business rule extraction
- Migration tracking

### 6.2 Ingestion Tools
- TreeSitter output parser
- Call graph builder
- Business rule detector (pattern matching)

### 6.3 Documentation Generators
- Mermaid diagram generator
- README generator
- API spec generator

### 6.4 Migration Tools
- Test spec generator
- Code scaffold generator
- Behavior comparison tool

---

## 7. Success Metrics

| Metric | Target |
|--------|--------|
| Code coverage in KG | 100% of classes |
| Business rules captured | All critical rules |
| Documentation generated | All domains |
| Tests generated | All business rules |
| Migration validation | Zero behavior changes |

---

## 8. Next Steps

1. **Validate approach with J** - Does this make sense?
2. **Get sample TreeSitter output** - Understand format
3. **Extend KG schema** - Add legacy code entities
4. **Build ingestion script** - Load one repo as POC
5. **Test with one module** - Document → Modernize → Validate

---

*Built for legacy modernization by the Chu Collective* 🐉
