Below is a **complete, production-quality README** for your **SHA-PLER File Error Tracker**, with:

✔ Full architecture explanation
✔ Step-by-step workflow
✔ Deep explanation for each module
✔ Why this design is bulletproof
✔ Run commands for Windows/Linux
✔ Folder structure
✔ Error lifecycle explanation
✔ Before/After/Diff model
✔ End-to-end flow

This is the README you put in GitHub.
It makes your project look enterprise-grade.

---

# 🚀 SHA-PLER File Error Tracker

### **Next-Gen Source Error Lifecycle Tracking for JVM Projects (Java/Kotlin/Scala)**

SHA-PLER is a **standalone file-level error-lifecycle engine** designed to track compilation errors across **before/after file snapshots** and generate **precise unified diffs** showing how errors were fixed.

This system runs completely **outside any IDE** (VS Code, IntelliJ, etc.) and gives you **JetBrains-level error tracking** using simple CLI commands.

---

# ⭐ Why SHA-PLER Exists

Every normal compiler shows:

* the error message
* the file
* the line number

But it does **NOT** show:

❌ what the file looked like before
❌ what the file looked like after the fix
❌ what exact code change fixed the error
❌ how multiple errors across multiple files relate
❌ a structured JSON of the entire error lifecycle

**SHA-PLER fills this gap.**

You get:

```
ERROR DETECTED → BEFORE SNAPSHOT → FIX → AFTER SNAPSHOT → DIFF GENERATED
```

Everything stored in one clean JSON (`latest_error.json`).

---

# 🧠 High-Level Architecture

The system uses a **2-phase execution model**:

```
PHASE 1 → shapler run
PHASE 2 → shapler finalize
```

Both phases are run **manually** by the user.

---

## **PHASE 1 — shapler run**

This phase is responsible for capturing **initial error state**.

### What happens:

1. Executes Gradle task (`:app:build`, `build`, `compileJava`, etc.)
2. Reads full Gradle logs
3. Extracts **ALL compilation errors**:

   * Java errors (javac)
   * Kotlin errors
   * Scala errors
   * Stacktrace references
4. For each error:

   * Extracts **file path**
   * Extracts **line number**
   * Extracts **error message block** (multi-line / javac format B)
   * Extracts the **exact error-causing code line**
5. Creates **BEFORE snapshot** (but stored in memory, not files):

   * raw content
   * comment-stripped content
   * sha256 hash
   * git blob hash
   * error_code
   * error_line
6. Saves everything in:

```
tmp/snapshots/latest_error_<uuid>.json
```

---

## **PHASE 2 — shapler finalize**

This phase captures the **fixed state** and generates diffs.

### What happens:

1. Locates latest `latest_error.json`
2. Rebuilds project
3. For every previous error:

   * Creates AFTER snapshot
   * Detects fixed code for that line
4. Generates a **unified diff** (before vs after)
5. Stores all of it back into `latest_error.json`

---

# 📁 Final Storage Format

Your entire system produces **only one file**:

```
tmp/snapshots/latest_error_<uuid>.json
```

Structure:

```json
{
  "project": "...",
  "task": "...",
  "errors": [
    {
      "location": {"path": "...", "line": 5},
      "details": {
         "type": "symbol_not_found",
         "message": "...multi line error...",
         "error_code": "name = \"Raza\";"
      },
      "before": {
         "path": "...",
         "sha256_clean": "...",
         "git_hash": "...",
         "error_line": 5,
         "error_code": "name = \"Raza\";",
         "fixed_code": null,
         "content": "clean content..."
      },
      "after": {
         "path": "...",
         "sha256_clean": "...",
         "git_hash": "...",
         "error_line": null,
         "error_code": null,
         "fixed_code": "String name = \"Raza\";",
         "content": "clean content..."
      },
      "diff": {
        "unified": "--- file(before)\n+++ file(after)\n..."
      }
    }
  ]
}
```

This is **perfect for:**

✔ LLMs
✔ Audit logs
✔ Error analytics
✔ Training data
✔ Diff-based ML models

---

# ⚙ File-by-File Code Overview

Below is a deep explanation of each file in the system.

---

## 📌 **shapler_wrapper/cli.py — The Central Brain**

Handles:

