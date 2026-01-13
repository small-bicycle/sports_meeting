# Implementation Plan: 报名表导出功能

## Overview

实现运动会报名表的批量导出功能，包括后端 API 扩展和前端班级选择弹窗。采用增量开发方式，先完成核心导出逻辑，再添加前端界面。

## Tasks

- [x] 1. 扩展后端 Schema 和 API 路由
  - [x] 1.1 在 `backend/app/schemas/__init__.py` 添加导出相关的请求/响应模型
    - 添加 `ExportableClassInfo` 模型
    - 添加 `ClassRegistrationExportRequest` 模型
    - _Requirements: 1.2, 2.1_

  - [x] 1.2 在 `backend/app/api/` 添加导出 API 路由
    - 添加 `GET /api/export/exportable-classes` 端点
    - 添加 `POST /api/export/registration-forms` 端点
    - _Requirements: 1.1, 2.1, 2.4_

- [x] 2. 实现 ExportService 核心方法
  - [x] 2.1 实现 `get_exportable_classes()` 方法
    - 查询有报名记录的班级
    - 返回班级信息和报名人数
    - _Requirements: 1.1, 1.2, 1.3_

  - [x] 2.2 编写属性测试：班级列表过滤正确性

    - **Property 1: 班级列表过滤正确性**
    - **Validates: Requirements 1.1, 1.2, 1.3**

  - [x] 2.3 实现 `_group_registrations_by_event_group()` 方法
    - 按项目和组别分组报名记录
    - 处理无组别情况
    - _Requirements: 3.1, 3.2, 3.3, 3.4_

  - [x] 2.4 编写属性测试：组别分组正确性

    - **Property 3: 组别分组正确性**
    - **Validates: Requirements 3.1, 3.2, 3.3, 3.4**

- [x] 3. 实现 Excel 生成逻辑
  - [x] 3.1 实现 `_build_class_sheet()` 方法
    - 构建单个班级的工作表
    - 添加组别标题行和数据行
    - 设置样式（加粗、居中、合并单元格）
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 5.2, 5.3, 5.4_

  - [ ]* 3.2 编写属性测试：报名表内容格式正确性
    - **Property 4: 报名表内容格式正确性**
    - **Validates: Requirements 4.1, 4.2, 4.3, 4.4**

  - [x] 3.3 实现 `export_class_registration_forms()` 方法
    - 批量生成多班级工作表
    - 工作表命名格式：年级名-班级名
    - _Requirements: 2.1, 2.2, 2.3_

  - [ ]* 3.4 编写属性测试：工作表结构正确性
    - **Property 2: 工作表结构正确性**
    - **Validates: Requirements 2.1, 2.2, 2.3**

  - [ ]* 3.5 编写属性测试：Excel文件格式有效性
    - **Property 5: Excel文件格式有效性**
    - **Validates: Requirements 5.1**

- [x] 4. Checkpoint - 后端功能验证
  - 确保所有后端测试通过
  - 使用 API 工具测试导出功能
  - 如有问题请询问用户

- [ ] 5. 实现前端班级选择弹窗
  - [ ] 5.1 创建 `RegistrationExportDialog.vue` 组件
    - 弹窗结构和样式
    - 班级列表按年级分组显示
    - _Requirements: 6.1, 6.2_

  - [ ] 5.2 实现班级选择逻辑
    - 复选框多选功能
    - 全选/反选/按年级选择
    - _Requirements: 6.3_

  - [ ] 5.3 实现导出 API 调用
    - 调用后端 API 下载文件
    - 加载状态显示
    - _Requirements: 6.4, 6.5_

- [ ] 6. 集成到数据导出页面
  - [ ] 6.1 在数据导出页面添加"报名表导出"按钮
    - 触发弹窗显示
    - _Requirements: 6.1_

- [ ] 7. Final Checkpoint - 完整功能验证
  - 确保所有测试通过
  - 验证前后端集成
  - 如有问题请询问用户

## Notes

- 任务标记 `*` 为可选测试任务，可跳过以加快 MVP 开发
- 每个任务引用具体需求以便追溯
- 检查点确保增量验证
- 属性测试验证通用正确性属性
- 单元测试验证具体示例和边界情况
