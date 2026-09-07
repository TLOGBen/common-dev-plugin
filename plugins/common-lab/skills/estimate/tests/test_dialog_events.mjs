import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
import test from 'node:test';

const template = readFileSync(new URL('../assets/assessment-report-template.html', import.meta.url), 'utf8');
const script = template.match(/<script>([\s\S]*?)<\/script>/)[1];

function setup() {
  const handlers = {};
  const closeHandlers = {};
  const closeButton = {addEventListener(name, callback) {closeHandlers[name] = callback;}};
  const dialog = {
    open: true,
    querySelectorAll() {return [closeButton];},
    addEventListener(name, callback) {handlers[name] = callback;},
    getBoundingClientRect() {return {left: 400, right: 1180, top: 0, bottom: 900};},
    close() {this.open = false;},
  };
  vm.runInNewContext(script, {
    document: {querySelectorAll(selector) {return selector === '.package-dialog' ? [dialog] : []; }},
    window: {scrollTo() {}},
  });
  return {dialog, handlers, closeHandlers};
}

test('keyboard activation of descendant summary does not close its dialog', () => {
  const {dialog, handlers} = setup();
  handlers.click({target: {tagName: 'SUMMARY'}, detail: 0, clientX: 0, clientY: 0});
  assert.equal(dialog.open, true);
});

test('descendant pointer clicks cannot be mistaken for backdrop clicks', () => {
  const {dialog, handlers} = setup();
  handlers.click({target: {tagName: 'SUMMARY'}, detail: 1, clientX: 0, clientY: 0});
  assert.equal(dialog.open, true);
});

test('real outside pointer click targeting dialog backdrop still closes', () => {
  const {dialog, handlers} = setup();
  handlers.click({target: dialog, detail: 1, clientX: 100, clientY: 100});
  assert.equal(dialog.open, false);
});

test('inside dialog clicks and keyboard dialog activation stay open', () => {
  for (const event of [{detail: 1, clientX: 600, clientY: 200}, {detail: 0, clientX: 0, clientY: 0}]) {
    const {dialog, handlers} = setup();
    handlers.click({...event, target: dialog});
    assert.equal(dialog.open, true);
  }
});

test('explicit close control still closes', () => {
  const {dialog, closeHandlers} = setup();
  closeHandlers.click();
  assert.equal(dialog.open, false);
});
