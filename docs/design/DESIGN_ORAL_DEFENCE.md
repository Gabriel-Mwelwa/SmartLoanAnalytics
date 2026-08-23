# Phase 10 — Design Oral Defence Quick Sheet

## Why Tkinter?
Tkinter is included with standard Python distributions, is suitable for a desktop academic
prototype and allows the group to demonstrate event-driven GUI programming without requiring
a web server.

## Why SQLite?
SQLite is lightweight, file-based, transactional and appropriate for a single-computer
prototype with hundreds of records. A production multi-user system could migrate to
PostgreSQL or another server database.

## Why a Layered Design?
Separating GUI, business rules, algorithms, analytics/reporting and database responsibilities
reduces coupling and makes testing and maintenance easier.

## What is the difference between the Class Diagram and ERD?
The class diagram represents object-oriented software concepts and relationships. The ERD
represents persistent database entities, keys and relationships.

## Why are Customer and Loan one-to-many?
One customer may apply for zero, one or many loans, while every loan belongs to one customer.

## Why are Loan and Repayment one-to-many?
A loan may receive multiple installment payments.

## What is a functional requirement?
It states what the system must do, such as register a repayment.

## What is a non-functional requirement?
It describes a quality or constraint, such as security, maintainability or performance.

## Live Defence Practice
Students should be able to:
1. Add a new field to Customer and explain what layers would change.
2. Add a new use case such as "Export Customer Statement".
3. Explain a foreign key.
4. Explain why deleting a customer with loan history can damage referential/business integrity.
5. Trace one loan from GUI input to validation, business logic, SQL storage and reporting.
