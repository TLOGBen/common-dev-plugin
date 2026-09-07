import test from "node:test";
import assert from "node:assert/strict";
import { summarizeQueue } from "../summarize-queue.mjs";

test("empty queue", () => {
  assert.deepEqual(summarizeQueue([]), []);
});

test("positive queued estimates", () => {
  assert.deepEqual(summarizeQueue([{owner: "ops", estimate: 2, status: "queued"}]), [{owner: "ops", tickets: 1, estimate: 2}]);
});
