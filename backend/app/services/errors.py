"""Domain-level exceptions."""


class DomainError(Exception):
    """Base class for service-layer errors."""


class NotFoundError(DomainError):
    """Raised when an entity cannot be located."""


class ConflictError(DomainError):
    """Raised when a unique constraint or business rule is violated."""
