#!/usr/bin/env python3
"""Checks that every Ingress backend points at a Service that exists, on the port it exposes.

Usage: helm template ironpass helm/ironpass -f helm/ironpass/values-prod.yaml \
         --set backend.tag=x --set frontend.tag=x | python3 scripts/check-helm-wiring.py
"""
import sys

import yaml

docs = [d for d in yaml.safe_load_all(sys.stdin) if d]
services = {
    d["metadata"]["name"]: {p["port"] for p in d["spec"]["ports"]}
    for d in docs
    if d["kind"] == "Service"
}

problems = []
checked = 0
for ingress in (d for d in docs if d["kind"] == "Ingress"):
    for rule in ingress["spec"]["rules"]:
        for path in rule["http"]["paths"]:
            target = path["backend"]["service"]
            name, port = target["name"], target["port"]["number"]
            checked += 1
            if name not in services:
                problems.append(f"path {path['path']}: Service {name} does not exist")
            elif port not in services[name]:
                problems.append(f"path {path['path']}: Service {name} has no port {port}")
            else:
                print(f"ok  {path['path']:<5} -> {name}:{port}")

if problems or checked == 0:
    print("\n".join(problems) or "no ingress paths found")
    sys.exit(1)
