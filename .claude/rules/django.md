# Django Rules

- Prefer fat models only for simple domain behavior; use services for longer workflows
- Keep views and API endpoints thin
- Use explicit imports
- Add tests with every change
- Avoid hidden magic in signals unless already established in the codebase
- Use Clean Architecture principles so that code is modular, testable, and maintainable so that each app logic will be written into a concrete folder
- Follow the Single Responsibility Principle (SRP) for models, views, and services
- Use a functional approach for business logic
- Use functional programming principles (monads, currying, composition, etc.). Reuse existing functional libraries whenever possible. Usually those functions are stored in the Core folder
- Make sure that every single piece of code is type-safe (add types for functions, variables, etc.) and follows the principles of immutability and referential transparency
- Use a linter to enforce code style and consistency
