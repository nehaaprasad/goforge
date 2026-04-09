"""Fixed unified diff for mock / no-API-key codegen (must apply to sandbox baseline)."""

from __future__ import annotations

# Must apply cleanly to the committed baseline in sandbox-repo (see internal/greet).
MOCK_DIFF = (
    "--- a/internal/greet/greet.go\n"
    "+++ b/internal/greet/greet.go\n"
    "@@ -3,5 +3,6 @@\n"
    " \n"
    " // Hello returns a fixed string for tests and demos.\n"
    " func Hello() string {\n"
    "+\t// PatchFlow: applied mock diff (sandbox).\n"
    " \treturn \"hello\"\n"
    " }\n"
)
