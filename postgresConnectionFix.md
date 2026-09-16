# Fix: `permission denied for schema public` on PostgreSQL (SQLAlchemy + FastAPI)

## Symptom

App works fine with SQLite. Switching `DATABASE_URL` to PostgreSQL, `Base.metadata.create_all(bind=engine)` fails with:

```
sqlalchemy.exc.ProgrammingError: (psycopg.errors.InsufficientPrivilege) permission denied for schema public
LINE 2: CREATE TABLE tags (
                     ^
```

Connection succeeds, SQLAlchemy can introspect existing tables, but it fails the moment it tries to `CREATE TABLE`.

## Root cause

Since **PostgreSQL 15**, the `public` schema no longer grants `CREATE` to all users by default. Only the **schema owner** (usually the DB owner, e.g. `postgres` or whoever created the database) can create objects in `public` out of the box.

If your app connects as a different role (e.g. `cuellar`) than the one that created the database (e.g. `danielgalvan`), that role has no `CREATE` rights on `public` — even if it has full privileges on the database itself.

### Important gotcha

`GRANT ALL PRIVILEGES ON DATABASE <db> TO <role>;` does **NOT** grant privileges on the `public` schema inside that database. Database-level grants (`CONNECT`, `TEMP`, `CREATE` *for new schemas*) are separate from schema-level grants (`CREATE`, `USAGE` *inside* `public`). This is the mistake that caused the error to persist even after granting "ALL" on the database.

## Fix

You must connect **to the specific database** (not `postgres`, not any other db) and grant on the schema **from inside it**:

```bash
psql -U danielgalvan -d blogfastapi
```

Confirm you're in the right database:

```sql
SELECT current_database();
-- must return: blogfastapi
```

Then grant schema-level privileges to the app's role:

```sql
GRANT ALL ON SCHEMA public TO cuellar;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO cuellar;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO cuellar;
```

Verify:

```sql
\dn+ public
```

`cuellar` should now appear in the schema's access privileges list, e.g. `cuellar=CTc/danielgalvan`.

Restart the app — `Base.metadata.create_all(bind=engine)` should now succeed.

## Alternative (simpler for local dev)

Make the app's role the owner of the database and schema:

```sql
ALTER DATABASE blogfastapi OWNER TO cuellar;
ALTER SCHEMA public OWNER TO cuellar;
```

Database ownership does not automatically imply schema ownership — both statements are usually needed.

## Checklist when this happens again

- [ ] Confirm which role the app actually connects as (check `DATABASE_URL`)
- [ ] Confirm you're granting **on the correct database** (`\c <dbname>` or `psql -d <dbname>` first)
- [ ] Grant on the **schema**, not just the database:
      `GRANT ALL ON SCHEMA public TO <role>;`
- [ ] Check current grants with `\dn+ public` before and after
- [ ] Remember: PG15+ changed the default — `public` is no longer world-writable

## Unrelated cleanup noted during debugging

The junction table was originally named `"post-tags"` (hyphenated). Hyphens in unquoted Postgres identifiers cause friction (must always be quoted in raw SQL). Renamed to `post_tags`:

```python
post_tags = Table(
    "post_tags",  # underscore, not hyphen
    Base.metadata,
    ...
)
```