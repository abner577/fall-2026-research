/**
 * @name Study: Flask-Limiter enforcement disabled
 * @description An explicit configuration or constructor setting disables Flask-Limiter.
 * @kind problem
 * @problem.severity warning
 * @precision low
 * @id study/py/flask-rate-limit-disabled
 * @tags security
 *       external/cwe/cwe-307
 */
// CUSTOM v1, V10. Review whether affected endpoints include login and have
// alternative restrictions. Missing/ineffective custom throttles are a gap.
import lib.Study

from AstNode node
where
  exists(False value | configSetting(node, "RATELIMIT_ENABLED", value))
  or exists(Call c |
    node = c and moduleCall(c, "flask_limiter", "Limiter") and keyword(c, "enabled") instanceof False
  )
select node, "Flask-Limiter is explicitly disabled; review protection against repeated authentication attempts."
