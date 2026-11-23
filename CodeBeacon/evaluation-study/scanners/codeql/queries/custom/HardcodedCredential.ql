/**
 * @name Study: literal credential or default
 * @description A credential-like location has a nonempty literal value.
 * @kind problem
 * @problem.severity warning
 * @precision medium
 * @id study/py/hardcoded-credential
 * @tags security
 *       external/cwe/cwe-798
 */
// CUSTOM v1, V1. Includes defaults, keys, attributes and environment fallbacks.
// Placeholders can match; names do not validate a secret. Empty values excluded.
import lib.Study

from StringLiteral value, string name
where
  credentialName(name) and value.getText() != "" and
  (
    assignedValue(name, value)
    or exists(Parameter p | p.getName() = name and p.getDefault() = value)
    or exists(Call c |
      (moduleCall(c, "os", "getenv") or
       c = API::moduleImport("os").getMember("environ").getMember("get").getACall().asExpr()) and
      c.getArg(0).(StringLiteral).getText() = name and
      value = [c.getArg(1), keyword(c, "default")]
    )
  )
select value, "A credential-like location has a literal value; load credentials from protected configuration."
