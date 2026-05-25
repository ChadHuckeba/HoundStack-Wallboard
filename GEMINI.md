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
Wallboard is a single-screen Meet and Greet display tool for Rover pet care sessions. It presents dog profile information, daily care schedules, discussion topics, and host details to pet owners during intake meetings. The non-negotiable UI constraint is single-screen integrity — zero scrolling, zero overflow at all times.

## 2.0 ARCHITECTURAL DECISIONS

### 2.1 Aesthetic Supremacy
All UI components MUST adhere to the **HoundStack Aesthetic Standard**: high-contrast, professional, and optimized for CLI-first operators. Consistency in spacing and typography is non-negotiable.

### 2.2 Telemetry Integration
All logging MUST use Cairn initialized via cairn.initialize(). Raw print() statements are prohibited. Log files are stored in logs/ per the SurvivalStack logging standard.

### 2.3 Deployment Constraints
*   **Zero-Cost Local:** Wallboard is designed for local-first deployment. No paid cloud services are authorized without explicit security review.

## 3.0 TROUBLESHOOTING
*   **Ingestion Lag:** Verify Cairn project tag accuracy in \`registry.json\`.
*   **UI Artifacts:** Force-clear browser cache and verify CSS source injection.
