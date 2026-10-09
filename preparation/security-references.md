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
- We will use the OWASP IoT Top 10 to build our list of possible security areas, then choose two to focus on. We have not chosen the two yet.

The selection process will be:
1. Record the ten categories and their descriptions from the [official OWASP IoT project](https://owasp.org/projects/internet-of-things?tab=seek-and-understand). The list provided there is the IoT Top 10 2018; record that edition.
2. For each category, consider what evidence we could find in uploaded code and what would require device or deployment information.
3. Identify the concrete weaknesses within each category that our app could reasonably check.
4. Choose two targets based on whether we can detect them, explain them, suggest useful fixes, and test the results within the project scope.

The categories are broad security areas, so selecting a category does not mean we can detect every issue within it.

#### Common Criteria: Connecting the security problem to requirments and evidence
- Common Criteria is a frameowrk for security application and evaluation, rather than a master catalog of common threat and vulnerabilities. 

It provides a structure for describing:
**1. The product and its boundaries:** Exactly what is being evaluated, called the Target of Evaluation

**2. The security problem:** Relevant threats

**3. Security objects:** What the product and its environment must achieve

**4. Security Functional Requirments (SFRs):** Required security behavior, such as access control, auth, or auditing

**5. Security Assurance Requirements (SARs):** The documentation, analysis, testing, and evaluation needed to support confidence in that behavior.

- It also defines Protection Profiles, which describe security needs for a type of product, and Security Targets, which describe the security claims and requirements for a specific product. 

---

## Proposed approach: start with CWE and consider Common Criteria later

For the first version, the recommendation is to use CWE as the main source of weakness information after choosing the two targets. Common Criteria is optional unless the project requires an evaluation of specific product security requirements. This is a recommendation, not a final decision to remove Common Criteria.

### What information we would keep from CWE

For each relevant weakness, keep its identifier, description, conditions that make it applicable, possible consequences, detection guidance, examples, and mitigation guidance where available. Also keep the source link and version used.

The scanner results and code provide the evidence. The retrieved CWE information helps the LLM interpret that evidence and explain possible fixes. CWE guidance is not automatically an executable scan rule or a ready-made patch for every project.

See the [CWE explanation of weaknesses and vulnerabilities](https://cwe.mitre.org/about/faq).

### What Common Criteria could add

Common Criteria could help organize a review around the product's purpose, boundaries, operating assumptions, security objectives, requirements, and supporting evidence. We would select relevant requirements and turn them into clear review questions rather than ask the LLM to follow the entire standard without further instructions.

For each selected requirement, the review could ask: What protection is expected? What code or configuration supports it? What evidence is missing? What change or test would help address the gap?

This could help the LLM examine issues beyond scanner findings, but it does not guarantee detection of missed vulnerabilities. Any additional finding would still need code evidence and checking. A missing requirement or missing evidence is not automatically a confirmed vulnerability. Following this structure would not make the report a formal Common Criteria evaluation or certification.

See the [Common Criteria general model](https://www.commoncriteriaportal.org/files/ccfiles/CC2022PART1R1.pdf).

### Asking the user about the product

A short product description would be useful even if we only use CWE. Alongside the ZIP, we could ask the user to explain:
- What the product does and whether the uploaded code belongs to the device, a backend, or a companion app.
- Who uses it, what it connects to, and what sensitive data or actions it handles.
- Whether the upload contains the whole project or only one component.

The description gives context; the app should treat it as information supplied by the user, not proof that a protection exists.

We could later look for an existing Protection Profile that matches the product type. A similar profile would be a starting reference, and its requirements and assumptions would need to be checked for relevance. A few sentences about a product are not enough to create a complete Protection Profile. For a specific product, a Security Target is the more relevant Common Criteria document; the first version can use a simple product description without creating either document.

### Do we need both?

We do not need both to build the focused code scanner. CWE is the closer fit for explaining weaknesses and suggesting mitigations. Common Criteria adds structure for reviewing security requirements, rather than replacing the detailed weakness information in CWE.

Start with CWE and the short product description. Add selected Common Criteria requirements if we identify a useful review question that the first version does not address, or if the project's requirements call for it. If we use both, we can prepare their selected information in one curated knowledge base instead of fetching from separate websites during every scan.
