import os, json, time
from typing import Dict, Any, List
from datetime import datetime, timedelta
from azure.cosmos import CosmosClient, PartitionKey, exceptions

COSMOS_URL = os.getenv("COSMOS_URL")
COSMOS_KEY = os.getenv("COSMOS_KEY")
COSMOS_DB = os.getenv("COSMOS_DB", "GmailDigest")
COSMOS_CONTAINER = os.getenv("COSMOS_CONTAINER", "Data")

DEFAULT_PREFS = {
    "vip_senders": [],
    "blocked_senders": [],
    "always_keywords": [],
    "mute_keywords": [],
    "urgency_bias": 0.5,
    "weights": {}, "email_theme":"light", "top_n":20, "min_score":0.0, "importance_threshold":0.5, "email_theme":"light", "top_n":20
}

class Storage:
    def __init__(self):
        self.client = CosmosClient(COSMOS_URL, COSMOS_KEY) if COSMOS_URL and COSMOS_KEY else None
        if self.client:
            self.db = self.client.create_database_if_not_exists(id=COSMOS_DB)
            self.container = self.db.create_container_if_not_exists(id=COSMOS_CONTAINER, partition_key=PartitionKey(path="/pk"))
        else:
            raise RuntimeError("Cosmos DB env not configured")

    # --- Allowlist & Admins ---
    def bootstrap_admin(self, admin_email: str):
        if not admin_email: return
        if not self.is_allowed(admin_email):
            self.container.upsert_item({"id": f"user:{admin_email}", "pk":"user", "email": admin_email, "role":"admin"})
    def is_admin(self, email: str) -> bool:
        try:
            item = self.container.read_item(item=f"user:{email}", partition_key="user")
            return item.get("role") == "admin"
        except exceptions.CosmosHttpResponseError:
            return False
    def is_allowed(self, email: str) -> bool:
        try:
            self.container.read_item(item=f"user:{email}", partition_key="user")
            return True
        except exceptions.CosmosHttpResponseError:
            return False
    def get_allowlist(self) -> List[str]:
        q = "SELECT c.email FROM c WHERE c.pk='user'"
        return [x["email"] for x in self.container.query_items(q, enable_cross_partition_query=True)]
    def add_allowed(self, email: str):
        self.container.upsert_item({"id": f"user:{email}", "pk":"user", "email": email, "role":"user"})
    def remove_allowed(self, email: str):
        try: self.container.delete_item(item=f"user:{email}", partition_key="user")
        except exceptions.CosmosHttpResponseError: pass

    # --- Prefs ---
    def get_prefs(self, email: str) -> Dict[str, Any]:
        try:
            item = self.container.read_item(item=f"prefs:{email}", partition_key="prefs")
            return item.get("data", DEFAULT_PREFS.copy())
        except exceptions.CosmosHttpResponseError:
            return DEFAULT_PREFS.copy()
    def save_prefs(self, email: str, data: Dict[str, Any]):
        self.container.upsert_item({"id": f"prefs:{email}", "pk":"prefs", "email": email, "data": data})

    # --- Digests ---
    def save_digest(self, email: str, messages: List[Dict]):
        ts = datetime.utcnow().isoformat()
        self.container.upsert_item({"id": f"digest:{email}:{ts}", "pk":"digest", "email": email, "created_at": ts, "data": messages})

    # --- Retention ---
    def cleanup_retention(self, days: int = 180):
        cutoff = (datetime.utcnow() - timedelta(days=days)).isoformat()
        q = f"SELECT c.id FROM c WHERE c.pk='digest' AND c.created_at < '{cutoff}'"
        to_delete = [x["id"] for x in self.container.query_items(q, enable_cross_partition_query=True)]
        for id_ in to_delete:
            try: self.container.delete_item(item=id_, partition_key="digest")
            except exceptions.CosmosHttpResponseError: pass


    def get_digests_since(self, cutoff_iso: str):
        q = f"SELECT c.id, c.email, c.created_at, c.data FROM c WHERE c.pk='digest' AND c.created_at >= '{cutoff_iso}'"
        return list(self.container.query_items(q, enable_cross_partition_query=True))
