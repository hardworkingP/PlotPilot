# AI 一致性架构设计文档

**日期**: 2026-04-01
**项目**: aitext - AI 小说创作系统
**设计目标**: 确保长篇小说（100+ 章，上万人物）的人物一致性、关系管理、伏笔追踪、剧情质量

---

## 目录

1. [核心挑战](#核心挑战)
2. [整体架构](#整体架构)
3. [领域模型设计](#领域模型设计)
4. [大规模上下文管理](#大规模上下文管理)
5. [人物管理系统](#人物管理系统)
6. [关系引擎](#关系引擎)
7. [一致性检查](#一致性检查)
8. [实现计划](#实现计划)

---

## 核心挑战

### 用户需求

在生成长篇小说（100 章，30 万字+）时，需要保证：

1. **人物不记错**: 第 50 章提到的人物设定，与第 3 章一致
2. **人物关系**: 关系演变合理，有迹可循（陌生人 → 朋友 → 恋人）
3. **背景事件**: 历史事件不矛盾，时间线清晰
4. **伏笔管理**: 埋下的伏笔能够适时回收
5. **人设立得住**: 人物行为符合性格设定
6. **剧情丰满跌宕**: 节奏控制，张力曲线合理

### 技术挑战

1. **上下文规模**: 100 章 × 3000 字 = 30 万字，加上元数据 = 50-100 万字
2. **LLM 限制**: Claude 200K tokens ≈ 40 万字，且越长越贵越慢
3. **人物规模**: 上万人物（主角、配角、龙套、群众）
4. **关系复杂度**: 人物关系网络呈指数增长
5. **检索效率**: 如何快速找到相关人物和历史信息

---

## 整体架构

### 架构选择：增强型 Workflow

**方案对比**：

| 方案 | 优点 | 缺点 | 选择 |
|------|------|------|------|
| A. 增强型 Workflow | 实现简单，流程清晰，易调试 | 顺序执行，某些检查滞后 | ✅ 采用 |
| B. 事件驱动 Reactive | 实时响应，解耦性强 | 架构复杂，调试困难，过度设计 | ❌ |
| C. 混合架构 | 平衡复杂度和灵活性 | 状态对象可能庞大 | ❌ |

**选择理由**：
- 小说创作本质是顺序流程（规划 → 写作 → 审阅），不是高并发事件流
- 核心需求是"一致性保证"，不是"实时响应"
- 方案 A 在满足需求的前提下，复杂度最低，可维护性最高

### 架构层次

```
┌─────────────────────────────────────────────────────────────┐
│                    Application Layer                         │
│  AutoNovelGenerationWorkflow (orchestrator)                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Consistency Layer (新增)                   │
│  ├─ ContextBuilder: 智能上下文组装                           │
│  ├─ ConsistencyChecker: 一致性验证                          │
│  ├─ StateExtractor: 自动信息提取                            │
│  └─ StateUpdater: 状态更新                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    Domain Layer (增强)                       │
│  Novel (聚合根)                                              │
│  ├─ Bible: 人物、世界观、关系图谱                            │
│  ├─ PlotArc: 剧情曲线、关键节点                              │
│  ├─ ForeshadowingRegistry: 伏笔注册表                       │
│  ├─ EventTimeline: 事件时间线                               │
│  └─ Chapter: 章节内容                                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│           Character Management System (新增)                 │
│  ├─ CharacterRegistry: 人物注册表 (分层管理)                 │
│  ├─ StorylineManager: 故事线管理器                           │
│  ├─ AppearanceScheduler: 出场调度器                          │
│  ├─ CharacterIndexer: 人物索引器 (向量检索)                  │
│  └─ RelationshipEngine: 关系引擎 (图数据库)                  │
└─────────────────────────────────────────────────────────────┘
```

### 完整数据流

生成第 N 章的完整流程：

```
1. Planning Phase (规划阶段)
   ↓
   - 创建 PlotArc (剧情曲线)
   - 设计关键转折点
   - 规划关系发展路线
   - 预设伏笔埋点
   - 为主要人物创建 Storyline

2. Pre-Generation (生成前)
   ↓
   AppearanceScheduler.schedule_appearances(chapter_N)
   ├─ 分析章节大纲
   ├─ 确定必须出场的人物
   ├─ 检查故事线里程碑
   └─ 安排场景人物配置
   ↓
   ContextBuilder.build_context(chapter_N)
   ├─ Layer 1: 核心上下文 (~5K tokens)
   │   ├─ 小说基本信息
   │   ├─ 主角完整信息
   │   └─ 当前剧情位置
   ├─ Layer 2: 相关上下文 (~20K tokens)
   │   ├─ 出场人物详细信息 (分层)
   │   ├─ 关系图谱摘要
   │   ├─ 未回收伏笔
   │   ├─ 活跃故事线
   │   └─ 相关历史章节 (向量检索)
   └─ Layer 3: 近期上下文 (~10K tokens)
       └─ 前 3-5 章内容/摘要

3. Generation (生成)
   ↓
   LLMService.generate(prompt + context)
   - AI 基于完整上下文生成章节

4. Post-Generation (生成后)
   ↓
   StateExtractor.extract(chapter_content)
   ├─ 提取新出现的人物
   ├─ 识别关系变化
   ├─ 检测新埋下的伏笔
   ├─ 识别已回收的伏笔
   └─ 提取关键事件
   ↓
   ConsistencyChecker.validate(extracted_info, novel_state)
   ├─ 人物行为是否符合人设 (LLM 判断)
   ├─ 关系变化是否合理
   ├─ 是否与历史矛盾
   └─ 伏笔是否被遗忘
   ↓
   StateUpdater.update(novel, extracted_info)
   ├─ 更新 Bible (新人物、关系变化)
   ├─ 更新 ForeshadowingRegistry
   ├─ 更新 EventTimeline
   ├─ 更新 PlotArc 进度
   ├─ 更新 StorylineManager
   ├─ 生成章节摘要
   └─ 索引到向量库

5. Review Phase (可选)
   ↓
   如果 ConsistencyChecker 发现问题
   - 提供修改建议
   - 或自动重新生成
```

---

## 领域模型设计

### 1. PlotArc (剧情曲线)

**职责**: 管理整体节奏和关键剧情节点

**核心属性**:
```python
class PlotArc(BaseEntity):
    novel_id: NovelId
    key_points: List[PlotPoint]        # 关键剧情点
    tension_curve: List[TensionLevel]  # 张力曲线
```

**关键方法**:
- `add_plot_point()`: 添加关键剧情点（开端/转折/高潮/结局）
- `get_expected_tension(chapter_number)`: 获取该章节应有的张力水平
- `get_next_plot_point(current_chapter)`: 获取下一个关键剧情点

**PlotPointType**:
- OPENING: 开端
- RISING_ACTION: 上升
- TURNING_POINT: 转折
- CLIMAX: 高潮
- FALLING_ACTION: 下降
- RESOLUTION: 结局

**TensionLevel**: LOW (1) → MEDIUM (2) → HIGH (3) → PEAK (4)

### 2. ForeshadowingRegistry (伏笔注册表)

**职责**: 跟踪所有伏笔的状态

**核心属性**:
```python
class ForeshadowingRegistry(BaseEntity):
    novel_id: NovelId
    foreshadowings: List[Foreshadowing]
```

**关键方法**:
- `register(foreshadowing)`: 注册新伏笔
- `mark_resolved(id, chapter)`: 标记伏笔已回收
- `get_unresolved()`: 获取所有未回收的伏笔
- `get_ready_to_resolve(chapter)`: 获取应该在当前章节回收的伏笔

**Foreshadowing 值对象**:
```python
@dataclass
class Foreshadowing:
    planted_in_chapter: int              # 埋在第几章
    description: str                     # 伏笔描述
    suggested_resolve_chapter: Optional[int]  # 建议回收章节
    status: ForeshadowingStatus          # PLANTED/RESOLVED/ABANDONED
    importance: ImportanceLevel          # 重要性
```

### 3. Bible (增强版)

**新增功能**:
- `RelationshipGraph`: 关系图谱（管理人物关系及其演变）
- `EventTimeline`: 事件时间线（记录所有关键事件）

**关键方法**:
```python
def update_relationship(
    char1_id: CharacterId,
    char2_id: CharacterId,
    new_relation: RelationType,
    chapter_number: int
)

def get_relationship_history(
    char1_id: CharacterId,
    char2_id: CharacterId
) -> List[Relationship]
```

**RelationType**:
- STRANGER → ACQUAINTANCE → FRIEND → CLOSE_FRIEND → LOVER
- STRANGER → ENEMY / RIVAL
- FAMILY (特殊关系)

### 4. EventTimeline (事件时间线)

**职责**: 记录所有关键事件，避免时间线矛盾

**核心方法**:
- `add_event(event)`: 添加事件
- `get_events_before(chapter)`: 获取某章节之前的所有事件
- `get_events_involving(character_id)`: 获取涉及某人物的所有事件

**EventType**:
- CHARACTER_INTRODUCTION: 人物登场
- RELATIONSHIP_CHANGE: 关系变化
- CONFLICT: 冲突
- REVELATION: 揭秘
- DECISION: 重大决定

---


## 大规模上下文管理

### 核心问题

一本 100 章的小说：
- 章节内容: 100 × 3000 字 = 30 万字
- Bible 元数据: 上万人物 × 平均 200 字 = 200 万字+
- 关系网络: 人物² 级别的关系数据
- 事件时间线: 数千个事件记录

**总计**: 远超 LLM 上下文窗口（Claude 200K tokens ≈ 40 万字）

### 解决方案：分层上下文 + 智能检索

#### 上下文分层策略

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 1: 核心上下文 (必须包含, ~5K tokens)                  │
│  - 小说基本信息 (书名、作者、类型、主题)                      │
│  - 主要人物列表 (名字、核心人设)                             │
│  - 当前剧情位置 (第几章、剧情曲线位置)                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 2: 相关上下文 (智能检索, ~20K tokens)                 │
│  - 相关人物详细信息 (本章涉及的人物)                         │
│  - 相关历史章节摘要 (与本章相关的前置章节)                   │
│  - 未回收伏笔 (需要考虑的伏笔)                               │
│  - 当前关系状态 (本章涉及人物的关系)                         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: 近期上下文 (最近 3-5 章, ~10K tokens)              │
│  - 前 3 章完整内容 (保持连贯性)                              │
│  - 或前 5 章摘要 (如果太长)                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  Layer 4: 归档上下文 (不直接传给 LLM)                        │
│  - 所有历史章节完整内容                                      │
│  - 通过向量检索按需提取                                      │
└─────────────────────────────────────────────────────────────┘
```

#### Token 预算分配

| 内容类型 | 存储方式 | 检索方式 | Token 预算 |
|---------|---------|---------|-----------|
| 核心信息 | 内存 | 直接加载 | ~5K |
| 主角信息 | 数据库 | 直接加载 | ~3K |
| 主要配角 | 数据库 | 按需加载 | ~8K |
| 配角信息 | 数据库 | 智能检索 | ~4K |
| 关系网络 | 图数据库 | 图查询 | ~3K |
| 故事线 | 数据库 | 按活跃度 | ~5K |
| 历史章节 | 向量库 | 语义检索 | ~5K |
| 近期章节 | 数据库 | 按章节号 | ~2K |
| **总计** | - | - | **~35K** |

### 关键技术组件

#### 1. ContextBuilder (智能上下文构建器)

**核心方法**:
```python
async def build_context(
    novel_id: NovelId,
    target_chapter_number: int,
    plot_outline: str
) -> GenerationContext
```

**工作流程**:
1. Layer 1: 核心上下文 (~5K tokens)
2. Layer 2: 智能检索相关上下文 (~20K tokens)
3. Layer 3: 近期上下文 (~10K tokens)

#### 2. VectorStore (向量检索)

**用途**: 语义检索相关历史章节

**索引**: 每章生成后立即索引

**检索**: 根据本章大纲找到最相关的 5 章

#### 3. ChapterSummarizer (章节摘要器)

**用途**: 将 3000 字压缩到 300 字

**摘要内容**: 主要事件、人物变化、重要对话、伏笔


---

## 人物管理系统

### 1. CharacterRegistry (分层人物注册表)

#### CharacterImportance (人物重要性分层)

```python
PROTAGONIST = 5      # 主角 (1-3 人)
MAJOR = 4           # 主要配角 (5-10 人)
SUPPORTING = 3      # 重要配角 (20-50 人)
MINOR = 2           # 次要角色 (100-500 人)
EXTRA = 1           # 龙套/群众 (1000+ 人)
```

#### 活跃度追踪

**最大出场间隔**:
- 主角: 3 章
- 主要配角: 10 章
- 重要配角: 30 章
- 次要角色: 100 章
- 龙套: 无限制

#### 分层上下文生成

**主角** (~1000 tokens/人):
- 完整描述、性格、背景、当前状态
- 目标与冲突
- 最近活动（前 5 章）
- 所有关系
- 故事线进度

**主要配角** (~800 tokens/人):
- 完整描述、性格、当前状态
- 最近活动（前 3 章）
- 关键关系
- 故事线进度

**重要配角** (~150 tokens/人):
- 摘要描述
- 核心特征（前 3 个）
- 当前状态
- 关键关系（前 3 个）

**次要角色/龙套** (~50 tokens/人):
- 一句话描述
- 角色定位
- 最后出场章节

### 2. StorylineManager (故事线管理器)

#### StorylineType (故事线类型)

- MAIN_QUEST: 主线任务
- CHARACTER_GROWTH: 人物成长
- RELATIONSHIP: 关系发展
- REVENGE: 复仇线
- REDEMPTION: 救赎线
- MYSTERY: 悬疑线
- ROMANCE: 感情线
- POWER_STRUGGLE: 权力斗争
- SIDE_QUEST: 支线任务

#### StorylineMilestone (里程碑)

```python
class StorylineMilestone:
    order: int
    title: str
    description: str
    target_chapter_range: Tuple[int, int]  # (最早, 最晚)
    prerequisites: List[str]               # 前置里程碑
    triggers: List[str]                    # 触发条件
    completed: bool
```

**示例**:
```
故事线: "张三的复仇之路"
类型: REVENGE
里程碑:
  1. 发现仇人线索 (第 10-15 章)
  2. 收集证据 (第 20-30 章, 前置: 1)
  3. 对质 (第 40-50 章, 前置: 2)
  4. 复仇成功 (第 60-70 章, 前置: 3)
```

#### 关键方法

- `get_pending_milestones(chapter, lookahead=5)`: 获取未来 N 章内的里程碑
- `get_storyline_context(character_id)`: 生成故事线上下文描述
- `complete_milestone(storyline_id, milestone_order, chapter)`: 标记完成

### 3. AppearanceScheduler (出场调度器)

#### 出场决策因素

1. **明确提到的人物** (必须出场) - 从大纲提取
2. **故事线要求** (必须出场) - 待完成里程碑涉及的人物
3. **主角** (必须出场) - 除非特殊章节
4. **长期未出场的重要人物** (应该出场) - 接近最大间隔 80%
5. **场景需求** (可选出场) - 配角和龙套丰富场景

#### AppearanceSchedule (出场安排)

```python
@dataclass
class AppearanceSchedule:
    chapter_number: int
    scene_assignments: List[SceneAssignment]  # 每个场景的人物配置
    must_appear: Set[CharacterId]             # 必须出场的人物
    storyline_milestones: List[...]           # 待完成里程碑
```


---

## 关系引擎

### RelationshipEngine (关系引擎 - 图数据库)

#### 核心设计

使用图结构管理复杂人物关系：
- **节点**: 人物
- **边**: 关系（有向，保留历史）
- **权重**: 关系强度

#### RelationType (关系类型)

**关系演变路径**:
```
STRANGER → ACQUAINTANCE → FRIEND → CLOSE_FRIEND → LOVER
STRANGER → ENEMY / RIVAL
FAMILY (特殊关系)
```

#### 关键方法

**基础操作**:
- `add_relationship()`: 添加关系（保留历史）
- `get_current_relationship()`: 获取当前关系
- `get_relationship_history()`: 获取关系演变历史

**图算法**:
- `find_path(start, end, max_depth=3)`: 查找关系路径（BFS）
- `get_common_connections()`: 获取共同联系人
- `get_relationship_cluster()`: 获取关系圈

**关系分析**:
- `calculate_relationship_strength()`: 计算关系强度（0-1）
- `suggest_relationship_development()`: 建议关系发展方向

#### 关系强度计算

```
strength = base_strength + interaction_bonus + common_bonus

base_strength: STRANGER(0.1) → LOVER(0.9) → FAMILY(0.95)
interaction_bonus: min(关系演变次数 × 0.05, 0.2)
common_bonus: min(共同联系人数 × 0.02, 0.1)
```

### CharacterIndexer (人物索引器 - 向量检索)

#### 核心功能

使用向量检索快速找到相关人物

#### 关键方法

- `search_by_description()`: 根据描述搜索人物
- `find_similar_characters()`: 查找相似人物
- `search_by_role()`: 根据角色需求搜索

**应用场景**:
1. 智能人物选择
2. 相似人物查找（避免重复）
3. 角色补充

---

## 一致性检查

### ConsistencyChecker (一致性检查器)

#### 检查维度

1. **人物一致性**: 行为是否符合人设（LLM 判断）
2. **关系合理性**: 关系变化是否过于突兀
3. **事件逻辑**: 是否与历史矛盾
4. **伏笔处理**: 是否有长期未回收的重要伏笔

#### ConsistencyReport

```python
@dataclass
class ConsistencyReport:
    is_consistent: bool
    issues: List[ConsistencyIssue]
    severity: Severity  # LOW/MEDIUM/HIGH/CRITICAL
    suggestions: List[str]
```

#### IssueType

- CHARACTER_INCONSISTENCY: 人物行为不符合人设
- RELATIONSHIP_ABRUPT: 关系变化过于突然
- LOGIC_ERROR: 逻辑错误
- FORESHADOWING_FORGOTTEN: 伏笔被遗忘
- TIMELINE_CONFLICT: 时间线冲突

### StateExtractor (状态提取器)

使用 LLM 从章节内容中提取：
- 新出现的人物
- 人物行为
- 关系变化
- 新埋下的伏笔
- 回收的伏笔
- 关键事件
- 剧情发展

### StateUpdater (状态更新器)

根据提取的信息更新：
1. Bible（新人物、关系变化）
2. ForeshadowingRegistry
3. EventTimeline
4. PlotArc
5. StorylineManager
6. 章节摘要并索引

---

## 实现计划

### Phase 1: 基础设施 (Week 1-2)

- [ ] 集成向量数据库（Qdrant/Milvus/Chroma）
- [ ] 实现 VectorStore 接口
- [ ] 实现 EmbeddingService
- [ ] PlotArc、ForeshadowingRegistry、EventTimeline 领域模型
- [ ] 相关仓储实现

### Phase 2: 人物管理系统 (Week 3-4)

- [ ] CharacterRegistry（分层存储、活跃度追踪）
- [ ] StorylineManager（故事线管理、里程碑）
- [ ] AppearanceScheduler（出场调度）
- [ ] RelationshipEngine（图结构、关系分析）
- [ ] CharacterIndexer（向量索引）

### Phase 3: 上下文管理 (Week 5)

- [ ] ChapterSummarizer（LLM 摘要生成）
- [ ] ContextBuilder（分层上下文构建）
- [ ] Token 预算控制

### Phase 4: 一致性检查 (Week 6)

- [ ] StateExtractor（结构化信息提取）
- [ ] ConsistencyChecker（多维度检查）
- [ ] StateUpdater（状态更新）

### Phase 5: 工作流集成 (Week 7)

- [ ] AutoNovelGenerationWorkflow 增强
- [ ] API 端点实现

### Phase 6: 测试与优化 (Week 8)

- [ ] 单元测试（覆盖率 > 80%）
- [ ] 集成测试（大规模人物、长篇小说）
- [ ] 性能优化

---

## 技术栈

### 新增依赖

| 组件 | 技术选型 | 用途 |
|------|---------|------|
| 向量数据库 | Qdrant / Milvus | 章节和人物向量检索 |
| Embedding | OpenAI text-embedding-3-small | 生成向量嵌入 |
| 图数据库 | 内存图结构 | 人物关系管理 |

---

## 关键设计决策

### 1. 为什么选择增强型 Workflow？

小说创作本质是顺序流程，不是高并发事件流。Workflow 更易理解、调试、维护。

### 2. 为什么使用向量检索？

语义检索比关键词匹配更准确，支持模糊查询，性能更好。

### 3. 为什么人物分层管理？

上万人物无法全部加载，不同重要性需要不同详细程度，精确控制 Token 预算。

### 4. 为什么使用图结构管理关系？

关系网络天然是图结构，支持复杂查询（路径查找、共同联系人）。

### 5. 为什么生成后才检查一致性？

生成前只能做规划，无法预知 AI 会生成什么。生成后检查可以发现实际问题。

---

## 预期效果

### 一致性保证

✅ **人物不记错**: ContextBuilder 智能检索 + ConsistencyChecker 验证
✅ **人物关系**: RelationshipEngine 跟踪演变 + 合理性检查
✅ **背景事件**: EventTimeline 记录 + 向量检索相关事件
✅ **伏笔管理**: ForeshadowingRegistry 跟踪 + AI 自动考虑回收
✅ **人设立得住**: ConsistencyChecker 验证行为一致性
✅ **剧情丰满跌宕**: PlotArc 管理张力曲线 + StorylineManager 推进故事线

### 性能指标

- **上下文大小**: 控制在 35K tokens 以内
- **人物管理**: 支持 10,000+ 人物
- **章节规模**: 支持 100+ 章节
- **检索速度**: < 100ms（向量检索）
- **生成速度**: 30-60s/章（取决于 LLM API）

---

## 风险与挑战

### 1. LLM 提取准确性

**风险**: StateExtractor 可能提取错误或遗漏信息

**缓解**: 结构化提示、低温度、人工审核关键信息

### 2. 向量检索相关性

**风险**: 检索到的历史章节可能不够相关

**缓解**: 优化 Embedding 模型、调整检索参数、结合关键词过滤

### 3. 性能瓶颈

**风险**: 大规模人物和章节可能导致性能问题

**缓解**: 分层加载、缓存热数据、异步并行、必要时升级数据库

### 4. 复杂度管理

**风险**: 系统复杂度增加，维护成本上升

**缓解**: 清晰模块划分、完善测试、详细文档、渐进式实现

---

## 总结

本设计通过**增强型 Workflow + 分层人物管理 + 智能上下文检索 + 一致性检查**的架构，解决了长篇小说 AI 创作中的核心挑战：

1. **上下文管理**: 分层 + 向量检索，将 100 万字压缩到 35K tokens
2. **人物管理**: 分层注册表 + 故事线管理 + 出场调度，支持上万人物
3. **关系管理**: 图结构 + 关系强度计算 + 趋势分析，确保关系合理演变
4. **一致性保证**: 自动提取 + 多维度检查 + 状态更新，确保人物、事件、伏笔一致

该架构在满足需求的前提下，保持了适中的复杂度，易于实现和维护。

