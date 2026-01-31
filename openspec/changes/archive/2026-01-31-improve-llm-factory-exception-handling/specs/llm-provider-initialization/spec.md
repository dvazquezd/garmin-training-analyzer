# Delta Spec: LLM Provider Initialization Error Handling

## MODIFIED Requirements

### Requirement: Exception chain preservation during provider initialization

When `LLMFactory.get_provider()` fails to initialize an LLM provider, the system SHALL preserve the original exception context to facilitate debugging. The error message SHALL include the complete traceback chain from the root cause.

#### Scenario: Import error preserves context

- **WHEN** the required LangChain library is not installed (e.g., `langchain_anthropic`)
- **THEN** the system raises a `RuntimeError` with message "Could not initialize LLM provider: <details>"
- **AND** the original `ImportError` is preserved in the exception chain via `raise ... from e`
- **AND** developers can see the complete traceback including the original import failure

#### Scenario: Missing API key preserves context

- **WHEN** a provider is configured but the API key is missing
- **THEN** the system raises a `RuntimeError` from the LangChainWrapper initialization
- **AND** the error message clearly indicates which provider failed
- **AND** the exception chain preserves the original "Missing API key" RuntimeError

#### Scenario: Unsupported provider preserves context

- **WHEN** user configures an unsupported provider (e.g., `LLM_PROVIDER=invalid`)
- **THEN** the system raises `RuntimeError: LLM provider not supported: invalid`
- **AND** this error is raised directly without being caught and re-raised
- **AND** the stack trace points to the exact location where the check occurs

## ADDED Requirements

### Requirement: Specific runtime errors propagate without wrapping

Provider-specific `RuntimeError` exceptions (e.g., missing API keys, unsupported providers) SHALL propagate directly to the caller without being caught and re-wrapped. Only import errors and unexpected exceptions SHALL be wrapped.

#### Scenario: Missing API key raises specific error

- **WHEN** `LangChainWrapper.__init__()` raises `RuntimeError('Missing API key for Anthropic/Claude provider')`
- **THEN** this exact `RuntimeError` propagates to the caller
- **AND** the error is NOT caught and re-wrapped in a generic message
- **AND** the stack trace shows the wrapper initialization as the source
