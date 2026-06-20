package com.daledou;

/**
 * 开发者全局配置管理类
 * 提示：App 名称和文件夹名已提升至 app/build.gradle 中统一管理
 * 修改 build.gradle 后，此处会自动同步。
 */
public class AppConfig {

    // 1. 应用基础信息 (自动同步 build.gradle 中的设置)
    public static final String APP_NAME = BuildConfig.GLOBAL_APP_NAME; 
    
    // 2. 外部存储配置 (自动同步 build.gradle 中的设置)
    public static final String CONF_DIR_NAME = BuildConfig.GLOBAL_CONF_DIR;
    
    // 3. UI 风格配置 (十六进制颜色码)
    public static final int COLOR_PRIMARY = 0xFF6366F1;   
    public static final int COLOR_ACCENT = 0xFFF59E0B;    
    public static final int COLOR_BG_LIGHT = 0xFFF8FAFC;  
    
    // 4. 其他常量
    public static final String DEFAULT_CONFIG_FILE = "default.yaml";
    public static final String COOKIE_BACKUP_FILE = "cookies_backup.txt";
    public static final String TASK_REG_FILE = "task_register.json";
    public static final int MAX_LOG_LENGTH = 10000;
}
