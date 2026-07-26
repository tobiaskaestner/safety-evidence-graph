Taxonomy Provider
=================

The taxonomy provider holds the vocabulary the rest of the engine works in:
which node kinds and edge kinds exist, which of those edges propagate
suspicion, and what content hashes each node kind carries. Its requirements fix
that vocabulary as closed and built in, so nothing a project configures can
change what counts as a node, an edge, or a propagating relationship.
Enforcement of that closure is the graph builder's job and appears on its
page.

.. sreq:: The built-in kind set is closed
   :id: SEG-SREQ-029
   :refines: SEG-SYS-009

   The taxonomy provider shall declare exactly the node kinds and edge kinds
   of the built-in safety-evidence graph type.

.. sreq:: Exactly three edge kinds propagate
   :id: SEG-SREQ-030
   :refines: SEG-SYS-009

   The taxonomy provider shall mark exactly the refines, verifies, and
   implements edge kinds as propagating suspicion.

.. sreq:: Each node kind declares its content hashes
   :id: SEG-SREQ-032
   :refines: SEG-SYS-009

   The taxonomy provider shall declare, for each node kind, the names of the
   content hashes that kind carries.
