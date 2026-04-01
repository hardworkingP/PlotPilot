# 子项目 2: 向量检索基础设施 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 集成向量数据库，实现章节和人物的语义检索

**Architecture:** 集成 Qdrant/Milvus/Chroma 向量数据库，实现 Embedding 服务和章节摘要生成

**Tech Stack:** Python 3.11, OpenAI Embedding API, Qdrant/Chroma, pytest

**Dependencies:** 无（独立子项目）

**Estimated Time:** 1-2 周

---

## File Structure

### Domain Files (New)
- `domain/ai/services/embedding_service.py` - Embedding 服务接口
- `domain/ai/services/vector_store.py` - 向量存储接口
- `domain/ai/services/chapter_summarizer.py` - 章节摘要服务接口

### Infrastructure Files (New)
- `infrastructure/ai/openai_embedding_service.py` - OpenAI Embedding 实现
- `infrastructure/ai/qdrant_vector_store.py` - Qdrant 向量存储实现
- `infrastructure/ai/claude_chapter_summarizer.py` - Claude 摘要实现

### Application Files (New)
- `application/services/indexing_service.py` - 索引服务

### Test Files (New)
- `tests/unit/domain/ai/services/test_embedding_service.py`
- `tests/integration/infrastructure/ai/test_qdrant_vector_store.py`
- `tests/integration/application/services/test_indexing_service.py`

---

## Task 1: 选择并安装向量数据库

**Files:**
- Create: `requirements.txt` (add dependencies)
- Create: `docker-compose.yml` (for Qdrant)

### Step 1: 评估向量数据库选项

- [ ] **比较三个选项**

| 数据库 | 优点 | 缺点 | 推荐度 |
|--------|------|------|--------|
| Qdrant | 性能好，功能完整，Docker 部署简单 | 需要额外服务 | ⭐⭐⭐⭐⭐ |
| Chroma | 轻量级，嵌入式，无需额外服务 | 性能较弱 | ⭐⭐⭐⭐ |
| Milvus | 企业级，功能强大 | 复杂，资源占用大 | ⭐⭐⭐ |

**决策**: 使用 Qdrant（性能和易用性平衡最好）

### Step 2: 添加依赖

- [ ] **更新 requirements.txt**

Edit: `requirements.txt`

添加：
```
qdrant-client==1.7.0
openai==1.12.0
```

- [ ] **安装依赖**

```bash
pip install -r requirements.txt
```

Expected: 安装成功

### Step 3: 创建 Docker Compose 配置

- [ ] **创建 docker-compose.yml**

Create: `docker-compose.yml`

```yaml
version: '3.8'

services:
  qdrant:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
      - "6334:6334"
    volumes:
      - ./data/qdrant_storage:/qdrant/storage
    environment:
      - QDRANT__SERVICE__GRPC_PORT=6334
```

- [ ] **启动 Qdrant**

```bash
docker-compose up -d qdrant
```

Expected: Qdrant 启动在 http://localhost:6333

### Step 4: 验证连接

- [ ] **测试连接**

```bash
curl http://localhost:6333/collections
```

Expected: 返回空列表 `{"result":{"collections":[]}}`

### Step 5: 提交

- [ ] **提交配置**

```bash
git add requirements.txt docker-compose.yml
git commit -m "feat: add Qdrant vector database setup"
```

---

## Task 2: EmbeddingService 接口和实现

**Files:**
- Create: `domain/ai/services/embedding_service.py`
- Create: `infrastructure/ai/openai_embedding_service.py`
- Create: `tests/unit/infrastructure/ai/test_openai_embedding_service.py`

### Step 1: 定义接口

- [ ] **创建 EmbeddingService 接口**

Create: `domain/ai/services/embedding_service.py`

```python
from abc import ABC, abstractmethod
from typing import List

class EmbeddingService(ABC):
    """Embedding 服务接口"""

    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """生成文本的向量嵌入"""
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量生成向量嵌入"""
        pass

    @abstractmethod
    def get_dimension(self) -> int:
        """获取向量维度"""
        pass
```

### Step 2: 实现 OpenAI Embedding

- [ ] **创建 OpenAIEmbeddingService**

