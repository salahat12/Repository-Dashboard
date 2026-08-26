CREATE TABLE repository (
    repo_id SERIAL PRIMARY KEY,
    github_id BIGINT NOT NULL,
    name VARCHAR(255) NOT NULL,
    owner VARCHAR(255) NOT NULL,
    description TEXT,
    url VARCHAR(500)
);

CREATE TABLE contributor (
    contributor_id SERIAL PRIMARY KEY,
    repo_id INTEGER NOT NULL,
    github_id BIGINT NOT NULL,
    username VARCHAR(255) NOT NULL,
    permission VARCHAR(100),

    CONSTRAINT fk_contributor_repository
        FOREIGN KEY (repo_id)
        REFERENCES repository(repo_id)
        ON DELETE CASCADE
);

CREATE TABLE branch (
    name VARCHAR(255) PRIMARY KEY,
    repo_id INTEGER NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,

    CONSTRAINT fk_branch_repository
        FOREIGN KEY (repo_id)
        REFERENCES repository(repo_id)
        ON DELETE CASCADE
);

CREATE TABLE pull_request (
    pr_id SERIAL PRIMARY KEY,
    branch_name VARCHAR(255) NOT NULL,
    number INTEGER NOT NULL,
    title VARCHAR(255) NOT NULL,
    state VARCHAR(50) NOT NULL,
    author VARCHAR(255),

    CONSTRAINT fk_pull_request_branch
        FOREIGN KEY (branch_name)
        REFERENCES branch(name)
        ON DELETE CASCADE
);

CREATE TABLE commits (
    commit_sha VARCHAR(255) PRIMARY KEY,
    pr_id INTEGER NOT NULL,
    message TEXT,
    author VARCHAR(255),

    CONSTRAINT fk_commit_pull_request
        FOREIGN KEY (pr_id)
        REFERENCES pull_request(pr_id)
        ON DELETE CASCADE
);
