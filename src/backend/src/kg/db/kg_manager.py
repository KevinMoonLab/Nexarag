"""
Knowledge Graph Management Module
Handles export, import, and switching between different Neo4j databases using APOC procedures.
"""

import os
import json
import subprocess
import shutil
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import logging
from dataclasses import dataclass
from .util import load_config, check_connection, load_kg

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
        self.import_directory = Path("/var/lib/neo4j/import")
        
    def _copy_to_dumps(self, filename: str) -> bool:
        """Copy a file from Neo4j import directory to dumps directory."""
        try:
            source = self.import_directory / filename
            dest = self.dumps_directory / filename
            if source.exists():
                shutil.copy2(source, dest)
                return True
            return False
        except Exception as e:
            logger.error(f"Error copying {filename} to dumps: {e}")
            return False
    
    def _copy_from_dumps(self, filename: str) -> bool:
        """Copy a file from dumps directory to Neo4j import directory."""
        try:
            source = self.dumps_directory / filename
            dest = self.import_directory / filename
            if source.exists():
                shutil.copy2(source, dest)
                return True
            return False
        except Exception as e:
            logger.error(f"Error copying {filename} from dumps: {e}")
            return False
        
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
        
        for dump_file in self.dumps_directory.glob("*.graphml"):
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
        """Export current knowledge graph using APOC procedures."""
        try:
            # Get Neo4j connection
            kg = load_kg(self.config)
            
            # APOC exports to import directory, which is now mounted as dumps volume
            export_filename = f"{name}.graphml"
            
            # Use APOC to export the entire graph
            export_query = """
            CALL apoc.export.graphml.all($exportPath, {
                useTypes: true,
                storeNodeIds: false,
                readLabels: true,
                defaultRelationshipType: "RELATED"
            })
            YIELD file, source, format, nodes, relationships, properties, time, rows, batchSize, batches, done, data
            RETURN file, nodes, relationships, time, done
            """
            
            logger.info(f"Exporting knowledge graph to {export_filename}")
            
            result = kg.query(export_query, {"exportPath": export_filename})
            
            if result and len(result) > 0:
                export_result = result[0]
                logger.info(f"Export completed: {export_result}")
                
                # Update metadata
                metadata = self._load_metadata()
                metadata[name] = {
                    'created_at': datetime.now().isoformat(),
                    'description': description,
                    'nodes': export_result.get('nodes', 0),
                    'relationships': export_result.get('relationships', 0),
                    'export_time': export_result.get('time', 0)
                }
                self._save_metadata(metadata)
                
                logger.info(f"Successfully exported knowledge graph: {name}")
                return True
            else:
                logger.error("Export query returned no results")
                return False
                
        except Exception as e:
            logger.error(f"Error exporting knowledge graph: {e}")
            return False
    
    def import_knowledge_graph(self, name: str) -> bool:
        """Import knowledge graph using APOC procedures."""
        try:
            # APOC imports from import directory, which is now mounted as dumps volume
            import_filename = f"{name}.graphml"
            
            # Check if file exists in dumps directory (same as import directory now)
            file_path = self.dumps_directory / import_filename
            if not file_path.exists():
                logger.error(f"Import file not found: {file_path}")
                return False
            
            # Get Neo4j connection
            kg = load_kg(self.config)
            
            # Clear existing data first
            logger.info("Clearing existing graph data...")
            clear_query = "MATCH (n) DETACH DELETE n"
            kg.query(clear_query)
            
            # Import the graph
            import_query = """
            CALL apoc.import.graphml($importPath, {
                readLabels: true,
                storeNodeIds: false,
                defaultRelationshipType: "RELATED"
            })
            YIELD file, source, format, nodes, relationships, properties, time, rows, batchSize, batches, done, data
            RETURN file, nodes, relationships, time, done
            """
            
            logger.info(f"Importing knowledge graph from {import_filename}")
            result = kg.query(import_query, {"importPath": import_filename})
            
            if result and len(result) > 0:
                import_result = result[0]
                logger.info(f"Import completed: {import_result}")
                return True
            else:
                logger.error("Import query returned no results")
                return False
                
        except Exception as e:
            logger.error(f"Error importing knowledge graph: {e}")
            return False
    
    def delete_knowledge_graph(self, name: str) -> bool:
        """Delete a knowledge graph file."""
        try:
            file_path = self.dumps_directory / f"{name}.graphml"
            if file_path.exists():
                file_path.unlink()
                
                # Remove from metadata
                metadata = self._load_metadata()
                if name in metadata:
                    del metadata[name]
                    self._save_metadata(metadata)
                
                logger.info(f"Successfully deleted knowledge graph: {name}")
                return True
            else:
                logger.warning(f"Knowledge graph file not found: {name}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting knowledge graph: {e}")
            return False
    
    def get_current_kg_info(self) -> Dict[str, any]:
        """Get information about the currently active knowledge graph."""
        try:
            kg = load_kg(self.config)
            
            # Get basic stats about the current graph
            stats_query = """
            MATCH (n)
            OPTIONAL MATCH (n)-[r]->()
            RETURN 
                count(DISTINCT n) as nodes,
                count(r) as relationships,
                collect(DISTINCT labels(n)) as node_labels
            """
            
            result = kg.query(stats_query)
            
            if result and len(result) > 0:
                stats = result[0]
                # Flatten nested labels
                all_labels = []
                for label_list in stats.get('node_labels', []):
                    all_labels.extend(label_list)
                unique_labels = list(set(all_labels))
                
                return {
                    "database": self.config['database']['database'],
                    "uri": self.config['database']['uri'],
                    "status": "active",
                    "nodes": stats.get('nodes', 0),
                    "relationships": stats.get('relationships', 0),
                    "node_types": unique_labels
                }
            else:
                return {
                    "database": self.config['database']['database'],
                    "uri": self.config['database']['uri'],
                    "status": "active",
                    "nodes": 0,
                    "relationships": 0,
                    "node_types": []
                }
                
        except Exception as e:
            logger.error(f"Error getting current KG info: {e}")
            return {"status": "error", "message": str(e)}
            
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
    
    def delete_knowledge_graph(self, name: str) -> bool:
        """Delete a knowledge graph file."""
        try:
            file_path = self.dumps_directory / f"{name}.graphml"
            if file_path.exists():
                file_path.unlink()
                
                # Remove from metadata
                metadata = self._load_metadata()
                if name in metadata:
                    del metadata[name]
                    self._save_metadata(metadata)
                
                logger.info(f"Successfully deleted knowledge graph: {name}")
                return True
            else:
                logger.warning(f"Knowledge graph file not found: {name}")
                return False
                
        except Exception as e:
            logger.error(f"Error deleting knowledge graph: {e}")
            return False
    
    def get_current_kg_info(self) -> Dict[str, any]:
        """Get information about the currently active knowledge graph."""
        try:
            kg = load_kg(self.config)
            
            # Get basic stats about the current graph
            stats_query = """
            MATCH (n)
            OPTIONAL MATCH (n)-[r]->()
            RETURN 
                count(DISTINCT n) as nodes,
                count(r) as relationships,
                collect(DISTINCT labels(n)) as node_labels
            """
            
            result = kg.query(stats_query)
            
            if result and len(result) > 0:
                stats = result[0]
                # Flatten nested labels
                all_labels = []
                for label_list in stats.get('node_labels', []):
                    all_labels.extend(label_list)
                unique_labels = list(set(all_labels))
                
                return {
                    "database": self.config['database']['database'],
                    "uri": self.config['database']['uri'],
                    "status": "active",
                    "nodes": stats.get('nodes', 0),
                    "relationships": stats.get('relationships', 0),
                    "node_types": unique_labels
                }
            else:
                return {
                    "database": self.config['database']['database'],
                    "uri": self.config['database']['uri'],
                    "status": "active",
                    "nodes": 0,
                    "relationships": 0,
                    "node_types": []
                }
                
        except Exception as e:
            logger.error(f"Error getting current KG info: {e}")
            return {"status": "error", "message": str(e)}
