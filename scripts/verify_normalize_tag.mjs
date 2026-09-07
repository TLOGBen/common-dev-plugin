#!/usr/bin/env node
// Independent local oracle. Reads the real target; never modifies a fixture.
import { pathToFileURL } from "node:url";
import path from "node:path";
const target = path.resolve(process.argv[2]);
const { normalizeTag } = await import(pathToFileURL(target).href);
const cases = [
  { id: "ordinary", input: "  Quick-TAG  ", expected: "quick-tag" },
  { id: "non-ascii", input: " İÉßＡ Z ", expected: "İÉßＡ z" },
  { id: "inner-spaces", input: " A  B ", expected: "a  b" },
  { id: "inner-controls", input: "A\tB\nC", expected: "a\tb\nc" },
  { id: "outer-nbsp", input: "\u00a0A\u00a0", expected: "a" },
  { id: "empty", input: "", error: "EMPTY_TAG" },
  { id: "whitespace-only", input: " \t\n ", error: "EMPTY_TAG" },
  { id: "bom-only", input: "\ufeff", error: "EMPTY_TAG" }
];
const results = cases.map(c => {
  let actual, error;
  try { actual = normalizeTag(c.input); } catch (e) { error = { isError: e instanceof Error, message: e?.message }; }
  const pass = c.error ? error?.isError === true && error.message === c.error : !error && actual === c.expected;
  return { ...c, actual, observedError: error, pass };
});
console.log(JSON.stringify({ target, results, passed: results.filter(r => r.pass).length, total: results.length, mutation: false }, null, 2));
process.exitCode = results.every(r => r.pass) ? 0 : 1;
