# Implementation Plans Overview

本目录包含 aitext 项目的所有实现计划。

## 实施顺序

### 阶段 0: 前后端对接完成（优先）

**计划文件**: `2026-04-01-frontend-backend-integration.md`

**目标**: 完成 Chapter 和 Cast 功能的后端 API 实现，更新前端组件

**任务列表**:
1. Chapter API 端点实现
2. 前端 Chapter API 客户端
3. 更新 Chapter.vue
4. 增强 Bible API
5. 前端 Bible API 客户端
6. 更新 Cast.vue
7. 更新 Workbench.vue
8. 端到端测试
9. 清理旧代码

**预计时间**: 1-2 天

---

### 阶段 1: AI 一致性架构（8 个子项目）

#### 子项目 1: 基础领域模型扩展

**计划文件**: `2026-04-01-subproject-1-domain-models.md`

**目标**: 实现 PlotArc、ForeshadowingRegistry、EventTimeline 等基础领域模型

**依赖**: 无

**预计时间**: 1-2 周

**任务列表**:
1. PlotArc 实体和值对象
2. ForeshadowingRegistry 实体
3. EventTimeline 值对象
4. RelationshipGraph 值对象
5. 仓储接口和实现
6. 单元测试
7. 集成测试

---

#### 子项目 2: 向量检索基础设施

**计划文件**: `2026-04-01-subproject-2-vector-search.md`

**目标**: 集成向量数据库，实现章节和人物的语义检索

**依赖**: 无

**预计时间**: 1-2 周

**任务列表**:
1. 选择并集成向量数据库（Qdrant/Milvus/Chroma）
2. 实现 VectorStore 接口
3. 实现 EmbeddingService
4. 实现 ChapterSummarizer
5. 章节索引和检索
6. 单元测试
7. 性能测试

---

#### 子项目 3: 人物管理系统

**计划文件**: `2026-04-01-subproject-3-character-management.md`

**目标**: 实现分层人物管理，支持上万人物

**依赖**: 子项目 2（向量检索）

**预计时间**: 2 周

**任务列表**:
1. CharacterRegistry（分层存储）
2. ActivityMetrics（活跃度追踪）
3. CharacterIndexer（向量检索）
4. 智能人物选择
5. 分层上下文生成
6. 单元测试
7. 大规模测试（1000+ 人物）

---

#### 子项目 4: 故事线管理

**计划文件**: `2026-04-01-subproject-4-storyline-management.md`

**目标**: 实现故事线和里程碑管理

**依赖**: 子项目 1（基础领域模型）

**预计时间**: 1-2 周

**任务列表**:
1. Storyline 实体
2. StorylineMilestone 值对象
3. StorylineManager 服务
4. 里程碑追踪和推进
5. 故事线上下文生成
6. 单元测试
7. 集成测试

---

#### 子项目 5: 关系引擎

**计划文件**: `2026-04-01-subproject-5-relationship-engine.md`

**目标**: 实现图结构的人物关系管理

**依赖**: 无

**预计时间**: 1-2 周

**任务列表**:
1. RelationshipEngine（图结构）
2. 关系历史管理
3. 图算法（路径查找、共同联系人）
4. 关系强度计算
5. 关系趋势分析
6. 单元测试
7. 性能测试

---

#### 子项目 6: 一致性检查系统

**计划文件**: `2026-04-01-subproject-6-consistency-checker.md`

**目标**: 实现多维度一致性检查

**依赖**: 子项目 1, 2, 3, 4, 5

**预计时间**: 2 周

**任务列表**:
1. StateExtractor（信息提取）
2. ConsistencyChecker（一致性验证）
3. StateUpdater（状态更新）
4. 人物一致性检查
5. 关系合理性检查
6. 伏笔处理检查
7. 单元测试
8. 集成测试

---

#### 子项目 7: 上下文构建器

**计划文件**: `2026-04-01-subproject-7-context-builder.md`

**目标**: 实现智能上下文组装，控制在 35K tokens

**依赖**: 子项目 2, 3, 4, 5

**预计时间**: 1-2 周

**任务列表**:
1. ContextBuilder（分层上下文）
2. AppearanceScheduler（出场调度）
3. Token 预算控制
4. Layer 1: 核心上下文
5. Layer 2: 智能检索
6. Layer 3: 近期上下文
7. 单元测试
8. 性能测试

---

#### 子项目 8: 工作流集成

**计划文件**: `2026-04-01-subproject-8-workflow-integration.md`

**目标**: 集成所有组件到 AutoNovelGenerationWorkflow

**依赖**: 子项目 1-7

**预计时间**: 1-2 周

**任务列表**:
1. AutoNovelGenerationWorkflow 增强
2. API 端点实现
3. 前端集成
4. 端到端测试
5. 性能优化
6. 文档更新

---

## 总体时间线

- **阶段 0**: 1-2 天（前后端对接）
- **子项目 1-2**: 2-4 周（可并行）
- **子项目 3-5**: 4-6 周（部分并行）
- **子项目 6-7**: 3-4 周（顺序）
- **子项目 8**: 1-2 周（集成）

**总计**: 约 8-10 周

---

## 当前状态

- [x] 设计文档完成
- [ ] 阶段 0: 前后端对接（✅ 计划完成，待执行）
- [ ] 子项目 1: 基础领域模型（✅ 计划完成，待执行）
- [ ] 子项目 2: 向量检索（✅ 计划完成，待执行）
- [ ] 子项目 3: 人物管理（✅ 概要完成，待执行）
- [ ] 子项目 4: 故事线管理（✅ 概要完成，待执行）
- [ ] 子项目 5: 关系引擎（✅ 概要完成，待执行）
- [ ] 子项目 6: 一致性检查（✅ 概要完成，待执行）
- [ ] 子项目 7: 上下文构建器（✅ 概要完成，待执行）
- [ ] 子项目 8: 工作流集成（✅ 概要完成，待执行）

**所有计划文档已完成！** 🎉

**计划文件**:
- 阶段 0: `2026-04-01-frontend-backend-integration.md`（9 个详细任务）
- 子项目 1: `2026-04-01-subproject-1-domain-models.md`（7 个详细任务）
- 子项目 2: `2026-04-01-subproject-2-vector-search.md`（7 个详细任务）
- 子项目 3-8: `2026-04-01-subprojects-3-8-overview.md`（36 个概要任务）

**总计**: 59 个任务

---

## 执行建议

1. **先完成阶段 0**（前后端对接），确保现有功能正常
2. **并行开始子项目 1 和 2**（基础模型 + 向量检索）
3. **然后依次实现子项目 3-8**
4. **每个子项目完成后进行独立测试和验证**
5. **使用 subagent-driven-development 执行每个计划**

