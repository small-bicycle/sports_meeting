# Requirements Document

## Introduction

本功能实现运动会报名表的批量导出功能。用户在项目配置完成且有班级数据后，可以按班级多选导出报名表。由于不同项目有不同的组别（如男子组、女子组、不同年级组），报名表需要按组别合理组织数据。

## Glossary

- **Export_Service**: 数据导出服务，负责生成Excel格式的报名表
- **Registration**: 报名记录，关联学生、项目和组别
- **Event**: 运动项目，包含名称、类型、单位等信息
- **EventGroup**: 项目组别，定义性别限制和适用年级
- **Class**: 班级，属于某个年级
- **Grade**: 年级
- **Student**: 学生，属于某个班级

## Requirements

### Requirement 1: 获取可导出班级列表

**User Story:** As a 管理员, I want to 查看所有可导出的班级列表, so that 我可以选择需要导出报名表的班级

#### Acceptance Criteria

1. WHEN 用户请求班级列表 THEN THE Export_Service SHALL 返回所有有报名记录的班级
2. WHEN 返回班级列表 THEN THE Export_Service SHALL 包含班级ID、班级名称、年级名称和报名人数
3. WHEN 某班级没有任何报名记录 THEN THE Export_Service SHALL 不在列表中显示该班级

### Requirement 2: 多选班级导出报名表

**User Story:** As a 管理员, I want to 多选班级并一键下载报名表, so that 我可以批量获取多个班级的报名数据

#### Acceptance Criteria

1. WHEN 用户选择多个班级ID并请求导出 THEN THE Export_Service SHALL 生成包含所选班级报名数据的Excel文件
2. WHEN 生成Excel文件 THEN THE Export_Service SHALL 为每个班级创建独立的工作表(Sheet)
3. WHEN 工作表命名 THEN THE Export_Service SHALL 使用"年级名-班级名"格式命名
4. IF 用户未选择任何班级 THEN THE Export_Service SHALL 返回错误提示

### Requirement 3: 按组别组织报名数据

**User Story:** As a 管理员, I want to 报名表按项目组别分组显示, so that 我可以清晰地看到不同组别的报名情况

#### Acceptance Criteria

1. WHEN 生成班级报名表 THEN THE Export_Service SHALL 按项目组别对报名记录进行分组
2. WHEN 显示组别信息 THEN THE Export_Service SHALL 包含组别名称、性别限制和适用年级
3. WHEN 某组别没有该班级的报名记录 THEN THE Export_Service SHALL 不显示该组别
4. WHEN 项目没有设置组别 THEN THE Export_Service SHALL 将报名记录归入"默认组"

### Requirement 4: 报名表内容格式

**User Story:** As a 管理员, I want to 报名表包含完整的学生和项目信息, so that 我可以用于现场核对和存档

#### Acceptance Criteria

1. WHEN 生成报名表 THEN THE Export_Service SHALL 包含以下字段：序号、学号、姓名、性别、项目名称、组别名称
2. WHEN 显示性别 THEN THE Export_Service SHALL 将"M"显示为"男"，"F"显示为"女"
3. WHEN 排序报名记录 THEN THE Export_Service SHALL 先按项目名称排序，再按组别名称排序，最后按学号排序
4. WHEN 生成表头 THEN THE Export_Service SHALL 在每个组别区域显示组别标题行

### Requirement 5: 导出文件格式

**User Story:** As a 管理员, I want to 导出标准的Excel文件, so that 我可以方便地打印和编辑

#### Acceptance Criteria

1. THE Export_Service SHALL 生成xlsx格式的Excel文件
2. WHEN 设置表头样式 THEN THE Export_Service SHALL 使用加粗字体和居中对齐
3. WHEN 设置列宽 THEN THE Export_Service SHALL 根据内容自动调整列宽
4. WHEN 设置组别标题 THEN THE Export_Service SHALL 使用合并单元格和背景色区分

### Requirement 6: 前端班级选择界面

**User Story:** As a 管理员, I want to 在弹窗中多选班级, so that 我可以灵活选择需要导出的班级

#### Acceptance Criteria

1. WHEN 用户点击"报名表导出"按钮 THEN THE System SHALL 弹出班级选择对话框
2. WHEN 显示班级列表 THEN THE System SHALL 按年级分组显示所有可导出班级
3. THE System SHALL 提供全选、反选和按年级选择功能
4. WHEN 用户确认选择 THEN THE System SHALL 调用后端API下载Excel文件
5. WHILE 正在生成文件 THEN THE System SHALL 显示加载状态

