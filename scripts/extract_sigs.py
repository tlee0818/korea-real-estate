#!/usr/bin/env python3
"""Print public method signatures of the three HTTP clients as JSON.

Usage: python scripts/extract_sigs.py <pkg_root_or_site_packages_dir>

Outputs a JSON dict:
{
  "PublicDataClient": {"method_name": {"param": {"required": bool, "kind": str}, ...}, ...},
  "RebClient":        {...},
  "JusoClient":       {...}
}

A class value of null means the import failed (package not present at that path).
"""

import inspect
import json
import sys

sys.path.insert(0, sys.argv[1])

CLIENTS = [
    ("korea_realestate.http.public_data", "PublicDataClient"),
    ("korea_realestate.http.reb", "RebClient"),
    ("korea_realestate.http.juso", "JusoClient"),
]

result = {}
for module_path, class_name in CLIENTS:
    try:
        mod = __import__(module_path, fromlist=[class_name])
        cls = getattr(mod, class_name)
        sigs = {}
        for name, obj in inspect.getmembers(cls, predicate=inspect.isfunction):
            if name.startswith("_"):
                continue
            sig = inspect.signature(obj)
            params = {}
            for pname, p in sig.parameters.items():
                if pname == "self":
                    continue
                params[pname] = {
                    "required": (
                        p.default is inspect.Parameter.empty
                        and p.kind
                        not in (
                            inspect.Parameter.VAR_POSITIONAL,
                            inspect.Parameter.VAR_KEYWORD,
                        )
                    ),
                    "kind": p.kind.name,
                }
            sigs[name] = params
        result[class_name] = sigs
    except Exception:
        result[class_name] = None

print(json.dumps(result))
