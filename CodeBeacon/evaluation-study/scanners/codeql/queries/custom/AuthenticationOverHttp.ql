/**
 * @name Study: authentication over HTTP
 * @description A request supplies authentication over an unencrypted HTTP URL.
 * @kind problem
 * @problem.severity warning
 * @precision medium
 * @id study/py/authentication-over-http
 * @tags security
 *       external/cwe/cwe-523
 */
// CUSTOM v1, V4. Explicit non-None auth argument only; headers, payloads and
// session-level credentials are gaps. Includes loopback for credential review.
// Overlap with http-transport is intentional; duplicate findings need grading.
import lib.Study

from Call c
where
  exists(StringLiteral url | httpLiteral(c, url)) and
  exists(Expr auth | auth = keyword(c, "auth") and not auth instanceof None)
select c, "Authentication is supplied over HTTP; use an authenticated HTTPS connection."
