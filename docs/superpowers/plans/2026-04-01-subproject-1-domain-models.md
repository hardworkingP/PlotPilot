# 子项目 1: 基础领域模型扩展 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现 PlotArc、ForeshadowingRegistry、EventTimeline 等基础领域模型

**Architecture:** 基于现有 DDD 架构，扩展 domain 层的实体和值对象

**Tech Stack:** Python 3.11, pytest, DDD

**Dependencies:** 无（独立子项目）

**Estimated Time:** 1-2 周

---

## File Structure

### Domain Files (New)
- `domain/novel/entities/plot_arc.py` - 剧情曲线实体
- `domain/novel/value_objects/plot_point.py` - 剧情点值对象
- `domain/novel/value_objects/tension_level.py` - 张力等级值对象
- `domain/novel/entities/foreshadowing_registry.py` - 伏笔注册表实体
- `domain/novel/value_objects/foreshadowing.py` - 伏笔值对象
- `domain/novel/value_objects/event_timeline.py` - 事件时间线值对象
- `domain/novel/value_objects/novel_event.py` - 小说事件值对象
- `domain/bible/value_objects/relationship_graph.py` - 关系图谱值对象
- `domain/bible/value_objects/relationship.py` - 关系值对象

### Repository Files (New)
- `domain/novel/repositories/plot_arc_repository.py` - PlotArc 仓储接口
- `domain/novel/repositories/foreshadowing_repository.py` - Foreshadowing 仓储接口
- `infrastructure/persistence/repositories/file_plot_arc_repository.py` - PlotArc 文件仓储实现
- `infrastructure/persistence/repositories/file_foreshadowing_repository.py` - Foreshadowing 文件仓储实现

### Test Files (New)
- `tests/unit/domain/novel/entities/test_plot_arc.py`
- `tests/unit/domain/novel/entities/test_foreshadowing_registry.py`
- `tests/unit/domain/novel/value_objects/test_event_timeline.py`
- `tests/unit/domain/bible/value_objects/test_relationship_graph.py`
- `tests/integration/infrastructure/persistence/repositories/test_file_plot_arc_repository.py`

---

## Task 1: PlotPoint 和 TensionLevel 值对象

**Files:**
- Create: `domain/novel/value_objects/plot_point.py`
- Create: `domain/novel/value_objects/tension_level.py`
- Create: `tests/unit/domain/novel/value_objects/test_plot_point.py`

### Step 1: 编写 TensionLevel 测试

- [ ] **创建测试文件**

Create: `tests/unit/domain/novel/value_objects/test_tension_level.py`

```python
import pytest
from domain.novel.value_objects.tension_level import TensionLevel

def test_tension_level_enum():
    """测试张力等级枚举"""
    assert TensionLevel.LOW.value == 1
    assert TensionLevel.MEDIUM.value == 2
    assert TensionLevel.HIGH.value == 3
    assert TensionLevel.PEAK.value == 4

def test_tension_level_comparison():
    """测试张力等级比较"""
    assert TensionLevel.LOW < TensionLevel.MEDIUM
    assert TensionLevel.HIGH > TensionLevel.MEDIUM
    assert TensionLevel.PEAK > TensionLevel.HIGH
```

- [ ] **运行测试确认失败**

```bash
pytest tests/unit/domain/novel/value_objects/test_tension_level.py -v
```

Expected: FAIL - Module not found

### Step 2: 实现 TensionLevel

- [ ] **创建 tension_level.py**

Create: `domain/novel/value_objects/tension_level.py`

```python
from enum import Enum

class TensionLevel(int, Enum):
    """张力等级"""
    LOW = 1      # 平缓
    MEDIUM = 2   # 中等
    HIGH = 3     # 紧张
    PEAK = 4     # 极度紧张
```

- [ ] **运行测试确认通过**

```bash
pytest tests/unit/domain/novel/value_objects/test_tension_level.py -v
```

Expected: PASS

### Step 3: 编写 PlotPoint 测试

- [ ] **创建测试文件**

Create: `tests/unit/domain/novel/value_objects/test_plot_point.py`

```python
import pytest
from domain.novel.value_objects.plot_point import PlotPoint, PlotPointType
from domain.novel.value_objects.tension_level import TensionLevel

def test_create_plot_point():
    """测试创建剧情点"""
    point = PlotPoint(
        chapter_number=10,
        point_type=PlotPointType.TURNING_POINT,
        description="主角发现真相",
        tension=TensionLevel.HIGH
    )
    assert point.chapter_number == 10
    assert point.point_type == PlotPointType.TURNING_POINT
    assert point.description == "主角发现真相"
    assert point.tension == TensionLevel.HIGH

def test_plot_point_type_enum():
    """测试剧情点类型枚举"""
    assert PlotPointType.OPENING.value == "opening"
    assert PlotPointType.CLIMAX.value == "climax"
```

