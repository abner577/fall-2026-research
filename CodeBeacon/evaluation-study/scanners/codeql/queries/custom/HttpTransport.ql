/**
 * @name Study: HTTP request transport
 * @description A request uses an unencrypted non-loopback HTTP URL.
 * @kind problem
 * @problem.severity warning
 * @precision low
 * @id study/py/http-transport
 * @tags security
 *       external/cwe/cwe-319
 */
// CUSTOM v1, V4. Requests/HTTPX literal URLs and local aliases only. Sensitivity
// needs review. Excludes localhost/IPv4/IPv6 loopback by URL authority, including
// ports, but not lookalike domains. Dynamically assembled URLs are a gap.
import lib.Study

from Call c
where exists(StringLiteral url |
  httpLiteral(c, url) and
  not url.getText().regexpMatch("(?i)http://(localhost|127\\.0\\.0\\.1|\\[::1\\])(:[0-9]+)?([/?#].*)?")
)
select c, "This request uses unencrypted HTTP; review sensitivity and use HTTPS."
