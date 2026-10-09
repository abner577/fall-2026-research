## We have 3 Security references that we were given, we need to decide how we are going to use those.

1. CWE --> A catalog of software and hardware weakness types, so it answers questions like: "What kind of weakness causes this security problem".

2. OWASP --> An organization that publishes security risk lists, requirements, testing guides, and prevention guidance.

3. Common Criteria --> A framework for specifying and evaluating a products security requirements.

---

#### Defining terms
1. Threat --> A potential event that could cause harm (For ex: Someone could steal your laptop)

2. Vulnerability --> A weakness in the particular systems that could be exploted (For ex: Your laptop is left unattended in an accesible location)

3. Attack --> A deliberate attempt to comprise security (For ex: Someone tries to take the laptop)

4. Impact --> The harm resulting from a successful attack (For ex: Losign the laptop and exposing sensitive data it had).

- The threat exists before anyone acts. The vulnerability makes the harmful action possible or easier. An attack doesnt have to succeed to count as an attack.


#### CWE: Identifying and explaining the weakness
- CWE stands for Common Weakness Enumeration.

A weakness type = A general pattern that can appear in many systems
A vulnerability = A specific exploitable instance in a particular system.

For example:
- Missing authorization is a weakness type.
- "Our app lets any signed is user access another users private information, because this endpoint never checks ownership" describes a specific vulnerability.

A CWE entry contains:
- An identifier and description of the weakness
- How the weakness gets introduced during design or implementation
- Coonseuqences if it is exploted, exampled code and real examples, and potential mitigations and relationships to other weaknesses.

#### OWASP: understand risks and applying security guidance
- OWASP is broader than a single list, we need to figure out exactly which OWASP publication they mean. They may mean the OWASP Top 10, which descrives major web application security risk categories. Or an IOT top 10

#### Common Criteria: Connecting the security problem to requirments and evidence
- Common Criteria is a frameowrk for security application and evaluation, rather than a master catalog of common threat and vulnerabilities. 

It provides a structure for describing:
**1. The product and its boundaries:** Exactly what is being evaluated, called the Target of Evaluation

**2. The security problem:** Relevant threats

**3. Security objects:** What the product and its environment must achieve

**4. Security Functional Requirments (SFRs):** Required security behavior, such as access control, auth, or auditing

**5. Security Assurance Requirements (SARs):** The documentation, analysis, testing, and evaluation needed to support confidence in that behavior.

- It also defines Protection Profiles, which describe security needs for a type of product, and Security Targets, which describe the security claims and requirements for a specific product. 
