#!/usr/bin/env python3
"""Shared future-episode wording adapter; frozen screen carrier stays unchanged."""
import sys
sys.dont_write_bytecode = True
import astra_lead_episode as carrier

_original_envelope = carrier.envelope

def model_budget_envelope(spec, role, writes):
    text = _original_envelope(spec, role, writes)
    return text.replace(
        str(spec["max_calls"]) + " CLI calls,",
        str(spec["max_calls"]) + " MODEL invocations (lead or worker, not shell/tool calls),",
    )

carrier.envelope = model_budget_envelope

if __name__ == "__main__":
    carrier.main()
