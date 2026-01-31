# SGNtech Auto Reconciliation API - Architecture Guide

> **Note:** This guide references `src/` in some examples; this project uses `app/` as the application root. Apply the same patterns under `app/` (e.g. `app/core/`, `app/models/`).

## 🎯 **CRITICAL: This document defines MANDATORY architectural patterns. ALL future development MUST follow these patterns strictly.**

---

## 🏛️ **SOLID PRINCIPLES (MANDATORY)**

### **S** - Single Responsibility Principle
- **ONE CLASS = ONE RESPONSIBILITY**: Each class must have exactly one reason to change
- **ONE FILE = ONE CLASS**: Never put multiple classes in the same file
- **FOCUSED MODULES**: Each module serves a single, well-defined purpose
- **CLEAR BOUNDARIES**: Business logic, data access, and presentation are strictly separated

### **O** - Open/Closed Principle  
- **EXTEND, DON'T MODIFY**: Use inheritance and composition to extend functionality
- **INTERFACE EXTENSIONS**: Add new implementations without changing existing interfaces
- **PLUGIN ARCHITECTURE**: Use dependency injection to swap implementations
- **BACKWARDS COMPATIBILITY**: New features must not break existing code

### **L** - Liskov Substitution Principle
- **INTERFACE CONTRACTS**: All implementations must honor interface contracts completely
- **BEHAVIORAL COMPATIBILITY**: Subclasses must be substitutable for their base classes
- **NO STRENGTHENING**: Implementations cannot add preconditions not in the interface
- **NO WEAKENING**: Implementations cannot weaken postconditions specified in the interface

### **I** - Interface Segregation Principle
- **FOCUSED INTERFACES**: Interfaces must be small, focused, and role-specific
- **NO FAT INTERFACES**: Never force classes to implement methods they don't use
- **CLIENT-SPECIFIC**: Design interfaces based on client needs, not implementation convenience
- **COMPOSITION OVER INHERITANCE**: Prefer multiple small interfaces over large hierarchies

### **D** - Dependency Inversion Principle
- **DEPEND ON ABSTRACTIONS**: High-level modules must not depend on low-level modules
- **INTERFACE DEPENDENCIES**: All dependencies must be through interfaces
- **DI CONTAINER**: Use dependency injection container for all service instantiation
- **INVERSION OF CONTROL**: Framework controls object lifecycle and dependencies

---

## 🎨 **DESIGN PRINCIPLES (MANDATORY)**

### **Modular Architecture**
```python
# ✅ CORRECT: Focused, single-purpose module
class UserAuthenticationService(IUserAuthenticationService):
    """Handles ONLY user authentication logic."""
    def __init__(self, user_repo: IUserRepository):
        self._user_repo = user_repo
    
    async def authenticate(self, credentials: UserCredentials) -> AuthResult:
        # Single responsibility: authenticate users
        pass

# ❌ WRONG: Multiple responsibilities in one class
class UserServiceGod:
    """Handles authentication, profile, notifications, billing..."""  # TOO MANY RESPONSIBILITIES
```

### **Testable Design**
```python
# ✅ CORRECT: Easy to test with dependency injection
class PaymentProcessor(IPaymentProcessor):
    def __init__(self, 
                 gateway: IPaymentGateway,
                 validator: IPaymentValidator,
                 logger: ILoggerService):
        self._gateway = gateway
        self._validator = validator
        self._logger = logger
    
    async def process_payment(self, payment: Payment) -> PaymentResult:
        # All dependencies can be easily mocked in tests
        pass

# ❌ WRONG: Hard to test due to tight coupling
class PaymentProcessorBad:
    async def process_payment(self, payment: Payment) -> PaymentResult:
        gateway = ExternalPaymentGateway()  # Hard dependency
        validator = PaymentValidator()      # Cannot mock
        logger = FileLogger("/logs/app.log")  # Side effects
```

### **Immutable Configuration**
```python
# ✅ CORRECT: Immutable, validated configuration
@dataclass(frozen=True)
class DatabaseConfig:
    host: str
    port: int
    database: str
    username: str
    password: str
    
    def __post_init__(self):
        if not self.host:
            raise ValueError("Database host is required")

# ❌ WRONG: Mutable, unvalidated configuration
class DatabaseConfigBad:
    def __init__(self):
        self.host = None  # Can be changed, no validation
```

## ⚡ **DEPENDENCY INJECTION (MANDATORY)**

### Core DI Container (`src/core/di.py`)
- **ALWAYS** use the DI container for service instantiation
- **NEVER** instantiate services directly with `new`
- Repository dependencies MUST be injected