- [ ] **运行测试确认失败**

```bash
pytest tests/unit/domain/novel/value_objects/test_plot_point.py -v
```

Expected: FAIL

### Step 4: 实现 PlotPoint

- [ ] **创建 plot_point.py**

Create: `domain/novel/value_objects/plot_point.py`

```python
from dataclasses import dataclass
from enum import Enum
from domain.novel.value_objects.tension_level import TensionLevel

class PlotPointType(str, Enum):
    """剧情点类型"""
    OPENING = "opening"              # 开端
    RISING_ACTION = "rising"         # 上升
    TURNING_POINT = "turning"        # 转折
    CLIMAX = "climax"                # 高潮
    FALLING_ACTION = "falling"       # 下降
    RESOLUTION = "resolution"        # 结局

@dataclass(frozen=True)
class PlotPoint:
    """剧情点值对象"""
    chapter_number: int
    point_type: PlotPointType
    description: str
    tension: TensionLevel

    def __post_init__(self):
        if self.chapter_number < 1:
            raise ValueError("Chapter number must be >= 1")
        if not self.description or not self.description.strip():
            raise ValueError("Description cannot be empty")
```

- [ ] **运行测试确认通过**

```bash
pytest tests/unit/domain/novel/value_objects/test_plot_point.py -v
```

Expected: PASS

### Step 5: 提交

- [ ] **提交代码**

```bash
git add domain/novel/value_objects/plot_point.py
git add domain/novel/value_objects/tension_level.py
git add tests/unit/domain/novel/value_objects/test_plot_point.py
git add tests/unit/domain/novel/value_objects/test_tension_level.py
git commit -m "feat: add PlotPoint and TensionLevel value objects"
```

---

## Task 2: PlotArc 实体

**Files:**
- Create: `domain/novel/entities/plot_arc.py`
- Create: `tests/unit/domain/novel/entities/test_plot_arc.py`

### Step 1: 编写 PlotArc 测试

- [ ] **创建测试文件**

Create: `tests/unit/domain/novel/entities/test_plot_arc.py`

```python
import pytest
from domain.novel.entities.plot_arc import PlotArc
from domain.novel.value_objects.novel_id import NovelId
from domain.novel.value_objects.plot_point import PlotPoint, PlotPointType
from domain.novel.value_objects.tension_level import TensionLevel

def test_create_plot_arc():
    """测试创建剧情曲线"""
    arc = PlotArc(id="arc-1", novel_id=NovelId("novel-1"))
    assert arc.id == "arc-1"
    assert arc.novel_id.value == "novel-1"
    assert len(arc.key_points) == 0

def test_add_plot_point():
    """测试添加剧情点"""
    arc = PlotArc(id="arc-1", novel_id=NovelId("novel-1"))
    point = PlotPoint(
        chapter_number=1,
        point_type=PlotPointType.OPENING,
        description="故事开始",
        tension=TensionLevel.LOW
    )
    arc.add_plot_point(point)
    assert len(arc.key_points) == 1
    assert arc.key_points[0].chapter_number == 1

def test_get_expected_tension():
    """测试获取预期张力"""
    arc = PlotArc(id="arc-1", novel_id=NovelId("novel-1"))
    arc.add_plot_point(PlotPoint(1, PlotPointType.OPENING, "开始", TensionLevel.LOW))
    arc.add_plot_point(PlotPoint(50, PlotPointType.CLIMAX, "高潮", TensionLevel.PEAK))

    # 第 1 章应该是 LOW
    assert arc.get_expected_tension(1) == TensionLevel.LOW
    # 第 50 章应该是 PEAK
    assert arc.get_expected_tension(50) == TensionLevel.PEAK
    # 中间章节应该插值
    tension_25 = arc.get_expected_tension(25)
    assert tension_25 in [TensionLevel.LOW, TensionLevel.MEDIUM, TensionLevel.HIGH]
```

- [ ] **运行测试确认失败**

```bash
pytest tests/unit/domain/novel/entities/test_plot_arc.py -v
```

Expected: FAIL

### Step 2: 实现 PlotArc

- [ ] **创建 plot_arc.py**

Create: `domain/novel/entities/plot_arc.py`

