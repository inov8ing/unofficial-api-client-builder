# Unofficial API Client Builder

A robust, reusable toolkit and workflow designed for building sophisticated Python client wrappers for private web application endpoints. This project standardizes the approach to capturing and automating web sessions, handling HTTP interactions, and packaging the resulting client for easy integration.

## Key Features

- **Standardized Client Architecture**: Templates and patterns for creating a cohesive `Client` class.
- **Session Automation**: Techniques and scripts for cookie extraction and management (supporting automated collection from browsers).
- **Advanced HTTP Parsing**: Built-in methods for handling Server-Sent Events (SSE) and complex JSON payloads.
- **Packaging Workflow**: Clear instructions and scaffolding for turning API wrappers into installable Python packages (`pyproject.toml`).
- **Comprehensive Documentation**: Detailed references on reverse engineering, authentication patterns, and best practices.

## Tech Stack

- **Python 3.9+**: The core language for client scaffolding and automation scripts.
- **Markdown**: For extensive documentation and structural references.

## Project Structure

```text
├── assets/                  # Starter templates and scaffolding assets
├── references/              # Detailed guides on architecture, auth, and parsing
├── scripts/                 # Scaffolding utilities (e.g., scaffold_unofficial_api.py)
├── SKILL.md                 # Main workflow instructions and guidelines
└── LICENSE                  # Project license
```

## Installation

This repository acts as a toolkit and reference guide. You can clone the repository to use the scaffolding scripts locally:

```bash
git clone https://github.com/USERNAME/unofficial-api-client-builder.git
cd unofficial-api-client-builder
```

## Usage

Use the provided scaffolding script to quickly bootstrap a new client package:

```bash
python scripts/scaffold_unofficial_api.py \
  --name my-service-api \
  --import-name my_service_api \
  --out ./my-service-api \
  --mode demo
```

For advanced usage, refer to the documentation in the `references/` directory.

## Development Workflow

1. Start by reviewing the core guidelines in `SKILL.md`.
2. Reference the specific documentation in `references/` depending on the phase of your project (e.g., `cookie-automation.md` for session management).
3. Utilize the `assets/templates` to copy standard patterns without starting from scratch.

## Troubleshooting

- **Authentication Issues**: Ensure the target application has not changed its authentication flow. Refer to `references/auth-patterns.md`.
- **Parsing Errors**: Web applications frequently update their payload structures. You may need to capture new endpoint contracts.

## Contributing

Contributions are welcome! Please ensure that any additions or changes adhere to the non-negotiable guardrails outlined in the project documentation. Ensure no sensitive information (such as personal cookies or tokens) is ever committed.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
