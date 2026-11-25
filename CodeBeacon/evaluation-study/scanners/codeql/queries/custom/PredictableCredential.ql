/**
 * @name Study: predictable generated credential
 * @description Noncryptographic randomness, time or UUID1 reaches a credential-like value.
 * @kind problem
 * @problem.severity warning
 * @precision medium
 * @id study/py/predictable-credential
 * @tags security
 *       external/cwe/cwe-330
 */
// CUSTOM v1, V8. Names infer security context; ordinary sensor randomness is
// not a sink. SystemRandom and secrets are not sources. Unknown PRNGs, entropy
// quality and arbitrary application-specific generators are coverage gaps.
import lib.Study

module Config implements DataFlow::ConfigSig {
  predicate isSource(DataFlow::Node n) {
    exists(Call c | c = n.asExpr() |
      moduleCall(c, "random", ["random", "randint", "randrange", "choice", "choices", "getrandbits", "randbytes"])
      or moduleCall(c, "time", ["time", "time_ns"])
      or moduleCall(c, "uuid", "uuid1")
    )
  }
  predicate isSink(DataFlow::Node n) {
    exists(string name |
      (credentialName(name) or name.regexpMatch("(?i)([a-z0-9]+_)*tokens?")) and
      assignedValue(name, n.asExpr())
    )
    or exists(Return ret, Function f |
      ret.getScope() = f and n.asExpr() = ret.getValue() and
      f.getName().regexpMatch("(?i)(generate|create|make|new|issue)_([a-z0-9]+_)*(password|secret|token|credential)s?")
    )
  }
}
module Flow = TaintTracking::Global<Config>;

from DataFlow::Node sink
where exists(DataFlow::Node source | Flow::flow(source, sink))
select sink, "Predictable data reaches a credential-like value; use a suitable cryptographic generator."
