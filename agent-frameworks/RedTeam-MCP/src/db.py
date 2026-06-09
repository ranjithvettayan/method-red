"""
SQLite Database Layer for Red Team MCP

Provides persistent storage for agents, teams, and settings.
Initializes from YAML config on first run.
"""

import sqlite3
import json
import secrets
import hashlib
import logging
from pathlib import Path
from datetime import datetime, UTC, timedelta
from typing import Dict, List, Any, Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Default database path
DEFAULT_DB_PATH = Path(__file__).parent.parent / "data" / "agents.db"


class Database:
    """SQLite database manager for agent configuration"""
    
    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()
    
    @contextmanager
    def _get_conn(self):
        """Get a database connection with row factory"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _init_schema(self):
        """Initialize database schema"""
        with self._get_conn() as conn:
            conn.executescript("""
                -- Settings table (key-value store)
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    category TEXT DEFAULT 'general',
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Agents table
                CREATE TABLE IF NOT EXISTS agents (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    model_id TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    role TEXT NOT NULL,
                    goal TEXT NOT NULL,
                    backstory TEXT NOT NULL,
                    enable_memory INTEGER DEFAULT 1,
                    sampling_params TEXT DEFAULT '{}',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Teams table
                CREATE TABLE IF NOT EXISTS teams (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    default_mode TEXT DEFAULT 'ensemble',
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Team members (many-to-many)
                CREATE TABLE IF NOT EXISTS team_members (
                    team_id TEXT NOT NULL,
                    agent_id TEXT NOT NULL,
                    position INTEGER DEFAULT 0,
                    PRIMARY KEY (team_id, agent_id),
                    FOREIGN KEY (team_id) REFERENCES teams(id) ON DELETE CASCADE,
                    FOREIGN KEY (agent_id) REFERENCES agents(id) ON DELETE CASCADE
                );
                
                -- Create indexes
                CREATE INDEX IF NOT EXISTS idx_agents_provider ON agents(provider);
                CREATE INDEX IF NOT EXISTS idx_team_members_team ON team_members(team_id);
                CREATE INDEX IF NOT EXISTS idx_team_members_agent ON team_members(agent_id);
                
                -- Custom providers table (for self-hosted like LM Studio, Ollama, etc.)
                CREATE TABLE IF NOT EXISTS custom_providers (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    base_url TEXT NOT NULL,
                    api_key TEXT DEFAULT '',
                    provider_type TEXT DEFAULT 'openai-compatible',
                    is_enabled INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                
                -- Custom models table (models for custom providers)
                CREATE TABLE IF NOT EXISTS custom_models (
                    id TEXT PRIMARY KEY,
                    provider_id TEXT NOT NULL,
                    model_name TEXT NOT NULL,
                    display_name TEXT,
                    context_length INTEGER DEFAULT 4096,
                    max_output INTEGER DEFAULT 4096,
                    supports_vision INTEGER DEFAULT 0,
                    supports_tools INTEGER DEFAULT 0,
                    supports_streaming INTEGER DEFAULT 1,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (provider_id) REFERENCES custom_providers(id) ON DELETE CASCADE
                );
                
                CREATE INDEX IF NOT EXISTS idx_custom_models_provider ON custom_models(provider_id);
                
                -- Usage tracking table
                CREATE TABLE IF NOT EXISTS usage_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT,
                    team_id TEXT,
                    provider TEXT NOT NULL,
                    model_id TEXT NOT NULL,
                    input_tokens INTEGER DEFAULT 0,
                    output_tokens INTEGER DEFAULT 0,
                    cached_tokens INTEGER DEFAULT 0,
                    input_cost REAL DEFAULT 0,
                    output_cost REAL DEFAULT 0,
                    total_cost REAL DEFAULT 0,
                    response_time_ms INTEGER DEFAULT 0,
                    success INTEGER DEFAULT 1,
                    error_message TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                );
                
                CREATE INDEX IF NOT EXISTS idx_usage_logs_agent ON usage_logs(agent_id);
                CREATE INDEX IF NOT EXISTS idx_usage_logs_provider ON usage_logs(provider);
                CREATE INDEX IF NOT EXISTS idx_usage_logs_created ON usage_logs(created_at);
            """)
    
    # ==================== Token Management ====================
    
    def get_or_create_token(self) -> Optional[str]:
        """Get existing token info or create new one. Returns raw token only on creation."""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT value FROM settings WHERE key = 'api_token_hash'"
            ).fetchone()
            
            if row:
                # Token exists, don't return it (can't retrieve from hash)
                return None
            
            # Generate new token
            raw_token = f"mcp_sk_{secrets.token_urlsafe(32)}"
            token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
            token_prefix = raw_token[:12]
            now = datetime.now(UTC).isoformat()
            
            conn.execute(
                "INSERT OR REPLACE INTO settings (key, value, category) VALUES (?, ?, ?)",
                ("api_token_hash", token_hash, "auth")
            )
            conn.execute(
                "INSERT OR REPLACE INTO settings (key, value, category) VALUES (?, ?, ?)",
                ("api_token_prefix", token_prefix, "auth")
            )
            conn.execute(
                "INSERT OR REPLACE INTO settings (key, value, category) VALUES (?, ?, ?)",
                ("api_token_created_at", now, "auth")
            )
            
            return raw_token
    
    def regenerate_token(self) -> str:
        """Generate a new token, invalidating the old one"""
        with self._get_conn() as conn:
            raw_token = f"mcp_sk_{secrets.token_urlsafe(32)}"
            token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
            token_prefix = raw_token[:12]
            now = datetime.now(UTC).isoformat()
            
            conn.execute(
                "INSERT OR REPLACE INTO settings (key, value, category) VALUES (?, ?, ?)",
                ("api_token_hash", token_hash, "auth")
            )
            conn.execute(
                "INSERT OR REPLACE INTO settings (key, value, category) VALUES (?, ?, ?)",
                ("api_token_prefix", token_prefix, "auth")
            )
            conn.execute(
                "INSERT OR REPLACE INTO settings (key, value, category) VALUES (?, ?, ?)",
                ("api_token_created_at", now, "auth")
            )
            
            return raw_token
    
    def validate_token(self, token: str) -> bool:
        """Validate a token against stored hash"""
        if not token:
            return False
        
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT value FROM settings WHERE key = 'api_token_hash'"
            ).fetchone()
            
            if not row:
                return False
            
            provided_hash = hashlib.sha256(token.encode()).hexdigest()
            return secrets.compare_digest(row["value"], provided_hash)
    
    def get_token_info(self) -> Dict[str, Any]:
        """Get token metadata (not the token itself)"""
        with self._get_conn() as conn:
            prefix = conn.execute(
                "SELECT value FROM settings WHERE key = 'api_token_prefix'"
            ).fetchone()
            created = conn.execute(
                "SELECT value FROM settings WHERE key = 'api_token_created_at'"
            ).fetchone()
            
            return {
                "prefix": prefix["value"] if prefix else None,
                "created_at": created["value"] if created else None,
                "exists": prefix is not None
            }
    
    # ==================== Settings ====================
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a setting value"""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT value FROM settings WHERE key = ?", (key,)
            ).fetchone()
            
            if row:
                try:
                    return json.loads(row["value"])
                except json.JSONDecodeError:
                    return row["value"]
            return default
    
    def set_setting(self, key: str, value: Any, category: str = "general"):
        """Set a setting value"""
        with self._get_conn() as conn:
            if isinstance(value, (dict, list)):
                value = json.dumps(value)
            conn.execute(
                """INSERT OR REPLACE INTO settings (key, value, category, updated_at) 
                   VALUES (?, ?, ?, ?)""",
                (key, str(value), category, datetime.now(UTC).isoformat())
            )
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings grouped by category"""
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT key, value, category FROM settings WHERE category != 'auth'"
            ).fetchall()
            
            result = {}
            for row in rows:
                try:
                    value = json.loads(row["value"])
                except (json.JSONDecodeError, TypeError):
                    value = row["value"]
                result[row["key"]] = {
                    "value": value,
                    "category": row["category"]
                }
            return result
    
    def update_settings(self, settings: Dict[str, Any]):
        """Update multiple settings"""
        for key, value in settings.items():
            if not key.startswith("api_token"):  # Protect token settings
                self.set_setting(key, value)
    
    # ==================== Agents CRUD ====================
    
    def get_agents(self) -> List[Dict[str, Any]]:
        """Get all agents"""
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM agents ORDER BY name").fetchall()
            return [self._row_to_agent(row) for row in rows]
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get a single agent by ID"""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM agents WHERE id = ?", (agent_id,)
            ).fetchone()
            return self._row_to_agent(row) if row else None
    
    def create_agent(self, agent: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new agent"""
        now = datetime.now(UTC).isoformat()
        sampling_params = json.dumps(agent.get("sampling_params", {}))
        
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO agents (id, name, model_id, provider, role, goal, backstory, 
                                   enable_memory, sampling_params, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                agent["id"],
                agent.get("name", agent["id"]),
                agent["model_id"],
                agent["provider"],
                agent["role"],
                agent["goal"],
                agent["backstory"],
                1 if agent.get("enable_memory", True) else 0,
                sampling_params,
                now,
                now
            ))
        
        return self.get_agent(agent["id"])
    
    def update_agent(self, agent_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing agent"""
        existing = self.get_agent(agent_id)
        if not existing:
            return None
        
        # Merge updates
        for key, value in updates.items():
            if key != "id":  # Can't change ID
                existing[key] = value
        
        existing["updated_at"] = datetime.now(UTC).isoformat()
        sampling_params = json.dumps(existing.get("sampling_params", {}))
        
        with self._get_conn() as conn:
            conn.execute("""
                UPDATE agents SET name=?, model_id=?, provider=?, role=?, goal=?, 
                                 backstory=?, enable_memory=?, sampling_params=?, updated_at=?
                WHERE id=?
            """, (
                existing["name"],
                existing["model_id"],
                existing["provider"],
                existing["role"],
                existing["goal"],
                existing["backstory"],
                1 if existing.get("enable_memory", True) else 0,
                sampling_params,
                existing["updated_at"],
                agent_id
            ))
        
        return self.get_agent(agent_id)
    
    def delete_agent(self, agent_id: str) -> bool:
        """Delete an agent"""
        with self._get_conn() as conn:
            cursor = conn.execute("DELETE FROM agents WHERE id = ?", (agent_id,))
            return cursor.rowcount > 0
    
    def _row_to_agent(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert a database row to an agent dict"""
        return {
            "id": row["id"],
            "name": row["name"],
            "model_id": row["model_id"],
            "provider": row["provider"],
            "role": row["role"],
            "goal": row["goal"],
            "backstory": row["backstory"],
            "enable_memory": bool(row["enable_memory"]),
            "sampling_params": json.loads(row["sampling_params"] or "{}"),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        }
    
    # ==================== Teams CRUD ====================
    
    def get_teams(self) -> List[Dict[str, Any]]:
        """Get all teams with their members"""
        with self._get_conn() as conn:
            teams = conn.execute("SELECT * FROM teams ORDER BY name").fetchall()
            result = []
            for team in teams:
                team_dict = self._row_to_team(team)
                team_dict["members"] = self._get_team_members(conn, team["id"])
                result.append(team_dict)
            return result
    
    def get_team(self, team_id: str) -> Optional[Dict[str, Any]]:
        """Get a single team by ID with members"""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM teams WHERE id = ?", (team_id,)
            ).fetchone()
            
            if not row:
                return None
            
            team = self._row_to_team(row)
            team["members"] = self._get_team_members(conn, team_id)
            return team
    
    def create_team(self, team: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new team"""
        now = datetime.now(UTC).isoformat()
        
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO teams (id, name, description, default_mode, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                team["id"],
                team.get("name", team["id"]),
                team.get("description", ""),
                team.get("default_mode", "ensemble"),
                now,
                now
            ))
            
            # Add members
            for i, agent_id in enumerate(team.get("members", [])):
                conn.execute(
                    "INSERT OR IGNORE INTO team_members (team_id, agent_id, position) VALUES (?, ?, ?)",
                    (team["id"], agent_id, i)
                )
        
        return self.get_team(team["id"])
    
    def update_team(self, team_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing team"""
        existing = self.get_team(team_id)
        if not existing:
            return None
        
        now = datetime.now(UTC).isoformat()
        
        with self._get_conn() as conn:
            conn.execute("""
                UPDATE teams SET name=?, description=?, default_mode=?, updated_at=?
                WHERE id=?
            """, (
                updates.get("name", existing["name"]),
                updates.get("description", existing["description"]),
                updates.get("default_mode", existing["default_mode"]),
                now,
                team_id
            ))
            
            # Update members if provided
            if "members" in updates:
                conn.execute("DELETE FROM team_members WHERE team_id = ?", (team_id,))
                for i, agent_id in enumerate(updates["members"]):
                    conn.execute(
                        "INSERT INTO team_members (team_id, agent_id, position) VALUES (?, ?, ?)",
                        (team_id, agent_id, i)
                    )
        
        return self.get_team(team_id)
    
    def delete_team(self, team_id: str) -> bool:
        """Delete a team"""
        with self._get_conn() as conn:
            cursor = conn.execute("DELETE FROM teams WHERE id = ?", (team_id,))
            return cursor.rowcount > 0
    
    def add_team_member(self, team_id: str, agent_id: str) -> bool:
        """Add an agent to a team"""
        with self._get_conn() as conn:
            # Get max position
            row = conn.execute(
                "SELECT MAX(position) as max_pos FROM team_members WHERE team_id = ?",
                (team_id,)
            ).fetchone()
            position = (row["max_pos"] or -1) + 1
            
            try:
                conn.execute(
                    "INSERT INTO team_members (team_id, agent_id, position) VALUES (?, ?, ?)",
                    (team_id, agent_id, position)
                )
                return True
            except sqlite3.IntegrityError:
                return False
    
    def remove_team_member(self, team_id: str, agent_id: str) -> bool:
        """Remove an agent from a team"""
        with self._get_conn() as conn:
            cursor = conn.execute(
                "DELETE FROM team_members WHERE team_id = ? AND agent_id = ?",
                (team_id, agent_id)
            )
            return cursor.rowcount > 0
    
    def _get_team_members(self, conn: sqlite3.Connection, team_id: str) -> List[str]:
        """Get member agent IDs for a team"""
        rows = conn.execute(
            "SELECT agent_id FROM team_members WHERE team_id = ? ORDER BY position",
            (team_id,)
        ).fetchall()
        return [row["agent_id"] for row in rows]
    
    def _row_to_team(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert a database row to a team dict"""
        return {
            "id": row["id"],
            "name": row["name"],
            "description": row["description"],
            "default_mode": row["default_mode"],
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        }
    
    # ==================== Custom Providers CRUD ====================
    
    def get_custom_providers(self) -> List[Dict[str, Any]]:
        """Get all custom providers"""
        with self._get_conn() as conn:
            rows = conn.execute(
                "SELECT * FROM custom_providers ORDER BY name"
            ).fetchall()
            return [self._row_to_custom_provider(row) for row in rows]
    
    def get_custom_provider(self, provider_id: str) -> Optional[Dict[str, Any]]:
        """Get a single custom provider by ID"""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM custom_providers WHERE id = ?", (provider_id,)
            ).fetchone()
            return self._row_to_custom_provider(row) if row else None
    
    def create_custom_provider(self, provider: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new custom provider"""
        now = datetime.now(UTC).isoformat()
        
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO custom_providers (id, name, base_url, api_key, provider_type, 
                                             is_enabled, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                provider["id"],
                provider.get("name", provider["id"]),
                provider["base_url"],
                provider.get("api_key", ""),
                provider.get("provider_type", "openai-compatible"),
                1 if provider.get("is_enabled", True) else 0,
                now,
                now
            ))
        
        return self.get_custom_provider(provider["id"])
    
    def update_custom_provider(self, provider_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing custom provider"""
        existing = self.get_custom_provider(provider_id)
        if not existing:
            return None
        
        # Merge updates
        for key, value in updates.items():
            if key != "id":
                existing[key] = value
        
        existing["updated_at"] = datetime.now(UTC).isoformat()
        
        with self._get_conn() as conn:
            conn.execute("""
                UPDATE custom_providers 
                SET name=?, base_url=?, api_key=?, provider_type=?, is_enabled=?, updated_at=?
                WHERE id=?
            """, (
                existing["name"],
                existing["base_url"],
                existing.get("api_key", ""),
                existing.get("provider_type", "openai-compatible"),
                1 if existing.get("is_enabled", True) else 0,
                existing["updated_at"],
                provider_id
            ))
        
        return self.get_custom_provider(provider_id)
    
    def delete_custom_provider(self, provider_id: str) -> bool:
        """Delete a custom provider and its models"""
        with self._get_conn() as conn:
            cursor = conn.execute("DELETE FROM custom_providers WHERE id = ?", (provider_id,))
            return cursor.rowcount > 0
    
    def _row_to_custom_provider(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert a database row to a custom provider dict"""
        return {
            "id": row["id"],
            "name": row["name"],
            "base_url": row["base_url"],
            "api_key": row["api_key"],
            "provider_type": row["provider_type"],
            "is_enabled": bool(row["is_enabled"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        }
    
    # ==================== Custom Models CRUD ====================
    
    def get_custom_models(self, provider_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get custom models, optionally filtered by provider"""
        with self._get_conn() as conn:
            if provider_id:
                rows = conn.execute(
                    "SELECT * FROM custom_models WHERE provider_id = ? ORDER BY display_name",
                    (provider_id,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT * FROM custom_models ORDER BY provider_id, display_name"
                ).fetchall()
            return [self._row_to_custom_model(row) for row in rows]
    
    def get_custom_model(self, model_id: str) -> Optional[Dict[str, Any]]:
        """Get a single custom model by ID"""
        with self._get_conn() as conn:
            row = conn.execute(
                "SELECT * FROM custom_models WHERE id = ?", (model_id,)
            ).fetchone()
            return self._row_to_custom_model(row) if row else None
    
    def create_custom_model(self, model: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new custom model"""
        now = datetime.now(UTC).isoformat()
        
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO custom_models (id, provider_id, model_name, display_name, 
                                          context_length, max_output, supports_vision,
                                          supports_tools, supports_streaming, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                model["id"],
                model["provider_id"],
                model["model_name"],
                model.get("display_name", model["model_name"]),
                model.get("context_length", 4096),
                model.get("max_output", 4096),
                1 if model.get("supports_vision", False) else 0,
                1 if model.get("supports_tools", False) else 0,
                1 if model.get("supports_streaming", True) else 0,
                now,
                now
            ))
        
        return self.get_custom_model(model["id"])
    
    def update_custom_model(self, model_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing custom model"""
        existing = self.get_custom_model(model_id)
        if not existing:
            return None
        
        # Merge updates
        for key, value in updates.items():
            if key != "id":
                existing[key] = value
        
        existing["updated_at"] = datetime.now(UTC).isoformat()
        
        with self._get_conn() as conn:
            conn.execute("""
                UPDATE custom_models 
                SET model_name=?, display_name=?, context_length=?, max_output=?,
                    supports_vision=?, supports_tools=?, supports_streaming=?, updated_at=?
                WHERE id=?
            """, (
                existing["model_name"],
                existing.get("display_name", existing["model_name"]),
                existing.get("context_length", 4096),
                existing.get("max_output", 4096),
                1 if existing.get("supports_vision", False) else 0,
                1 if existing.get("supports_tools", False) else 0,
                1 if existing.get("supports_streaming", True) else 0,
                existing["updated_at"],
                model_id
            ))
        
        return self.get_custom_model(model_id)
    
    def delete_custom_model(self, model_id: str) -> bool:
        """Delete a custom model"""
        with self._get_conn() as conn:
            cursor = conn.execute("DELETE FROM custom_models WHERE id = ?", (model_id,))
            return cursor.rowcount > 0
    
    def _row_to_custom_model(self, row: sqlite3.Row) -> Dict[str, Any]:
        """Convert a database row to a custom model dict"""
        return {
            "id": row["id"],
            "provider_id": row["provider_id"],
            "model_name": row["model_name"],
            "display_name": row["display_name"],
            "context_length": row["context_length"],
            "max_output": row["max_output"],
            "supports_vision": bool(row["supports_vision"]),
            "supports_tools": bool(row["supports_tools"]),
            "supports_streaming": bool(row["supports_streaming"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        }
    
    # ==================== Usage Tracking ====================
    
    def log_usage(self, usage: Dict[str, Any]) -> int:
        """Log API usage for tracking and costing"""
        now = datetime.now(UTC).isoformat()
        
        with self._get_conn() as conn:
            cursor = conn.execute("""
                INSERT INTO usage_logs (
                    agent_id, team_id, provider, model_id,
                    input_tokens, output_tokens, cached_tokens,
                    input_cost, output_cost, total_cost,
                    response_time_ms, success, error_message, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                usage.get("agent_id"),
                usage.get("team_id"),
                usage["provider"],
                usage["model_id"],
                usage.get("input_tokens", 0),
                usage.get("output_tokens", 0),
                usage.get("cached_tokens", 0),
                usage.get("input_cost", 0),
                usage.get("output_cost", 0),
                usage.get("total_cost", 0),
                usage.get("response_time_ms", 0),
                1 if usage.get("success", True) else 0,
                usage.get("error_message"),
                now
            ))
            return cursor.lastrowid
    
    def get_usage_stats(self, 
                        days: int = 30, 
                        agent_id: Optional[str] = None,
                        provider: Optional[str] = None) -> Dict[str, Any]:
        """Get usage statistics for the specified period"""
        from_date = (datetime.now(UTC) - timedelta(days=days)).isoformat()
        
        with self._get_conn() as conn:
            # Build query with optional filters
            conditions = ["created_at >= ?"]
            params = [from_date]
            
            if agent_id:
                conditions.append("agent_id = ?")
                params.append(agent_id)
            if provider:
                conditions.append("provider = ?")
                params.append(provider)
            
            where_clause = " AND ".join(conditions)
            
            # Get totals
            totals = conn.execute(f"""
                SELECT 
                    COUNT(*) as total_requests,
                    SUM(input_tokens) as total_input_tokens,
                    SUM(output_tokens) as total_output_tokens,
                    SUM(cached_tokens) as total_cached_tokens,
                    SUM(total_cost) as total_cost,
                    AVG(response_time_ms) as avg_response_time,
                    SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful_requests,
                    SUM(CASE WHEN success = 0 THEN 1 ELSE 0 END) as failed_requests
                FROM usage_logs
                WHERE {where_clause}
            """, params).fetchone()
            
            # Get breakdown by provider
            by_provider = conn.execute(f"""
                SELECT 
                    provider,
                    COUNT(*) as requests,
                    SUM(input_tokens) as input_tokens,
                    SUM(output_tokens) as output_tokens,
                    SUM(total_cost) as cost
                FROM usage_logs
                WHERE {where_clause}
                GROUP BY provider
                ORDER BY cost DESC
            """, params).fetchall()
            
            # Get breakdown by model
            by_model = conn.execute(f"""
                SELECT 
                    provider,
                    model_id,
                    COUNT(*) as requests,
                    SUM(input_tokens) as input_tokens,
                    SUM(output_tokens) as output_tokens,
                    SUM(total_cost) as cost
                FROM usage_logs
                WHERE {where_clause}
                GROUP BY provider, model_id
                ORDER BY cost DESC
                LIMIT 20
            """, params).fetchall()
            
            # Get breakdown by agent
            by_agent = conn.execute(f"""
                SELECT 
                    agent_id,
                    COUNT(*) as requests,
                    SUM(input_tokens) as input_tokens,
                    SUM(output_tokens) as output_tokens,
                    SUM(total_cost) as cost
                FROM usage_logs
                WHERE {where_clause} AND agent_id IS NOT NULL
                GROUP BY agent_id
                ORDER BY cost DESC
                LIMIT 20
            """, params).fetchall()
            
            # Get daily breakdown
            daily = conn.execute(f"""
                SELECT 
                    DATE(created_at) as date,
                    COUNT(*) as requests,
                    SUM(input_tokens) as input_tokens,
                    SUM(output_tokens) as output_tokens,
                    SUM(total_cost) as cost
                FROM usage_logs
                WHERE {where_clause}
                GROUP BY DATE(created_at)
                ORDER BY date DESC
                LIMIT {days}
            """, params).fetchall()
            
            return {
                "period_days": days,
                "totals": {
                    "requests": totals["total_requests"] or 0,
                    "input_tokens": totals["total_input_tokens"] or 0,
                    "output_tokens": totals["total_output_tokens"] or 0,
                    "cached_tokens": totals["total_cached_tokens"] or 0,
                    "total_cost": round(totals["total_cost"] or 0, 4),
                    "avg_response_time_ms": round(totals["avg_response_time"] or 0, 0),
                    "successful_requests": totals["successful_requests"] or 0,
                    "failed_requests": totals["failed_requests"] or 0,
                },
                "by_provider": [
                    {
                        "provider": row["provider"],
                        "requests": row["requests"],
                        "input_tokens": row["input_tokens"] or 0,
                        "output_tokens": row["output_tokens"] or 0,
                        "cost": round(row["cost"] or 0, 4),
                    }
                    for row in by_provider
                ],
                "by_model": [
                    {
                        "provider": row["provider"],
                        "model_id": row["model_id"],
                        "requests": row["requests"],
                        "input_tokens": row["input_tokens"] or 0,
                        "output_tokens": row["output_tokens"] or 0,
                        "cost": round(row["cost"] or 0, 4),
                    }
                    for row in by_model
                ],
                "by_agent": [
                    {
                        "agent_id": row["agent_id"],
                        "requests": row["requests"],
                        "input_tokens": row["input_tokens"] or 0,
                        "output_tokens": row["output_tokens"] or 0,
                        "cost": round(row["cost"] or 0, 4),
                    }
                    for row in by_agent
                ],
                "daily": [
                    {
                        "date": row["date"],
                        "requests": row["requests"],
                        "input_tokens": row["input_tokens"] or 0,
                        "output_tokens": row["output_tokens"] or 0,
                        "cost": round(row["cost"] or 0, 4),
                    }
                    for row in daily
                ],
            }
    
    def get_recent_usage(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent usage logs"""
        with self._get_conn() as conn:
            rows = conn.execute("""
                SELECT * FROM usage_logs
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,)).fetchall()
            
            return [
                {
                    "id": row["id"],
                    "agent_id": row["agent_id"],
                    "team_id": row["team_id"],
                    "provider": row["provider"],
                    "model_id": row["model_id"],
                    "input_tokens": row["input_tokens"],
                    "output_tokens": row["output_tokens"],
                    "cached_tokens": row["cached_tokens"],
                    "input_cost": row["input_cost"],
                    "output_cost": row["output_cost"],
                    "total_cost": row["total_cost"],
                    "response_time_ms": row["response_time_ms"],
                    "success": bool(row["success"]),
                    "error_message": row["error_message"],
                    "created_at": row["created_at"],
                }
                for row in rows
            ]
    
    def clear_usage_logs(self, before_date: Optional[str] = None) -> int:
        """Clear usage logs, optionally only before a certain date"""
        with self._get_conn() as conn:
            if before_date:
                cursor = conn.execute(
                    "DELETE FROM usage_logs WHERE created_at < ?",
                    (before_date,)
                )
            else:
                cursor = conn.execute("DELETE FROM usage_logs")
            return cursor.rowcount
    
    # ==================== Import/Export ====================
    
    def export_all(self) -> Dict[str, Any]:
        """Export all data as JSON-serializable dict"""
        return {
            "agents": self.get_agents(),
            "teams": self.get_teams(),
            "settings": self.get_all_settings(),
            "exported_at": datetime.now(UTC).isoformat()
        }
    
    def import_all(self, data: Dict[str, Any], replace: bool = False):
        """Import data from dict"""
        if replace:
            with self._get_conn() as conn:
                conn.execute("DELETE FROM team_members")
                conn.execute("DELETE FROM teams")
                conn.execute("DELETE FROM agents")
                conn.execute("DELETE FROM settings WHERE category != 'auth'")
        
        # Import agents
        for agent in data.get("agents", []):
            if not self.get_agent(agent["id"]):
                self.create_agent(agent)
            elif replace:
                self.update_agent(agent["id"], agent)
        
        # Import teams
        for team in data.get("teams", []):
            if not self.get_team(team["id"]):
                self.create_team(team)
            elif replace:
                self.update_team(team["id"], team)
        
        # Import settings
        for key, setting in data.get("settings", {}).items():
            value = setting.get("value", setting) if isinstance(setting, dict) else setting
            category = setting.get("category", "general") if isinstance(setting, dict) else "general"
            self.set_setting(key, value, category)
    
    def import_from_yaml_config(self, config):
        """Import from the existing YAML config object"""
        # Import agents
        for agent in config.get_predefined_agents().values():
            if not self.get_agent(agent.get("id", agent.get("name", "").lower().replace(" ", "_"))):
                agent_data = {
                    "id": agent.get("id", agent.get("name", "").lower().replace(" ", "_")),
                    "name": agent.get("name", agent.get("id", "")),
                    "model_id": agent.get("model_id", "claude-3-haiku-20240307"),
                    "provider": agent.get("provider", "anthropic"),
                    "role": agent.get("role", "Assistant"),
                    "goal": agent.get("goal", "Help users"),
                    "backstory": agent.get("backstory", "A helpful AI assistant"),
                    "enable_memory": agent.get("enable_memory", True),
                    "sampling_params": agent.get("sampling_params", {})
                }
                self.create_agent(agent_data)
        
        # Import teams
        for team_id, team in config.get_teams().items():
            if not self.get_team(team_id):
                team_data = {
                    "id": team_id,
                    "name": team.get("name", team_id),
                    "description": team.get("description", ""),
                    "default_mode": team.get("default_mode", "ensemble"),
                    "members": team.get("members", team.get("agents", []))
                }
                self.create_team(team_data)
        
        # Import settings
        settings_to_import = [
            ("api.host", config.get("api.host", "0.0.0.0")),
            ("api.port", config.get("api.port", 8000)),
            ("api.rate_limit", config.get("api.rate_limit", "100/minute")),
            ("logging.level", config.get("logging.level", "INFO")),
            ("models.default", config.get("models.default", "claude-3-haiku-20240307")),
        ]
        
        for key, value in settings_to_import:
            if self.get_setting(key) is None:
                category = key.split(".")[0]
                self.set_setting(key, value, category)
    
    def is_initialized(self) -> bool:
        """Check if database has been initialized with data"""
        with self._get_conn() as conn:
            row = conn.execute("SELECT COUNT(*) as count FROM agents").fetchone()
            return row["count"] > 0


# Global database instance
_db: Optional[Database] = None


def get_db() -> Database:
    """Get the global database instance"""
    global _db
    if _db is None:
        _db = Database()
    return _db


def init_db(db_path: Optional[Path] = None) -> Database:
    """Initialize the database with optional custom path"""
    global _db
    _db = Database(db_path)
    return _db
