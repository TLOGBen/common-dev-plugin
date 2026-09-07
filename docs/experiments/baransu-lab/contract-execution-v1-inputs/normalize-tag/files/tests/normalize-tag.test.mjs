import test from "node:test";
import assert from "node:assert/strict";
import { normalizeTag } from "../src/normalize-tag.mjs";

test("trims outer ASCII spaces and lowers ASCII", () => {
  assert.equal(normalizeTag("  Quick-TAG  "), "quick-tag");
});

test("preserves an already normalized tag", () => {
  assert.equal(normalizeTag("clean_tag"), "clean_tag");
});
