-- Primero, respaldar datos existentes si los hay
CREATE TABLE projects_backup AS SELECT * FROM projects;

-- Eliminar la tabla actual
DROP TABLE IF EXISTS projects CASCADE;

-- Crear la nueva tabla con la estructura correcta
CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    
    -- Información del participante (Sección 1)
    participant_name VARCHAR(255) NOT NULL,
    participant_phone VARCHAR(20) NOT NULL,
    participant_country VARCHAR(100) NOT NULL,
    participant_city VARCHAR(100) NOT NULL,
    participant_occupation VARCHAR(255) NOT NULL,
    participant_institution VARCHAR(255),
    participant_area VARCHAR(255) NOT NULL,
    participant_portfolio VARCHAR(500),
    
    -- Información del proyecto (Sección 2)
    project_category VARCHAR(100) NOT NULL,
    project_title VARCHAR(255) NOT NULL,
    project_description TEXT NOT NULL,
    project_format VARCHAR(255) NOT NULL,
    project_files TEXT,
    
    -- Autorizaciones y términos (Sección 3)
    previous_participation VARCHAR(10),
    media_authorization VARCHAR(10) NOT NULL,
    terms BOOLEAN NOT NULL DEFAULT FALSE,
    
    -- Metadatos
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Relación con usuarios
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Crear índices para mejorar rendimiento
CREATE INDEX idx_projects_user_id ON projects(user_id);
CREATE INDEX idx_projects_category ON projects(project_category);
CREATE INDEX idx_projects_created ON projects(created_at);