# 前后端对接完成 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 完成 Chapter 和 Cast 功能的后端 API 实现，并更新前端组件使用新 API

**Architecture:** 基于现有 DDD 架构，实现 Chapter 和 Bible 相关的 API 端点，前端从 bookApi 迁移到 novelApi

**Tech Stack:** Python 3.11, FastAPI, Vue 3, TypeScript, Pinia

---

## File Structure

### Backend Files
- `interfaces/api/v1/chapters.py` - Chapter API 端点（新建）
- `application/services/chapter_service.py` - Chapter 应用服务（已存在，可能需要增强）
- `application/dtos/chapter_dto.py` - Chapter DTO（已存在）
- `interfaces/api/v1/bible.py` - Bible API 端点（已存在，可能需要增强）

### Frontend Files
- `web-app/src/api/chapter.ts` - Chapter API 客户端（新建）
- `web-app/src/views/Chapter.vue` - 章节视图（修改）
- `web-app/src/views/Cast.vue` - 人物视图（修改）
- `web-app/src/views/Workbench.vue` - 工作台视图（修改）

---

## Task 1: Chapter API 端点实现

**Files:**
- Create: `interfaces/api/v1/chapters.py`
- Reference: `interfaces/api/v1/novels.py`
- Reference: `application/services/chapter_service.py`

### Step 1: 编写 Chapter API 测试

- [ ] **创建测试文件**

Create: `tests/integration/interfaces/api/v1/test_chapters_api.py`

```python
import pytest
from fastapi.testclient import TestClient
from interfaces.main import app

client = TestClient(app)

def test_list_chapters():
    """测试获取章节列表"""
    # 先创建一个小说
    novel_response = client.post("/api/v1/novels", json={
        "novel_id": "test-novel-chapters",
        "title": "测试小说",
        "author": "测试作者",
        "target_chapters": 10
    })
    assert novel_response.status_code == 200

    # 获取章节列表
    response = client.get("/api/v1/novels/test-novel-chapters/chapters")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_chapter_detail():
    """测试获取章节详情"""
    novel_id = "test-novel-chapters"

    # 假设已有章节，获取第一章
    response = client.get(f"/api/v1/novels/{novel_id}/chapters/1")

    # 如果没有章节，应该返回 404
    if response.status_code == 404:
        assert "not found" in response.json()["detail"].lower()
    else:
        assert response.status_code == 200
        data = response.json()
        assert "number" in data
        assert "title" in data
        assert "content" in data

def test_update_chapter_content():
    """测试更新章节内容"""
    novel_id = "test-novel-chapters"
    chapter_number = 1

    response = client.put(
        f"/api/v1/novels/{novel_id}/chapters/{chapter_number}",
        json={
            "title": "更新的标题",
            "content": "更新的内容"
        }
    )

    # 如果章节不存在，应该返回 404
    if response.status_code == 404:
        assert "not found" in response.json()["detail"].lower()
    else:
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "更新的标题"
        assert data["content"] == "更新的内容"
```

- [ ] **运行测试确认失败**

```bash
pytest tests/integration/interfaces/api/v1/test_chapters_api.py -v
```

Expected: FAIL - "No module named 'interfaces.api.v1.chapters'" 或路由不存在

### Step 2: 实现 Chapter API 端点

- [ ] **创建 chapters.py**

Create: `interfaces/api/v1/chapters.py`

```python
from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel

from application.services.chapter_service import ChapterService
from application.dtos.chapter_dto import ChapterDTO
from domain.novel.value_objects.novel_id import NovelId
from domain.shared.exceptions import EntityNotFoundError
from interfaces.dependencies import get_chapter_service

router = APIRouter(prefix="/novels/{novel_id}/chapters", tags=["chapters"])


class UpdateChapterRequest(BaseModel):
    title: str
    content: str


@router.get("", response_model=List[ChapterDTO])
async def list_chapters(
    novel_id: str,
    chapter_service: ChapterService = Depends(get_chapter_service)
):
    """获取小说的所有章节"""
    try:
        chapters = chapter_service.list_chapters(novel_id)
        return chapters
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/{chapter_number}", response_model=ChapterDTO)
async def get_chapter(
    novel_id: str,
    chapter_number: int,
    chapter_service: ChapterService = Depends(get_chapter_service)
):
    """获取指定章节"""
    try:
        chapter = chapter_service.get_chapter(novel_id, chapter_number)
        if chapter is None:
            raise HTTPException(
                status_code=404,
                detail=f"Chapter {chapter_number} not found in novel {novel_id}"
            )
        return chapter
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{chapter_number}", response_model=ChapterDTO)
async def update_chapter(
    novel_id: str,
    chapter_number: int,
    request: UpdateChapterRequest,
    chapter_service: ChapterService = Depends(get_chapter_service)
):
    """更新章节内容"""
    try:
        chapter = chapter_service.update_chapter(
            novel_id=novel_id,
            chapter_number=chapter_number,
            title=request.title,
            content=request.content
        )
        return chapter
    except EntityNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

- [ ] **在 main.py 中注册路由**

Modify: `interfaces/main.py`

找到路由注册部分，添加：

```python
from interfaces.api.v1 import chapters

