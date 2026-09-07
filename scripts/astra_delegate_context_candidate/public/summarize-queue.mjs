export function summarizeQueue(tickets) {
  const groups = new Map();
  for (const ticket of tickets) {
    if (ticket.status !== "queued" || !ticket.estimate) continue;
    const group = groups.get(ticket.owner) ?? { owner: ticket.owner, tickets: 0, estimate: 0 };
    group.tickets += 1;
    group.estimate += ticket.estimate;
    groups.set(ticket.owner, group);
  }
  return [...groups.values()].sort((a, b) => a.owner < b.owner ? -1 : a.owner > b.owner ? 1 : 0);
}