### Service Registration Pattern:
```python
# Service configuration
container.register_singleton(IInterface, ConcreteImplementation)

# Usage in services
def __init__(self, repository: IRepository = Depends(container.get)):
    self.repository = repository
```

### FastAPI Integration:
```python
# Controller dependencies
async def endpoint(service: Service = Depends(container.get)):
    return await service.execute()
```

## 🏗️ **INTERFACE-DRIVEN DESIGN (MANDATORY)**

### Abstract Interfaces (`src/interfaces/`)
- **ALL** services MUST implement interfaces
- **ALL** repositories MUST implement interfaces
- Use dependency inversion principle strictly

### Implementation Pattern:
```python
# Interface
class IService(ABC):
    @abstractmethod
    async def method(self) -> Result: ...

# Implementation  
class Service(IService):
    def __init__(self, repo: IRepository):
        self.repo = repo
    
    async def method(self) -> Result:
        return await self.repo.operation()
```

## 🗄️ **REPOSITORY PATTERN (MANDATORY)**

### Base Repository (`src/repositories/base.py`)
- **ALL** repositories MUST inherit from `BaseRepository[T]`
- **NEVER** use direct SQLAlchemy calls in services
- Generic typing MUST be used: `BaseRepository[ModelType]`

### Repository Structure:
```python
class EntityRepository(BaseRepository[Entity]):
    def __init__(self, session: AsyncSession):
        super().__init__(session, Entity)
    
    async def custom_query(self) -> List[Entity]:
        # Custom repository methods
```

## 🚀 **SERVICE LAYER ARCHITECTURE (MANDATORY)**

### Service Construction:
- **ALWAYS** inject repositories via constructor
- **ALWAYS** implement corresponding interface
- **NEVER** mix business logic with data access

### Business Event Logging:
```python
from src.services.events import BusinessEvent

# MANDATORY: Log all significant business operations
self.business_events.append(BusinessEvent(
    event_type="OPERATION_TYPE",
    description="Operation description",
    metadata={"key": "value"}
))
```

## ⚙️ **CONFIGURATION MANAGEMENT (MANDATORY)**

### Settings Pattern (`src/core/config.py`)
```python
class Settings(BaseSettings):
    # Environment-based configuration
    database_url: str
    admin_master_key: str
    
    class Config:
        env_file = ".env"

# Usage
def get_settings() -> Settings:
    return Settings()
```

### Bootstrap Configuration:
- **ALWAYS** use JSON-based bootstrap API key configuration
- **NEVER** hardcode sensitive configuration

## 📊 **DATABASE PATTERNS (MANDATORY)**

### Model Definitions (`src/models/`)
```python
from src.models.api_key import APIKey
from src.models.ml_model import MLModel
from src.models.request_log import RequestLog


class Entity(Base):
    __tablename__ = "entities"
    
    id: Mapped[UUID] = mapped_column(PostgresUUID(as_uuid=True), primary_key=True)
    # SQLAlchemy 2.0 mapped_column syntax MANDATORY
```

### Session Management:
- **ALWAYS** use async sessions
- **ALWAYS** handle transactions in service layer
- **NEVER** expose sessions to controllers

## 🧪 **TESTING ARCHITECTURE (IMMUTABLE)**

### Test Structure:
- **MUST** mirror `src/` directory structure exactly
- **NEVER** use real database connections
- **ALWAYS** use comprehensive mocking

### Test Patterns:
```python
class TestService:
    @pytest.fixture
    def mock_repository(self):
        return AsyncMock(spec=IRepository)
    
    @pytest.fixture  
    def service(self, mock_repository):
        return Service(mock_repository)
    
    @pytest.mark.asyncio
    async def test_method_success(self, service, mock_repository):
        # Comprehensive test with mocks
```

### Test Categories (MANDATORY for each service):
1. **Core Functionality** - Happy path scenarios
2. **Error Handling** - Exception scenarios  
3. **Edge Cases** - Boundary conditions
4. **Integration** - Service interaction patterns
5. **Business Logic Validation** - Verify business rules and domain logic

### Fixture Standards:
- **ALWAYS** use `AsyncMock(spec=Interface)` for repositories
- **ALWAYS** use `Mock(spec=Model)` for database models
- **NEVER** instantiate real SQLAlchemy models in tests

