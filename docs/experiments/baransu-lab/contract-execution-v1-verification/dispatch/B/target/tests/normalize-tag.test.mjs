import test from "node:test";
import assert from "node:assert/strict";
import { normalizeTag } from "../src/normalize-tag.mjs";

test("trims outer ASCII spaces and lowers ASCII", () => {
  assert.equal(normalizeTag("  Quick-TAG  "), "quick-tag");
});

test("preserves an already normalized tag", () => {
  assert.equal(normalizeTag("clean_tag"), "clean_tag");
});

test("preserves internal whitespace while lowering ASCII", () => {
  assert.equal(
    normalizeTag(" \tQuick TAG\twith\n  spaces \n"),
    "quick tag\twith\n  spaces",
  );
});

test("preserves non-ASCII characters", () => {
  assert.equal(normalizeTag(" ÄéΩ 中文 ＡＢＣ Quick "), "ÄéΩ 中文 ＡＢＣ quick");
});

test("throws the exact EMPTY_TAG error after trimming", () => {
  assert.throws(() => normalizeTag(" \t\n"), { message: "EMPTY_TAG" });
});
