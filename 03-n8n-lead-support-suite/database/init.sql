CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE TABLE leads (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE,
    company TEXT,
    score INT DEFAULT 0,
    status TEXT DEFAULT 'new'
);