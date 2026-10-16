#!/usr/bin/env bash
# Checks that every icon URL answers 200 with the right content type and that a
# missing path with an extension is a 404.   bash check_icons.sh http://localhost:3000
base="${1%/}"
fail=0
check() { # path, expected status, expected content type start
  local out code type
  out=$(curl -s -o /dev/null -D - -w '%{http_code}' "$base$1")
  code=${out##*$'\n'}; code=${code: -3}
  type=$(printf '%s' "$out" | grep -i '^content-type:' | tr -d '\r' | sed 's/^[^:]*: *//')
  cache=$(printf '%s' "$out" | grep -i '^cache-control:' | tr -d '\r' | sed 's/^[^:]*: *//')
  ok=OK
  [ "$code" = "$2" ] || ok=FAIL
  case "$type" in "$3"*) ;; *) ok=FAIL ;; esac
  [ "$ok" = OK ] || fail=1
  printf '%-4s %-26s %s  %-32s %s\n' "$ok" "$1" "$code" "$type" "$cache"
}
check /favicon.svg 200 image/svg+xml
check /favicon.ico 200 image/
check /favicon-32.png 200 image/png
check /apple-touch-icon.png 200 image/png
check /icon-192.png 200 image/png
check /icon-512.png 200 image/png
check /icon-maskable-512.png 200 image/png
check /manifest.webmanifest 200 application/manifest+json
check / 200 text/html
check /missing.png 404 text/html
check /nothing.ico 404 text/html
check /assets/missing.js 404 text/html
check /some/page 200 text/html
exit $fail
