# Data Loss Prevention (DLP) Agent

## Phase 0 – Requirements & Design Specification

**Document Version:** 1.0
**Status:** Frozen (Baseline for Phase 1)
**Target Audience:** Security Engineers, Backend Engineers, DevOps, Compliance Teams

---

## 1. Purpose of This Document

This document formally defines the **Phase 0 requirements and design constraints** for the DLP Agent. It establishes a clear contract describing **what the agent must do, how it behaves, and what it must never do**.

No implementation details are included in this phase. This document acts as the foundation for all subsequent development phases.

---

## 2. System Objective

The DLP Agent is a **node-installed security agent** designed to detect and report the presence of sensitive personal and financial data within files and logs on host systems.

### Primary Goals

* Detect regulated sensitive data
* Prevent accidental data leakage
* Provide visibility without modifying user data
* Operate with minimal performance overhead

### Non-Goals (Phase 0)

* Blocking or quarantining files
* Machine learning–based detection
* Endpoint user interaction

---

## 3. Supported Sensitive Data Types

### 3.1 Credit & Debit Card Numbers

**Description:** Payment card numbers (Visa, MasterCard, etc.)

**Format Rules:**

* Length: 13–19 digits
* Optional separators: spaces or hyphens

**Detection Method:**

* Regex pattern matching
* Mandatory Luhn checksum validation

**Severity Level:** HIGH

---

### 3.2 Aadhaar Number (India)

**Description:** Unique Identification Number issued by UIDAI

**Format Rules:**

* Exactly 12 digits
* First digit must be between 2–9
* Optional space separation

**Detection Method:**

* Regex validation
* Format validation
* Repeated-digit exclusion

**Severity Level:** CRITICAL

**Compliance Note:** Aadhaar numbers must never be stored or transmitted in raw form.

---

### 3.3 PAN (India)

**Description:** Permanent Account Number issued by Income Tax Department

**Format Rules:**

* 5 uppercase letters
* 4 digits
* 1 uppercase letter

**Detection Method:**

* Strict regex
* Case-insensitive matching

**Severity Level:** HIGH

---

### 3.4 Out-of-Scope Data Types

The following are explicitly excluded in Phase 0:

* Bank account numbers
* Phone numbers
* Email addresses
* Passport numbers

---

## 4. Detection Strategy

### 4.1 Layered Detection Model

Detection is performed in sequential layers:

1. Raw text extraction
2. Regex-based pattern matching
3. Validation (checksum or structural validation)
4. Policy evaluation

Regex-only detection is not acceptable without validation.

---

### 4.2 Exclusion of Machine Learning

Machine learning–based detection is excluded due to:

* Increased false positives
* Reduced explainability
* Higher CPU and memory cost
* Audit and compliance challenges

---

## 5. Scan Scope

### 5.1 Supported File Types

The agent is permitted to scan the following text-based formats:

* .txt
* .log
* .csv
* .json
* .xml
* .md

---

### 5.2 Unsupported File Types

The agent must not scan the following:

* Executables (.exe, .dll, .so)
* Archives (.zip, .rar, .7z)

Reason: performance overhead and low signal value.

---

### 5.3 Directory Scope

**Default Allowed Paths:**

* /home
* /var/log
* /app/data

**Default Excluded Paths:**

* /proc
* /sys
* /dev
* /node_modules
* /.git

All paths must be configurable.

---

## 6. Scanning Modes

The agent supports the following scan modes (definition only):

* On-demand scan
* Scheduled scan
* Real-time file monitoring

Implementation details are deferred to later phases.

---

## 7. File Handling Constraints

* Maximum file size: 10 MB
* Files must be read in chunks
* Binary files must be skipped
* No file modifications are allowed

---

## 8. Data Handling & Privacy Rules

### 8.1 Prohibited Actions

The agent must never:

* Store raw sensitive data
* Transmit unmasked identifiers
* Log sensitive values in plaintext
* Modify or block files

---

### 8.2 Allowed Actions

The agent may:

* Detect sensitive data
* Mask data before storage or transmission
* Hash values for deduplication
* Send metadata to a backend service

---

### 8.3 Masking Rules

| Data Type | Masking Format   |
| --------- | ---------------- |
| Aadhaar   | XXXX XXXX 9012   |
| PAN       | ABCDE****F       |
| Card      | ************1111 |

---

## 9. Policy Configuration Model

All detection behavior must be policy-driven.

**Sample Policy Structure:**

```json
{
  "rules": {
    "aadhaar": { "enabled": true, "severity": "CRITICAL" },
    "pan": { "enabled": true, "severity": "HIGH" },
    "card": { "enabled": true, "severity": "HIGH" }
  }
}
```

---

## 10. Performance Constraints

| Metric          | Target      |
| --------------- | ----------- |
| CPU usage       | < 5%        |
| Memory usage    | < 150 MB    |
| Scan throughput | ≥ 20 MB/s   |
| Startup time    | < 2 seconds |

---

## 11. Security Constraints

* Agent must run with least privilege
* Read-only filesystem access
* Configuration file permissions: 600
* Log rotation enabled

---

## 12. Legal & Compliance Considerations (India)

* Aadhaar Act compliance required
* Aadhaar data must not persist
* Masking is mandatory
* Scan paths must be explicitly configured

---

## 13. Phase 0 Exit Criteria

Phase 0 is considered complete when:

* Supported data types are finalized
* Detection rules are frozen
* Scan boundaries are defined
* Masking rules are approved
* Performance and security constraints are agreed upon

Any future changes require a documented version increment.

---