### Test Structure Best Practices:
```python
class TestServiceName:
    """Test class for ServiceName following ARCHITECTURE_GUIDE.md patterns."""
    
    # ============================================================================
    # FIXTURES (Dependency Injection)
    # ============================================================================
    
    @pytest.fixture
    def mock_dependency(self):
        """Mock dependency with proper interface specification."""
        return Mock(spec=IDependencyInterface)
    
    @pytest.fixture
    def service_instance(self, mock_dependency):
        """Service instance with injected dependencies."""
        return ServiceName(mock_dependency)
    
    # ============================================================================
    # CORE FUNCTIONALITY TESTS
    # ============================================================================
    
    def test_basic_operation_success(self, service_instance, mock_dependency):
        """Test basic operation with valid inputs."""
        # Arrange
        mock_dependency.method.return_value = expected_result
        
        # Act
        result = service_instance.operation(input_data)
        
        # Assert
        assert result == expected_result
        mock_dependency.method.assert_called_once_with(input_data)
    
    # ============================================================================
    # ERROR HANDLING TESTS
    # ============================================================================
    
    def test_operation_with_invalid_input(self, service_instance):
        """Test operation behavior with invalid inputs."""
        with pytest.raises(ValidationError):
            service_instance.operation(invalid_data)
    
    # ============================================================================
    # EDGE CASES AND BOUNDARY CONDITIONS
    # ============================================================================
    
    def test_operation_with_empty_data(self, service_instance):
        """Test operation with empty or minimal data."""
        result = service_instance.operation(empty_data)
        assert result is not None
    
    # ============================================================================
    # INTEGRATION TESTS
    # ============================================================================
    
    def test_service_integration_workflow(self, service_instance, mock_dependency):
        """Test complete service workflow with multiple dependencies."""
        # Test end-to-end workflow
        pass
    
    # ============================================================================
    # BUSINESS LOGIC VALIDATION TESTS
    # ============================================================================
    
    def test_business_rule_validation(self, service_instance):
        """Test specific business rules and domain logic."""
        # Test business-specific validation
        pass
```

### Mocking Best Practices:
- **NEVER** replicate real functionality in mocks - mocks should return predetermined values
- **ALWAYS** use `spec` parameter for type safety and interface compliance
- **ALWAYS** verify mock calls with `assert_called_once_with()` or similar
- **NEVER** mock the class under test - only mock its dependencies
- **ALWAYS** use `AsyncMock` for async dependencies, `Mock` for sync dependencies

### Common Testing Pitfalls to Avoid:
```python
# ❌ WRONG: Replicating real functionality in mocks
def test_bad_mock_example(self):
    mock_converter = Mock()
    # DON'T DO THIS - replicating real logic in mock
    mock_converter.convert_amount.side_effect = lambda x: float(x.replace(',', ''))
    
# ✅ CORRECT: Simple predetermined return values
def test_good_mock_example(self):
    mock_converter = Mock(spec=IDataTypeConverter)
    mock_converter.convert_amount.return_value = 1234.56
    # Mock returns predetermined value, no logic replication

# ❌ WRONG: Testing implementation details instead of behavior
def test_bad_implementation_test(self):
    service = Service(mock_dep)
    service.process_data(data)
    # DON'T test internal method calls - test the outcome
    assert service._internal_method.called

# ✅ CORRECT: Testing behavior and outcomes
def test_good_behavior_test(self):
    service = Service(mock_dep)
    result = service.process_data(data)
    # Test the actual result and side effects
    assert result.status == "success"
    assert result.processed_count == 5

# ❌ WRONG: Not using proper interface specifications
def test_bad_mock_spec(self):
    mock_service = Mock()  # No spec - can call any method
    # This won't catch interface violations

# ✅ CORRECT: Using interface specifications
def test_good_mock_spec(self):
    mock_service = Mock(spec=IServiceInterface)
    # This will catch interface violations and provide better error messages
```

### Test Organization Anti-Patterns:
- **DON'T** use `setup_method()` - use `@pytest.fixture` instead
- **DON'T** create multiple test classes for the same service - consolidate into one
- **DON'T** test private methods directly - test through public interface
- **DON'T** create tests that depend on external services or databases
- **DON'T** write tests that are too complex - one test should verify one behavior

### Coverage Analysis and Missing Test Cases Assessment:

#### **MANDATORY Coverage Analysis Process:**
1. **Run Coverage Report**: Always run coverage analysis to identify uncovered lines
   ```bash
   python -m pytest tests/path/to/test_file.py -v --cov=src/path/to/source_file --cov-report=term-missing
   ```

2. **Analyze Missing Lines**: For each uncovered line, assess if it represents:
   - **Missing Test Case**: Line contains business logic that should be tested
   - **Edge Case**: Line handles boundary conditions or error scenarios
   - **Defensive Code**: Line contains safety checks or validation logic
   - **Unreachable Code**: Line that cannot be reached through normal execution paths