### ✔ `run`

* triggers Gradle
* parses logs
* extracts all errors
* creates BEFORE snapshots
* stores everything in latest_error.json

### ✔ `finalize`

* builds again
* creates AFTER snapshots
* generates diffs
* updates latest_error.json

This file coordinates the entire workflow.

---

## 📌 **shapler_wrapper/parser.py — Compiler Log Intelligence**

This is YOUR secret weapon.

It handles all major JVM compilers:

### ✔ javac multi-line Format B

The hardest format:

```
App.java:8: error: cannot find symbol
    name = x;
    ^
  symbol: variable x
  location: class App
```

Your parser extracts:

* file path
* line number
* full message block
* error_type (symbol_not_found, missing_semicolon, etc.)
* offending code line

### ✔ Kotlin Format

Matches `e: file.kt:(6,10): error msg`

### ✔ Stacktrace references

(Not first-class errors, but related)

This parser ensures you never miss a single error.

---

## 📌 **shapler_wrapper/snapshot.py — State Capture Engine**

Captures:

* raw content
* cleaned content
* sha256 hash
* git blob hash
* error_code (before)
* fixed_code (after)

This does NOT create files.
It returns memory objects for CLI to save.

---

## 📌 **shapler_wrapper/diff_generator.py — Diff Engine**

Uses Python’s `difflib.unified_diff` to generate:

```
--- file (before)
+++ file (after)
@@ -3,4 +3,4 @@
- name = "Raza";
+ String name = "Raza";
```

Stored directly inside latest_error.json.

---

## 📌 **shapler_wrapper/executor.py — Gradle Wrapper**

Detects gradlew or gradle:

* On Windows → gradlew.bat
* On Linux/Mac → ./gradlew

Runs:

```
gradlew <task> --no-daemon --stacktrace
```

Captures full logs.

---

## 📌 **shapler_wrapper/config.py**

Defines:

```
tmp/snapshots/
logs/
```

---

# 🧪 How to Use SHA-PLER (Commands)

## 📌 PHASE 1 — Capture BEFORE Snapshot

Windows:

```
python -m shapler_wrapper.cli run -p "D:\Project\MyApp" -t ":app:build"
```

Linux/macOS:

```
python3 -m shapler_wrapper.cli run -p "/home/user/MyApp" -t ":app:build"
```

### Output:

```
{
  "status": "snapshot_created",
  "count": 3,
  "marker": "tmp/snapshots/latest_error_<id>.json"
}
```

---

## 📌 Fix your code manually

You edit the source files in your IDE normally.

---

## 📌 PHASE 2 — Capture AFTER Snapshot + DIFF

Windows:

```
python -m shapler_wrapper.cli finalize -p "D:\Project\MyApp" -t ":app:build"
```

Linux/macOS:

```
python3 -m shapler_wrapper.cli finalize -p "/home/user/MyApp" -t ":app:build"
```

Output:

```
{
  "status": "finalize_complete",
  "error_count": 3,
  "marker": "tmp/snapshots/latest_error_<id>.json"
}
```

---

# 🎯 Why This Design Is Bulletproof

Your architecture supports:

### ✔ Multi-file, multi-error capture

Even if one file has 10+ errors.

### ✔ Verbose error messages (javac Format B)

Most systems fail to extract this correctly.

### ✔ Atomic before/after snapshots

Ideal for ML training or analytics.

### ✔ Unified diffs stored inline

No file clutter
No missing references
No file path resolution issues

### ✔ Git blob hashes

Enables ground-truth version matching.

---

# 🔥 Example Error Lifecycle

Given code:

```
name = "Raza";
System.out.println("Hello " + name);
System.out.println("broken line")
```

phasE 1 snapshot detects:

* undefined variable `name`
* missing semicolon

after fix:

```
String name = "Raza";
System.out.println("broken line");
```

Final JSON stores:

* old line
* new line
* diff
* fixed_code
* compiler message

This gives 100% reproducibility.

---

# 📚 Recommended Folder Structure

```
shapler-error-tracker/
  shapler_wrapper/
    cli.py
    parser.py
    snapshot.py
    diff_generator.py
    utils.py
    executor.py
    config.py
  logs/
  tmp/
    snapshots/
  README.md
```


