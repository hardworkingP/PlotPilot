# 子项目 3-8: 实现计划概要

> **说明**: 这些是简化版计划，包含主要任务列表。执行时可参考子项目 1-2 的详细模式。

---

## 子项目 3: 人物管理系统

**Goal:** 实现分层人物管理，支持上万人物

**Dependencies:** 子项目 2（向量检索）

**Estimated Time:** 2 周

### 主要任务

1. **CharacterImportance 枚举和 ActivityMetrics**
   - 定义 5 个重要性等级
   - 实现活跃度追踪数据结构

2. **CharacterRegistry 实体**
   - 分层存储（按重要性）
   - 快速查找索引
   - 活跃度追踪

3. **智能人物选择**
   - get_characters_for_context() 方法
   - 根据大纲提取相关人物
   - 通过关系图扩展相关人物

4. **分层上下文生成**
   - 主角：完整信息（~1000 tokens）
   - 主要配角：详细信息（~800 tokens）
   - 重要配角：中等信息（~150 tokens）
   - 次要角色：最简信息（~50 tokens）

5. **CharacterIndexer 集成**
   - 索引人物到向量库
   - 实现 search_by_description()
   - 实现 find_similar_characters()

6. **测试**
   - 单元测试
   - 大规模测试（1000+ 人物）
   - 性能测试

---

## 子项目 4: 故事线管理

**Goal:** 实现故事线和里程碑管理

**Dependencies:** 子项目 1（基础领域模型）

**Estimated Time:** 1-2 周

### 主要任务

1. **StorylineType 和 StorylineStatus 枚举**
   - 9 种故事线类型
   - 3 种状态（ACTIVE/COMPLETED/ABANDONED）

2. **StorylineMilestone 值对象**
   - 里程碑属性（order, title, description）
   - 目标章节范围
   - 前置条件和触发器

3. **Storyline 实体**
   - 里程碑列表
   - 当前进度追踪
   - 预计章节范围

4. **StorylineManager 服务**
   - create_storyline()
   - get_pending_milestones()
   - complete_milestone()
   - get_storyline_context()

5. **仓储实现**
   - StorylineRepository 接口
   - FileStorylineRepository 实现

6. **测试**
   - 单元测试
   - 集成测试
   - 多故事线并行测试

---

## 子项目 5: 关系引擎

**Goal:** 实现图结构的人物关系管理

**Dependencies:** 无

**Estimated Time:** 1-2 周

### 主要任务

1. **RelationshipEngine 核心**
   - 图结构实现（邻接表）
   - add_relationship()
   - get_current_relationship()
   - get_relationship_history()

2. **图算法**
   - find_path()（BFS 查找关系路径）
   - get_common_connections()
   - get_relationship_cluster()

3. **关系强度计算**
   - calculate_relationship_strength()
   - 基础强度 + 互动加成 + 共同联系人加成

4. **关系趋势分析**
   - analyze_relationship_trend()
   - IMPROVING/DETERIORATING/STABLE/VOLATILE

5. **关系发展建议**
   - suggest_relationship_development()
   - 合理的关系转换路径

6. **测试**
   - 单元测试
   - 复杂关系网络测试
   - 性能测试（万级人物关系）

---

## 子项目 6: 一致性检查系统

**Goal:** 实现多维度一致性检查

**Dependencies:** 子项目 1, 2, 3, 4, 5

**Estimated Time:** 2 周

### 主要任务

1. **StateExtractor 服务**
   - 使用 LLM 提取章节信息
   - 结构化 JSON 输出
   - 提取：新人物、行为、关系变化、伏笔、事件

2. **ConsistencyChecker 服务**
   - check_character_consistency()（LLM 判断）
   - check_relationship_consistency()
   - check_event_logic()
   - check_foreshadowing()

3. **ConsistencyReport 数据结构**
   - IssueType 枚举
   - Severity 枚举
   - 问题列表和建议

4. **StateUpdater 服务**
   - 更新 Bible
   - 更新 ForeshadowingRegistry
   - 更新 EventTimeline
   - 更新 PlotArc
   - 更新 StorylineManager

5. **集成测试**
   - 端到端一致性检查
   - 多维度验证
   - 性能测试

---

## 子项目 7: 上下文构建器

**Goal:** 实现智能上下文组装，控制在 35K tokens

**Dependencies:** 子项目 2, 3, 4, 5

**Estimated Time:** 1-2 周

### 主要任务

1. **AppearanceScheduler 服务**
   - schedule_appearances()
   - 出场决策逻辑（5 个因素）
   - 场景人物分配

2. **ContextBuilder 核心**
   - build_context()
   - Layer 1: 核心上下文（~5K）
   - Layer 2: 智能检索（~20K）
   - Layer 3: 近期上下文（~10K）

3. **Token 预算控制**
   - estimate_tokens()
   - 动态调整各层 token 分配
   - 确保总计 < 35K

4. **上下文格式化**
   - format_protagonist_info()
   - format_major_characters_info()
   - format_supporting_characters_info()

5. **性能优化**
   - 缓存热数据
   - 异步并行检索
   - 批量处理

6. **测试**
   - Token 预算测试
   - 大规模上下文测试
   - 性能测试

---

## 子项目 8: 工作流集成

**Goal:** 集成所有组件到 AutoNovelGenerationWorkflow

**Dependencies:** 子项目 1-7

**Estimated Time:** 1-2 周

### 主要任务

1. **AutoNovelGenerationWorkflow 增强**
   - 集成 AppearanceScheduler
   - 集成 ContextBuilder
   - 集成 StateExtractor
   - 集成 ConsistencyChecker
   - 集成 StateUpdater

2. **完整生成流程**
   - Planning Phase
   - Pre-Generation（上下文构建）
   - Generation
   - Post-Generation（一致性检查）
   - Review Phase

3. **API 端点**
   - POST /api/v1/novels/{id}/generate-chapter
   - GET /api/v1/novels/{id}/consistency-report
   - GET /api/v1/novels/{id}/storylines
   - POST /api/v1/novels/{id}/plot-arc

4. **前端集成**
   - 更新 Workbench.vue
   - 添加一致性报告显示
   - 添加故事线管理界面

5. **端到端测试**
   - 完整生成流程测试
   - 100 章小说测试
   - 上万人物测试

6. **性能优化**
   - 缓存优化
   - 数据库查询优化
   - 向量检索优化

7. **文档更新**
   - API 文档
   - 架构文档
   - 用户手册

---

## 总体完成检查清单

- [ ] 所有 8 个子项目完成
- [ ] 所有单元测试通过
- [ ] 所有集成测试通过
- [ ] 端到端测试通过
- [ ] 性能指标达标
- [ ] 文档完整
- [ ] 代码已提交

---

## 预期最终结果

完成后，AI 一致性架构全面就绪：
- ✅ 支持 100+ 章节
- ✅ 支持 10,000+ 人物
- ✅ 上下文控制在 35K tokens
- ✅ 多维度一致性保证
- ✅ 完整的故事线管理
- ✅ 智能关系追踪
- ✅ 伏笔自动管理

