import test from "node:test";
import assert from "node:assert/strict";
import { countLabel } from "../src/count-label.mjs";

test("zero records", () => {
  assert.equal(countLabel(0), "0 records");
});

test("multiple records", () => {
  assert.equal(countLabel(2), "2 records");
});

