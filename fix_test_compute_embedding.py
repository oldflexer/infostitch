import re

with open('tests/integration/pipeline/test_compute_embedding.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Move fixtures to module level
old = '''class TestComputeEmbeddingStep:
    """Tests for ComputeEmbeddingStep (embedding generation)."""

    @pytest.fixture
    def sample_generated_posts(self):
        """Create sample generated posts."""
        return [{"article_id": 1,
                 "source_id": 1,
                 "title": "AI Breakthrough",
                 "summary": "Revolutionary AI model achieves human-level reasoning",
                 "post_text": "🚀 AI Breakthrough! Revolutionary model...",
                 "template_id": "news_brief",
                 "clean_url": "https://example.com/1",
                 "image_url": "https://example.com/image1.jpg",
                 },
                {"article_id": 2,
                 "source_id": 2,
                 "title": "Quantum Computing",
                 "summary": "Quantum computer solves impossible problem",
                 "post_text": "⚛️ Quantum Computing Milestone! ...",
                 "template_id": "tech_deep_dive",
                 "clean_url": "https://example.com/2",
                 "image_url": None,
                 },
                ]

    @pytest.fixture
    def mock_embedding_service(self):
        """Create a mock embedding service."""
        from application.services.embedding_service import EmbeddingService
        from domain.value_objects.embedding import Embedding
        service = MagicMock(spec=EmbeddingService)
        # Return 768-dimensional embeddings
        service.generate_embedding = AsyncMock(side_effect=[
            Embedding([0.1] * 768),
            Embedding([0.2] * 768),
        ])
        return service

    @pytest.mark.asyncio'''

new = '''@pytest.fixture
def sample_generated_posts():
    """Create sample generated posts."""
    return [{"article_id": 1,
             "source_id": 1,
             "title": "AI Breakthrough",
             "summary": "Revolutionary AI model achieves human-level reasoning",
             "post_text": "🚀 AI Breakthrough! Revolutionary model...",
             "template_id": "news_brief",
             "clean_url": "https://example.com/1",
             "image_url": "https://example.com/image1.jpg",
             },
            {"article_id": 2,
             "source_id": 2,
             "title": "Quantum Computing",
             "summary": "Quantum computer solves impossible problem",
             "post_text": "⚛️ Quantum Computing Milestone! ...",
             "template_id": "tech_deep_dive",
             "clean_url": "https://example.com/2",
             "image_url": None,
             },
            ]


@pytest.fixture
def mock_embedding_service():
    """Create a mock embedding service."""
    from application.services.embedding_service import EmbeddingService
    from domain.value_objects.embedding import Embedding
    service = MagicMock(spec=EmbeddingService)
    # Return 768-dimensional embeddings
    service.generate_embedding = AsyncMock(side_effect=[
        Embedding([0.1] * 768),
        Embedding([0.2] * 768),
    ])
    return service


class TestComputeEmbeddingStep:
    """Tests for ComputeEmbeddingStep (embedding generation)."""

    @pytest.mark.asyncio'''

content = content.replace(old, new)

with open('tests/integration/pipeline/test_compute_embedding.py', 'w', encoding='utf-8') as f:
    f.write(content)

print('Fixed test_compute_embedding.py')
import re

with open('tests/integration/pipeline/test_compute_embedding.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Use regex to replace the mock_embedding_service fixture
pattern = r'(@pytest\.fixture\s+def mock_embedding_service\(self\):.*?return service)'
replacement = '''    @pytest.fixture
    def mock_embedding_service(self):
        """Create a mock embedding service."""
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