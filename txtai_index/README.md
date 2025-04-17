# txtai Index Directory

This directory stores the txtai embeddings index for semantic search.

## About txtai

txtai is a powerful embeddings database that transforms text into vectors for semantic search and natural language processing. This implementation uses the all-MiniLM-L6-v2 model, which provides a good balance between performance and efficiency.

## Index Persistence

When the research application processes content, the txtai index will be saved to this directory. The index is persisted as a `.tar.gz` file, allowing the embeddings to be reloaded when the application restarts.

This ensures that your research data remains available between sessions, eliminating the need to reprocess the same content multiple times.

## Hardware Considerations

The index is configured to work efficiently on the specified hardware constraints (i3 3rd gen processor with 16GB DDR3 RAM). The vectorization model is optimized for this environment, balancing accuracy with performance.
