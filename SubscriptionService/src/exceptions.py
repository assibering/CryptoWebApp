class BaseAppException(Exception):
    """Base exception for our application"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

class ResourceNotFoundException(BaseAppException):
    """Raised when a requested resource is not found"""
    def __init__(self, message: str):
        super().__init__(message, status_code=404)

class ResourceAlreadyExistsException(BaseAppException):
    """Raised when an existing resource is being created again"""
    def __init__(self, message: str):
        super().__init__(message, status_code=409)

class ValidationException(BaseAppException):
    """Raised when input validation fails"""
    def __init__(self, message: str):
        super().__init__(message, status_code=404)

class UnauthorizedException(BaseAppException):
    """Raised when user is not authorized"""
    def __init__(self, message: str):
        super().__init__(message, status_code=401)