import re
with open('tests/integration/pipeline/test_compute_embedding.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Use regex to replace the mock_embedding_service fixture
pattern = r'(@pytest\.fixture\s+def mock_embedding_service\(self\):.*?return service)'
replacement = '''    @pytest.fixture
    def mock_embedding_service(self):
        \
\\Create
a
mock
embedding
service.\\\
        from application.services.embedding_service import EmbeddingService
        from domain.value_objects.embedding import Embedding
        service = MagicMock(spec=EmbeddingService)
        # Return 768-dimensional embeddings
        service.generate_embedding = AsyncMock(side_effect=[
            Embedding([0.1] * 768),
            Embedding([0.2] * 768),
        ])
        return service'''

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

with open('tests/integration/pipeline/test_compute_embedding.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print('Fixed test_compute_embedding.py')
