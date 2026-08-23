# SmartLoan Analytics — Oral Defence Master Guide

## Core Questions Every Member Must Answer

### 1. What problem does the system solve?
It centralizes customer, loan and repayment data and converts operational records into useful
analytics and reports.

### 2. Why did you choose Tkinter?
It supports a Python desktop GUI without requiring a web server and is appropriate for the
assignment prototype.

### 3. Why SQLite?
It is lightweight, relational, transactional and appropriate for a local academic dataset.

### 4. Authentication vs authorization?
Authentication verifies identity. Authorization determines permitted actions.

### 5. Why hash passwords?
So the database does not store the original password in readable plain text.

### 6. What is a foreign key?
A field that references a key in another table and represents a relationship.

### 7. Explain Customer → Loan.
One customer can have many loans. Each loan belongs to one customer.

### 8. Explain Loan → Repayment.
One loan can receive multiple repayments.

### 9. What is encapsulation?
Grouping data/behaviour and controlling how internal details are accessed.

### 10. What is inheritance?
A specialized class derives common properties/behaviour from a parent class.

### 11. What is polymorphism?
Different objects can provide different implementations of a common operation, such as
role-specific permissions.

### 12. What is composition?
Building an object/system using other related objects or components.

## Algorithm Questions

### Why is eligibility O(1)?
There is no input-size-dependent loop. The algorithm performs a fixed set of arithmetic and
comparison operations.

### Why is repayment scheduling O(n)?
One schedule entry is created for each of n months.

### Why is schedule space O(n)?
The returned list stores n entries.

### Why is risk ranking O(n²)?
Selection sort contains nested loops and performs approximately n(n-1)/2 comparisons.

### Why not just call sorted()?
The manual algorithm demonstrates underlying ranking logic for the assignment. Production code
could use a more efficient built-in/database approach.

### If n doubles for O(n²), what happens?
Work can grow by approximately four times.

## Database Questions

### Why parameterized SQL?
It separates SQL structure from values and reduces injection risk.

### Why unique repayment references?
To reduce accidental duplicate transaction recording.

### What would you change for many simultaneous users?
Move from a local SQLite desktop architecture to a server database/client-server or web design.

## Validation Questions

Be prepared to demonstrate:
- missing field;
- invalid email;
- invalid phone;
- duplicate customer;
- invalid interest rate;
- invalid term;
- future repayment date;
- payment above outstanding balance.

## Live Coding Exercises

Practice each of these before assessment:

1. Change a validation range.
2. Add another loan purpose.
3. Change the risk weight for missed payments.
4. Return only the top five risky loans.
5. Change a report heading.
6. Add a field to a displayed table.
7. Modify an error message.
8. Write a small function and test it.
9. Fix an intentionally misspelled variable.
10. Add a simple validation test.

After every code change:
- explain what changed;
- save;
- run the relevant test;
- run `python -m pytest -q` if time permits.

## Debugging Scenario

If the lecturer introduces an error:
1. Read the error type and traceback.
2. Identify the file and line.
3. Inspect variable names/types and assumptions.
4. Make the smallest justified correction.
5. Run the affected function/test.
6. Explain why the correction works.

## Git Questions

Know:
- what Git is;
- why incremental commits matter;
- the difference between commit and push;
- what a tag represents;
- at least several actual commits in your repository.

Never invent an explanation for a commit you cannot show.

## Final Defence Rule

Do not memorize only definitions. Practice tracing actual code with sample values.
