# Excel Data Test Analysis Report
## Generated using LlamaIndex Approach with HuggingFace

---

## 1. TEST SCENARIOS

| # | Scenario Name | Description | Business Value | Risk Level |
|---|----------------|-------------|----------------|------------|
| 1 | **Primary Key Uniqueness & Auto‑Increment** | Verify that every table has a single, non‑NULL, auto‑incremented PK that is unique. | Guarantees entity identity – essential for relational integrity and auditability. | **High** |
| 2 | **Foreign Key Referential Integrity** | Confirm that all FK columns (`researcher_type_id`, `researcher_id`, `compound_id`, `lead_researcher_id`) reference existing parent rows and that cascade rules are respected. | Prevents orphan records that break business logic and reporting. | **High** |
| 3 | **Mandatory Field Validation** | Ensure all “Required” columns are non‑NULL and meet length/format constraints (e.g., `email`, `password`, `employee_id`). | Guarantees that critical user data is always present – critical for authentication and audit. | **High** |
| 4 | **Uniqueness & Business Rules** | Validate that columns flagged as `Unique` (e.g., `email`) are truly unique and that business rules (e.g., `principal_investigator` can only have `researcher_type_id = PI`) hold. | Avoids duplicate accounts and enforces role‑based access. | **Medium** |
| 5 | **Data Quality & Consistency** | Check for data type mismatches, out‑of‑range values, and missing values in optional fields that are expected to be populated in certain contexts (e.g., `lead_researcher_id` must be present when `status = ‘Active’`). | Improves reporting accuracy and reduces downstream errors. | **Medium** |
| 6 | **Security & Encryption** | Verify that password hashes are stored, not plain text, and that authentication tokens are stored securely. | Protects user credentials and complies with data‑privacy regulations. | **High** |
| 7 | **Performance & Scalability** | Validate that queries (e.g., joins between `research_studies` and `compounds`) return within acceptable thresholds as row counts grow. | Ensures a responsive system for end users. | **Low** |
| 8 | **Edge‑Case & Boundary Testing** | Test extreme values such as very long strings, zero or negative IDs, and null FK values where optional. | Detects hidden bugs that could surface under load or data migration. | **Medium** |

---

## 2. TEST CASES

| Test ID | Test Name | Objective | Prerequisites | Test Steps | Expected Results | Test Data Required | Priority |
|---------|-----------|-----------|---------------|------------|------------------|--------------------|----------|
| TC‑001 | **PK Uniqueness – Researchers** | Verify `researchers.id` is unique and auto‑incremented. | Create 100 dummy researcher rows. | 1. Insert 100 rows with `id` omitted. 2. Query `SELECT id FROM researchers;` 3. Check count = 100. | All 100 IDs are distinct and sequential starting at 1. | 100 random `employee_id`, `email`, etc. | P1 |
| TC‑002 | **FK Integrity – researcher_type_id** | Ensure `researcher_type_id` in `researchers` references `researcher_types.id`. | Populate `researcher_types` with 4 rows. | 1. Insert researcher with `researcher_type_id = 99`. 2. Expect FK violation. | Transaction fails, error message “FK constraint violated.” | 1 researcher row with invalid FK. | P1 |
| TC‑003 | **Mandatory Field – Email** | Verify `email` cannot be NULL or empty. | `researchers` table exists. | 1. Attempt to insert row with `email = NULL`. 2. Expect error. | Insertion fails with NOT NULL constraint. | 1 row with NULL email. | P1 |
| TC‑004 | **Unique Email Constraint** | Ensure two researchers cannot share the same email. | Insert researcher with `email = test@example.com`. | 1. Insert second researcher with same email. 2. Expect unique constraint violation. | Transaction fails with UNIQUE constraint error. | 2 rows with same email. | P1 |
| TC‑005 | **Password Hash** | Verify passwords are stored as hash, not plain text. | Insert researcher with `password = 'secret'`. | 1. Query `SELECT password FROM researchers WHERE email='...'`. 2. Expect hash string (e.g., 60 chars bcrypt). | Stored value differs from plain text. | Plain password string. | P1 |
| TC‑006 | **Lead Researcher Mandatory on Active Study** | Validate that `lead_researcher_id` is required when `status='Active'`. | Insert `research_studies` row with `status='Active'` and NULL `lead_researcher_id`. | 1. Attempt insert. 2. Expect constraint or trigger error. | Insertion fails. | 1 row with status=Active, lead=NULL. | P2 |
| TC‑007 | **Data Type Truncation – employee_id** | Ensure `employee_id` varchar(50) does not truncate longer values. | Insert `employee_id` with 60 characters. | 1. Insert row. 2. Query length. | Stored length = 60; value not truncated if column is varchar(255). | 1 long string. | P2 |
| TC‑008 | **Referential Integrity – Compound in Study** | Verify `compound_id` in `research_studies` refers to `compounds.id`. | Populate `compounds` with 10 rows. | 1. Insert study with `compound_id=9999`. 2. Expect FK error. | Transaction fails. | 1 study row with invalid FK. | P1 |
| TC‑009 | **Optional Field Null Acceptance – Notes** | Test that optional `Notes` can be NULL or empty. | Insert researcher with `Notes=NULL`. | 1. Insert row. 2. Query. | Row inserted, `Notes` = NULL. | 1 row with NULL notes. | P3 |
| TC‑010 | **Performance – Join Count** | Ensure that a join between `research_studies` and `compounds` returns within 500 ms with 10k rows. | Seed database with 10k studies and 5k compounds. | 1. Run `SELECT COUNT(*) FROM research_studies rs JOIN compounds c ON rs.compound_id=c.id;` 2. Measure latency. | Query completes < 500 ms. | 10k study rows, 5k compound rows. | P2 |
| TC‑011 | **Edge Case – Negative ID** | Verify system rejects negative PK values. | Attempt to insert researcher with `id=-5`. | 1. Insert row. 2. Expect error. | Insertion fails; PK auto‑increment prevents negative values. | 1 row with negative ID. | P2 |
| TC‑012 | **Data Quality – Email Format** | Validate that `email` follows RFC‑5322 pattern. | Insert researcher with `email='notanemail'`. | 1. Attempt insert. 2. Expect validation failure. | Insertion fails or triggers a validation error. | 1 invalid email. | P2 |

