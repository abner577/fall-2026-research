/**
 * @name Study: disabled TLS verification configuration
 * @description An SSL context, Requests session or HTTPX client disables certificate verification.
 * @kind problem
 * @problem.severity warning
 * @precision medium
 * @id study/py/disabled-tls-configuration
 * @tags security
 *       external/cwe/cwe-295
 */
// CUSTOM v1, V9. Complements the upstream request query with standalone
// configurations. verify_mode uses a semantic property heuristic. Requests
// sessions require a visible constructor. check_hostname=False alone omitted.
// A config alert does not prove a request uses that configuration.
import lib.Study

from AstNode node
where
  exists(Call c |
    node = c and
    (moduleCall(c, "ssl", "_create_unverified_context") or
     moduleCall(c, "httpx", ["Client", "AsyncClient"]) and keyword(c, "verify") instanceof False)
  )
  or exists(Assign a, Attribute target |
    node = a and target = a.getATarget() and
    (
      target.getName() = "verify_mode" and
      a.getValue() = API::moduleImport("ssl").getMember("CERT_NONE").getAValueReachableFromSource().asExpr()
      or target.getName() = "verify" and a.getValue() instanceof False and
      target.getObject() = API::moduleImport("requests").getMember("Session").getReturn().getAValueReachableFromSource().asExpr()
    )
  )
select node, "TLS certificate verification is explicitly disabled in this configuration."
