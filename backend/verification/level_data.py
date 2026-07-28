"""Level-based requirement definitions for AI consulting document verification.

11 Levels (A-K) with document-specific keyword verification.
Level unlock: all documents in current level must pass verification.

Each level contains:
  - description: What this level covers
  - must_include: Required items that MUST be present for level completion
  - recommended: Suggested items that strengthen the deliverable
  - key_prompts: AI prompts to help gather/validate information
"""

LEVEL_REQUIREMENTS = {
    1: {
        "title": "Discovery & Evaluation",
        "icon": "search",
        "color": "emerald",
        "description": "Clear articulation of business goals, stakeholder alignment, and measurable success criteria. Establish the foundation for the entire engagement by identifying problems, opportunities, and expected outcomes.",
        "must_include": [
            "Executive vision and project sponsor identification",
            "Problem statement with quantified business impact",
            "Success metrics and KPIs with measurable targets",
            "Department or business unit owner",
            "Current state pain points and process gaps",
            "Feasibility and preliminary ROI assessment",
        ],
        "recommended": [
            "Strategic context and alignment to corporate objectives",
            "KPI measurement framework with data collection plan",
            "Stakeholder influence/interest matrix",
            "Competitive or industry benchmarking data",
            "Quick-win identification for early value delivery",
        ],
        "key_prompts": [
            "Who is the executive sponsor and what business outcome do they expect?",
            "What specific problem are we solving and what is the cost of inaction?",
            "What KPIs will define success and how will they be measured?",
            "Which departments are affected and who are the key stakeholders?",
            "What data sources are available and what are the data quality gaps?",
            "What is the expected ROI timeline and confidence level?",
        ],
        "required_documents": [
            {
                "doc_type": "USE_CASE",
                "label": "Use Cases",
                "keywords": [
                    "problem statement", "expected outcomes", "department owner",
                    "data sources", "pain points", "current process gaps",
                    "use case", "business objective",
                ],
            },
            {
                "doc_type": "EVAL_SHEET",
                "label": "Use Case Evaluation Sheet",
                "keywords": [
                    "data availability", "management priority", "third-party dependency",
                    "feasibility", "roi", "operational readiness", "evaluation",
                ],
            },
            {
                "doc_type": "SHORTLIST",
                "label": "Use Case Shortlisting Report",
                "keywords": [
                    "scoring summary", "shortlisted", "rationale", "selection criteria",
                    "priority ranking", "use case shortlist",
                ],
            },
        ],
        "requirements": [
            {"key": "problem_statements", "label": "Problem Statements", "aliases": ["problem statement", "problem statements", "business problem", "pain points"], "required": True},
            {"key": "expected_outcomes", "label": "Expected Outcomes", "aliases": ["expected outcomes", "expected outcome", "business objectives", "goals"], "required": True},
            {"key": "department_owner", "label": "Department Owner", "aliases": ["department owner", "stakeholder", "sponsor", "owner"], "required": True},
            {"key": "data_sources", "label": "Data Sources", "aliases": ["data sources", "data source", "data inventory", "data availability"], "required": True},
            {"key": "pain_points", "label": "Pain Points & Gaps", "aliases": ["pain points", "pain point", "gaps", "current process", "process gaps"], "required": True},
            {"key": "feasibility_roi", "label": "Feasibility & ROI", "aliases": ["feasibility", "roi", "return on investment", "operational readiness"], "required": True},
            {"key": "strategic_context", "label": "Strategic Context", "aliases": ["strategic context", "corporate objective", "alignment", "strategic"], "required": False},
            {"key": "kpi_framework", "label": "KPI Framework", "aliases": ["kpi framework", "measurement framework", "data collection", "kpi"], "required": False},
        ],
    },
    2: {
        "title": "User & Experience",
        "icon": "people",
        "color": "blue",
        "description": "Detailed understanding of end users, their workflows, pain points, and experience expectations. Map user journeys to identify AI intervention opportunities and design human-centered solutions.",
        "must_include": [
            "User personas with roles, responsibilities, and motivations",
            "End-to-end user journeys with touchpoints and emotions",
            "Decision points and branching logic in workflows",
            "Current pain points and frustrations in the user experience",
            "AI intervention opportunities within existing workflows",
        ],
        "recommended": [
            "Empathy maps and user mindset analysis",
            "Service blueprints with backstage/frontstage activities",
            "Accessibility and inclusivity considerations",
            "User satisfaction benchmarks and NPS targets",
            "Change management impact assessment",
        ],
        "key_prompts": [
            "Who are the primary and secondary user types for this solution?",
            "What are the step-by-step user journeys from start to finish?",
            "Where do users currently experience the most friction or frustration?",
            "At which decision points can AI provide the most value?",
            "What are the user expectations for speed, accuracy, and usability?",
            "How will users be onboarded and trained on the new solution?",
        ],
        "required_documents": [
            {
                "doc_type": "PERSONAS",
                "label": "User Personas",
                "keywords": [
                    "user types", "roles", "responsibilities", "motivations",
                    "pain points", "expected benefits", "persona", "user profile",
                ],
            },
            {
                "doc_type": "USER_JOURNEYS",
                "label": "User Journeys",
                "keywords": [
                    "step-by-step", "touchpoints", "emotions", "frustrations",
                    "ai intervention", "user journey", "journey map",
                ],
            },
            {
                "doc_type": "USER_FLOWS",
                "label": "User Flows",
                "keywords": [
                    "workflow diagrams", "inputs", "outputs", "decision points",
                    "exceptions", "user flow", "process flow",
                ],
            },
        ],
        "requirements": [
            {"key": "user_types", "label": "User Types", "aliases": ["user types", "user type", "user personas", "personas"], "required": True},
            {"key": "roles_responsibilities", "label": "Roles & Responsibilities", "aliases": ["roles", "responsibilities", "role", "responsibility"], "required": True},
            {"key": "touchpoints", "label": "Touchpoints", "aliases": ["touchpoints", "touchpoint", "interaction points", "moments"], "required": True},
            {"key": "decision_points", "label": "Decision Points", "aliases": ["decision points", "decision point", "branching", "if-else"], "required": True},
            {"key": "ai_intervention", "label": "AI Intervention Opportunities", "aliases": ["ai intervention", "ai opportunity", "automation", "ai use"], "required": True},
            {"key": "empathy_maps", "label": "Empathy Maps", "aliases": ["empathy map", "empathy", "user mindset", "user thinking"], "required": False},
            {"key": "accessibility", "label": "Accessibility", "aliases": ["accessibility", "inclusive", "wcag", "a11y"], "required": False},
        ],
    },
    3: {
        "title": "Requirements & Prioritization",
        "icon": "assignment",
        "color": "violet",
        "description": "Comprehensive business, functional, and non-functional requirements with clear prioritization. Establish scope boundaries, acceptance criteria, and traceability from business goals to technical specifications.",
        "must_include": [
            "Business problem definition with scope and out-of-scope items",
            "Functional requirements with system behavior descriptions",
            "Non-functional requirements (performance, security, scalability)",
            "Feature prioritization using MoSCoW or similar framework",
            "Acceptance criteria for each major requirement",
            "Success metrics tied to business objectives",
        ],
        "recommended": [
            "Requirements traceability matrix",
            "Risk assessment for each requirement area",
            "Assumptions and dependencies documentation",
            "User stories with acceptance criteria in Gherkin format",
            "Release planning with phased delivery approach",
        ],
        "key_prompts": [
            "What is the business problem and how does it map to specific requirements?",
            "What are the must-have vs nice-to-have features?",
            "What are the performance, security, and compliance requirements?",
            "How will we validate that each requirement has been met?",
            "What are the key assumptions and dependencies?",
            "What is the minimum viable scope for Phase 1 delivery?",
        ],
        "required_documents": [
            {
                "doc_type": "BRD",
                "label": "Business Requirements Document",
                "keywords": [
                    "business problem", "scope", "out of scope", "success metrics",
                    "risks", "assumptions", "stakeholder", "business requirements",
                ],
            },
            {
                "doc_type": "FRD",
                "label": "Functional Requirements Document",
                "keywords": [
                    "functional flows", "system behavior", "input", "output",
                    "integration points", "acceptance criteria", "functional requirements",
                ],
            },
            {
                "doc_type": "FEATURE_PRIOR",
                "label": "Feature Prioritization",
                "keywords": [
                    "must-have", "should-have", "could-have", "won't-have",
                    "priority rationale", "moscow", "prioritization",
                ],
            },
            {
                "doc_type": "NFR",
                "label": "Non-Functional Requirements",
                "keywords": [
                    "performance", "scalability", "security", "availability",
                    "compliance", "non-functional", "nfr",
                ],
            },
            {
                "doc_type": "PRD",
                "label": "Product Requirements Document",
                "keywords": [
                    "product vision", "feature list", "release plan",
                    "user stories", "acceptance criteria", "product requirements",
                ],
            },
        ],
        "requirements": [
            {"key": "business_problem", "label": "Business Problem", "aliases": ["business problem", "problem statement", "business objective"], "required": True},
            {"key": "scope", "label": "Scope", "aliases": ["scope", "in scope", "out of scope", "boundaries"], "required": True},
            {"key": "success_metrics", "label": "Success Metrics", "aliases": ["success metrics", "kpis", "key performance indicators", "measurable outcomes"], "required": True},
            {"key": "functional_flows", "label": "Functional Flows", "aliases": ["functional flows", "functional flow", "system behavior", "workflow"], "required": True},
            {"key": "acceptance_criteria", "label": "Acceptance Criteria", "aliases": ["acceptance criteria", "acceptance criterion", "testable criteria", "definition of done"], "required": True},
            {"key": "prioritization", "label": "Feature Prioritization", "aliases": ["must-have", "should-have", "could-have", "won't-have", "moscow"], "required": True},
            {"key": "nfr", "label": "Non-Functional Requirements", "aliases": ["performance", "scalability", "security", "availability", "compliance"], "required": True},
            {"key": "traceability", "label": "Traceability Matrix", "aliases": ["traceability", "trace", "mapping", "matrix"], "required": False},
            {"key": "risk_assessment", "label": "Risk Assessment", "aliases": ["risk", "risk assessment", "risk register", "mitigation"], "required": False},
        ],
    },
    4: {
        "title": "Estimation & Planning",
        "icon": "calendar_month",
        "color": "amber",
        "description": "Accurate effort estimation, resource planning, and project scheduling. Establish realistic timelines with clear milestones, dependencies, and accountability through RACI matrices.",
        "must_include": [
            "Module-wise effort estimation with total hours",
            "Function point or story point analysis",
            "Project timeline with milestones and sprint planning",
            "Resource allocation and team composition",
            "RACI matrix for key deliverables",
            "Dependency identification and risk mitigation",
        ],
        "recommended": [
            "Historical velocity data for estimation calibration",
            "Buffer and contingency planning",
            "Critical path analysis",
            "Budget breakdown by phase and resource type",
            "Quality gates and Definition of Done criteria",
        ],
        "key_prompts": [
            "How many total effort hours are estimated per module or feature?",
            "What is the function point count and complexity scoring?",
            "What are the key milestones and sprint boundaries?",
            "Who is responsible, accountable, consulted, and informed for each deliverable?",
            "What are the critical dependencies and blocking risks?",
            "What buffer has been allocated for unknowns and rework?",
        ],
        "required_documents": [
            {
                "doc_type": "EFFORT_EST",
                "label": "Effort Estimation",
                "keywords": [
                    "module-wise", "total hours", "resource allocation",
                    "timeline estimation", "effort", "man-hours",
                ],
            },
            {
                "doc_type": "FP_EST",
                "label": "Function Point Estimation",
                "keywords": [
                    "function point", "complexity scoring", "estimated development",
                    "function point breakdown", "fp count",
                ],
            },
            {
                "doc_type": "PROJECT_PLAN",
                "label": "Project Plan / Timeline",
                "keywords": [
                    "milestones", "sprints", "dependencies", "risks",
                    "project plan", "timeline", "gantt",
                ],
            },
            {
                "doc_type": "RACI",
                "label": "RACI Matrix",
                "keywords": [
                    "responsible", "accountable", "consulted", "informed",
                    "raci", "raci matrix",
                ],
            },
        ],
        "requirements": [
            {"key": "effort_estimation", "label": "Effort Estimation", "aliases": ["effort estimation", "man-hours", "total hours", "resource allocation"], "required": True},
            {"key": "function_points", "label": "Function Point Analysis", "aliases": ["function point", "fp count", "complexity scoring", "function point breakdown"], "required": True},
            {"key": "milestones", "label": "Milestones", "aliases": ["milestones", "milestone", "sprints", "sprint"], "required": True},
            {"key": "dependencies", "label": "Dependencies", "aliases": ["dependencies", "dependency", "risks", "blockers"], "required": True},
            {"key": "raci", "label": "RACI Matrix", "aliases": ["responsible", "accountable", "consulted", "informed", "raci"], "required": True},
            {"key": "critical_path", "label": "Critical Path", "aliases": ["critical path", "critical path analysis", "longest path"], "required": False},
            {"key": "budget_breakdown", "label": "Budget Breakdown", "aliases": ["budget", "cost breakdown", "financial plan", "budget by phase"], "required": False},
        ],
    },
    5: {
        "title": "Architecture & Technical",
        "icon": "architecture",
        "color": "cyan",
        "description": "System architecture design covering high-level and detailed component design, AI/ML architecture, API specifications, and technology stack selection. Ensure scalable, maintainable, and secure technical foundations.",
        "must_include": [
            "High-level system architecture with major components",
            "Integration points and API contracts",
            "Data flow diagrams and processing pipelines",
            "AI/RAG architecture with model selection rationale",
            "API specification with endpoints and schemas",
            "Technology stack justification",
        ],
        "recommended": [
            "Low-level design with detailed component specs",
            "Database schema and entity-relationship diagrams",
            "Deployment architecture and infrastructure design",
            "Performance and scalability architecture patterns",
            "Disaster recovery and high availability design",
        ],
        "key_prompts": [
            "What is the high-level system architecture and how do components interact?",
            "What are the key integration points and API contracts?",
            "How does data flow through the system from input to output?",
            "What is the RAG architecture and how is the LLM selected?",
            "What technology stack is chosen and why?",
            "How will the system scale to handle peak loads?",
        ],
        "required_documents": [
            {
                "doc_type": "HLA",
                "label": "High-Level Architecture",
                "keywords": [
                    "system overview", "major components", "integration points",
                    "data flow", "high-level architecture", "hla",
                ],
            },
            {
                "doc_type": "LLA",
                "label": "Low-Level Architecture",
                "keywords": [
                    "detailed component", "api contracts", "database schema",
                    "deployment model", "low-level architecture", "lla",
                ],
            },
            {
                "doc_type": "AI_BLUEPRINT",
                "label": "AI Architecture Blueprint",
                "keywords": [
                    "rag architecture", "prompt flow", "model selection",
                    "guardrails", "ai architecture", "llm", "embedding",
                ],
            },
            {
                "doc_type": "API_SPEC",
                "label": "API Specification",
                "keywords": [
                    "endpoints", "request", "response", "authentication",
                    "error codes", "swagger", "openapi", "api specification",
                ],
            },
        ],
        "requirements": [
            {"key": "system_overview", "label": "System Overview", "aliases": ["system overview", "system architecture", "solution architecture"], "required": True},
            {"key": "integration_points", "label": "Integration Points", "aliases": ["integration points", "integration", "interfaces", "api contracts"], "required": True},
            {"key": "data_flow", "label": "Data Flow", "aliases": ["data flow", "data flow diagram", "dfd", "flow of data"], "required": True},
            {"key": "rag_architecture", "label": "RAG Architecture", "aliases": ["rag", "rag architecture", "retrieval augmented", "embedding", "vector"], "required": True},
            {"key": "api_specification", "label": "API Specification", "aliases": ["endpoints", "swagger", "openapi", "api specification", "rest"], "required": True},
            {"key": "database_design", "label": "Database Design", "aliases": ["database schema", "er diagram", "entity relationship", "database design"], "required": False},
            {"key": "deployment_architecture", "label": "Deployment Architecture", "aliases": ["deployment", "infrastructure", "cloud", "kubernetes", "docker"], "required": False},
        ],
    },
    6: {
        "title": "Security & Compliance",
        "icon": "shield",
        "color": "red",
        "description": "Comprehensive security policies, AI guardrails, secrets management, and regulatory compliance. Protect data, control access, and ensure the solution meets all applicable standards and regulations.",
        "must_include": [
            "AI security policy with data handling rules",
            "PII protection and access control mechanisms",
            "AI guardrails for prompt filtering and output validation",
            "Secrets management with rotation policies",
            "Compliance checklist covering applicable regulations",
            "Hallucination control and safety measures",
        ],
        "recommended": [
            "Threat modeling and risk assessment",
            "Penetration testing plan",
            "Data classification and retention policies",
            "Audit logging and monitoring for security events",
            "Incident response procedures",
        ],
        "key_prompts": [
            "What data handling rules apply and how is PII protected?",
            "What access control model is implemented (RBAC, ABAC)?",
            "What AI guardrails prevent harmful or biased outputs?",
            "How are secrets managed and when are they rotated?",
            "Which compliance standards must be met (ISO, SOC, GDPR)?",
            "What is the incident response procedure for security breaches?",
        ],
        "required_documents": [
            {
                "doc_type": "SEC_POLICY",
                "label": "AI Security Policy",
                "keywords": [
                    "data handling", "pii protection", "access control",
                    "security policy", "ai security", "data protection",
                ],
            },
            {
                "doc_type": "GUARDRAILS",
                "label": "Guardrails Document",
                "keywords": [
                    "prompt filtering", "output validation", "hallucination control",
                    "safety rules", "guardrails", "ai safety",
                ],
            },
            {
                "doc_type": "KEY_VAULT",
                "label": "Azure Key Vault Secrets Map",
                "keywords": [
                    "secrets list", "rotation policy", "access matrix",
                    "key vault", "secrets management",
                ],
            },
            {
                "doc_type": "COMPLIANCE",
                "label": "Compliance Checklist",
                "keywords": [
                    "iso", "soc", "internal it policies", "audit requirements",
                    "compliance", "regulatory", "gdpr",
                ],
            },
        ],
        "requirements": [
            {"key": "data_handling", "label": "Data Handling Rules", "aliases": ["data handling", "data protection", "pii", "pii protection"], "required": True},
            {"key": "access_control", "label": "Access Control", "aliases": ["access control", "rbac", "authorization", "authentication"], "required": True},
            {"key": "guardrails", "label": "Guardrails", "aliases": ["guardrails", "prompt filtering", "output validation", "safety rules"], "required": True},
            {"key": "secrets_management", "label": "Secrets Management", "aliases": ["secrets", "key vault", "rotation policy", "secrets management"], "required": True},
            {"key": "compliance", "label": "Compliance", "aliases": ["compliance", "iso", "soc", "audit", "regulatory", "gdpr"], "required": True},
            {"key": "threat_modeling", "label": "Threat Modeling", "aliases": ["threat model", "threat modeling", "attack vector", "risk assessment"], "required": False},
            {"key": "incident_response", "label": "Incident Response", "aliases": ["incident response", "breach response", "security incident"], "required": False},
        ],
    },
    7: {
        "title": "Monitoring & Observability",
        "icon": "monitoring",
        "color": "teal",
        "description": "Comprehensive monitoring, observability, and AI performance tracking. Establish dashboards, alerting, LLM evaluation, and incident management to ensure operational excellence.",
        "must_include": [
            "Product usage and adoption metrics definition",
            "AI performance metrics (accuracy, relevance, hallucination rate)",
            "Monitoring and observability infrastructure setup",
            "Incident and error management SOP",
            "Alerting thresholds and escalation procedures",
        ],
        "recommended": [
            "Custom dashboards for business and technical stakeholders",
            "A/B testing framework for AI model comparisons",
            "Log aggregation and analysis pipeline",
            "SLA/SLO definitions with error budgets",
            "Automated anomaly detection",
        ],
        "key_prompts": [
            "What product usage and adoption metrics will be tracked?",
            "How will AI performance (accuracy, hallucination rate) be measured?",
            "What monitoring tools are deployed (Azure Monitor, Prometheus, Grafana)?",
            "What is the incident escalation flow and severity classification?",
            "What alerting thresholds trigger automated responses?",
            "How will LLM evaluation results feed back into model improvement?",
        ],
        "required_documents": [
            {
                "doc_type": "METRICS",
                "label": "Metrics",
                "keywords": [
                    "product usage", "ai performance", "adoption metrics",
                    "business impact", "metrics", "kpi",
                ],
            },
            {
                "doc_type": "OBS_PLAN",
                "label": "Monitoring & Observability Plan",
                "keywords": [
                    "azure monitor", "prometheus", "grafana", "dashboards",
                    "monitoring", "observability", "alerting",
                ],
            },
            {
                "doc_type": "LLM_EVAL",
                "label": "LLM Evaluation Report",
                "keywords": [
                    "accuracy", "relevance", "hallucination rate",
                    "regression results", "llm evaluation", "ai evaluation",
                ],
            },
            {
                "doc_type": "INCIDENT_SOP",
                "label": "Incident & Error Management SOP",
                "keywords": [
                    "escalation flow", "severity levels", "resolution steps",
                    "incident management", "error management", "sop",
                ],
            },
        ],
        "requirements": [
            {"key": "usage_metrics", "label": "Usage Metrics", "aliases": ["product usage", "usage metrics", "adoption metrics", "dau", "mau"], "required": True},
            {"key": "ai_performance", "label": "AI Performance Metrics", "aliases": ["ai performance", "accuracy", "relevance", "hallucination rate"], "required": True},
            {"key": "monitoring", "label": "Monitoring Setup", "aliases": ["azure monitor", "prometheus", "grafana", "dashboards", "monitoring"], "required": True},
            {"key": "incident_management", "label": "Incident Management", "aliases": ["escalation", "severity levels", "incident management", "error management"], "required": True},
            {"key": "sla_slo", "label": "SLA/SLO Definitions", "aliases": ["sla", "slo", "service level", "error budget"], "required": False},
            {"key": "anomaly_detection", "label": "Anomaly Detection", "aliases": ["anomaly", "anomaly detection", "automated alert", "outlier"], "required": False},
        ],
    },
    8: {
        "title": "Deployment & Release",
        "icon": "rocket_launch",
        "color": "indigo",
        "description": "Production deployment planning with environment setup, release management, rollback procedures, and version tracking. Ensure smooth, reliable, and repeatable deployment processes.",
        "must_include": [
            "Environment setup and infrastructure configuration",
            "Release steps with go-live checklist",
            "Rollback plan and recovery procedures",
            "Version tracking and change log",
            "Production readiness verification",
        ],
        "recommended": [
            "Blue-green or canary deployment strategy",
            "Feature flag management plan",
            "Post-deployment verification automation",
            "Capacity planning for production loads",
            "Communication plan for stakeholder notifications",
        ],
        "key_prompts": [
            "What are the environment setup requirements and infrastructure specs?",
            "What is the step-by-step release process for go-live?",
            "What is the rollback plan if deployment fails?",
            "How are version changes tracked and communicated?",
            "What production readiness checks must pass before deployment?",
            "What is the post-deployment verification process?",
        ],
        "required_documents": [
            {
                "doc_type": "DEPLOY_GUIDE",
                "label": "Deployment Guide",
                "keywords": [
                    "environment setup", "release steps", "rollback plan",
                    "deployment guide", "deploy", "production",
                ],
            },
            {
                "doc_type": "RELEASE_NOTES",
                "label": "Release Notes",
                "keywords": [
                    "version changes", "fixes", "enhancements",
                    "release notes", "changelog",
                ],
            },
            {
                "doc_type": "CHANGE_LOG",
                "label": "Change Log",
                "keywords": [
                    "all updates", "dates", "owners",
                    "change log", "revision history", "version history",
                ],
            },
        ],
        "requirements": [
            {"key": "environment_setup", "label": "Environment Setup", "aliases": ["environment setup", "environment", "infrastructure", "deploy"], "required": True},
            {"key": "release_steps", "label": "Release Steps", "aliases": ["release steps", "release", "go live", "cutover"], "required": True},
            {"key": "rollback_plan", "label": "Rollback Plan", "aliases": ["rollback", "rollback plan", "rollback strategy", "recovery"], "required": True},
            {"key": "version_tracking", "label": "Version Tracking", "aliases": ["version changes", "changelog", "change log", "release notes"], "required": True},
            {"key": "feature_flags", "label": "Feature Flags", "aliases": ["feature flag", "feature toggle", "feature management"], "required": False},
            {"key": "capacity_planning", "label": "Capacity Planning", "aliases": ["capacity", "capacity planning", "load planning", "scaling plan"], "required": False},
        ],
    },
    9: {
        "title": "Adoption & Training",
        "icon": "school",
        "color": "orange",
        "description": "User enablement through training materials, onboarding guides, and adoption tracking. Ensure users can effectively utilize the solution and measure adoption success.",
        "must_include": [
            "Training manual with admin and user guides",
            "Onboarding guide with access instructions",
            "Adoption dashboard with usage metrics",
            "FAQ and troubleshooting documentation",
            "Support channel definitions",
        ],
        "recommended": [
            "Video tutorials and interactive walkthroughs",
            "Role-based training paths",
            "Gamification and incentive programs",
            "User feedback collection mechanisms",
            "Train-the-trainer program",
        ],
        "key_prompts": [
            "What training materials are needed for admin and end users?",
            "How will users be onboarded and what are the access instructions?",
            "What adoption metrics will be tracked (DAU, MAU, feature usage)?",
            "What support channels are available for user assistance?",
            "How will user feedback be collected and incorporated?",
            "What is the target adoption rate and timeline?",
        ],
        "required_documents": [
            {
                "doc_type": "TRAINING",
                "label": "Training Manual",
                "keywords": [
                    "admin guide", "user guide", "faqs",
                    "training manual", "training", "how-to",
                ],
            },
            {
                "doc_type": "ONBOARDING",
                "label": "Onboarding Guide",
                "keywords": [
                    "how to start", "access instructions", "support channels",
                    "onboarding", "getting started",
                ],
            },
            {
                "doc_type": "ADOPTION_DASH",
                "label": "Adoption Dashboard",
                "keywords": [
                    "dau", "mau", "feature usage", "feedback scores",
                    "adoption dashboard", "adoption metrics",
                ],
            },
        ],
        "requirements": [
            {"key": "training_content", "label": "Training Content", "aliases": ["training manual", "training", "admin guide", "user guide", "faqs"], "required": True},
            {"key": "onboarding", "label": "Onboarding Guide", "aliases": ["onboarding", "getting started", "access instructions", "how to start"], "required": True},
            {"key": "adoption_tracking", "label": "Adoption Tracking", "aliases": ["adoption dashboard", "dau", "mau", "feature usage", "feedback"], "required": True},
            {"key": "video_tutorials", "label": "Video Tutorials", "aliases": ["video", "tutorial", "walkthrough", "demo"], "required": False},
            {"key": "feedback_mechanism", "label": "Feedback Mechanism", "aliases": ["feedback", "survey", "user feedback", "feedback collection"], "required": False},
        ],
    },
    10: {
        "title": "Governance & AI Strategy",
        "icon": "account_balance",
        "color": "purple",
        "description": "AI governance framework with decision rights, review cycles, and strategic roadmap. Establish oversight mechanisms and plan for future AI expansion and model management.",
        "must_include": [
            "AI governance framework with roles and responsibilities",
            "Steering committee charter with decision rights",
            "AI roadmap with quarterly goals and future use cases",
            "Model retraining and drift management plan",
            "Review cycles and escalation paths",
        ],
        "recommended": [
            "AI ethics guidelines and responsible AI principles",
            "Model performance benchmarks and comparison framework",
            "Budget allocation for AI initiatives",
            "Partnership and vendor management strategy",
            "Innovation pipeline and experimentation framework",
        ],
        "key_prompts": [
            "Who owns AI governance and what are the decision rights?",
            "What is the meeting cadence for the steering committee?",
            "What are the quarterly AI goals and future use case candidates?",
            "How will model drift be detected and retraining triggered?",
            "What ethical guidelines govern AI deployment?",
            "What is the long-term AI expansion roadmap?",
        ],
        "required_documents": [
            {
                "doc_type": "GOV_FRAMEWORK",
                "label": "AI Governance Framework",
                "keywords": [
                    "roles", "responsibilities", "review cycles",
                    "governance framework", "ai governance",
                ],
            },
            {
                "doc_type": "STEERING",
                "label": "Steering Committee Charter",
                "keywords": [
                    "meeting cadence", "decision rights", "escalation path",
                    "steering committee", "charter",
                ],
            },
            {
                "doc_type": "AI_ROADMAP",
                "label": "AI Roadmap",
                "keywords": [
                    "quarterly goals", "future use cases", "expansion plan",
                    "ai roadmap", "roadmap",
                ],
            },
            {
                "doc_type": "DRIFT_PLAN",
                "label": "Model Retraining & Drift Management",
                "keywords": [
                    "monitoring", "retraining triggers", "versioning",
                    "drift management", "model retraining", "model monitoring",
                ],
            },
        ],
        "requirements": [
            {"key": "governance_roles", "label": "Governance Roles", "aliases": ["roles", "responsibilities", "governance", "governance framework"], "required": True},
            {"key": "decision_rights", "label": "Decision Rights", "aliases": ["decision rights", "decision", "escalation", "steering"], "required": True},
            {"key": "ai_roadmap", "label": "AI Roadmap", "aliases": ["ai roadmap", "roadmap", "quarterly goals", "future use cases"], "required": True},
            {"key": "model_retraining", "label": "Model Retraining Plan", "aliases": ["retraining", "drift", "versioning", "model monitoring"], "required": True},
            {"key": "ethics_guidelines", "label": "AI Ethics Guidelines", "aliases": ["ethics", "responsible ai", "ai ethics", "ethical guidelines"], "required": False},
            {"key": "innovation_pipeline", "label": "Innovation Pipeline", "aliases": ["innovation", "experimentation", "pipeline", "poc"], "required": False},
        ],
    },
    11: {
        "title": "Testing & Quality Engineering",
        "icon": "bug_report",
        "color": "rose",
        "description": "Comprehensive testing strategy covering functional, API, regression, performance, security, and LLM evaluation. Ensure quality through systematic test planning, execution, and reporting.",
        "must_include": [
            "Test strategy with scope, types, and entry/exit criteria",
            "Functional and API test cases with module-wise coverage",
            "Regression test suite for critical workflows",
            "Performance test report with load and stress results",
            "Security test report with vulnerability assessment",
            "LLM/RAG evaluation with accuracy and hallucination metrics",
        ],
        "recommended": [
            "Automated test pipeline integration (CI/CD)",
            "Chaos engineering and resilience testing",
            "User acceptance testing (UAT) plan",
            "Test data management strategy",
            "Defect triage and resolution workflow",
        ],
        "key_prompts": [
            "What is the test strategy and what types of testing are included?",
            "What are the entry and exit criteria for each test phase?",
            "How many test cases cover each module and API endpoint?",
            "What are the performance benchmarks (latency, throughput, error rate)?",
            "What security vulnerabilities were identified and how were they remediated?",
            "What is the LLM evaluation score for accuracy, relevance, and hallucination rate?",
        ],
        "required_documents": [
            {
                "doc_type": "TEST_STRATEGY",
                "label": "Test Strategy",
                "keywords": [
                    "scope of testing", "types of testing", "tools",
                    "environments", "entry criteria", "exit criteria",
                    "test strategy", "risk-based testing",
                ],
            },
            {
                "doc_type": "TEST_CASES",
                "label": "Functional & API Test Cases",
                "keywords": [
                    "module-wise", "api endpoint", "input", "output",
                    "error handling", "acceptance criteria", "test cases",
                ],
            },
            {
                "doc_type": "REGRESSION",
                "label": "Regression Test Suite",
                "keywords": [
                    "critical workflows", "high-risk areas", "ai prompt regression",
                    "rag retrieval", "regression", "regression suite",
                ],
            },
            {
                "doc_type": "PERF_TEST",
                "label": "Performance Test Report",
                "keywords": [
                    "load test", "stress test", "latency", "throughput",
                    "error rate", "bottleneck", "performance test",
                ],
            },
            {
                "doc_type": "SEC_TEST",
                "label": "Security Test Report",
                "keywords": [
                    "vulnerability scan", "penetration testing", "rbac",
                    "secrets", "owasp", "security test",
                ],
            },
            {
                "doc_type": "LLM_EVAL_TEST",
                "label": "LLM/RAG Evaluation Report",
                "keywords": [
                    "accuracy", "relevance", "hallucination rate",
                    "safety", "toxicity", "retrieval quality",
                    "guardrail validation", "llm evaluation",
                ],
            },
        ],
        "requirements": [
            {"key": "test_strategy", "label": "Test Strategy", "aliases": ["test strategy", "scope of testing", "entry criteria", "exit criteria"], "required": True},
            {"key": "test_cases", "label": "Functional Test Cases", "aliases": ["test cases", "functional test", "api test", "module-wise"], "required": True},
            {"key": "regression_suite", "label": "Regression Suite", "aliases": ["regression", "regression suite", "critical workflows", "ai prompt regression"], "required": True},
            {"key": "performance_testing", "label": "Performance Testing", "aliases": ["load test", "stress test", "latency", "throughput", "performance"], "required": True},
            {"key": "security_testing", "label": "Security Testing", "aliases": ["vulnerability", "penetration testing", "owasp", "security test"], "required": True},
            {"key": "llm_evaluation", "label": "LLM/RAG Evaluation", "aliases": ["llm evaluation", "hallucination", "accuracy", "retrieval quality", "guardrail"], "required": True},
            {"key": "uat_plan", "label": "UAT Plan", "aliases": ["uat", "user acceptance", "acceptance testing", "uat plan"], "required": False},
            {"key": "chaos_testing", "label": "Chaos Engineering", "aliases": ["chaos", "chaos engineering", "resilience", "fault injection"], "required": False},
        ],
    },
}

