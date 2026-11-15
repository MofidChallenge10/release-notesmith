#!/usr/bin/env python3
"""Compose Markdown release notes from Conventional Commit subjects."""
import argparse,re,subprocess,sys,unittest
ORDER=("Features","Fixes","Performance","Documentation","Maintenance")
TYPES={"feat":"Features","fix":"Fixes","perf":"Performance","docs":"Documentation","refactor":"Maintenance","test":"Maintenance","build":"Maintenance","ci":"Maintenance","chore":"Maintenance"}
PATTERN=re.compile(r"^(?P<type>[a-z]+)(?:\((?P<scope>[^)]+)\))?(?P<breaking>!)?:\s*(?P<subject>.+)$")
def compose(subjects):
    groups={name:[] for name in ORDER}; breaking=[]
    for raw in subjects:
        line=raw.strip()
        if not line or line.lower().startswith("merge "): continue
        match=PATTERN.match(line)
        if not match: continue
        section=TYPES.get(match.group("type"))
        if not section: continue
        scope=f"**{match.group('scope')}**: " if match.group("scope") else ""
        entry=f"- {scope}{match.group('subject')}"
        groups[section].append(entry)
        if match.group("breaking"): breaking.append(entry)
    out=["# Release notes",""]
    if breaking: out += ["## Breaking changes","",*breaking,""]
    for section in ORDER:
        if groups[section]: out += [f"## {section}","",*groups[section],""]
    return "\n".join(out).rstrip()+"\n"
class Tests(unittest.TestCase):
    def test_grouping(self):
        text=compose(["feat(auth): add passkeys","fix: handle empty input","chore: bump tooling"])
        self.assertIn("## Features",text); self.assertIn("## Fixes",text); self.assertIn("passkeys",text)
    def test_breaking(self): self.assertIn("## Breaking changes",compose(["feat(api)!: remove v1"]))
    def test_ignore_non_conventional(self): self.assertNotIn("random",compose(["random message"]))
def main():
    ap=argparse.ArgumentParser(description=__doc__); ap.add_argument("--from-file"); ap.add_argument("--output"); a=ap.parse_args()
    try:
        if a.from_file: subjects=open(a.from_file,encoding="utf-8").read().splitlines()
        else: subjects=subprocess.run(["git","log","--pretty=%s"],check=True,text=True,capture_output=True).stdout.splitlines()
    except (OSError,subprocess.CalledProcessError) as exc: ap.error(str(exc))
    result=compose(subjects)
    if a.output: open(a.output,"w",encoding="utf-8").write(result)
    else: print(result,end="")
if __name__=="__main__":
    if "--self-test" in sys.argv: unittest.main(argv=[sys.argv[0]])
    else: main()
