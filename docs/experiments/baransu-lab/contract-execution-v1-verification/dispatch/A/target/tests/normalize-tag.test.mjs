import test from "node:test";
import assert from "node:assert/strict";
import { normalizeTag } from "../src/normalize-tag.mjs";

test("trims outer ASCII spaces and lowers ASCII", () => {
  assert.equal(normalizeTag("  Quick-TAG  "), "quick-tag");
});

test("preserves an already normalized tag", () => {
  assert.equal(normalizeTag("clean_tag"), "clean_tag");
});

test("trims boundaries, lowercases only ASCII, and preserves internal whitespace", () => {
  assert.equal(normalizeTag("\tÄBC  DeF\n中  "), "Äbc  def\n中");
});

test("rejects a tag that is empty after trimming", () => {
  assert.throws(() => normalizeTag(" \t\n "), (error) => {
    assert.equal(error.message, "EMPTY_TAG");
    return true;
  });
});