# 在现有路由注册后添加
app.include_router(chapters.router, prefix="/api/v1")
```

### Step 3: 检查 ChapterService 是否需要增强

- [ ] **检查现有 ChapterService**

Read: `application/services/chapter_service.py`

如果缺少 `list_chapters` 或 `update_chapter` 方法，需要添加。

- [ ] **如果需要，添加缺失方法**

Modify: `application/services/chapter_service.py`

```python
def list_chapters(self, novel_id: str) -> List[ChapterDTO]:
    """获取小说的所有章节"""
    novel = self.novel_repository.get_by_id(NovelId(novel_id))
    if novel is None:
        raise EntityNotFoundError("Novel", novel_id)

    return [ChapterDTO.from_domain(chapter) for chapter in novel.chapters]

def update_chapter(
    self,
    novel_id: str,
    chapter_number: int,
    title: str,
    content: str
) -> ChapterDTO:
    """更新章节内容"""
    novel = self.novel_repository.get_by_id(NovelId(novel_id))
    if novel is None:
        raise EntityNotFoundError("Novel", novel_id)

    # 查找章节
    chapter = next(
        (ch for ch in novel.chapters if ch.number == chapter_number),
        None
    )

    if chapter is None:
        raise EntityNotFoundError("Chapter", f"{novel_id}/chapter-{chapter_number}")

    # 更新章节
    chapter.title = title
    chapter.update_content(content)

    # 保存
    self.novel_repository.save(novel)

    return ChapterDTO.from_domain(chapter)
```

### Step 4: 运行测试确认通过

- [ ] **运行测试**

```bash
pytest tests/integration/interfaces/api/v1/test_chapters_api.py -v
```

Expected: PASS (所有测试通过)

### Step 5: 提交

- [ ] **提交代码**

```bash
git add interfaces/api/v1/chapters.py
git add interfaces/main.py
git add application/services/chapter_service.py
git add tests/integration/interfaces/api/v1/test_chapters_api.py
git commit -m "feat: add chapter API endpoints"
```

---

## Task 2: 前端 Chapter API 客户端

**Files:**
- Create: `web-app/src/api/chapter.ts`
- Reference: `web-app/src/api/novel.ts`

### Step 1: 创建 chapter.ts

- [ ] **创建 API 客户端**

Create: `web-app/src/api/chapter.ts`

```typescript
import axios from 'axios'

export interface ChapterDTO {
  id: string
  novel_id: string
  number: int
  title: string
  content: string
  status: string
  word_count: number
  created_at: string
  updated_at: string
}

export interface UpdateChapterRequest {
  title: string
  content: string
}

export const chapterApi = {
  /**
   * 获取小说的所有章节
   */
  async listChapters(novelId: string): Promise<ChapterDTO[]> {
    const response = await axios.get(`/api/v1/novels/${novelId}/chapters`)
    return response.data
  },

  /**
   * 获取指定章节
   */
  async getChapter(novelId: string, chapterNumber: number): Promise<ChapterDTO> {
    const response = await axios.get(`/api/v1/novels/${novelId}/chapters/${chapterNumber}`)
    return response.data
  },

  /**
   * 更新章节内容
   */
  async updateChapter(
    novelId: string,
    chapterNumber: number,
    data: UpdateChapterRequest
  ): Promise<ChapterDTO> {
    const response = await axios.put(
      `/api/v1/novels/${novelId}/chapters/${chapterNumber}`,
      data
    )
    return response.data
  }
}
```

### Step 2: 提交

- [ ] **提交代码**

```bash
git add web-app/src/api/chapter.ts
git commit -m "feat: add chapter API client"
```

---

## Task 3: 更新 Chapter.vue

**Files:**
- Modify: `web-app/src/views/Chapter.vue`

### Step 1: 读取现有 Chapter.vue

- [ ] **读取文件了解当前实现**

Read: `web-app/src/views/Chapter.vue`

### Step 2: 更新为使用新 API

- [ ] **替换 API 调用**

Modify: `web-app/src/views/Chapter.vue`

在 `<script setup>` 部分：

```typescript
// 旧的导入（删除或注释）
// import { bookApi } from '@/api/book'

