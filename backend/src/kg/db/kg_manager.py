"""
Knowledge Graph Management Module
Handles export, import, and switching between different Neo4j databases.
"""

import os
import subprocess
import json
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import logging
from dataclasses import dataclass
from .util import load_config, check_connection

logger = logging.getLogger(__name__)

@dataclass
class KnowledgeGraphInfo:
    name: str
    file_path: str
    created_at: str
    size_mb: float
    description: Optional[str] = None

class KnowledgeGraphManager:
    def __init__(self, dumps_directory: str = "/dumps"):
        self.dumps_directory = Path(dumps_directory)
        self.dumps_directory.mkdir(exist_ok=True)
        self.metadata_file = self.dumps_directory / "kg_metadata.json"
        self.config = load_config()
        
    def get_neo4j_container_name(self) -> str:
        """Get the Neo4j container name from environment or default."""
        return os.getenv("NEO4J_CONTAINER_NAME", "nexarag.neo4j")
        
    def _load_metadata(self) -> Dict[str, Dict]:
        """Load metadata about knowledge graphs."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading metadata: {e}")
                return {}
        return {}
    
    def _save_metadata(self, metadata: Dict[str, Dict]):
        """Save metadata about knowledge graphs."""
        try:
            with open(self.metadata_file, 'w') as f:
                json.dump(metadata, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving metadata: {e}")
    
    def list_knowledge_graphs(self) -> List[KnowledgeGraphInfo]:
        """List all available knowledge graph dumps."""
        metadata = self._load_metadata()
        kg_list = []
        
        for dump_file in self.dumps_directory.glob("*.dump"):
            name = dump_file.stem
            file_path = str(dump_file)
            
            # Get metadata if available
            kg_metadata = metadata.get(name, {})
            
            # Get file stats
            try:
                stat = dump_file.stat()
                size_mb = stat.st_size / (1024 * 1024)
                created_at = datetime.fromtimestamp(stat.st_mtime).isoformat()
            except Exception:
                size_mb = 0
                created_at = datetime.now().isoformat()
            
            kg_info = KnowledgeGraphInfo(
                name=name,
                file_path=file_path,
                created_at=kg_metadata.get('created_at', created_at),
                size_mb=size_mb,
                description=kg_metadata.get('description')
            )
            kg_list.append(kg_info)
        
        return sorted(kg_list, key=lambda x: x.created_at, reverse=True)
    
    def export_knowledge_graph(self, name: str, description: Optional[str] = None) -> bool:
        """Export current knowledge graph to a dump file."""
        try:
            dump_path = self.dumps_directory / f"{name}.dump"
            container_name = self.get_neo4j_container_name()
            database_name = self.config['database']['database']
            
            # Use docker exec to run neo4j-admin dump inside the container
            # Neo4j 5.x uses different command structure
            cmd = [
                "docker", "exec", container_name,
                "neo4j-admin", "database", "dump",
                "--to-path=/dumps",
                f"--database={database_name}",
                "--overwrite-destination=true"
            ]
            
            logger.info(f"Exporting knowledge graph with command: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                logger.error(f"Export failed: {result.stderr}")
                return False
            
            # Move the dump to our named file
            default_dump = self.dumps_directory / f"{database_name}.dump"
            if default_dump.exists():
                default_dump.rename(dump_path)
            
            # Update metadata
            metadata = self._load_metadata()
            metadata[name] = {
                'created_at': datetime.now().isoformat(),
                'description': description,
                'database': database_name
            }
            self._save_metadata(metadata)
            
            logger.info(f"Successfully exported knowledge graph to {dump_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error exporting knowledge graph: {e}")
            return False
    
    def import_knowledge_graph(self, name: str) -> bool:
        """Import knowledge graph from a dump file."""
        try:
            dump_path = self.dumps_directory / f"{name}.dump"
            if not dump_path.exists():
                logger.error(f"Dump file not found: {dump_path}")
                return False
            
            container_name = self.get_neo4j_container_name()
            database_name = self.config['database']['database']
            
            # Stop Neo4j database first
            stop_cmd = [
                "docker", "exec", container_name,
                "cypher-shell", "-u", self.config['database']['username'],
                "-p", self.config['database']['password'],
                f"STOP DATABASE {database_name}"
            ]
            
            subprocess.run(stop_cmd, capture_output=True, text=True)
            
            # Load the database
            # Neo4j 5.x uses different command structure
            load_cmd = [
                "docker", "exec", container_name,
                "neo4j-admin", "database", "load",
                "--from-path=/dumps",
                f"--database={database_name}",
                "--overwrite-destination=true"
            ]
            
            # Copy our named dump to the expected location
            expected_dump = self.dumps_directory / f"{database_name}.dump"
            if expected_dump.exists():
                expected_dump.unlink()
            dump_path.copy(expected_dump)
            
            logger.info(f"Loading knowledge graph with command: {' '.join(load_cmd)}")
            result = subprocess.run(load_cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode != 0:
                logger.error(f"Load failed: {result.stderr}")
                return False
            
            # Start the database again
            start_cmd = [
                "docker", "exec", container_name,
                "cypher-shell", "-u", self.config['database']['username'],
                "-p", self.config['database']['password'],
                f"START DATABASE {database_name}"
            ]
            
            subprocess.run(start_cmd, capture_output=True, text=True)
            
            logger.info(f"Successfully loaded knowledge graph from {dump_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error importing knowledge graph: {e}")
            return False
    
    def delete_knowledge_graph(self, name: str) -> bool:
        """Delete a knowledge graph dump file."""
        try:
            dump_path = self.dumps_directory / f"{name}.dump"
            if dump_path.exists():
                dump_path.unlink()
                
                # Remove from metadata
                metadata = self._load_metadata()
                if name in metadata:
                    del metadata[name]
                    self._save_metadata(metadata)
                
                logger.info(f"Successfully deleted knowledge graph: {name}")
                return True
            else:
                logger.warning(f"Knowledge graph dump not found: {name}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting knowledge graph: {e}")
            return False
    
    def get_current_kg_info(self) -> Dict[str, any]:
        """Get information about the currently active knowledge graph."""
        try:
            # This would require querying the database for statistics
            # For now, return basic info
            return {
                "database": self.config['database']['database'],
                "uri": self.config['database']['uri'],
                "status": "active"
            }
        except Exception as e:
            logger.error(f"Error getting current KG info: {e}")
            return {"status": "error", "message": str(e)}
