
CREATE TABLE Repository (
    repo_id SERIAL PRIMARY KEY,
    github_id BIGINT UNIQUE NOT NULL,
    repo_name VARCHAR(255) NOT NULL,
    owner VARCHAR(255) NOT NULL,
    description TEXT,
    url TEXT,
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL
);


CREATE TABLE Contributor (
    contributor_id SERIAL PRIMARY KEY,
    repo_id INT NOT NULL,
    github_id BIGINT NOT NULL,
    username VARCHAR(255) NOT NULL,
    permission VARCHAR(50),
    CONSTRAINT fk_contributor_repository 
        FOREIGN KEY (repo_id) 
        REFERENCES Repository(repo_id)
);


CREATE TABLE Branch (
    branch_id SERIAL PRIMARY KEY,
    repo_id INT NOT NULL,
    branch_name VARCHAR(255) NOT NULL,
    is_default BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_branch_repository 
        FOREIGN KEY (repo_id) 
        REFERENCES Repository(repo_id)
);


CREATE TABLE Pull_Request (
    pr_id SERIAL PRIMARY KEY,
    branch_id INT NOT NULL,
    pr_number INT NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    state VARCHAR(50),
    author VARCHAR(255),
    created_at TIMESTAMPTZ NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT fk_pr_branch 
        FOREIGN KEY (branch_id) 
        REFERENCES Branch(branch_id)
);


CREATE TABLE Commit (
    commit_id SERIAL PRIMARY KEY,
    pr_id INT NOT NULL,
    commit_sha VARCHAR(40) UNIQUE NOT NULL,
    message TEXT,
    author VARCHAR(255),
    committed_at TIMESTAMPTZ NOT NULL,
    CONSTRAINT fk_commit_pr 
        FOREIGN KEY (pr_id) 
        REFERENCES Pull_Request(pr_id)
);
