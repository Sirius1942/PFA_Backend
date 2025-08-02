-- 私人金融分析师数据库初始化脚本
-- 创建时间: 2024
-- 描述: 初始化数据库表结构和基础数据

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- 用户表
-- ----------------------------
CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '用户ID',
  `username` varchar(50) NOT NULL COMMENT '用户名',
  `email` varchar(100) NOT NULL COMMENT '邮箱',
  `phone` varchar(20) DEFAULT NULL COMMENT '手机号',
  `hashed_password` varchar(255) NOT NULL COMMENT '密码哈希',
  `full_name` varchar(100) DEFAULT NULL COMMENT '真实姓名',
  `avatar` varchar(255) DEFAULT NULL COMMENT '头像URL',
  `is_active` tinyint(1) DEFAULT 1 COMMENT '是否激活',
  `is_verified` tinyint(1) DEFAULT 0 COMMENT '是否验证',
  `is_superuser` tinyint(1) DEFAULT 0 COMMENT '是否超级用户',
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  `last_login` timestamp NULL DEFAULT NULL COMMENT '最后登录时间',
  `login_count` int(11) DEFAULT 0 COMMENT '登录次数',
  `bio` text COMMENT '个人简介',
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `phone` (`phone`),
  KEY `idx_username` (`username`),
  KEY `idx_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- ----------------------------
-- 角色表
-- ----------------------------
CREATE TABLE IF NOT EXISTS `roles` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '角色ID',
  `name` varchar(50) NOT NULL COMMENT '角色名称',
  `display_name` varchar(100) NOT NULL COMMENT '显示名称',
  `description` text COMMENT '角色描述',
  `is_active` tinyint(1) DEFAULT 1 COMMENT '是否激活',
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `idx_name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色表';

-- ----------------------------
-- 权限表
-- ----------------------------
CREATE TABLE IF NOT EXISTS `permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '权限ID',
  `code` varchar(100) NOT NULL COMMENT '权限代码',
  `name` varchar(100) NOT NULL COMMENT '权限名称',
  `description` text COMMENT '权限描述',
  `module` varchar(50) NOT NULL COMMENT '所属模块',
  `is_active` tinyint(1) DEFAULT 1 COMMENT '是否激活',
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `idx_code` (`code`),
  KEY `idx_module` (`module`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='权限表';

-- ----------------------------
-- 用户角色关联表
-- ----------------------------
CREATE TABLE IF NOT EXISTS `user_roles` (
  `user_id` int(11) NOT NULL COMMENT '用户ID',
  `role_id` int(11) NOT NULL COMMENT '角色ID',
  PRIMARY KEY (`user_id`, `role_id`),
  KEY `fk_user_roles_role` (`role_id`),
  CONSTRAINT `fk_user_roles_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_user_roles_role` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户角色关联表';

-- ----------------------------
-- 角色权限关联表
-- ----------------------------
CREATE TABLE IF NOT EXISTS `role_permissions` (
  `role_id` int(11) NOT NULL COMMENT '角色ID',
  `permission_id` int(11) NOT NULL COMMENT '权限ID',
  PRIMARY KEY (`role_id`, `permission_id`),
  KEY `fk_role_permissions_permission` (`permission_id`),
  CONSTRAINT `fk_role_permissions_role` FOREIGN KEY (`role_id`) REFERENCES `roles` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_role_permissions_permission` FOREIGN KEY (`permission_id`) REFERENCES `permissions` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='角色权限关联表';

