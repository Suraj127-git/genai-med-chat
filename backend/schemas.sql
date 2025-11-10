-- backend/schemas.sql
CREATE DATABASE IF NOT EXISTS genai_med CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE genai_med;

CREATE TABLE IF NOT EXISTS users (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(255) UNIQUE,
  email VARCHAR(255) UNIQUE,
  password_hash VARCHAR(255),
  role VARCHAR(50),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS conversations (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  user_id BIGINT,
  title VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS messages (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  conv_id BIGINT,
  sender ENUM('user','bot'),
  content TEXT,
  metadata JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS docs (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  source VARCHAR(255),
  filepath VARCHAR(1024),
  uploaded_by BIGINT,
  metadata JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Graph tables for reasoning/provenance
CREATE TABLE IF NOT EXISTS graph_nodes (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  conv_id BIGINT,
  node_type VARCHAR(100),      -- e.g., 'user', 'retrieval', 'generation'
  content TEXT,
  metadata JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS graph_edges (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  conv_id BIGINT,
  from_node BIGINT,
  to_node BIGINT,
  relation VARCHAR(100),
  metadata JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
