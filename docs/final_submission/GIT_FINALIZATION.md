# Git Finalization Guide

The assignment requires at least 15 meaningful commits. Use the repository's **real**
development history. Do not fabricate historical commits.

## Check History

```bash
git status
git log --oneline --decorate
```

Confirm that the repository contains at least 15 genuine incremental commits.

## Examples of Meaningful Development Areas

Your actual history should ideally contain commits corresponding to work such as:

1. Initialize SmartLoan project structure
2. Create SQLite schema and configuration
3. Add logging and domain models
4. Implement registration and password hashing
5. Add login and role-based access
6. Implement customer management
7. Implement loan application workflow
8. Add approval and disbursement
9. Implement repayments and penalties
10. Add analytics dashboard
11. Add Matplotlib visualizations
12. Add PDF and CSV reports
13. Improve validation and exception handling
14. Add automated tests
15. Add 650-record synthetic dataset
16. Document algorithms and complexity
17. Add UML/system design documentation
18. Add technical report and user manual
19. Add final presentation and defence material

These are examples only. Do not create false commits merely to imitate this list.

## Final Genuine Commit

After reviewing the final files:

```bash
git add .
git commit -m "Prepare SmartLoan Analytics final submission and defence materials"
```

## Run Tests Before Tagging

```bash
python -m pytest -q
```

## Create Final Release Tag

Only after the final commit and successful tests:

```bash
git tag -a v1.0.0 -m "SmartLoan Analytics final academic release"
```

Check:

```bash
git tag
git show v1.0.0
```

Push according to the repository hosting setup:

```bash
git push
git push --tags
```