-- ----------------------------
-- 股票基本信息表
-- ----------------------------
CREATE TABLE IF NOT EXISTS `stock_info` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '股票ID',
  `code` varchar(20) NOT NULL COMMENT '股票代码',
  `name` varchar(100) NOT NULL COMMENT '股票名称',
  `market` varchar(10) NOT NULL COMMENT '市场类型(SH/SZ)',
  `industry` varchar(100) DEFAULT NULL COMMENT '所属行业',
  `sector` varchar(100) DEFAULT NULL COMMENT '所属板块',
  `listing_date` date DEFAULT NULL COMMENT '上市日期',
  `total_shares` decimal(20,2) DEFAULT NULL COMMENT '总股本',
  `float_shares` decimal(20,2) DEFAULT NULL COMMENT '流通股本',
  `market_cap` decimal(20,2) DEFAULT NULL COMMENT '总市值',
  `float_market_cap` decimal(20,2) DEFAULT NULL COMMENT '流通市值',
  `is_active` tinyint(1) DEFAULT 1 COMMENT '是否有效',
  `is_st` tinyint(1) DEFAULT 0 COMMENT '是否ST股票',
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `idx_code` (`code`),
  KEY `idx_market` (`market`),
  KEY `idx_industry` (`industry`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票基本信息表';

-- ----------------------------
-- K线数据表
-- ----------------------------
CREATE TABLE IF NOT EXISTS `kline_data` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT 'K线ID',
  `code` varchar(20) NOT NULL COMMENT '股票代码',
  `date` date NOT NULL COMMENT '交易日期',
  `open_price` decimal(10,3) NOT NULL COMMENT '开盘价',
  `high_price` decimal(10,3) NOT NULL COMMENT '最高价',
  `low_price` decimal(10,3) NOT NULL COMMENT '最低价',
  `close_price` decimal(10,3) NOT NULL COMMENT '收盘价',
  `volume` bigint(20) NOT NULL COMMENT '成交量',
  `amount` decimal(20,2) NOT NULL COMMENT '成交额',
  `change_amount` decimal(10,3) DEFAULT NULL COMMENT '涨跌额',
  `change_percent` decimal(8,4) DEFAULT NULL COMMENT '涨跌幅',
  `turnover_rate` decimal(8,4) DEFAULT NULL COMMENT '换手率',
  `adj_factor` decimal(10,6) DEFAULT 1.000000 COMMENT '复权因子',
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_code_date` (`code`, `date`),
  KEY `idx_code_date` (`code`, `date`),
  KEY `idx_date_code` (`date`, `code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='K线数据表';

-- ----------------------------
-- 实时行情表
-- ----------------------------
CREATE TABLE IF NOT EXISTS `realtime_quotes` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '行情ID',
  `code` varchar(20) NOT NULL COMMENT '股票代码',
  `name` varchar(100) NOT NULL COMMENT '股票名称',
  `current_price` decimal(10,3) NOT NULL COMMENT '当前价格',
  `open_price` decimal(10,3) NOT NULL COMMENT '开盘价',
  `high_price` decimal(10,3) NOT NULL COMMENT '最高价',
  `low_price` decimal(10,3) NOT NULL COMMENT '最低价',
  `pre_close` decimal(10,3) NOT NULL COMMENT '昨收价',
  `change_amount` decimal(10,3) NOT NULL COMMENT '涨跌额',
  `change_percent` decimal(8,4) NOT NULL COMMENT '涨跌幅',
  `volume` bigint(20) NOT NULL COMMENT '成交量',
  `amount` decimal(20,2) NOT NULL COMMENT '成交额',
  `turnover_rate` decimal(8,4) DEFAULT NULL COMMENT '换手率',
  `bid1_price` decimal(10,3) DEFAULT NULL COMMENT '买一价',
  `bid1_volume` bigint(20) DEFAULT NULL COMMENT '买一量',
  `ask1_price` decimal(10,3) DEFAULT NULL COMMENT '卖一价',
  `ask1_volume` bigint(20) DEFAULT NULL COMMENT '卖一量',
  `market_cap` decimal(20,2) DEFAULT NULL COMMENT '总市值',
  `float_market_cap` decimal(20,2) DEFAULT NULL COMMENT '流通市值',
  `quote_time` timestamp NOT NULL COMMENT '行情时间',
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  KEY `idx_code` (`code`),
  KEY `idx_quote_time` (`quote_time`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='实时行情表';

-- ----------------------------
-- 用户自选股表
-- ----------------------------
CREATE TABLE IF NOT EXISTS `user_watchlist` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '自选股ID',
  `user_id` int(11) NOT NULL COMMENT '用户ID',
  `stock_code` varchar(20) NOT NULL COMMENT '股票代码',
  `alert_price_high` decimal(10,3) DEFAULT NULL COMMENT '价格上限提醒',
  `alert_price_low` decimal(10,3) DEFAULT NULL COMMENT '价格下限提醒',
  `alert_change_percent` decimal(8,4) DEFAULT NULL COMMENT '涨跌幅提醒',
  `notes` text COMMENT '备注',
  `tags` varchar(255) DEFAULT NULL COMMENT '标签',
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
  `updated_at` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_stock` (`user_id`, `stock_code`),
  KEY `idx_user_id` (`user_id`),
  KEY `idx_stock_code` (`stock_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户自选股表';

-- ----------------------------
-- 插入基础角色数据
-- ----------------------------
INSERT INTO `roles` (`name`, `display_name`, `description`) VALUES
('admin', '系统管理员', '拥有系统所有权限的管理员角色'),
('user', '普通用户', '普通用户角色，可以查看股票数据和使用AI助手'),
('vip', 'VIP用户', 'VIP用户角色，拥有更多高级功能权限')
ON DUPLICATE KEY UPDATE `display_name` = VALUES(`display_name`), `description` = VALUES(`description`);

-- ----------------------------
-- 插入基础权限数据
-- ----------------------------
INSERT INTO `permissions` (`code`, `name`, `description`, `module`) VALUES
-- 用户管理权限
('user.view', '查看用户', '查看用户信息', 'user'),
('user.create', '创建用户', '创建新用户', 'user'),
('user.update', '更新用户', '更新用户信息', 'user'),
('user.delete', '删除用户', '删除用户', 'user'),

-- 股票数据权限
('stock.view', '查看股票', '查看股票数据', 'stock'),
('stock.realtime', '实时行情', '查看实时股票行情', 'stock'),
('stock.history', '历史数据', '查看历史股票数据', 'stock'),
('stock.watchlist', '自选股', '管理自选股列表', 'stock'),

-- AI助手权限
('agent.chat', 'AI对话', '与AI助手对话', 'agent'),
('agent.analysis', 'AI分析', '使用AI进行股票分析', 'agent'),

-- 系统管理权限
('admin.user', '用户管理', '管理系统用户', 'admin'),
('admin.role', '角色管理', '管理系统角色', 'admin'),
('admin.permission', '权限管理', '管理系统权限', 'admin'),
('admin.system', '系统设置', '管理系统设置', 'admin')
ON DUPLICATE KEY UPDATE `name` = VALUES(`name`), `description` = VALUES(`description`);

-- ----------------------------
-- 分配角色权限
-- ----------------------------
-- 管理员拥有所有权限
INSERT INTO `role_permissions` (`role_id`, `permission_id`)
SELECT r.id, p.id
FROM `roles` r, `permissions` p
WHERE r.name = 'admin'
ON DUPLICATE KEY UPDATE `role_id` = VALUES(`role_id`);

-- 普通用户权限
INSERT INTO `role_permissions` (`role_id`, `permission_id`)
SELECT r.id, p.id
FROM `roles` r, `permissions` p
WHERE r.name = 'user' AND p.code IN (
  'stock.view', 'stock.realtime', 'stock.history', 'stock.watchlist',
  'agent.chat', 'agent.analysis'
)
ON DUPLICATE KEY UPDATE `role_id` = VALUES(`role_id`);

-- VIP用户权限（包含普通用户所有权限）
INSERT INTO `role_permissions` (`role_id`, `permission_id`)
SELECT r.id, p.id
FROM `roles` r, `permissions` p
WHERE r.name = 'vip' AND p.code IN (
  'stock.view', 'stock.realtime', 'stock.history', 'stock.watchlist',
  'agent.chat', 'agent.analysis', 'user.view'
)
ON DUPLICATE KEY UPDATE `role_id` = VALUES(`role_id`);

-- ----------------------------
-- 创建默认管理员用户
-- ----------------------------
-- 密码: admin123 (请在生产环境中修改)
INSERT INTO `users` (`username`, `email`, `hashed_password`, `full_name`, `is_active`, `is_verified`, `is_superuser`) VALUES
('admin', 'admin@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewdBPj6hsxq5/Qe2', '系统管理员', 1, 1, 1)
ON DUPLICATE KEY UPDATE `email` = VALUES(`email`);

-- 分配管理员角色
INSERT INTO `user_roles` (`user_id`, `role_id`)
SELECT u.id, r.id
FROM `users` u, `roles` r
WHERE u.username = 'admin' AND r.name = 'admin'
ON DUPLICATE KEY UPDATE `user_id` = VALUES(`user_id`);

SET FOREIGN_KEY_CHECKS = 1;

-- 完成初始化
SELECT 'Database initialization completed successfully!' as message;