# Runtime selection

Use the available native delegation API when it can represent the required role, model, reasoning effort, permissions, and workspace. Otherwise inspect the installed CLI's current help and model catalog before using a supported command.

An explicit model/profile request is a constraint, not a suggestion. For "Luna Max", select the live Luna model identifier with max reasoning only if both values are supported. If the profile cannot be represented, explain the missing capability and request a choice; do not silently change effort, use a different model, or claim the requested profile ran.

Without an explicit worker profile, choose an available economical model suited to the slice. Use known current prices or describe this as a hypothesis when prices are not exposed. Never fabricate a model ID from the user's colloquial name. Account for retry and supervision cost, not only unit price.

Native role names are not automatically installed by a plugin. Read the bundled executor role and pass the complete instructions to a generic worker unless the runtime confirms that the role is registered. If the bundled definition is missing, stop delegation with AGENT_DEFINITION_MISSING instead of improvising a similarly named role.

Preserve the existing permission boundary in any CLI fallback. Do not disable approval, sandboxing, or audit controls to make a dispatch work. Keep logs within the task's permitted local directory and avoid putting credentials in prompts or logs.

After an uncertain dispatch result, inspect the existing task/session before launching another worker that could duplicate writes. Parallel workers require independent work or explicit ownership coordination.
