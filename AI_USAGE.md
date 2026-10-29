# AI Usage

## 1. AI Tools Used

I used Claude (Anthropic) to assist with the development of this project.

The AI was used as a coding assistant to help generate the initial implementation, suggest improvements, create tests, and review the solution. All generated code was reviewed and verified before final submission.

---

## 2. Prompts I Provided

### Prompt 1

> I have a Django assignment for a 3D bin-packing and box selection system. Read the requirements carefully and create a complete Django solution with models, algorithms, API endpoints, tests, documentation, and project structure. The solution should follow clean coding practices and be easy to test.

### Output Accepted

- Initial Django project structure
- Models for products and boxes
- Packing algorithm implementation
- REST API endpoint structure
- Documentation outline

---

### Prompt 2

> Implement the packing algorithm separately from the Django code so that it can be unit tested independently. The algorithm should determine whether products fit inside available boxes and select the most cost-effective box.

### Output Accepted

- Separate `algorithm.py` module
- Packing logic isolated from Django views
- Reusable and testable implementation

---

### Prompt 3

> Create a box selection strategy that chooses the cheapest available box. If multiple boxes have the same price, select the one with smaller volume. If volume is also the same, choose alphabetically by box name.

### Output Accepted

- Cheapest-box selection rule
- Tie-breaking logic
- Deterministic results

---

### Prompt 4

> Generate Django API endpoints that accept product quantities and return the selected box along with item placements in JSON format.

### Output Accepted

- API request validation
- JSON response structure
- Error handling

---

### Prompt 5

> Create comprehensive unit tests for the packing algorithm and Django API. Include edge cases and validation tests.

### Output Accepted

- Algorithm test suite
- API tests
- Edge-case coverage

---

### Prompt 6

> Review the entire project for potential bugs, code quality improvements, documentation issues, and test coverage gaps.

### Output Accepted

- Code review suggestions
- Documentation improvements
- Minor bug fixes

---

## 3. AI Output I Accepted

The following AI-generated outputs were accepted with little or no modification:

- Project folder structure
- Django models
- Packing algorithm architecture
- API implementation
- Unit test structure
- README documentation
- CI workflow configuration

I accepted these outputs because they aligned with the assignment requirements and followed good software engineering practices.

---

## 4. AI Output I Modified

Although the AI generated most of the initial implementation, I reviewed and modified several areas:

- Corrected packing test expectations.
- Improved code readability.
- Adjusted edge-case handling.
- Refined documentation wording.
- Verified API responses manually.
- Updated comments and naming conventions where necessary.

These modifications ensured that the solution matched the assignment requirements exactly.

---

## 5. Mistakes Made by the AI

During development, I identified the following issues:

### Incorrect Test Assumption

The AI initially assumed that a mug would fit inside the "Mailer XS" box. After reviewing the dimensions, it became clear that the mug's smallest side was larger than the box height. The expected result was corrected to "Box S".

### Environment Limitation

The AI environment could not install Django packages, so only the pure algorithm tests were executed by the AI. The complete Django test suite was executed later on my local machine.

### Manual Fixes

I manually reviewed the generated solution and corrected any issues found during local testing before final submission.

---

## 6. How I Verified the Final Code

### Automated Testing

```bash
python manage.py test -v 2
```

I executed the complete Django test suite locally and confirmed that all tests passed successfully.

### Algorithm Validation

The algorithm was verified using an independent validation function that checked:

- Every product remained inside the selected box.
- No items overlapped.
- Placement coordinates were valid.

### Manual Testing

I manually tested:

- Valid product combinations
- Invalid product requests
- Edge cases
- API responses
- Error handling
- Output format requirements

### Final Review

Before submission, I performed a full review of:

- Project structure
- Coding standards
- Documentation
- Test coverage
- Assignment requirements

This process ensured that the final solution was correct, stable, and ready for submission.