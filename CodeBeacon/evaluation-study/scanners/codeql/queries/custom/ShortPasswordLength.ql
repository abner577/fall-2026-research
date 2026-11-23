/**
 * @name Study: short password length floor
 * @description A password length comparison permits a minimum below eight characters.
 * @kind problem
 * @problem.severity warning
 * @precision low
 * @id study/py/short-password-length
 * @tags security
 *       external/cwe/cwe-521
 */
// CUSTOM v1, V2. Screening floor 8, matching Semgrep. Explicit simple numeric
// comparisons only; no absent-policy inference or claim of policy compliance.
import lib.Study

from Compare cmp, Call length, int n
where
  length.getFunc().(Name).getId() = "len" and
  passwordName(length.getArg(0).(Name).getId()) and
  cmp.getLeft() = length and n = cmp.getComparator(0).(IntegerLiteral).getValue() and
  (
    (cmp.getOp(0) instanceof Lt or cmp.getOp(0) instanceof GtE) and n > 0 and n < 8
    or (cmp.getOp(0) instanceof LtE or cmp.getOp(0) instanceof Gt) and n >= 0 and n < 7
  )
select cmp, "This password length comparison uses a floor below eight characters; review the full policy."