Create: `infrastructure/ai/openai_embedding_service.py`

```python
import os
from typing import List
from openai import AsyncOpenAI
from domain.ai.services.embedding_service import EmbeddingService

class OpenAIEmbeddingService(EmbeddingService):
    """OpenAI Embedding 服务实现"""

    def __init__(self, model: str = "text-embedding-3-small"):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        self._dimension = 1536 if "small" in model else 3072

    async def embed(self, text: str) -> List[float]:
        """生成单个文本的向量嵌入"""
        response = await self.client.embeddings.create(
            model=self.model,
            input=text
        )
        return response.data[0].embedding

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量生成向量嵌入"""
        response = await self.client.embeddings.create(
            model=self.model,
            input=texts
        )
        return [item.embedding for item in response.data]

    def get_dimension(self) -> int:
        """获取向量维度"""
        return self._dimension
```

### Step 3: 编写测试

- [ ] **创建测试**

Create: `tests/unit/infrastructure/ai/test_openai_embedding_service.py`

```python
import pytest
import os
from infrastructure.ai.openai_embedding_service import OpenAIEmbeddingService

@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set"
)
@pytest.mark.asyncio
async def test_embed_single_text():
    """测试单个文本嵌入"""
    service = OpenAIEmbeddingService()
    embedding = await service.embed("Hello world")

    assert isinstance(embedding, list)
    assert len(embedding) == service.get_dimension()
    assert all(isinstance(x, float) for x in embedding)

@pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set"
)
@pytest.mark.asyncio
async def test_embed_batch():
    """测试批量嵌入"""
    service = OpenAIEmbeddingService()
    texts = ["Hello", "World", "Test"]
    embeddings = await service.embed_batch(texts)

    assert len(embeddings) == 3
    assert all(len(emb) == service.get_dimension() for emb in embeddings)
```

- [ ] **运行测试**

```bash
pytest tests/unit/infrastructure/ai/test_openai_embedding_service.py -v
```

Expected: PASS（如果设置了 OPENAI_API_KEY）

### Step 4: 提交

- [ ] **提交代码**

```bash
git add domain/ai/services/embedding_service.py
git add infrastructure/ai/openai_embedding_service.py
git add tests/unit/infrastructure/ai/test_openai_embedding_service.py
git commit -m "feat: add EmbeddingService interface and OpenAI implementation"
```

---

## Task 3-7: 剩余任务概要

由于篇幅限制，以下任务遵循相同的 TDD 模式（测试 → 实现 → 验证 → 提交）：

### Task 3: VectorStore 接口和 Qdrant 实现
- 定义 VectorStore 接口（insert, search, delete）
- 实现 QdrantVectorStore
- 创建 collections（chapters, characters）
- 测试索引和检索功能

### Task 4: ChapterSummarizer 服务
- 定义 ChapterSummarizer 接口
- 实现 ClaudeChapterSummarizer（使用 LLM 生成摘要）
- 测试摘要生成（3000 字 → 300 字）

### Task 5: IndexingService 应用服务
- 创建 IndexingService（协调 Embedding + VectorStore）
- 实现 index_chapter() 方法
- 实现 search_chapters() 方法
- 集成测试

### Task 6: 批量索引和性能测试
- 实现 batch_index_chapters()
- 性能测试（索引 100 章的时间）
- 优化批量处理

### Task 7: 集成到现有系统
- 在 ChapterService 中集成索引
- 章节创建/更新时自动索引
- 添加搜索 API 端点

---

## 完成检查清单

- [ ] Qdrant 数据库运行正常
- [ ] EmbeddingService 实现并测试通过
- [ ] VectorStore 实现并测试通过
- [ ] ChapterSummarizer 实现并测试通过
- [ ] IndexingService 实现并测试通过
- [ ] 性能测试通过（< 100ms 检索时间）
- [ ] 集成到现有系统
- [ ] 所有代码已提交

---

## 预期结果

- ✅ 向量检索基础设施就绪
- ✅ 支持章节语义检索
- ✅ 支持人物向量索引
- ✅ 性能满足要求（< 100ms）

**下一步**: 子项目 3（人物管理系统）

