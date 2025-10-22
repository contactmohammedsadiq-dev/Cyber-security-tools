#!/usr/bin/env python3
"""
pentoolkit.py — simple pentest orchestration wrapper (educational & for authorized testing only)

Dependencies (install separately):
 - amass, subfinder, assetfinder, waybackurls, ffuf, dirsearch, nuclei, nmap
(Install from each project's official repos / package manager)

Usage:
    python3 pentoolkit.py example.com

Outputs are saved to ./results/<target>/
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime

# --- CONFIG ---
TOOLS = {
    "amass": "amass",
    "subfinder": "subfinder",
    "assetfinder": "assetfinder",
    "waybackurls": "waybackurls",
    "ffuf": "ffuf",
    "dirsearch": "dirsearch",
    "nuclei": "nuclei",
    "nmap": "nmap",
}
RESULTS_DIR = "results"
# wordlist path — change to your preferred list
WORDLIST = "/usr/share/wordlists/seclists/Discovery/Web-Content/common.txt"

# --- HELPERS ---
def has_tool(name):
    return shutil.which(name) is not None

def run(cmd, outpath=None, silent=False):
    print(f"[+] running: {' '.join(cmd)}")
    with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as p:
        out_lines = []
        for line in p.stdout:
            if not silent:
                print(line.rstrip())
            out_lines.append(line)
    if outpath:
        with open(outpath, "w", encoding="utf-8") as f:
            f.writelines(out_lines)
    return "".join(out_lines)

def ensure_dir(path):
    os.makedirs(path, exist_ok=True)

# --- MAIN FLOW ---
def main(target):
    if not target:
        print("Usage: python3 pentoolkit.py <target-domain>")
        sys.exit(1)

    print("=== SIMPLE PENTEST TOOLKIT (educational) ===")
    print("Authorization check: you MUST have explicit permission to test this target.")
    ack = input("Type I_HAVE_PERMISSION to continue: ").strip()
    if ack != "I_HAVE_PERMISSION":
        print("Permission not confirmed. Exiting.")
        sys.exit(1)

    ts = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    base = os.path.join(RESULTS_DIR, target.replace("/", "_") + "_" + ts)
    ensure_dir(base)

    # 1) Passive subdomain enumeration
    subdomains_file = os.path.join(base, "subdomains.txt")
    subs = set()

    # amass (passive + active if available)
    if has_tool(TOOLS["amass"]):
        out = run([TOOLS["amass"], "enum", "-passive", "-d", target], outpath=os.path.join(base, "amass.txt"), silent=True)
        for line in out.splitlines():
            if line.strip() and "." in line:
                subs.add(line.strip())

    # subfinder (fast passive)
    if has_tool(TOOLS["subfinder"]):
        out = run([TOOLS["subfinder"], "-d", target, "-silent"], outpath=os.path.join(base, "subfinder.txt"), silent=True)
        for line in out.splitlines():
            if line.strip(): subs.add(line.strip())

    # assetfinder
    if has_tool(TOOLS["assetfinder"]):
        out = run([TOOLS["assetfinder"], target], outpath=os.path.join(base, "assetfinder.txt"), silent=True)
        for line in out.splitlines():
            if line.strip(): subs.add(line.strip())

    # write merged list
    with open(subdomains_file, "w", encoding="utf-8") as f:
        for s in sorted(subs):
            f.write(s + "\n")
    print(f"[+] Passive subdomain enumeration complete — {len(subs)} entries saved to {subdomains_file}")

    # 2) Collect URLs from Wayback / archives
    urls_file = os.path.join(base, "archived_urls.txt")
    if has_tool(TOOLS["waybackurls"]):
        # feed the subdomains into waybackurls
        wayback_out = run([TOOLS["waybackurls"]], outpath=None, silent=True) if False else None
        # safer: run per-domain using subprocess stdin
        with open(subdomains_file, "r", encoding="utf-8") as sfd, open(urls_file, "w", encoding="utf-8") as outf:
            for line in sfd:
                d = line.strip()
                if not d: continue
                proc = subprocess.Popen([TOOLS["waybackurls"], d], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
                for u in proc.stdout:
                    outf.write(u)
    print(f"[+] Archived URLs saved to {urls_file}")

    # 3) Directory fuzzing (use ffuf if available; fallback to dirsearch)
    fuzz_dir = os.path.join(base, "fuzzing")
    ensure_dir(fuzz_dir)
    if has_tool(TOOLS["ffuf"]) and os.path.exists(WORDLIST):
        # Note: keep request rate low by default. User can edit the command below.
        first_host = None
        with open(subdomains_file, "r", encoding="utf-8") as f:
            for line in f:
                host = line.strip()
                if host:
                    first_host = host
                    break
        if first_host:
            url = f"https://{first_host}/FUZZ"
            outpath = os.path.join(fuzz_dir, f"ffuf_{first_host.replace('/', '_')}.txt")
            run([TOOLS["ffuf"], "-u", url, "-w", WORDLIST, "-mc", "200,301,302,403", "-t", "20"], outpath=outpath, silent=True)
            print(f"[+] ffuf results saved to {outpath}")
    elif has_tool(TOOLS["dirsearch"]):
        # dirsearch usually runs as a python tool; here we call it simply
        run([TOOLS["dirsearch"], "-u", f"https://{target}", "-e", "php,html,js,txt,json", "-w", WORDLIST], outpath=os.path.join(fuzz_dir, "dirsearch.txt"), silent=True)
        print(f"[+] dirsearch results saved to {os.path.join(fuzz_dir, 'dirsearch.txt')}")

    # 4) Service discovery with nmap (safe, basic)
    nmap_out = os.path.join(base, "nmap.xml")
    if has_tool(TOOLS["nmap"]):
        # Basic port/service discovery (no intrusive scripts)
        run([TOOLS["nmap"], "-Pn", "-sV", "-oX", nmap_out, target], outpath=nmap_out, silent=True)
        print(f"[+] nmap scan saved to {nmap_out}")

    # 5) Nuclei vulnerability scan (templates)
    nuclei_out = os.path.join(base, "nuclei.txt")
    if has_tool(TOOLS["nuclei"]) and os.path.exists(subdomains_file):
        run([TOOLS["nuclei"], "-l", subdomains_file, "-o", nuclei_out], outpath=nuclei_out, silent=True)
        print(f"[+] nuclei scan saved to {nuclei_out}")

    print("\n=== DONE ===")
    print(f"Results folder: {base}")
    print("Review outputs before taking any action. Use findings only with permission.")
    print("Tip: pipe results into CSV or triage manually: subdomains -> urls -> fuzz results -> nuclei")

if __name__ == "__main__":
    tgt = sys.argv[1] if len(sys.argv) > 1 else None
    main(tgt)
