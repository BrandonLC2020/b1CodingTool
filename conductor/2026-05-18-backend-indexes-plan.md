# Backend Indexes Guidelines Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enhance Django, FastAPI, and Django-Ninja modules by adding specific database index guidelines to their `best-practices.md` files for efficiency and performance.

**Architecture:** We will update the markdown documentation files (context files) for each of the three backend frameworks to explicitly define how and when to create database indexes.

**Tech Stack:** Markdown, Django, FastAPI (SQLAlchemy), Django-Ninja

---

### Task 1: Update Django Best Practices

**Files:**
- Modify: `modules/framework/django/context/best-practices.md`

- [ ] **Step 1: Add Indexing Guidelines**

Find the `## Models & ORM` section and add the following bullet points at the end of the section:

```markdown
- **Database Indexes:** Always evaluate query patterns and add indexes for performance.
  - Use `db_index=True` on fields that are frequently used in `.filter()`, `.exclude()`, or `order_by()`.
  - Use `class Meta: indexes = [...]` for composite indexes (filtering on multiple columns together) or when using specific index types (e.g., `GinIndex`, `BrinIndex`).
  - Avoid creating indexes on low-cardinality fields (like `BooleanField`) unless the data is highly skewed.
  - Remember that `unique=True` and `ForeignKey` automatically create an index.
```

- [ ] **Step 2: Commit**

```bash
git add modules/framework/django/context/best-practices.md
git commit -m "docs(django): add database indexing guidelines for performance"
```

---

### Task 3: Update FastAPI Best Practices

**Files:**
- Modify: `modules/framework/fastapi/context/best-practices.md`

- [ ] **Step 1: Add Indexing Guidelines**

Find the `## SQLAlchemy 2.x Async` section and add the following bullet points at the end of the section:

```markdown
- **Database Indexes:** Proactively add indexes to columns frequently queried or sorted.
  - Use `index=True` in `mapped_column()` for single-column indexes (e.g., `email: Mapped[str] = mapped_column(String, index=True)`).
  - Use the `Index` construct inside `__table_args__` for composite indexes or advanced indexing configurations:
    ```python
    __table_args__ = (
        Index("ix_user_status_created", "status", "created_at"),
    )
    ```
  - Rely on `unique=True` for constraints, as it automatically creates a unique index.
```

- [ ] **Step 2: Commit**

```bash
git add modules/framework/fastapi/context/best-practices.md
git commit -m "docs(fastapi): add database indexing guidelines to best practices"
```

---

### Task 4: Update Django-Ninja Best Practices

**Files:**
- Modify: `modules/framework/django-ninja/context/best-practices.md`

- [ ] **Step 1: Add Indexing Guidelines**

Find the `## Performance` section and add the following bullet point:

```markdown
- **Database Indexing:** Ensure underlying Django models are properly indexed (`db_index=True` or `Meta.indexes`) for fields frequently used in API filtering, sorting, or lookups to maintain fast response times.
```

- [ ] **Step 2: Commit**

```bash
git add modules/framework/django-ninja/context/best-practices.md
git commit -m "docs(django-ninja): add database indexing guidelines"
```
