project = "SEG sphinx-needs Spike"
extensions = ["sphinx_needs"]

needs_types = [
    dict(directive="sys", title="System Requirement", prefix="SYS_", color="#BFD8D2", style="node"),
    dict(directive="req", title="Software Requirement", prefix="R_", color="#BFD8D2", style="node"),
    dict(directive="adr", title="Design Decision", prefix="A_", color="#DF744A", style="node"),
    dict(directive="impl", title="Implementation", prefix="I_", color="#DCB239", style="node"),
    dict(directive="tst", title="Test Specification", prefix="T_", color="#FEDCD2", style="node"),
]

needs_extra_links = [
    dict(option="refines", incoming="is refined by", outgoing="refines"),
    dict(option="answers", incoming="is answered by", outgoing="answers"),
    dict(option="adheres", incoming="is adhered to by", outgoing="adheres to"),
    dict(option="verifies", incoming="is verified by", outgoing="verifies"),
    dict(option="implements", incoming="is implemented by", outgoing="implements"),
]