TOTAL_LEVELS = 11

LEVEL_LABELS = {
    1: "A", 2: "B", 3: "C", 4: "D", 5: "E",
    6: "F", 7: "G", 8: "H", 9: "I", 10: "J", 11: "K",
}


def get_level_module_info(level: int) -> dict:
    """Return full module info for a level including description, must_include, recommended, key_prompts."""
    level = max(1, min(int(level or 1), TOTAL_LEVELS))
    config = LEVEL_REQUIREMENTS[level]
    return {
        "level": level,
        "label": LEVEL_LABELS.get(level, str(level)),
        "title": config["title"],
        "icon": config.get("icon", "folder"),
        "color": config.get("color", "gray"),
        "description": config.get("description", ""),
        "must_include": config.get("must_include", []),
        "recommended": config.get("recommended", []),
        "key_prompts": config.get("key_prompts", []),
        "required_documents": [
            {"doc_type": doc["doc_type"], "label": doc["label"]}
            for doc in config.get("required_documents", [])
        ],
        "requirements_count": len(config.get("requirements", [])),
        "required_count": sum(1 for r in config.get("requirements", []) if r.get("required", True)),
        "recommended_count": sum(1 for r in config.get("requirements", []) if not r.get("required", True)),
    }


def get_all_levels_module_info() -> list:
    """Return module info for all levels."""
    return [get_level_module_info(level) for level in range(1, TOTAL_LEVELS + 1)]
