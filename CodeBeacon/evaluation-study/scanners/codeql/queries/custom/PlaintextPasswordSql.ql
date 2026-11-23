/**
 * @name Study: plaintext password in SQL write
 * @description Password-like input reaches a direct SQL password write without a recognized password KDF.
 * @kind problem
 * @problem.severity warning
 * @precision medium
 * @id study/py/plaintext-password-sql
 * @tags security
 *       external/cwe/cwe-256
 */
// CUSTOM v1, V3. Literal INSERT/UPDATE and execute(sql, values) only. Dynamic
// SQL, ORMs and schemas without password-like columns are gaps. A password in
// a WHERE clause may cause an audit false alarm. KDF costs are not validated.
import lib.Study

module Config implements DataFlow::ConfigSig {
  predicate isSource(DataFlow::Node n) { passwordSource(n) }
  predicate isSink(DataFlow::Node n) {
    exists(Call c, StringLiteral sql |
      c.getFunc().(Attribute).getName() = "execute" and sql = c.getArg(0) and
      sql.getText().regexpMatch("(?is).*(insert\\s+into|update)\\b.*\\b(password|passwd|pwd|password_hash)\\b.*") and
      n.asExpr() = c.getArg(1)
    )
  }
  predicate isBarrier(DataFlow::Node n) { passwordKdf(n) }
}
module Flow = TaintTracking::Global<Config>;

from DataFlow::Node sink
where exists(DataFlow::Node source | Flow::flow(source, sink))
select sink, "Raw password-like data reaches a SQL password write; store only a salted password KDF result."
