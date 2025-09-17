# IPTV Schedule API

一个用于自动下载和处理IPTV节目调度数据的异步API服务。

## 项目架构

```mermaid
graph TB
    subgraph "Client Layer"
        A[HTTP Client]
        B[Web Browser]
    end

    subgraph "API Layer"
        C[FastAPI Server<br/>Port: 8000]
        D[Logger Middleware]
    end

    subgraph "Business Logic Layer"
        E[Download Service<br/>script/iptv.py]
        F[Processing Service<br/>utils/processing.py]
        G[Schema Validation<br/>schema/schema.py]
    end

    subgraph "Infrastructure Layer"
        H[Playwright Browser<br/>Web Scraping]
        I[Pandas<br/>Data Processing]
        J[File System<br/>CSV Storage]
    end

    subgraph "Data Storage"
        K[data/iptv/original/<br/>Raw CSV Files]
        L[data/iptv/processed/<br/>Processed CSV Files]
        M[logs/<br/>Application Logs]
    end

    A --> C
    B --> C
    C --> D
    C --> G
    C --> E
    C --> F
    E --> H
    F --> I
    E --> K
    F --> L
    D --> M

    style C fill:#e1f5fe
    style E fill:#f3e5f5
    style F fill:#f3e5f5
    style K fill:#fff3e0
    style L fill:#fff3e0
```

## 系统架构说明

### 1. API层 (FastAPI)
- **端点**: `/download-iptv` - 下载并处理IPTV调度数据
- **端点**: `/schedules` - 列出所有调度文件
- **端点**: `/schedule/{filename}` - 获取特定调度文件内容
- **日志**: 完整的请求/响应日志记录

### 2. 业务逻辑层
- **下载服务**: 使用Playwright自动化浏览器操作
- **处理服务**: 异步数据清理和过滤
- **数据验证**: Pydantic模型验证输入输出

### 3. 数据流程