```python
from typing import List, Optional
from domain.shared.base_entity import BaseEntity
from domain.novel.value_objects.novel_id import NovelId
from domain.novel.value_objects.plot_point import PlotPoint
from domain.novel.value_objects.tension_level import TensionLevel

class PlotArc(BaseEntity):
    """剧情曲线实体"""

    def __init__(self, id: str, novel_id: NovelId):
        super().__init__(id)
        self.novel_id = novel_id
        self.key_points: List[PlotPoint] = []

    def add_plot_point(self, point: PlotPoint) -> None:
        """添加剧情点"""
        # 按章节号排序插入
        self.key_points.append(point)
        self.key_points.sort(key=lambda p: p.chapter_number)

    def get_expected_tension(self, chapter_number: int) -> TensionLevel:
        """获取指定章节的预期张力水平（线性插值）"""
        if not self.key_points:
            return TensionLevel.MEDIUM

        # 找到前后两个剧情点
        before = None
        after = None

        for point in self.key_points:
            if point.chapter_number <= chapter_number:
                before = point
            if point.chapter_number >= chapter_number and after is None:
                after = point

        # 如果正好在剧情点上
        if before and before.chapter_number == chapter_number:
            return before.tension
        if after and after.chapter_number == chapter_number:
            return after.tension

        # 如果只有一个剧情点
        if before and not after:
            return before.tension
        if after and not before:
            return after.tension

        # 线性插值
        if before and after:
            ratio = (chapter_number - before.chapter_number) / (after.chapter_number - before.chapter_number)
            tension_value = before.tension.value + ratio * (after.tension.value - before.tension.value)
            return TensionLevel(round(tension_value))

        return TensionLevel.MEDIUM

    def get_next_plot_point(self, current_chapter: int) -> Optional[PlotPoint]:
        """获取下一个剧情点"""
        for point in self.key_points:
            if point.chapter_number > current_chapter:
                return point
        return None
```

- [ ] **运行测试确认通过**

```bash
pytest tests/unit/domain/novel/entities/test_plot_arc.py -v
```

Expected: PASS

### Step 3: 提交

- [ ] **提交代码**

```bash
git add domain/novel/entities/plot_arc.py
git add tests/unit/domain/novel/entities/test_plot_arc.py
git commit -m "feat: add PlotArc entity"
```

---

## Task 3: Foreshadowing 值对象

**Files:**
- Create: `domain/novel/value_objects/foreshadowing.py`
- Create: `tests/unit/domain/novel/value_objects/test_foreshadowing.py`

### Step 1: 编写 Foreshadowing 测试

- [ ] **创建测试文件**

Create: `tests/unit/domain/novel/value_objects/test_foreshadowing.py`

```python
import pytest
from domain.novel.value_objects.foreshadowing import Foreshadowing, ForeshadowingStatus, ImportanceLevel

def test_create_foreshadowing():
    """测试创建伏笔"""
    foreshadow = Foreshadowing(
        id="foreshadow-1",
        planted_in_chapter=10,
        description="主角捡到神秘玉佩",
        importance=ImportanceLevel.HIGH,
        status=ForeshadowingStatus.PLANTED
    )
    assert foreshadow.id == "foreshadow-1"
    assert foreshadow.planted_in_chapter == 10
    assert foreshadow.status == ForeshadowingStatus.PLANTED

def test_foreshadowing_status_enum():
    """测试伏笔状态枚举"""
    assert ForeshadowingStatus.PLANTED.value == "planted"
    assert ForeshadowingStatus.RESOLVED.value == "resolved"
    assert ForeshadowingStatus.ABANDONED.value == "abandoned"

def test_importance_level_enum():
    """测试重要性等级"""
    assert ImportanceLevel.LOW.value == 1
    assert ImportanceLevel.MEDIUM.value == 2
    assert ImportanceLevel.HIGH.value == 3
    assert ImportanceLevel.CRITICAL.value == 4
```

- [ ] **运行测试确认失败**

```bash
pytest tests/unit/domain/novel/value_objects/test_foreshadowing.py -v
```

Expected: FAIL

### Step 2: 实现 Foreshadowing

- [ ] **创建 foreshadowing.py**

Create: `domain/novel/value_objects/foreshadowing.py`

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional

class ForeshadowingStatus(str, Enum):
    """伏笔状态"""
    PLANTED = "planted"      # 已埋下
    RESOLVED = "resolved"    # 已回收
    ABANDONED = "abandoned"  # 已废弃

