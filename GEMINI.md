# WALLBOARD: ARCHITECTURAL SOURCE OF TRUTH
*Governs project-specific architecture, localized mandates, and strategic intent. Procedural execution is delegated to specialized SKILLS.*

### Architecture at a Glance
| Component | Purpose | Role |
| :--- | :--- | :--- |
| **Policy** | This file (\`GEMINI.md\`) | **Supreme Authority** |
| **Memory** | \`MEMORY.md\` | Persistent State |
| **Docs** | \`/docs/\` | Functional Specs |

### Precedence Statement
**Global Policy (Ecosystem) > Project Policy (Local).** This file may add project-specific specificity but cannot contradict Global mandates. In this repository, \`/docs\` expands upon the architectural truth established in \`GEMINI.md\`, but \`GEMINI.md\` retains highest precedence for autonomous mandates.

---

## 1. Project Architecture & Constraints

### 1.1 The Wallboard Mandate
Wallboard is the primary visualization and monitoring hub for the HoundStack. It provides real-time telemetry and management interfaces for all PUP (Personal Utility Platform) services.

## 2.0 ARCHITECTURAL DECISIONS

### 2.1 Aesthetic Supremacy
All UI components MUST adhere to the **HoundStack Aesthetic Standard**: high-contrast, professional, and optimized for CLI-first operators. Consistency in spacing and typography is non-negotiable.

### 2.2 Telemetry Integration
*   **Mandate:** All Puppy (Puppeteer) services MUST feed telemetry to the Wallboard ingestion API.
*   **Standard:** Raw puppy logs are intercepted by Cairn and forwarded to Wallboard for visualization.

### 2.3 Deployment Constraints
*   **Zero-Cost Local:** Wallboard is designed for local-first deployment. No paid cloud services are authorized for Puppeteer orchestration without explicit security review.

## 3.0 TROUBLESHOOTING
*   **Ingestion Lag:** Verify Cairn project tag accuracy in \`registry.json\`.
*   **UI Artifacts:** Force-clear browser cache and verify CSS source injection.
