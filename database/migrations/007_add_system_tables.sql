-- 添加系统相关表
-- 创建时间: 2025-01-04

-- 系统日志表
CREATE TABLE IF NOT EXISTS system_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '日志时间',
    level VARCHAR(20) NOT NULL COMMENT '日志级别(INFO/WARNING/ERROR/DEBUG)',
    message TEXT NOT NULL COMMENT '日志消息',
    module VARCHAR(50) NOT NULL COMMENT '模块名称',
    user_id INT NULL COMMENT '关联用户ID',
    request_id VARCHAR(100) NULL COMMENT '请求ID',
    ip_address VARCHAR(45) NULL COMMENT 'IP地址',
    user_agent VARCHAR(500) NULL COMMENT '用户代理',
    extra_data JSON NULL COMMENT '额外数据',
    INDEX idx_timestamp (timestamp),
    INDEX idx_level (level),
    INDEX idx_module (module),
    INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统日志';

-- 系统配置表
CREATE TABLE IF NOT EXISTS system_configs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    `key` VARCHAR(100) NOT NULL UNIQUE COMMENT '配置键',
    value TEXT NOT NULL COMMENT '配置值',
    description VARCHAR(500) NULL COMMENT '配置描述',
    category VARCHAR(50) NOT NULL COMMENT '配置分类',
    data_type VARCHAR(20) DEFAULT 'string' COMMENT '数据类型(string/int/float/bool/json)',
    is_public BOOLEAN DEFAULT FALSE COMMENT '是否为公开配置',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    updated_by INT NULL COMMENT '更新者ID',
    INDEX idx_key (`key`),
    INDEX idx_category (category),
    INDEX idx_updated_at (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统配置';

-- 系统备份记录表
CREATE TABLE IF NOT EXISTS system_backups (
    id INT AUTO_INCREMENT PRIMARY KEY,
    backup_id VARCHAR(100) NOT NULL UNIQUE COMMENT '备份ID',
    backup_type VARCHAR(20) NOT NULL COMMENT '备份类型(full/incremental/schema)',
    file_path VARCHAR(500) NOT NULL COMMENT '备份文件路径',
    file_size BIGINT NOT NULL DEFAULT 0 COMMENT '文件大小(字节)',
    status VARCHAR(20) DEFAULT 'running' COMMENT '备份状态(running/completed/failed)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    completed_at DATETIME NULL COMMENT '完成时间',
    created_by INT NOT NULL COMMENT '创建者ID',
    error_message TEXT NULL COMMENT '错误信息',
    metadata JSON NULL COMMENT '备份元数据',
    INDEX idx_backup_id (backup_id),
    INDEX idx_status (status),
    INDEX idx_created_at (created_at),
    INDEX idx_created_by (created_by)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统备份记录';

-- 性能指标表
CREATE TABLE IF NOT EXISTS performance_metrics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '记录时间',
    cpu_usage FLOAT NOT NULL COMMENT 'CPU使用率(%)',
    memory_usage FLOAT NOT NULL COMMENT '内存使用率(%)',
    disk_usage FLOAT NOT NULL COMMENT '磁盘使用率(%)',
    network_io JSON NULL COMMENT '网络IO统计',
    active_connections INT DEFAULT 0 COMMENT '活跃连接数',
    response_time FLOAT NULL COMMENT '平均响应时间(秒)',
    request_count INT DEFAULT 0 COMMENT '请求数量',
    error_count INT DEFAULT 0 COMMENT '错误数量',
    INDEX idx_timestamp (timestamp)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统性能指标';

-- 维护模式记录表
CREATE TABLE IF NOT EXISTS maintenance_mode (
    id INT AUTO_INCREMENT PRIMARY KEY,
    enabled BOOLEAN DEFAULT FALSE COMMENT '是否启用维护模式',
    message TEXT NULL COMMENT '维护提示信息',
    start_time DATETIME NULL COMMENT '维护开始时间',
    end_time DATETIME NULL COMMENT '维护结束时间',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    updated_by INT NOT NULL COMMENT '操作者ID',
    INDEX idx_enabled (enabled),
    INDEX idx_updated_at (updated_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='维护模式记录';

-- 插入默认系统配置
INSERT IGNORE INTO system_configs (`key`, value, description, category, data_type, updated_by) VALUES
('app.name', '私人金融分析师', '应用名称', 'app', 'string', 1),
('app.version', '1.0.0', '应用版本', 'app', 'string', 1),
('security.jwt_expire_minutes', '30', 'JWT令牌过期时间（分钟）', 'security', 'int', 1),
('api.rate_limit', '1000', 'API速率限制（每小时）', 'api', 'int', 1),
('data.cache_expire_seconds', '300', '数据缓存过期时间（秒）', 'data', 'int', 1),
('system.maintenance_enabled', 'false', '系统维护模式', 'system', 'bool', 1),
('logging.level', 'INFO', '日志级别', 'logging', 'string', 1),
('backup.auto_enabled', 'true', '自动备份是否启用', 'backup', 'bool', 1),
('backup.retention_days', '30', '备份保留天数', 'backup', 'int', 1);

-- 插入一条初始的系统日志
INSERT INTO system_logs (level, message, module, user_id) VALUES
('INFO', '系统表初始化完成', 'system', 1);

-- 记录当前的系统性能基线
INSERT INTO performance_metrics (cpu_usage, memory_usage, disk_usage, active_connections, request_count, error_count) 
VALUES (0.0, 0.0, 0.0, 0, 0, 0);