class ImportanceLevel(int, Enum):
    """重要性等级"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

@dataclass
class Foreshadowing:
    """伏笔值对象"""
    id: str
    planted_in_chapter: int
    description: str
    importance: ImportanceLevel
    status: ForeshadowingStatus
    suggested_resolve_chapter: Optional[int] = None
    resolved_in_chapter: Optional[int] = None

    def __post_init__(self):
        if self.planted_in_chapter < 1:
            raise ValueError("Chapter number must be >= 1")
        if not self.description or not self.description.strip():
            raise ValueError("Description cannot be empty")
        if self.status == ForeshadowingStatus.RESOLVED and self.resolved_in_chapter is None:
            raise ValueError("Resolved foreshadowing must have resolved_in_chapter")
```

- [ ] **运行测试确认通过**

```bash
pytest tests/unit/domain/novel/value_objects/test_foreshadowing.py -v
```

Expected: PASS

### Step 3: 提交

- [ ] **提交代码**

```bash
git add domain/novel/value_objects/foreshadowing.py
git add tests/unit/domain/novel/value_objects/test_foreshadowing.py
git commit -m "feat: add Foreshadowing value object"
```

---

## Task 4: ForeshadowingRegistry 实体

**Files:**
- Create: `domain/novel/entities/foreshadowing_registry.py`
- Create: `tests/unit/domain/novel/entities/test_foreshadowing_registry.py`

### Step 1: 编写测试

- [ ] **创建测试文件**

Create: `tests/unit/domain/novel/entities/test_foreshadowing_registry.py`

```python
import pytest
from domain.novel.entities.foreshadowing_registry import ForeshadowingRegistry
from domain.novel.value_objects.novel_id import NovelId
from domain.novel.value_objects.foreshadowing import Foreshadowing, ForeshadowingStatus, ImportanceLevel

def test_create_registry():
    """测试创建伏笔注册表"""
    registry = ForeshadowingRegistry(id="reg-1", novel_id=NovelId("novel-1"))
    assert registry.id == "reg-1"
    assert len(registry.foreshadowings) == 0

def test_register_foreshadowing():
    """测试注册伏笔"""
    registry = ForeshadowingRegistry(id="reg-1", novel_id=NovelId("novel-1"))
    foreshadow = Foreshadowing(
        id="f-1",
        planted_in_chapter=10,
        description="神秘玉佩",
        importance=ImportanceLevel.HIGH,
        status=ForeshadowingStatus.PLANTED
    )
    registry.register(foreshadow)
    assert len(registry.foreshadowings) == 1

def test_mark_resolved():
    """测试标记伏笔已回收"""
    registry = ForeshadowingRegistry(id="reg-1", novel_id=NovelId("novel-1"))
    foreshadow = Foreshadowing(
        id="f-1",
        planted_in_chapter=10,
        description="神秘玉佩",
        importance=ImportanceLevel.HIGH,
        status=ForeshadowingStatus.PLANTED
    )
    registry.register(foreshadow)
    registry.mark_resolved("f-1", resolved_in_chapter=50)

    resolved = registry.get_by_id("f-1")
    assert resolved.status == ForeshadowingStatus.RESOLVED
    assert resolved.resolved_in_chapter == 50

def test_get_unresolved():
    """测试获取未回收伏笔"""
    registry = ForeshadowingRegistry(id="reg-1", novel_id=NovelId("novel-1"))
    registry.register(Foreshadowing("f-1", 10, "伏笔1", ImportanceLevel.HIGH, ForeshadowingStatus.PLANTED))
    registry.register(Foreshadowing("f-2", 20, "伏笔2", ImportanceLevel.MEDIUM, ForeshadowingStatus.PLANTED))
    registry.mark_resolved("f-1", 50)

    unresolved = registry.get_unresolved()
    assert len(unresolved) == 1
    assert unresolved[0].id == "f-2"
```

- [ ] **运行测试确认失败**

```bash
pytest tests/unit/domain/novel/entities/test_foreshadowing_registry.py -v
```

Expected: FAIL

### Step 2: 实现 ForeshadowingRegistry

- [ ] **创建 foreshadowing_registry.py**

Create: `domain/novel/entities/foreshadowing_registry.py`

```python
from typing import List, Optional
from domain.shared.base_entity import BaseEntity
from domain.novel.value_objects.novel_id import NovelId
from domain.novel.value_objects.foreshadowing import Foreshadowing, ForeshadowingStatus
from domain.shared.exceptions import InvalidOperationError

class ForeshadowingRegistry(BaseEntity):
    """伏笔注册表实体"""

    def __init__(self, id: str, novel_id: NovelId):
        super().__init__(id)
        self.novel_id = novel_id
        self._foreshadowings: List[Foreshadowing] = []

    @property
    def foreshadowings(self) -> List[Foreshadowing]:
        """获取伏笔列表副本"""
        return self._foreshadowings.copy()

    def register(self, foreshadowing: Foreshadowing) -> None:
        """注册新伏笔"""
        if any(f.id == foreshadowing.id for f in self._foreshadowings):
            raise InvalidOperationError(f"Foreshadowing {foreshadowing.id} already exists")
        self._foreshadowings.append(foreshadowing)

    def mark_resolved(self, foreshadowing_id: str, resolved_in_chapter: int) -> None:
        """标记伏笔已回收"""
        foreshadow = self.get_by_id(foreshadowing_id)
        if foreshadow is None:
            raise InvalidOperationError(f"Foreshadowing {foreshadowing_id} not found")

        # 创建新的已回收伏笔对象（值对象不可变）
        resolved = Foreshadowing(
            id=foreshadow.id,
            planted_in_chapter=foreshadow.planted_in_chapter,
            description=foreshadow.description,
            importance=foreshadow.importance,
            status=ForeshadowingStatus.RESOLVED,
            suggested_resolve_chapter=foreshadow.suggested_resolve_chapter,
            resolved_in_chapter=resolved_in_chapter
        )

        # 替换
        self._foreshadowings = [
            resolved if f.id == foreshadowing_id else f
            for f in self._foreshadowings
        ]

    def get_by_id(self, foreshadowing_id: str) -> Optional[Foreshadowing]:
        """根据 ID 获取伏笔"""
        return next((f for f in self._foreshadowings if f.id == foreshadowing_id), None)

    def get_unresolved(self) -> List[Foreshadowing]:
        """获取所有未回收的伏笔"""
        return [f for f in self._foreshadowings if f.status == ForeshadowingStatus.PLANTED]

    def get_ready_to_resolve(self, current_chapter: int) -> List[Foreshadowing]:
        """获取应该在当前章节回收的伏笔"""
        return [
            f for f in self._foreshadowings
            if f.status == ForeshadowingStatus.PLANTED
            and f.suggested_resolve_chapter is not None
            and f.suggested_resolve_chapter <= current_chapter
        ]
```

- [ ] **运行测试确认通过**

```bash
pytest tests/unit/domain/novel/entities/test_foreshadowing_registry.py -v
```

Expected: PASS

### Step 3: 提交

- [ ] **提交代码**

```bash
git add domain/novel/entities/foreshadowing_registry.py
git add tests/unit/domain/novel/entities/test_foreshadowing_registry.py
git commit -m "feat: add ForeshadowingRegistry entity"
```

---

## Task 5: NovelEvent 和 EventTimeline 值对象

**Files:**
- Create: `domain/novel/value_objects/novel_event.py`
- Create: `domain/novel/value_objects/event_timeline.py`
- Create: `tests/unit/domain/novel/value_objects/test_event_timeline.py`

### Step 1: 编写测试

- [ ] **创建测试文件**

Create: `tests/unit/domain/novel/value_objects/test_event_timeline.py`

```python
import pytest
from domain.novel.value_objects.event_timeline import EventTimeline
from domain.novel.value_objects.novel_event import NovelEvent, EventType
from domain.bible.value_objects.character_id import CharacterId

def test_create_timeline():
    """测试创建事件时间线"""
    timeline = EventTimeline()
    assert len(timeline.events) == 0

def test_add_event():
    """测试添加事件"""
    timeline = EventTimeline()
    event = NovelEvent(
        chapter_number=10,
        event_type=EventType.CHARACTER_INTRODUCTION,
        description="张三登场",
        involved_characters=[CharacterId("char-1")]
    )
    timeline.add_event(event)
    assert len(timeline.events) == 1

def test_events_sorted_by_chapter():
    """测试事件按章节号排序"""
    timeline = EventTimeline()
    timeline.add_event(NovelEvent(20, EventType.CONFLICT, "冲突", []))
    timeline.add_event(NovelEvent(10, EventType.CHARACTER_INTRODUCTION, "登场", []))
    timeline.add_event(NovelEvent(15, EventType.DECISION, "决定", []))

    events = timeline.events
    assert events[0].chapter_number == 10
    assert events[1].chapter_number == 15
    assert events[2].chapter_number == 20

def test_get_events_before():
    """测试获取某章节之前的事件"""
    timeline = EventTimeline()
    timeline.add_event(NovelEvent(10, EventType.CHARACTER_INTRODUCTION, "登场", []))
    timeline.add_event(NovelEvent(20, EventType.CONFLICT, "冲突", []))
    timeline.add_event(NovelEvent(30, EventType.DECISION, "决定", []))

    before_25 = timeline.get_events_before(25)
    assert len(before_25) == 2
    assert before_25[0].chapter_number == 10
    assert before_25[1].chapter_number == 20
```

- [ ] **运行测试确认失败**

```bash
pytest tests/unit/domain/novel/value_objects/test_event_timeline.py -v
```

Expected: FAIL

### Step 2: 实现 NovelEvent

- [ ] **创建 novel_event.py**

Create: `domain/novel/value_objects/novel_event.py`

```python
from dataclasses import dataclass
from enum import Enum
from typing import List
from domain.bible.value_objects.character_id import CharacterId

class EventType(str, Enum):
    """事件类型"""
    CHARACTER_INTRODUCTION = "character_intro"
    RELATIONSHIP_CHANGE = "relationship_change"
    CONFLICT = "conflict"
    REVELATION = "revelation"
    DECISION = "decision"

@dataclass(frozen=True)
class NovelEvent:
    """小说事件值对象"""
    chapter_number: int
    event_type: EventType
    description: str
    involved_characters: List[CharacterId]

    def __post_init__(self):
        if self.chapter_number < 1:
            raise ValueError("Chapter number must be >= 1")
        if not self.description or not self.description.strip():
            raise ValueError("Description cannot be empty")
```

### Step 3: 实现 EventTimeline

- [ ] **创建 event_timeline.py**

Create: `domain/novel/value_objects/event_timeline.py`

```python
from typing import List
from domain.novel.value_objects.novel_event import NovelEvent
from domain.bible.value_objects.character_id import CharacterId

class EventTimeline:
    """事件时间线值对象"""

    def __init__(self):
        self._events: List[NovelEvent] = []

    @property
    def events(self) -> List[NovelEvent]:
        """获取事件列表副本"""
        return self._events.copy()

    def add_event(self, event: NovelEvent) -> None:
        """添加事件（自动按章节号排序）"""
        self._events.append(event)
        self._events.sort(key=lambda e: e.chapter_number)

    def get_events_before(self, chapter_number: int) -> List[NovelEvent]:
        """获取某章节之前的所有事件"""
        return [e for e in self._events if e.chapter_number < chapter_number]

    def get_events_involving(self, character_id: CharacterId) -> List[NovelEvent]:
        """获取涉及某人物的所有事件"""
        return [
            e for e in self._events
            if character_id in e.involved_characters
        ]
```

- [ ] **运行测试确认通过**

```bash
pytest tests/unit/domain/novel/value_objects/test_event_timeline.py -v
```

Expected: PASS

### Step 4: 提交

- [ ] **提交代码**

```bash
git add domain/novel/value_objects/novel_event.py
git add domain/novel/value_objects/event_timeline.py
git add tests/unit/domain/novel/value_objects/test_event_timeline.py
git commit -m "feat: add NovelEvent and EventTimeline value objects"
```

---

## Task 6: Relationship 和 RelationshipGraph 值对象

**Files:**
- Create: `domain/bible/value_objects/relationship.py`
- Create: `domain/bible/value_objects/relationship_graph.py`
- Create: `tests/unit/domain/bible/value_objects/test_relationship_graph.py`

### Step 1: 编写测试

- [ ] **创建测试文件**

Create: `tests/unit/domain/bible/value_objects/test_relationship_graph.py`

```python
import pytest
from domain/bible/value_objects.relationship_graph import RelationshipGraph, RelationType
from domain/bible.value_objects.relationship import Relationship
from domain.bible.value_objects.character_id import CharacterId

def test_create_graph():
    """测试创建关系图谱"""
    graph = RelationshipGraph()
    assert graph is not None

def test_add_relationship():
    """测试添加关系"""
    graph = RelationshipGraph()
    char1 = CharacterId("char-1")
    char2 = CharacterId("char-2")
    relation = Relationship(
        relation_type=RelationType.FRIEND,
        established_in_chapter=10,
        description="成为朋友"
    )
    graph.add_relationship(char1, char2, relation)

    current = graph.get_current_relationship(char1, char2)
    assert current is not None
    assert current.relation_type == RelationType.FRIEND

def test_relationship_history():
    """测试关系演变历史"""
    graph = RelationshipGraph()
    char1 = CharacterId("char-1")
    char2 = CharacterId("char-2")

    # 陌生人 -> 朋友 -> 恋人
    graph.add_relationship(char1, char2, Relationship(RelationType.STRANGER, 1, "初次见面"))
    graph.add_relationship(char1, char2, Relationship(RelationType.FRIEND, 10, "成为朋友"))
    graph.add_relationship(char1, char2, Relationship(RelationType.LOVER, 50, "确立关系"))

    history = graph.get_relationship_history(char1, char2)
    assert len(history) == 3
    assert history[0].relation_type == RelationType.STRANGER
    assert history[2].relation_type == RelationType.LOVER

def test_relation_type_enum():
    """测试关系类型枚举"""
    assert RelationType.STRANGER.value == "stranger"
    assert RelationType.FRIEND.value == "friend"
    assert RelationType.LOVER.value == "lover"
```

- [ ] **运行测试确认失败**

```bash
pytest tests/unit/domain/bible/value_objects/test_relationship_graph.py -v
```

Expected: FAIL

### Step 2: 实现 Relationship

- [ ] **创建 relationship.py**

Create: `domain/bible/value_objects/relationship.py`

```python
from dataclasses import dataclass
from enum import Enum

class RelationType(str, Enum):
    """关系类型"""
    STRANGER = "stranger"
    ACQUAINTANCE = "acquaintance"
    FRIEND = "friend"
    CLOSE_FRIEND = "close_friend"
    LOVER = "lover"
    ENEMY = "enemy"
    RIVAL = "rival"
    FAMILY = "family"

@dataclass(frozen=True)
class Relationship:
    """关系值对象"""
    relation_type: RelationType
    established_in_chapter: int
    description: str

    def __post_init__(self):
        if self.established_in_chapter < 1:
            raise ValueError("Chapter number must be >= 1")
        if not self.description or not self.description.strip():
            raise ValueError("Description cannot be empty")
```

### Step 3: 实现 RelationshipGraph

- [ ] **创建 relationship_graph.py**

Create: `domain/bible/value_objects/relationship_graph.py`

```python
from typing import Dict, List, Tuple, Optional
from domain.bible.value_objects.character_id import CharacterId
from domain.bible.value_objects.relationship import Relationship, RelationType

class RelationshipGraph:
    """关系图谱值对象 - 使用邻接表存储"""

    def __init__(self):
        # 邻接表：char1 -> char2 -> [关系历史]
        self._edges: Dict[CharacterId, Dict[CharacterId, List[Relationship]]] = {}

    def add_relationship(
        self,
        char1: CharacterId,
        char2: CharacterId,
        relation: Relationship
    ) -> None:
        """添加关系（保留历史）"""
        if char1 not in self._edges:
            self._edges[char1] = {}

        if char2 not in self._edges[char1]:
            self._edges[char1][char2] = []

        self._edges[char1][char2].append(relation)

    def get_current_relationship(
        self,
        char1: CharacterId,
        char2: CharacterId
    ) -> Optional[Relationship]:
        """获取当前关系（最新的）"""
        if char1 not in self._edges:
            return None

        if char2 not in self._edges[char1]:
            return None

        relationships = self._edges[char1][char2]
        return relationships[-1] if relationships else None

    def get_relationship_history(
        self,
        char1: CharacterId,
        char2: CharacterId
    ) -> List[Relationship]:
        """获取关系演变历史"""
        if char1 not in self._edges:
            return []

        return self._edges[char1].get(char2, []).copy()

    def get_all_relationships(
        self,
        char_id: CharacterId
    ) -> List[Tuple[CharacterId, Relationship]]:
        """获取某人物的所有当前关系"""
        if char_id not in self._edges:
            return []

        relationships = []
        for other_id, relations in self._edges[char_id].items():
            if relations:
                relationships.append((other_id, relations[-1]))

        return relationships
```

- [ ] **运行测试确认通过**

```bash
pytest tests/unit/domain/bible/value_objects/test_relationship_graph.py -v
```

Expected: PASS

### Step 4: 提交

- [ ] **提交代码**

```bash
git add domain/bible/value_objects/relationship.py
git add domain/bible/value_objects/relationship_graph.py
git add tests/unit/domain/bible/value_objects/test_relationship_graph.py
git commit -m "feat: add Relationship and RelationshipGraph value objects"
```

---

## Task 7: 仓储接口和实现

**Files:**
- Create: `domain/novel/repositories/plot_arc_repository.py`
- Create: `domain/novel/repositories/foreshadowing_repository.py`
- Create: `infrastructure/persistence/repositories/file_plot_arc_repository.py`
- Create: `infrastructure/persistence/repositories/file_foreshadowing_repository.py`
- Create: `tests/integration/infrastructure/persistence/repositories/test_file_plot_arc_repository.py`

### Step 1: 编写 PlotArcRepository 接口

- [ ] **创建仓储接口**

Create: `domain/novel/repositories/plot_arc_repository.py`

```python
from abc import ABC, abstractmethod
from typing import Optional
from domain.novel.entities.plot_arc import PlotArc
from domain.novel.value_objects.novel_id import NovelId

class PlotArcRepository(ABC):
    """PlotArc 仓储接口"""

    @abstractmethod
    def save(self, plot_arc: PlotArc) -> None:
        """保存剧情曲线"""
        pass

    @abstractmethod
    def get_by_novel_id(self, novel_id: NovelId) -> Optional[PlotArc]:
        """根据小说 ID 获取剧情曲线"""
        pass

    @abstractmethod
    def delete(self, novel_id: NovelId) -> None:
        """删除剧情曲线"""
        pass
```

### Step 2: 编写 ForeshadowingRepository 接口

- [ ] **创建仓储接口**

Create: `domain/novel/repositories/foreshadowing_repository.py`

```python
from abc import ABC, abstractmethod
from typing import Optional
from domain.novel.entities.foreshadowing_registry import ForeshadowingRegistry
from domain.novel.value_objects.novel_id import NovelId

class ForeshadowingRepository(ABC):
    """Foreshadowing 仓储接口"""

    @abstractmethod
    def save(self, registry: ForeshadowingRegistry) -> None:
        """保存伏笔注册表"""
        pass

    @abstractmethod
    def get_by_novel_id(self, novel_id: NovelId) -> Optional[ForeshadowingRegistry]:
        """根据小说 ID 获取伏笔注册表"""
        pass

    @abstractmethod
    def delete(self, novel_id: NovelId) -> None:
        """删除伏笔注册表"""
        pass
```

### Step 3: 实现文件仓储（简化版）

- [ ] **创建 FilePlotArcRepository**

Create: `infrastructure/persistence/repositories/file_plot_arc_repository.py`

```python
import json
from pathlib import Path
from typing import Optional
from domain.novel.entities.plot_arc import PlotArc
from domain.novel.value_objects.novel_id import NovelId
from domain.novel.repositories.plot_arc_repository import PlotArcRepository

class FilePlotArcRepository(PlotArcRepository):
    """基于文件的 PlotArc 仓储实现"""

    def __init__(self, data_root: Path):
        self.data_root = data_root
        self.plot_arcs_dir = data_root / "plot_arcs"
        self.plot_arcs_dir.mkdir(parents=True, exist_ok=True)

    def save(self, plot_arc: PlotArc) -> None:
        """保存剧情曲线到 JSON 文件"""
        file_path = self.plot_arcs_dir / f"{plot_arc.novel_id.value}.json"

        data = {
            "id": plot_arc.id,
            "novel_id": plot_arc.novel_id.value,
            "key_points": [
                {
                    "chapter_number": p.chapter_number,
                    "point_type": p.point_type.value,
                    "description": p.description,
                    "tension": p.tension.value
                }
                for p in plot_arc.key_points
            ]
        }

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def get_by_novel_id(self, novel_id: NovelId) -> Optional[PlotArc]:
        """从 JSON 文件加载剧情曲线"""
        file_path = self.plot_arcs_dir / f"{novel_id.value}.json"

        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        from domain.novel.value_objects.plot_point import PlotPoint, PlotPointType
        from domain.novel.value_objects.tension_level import TensionLevel

        plot_arc = PlotArc(id=data["id"], novel_id=NovelId(data["novel_id"]))

        for p_data in data["key_points"]:
            point = PlotPoint(
                chapter_number=p_data["chapter_number"],
                point_type=PlotPointType(p_data["point_type"]),
                description=p_data["description"],
                tension=TensionLevel(p_data["tension"])
            )
            plot_arc.add_plot_point(point)

        return plot_arc

    def delete(self, novel_id: NovelId) -> None:
        """删除剧情曲线文件"""
        file_path = self.plot_arcs_dir / f"{novel_id.value}.json"
        if file_path.exists():
            file_path.unlink()
```

### Step 4: 编写集成测试

- [ ] **创建集成测试**

Create: `tests/integration/infrastructure/persistence/repositories/test_file_plot_arc_repository.py`

```python
import pytest
from pathlib import Path
import tempfile
import shutil
from domain.novel.entities.plot_arc import PlotArc
from domain.novel.value_objects.novel_id import NovelId
from domain.novel.value_objects.plot_point import PlotPoint, PlotPointType
from domain.novel.value_objects.tension_level import TensionLevel
from infrastructure.persistence.repositories.file_plot_arc_repository import FilePlotArcRepository

@pytest.fixture
def temp_data_dir():
    """创建临时数据目录"""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir)

def test_save_and_load(temp_data_dir):
    """测试保存和加载"""
    repo = FilePlotArcRepository(temp_data_dir)

    # 创建剧情曲线
    arc = PlotArc(id="arc-1", novel_id=NovelId("novel-1"))
    arc.add_plot_point(PlotPoint(1, PlotPointType.OPENING, "开始", TensionLevel.LOW))
    arc.add_plot_point(PlotPoint(50, PlotPointType.CLIMAX, "高潮", TensionLevel.PEAK))

    # 保存
    repo.save(arc)

    # 加载
    loaded = repo.get_by_novel_id(NovelId("novel-1"))
    assert loaded is not None
    assert loaded.id == "arc-1"
    assert len(loaded.key_points) == 2

def test_get_nonexistent(temp_data_dir):
    """测试获取不存在的剧情曲线"""
    repo = FilePlotArcRepository(temp_data_dir)
    result = repo.get_by_novel_id(NovelId("nonexistent"))
    assert result is None
```

- [ ] **运行测试**

```bash
pytest tests/integration/infrastructure/persistence/repositories/test_file_plot_arc_repository.py -v
```

Expected: PASS

### Step 5: 提交

- [ ] **提交代码**

```bash
git add domain/novel/repositories/plot_arc_repository.py
git add domain/novel/repositories/foreshadowing_repository.py
git add infrastructure/persistence/repositories/file_plot_arc_repository.py
git add tests/integration/infrastructure/persistence/repositories/test_file_plot_arc_repository.py
git commit -m "feat: add repository interfaces and file implementations"
```

---

## 完成检查清单

- [ ] 所有值对象实现并测试通过
- [ ] 所有实体实现并测试通过
- [ ] 仓储接口定义
- [ ] 文件仓储实现并测试通过
- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 代码已提交到 git

---

## 预期结果

完成后，基础领域模型已就绪：
- ✅ PlotArc（剧情曲线）
- ✅ ForeshadowingRegistry（伏笔注册表）
- ✅ EventTimeline（事件时间线）
- ✅ RelationshipGraph（关系图谱）
- ✅ 所有仓储接口和实现
- ✅ 完整的测试覆盖

**下一步**: 可以开始子项目 2（向量检索基础设施）