3. **Coverage Assessment Criteria**:
   ```python
   # ✅ MISSING TEST CASE - Should be tested
   def process_amount(self, amount: str) -> float:
       if not amount:  # Line 45 - MISSING: Empty string handling
           return 0.0
       return float(amount)
   
   # ✅ EDGE CASE - Should be tested  
   def validate_date(self, date_str: str) -> bool:
       if len(date_str) > 10:  # Line 67 - MISSING: Long string handling
           return False
       return True
   
   # ✅ DEFENSIVE CODE - Should be tested
   def safe_divide(self, a: float, b: float) -> float:
       if b == 0:  # Line 89 - MISSING: Division by zero handling
           raise ValueError("Cannot divide by zero")
       return a / b
   
   # ❌ UNREACHABLE CODE - May not need testing
   def legacy_method(self) -> str:
       return "deprecated"
       # Line 123 - This line is unreachable, no test needed
   ```

4. **Missing Test Case Identification**:
   - **Business Logic Lines**: Always require test coverage
   - **Error Handling Lines**: Must be tested with exception scenarios
   - **Validation Lines**: Test with valid and invalid inputs
   - **Edge Case Lines**: Test boundary conditions and extreme values
   - **Interface Method Lines**: Test all public interface methods
   - **Helper Method Lines**: Test through public interface or directly if critical

5. **Test Case Addition Process**:
   ```python
   # Example: Adding missing test cases for uncovered lines
   
   # Line 45: Empty string handling in process_amount
   def test_process_amount_empty_string(self, service):
       """Test process_amount with empty string - covers line 45."""
       result = service.process_amount("")
       assert result == 0.0
   
   # Line 67: Long string handling in validate_date  
   def test_validate_date_long_string(self, service):
       """Test validate_date with string longer than 10 chars - covers line 67."""
       result = service.validate_date("2023-12-25-extra")
       assert result is False
   
   # Line 89: Division by zero handling in safe_divide
   def test_safe_divide_by_zero(self, service):
       """Test safe_divide with zero divisor - covers line 89."""
       with pytest.raises(ValueError, match="Cannot divide by zero"):
           service.safe_divide(10, 0)
   ```

6. **Coverage Quality Standards**:
   - **Minimum Coverage**: 90% for all services
   - **Uncovered Lines**: Must be justified if not tested
   - **Defensive Code**: Always test error conditions and edge cases

7. **Coverage Analysis Checklist**:
   - [ ] Run coverage report for the service
   - [ ] Identify all uncovered lines
   - [ ] Assess each uncovered line for test necessity
   - [ ] Add missing test cases for business logic
   - [ ] Add missing test cases for error handling
   - [ ] Add missing test cases for edge cases
   - [ ] Add missing test cases for interface methods
   - [ ] Verify 95%+ coverage achieved
   - [ ] Document any justified uncovered lines

8. **Coverage Analysis Anti-Patterns**:
   ```python
   # ❌ WRONG: Ignoring uncovered lines without analysis
   # "Line 45 is uncovered but it's just a simple check"
   
   # ❌ WRONG: Testing only happy paths
   def test_process_amount_valid(self, service):
       result = service.process_amount("123.45")
       assert result == 123.45
   # Missing: test_process_amount_empty_string, test_process_amount_invalid
   
   # ❌ WRONG: Not testing error conditions
   def test_safe_divide_valid(self, service):
       result = service.safe_divide(10, 2)
       assert result == 5.0
   # Missing: test_safe_divide_by_zero
   
   # ✅ CORRECT: Comprehensive coverage analysis
   def test_process_amount_comprehensive(self, service):
       # Test valid input
       assert service.process_amount("123.45") == 123.45
       # Test empty string (covers line 45)
       assert service.process_amount("") == 0.0
       # Test invalid input
       with pytest.raises(ValueError):
           service.process_amount("invalid")
   ```

9. **Coverage Analysis Tools Integration**:
   ```bash
   # Run coverage with detailed missing line report
   python -m pytest tests/ -v --cov=src/ --cov-report=term-missing --cov-report=html
   
   # Focus on specific service coverage
   python -m pytest tests/services/data_transformation/ -v --cov=src/services/data_transformation/ --cov-report=term-missing
   
   # Generate HTML coverage report for detailed analysis
   python -m pytest tests/ --cov=src/ --cov-report=html
   # Open htmlcov/index.html in browser for visual analysis
   ```

## 🔒 **ERROR HANDLING (MANDATORY)**

### Exception Hierarchy (`src/core/exceptions.py`)
```python
class BusinessLogicError(Exception):
    def __init__(self, message: str, error_code: str, details: dict = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
```

