## ADDED Requirements

### Requirement: Load configuration from environment file

The system SHALL load configuration from .env files using python-dotenv.

#### Scenario: Load complete configuration from env file
- **WHEN** .env file exists with all required fields
- **THEN** Config object is created with values from .env file

#### Scenario: Use defaults when env file missing
- **WHEN** .env file does not exist
- **THEN** Config object uses default values
- **AND** warning is logged about missing file

### Requirement: Validate required fields

The system SHALL validate required configuration fields are present.

#### Scenario: Missing required field
- **WHEN** GARMIN_EMAIL is not provided
- **THEN** ConfigError is raised with descriptive message

### Requirement: Validate data types

The system SHALL validate configuration values match expected types.

#### Scenario: Invalid type provided
- **WHEN** ANALYSIS_DAYS is non-numeric string
- **THEN** ConfigError is raised describing type mismatch

### Requirement: Validate value ranges

The system SHALL validate numeric values are within acceptable ranges.

#### Scenario: Value exceeds range
- **WHEN** TEMPERATURE is set to 2.5
- **THEN** ConfigError is raised with range information

### Requirement: CLI arguments override configuration

The system SHALL allow CLI arguments to override environment values.

#### Scenario: CLI overrides env file
- **WHEN** .env has ANALYSIS_DAYS=30 and CLI passes --days 60
- **THEN** Config.analysis_days equals 60

### Requirement: Multi-environment support

The system SHALL support environment-specific configuration files.

#### Scenario: Load production environment
- **WHEN** env="production" is specified
- **THEN** .env.production is loaded instead of .env

### Requirement: Validate API key formats

The system SHALL validate API keys match provider format requirements.

#### Scenario: Invalid API key format
- **WHEN** ANTHROPIC_API_KEY does not start with sk-ant-
- **THEN** ConfigError is raised with format requirements

### Requirement: Generate documentation

The system SHALL provide configuration documentation generation.

#### Scenario: Generate docs
- **WHEN** Config.generate_docs() is called
- **THEN** formatted table of all parameters is returned

### Requirement: Type-safe configuration

The system SHALL use dataclasses with type hints for configuration.

#### Scenario: Config has type annotations
- **WHEN** Config class is inspected
- **THEN** __annotations__ attribute exists with type hints

### Requirement: Export configuration

The system SHALL allow exporting configuration to JSON with secrets hidden.

#### Scenario: Export with hidden secrets
- **WHEN** Config.export() is called with hide_secrets=True
- **THEN** JSON file contains configuration with masked secrets

### Requirement: Hot reload in development

The system MAY support configuration reloading when files change.

#### Scenario: Detect configuration change
- **WHEN** DEBUG=true and .env is modified
- **THEN** configuration is automatically reloaded