// 新的导入
import { chapterApi } from '@/api/chapter'
import { novelApi } from '@/api/novel'

// 更新 fetchChapter 函数
const fetchChapter = async () => {
  if (!route.params.slug || !route.params.chapterId) return

  loading.value = true
  try {
    const novelId = route.params.slug as string
    const chapterNumber = parseInt(route.params.chapterId as string)

    // 使用新 API
    const chapterData = await chapterApi.getChapter(novelId, chapterNumber)

    chapter.value = {
      id: chapterData.id,
      number: chapterData.number,
      title: chapterData.title,
      content: chapterData.content,
      status: chapterData.status,
      word_count: chapterData.word_count
    }
  } catch (error: any) {
    message.error(error.response?.data?.detail || '加载章节失败')
  } finally {
    loading.value = false
  }
}

// 更新 saveChapter 函数
const saveChapter = async () => {
  if (!route.params.slug || !chapter.value) return

  saving.value = true
  try {
    const novelId = route.params.slug as string

    await chapterApi.updateChapter(
      novelId,
      chapter.value.number,
      {
        title: chapter.value.title,
        content: chapter.value.content
      }
    )

    message.success('保存成功')
  } catch (error: any) {
    message.error(error.response?.data?.detail || '保存失败')
  } finally {
    saving.value = false
  }
}
```

### Step 3: 测试前端功能

- [ ] **启动前端开发服务器**

```bash
cd web-app
npm run dev
```

- [ ] **手动测试**

1. 访问 http://localhost:3000
2. 进入某个小说的工作台
3. 点击章节，确认可以加载
4. 编辑章节内容，确认可以保存

Expected: 章节加载和保存功能正常

### Step 4: 提交

- [ ] **提交代码**

```bash
git add web-app/src/views/Chapter.vue
git commit -m "feat: migrate Chapter.vue to new API"
```

---

## Task 4: 增强 Bible API

**Files:**
- Modify: `interfaces/api/v1/bible.py`
- Create: `tests/integration/interfaces/api/v1/test_bible_api.py`

### Step 1: 编写 Bible API 测试

- [ ] **创建测试文件**

Create: `tests/integration/interfaces/api/v1/test_bible_api.py`

```python
import pytest
from fastapi.testclient import TestClient
from interfaces.main import app

client = TestClient(app)

def test_get_bible():
    """测试获取 Bible"""
    novel_id = "test-novel-bible"

    # 先创建小说
    client.post("/api/v1/novels", json={
        "novel_id": novel_id,
        "title": "测试小说",
        "author": "测试作者",
        "target_chapters": 10
    })

    response = client.get(f"/api/v1/novels/{novel_id}/bible")
    assert response.status_code == 200
    data = response.json()
    assert "characters" in data

def test_list_characters():
    """测试获取人物列表"""
    novel_id = "test-novel-bible"
    response = client.get(f"/api/v1/novels/{novel_id}/bible/characters")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_add_character():
    """测试添加人物"""
    novel_id = "test-novel-bible"
    response = client.post(
        f"/api/v1/novels/{novel_id}/bible/characters",
        json={
            "character_id": "char-001",
            "name": "张三",
            "description": "主角"
        }
    )
    assert response.status_code == 200
```

- [ ] **运行测试确认失败**

```bash
pytest tests/integration/interfaces/api/v1/test_bible_api.py -v
```

Expected: FAIL - 部分端点不存在

### Step 2: 增强 Bible API

- [ ] **检查现有 bible.py**

Read: `interfaces/api/v1/bible.py`

- [ ] **添加缺失端点**

Modify: `interfaces/api/v1/bible.py`

添加以下端点（如果不存在）：

```python
@router.get("", response_model=BibleDTO)
async def get_bible(
    novel_id: str,
    bible_service: BibleService = Depends(get_bible_service)
):
    """获取 Bible"""
    bible = bible_service.get_bible_by_novel(novel_id)
    if bible is None:
        raise HTTPException(status_code=404, detail=f"Bible not found")
    return bible

