import test from "node:test";
import assert from "node:assert/strict";
import { avatarTone, formatDate, initials, PLAN_TONE } from "./utils.js";

test("formatDate writes day, short month and year", () => {
  assert.equal(formatDate("2026-09-26"), "26 Sep 2026");
  assert.equal(formatDate("2027-01-04"), "04 Jan 2027");
});

test("initials uses the first and last name", () => {
  assert.equal(initials("Aarav Mehta"), "AM");
  assert.equal(initials("Isha"), "I");
});

test("the same name always gets the same avatar colour", () => {
  assert.equal(avatarTone("Rohan Das"), avatarTone("Rohan Das"));
});

test("every plan type has a colour and none uses coral", () => {
  for (const type of ["DAY_PASS", "MONTHLY", "QUARTERLY", "ANNUAL"]) {
    assert.ok(PLAN_TONE[type]);
    assert.notEqual(PLAN_TONE[type], "coral");
  }
});
