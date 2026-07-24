Test Specification
==================

Test specifications for the affirmatrix requirements (``SEG-TS-nnn``). The
``verifies`` links target needs imported from the requirement specification
(cross-document, via the registry).

.. tspec:: Byte-span hash stability
   :id: SEG-TS-001
   :verifies: SEG-SREQ-001

   Verify that a located span's hash is stable under reformatting outside the
   span and changes for any byte change inside the span.

.. tspec:: Affirmation records both endpoint hashes
   :id: SEG-TS-002
   :verifies: SEG-SREQ-002

   Verify that a recorded affirmation carries the content hashes of both
   endpoints and is invalidated by drift on either side.
