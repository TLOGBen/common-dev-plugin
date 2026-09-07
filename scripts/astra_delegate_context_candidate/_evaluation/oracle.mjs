import assert from "node:assert/strict";
import { pathToFileURL } from "node:url";
import path from "node:path";
import crypto from "node:crypto";
import fs from "node:fs";

const root = path.resolve(process.argv[2]);
const program = path.join(root, "summarize-queue.mjs");
const before = fs.readFileSync(program);
const { summarizeQueue } = await import(pathToFileURL(program));
const cases = [
  {name:"empty", input:[], expected:[]},
  {name:"zero", input:[{owner:"ops",estimate:0,status:"queued"}], expected:[{owner:"ops",tickets:1,estimate:0}]},
  {name:"archived_only", input:[{owner:"ops",estimate:10,status:"done"}], expected:[]},
  {name:"same_owner_mixed", input:[{owner:"ops",estimate:0,status:"queued"},{owner:"ops",estimate:4,status:"queued"},{owner:"ops",estimate:9,status:"done"}], expected:[{owner:"ops",tickets:2,estimate:4}]},
  {name:"several_owners", input:[{owner:"研發, 二組",estimate:0,status:"queued"},{owner:"a",estimate:3,status:"queued"},{owner:"z",estimate:2,status:"queued"},{owner:"a",estimate:0,status:"queued"}], expected:[{owner:"a",tickets:2,estimate:3},{owner:"z",tickets:1,estimate:2},{owner:"研發, 二組",tickets:1,estimate:0}]},
];
const results = [];
for (const item of cases) {
  const source = structuredClone(item.input);
  try {
    assert.deepStrictEqual(summarizeQueue(source), item.expected);
    assert.deepStrictEqual(source, item.input);
    assert.deepStrictEqual(summarizeQueue(structuredClone(item.input).reverse()), item.expected);
    results.push({name:item.name,passed:true});
  } catch (error) {results.push({name:item.name,passed:false,error:error.message});}
}
const unchanged = before.equals(fs.readFileSync(program));
const result = {passed:unchanged && results.every(item=>item.passed),checks:results,program_unchanged:unchanged,program_sha256:crypto.createHash("sha256").update(before).digest("hex"),model_calls:0};
console.log(JSON.stringify(result,null,2));
process.exitCode = result.passed ? 0 : 1;
