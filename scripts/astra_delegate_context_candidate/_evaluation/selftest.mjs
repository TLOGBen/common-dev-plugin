import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";
import crypto from "node:crypto";
const folder = path.dirname(fileURLToPath(import.meta.url));
const seed = path.join(folder,"../public");
const root = fs.mkdtempSync(path.join(os.tmpdir(),"astra-context-oracle-control-"));
const initial = fs.readFileSync(path.join(seed,"summarize-queue.mjs"),"utf8");
const corrected = initial.replace('ticket.status !== "queued" || !ticket.estimate','ticket.status !== "queued"');
if (initial === corrected) throw Error("Reference substitution missing");
const cases = [
  {name:"unmodified_green_smoke",source:initial,expected:false},
  {name:"reference",source:corrected,expected:true},
  {name:"boolean_zero",source:corrected.replace('group.estimate += ticket.estimate;', 'group.estimate = ticket.estimate === 0 ? false : group.estimate + ticket.estimate;'),expected:false},
  {name:"constant_empty",source:'export function summarizeQueue() { return []; }\n',expected:false},
];
const rows=[];
for(const item of cases) {
  const workspace=path.join(root,item.name);
  fs.cpSync(seed,workspace,{recursive:true,errorOnExist:true,force:false});
  fs.writeFileSync(path.join(workspace,"summarize-queue.mjs"),item.source);
  const run=spawnSync(process.execPath,[path.join(folder,"oracle.mjs"),workspace],{encoding:"utf8",timeout:20000});
  const result=JSON.parse(run.stdout);
  rows.push({name:item.name,workspace,expected:item.expected,observed:result.passed,control_pass:result.passed===item.expected,exit:run.status,stdout:run.stdout,stderr:run.stderr});
}
const receipt={model_calls:0,passed:rows.every(row=>row.control_pass),temp_root_retained:root,rows,oracle_sha256:crypto.createHash("sha256").update(fs.readFileSync(path.join(folder,"oracle.mjs"))).digest("hex")};
if(process.argv[2]) fs.writeFileSync(process.argv[2],JSON.stringify(receipt,null,2)+"\n",{flag:"wx"});
console.log(JSON.stringify({passed:receipt.passed,controls:rows.length,root,model_calls:0}));
process.exitCode=receipt.passed?0:1;
