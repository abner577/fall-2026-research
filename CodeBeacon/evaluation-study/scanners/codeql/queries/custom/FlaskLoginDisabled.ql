/**
 * @name Study: Flask-Login enforcement disabled
 * @description An explicit configuration setting disables Flask-Login authentication enforcement.
 * @kind problem
 * @problem.severity warning
 * @precision medium
 * @id study/py/flask-login-disabled
 * @tags security
 *       external/cwe/cwe-306
 */
// CUSTOM v1, V6. Config assignment/update only. Review Flask-Login usage;
// missing decorators, custom guards, proxy auth and public routes are not inferred.
import lib.Study

from AstNode node, True value
where configSetting(node, "LOGIN_DISABLED", value)
select node, "Flask-Login enforcement is explicitly disabled; protected routes may accept unauthenticated requests."
