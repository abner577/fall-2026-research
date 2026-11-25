/** Shared semantic helpers for newly authored study queries, version 1.
 * API graphs resolve imported modules/aliases; syntactic configuration names
 * and SQL method names are audit heuristics. No application code is referenced.
 */
import python
import semmle.python.ApiGraphs
import semmle.python.dataflow.new.DataFlow
import semmle.python.dataflow.new.TaintTracking

bindingset[name]
predicate credentialName(string name) {
  name.regexpMatch("(?i)([a-z0-9]+_)*(password|passwd|pwd|secret|secret_key|api_key|access_token|auth_token|device_token|client_secret|credential)s?")
}

bindingset[name]
predicate passwordName(string name) {
  name.regexpMatch("(?i)([a-z0-9]+_)*(password|passwd|pwd)")
}

string locationName(Expr e) {
  result = e.(Name).getId()
  or result = e.(Attribute).getName()
  or result = e.(Subscript).getIndex().(StringLiteral).getText()
}

predicate assignedValue(string name, Expr value) {
  exists(Assign a | name = locationName(a.getATarget()) and value = a.getValue())
  or exists(AnnAssign a | name = locationName(a.getTarget()) and value = a.getValue())
  or exists(KeyValuePair p | name = p.getKey().(StringLiteral).getText() and value = p.getValue())
}

predicate moduleCall(Call c, string moduleName, string member) {
  c = API::moduleImport(moduleName).getMember(member).getACall().asExpr()
}

Expr keyword(Call c, string name) {
  exists(Keyword k | k = c.getANamedArg() and k.getArg() = name | result = k.getValue())
}

predicate passwordSource(DataFlow::Node n) {
  passwordName(n.asExpr().(Name).getId())
}

predicate passwordKdf(DataFlow::Node n) {
  exists(Call c | c = n.asExpr() |
    moduleCall(c, "werkzeug.security", "generate_password_hash")
    or moduleCall(c, "bcrypt", "hashpw")
    or moduleCall(c, "hashlib", ["scrypt", "pbkdf2_hmac"])
    or c = API::moduleImport("argon2").getMember("PasswordHasher")
      .getReturn().getMember("hash").getACall().asExpr()
  )
}

/** Direct Requests/HTTPX and locally constructed session methods; no helper
 * wrappers or arbitrary URL-building code is inferred by these HTTP checks. */
predicate httpCall(Call c, Expr url) {
  exists(string mod, string method | mod = ["requests", "httpx"] |
    method = ["get", "post", "put", "patch", "delete", "head", "options"] and
    moduleCall(c, mod, method) and
    url = [c.getArg(0), keyword(c, "url")]
    or
    method = ["request", "Request"] and moduleCall(c, mod, method) and
    url = [c.getArg(1), keyword(c, "url")]
  )
  or
  exists(string mod, string ctor, string method |
    mod = "requests" and ctor = "Session"
    or mod = "httpx" and ctor = ["Client", "AsyncClient"]
  |
    c = API::moduleImport(mod).getMember(ctor).getReturn().getMember(method).getACall().asExpr() and
    (
      method = ["get", "post", "put", "patch", "delete", "head", "options"] and
      url = [c.getArg(0), keyword(c, "url")]
      or method = "request" and url = [c.getArg(1), keyword(c, "url")]
    )
  )
}

predicate httpLiteral(Call c, StringLiteral literal) {
  exists(Expr url |
    httpCall(c, url) and
    DataFlow::localFlow(DataFlow::exprNode(literal), DataFlow::exprNode(url)) and
    literal.getText().regexpMatch("(?i)http://.*")
  )
}

/** A config subscript assignment or keyword update; configuration policy and
 * framework presence need review, as in the Semgrep configuration checks. */
predicate configSetting(AstNode node, string name, Expr value) {
  exists(Assign a, Subscript sub, Attribute config |
    sub = a.getATarget() and config = sub.getObject() and config.getName() = "config" and
    sub.getIndex().(StringLiteral).getText() = name and value = a.getValue() and node = a
  )
  or exists(Call c, Attribute update, Attribute config |
    update = c.getFunc() and update.getName() = "update" and
    config = update.getObject() and config.getName() = "config" and
    value = keyword(c, name) and node = c
  )
}
