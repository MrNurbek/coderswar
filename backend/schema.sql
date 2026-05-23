-- ============================================================
-- Coders War Platform — PostgreSQL Reference Schema
-- Django migrations bilan avtomatik yaratiladi.
-- Bu fayl ma'lumotnoma sifatida saqlanadi.
-- ============================================================

-- ── users ────────────────────────────────────────────────────

CREATE TABLE users_user (
    id           SERIAL PRIMARY KEY,
    username     VARCHAR(150) UNIQUE NOT NULL,
    email        VARCHAR(254) UNIQUE NOT NULL,
    first_name   VARCHAR(150) DEFAULT '',
    last_name    VARCHAR(150) DEFAULT '',
    password     VARCHAR(128) NOT NULL,
    role         VARCHAR(20)  NOT NULL DEFAULT 'student',
    phone        VARCHAR(20)  DEFAULT '',
    bio          TEXT         DEFAULT '',
    avatar       VARCHAR(100),
    is_verified  BOOLEAN      NOT NULL DEFAULT FALSE,
    is_active    BOOLEAN      NOT NULL DEFAULT TRUE,
    is_staff     BOOLEAN      NOT NULL DEFAULT FALSE,
    is_superuser BOOLEAN      NOT NULL DEFAULT FALSE,
    date_joined  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE users_otpcode (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    code       VARCHAR(6)   NOT NULL,
    is_used    BOOLEAN      NOT NULL DEFAULT FALSE,
    expires_at TIMESTAMPTZ  NOT NULL,
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE users_group (
    id         SERIAL PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    code       VARCHAR(20)  UNIQUE NOT NULL,
    teacher_id INTEGER REFERENCES users_user(id) ON DELETE SET NULL,
    year       SMALLINT NOT NULL,
    faculty    VARCHAR(100) DEFAULT '',
    created_at TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE users_groupmembership (
    id         SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    group_id   INTEGER NOT NULL REFERENCES users_group(id) ON DELETE CASCADE,
    joined_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (student_id, group_id)
);

CREATE TABLE users_studentprofile (
    id             SERIAL PRIMARY KEY,
    user_id        INTEGER NOT NULL UNIQUE REFERENCES users_user(id) ON DELETE CASCADE,
    character      VARCHAR(20)    NOT NULL DEFAULT 'warrior',
    level          VARCHAR(20)    NOT NULL DEFAULT 'recruit',
    rating_score   INTEGER        NOT NULL DEFAULT 0,
    academic_score NUMERIC(5,2)   NOT NULL DEFAULT 0,
    current_streak INTEGER        NOT NULL DEFAULT 0,
    max_streak     INTEGER        NOT NULL DEFAULT 0,
    last_active    DATE,
    updated_at     TIMESTAMPTZ    NOT NULL DEFAULT NOW()
);

CREATE TABLE users_teacherprofile (
    id         SERIAL PRIMARY KEY,
    user_id    INTEGER NOT NULL UNIQUE REFERENCES users_user(id) ON DELETE CASCADE,
    department VARCHAR(100) DEFAULT '',
    university VARCHAR(150) DEFAULT '',
    title      VARCHAR(100) DEFAULT ''
);

-- ── courses ──────────────────────────────────────────────────

CREATE TABLE courses_module (
    id          SERIAL PRIMARY KEY,
    number      SMALLINT    NOT NULL UNIQUE,
    title       VARCHAR(200) NOT NULL,
    description TEXT         DEFAULT '',
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE
);

CREATE TABLE courses_topic (
    id          SERIAL PRIMARY KEY,
    module_id   INTEGER      NOT NULL REFERENCES courses_module(id) ON DELETE CASCADE,
    number      SMALLINT     NOT NULL,
    title       VARCHAR(200) NOT NULL,
    description TEXT         DEFAULT '',
    difficulty  VARCHAR(10)  NOT NULL DEFAULT 'medium',
    theory_url  VARCHAR(200) DEFAULT '',
    video_url   VARCHAR(200) DEFAULT '',
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
    "order"     SMALLINT     NOT NULL DEFAULT 0,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    UNIQUE (module_id, number)
);

CREATE TABLE courses_topicscore (
    id            SERIAL PRIMARY KEY,
    student_id    INTEGER   NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    topic_id      INTEGER   NOT NULL REFERENCES courses_topic(id) ON DELETE CASCADE,
    level         VARCHAR(15) NOT NULL DEFAULT 'beginner',
    mo_score      SMALLINT  NOT NULL DEFAULT 0 CHECK (mo_score <= 10),
    ko_score      SMALLINT  NOT NULL DEFAULT 0 CHECK (ko_score <= 20),
    fa_score      SMALLINT  NOT NULL DEFAULT 0 CHECK (fa_score <= 30),
    ad_score      SMALLINT  NOT NULL DEFAULT 0 CHECK (ad_score <= 15),
    kr_score      SMALLINT  NOT NULL DEFAULT 0 CHECK (kr_score <= 15),
    re_score      SMALLINT  NOT NULL DEFAULT 0 CHECK (re_score <= 10),
    total_score   SMALLINT  NOT NULL DEFAULT 0,      -- avtomatik hisob: Mo+Ko+Fa+Ad+Kr+Re
    is_completed  BOOLEAN   NOT NULL DEFAULT FALSE,
    attempt_count SMALLINT  NOT NULL DEFAULT 0,
    completed_at  TIMESTAMPTZ,
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (student_id, topic_id)
);

CREATE TABLE courses_task (
    id              SERIAL PRIMARY KEY,
    topic_id        INTEGER      NOT NULL REFERENCES courses_topic(id) ON DELETE CASCADE,
    title           VARCHAR(200) NOT NULL,
    description     TEXT         NOT NULL,
    task_type       VARCHAR(20)  NOT NULL DEFAULT 'algorithm',
    difficulty      VARCHAR(10)  NOT NULL DEFAULT 'medium',
    starter_code    TEXT         DEFAULT '',
    expected_output TEXT         DEFAULT '',
    test_cases      JSONB        NOT NULL DEFAULT '[]',
    time_limit_ms   INTEGER      NOT NULL DEFAULT 2000,
    memory_limit_mb INTEGER      NOT NULL DEFAULT 256,
    max_score       SMALLINT     NOT NULL DEFAULT 10,
    "order"         SMALLINT     NOT NULL DEFAULT 0,
    is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at      TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE courses_submission (
    id            SERIAL PRIMARY KEY,
    student_id    INTEGER     NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    task_id       INTEGER     NOT NULL REFERENCES courses_task(id) ON DELETE CASCADE,
    code          TEXT        NOT NULL,
    language      VARCHAR(20) NOT NULL DEFAULT 'csharp',
    status        VARCHAR(10) NOT NULL DEFAULT 'pending',
    runtime_ms    INTEGER,
    memory_kb     INTEGER,
    judge0_token  VARCHAR(100) DEFAULT '',
    test_results  JSONB       NOT NULL DEFAULT '[]',
    score_awarded SMALLINT    NOT NULL DEFAULT 0,
    error_message TEXT        DEFAULT '',
    submitted_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE courses_diagnostictest (
    id           SERIAL PRIMARY KEY,
    student_id   INTEGER  NOT NULL UNIQUE REFERENCES users_user(id) ON DELETE CASCADE,
    score        SMALLINT NOT NULL DEFAULT 0,
    level        VARCHAR(15) NOT NULL,
    answers      JSONB    NOT NULL DEFAULT '{}',
    completed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE courses_reflectionjournal (
    id         SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    topic_id   INTEGER NOT NULL REFERENCES courses_topic(id) ON DELETE CASCADE,
    content    TEXT    NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (student_id, topic_id)
);

-- ── gamification ─────────────────────────────────────────────

CREATE TABLE gamification_clan (
    id           SERIAL PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    tag          VARCHAR(10)  UNIQUE NOT NULL,
    emblem       VARCHAR(10)  NOT NULL DEFAULT '🏰',
    description  TEXT         DEFAULT '',
    leader_id    INTEGER REFERENCES users_user(id) ON DELETE SET NULL,
    rating_score INTEGER      NOT NULL DEFAULT 0,
    is_active    BOOLEAN      NOT NULL DEFAULT TRUE,
    created_at   TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE gamification_clanmembership (
    id        SERIAL PRIMARY KEY,
    clan_id   INTEGER NOT NULL REFERENCES gamification_clan(id) ON DELETE CASCADE,
    user_id   INTEGER NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    role      VARCHAR(10) NOT NULL DEFAULT 'member',
    joined_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (clan_id, user_id)
);

CREATE TABLE gamification_duel (
    id               SERIAL PRIMARY KEY,
    challenger_id    INTEGER NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    opponent_id      INTEGER REFERENCES users_user(id) ON DELETE CASCADE,
    task_id          INTEGER REFERENCES courses_task(id) ON DELETE SET NULL,
    duel_type        VARCHAR(15) NOT NULL DEFAULT 'algorithmic',
    status           VARCHAR(15) NOT NULL DEFAULT 'waiting',
    winner_id        INTEGER REFERENCES users_user(id) ON DELETE SET NULL,
    challenger_code  TEXT    DEFAULT '',
    opponent_code    TEXT    DEFAULT '',
    challenger_score SMALLINT NOT NULL DEFAULT 0,
    opponent_score   SMALLINT NOT NULL DEFAULT 0,
    rating_reward    SMALLINT NOT NULL DEFAULT 15,
    room_id          VARCHAR(50) UNIQUE NOT NULL,
    started_at       TIMESTAMPTZ,
    ended_at         TIMESTAMPTZ,
    created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE gamification_clanwar (
    id           SERIAL PRIMARY KEY,
    clan1_id     INTEGER NOT NULL REFERENCES gamification_clan(id) ON DELETE CASCADE,
    clan2_id     INTEGER NOT NULL REFERENCES gamification_clan(id) ON DELETE CASCADE,
    war_type     VARCHAR(15) NOT NULL DEFAULT 'algorithmic',
    status       VARCHAR(15) NOT NULL DEFAULT 'scheduled',
    winner_id    INTEGER REFERENCES gamification_clan(id) ON DELETE SET NULL,
    clan1_score  SMALLINT NOT NULL DEFAULT 0,
    clan2_score  SMALLINT NOT NULL DEFAULT 0,
    scheduled_at TIMESTAMPTZ NOT NULL,
    started_at   TIMESTAMPTZ,
    ended_at     TIMESTAMPTZ
);

CREATE TABLE gamification_clanchat (
    id         SERIAL PRIMARY KEY,
    clan_id    INTEGER NOT NULL REFERENCES gamification_clan(id) ON DELETE CASCADE,
    user_id    INTEGER NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    message    TEXT    NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE gamification_badge (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    description TEXT         NOT NULL,
    icon        VARCHAR(10)  NOT NULL DEFAULT '🏅',
    badge_type  VARCHAR(15)  NOT NULL,
    condition   JSONB        NOT NULL DEFAULT '{}',
    is_active   BOOLEAN      NOT NULL DEFAULT TRUE
);

CREATE TABLE gamification_userbadge (
    id        SERIAL PRIMARY KEY,
    user_id   INTEGER NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    badge_id  INTEGER NOT NULL REFERENCES gamification_badge(id) ON DELETE CASCADE,
    earned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, badge_id)
);

-- ── social ───────────────────────────────────────────────────

CREATE TABLE social_peerreview (
    id             SERIAL PRIMARY KEY,
    reviewer_id    INTEGER  NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    reviewee_id    INTEGER  NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    topic_score_id INTEGER  NOT NULL REFERENCES courses_topicscore(id) ON DELETE CASCADE,
    ko_score       SMALLINT NOT NULL DEFAULT 0 CHECK (ko_score <= 20),
    fa_score       SMALLINT NOT NULL DEFAULT 0 CHECK (fa_score <= 30),
    ad_score       SMALLINT NOT NULL DEFAULT 0 CHECK (ad_score <= 15),
    kr_score       SMALLINT NOT NULL DEFAULT 0 CHECK (kr_score <= 15),
    re_score       SMALLINT NOT NULL DEFAULT 0 CHECK (re_score <= 10),
    comment        TEXT     NOT NULL,
    star_rating    SMALLINT NOT NULL DEFAULT 3 CHECK (star_rating BETWEEN 1 AND 5),
    created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (reviewer_id, topic_score_id)
);

CREATE TABLE social_notification (
    id          SERIAL PRIMARY KEY,
    user_id     INTEGER      NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    title       VARCHAR(200) NOT NULL,
    message     TEXT         NOT NULL,
    notif_type  VARCHAR(15)  NOT NULL DEFAULT 'system',
    is_read     BOOLEAN      NOT NULL DEFAULT FALSE,
    link        VARCHAR(200) DEFAULT '',
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE social_activitylog (
    id            SERIAL PRIMARY KEY,
    user_id       INTEGER NOT NULL REFERENCES users_user(id) ON DELETE CASCADE,
    activity_type VARCHAR(15) NOT NULL,
    date          DATE        NOT NULL,
    detail        JSONB       NOT NULL DEFAULT '{}',
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ── Indexes ──────────────────────────────────────────────────

CREATE INDEX idx_topicscore_student    ON courses_topicscore(student_id);
CREATE INDEX idx_topicscore_completed  ON courses_topicscore(is_completed);
CREATE INDEX idx_submission_student    ON courses_submission(student_id);
CREATE INDEX idx_submission_status     ON courses_submission(status);
CREATE INDEX idx_activitylog_user_date ON social_activitylog(user_id, date);
CREATE INDEX idx_notification_user     ON social_notification(user_id, is_read);
CREATE INDEX idx_duel_room             ON gamification_duel(room_id);
CREATE INDEX idx_peerreview_reviewer   ON social_peerreview(reviewer_id);
