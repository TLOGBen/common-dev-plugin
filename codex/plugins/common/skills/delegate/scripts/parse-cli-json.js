// delegate skill only: parse a CLI's single-JSON output.
let data = '';
process.stdin.on('data', chunk => data += chunk);
process.stdin.on('end', () => {
  const input = data.trim();
  if (!input) {
    console.error('delegate: partner produced no JSON; check the given session id — do not resend the prompt.');
    process.exitCode = 1;
    return;
  }

  let parsed;
  try {
    parsed = JSON.parse(input);
  } catch {
    console.error('delegate: partner output is not valid JSON; check stderr and output-format.');
    process.exitCode = 1;
    return;
  }

  const [mode, ...fields] = process.argv.slice(2);
  if (mode === 'models') {
    for (const model of parsed.models || []) {
      if (model.visibility === 'list') {
        const efforts = (model.supported_reasoning_levels || [])
          .map(level => level.effort)
          .filter(Boolean)
          .join(',');
        const speedTiers = model.additional_speed_tiers || [];
        const serviceTierIds = (model.service_tiers || [])
          .map(tier => tier.id)
          .filter(Boolean);
        const supportsFast = speedTiers.includes('fast') || serviceTierIds.includes('priority');
        console.log(model.slug, '|', model.display_name, '| efforts:', efforts || 'unknown', '| fast:', supportsFast ? 'yes' : 'no', '|', model.description);
      }
    }
    return;
  }

  for (const field of fields) {
    console.log(field === 'result' ? parsed[field] : `${field}: ${parsed[field]}`);
  }
});
