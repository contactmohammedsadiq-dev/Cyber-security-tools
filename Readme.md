# pentoolkit — Simple Penetration Testing Orchestrator

**Purpose:**
A tiny, single-file toolkit that orchestrates common recon and scanning tools (passive/active subdomain enumeration, archive URL gathering, directory fuzzing, service discovery, and template-based vulnerability scanning). This wrapper is designed for **authorized, educational, and lab testing only**.

> ⚠️ **Legal / Safety Notice:** Only run this against systems you own or have written permission to test. Unauthorized scanning is illegal and unethical.

---

## Features

* Passive subdomain enumeration using `amass`, `subfinder`, and `assetfinder` (if installed).
* Archive URL harvesting via `waybackurls`.
* Directory fuzzing with `ffuf` or `dirsearch` (if installed).
* Service discovery using `nmap` (non-intrusive by default).
* Vulnerability scanning orchestration using `nuclei` templates.
* Saves all outputs to `./results/<target>_<timestamp>/` for easy triage.

---

## What this is **not**

* Not an exploit framework. It does not include exploit payloads or automated exploitation steps.
* Not a magic one-click scanner — it's an orchestrator that relies on well-known OSS tools.

---

## Prerequisites

Install the external tools separately and ensure they are in your `PATH`:

* `amass` (optional but recommended)
* `subfinder`
* `assetfinder`
* `waybackurls`
* `ffuf` or `dirsearch`
* `nmap`
* `nuclei`

Recommended wordlists: [SecLists](https://github.com/danielmiessler/SecLists) (or any wordlist you trust).

---

## Files

* `pentoolkit.py` — the main Python wrapper script.
* `README.md` — this file.
* `results/` — output directory created when the script runs.

---

## Quick Install (example)

1. Clone or copy the files to a local directory.
2. Make sure Python 3 is available: `python3 --version`.
3. Install any external tools you plan to use and add them to `PATH`.
4. (Optional) Update the `WORDLIST` variable in `pentoolkit.py` to point to your preferred wordlist.

---

## Usage

```bash
python3 pentoolkit.py example.com
```

The script will prompt you to type `I_HAVE_PERMISSION` before proceeding.

---

## What to expect (outputs)

When you run the script, a folder will be created like:

```
results/example.com_20250101T120000Z/
```

Inside you will see files such as:

* `amass.txt`, `subfinder.txt`, `assetfinder.txt` — raw tool outputs
* `subdomains.txt` — merged passive subdomain list
* `archived_urls.txt` — URLs from Wayback/archives
* `fuzzing/` — fuzzing results (ffuf/dirsearch)
* `nmap.xml` — nmap scan (XML format)
* `nuclei.txt` — nuclei findings

Use these outputs to triage manually or feed into an internal reporting tool.

---

## Tips & Improvements

* Start with small wordlists and low thread counts to avoid overloading targets.
* Add rate limiting or sleep between requests when scanning production systems.
* Parse `nuclei` and `nmap` outputs into CSV/HTML for triage.
* Add a Dockerfile for a lab-only image (isolates toolchain).

---

## Safety & Ethics

* Get written permission (scope, allowed IPs/domains, and testing window) before scanning.
* Disclose findings responsibly to the asset owner.
* Do not perform destructive testing without coordination.

---

## Contributing

This is intentionally simple. If you'd like features or improvements, open a PR or submit an issue with the requested change.

---

## License

Use this code at your own risk. No warranty is provided. Include your preferred license when publishing publicly (e.g., MIT).

---