@router.get("/characters")
async def list_characters(
    novel_id: str,
    bible_service: BibleService = Depends(get_bible_service)
):
    """获取人物列表"""
    bible = bible_service.get_bible_by_novel(novel_id)
    return bible.characters if bible else []
```

### Step 3: 运行测试确认通过

- [ ] **运行测试**

```bash
pytest tests/integration/interfaces/api/v1/test_bible_api.py -v
```

Expected: PASS

### Step 4: 提交

- [ ] **提交代码**

```bash
git add interfaces/api/v1/bible.py tests/integration/interfaces/api/v1/test_bible_api.py
git commit -m "feat: enhance bible API endpoints"
```

---

## Task 5: 前端 Bible API 客户端

**Files:**
- Create: `web-app/src/api/bible.ts`

### Step 1: 创建 bible.ts

- [ ] **创建 API 客户端**

Create: `web-app/src/api/bible.ts`

```typescript
import axios from 'axios'

export interface CharacterDTO {
  id: string
  name: string
  description: string
  relationships: string[]
}

export interface BibleDTO {
  id: string
  novel_id: string
  characters: CharacterDTO[]
  world_settings: any[]
}

export interface AddCharacterRequest {
  character_id: string
  name: string
  description: string
}

export const bibleApi = {
  async getBible(novelId: string): Promise<BibleDTO> {
    const response = await axios.get(`/api/v1/novels/${novelId}/bible`)
    return response.data
  },

  async listCharacters(novelId: string): Promise<CharacterDTO[]> {
    const response = await axios.get(`/api/v1/novels/${novelId}/bible/characters`)
    return response.data
  },

  async addCharacter(novelId: string, data: AddCharacterRequest): Promise<BibleDTO> {
    const response = await axios.post(
      `/api/v1/novels/${novelId}/bible/characters`,
      data
    )
    return response.data
  }
}
```

### Step 2: 提交

- [ ] **提交代码**

```bash
git add web-app/src/api/bible.ts
git commit -m "feat: add bible API client"
```

---

## Task 6: 更新 Cast.vue

**Files:**
- Modify: `web-app/src/views/Cast.vue`

### Step 1: 读取现有 Cast.vue

- [ ] **读取文件了解当前实现**

Read: `web-app/src/views/Cast.vue`

### Step 2: 更新为使用新 API

- [ ] **替换 API 调用**

Modify: `web-app/src/views/Cast.vue`

在 `<script setup>` 部分，替换 bookApi 为 bibleApi：

```typescript
// 删除旧导入
// import { bookApi } from '@/api/book'

// 添加新导入
import { bibleApi } from '@/api/bible'

// 更新 fetchCharacters 函数
const fetchCharacters = async () => {
  if (!route.params.slug) return
  loading.value = true
  try {
    const novelId = route.params.slug as string
    const charactersData = await bibleApi.listCharacters(novelId)
    characters.value = charactersData
  } catch (error: any) {
    message.error(error.response?.data?.detail || '加载人物失败')
  } finally {
    loading.value = false
  }
}

// 更新 addCharacter 函数
const addCharacter = async () => {
  if (!route.params.slug || !newCharacter.value.name) return
  saving.value = true
  try {
    const novelId = route.params.slug as string
    await bibleApi.addCharacter(novelId, {
      character_id: `char-${Date.now()}`,
      name: newCharacter.value.name,
      description: newCharacter.value.description
    })
    message.success('添加成功')
    await fetchCharacters()
    newCharacter.value = { name: '', description: '' }
    showAddDialog.value = false
  } catch (error: any) {
    message.error(error.response?.data?.detail || '添加失败')
  } finally {
    saving.value = false
  }
}
```

### Step 3: 测试前端功能

- [ ] **手动测试**

1. 访问 http://localhost:3000
2. 进入某个小说的人物管理
3. 确认可以查看人物列表
4. 添加新人物，确认可以保存

Expected: 人物管理功能正常

### Step 4: 提交

- [ ] **提交代码**

```bash
git add web-app/src/views/Cast.vue
git commit -m "feat: migrate Cast.vue to new API"
```

---

## Task 7: 更新 Workbench.vue

**Files:**
- Modify: `web-app/src/views/Workbench.vue`

### Step 1: 读取现有 Workbench.vue

- [ ] **读取文件了解当前实现**

Read: `web-app/src/views/Workbench.vue`

### Step 2: 更新为使用新 API

- [ ] **替换 API 调用**

Modify: `web-app/src/views/Workbench.vue`

在 `<script setup>` 部分，替换 bookApi 为 novelApi 和 chapterApi：

```typescript
// 删除旧导入
// import { bookApi } from '@/api/book'

