Content Extractor
=================

The content extractor turns source into content hashes. It locates the span
a node covers and hashes it, so the hash binds the exact bytes a reviewer
reads rather than any reconstruction of them. Its requirement here fixes the
canonical content form for source-located nodes as the verbatim byte span. It
is the first of the extraction adapters in the component map; the requirements
reader and the outcome extractor join this page when record production
lands.

.. sreq:: Content hashes over verbatim byte spans
   :id: SEG-SREQ-001
   :refines: SEG-SYS-001

   The content extractor shall compute each content hash as the SHA-256 of
   the verbatim source byte span it covers.