---

## 3. SQL VALIDATION QUERIES

1. **Duplicate Primary Keys (Data Integrity)**
   ```sql
   SELECT id, COUNT(*) AS dup_count
   FROM researchers
   GROUP BY id
   HAVING COUNT(*) > 1;
   ```

2. **Foreign Key Referential Integrity (researcher_type_id)**
   ```sql
   SELECT r.id
   FROM researchers r
   LEFT JOIN researcher_types rt ON r.researcher_type_id = rt.id
   WHERE rt.id IS NULL;
   ```

3. **Unique Email Enforcement (Business Rule)**
   ```sql
   SELECT email, COUNT(*) AS c
   FROM researchers
   GROUP BY email
   HAVING COUNT(*) > 1;
   ```

4. **Password Hash Length & Pattern (Security)**
   ```sql
   SELECT id, password
   FROM researchers
   WHERE LENGTH(password) < 60
      OR password NOT REGEXP '^[A-Za-z0-9+/]+={0,2}$';
   ```

5. **Performance Benchmark – Join Latency**
   ```sql
   /* Run with EXPLAIN ANALYZE to capture actual time */
   EXPLAIN ANALYZE
   SELECT COUNT(*) 
   FROM research_studies rs
   JOIN compounds c ON rs.compound_id = c.id;
   ```

6. **Edge‑Case Null FK (study_participants)**
   ```sql
   SELECT * 
   FROM study_participants 
   WHERE researcher_id IS NULL
      OR study_id IS NULL;
   ```

7. **Data Quality – Null Optional Fields (Notes)**
   ```sql
   SELECT *
   FROM researchers
   WHERE notes IS NULL
      OR TRIM(notes) = '';
   ```

8. **Constraint Enforcement – lead_researcher_id on Active Study**
   ```sql
   SELECT *
   FROM research_studies
   WHERE status = 'Active'
      AND lead_researcher_id IS NULL;
   ```

9. **Referential Integrity – compound_id in studies**
   ```sql
   SELECT rs.id
   FROM research_studies rs
   LEFT JOIN compounds c ON rs.compound_id = c.id
   WHERE c.id IS NULL;
   ```

10. **Data Consistency – researcher_type_id mapping**
    ```sql
    SELECT r.id, rt.type_name
    FROM researchers r
    JOIN researcher_types rt ON r.researcher_type_id = rt.id
    WHERE rt.access_level NOT IN ('scientist','lab_tech','data_analyst','principal_investigator');
    ```

---

## 4. DATA QUALITY CHECKS

| Issue | Description | Validation Rule | Cleansing Action |
|-------|-------------|-----------------|-----------------|
| **Duplicate PKs** | Same ID in a table | Check for duplicates (`COUNT(*)>1`) | Remove or re‑generate IDs |
| **Broken FK** | Child row references non‑existent parent | Verify FK existence | Add missing parent or delete child |
| **Null Mandatory Fields** | Required columns contain NULL | `NOT NULL` constraints + data scan | Populate defaults or delete row |
| **Email Format** | Invalid email strings | Regex match | Correct or discard row |
| **Password Plain Text** | Password stored unencrypted | Check for length/complexity | Re‑hash using bcrypt |
| **Over‑long Strings** | Data truncated on insert | Column length < data length | Increase column length or truncate data |
| **Missing Optional Data** | `Notes` or `description` empty but required for certain statuses | Business rule | Prompt for completion or set default |
| **Out‑of‑Range Values** | `status` not in allowed set (`Active`, `Completed`, `Closed`) | ENUM check | Correct status |
| **Duplicate Emails** | Two accounts share same email | Unique constraint | Merge/delete duplicate |
| **Stale Tokens** | Authentication tokens older than policy period | Token age > threshold | Re‑issue token |

---

## 5. TEST AUTOMATION STRATEGY

| Area | Recommended Tests to Automate | Framework / Tool | CI/CD Integration | Test Data Management |
|------|-----------------------------|------------------|-------------------|----------------------|
| **Database Layer** | PK/Unique checks, FK integrity, mandatory field validation, security hash checks, performance queries | **pytest + SQLAlchemy +