// 添加新导入
import { novelApi } from '@/api/novel'
import { chapterApi } from '@/api/chapter'

// 更新 fetchNovel 函数
const fetchNovel = async () => {
  if (!route.params.slug) return
  loading.value = true
  try {
    const novelId = route.params.slug as string
    const novelData = await novelApi.getNovel(novelId)
    novel.value = {
      id: novelData.id,
      title: novelData.title,
      author: novelData.author,
      stage: novelData.stage,
      target_chapters: novelData.target_chapters,
      completed_chapters: novelData.completed_chapters
    }
  } catch (error: any) {
    message.error(error.response?.data?.detail || '加载小说失败')
  } finally {
    loading.value = false
  }
}

// 更新 fetchChapters 函数
const fetchChapters = async () => {
  if (!route.params.slug) return
  try {
    const novelId = route.params.slug as string
    const chaptersData = await chapterApi.listChapters(novelId)
    chapters.value = chaptersData.map(ch => ({
      id: ch.id,
      number: ch.number,
      title: ch.title,
      status: ch.status,
      word_count: ch.word_count
    }))
  } catch (error: any) {
    message.error(error.response?.data?.detail || '加载章节失败')
  }
}
```

### Step 3: 测试前端功能

- [ ] **手动测试**

1. 访问 http://localhost:3000
2. 进入某个小说的工作台
3. 确认可以看到小说信息和章节列表
4. 点击章节跳转，确认功能正常

Expected: 工作台功能正常

### Step 4: 提交

- [ ] **提交代码**

```bash
git add web-app/src/views/Workbench.vue
git commit -m "feat: migrate Workbench.vue to new API"
```

---

## Task 8: 端到端测试

**Files:**
- None (manual testing)

### Step 1: 启动后端服务

- [ ] **启动后端**

```bash
python -m uvicorn interfaces.main:app --reload --port 8000
```

Expected: 服务启动在 http://localhost:8000

### Step 2: 启动前端服务

- [ ] **启动前端**

```bash
cd web-app
npm run dev
```

Expected: 服务启动在 http://localhost:3000

### Step 3: 完整流程测试

- [ ] **测试完整流程**

1. 访问 http://localhost:3000
2. 创建新书目
3. 进入工作台，确认可以看到小说信息
4. 查看章节列表
5. 点击章节，编辑内容并保存
6. 进入人物管理，添加人物
7. 返回工作台，确认所有功能正常

Expected: 所有功能正常工作，无报错

### Step 4: 检查浏览器控制台

- [ ] **检查是否有错误**

打开浏览器开发者工具（F12），检查 Console 和 Network 标签

Expected: 无 404 错误，无 API 调用失败

---

## Task 9: 清理旧代码

**Files:**
- Delete: `web-app/src/api/book.ts` (如果存在且不再使用)

### Step 1: 确认旧 API 不再使用

- [ ] **搜索 bookApi 引用**

```bash
cd web-app
grep -r "bookApi" src/ || echo "No references found"
```

Expected: 无结果或只在已删除的文件中

### Step 2: 删除旧文件（如果存在）

- [ ] **删除 book.ts**

```bash
if [ -f web-app/src/api/book.ts ]; then
  git rm web-app/src/api/book.ts
  echo "Deleted book.ts"
else
  echo "book.ts does not exist, skipping"
fi
```

### Step 3: 提交

- [ ] **提交清理**

```bash
git commit -m "chore: remove deprecated book API" --allow-empty
```

---

## 完成检查清单

- [ ] 所有后端 API 端点实现并测试通过
- [ ] 所有前端组件迁移到新 API
- [ ] 端到端测试通过
- [ ] 旧代码已清理
- [ ] 所有更改已提交到 git

---

## 预期结果

完成后，前后端完全对接：
- ✅ Chapter.vue 使用新 API
- ✅ Cast.vue 使用新 API
- ✅ Workbench.vue 使用新 API
- ✅ 所有功能正常工作
- ✅ 无遗留的 bookApi 引用