### Controller Error Handling:
```python
try:
    result = await service.execute()
except BusinessLogicError as e:
    raise HTTPException(
        status_code=400,
        detail={
            "error": e.message,
            "error_code": e.error_code,
            "details": e.details
        }
    )
```

## 📝 **API DESIGN PATTERNS (MANDATORY)**

### Controller Structure (`src/controllers/`)
- **THIN** controllers - business logic in services only  
- **ALWAYS** use dependency injection
- **CONSISTENT** error responses

### Authentication:
```python
# Admin endpoints
async def endpoint(admin_key: str = Depends(get_admin_key)):
    pass

# API key endpoints  
async def endpoint(api_key: APIKey = Depends(get_api_key)):
    pass
```

## 🎯 **CRITICAL COMPLIANCE REQUIREMENTS**

### ❌ **NEVER DO:**
- Direct SQLAlchemy queries in services/controllers
- Database-dependent tests  
- Hardcoded configuration values
- Service instantiation without DI
- Breaking interface contracts
- Mixing business logic with data access
- Real database connections in tests

### ✅ **ALWAYS DO:**
- Use DI container for all service dependencies
- Implement interfaces for all services/repositories  
- Comprehensive mock-based testing
- Business event logging for significant operations
- Environment-based configuration
- Generic typing for repositories
- Async/await patterns consistently
- Exception handling with proper error codes

## 🔍 **CODE REVIEW CHECKLIST**

### **SOLID Principles Compliance:**
- [ ] **Single Responsibility**: Each class has exactly one reason to change
- [ ] **Open/Closed**: New functionality added without modifying existing code
- [ ] **Liskov Substitution**: All implementations honor their interface contracts
- [ ] **Interface Segregation**: Interfaces are small, focused, and role-specific
- [ ] **Dependency Inversion**: Dependencies are through interfaces, not concrete classes

### **Architecture Compliance:**
- [ ] Service implements required interface
- [ ] Repository inherits from BaseRepository[T]
- [ ] Dependencies injected via constructor (no service locator pattern)
- [ ] One class per file with meaningful file names
- [ ] Tests use AsyncMock/Mock with spec parameters
- [ ] Business events logged for operations
- [ ] Error handling with proper exceptions
- [ ] Configuration accessed via Settings
- [ ] No direct database queries in services

### **Code Quality:**
- [ ] Clear, descriptive class and method names
- [ ] Comprehensive docstrings for public methods
- [ ] Type hints for all method parameters and return values
- [ ] No magic numbers or hardcoded values
- [ ] Proper error messages with context
- [ ] Consistent code formatting and style

### **Testing Requirements:**
- [ ] Comprehensive test coverage for happy paths
- [ ] Error scenarios and edge cases tested
- [ ] All dependencies properly mocked
- [ ] Tests follow AAA pattern (Arrange, Act, Assert)
- [ ] Test names clearly describe what is being tested

---


## **TEST DEVELOMPMENT INSTRUCTIONS**

**Files Completed**: 00/0 total testable files (0%)
**Scope**: ALL testable source files in src/ directory
**CURRENTLY FOCUSED ON**: `src/**`
**NEXT FILE AFTER**: `src/**`

## 📋 **PROCEDURE (DO NOT DEVIATE)**

### For Each File:
1. **ANALYZE**: Read and understand the complete source code of the file being tested
2. **FIX ISSUES**: If there are ANY issues (DI, bugs, logic errors), fix them first
3. **GENERATE/UPDATE**: Create/Update the comprehensive tests following the new architecture
4. **RUN TESTS**: Execute tests and verify they pass
5. **FIX TEST ISSUES**: If test failures occur, fix them and continue
6. **UPDATE TODO**: Reflect progress in this TODO file
7. **MOVE TO NEXT**: Mark complete and proceed to next file

### Key Points:
- **Testing is the PRIMARY focus**, not issue fixing
- **Issue fixing is a prerequisite**, not the main goal
- **Test files mirror src/ architecture**
- **Comprehensive test coverage** for all functionality
- **DI pattern compliance** throughout

---

## ⚠️ **WHAT NOT TO DO**
- Don't go to the next file until the current one is fully done, and ALL tests pass
- Don't skip comprehensive test creation
- Don't create minimal tests - make them COMPREHENSIVE

## ✅ **WHAT TO DO** 
- Analyze COMPLETE source code first
- Fix ANY issues found (prerequisite)
- Create COMPREHENSIVE test restructuring
- Ensure all tests pass before moving on
- Check and resolve/ignore pylance warnings/errors